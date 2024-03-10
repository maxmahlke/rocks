"""Local and remote asteroid name resolution for rocks."""

import asyncio
import re

import aiohttp
import nest_asyncio
import numpy as np

from rich.progress import Progress

from rocks import cli
from rocks import config
from rocks import index
from rocks.logging import logger

# Run asyncio nested for jupyter notebooks, GUIs, ...
try:
    nest_asyncio.apply()
except RuntimeError:
    pass


def get_or_create_eventloop():
    """Enable asyncio to get the event loop in a thread other than the main thread

    Returns
    --------
    out: asyncio.unix_events._UnixSelectorEventLoop
    """
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()


# TODO: Use singledispatch to simplify the function call and return structure
def identify(id_, type_=None, local=True, progress=False):
    """Resolve names and numbers of one or more minor bodies using identifiers.

    Parameters
    ----------
    id_ : str, int, float, list, range, set, np.ndarray, pd.Series
        One or more identifying names or numbers to resolve.
    type_: str
        The type of the minor body. Choose one of ['Asteroid', 'Comet', 'Satellite'].
        Default is None, which includes asteroids (and dwarf planets).
    local : bool
        Try resolving the name locally first. Default is True.
    progress : bool
        Show progress bar. Default is False.

    Returns
    -------
    tuple, list of tuple : (str, int, str), (None, np.nan, None)
        List containing len(id_) tuples. Each tuple contains the minor body's
        name and number. If the resolution failed, the values are None for name
        and SsODNet and np.nan for the number. If a single identifier is
        resolved, a tuple is returned.
    """

    # Ensure the asteroid name-number index exists
    if not config.PATH_INDEX.is_dir() and not config.CACHELESS:
        index._ensure_index_exists()

    type_ = "Asteroid" if type_ is None else type_

    if type_ not in ["Asteroid", "Comet", "Satellite", "Dwarf Planet"]:
        raise ValueError("'type_' must one of: 'Asteroid', 'Comet', 'Satellite'")

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
        return (None, np.nan)
    elif not isinstance(id_, (list, np.ndarray)):
        try:
            id_ = id_.to_list()  # pandas Series
        except AttributeError:
            raise TypeError(
                f"Received id_ of type {type(id_)}, expected one of: "
                "str, int, float, list, set, range, np.ndarray"
            )

    if not id_:
        logger.warning("Received empty list of identifiers.")
        return (None, np.nan)

    # ------
    # For a single name, try local lookup right away, async process has overhead
    if config.CACHELESS:
        local = False

    if len(id_) == 1 and local:
        success, (name, number) = _local_lookup(id_[0], type_)

        if success:
            return (name, number)
        else:
            # Local lookup just failed, no need to try it again
            local = False

    # ------
    # Run asynchronous event loop for name resolution
    with Progress(disable=not progress) as progress_bar:
        task = progress_bar.add_task("Identifying rocks", total=len(id_))  # type: ignore
        loop = get_or_create_eventloop()
        results = loop.run_until_complete(
            _identify(id_, type_, local, progress_bar, task)
        )

        # ------
        # Check if any failed due to 502 and rerun them
        idx_failed = [
            i for i, result in enumerate(results) if result == (None, None, None)
        ]

        if idx_failed:
            # avoid repeating error messages
            level = logger.level
            logger.setLevel("CRITICAL")
            results = np.array(results)
            results[idx_failed] = loop.run_until_complete(
                _identify(np.array(id_)[idx_failed], type_, local, progress_bar, task)
            )
            results = results.tolist()
            logger.setLevel(level)

    # ------
    # Verify the output format
    results = [r[:2] for r in results]

    if len(id_) == 1:  # type: ignore
        results = results[0]

    return results  # type: ignore


async def _identify(id_, type_, local, progress_bar, task):
    """Establish the asynchronous HTTP session and launch the name resolution."""

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout()) as session:
        tasks = [
            asyncio.ensure_future(
                _resolve(i, type_, session, local, progress_bar, task)
            )
            for i in id_
        ]

        results = await asyncio.gather(*tasks)

    return results


async def _resolve(id_, type_, session, local, progress_bar, task):
    """Resolve the identifier locally or remotely."""

    if not id_ or id is None:
        logger.warning("Received empty or NaN identifier.")
        progress_bar.update(task, advance=1)
        return (None, np.nan, None, None)

    if not isinstance(id_, str):
        if np.isnan(id_):
            logger.warning("Received empty or NaN identifier.")
            progress_bar.update(task, advance=1)
            return (None, np.nan, None, None)

    if local:
        success, (name, number) = _local_lookup(id_, type_)

        if success:
            progress_bar.update(task, advance=1)
            return (name, number)

    # Local resolution failed, do remote query
    id_ = _standardize_id_for_quaero(id_)
    response = await _query_quaero(id_, type_, session)

    if response is None:  # query failed with 502
        return (None, np.nan, None, None)

    if not response:  # remote resolution failed
        progress_bar.update(task, advance=1)
        return (None, np.nan, None, None)

    progress_bar.update(task, advance=1)
    return _parse_quaero_response(response["data"], str(id_))


def _local_lookup(id_, type_):
    """Perform local index resolution."""

    # Reduce ID and retrieve fitting index
    id_ = _reduce_id_for_local(id_)
    INDEX = index._get_index_file(id_, type_)

    # look up possible matches type by type
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
        return True, (name, number)
    else:
        return False, (None, np.nan)


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

    # -> Name or designation

    # Strip leading and trailing whitespace
    id_ = id_.strip()

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
        # Strip leading and trailing whitespace
        id_ = id_.strip()

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


async def _query_quaero(id_, type_, session):
    """Query quaero and parse result for a single object.

    Parameters
    ----------
    id_ : str, int, float
        Asteroid name, number, or designation.
    type_: str
        The type of the minor body. Choose one of ['Asteroid', 'Comet', 'Satellite'].
        Default is None, which includes asteroids (and dwarf planets).
    session : aiohttp.ClientSession
        asyncio session

    Returns
    -------
    dict, None, or False
        Quaero response in json format if successful. None if ContentTypeError.
        False if query failed.
    """

    url = "https://api.ssodnet.imcce.fr/quaero/1/sso/search"
    type_ = "Asteroid OR 'Dwarf Planet'" if type_ == "Asteroid" else type_

    params = {
        "q": f'type:({type_}) AND "{id_}"~0',
        "from": "rocks",
        "limit": 100,
    }

    try:
        response = await session.request(method="GET", url=url, params=params)
    except aiohttp.client_exceptions.ClientConnectorError:
        logger.error(f"Failed to establish connection to {url}")
        return None

    try:
        response = await response.json(content_type=None)
    except aiohttp.ContentTypeError:
        return None

    if "data" not in response.keys():  # no match found
        logger.error(f"Could not identify {type_.lower()} '{id_}'.")
        return False

    elif not response["data"]:  # empty response
        logger.error(f"Could not identify {type_.lower()} '{id_}'.")
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
        logger.warning(f"Could not identify {type_.lower()} '{id_}'.")
        return (None, np.nan, None)

    # Found match
    numeric = [int(alias) for alias in match["aliases"] if alias.isnumeric()]
    number = min(numeric) if numeric else np.nan
    return (match["name"], number, match["id"], match["aliases"])


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
