"""Local and remote asteroid name resolution for rocks."""

import asyncio
import pickle
import re
import sys

import aiohttp
import nest_asyncio
import numpy as np

import requests
from rich.progress import Progress

from rocks import cli
from rocks import index
from rocks.logging import logger

# Run asyncio nested for jupyter notebooks, GUIs, ...
nest_asyncio.apply()


def identify(id_, return_id=False, local=True, progress=False):
    """Resolve names and numbers of one or more minor bodies using identifiers.

    Parameters
    ----------
    id_ : str, int, float, list, range, set, np.ndarray, pd.Series
        One or more identifying names or numbers to resolve.
    return_id : bool
        Return the SsODNet ID of the asteroid as third member of
        the tuple. Default is False.
    local : bool
        Try resolving the name locally first. Default is True.
    progress : bool
        Show progress bar. Default is False.

    Returns
    -------
    tuple, list of tuple : (str, int, str), (None, np.nan, None)
        List containing len(id_) tuples. Each tuple contains the asteroid's
        name, number, and the SsODNet ID if return_id=True. If the resolution
        failed, the values are None for name and SsODNet and np.nan for the
        number. If a single identifier is resolved, a tuple is returned.

    Notes
    -----
    Name resolution is first attempted locally, then remotely via quaero. If
    the asteroid is unnumbered, its number is np.nan.
    """

    # ------
    # Verify input
    if isinstance(id_, (str, int, float)):
        id_ = [id_]
    elif isinstance(id_, np.ndarray):
        id_ = id_.tolist()
    elif isinstance(id_, (set, range)):
        id_ = list(id_)
    elif id_ is None:
        logger.warning(f"Received id_ of type {type(id_)}.")
        return (None, np.nan) if not return_id else (None, np.nan, None)  # type: ignore
    elif not isinstance(id_, (list, np.ndarray)):
        raise TypeError(
            f"Received id_ of type {type(id_)}, expected one of: "
            "str, int, float, list, set, range, np.ndarray"
        )

    if not id_:
        logger.warning("Received empty list of identifiers.")
        return (None, np.nan) if not return_id else (None, np.nan, None)  # type: ignore

    # ------
    # For a single name, try local lookup right away, async process has overhead
    if len(id_) == 1 and local:

        success, (name, number, ssodnet_id) = _local_lookup(id_[0])

        if success:
            if not return_id:
                return (name, number)
            else:
                return (name, number, ssodnet_id)

    # ------
    # Run asynchronous event loop for name resolution
    with Progress(disable=not progress) as progress_bar:

        task = progress_bar.add_task("Identifying rocks", total=len(id_))  # type: ignore
        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(_identify(id_, local, progress_bar, task))

        # ------
        # Check if any failed due to 502 and rerun them
        idx_failed = [
            i for i, result in enumerate(results) if result == (None, None, None)
        ]

        if idx_failed:
            results = np.array(results)
            results[idx_failed] = loop.run_until_complete(
                _identify(np.array(id_)[idx_failed], local, progress_bar, task)
            )
            results = results.tolist()

    # ------
    # Verify the output format
    if not return_id:
        results = [r[:2] for r in results]

    if len(id_) == 1:  # type: ignore
        results = results[0]

    return results  # type: ignore


async def _identify(id_, local, progress_bar, task):
    """Establish the asynchronous HTTP session and launch the name resolution."""

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout()) as session:

        tasks = [
            asyncio.ensure_future(_resolve(i, session, local, progress_bar, task))
            for i in id_
        ]

        results = await asyncio.gather(*tasks)

    return results


async def _resolve(id_, session, local, progress_bar, task):
    """Resolve the identifier locally or remotely."""

    if not id_ or id is None:
        logger.warning("Received empty or NaN identifier.")
        progress_bar.update(task, advance=1)
        return (None, np.nan, None)

    if not isinstance(id_, str):
        if np.isnan(id_):
            logger.warning("Received empty or NaN identifier.")
            progress_bar.update(task, advance=1)
            return (None, np.nan, None)

    if local:
        success, (name, number, ssodnet_id) = _local_lookup(id_)

        if success:
            progress_bar.update(task, advance=1)
            return (name, number, ssodnet_id)

    # Local resolution failed, do remote query
    id_ = _standardize_id_for_quaero(id_)
    response = await _query_quaero(id_, session)

    if response is None:  # query failed with 502
        return (None, None, None)

    if not response:  # remote resolution failed
        progress_bar.update(task, advance=1)
        return (None, np.nan, None)

    progress_bar.update(task, advance=1)
    return _parse_quaero_response(response["data"], str(id_))


def _local_lookup(id_):
    """Perform local index resolution."""

    # Reduce ID and retrieve fitting index
    id_ = _reduce_id_for_local(id_)
    INDEX = index._get_index_file(id_)

    if id_ in INDEX:
        # Is the number included?
        # Not included for number queries and for unnumbered asteroids
        if len(INDEX[id_]) == 2:
            name, ssodnet_id = INDEX[id_]

            # Use ID as number if it is one
            if isinstance(id_, int):
                number = id_
            else:
                number = np.nan
        else:
            name, number, ssodnet_id = INDEX[id_]
        return True, (name, number, ssodnet_id)
    else:
        return False, (None, np.nan, None)


def _reduce_id_for_local(id_):
    """Reduce the id_ to a string or number with fewer free parameters.

    Parameters
    ----------
    id_ : str, int, float
        The minor body's name, designation, or number.

    Returns
    -------
    str, int
        The standardized name, designation, or number. None if id_ is NaN or None.
    """

    # Number?
    if isinstance(id_, (int, float)):
        return int(id_)

    try:
        id_ = int(float(id_))
        return id_
    except ValueError:
        pass

    # Name or designation
    return id_.replace("_(Asteroid)", "").replace("_", "").replace(" ", "").lower()


def _standardize_id_for_quaero(id_):
    """Try to infer id_ type and re-format if necessary to ensure
    successful remote lookup.

    Parameters
    ----------
    id_ : str, int, float
        The minor body's name, designation, or number.

    Returns
    -------
    str, int, None
        The standardized name, designation, or number. None if id_ is NaN or None.
    """
    if isinstance(id_, (int, float)):
        return int(id_)

    elif isinstance(id_, str):
        # String id_. Perform some regex tests to make sure it's well formatted

        # Asteroid number
        try:
            id_ = int(float(id_))
            return id_
        except ValueError:
            pass

        # Ensure that there is no suffix
        id_ = id_.replace("_(Asteroid)", "")

        # Asteroid name
        if re.match(r"^[A-Za-z _]*$", id_):
            # make case-independent
            id_ = id_.lower()

        # Asteroid designation
        elif re.match(
            r"(^([1A][8-9][0-9]{2}[ _]?[A-Za-z]{2}[0-9]{0,3}$)|"
            r"(^20[0-9]{2}[_ ]?[A-Za-z]{2}[0-9]{0,3}$))",
            id_,
        ):

            # Ensure whitespace between year and id_
            id_ = re.sub(r"[\W_]+", "", id_)
            ind = re.search(r"[A18920]{1,2}[0-9]{2}", id_).end()  # type: ignore
            id_ = f"{id_[:ind]} {id_[ind:]}"

            # Replace A by 1
            id_ = re.sub(r"^A", "1", id_)

            # Ensure uppercase
            id_ = id_.upper()

        # Palomar-Leiden / Transit
        elif re.match(r"^[1-9][0-9]{3}[ _]?(P-L|T-[1-3])$", id_):

            # Ensure whitespace
            id_ = re.sub(r"[ _]+", "", id_)
            id_ = f"{id_[:4]} {id_[4:]}"

        # Comet
        elif re.match(r"(^[PDCXAI]/[- 0-9A-Za-z]*)", id_):
            pass

        # Remaining should be unconventional asteroid names like
        # "G!kun||'homdima" or packed designations
        else:
            pass
    else:
        logger.warning(
            f"Did not understand type of id: {type(id_)}"
            "\nShould be integer, float, or string."
        )
    return id_


async def _query_quaero(id_, session):
    """Query quaero and parse result for a single object.

    Parameters
    ----------
    id_ : str, int, float
        Asteroid name, number, or designation.
    session : aiohttp.ClientSession
        asyncio session

    Returns
    -------
    dict, None, or False
        Quaero response in json format if successful. None if ContentTypeError.
        False if query failed.
    """

    url = "https://api.ssodnet.imcce.fr/quaero/1/sso/search"

    params = {
        "q": f'type:("Dwarf Planet" OR Asteroid) AND "{id_}"~0',
        "from": "rocks",
        "limit": 100,
    }

    response = await session.request(method="GET", url=url, params=params)

    try:
        response = await response.json(content_type=None)
    except aiohttp.ContentTypeError:
        return None

    if "data" not in response.keys():  # no match found
        logger.warning(f"Could not find match for id {id_}.")
        return False

    elif not response["data"]:  # empty response
        logger.warning(f"Could not find match for id {id_}.")
        return False

    return response


def _parse_quaero_response(data, id_):
    """Parse JSON response from Quaero.

    Parameters
    ----------
    data : list of dict
        Quaero query response in json format.
    id_ : str, int, float
        Asteroid name, number, or designation.

    Returns
    -------
    tuple : (str, int, str), (None, np.nan, None)
        Tuple containing the asteroid's name, number, and SsODNet ID if the
        identifier was resolved. Otherwise, the values are None for name and
        SsODNet and np.nan for the number.
    """

    id_ = str(id_).lower()

    for match in data:
        if match["name"].lower() == id_:
            break
        elif match["id"].lower() == id_:
            break
        elif any(alias.lower() == id_ for alias in match["aliases"]):
            break
    else:
        # Unclear which match is correct.
        logger.warning(f"Could not find match for id {id_}.")
        return (None, np.nan, None)

    # Found match
    numeric = [int(alias) for alias in match["aliases"] if alias.isnumeric()]
    number = min(numeric) if numeric else np.nan
    return (match["name"], number, match["id"])


def _interactive():
    """Launch interactive, fuzzy-searchable selection of asteroid.

    Returns
    -------
    str
        The name of the selected asteroid.
    """

    # Load fuzzy index
    LINES = index._load("fuzzy_index.pkl")

    # Launch selection
    choice = cli._interactive(LINES)

    # Return asteroid name
    return " ".join(choice.split()[1:])


def get_citation_from_mpc(name):
    """Query asteroid information from MPC and extract citation from HTML response."""
    from bs4 import BeautifulSoup
    import urllib

    URL = f"https://minorplanetcenter.net/db_search/show_object?object_id={urllib.parse.quote_plus(str(name))}"

    soup = BeautifulSoup(requests.get(URL).text, "html.parser")

    citation = soup.find("div", {"id": "citation"})

    if citation is None:
        return None

    # Extract citation and do minor formatting
    citation = citation.find("br").next_sibling.next_sibling
    citation = citation.split("[")[0].strip().replace("  ", " ")
    return citation
