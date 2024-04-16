"""Local and remote asteroid name resolution for rocks."""

import asyncio
from functools import singledispatch
from typing import Union

import aiohttp
import numpy as np
import pandas as pd
import nest_asyncio

from rich.progress import Progress

from rocks import cli
from rocks import config
from rocks import index
from rocks.logging import logger

from . import quaero
from .id import Id


# Run asyncio nested for jupyter notebooks, GUIs, ...
try:
    nest_asyncio.apply()
except RuntimeError:
    pass

type_builtin = type


@singledispatch
def identify(id, **kwargs) -> Union[Id, list[Id]]:
    """Resolve names and numbers of one or more minor bodies using identifiers.

    Parameters
    ----------
    id : str, int, float, list, range, set, np.ndarray, pd.Series
        One or more identifying names or numbers to resolve.
    type: str
        The type of the minor body. Choose one of ['Asteroid', 'Comet', 'Satellite'].
        Default is None, which includes asteroids (and dwarf planets).
    local : bool
        Try resolving the name locally first. Default is True.
    progress : bool
        Show progress bar. Default is False.

    Returns
    -------
    dict
    """
    logger.error(
        f"Received id of type {type_builtin(id)}. "
        "Expected one of: str, int, float, list, range, set, np.ndarray, pd.Series."
    )
    return Id(**{})


# NOTE: singledispatch does not support Union types for py<3.11
@identify.register
def _(id: str, **kwargs) -> Id:
    return _identify_sync(id, **kwargs)


@identify.register
def _(id: int, **kwargs) -> Id:
    return _identify_sync(id, **kwargs)


@identify.register
def _(id: float, **kwargs) -> Id:
    """ """
    if np.isnan(id):
        logger.warning("Received empty or NaN identifier.")
        return Id()
    return _identify_sync(int(id), **kwargs)


@identify.register
def _(id: list, **kwargs) -> list[Id]:
    if not id:
        logger.warning("Received empty list of identifiers.")
        return [Id()]
    if len(id) == 1:
        return [_identify_sync(id[0], **kwargs)]
    return _identify_async(id, **kwargs)


@identify.register
def _(id: set, **kwargs) -> list[Id]:
    return identify(list(id), **kwargs)


@identify.register
def _(id: np.ndarray, **kwargs) -> list[Id]:
    return identify(id.tolist(), **kwargs)


@identify.register
def _(id: pd.Series, **kwargs) -> list[Id]:
    return identify(id.to_list(), **kwargs)


def _identify_sync(
    id: Union[int, str, list],
    type: str = "asteroid",
    local: bool = True,
) -> Id:
    """Resolve names and numbers of one or more minor bodies using identifiers.

    Parameters
    ----------
    id : str, int, float, list, range, set, np.ndarray, pd.Series
        One or more identifying names or numbers to resolve.
    type: str
        The type of the minor body. Choose one of ['Asteroid', 'Comet', 'Satellite'].
        Default is None, which includes asteroids (and dwarf planets).
    local : bool
        Try resolving the name locally first. Default is True.

    Returns
    -------
    dict
    """

    # Ensure the asteroid name-number index exists
    if not config.PATH_INDEX.is_dir() and not config.CACHELESS:
        index._ensure_index_exists()

    if type not in ["asteroid", "comet", "satellite"]:
        raise ValueError("'type' must be one of: 'asteroid', 'comet', 'satellite'")

    # ------
    # For a single name, try local lookup right away, async process has overhead
    if config.CACHELESS:
        local = False

    if local:
        match = _local_lookup(id, type)

        if match:
            return Id(**match)

    # Local resolution failed, do remote query
    id = quaero.standardize_id(id)
    match = asyncio.run(quaero.query(id, type))
    return Id(**match)


def _identify_async(
    id, type: str = "asteroid", local: bool = True, progress: bool = False
) -> list[Id]:
    """Resolve names and numbers of one or more minor bodies using identifiers.

    Parameters
    ----------
    id : str, int, float, list, range, set, np.ndarray, pd.Series
        One or more identifying names or numbers to resolve.
    type: str
        The type of the minor body. Choose one of ['Asteroid', 'Comet', 'Satellite'].
        Default is None, which includes asteroids (and dwarf planets).
    local : bool
        Try resolving the name locally first. Default is True.
    progress : bool
        Show progress bar. Default is False.

    Returns
    -------
    tuple, list of tuple : (str, int, str), (None, np.nan, None)
        List containing len(id) tuples. Each tuple contains the minor body's
        name and number. If the resolution failed, the values are None for name
        and SsODNet and np.nan for the number. If a single identifier is
        resolved, a tuple is returned.
    """

    # Ensure the asteroid name-number index exists
    if not config.PATH_INDEX.is_dir() and not config.CACHELESS:
        index._ensure_index_exists()

    if type not in ["asteroid", "comet", "satellite"]:
        raise ValueError("'type' must be one of: 'asteroid', 'comet', 'satellite'")

    if config.CACHELESS:
        local = False

    # Run asynchronous event loop for name resolution
    with Progress(disable=not progress) as progress_bar:
        task = progress_bar.add_task("Identifying rocks", total=len(id))  # type: ignore
        loop = get_or_create_eventloop()
        matches = loop.run_until_complete(
            _identify(id, type, local, progress_bar, task)
        )

    return [Id(**match) for match in matches]  # type: ignore


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


async def _identify(id, type, local, progress_bar, task):
    """Establish the asynchronous HTTP session and launch the name resolution."""

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout()) as session:
        tasks = [
            asyncio.ensure_future(_resolve(i, type, session, local, progress_bar, task))
            for i in id
        ]

        results = await asyncio.gather(*tasks)

    return results


async def _resolve(id, type, session, local, progress_bar, task):
    """Resolve the identifier locally or remotely."""

    if not id or id is None:
        logger.warning("Received empty or NaN identifier.")
        progress_bar.update(task, advance=1)
        return {}

    if not isinstance(id, str):
        if np.isnan(id):
            logger.warning("Received empty or NaN identifier.")
            progress_bar.update(task, advance=1)
            return {}

    if local:
        match = _local_lookup(id, type)

        if match:
            progress_bar.update(task, advance=1)
            return match

    # Local resolution failed, do remote query
    id = quaero.standardize_id(id)
    match = await quaero.query(id, type, session)
    progress_bar.update(task, advance=1)
    return match


def _local_lookup(id, type):
    """Perform local index resolution."""
    # Reduce ID and retrieve fitting index
    id = _reduce_id_for_local(id)
    INDEX = index._get_index_file(id, type)

    # look up possible matches type by type
    if id in INDEX:
        return INDEX[id]
    return {}


def _reduce_id_for_local(id):
    """Reduce the id to a string or number with fewer free parameters.

    Parameters
    ----------
    id : str, int, float
        The minor body's name, designation, or number.

    Returns
    -------
    str, int
        The standardized name, designation, or number. None if id is NaN or None.
    """

    # Number?
    if isinstance(id, (int, float)):
        return int(id)

    try:
        id = int(float(id))
        return id
    except ValueError:
        pass

    # -> Name or designation

    # Strip leading and trailing whitespace
    id = id.strip()

    return id.replace("_(Asteroid)", "").replace("_", "").replace(" ", "").lower()


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
