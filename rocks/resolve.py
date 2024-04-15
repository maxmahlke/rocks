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
from rocks.resolve import quaero

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
    response = await quaero.query(id_, type_, session)

    if response is None:  # query failed with 502
        return (None, np.nan, None, None)

    if not response:  # remote resolution failed
        progress_bar.update(task, advance=1)
        return (None, np.nan, None, None)

    progress_bar.update(task, advance=1)
    return quaero.parse_response(response["data"], str(id_))


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
