#!/usr/bin/env python
"""Implement SsODNet:Datacloud queries."""

import asyncio
from functools import partial
from itertools import product
from urllib.request import Request, urlopen


import aiohttp
import json
import numpy as np
import pandas as pd
from rich.progress import BarColumn, DownloadColumn, Progress, TextColumn

from rocks import bft
from rocks import config
from rocks.logging import logger
from rocks.resolve import get_or_create_eventloop

URL_SSODNET = "https://ssp.imcce.fr"


def get_ssocard(id_ssodnet, progress=False, local=True):
    """Retrieve the ssoCard of one or many asteroids, using their SsODNet IDs.

    Parameters
    ----------
    id_ssodnet : str, list, np.ndarray, pd.series
        one or more ssodnet ids.
    progress : bool
        Show progressbar. Default is False.
    local : bool
        If False, forces the remote query of the ssoCard. Default is True.

    Returns
    -------
    dict, list of dict
        list containing len(id_) dictionaries corresponding to the ssocards of
        the passed identifiers. if the card is not available, the dict is empty.
        If a single card is retrieved, a dict is returned.

    Notes
    -----
    Card retrieval is first attempted locally, then remotely via datacloud.
    """
    if isinstance(id_ssodnet, str):
        id_ssodnet = [id_ssodnet]
    elif isinstance(id_ssodnet, pd.Series):
        id_ssodnet = id_ssodnet.values
    elif isinstance(id_ssodnet, (set, tuple)):
        id_ssodnet = list(id_ssodnet)
    elif id_ssodnet is None:
        logger.warning(f"Received SsODNet ID of type {type(id_ssodnet)}.")
        return [(None, np.nan, None)]
    elif not isinstance(id_ssodnet, (list, np.ndarray)):
        raise TypeError(
            f"Received SsODNet ID of type {type(id_ssodnet)}, expected one of: "
            "str, list, np.ndarray, pd.Series"
        )

    if config.CACHELESS:
        local = False

    # ---
    # Run async loop to get ssoCard
    if not progress:
        # Launching the progressbar in jupyter notebooks spams empty
        # lines, so I'm not using the 'disable' argument of the Progress class
        loop = get_or_create_eventloop()
        cards = loop.run_until_complete(_get_ssocard(id_ssodnet, None, None, local))

    else:
        with Progress() as progress_bar:
            progress = progress_bar.add_task("Getting ssoCards", total=len(id_ssodnet))
            loop = get_or_create_eventloop()
            cards = loop.run_until_complete(
                _get_ssocard(id_ssodnet, progress_bar, progress, local)
            )

    if len(id_ssodnet) == 1:
        cards = cards[0]

    return cards


async def _get_ssocard(id_ssodnet, progress_bar, progress, local):
    """Get ssoCard asynchronously. First attempt local lookup, then query SsODNet."""
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout()) as session:
        tasks = [
            asyncio.ensure_future(
                _local_or_remote(i, session, progress_bar, progress, local)
            )
            for i in id_ssodnet
        ]

        results = await asyncio.gather(*tasks)

    return results


async def _local_or_remote(id_ssodnet, session, progress_bar, progress, local):
    """Check for presence of ssoCard in cache directory. Else, query from SsODNet."""

    PATH_CARD = config.PATH_CACHE / f"{id_ssodnet}.json"

    if PATH_CARD.is_file() and local and not config.CACHELESS:
        _update_progress(progress_bar, progress)

        with open(PATH_CARD, "r") as file_card:
            return json.load(file_card)

    # Local retrieval failed, do remote query
    card = await _query_ssodnet(id_ssodnet, session)

    if card is not None:
        card = _postprocess_ssocard(card)

        if not config.CACHELESS:
            with open(PATH_CARD, "w") as file_card:
                json.dump(card, file_card)

    _update_progress(progress_bar, progress)
    return card


async def _query_ssodnet(id_ssodnet, session):
    """Query quaero and parse result for a single object.

    Parameters
    ----------
    id_ssodnet : str
        Asteroid ID from SsODNet.
    session : aiohttp.ClientSession
        asyncio session

    Returns
    -------
    dict
        SsODNet response as dict if successful. Empty if query failed.
    """

    URL = f"{URL_SSODNET}/webservices/ssodnet/api/ssocard.php?q={id_ssodnet}"

    response = await session.request(method="GET", url=URL)

    if not response.ok:
        logger.warning(f"ssoCard query failed for ID '{id_ssodnet}'")
        return None

    response_json = await response.json()

    if response_json is None:
        logger.warning(f"ssoCard query returned empty ssoCard for ID '{id_ssodnet}'")
        return None

    return response_json


def _postprocess_ssocard(card):
    """Apply ssoCard structure improvements for pydantic deserialization."""

    def make_dict(values):
        """Turn lower-level dict values into dicts."""
        for key, value in values.items():
            if isinstance(value, dict):
                make_dict(value)
            else:
                # These keys are not touched, they don't have metadata
                if key in [
                    "bibref",
                    "method",
                    "value",
                    "error",
                    "min",
                    "max",
                    "links",
                    "datacloud",
                    "selection",
                ]:
                    continue
                # Turn non-dict value into dict for merging with metadata
                values[key] = {"value": value}
        return values

    # Turn low-level parameters into dictionaries
    card["parameters"] = make_dict(card["parameters"])

    # ------
    # Convert spin to list
    if "spins" not in card["parameters"]["physical"]:
        card["parameters"]["physical"]["spins"] = {}

    spins = card["parameters"]["physical"]["spins"]
    spin_solutions = []

    for key, spin in spins.items():
        # spin entries have integer ids
        if not key.isnumeric():
            continue

        # convert the spin key to an entry in the solution dict
        spin["id_"] = {
            "value": key,
        }

        spin_solutions.append(spin)
    card["parameters"]["physical"]["spin"] = spin_solutions
    del card["parameters"]["physical"]["spins"]

    return card


# ------
def get_datacloud_catalogue(id_ssodnet, catalogue, progress=False, local=True):
    """Retrieve the datacloud catalogue of one or many asteroids, using their SsODNet IDs.

    Parameters
    ----------
    id_ssodnet : str, list, np.ndarray, pd.series
        The ssodnet id of the asteroid. Can be one or many.
    catalogue : str, list of str
        The name of the datacloud catalogue to retrieve. Can be one or many.
    progress : bool
        Show progressbar. Default is False.
    local : bool
        If False, forces the remote query of the ssoCard. Default is True.

    Returns
    -------
    list of dict, list of list of dict
        list containing len(catalogue) dictionaries corresponding to
        the catalogues of the passed identifier. If the catalogue is
        not available, the dict is empty.
    progress : bool or tdqm.std.tqdm
       If progress is True, this is a progress bar instance. Else, it's False.

    Notes
    -----
    Catalogue retrieval is first attempted locally, then remotely via datacloud.
    """
    if isinstance(id_ssodnet, str):
        id_ssodnet = [id_ssodnet]
    elif isinstance(id_ssodnet, pd.Series):
        id_ssodnet = id_ssodnet.values
    elif isinstance(id_ssodnet, (set, tuple)):
        id_ssodnet = list(id_ssodnet)
    elif id_ssodnet is None:
        logger.warning(f"Received SsODNet ID of type {type(id_ssodnet)}.")
        return [(None, np.nan, None)]
    elif not isinstance(id_ssodnet, (list, np.ndarray)):
        raise TypeError(
            f"Received SsODNet ID of type {type(id_ssodnet)}, expected one of: "
            "str, list, np.ndarray, pd.Series"
        )

    if isinstance(catalogue, str):
        catalogue = [catalogue]
    elif not isinstance(catalogue, (list, np.ndarray)):
        raise TypeError(
            f"Received catalogue of type {type(catalogue)}, expected one of: "
            "str, list, np.ndarray"
        )

    # Flatten input for easier calling
    id_catalogue = list(product(id_ssodnet, catalogue))

    if config.CACHELESS:
        local = False

    if not progress:
        loop = get_or_create_eventloop()
        catalogues = loop.run_until_complete(
            _get_datacloud_catalogue(id_catalogue, None, None, local)
        )[0]

    else:
        with Progress(disable=not progress) as progress_bar:
            progress = progress_bar.add_task(
                "Getting catalogues" if len(catalogue) > 1 else catalogue[0],
                total=len(id_catalogue),
            )

            # Run async loop to get ssoCard
            loop = get_or_create_eventloop()
            catalogues = loop.run_until_complete(
                _get_datacloud_catalogue(id_catalogue, progress_bar, progress, local)
            )[0]

    return catalogues


async def _get_datacloud_catalogue(id_catalogue, progress_bar, progress, local):
    """Get catalogue asynchronously. First attempt local lookup, then query SsODNet.

    Parameters
    ----------
    id_catalogue : list
        Asteroid - catalogue combinations.
    progress : bool or tdqm.std.tqdm
        If progress is True, this is a progress bar instance. Else, it's False.
    local : bool
        If False, forces the remote query of the ssoCard. Default is True.

    Returns
    -------
    list of dict
        list containing len(id_) list with dictionaries corresponding to the
    catalogues of the passed identifiers. If the catalogue is not available, the dict
    is empty.
    """
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout()) as session:
        tasks = [
            asyncio.ensure_future(
                _local_or_remote_catalogue(
                    i[0], i[1], session, progress_bar, progress, local
                )
            )
            for i in id_catalogue
        ]

        results = await asyncio.gather(*tasks)

    return results


def _update_progress(progress_bar, progress):
    if progress_bar is not None:
        progress_bar.update(progress, advance=1)


async def _local_or_remote_catalogue(
    id_ssodnet, catalogue, session, progress_bar, progress, local
):
    """Check for presence of ssoCard in cache directory. Else, query from SsODNet."""

    PATH_CATALOGUE = config.PATH_CACHE / f"{id_ssodnet}_{catalogue}.json"

    if PATH_CATALOGUE.is_file() and local:
        _update_progress(progress_bar, progress)
        with open(PATH_CATALOGUE, "r") as file_card:
            return json.load(file_card)

    # Local retrieval failed, do remote query
    cat = await _query_datacloud(id_ssodnet, catalogue, session)
    cat = cat["data"]

    # Always save the result, even if catalogue is empty
    if cat is not None:
        try:
            cat = cat[0]["datacloud"]
        except (IndexError, KeyError):
            logger.error(
                f"Catalogue '{catalogue}' for '{id_ssodnet}' got an invalid response from datacloud."
            )
            cat = {}
            _update_progress(progress_bar, progress)
            return cat
        if catalogue in cat:
            cat = cat[catalogue]
        else:
            cat = {}
    else:
        cat = {}

    if not config.CACHELESS:
        with open(PATH_CATALOGUE, "w") as file_card:
            json.dump(cat, file_card)

    _update_progress(progress_bar, progress)
    return cat


async def _query_datacloud(id_ssodnet, catalogue, session):
    """Query quaero and parse result for a single object.

    Parameters
    ----------
    id_ssodnet : str
        Asteroid ID from SsODNet.
    catalogue : str
        Datacloud catalogue name.
    session : aiohttp.ClientSession
        asyncio session

    Returns
    -------
    dict
        SsODNet response as dict if successful. Empty if query failed.
    """
    URL = (
        f"{URL_SSODNET}/webservices/ssodnet/api/datacloud.php?-name=id:{id_ssodnet}"
        f"&-resource={catalogue}&-mime=json&-from=rocks"
    )

    response = await session.request(method="GET", url=URL)

    if not response.ok:
        return {"data": {id_ssodnet: {"datacloud": None}}}

    response_json = await response.json()
    return response_json


# ------
# Get ssoBFT
def _get_bft():
    """Retrieve the ssoBFT in parquet format to cache."""
    URL = f"{URL_SSODNET}/data/ssoBFT-latest.parquet"

    progress = Progress(
        TextColumn("{task.fields[desc]}"), BarColumn(), DownloadColumn()
    )

    # ------
    # Launch download
    with progress:
        request = Request(URL)
        response = urlopen(request)

        task = progress.add_task(
            "download",
            desc="Downloading ssoBFT",
            total=int(response.info()["Content-length"]),
        )

        with open(bft.PATH, "wb") as file:
            for data in iter(partial(response.read, 32768), b""):
                file.write(data)
                progress.update(task, advance=len(data))
