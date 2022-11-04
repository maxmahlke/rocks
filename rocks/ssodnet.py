#!/usr/bin/env python
"""Implement SsODNet:Datacloud queries."""

import asyncio
from itertools import product

import aiohttp
import json
import numpy as np
import pandas as pd
from rich.progress import Progress

from rocks import config
from rocks.logging import logger


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

    # ---
    # Run async loop to get ssoCard
    with Progress(disable=not progress) as progress_bar:

        progress = progress_bar.add_task("Getting ssoCards", total=len(id_ssodnet))
        loop = asyncio.get_event_loop()
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

    if PATH_CARD.is_file() and local:
        with open(PATH_CARD, "r") as file_card:
            progress_bar.update(progress, advance=1)
            return json.load(file_card)

    # Local retrieval failed, do remote query
    card = await _query_ssodnet(id_ssodnet, session)

    # save to cache
    if card is not None:
        card = _postprocess_ssocard(card)

        with open(PATH_CARD, "w") as file_card:
            json.dump(card, file_card)

    progress_bar.update(progress, advance=1)
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

    URL = f"https://ssp.imcce.fr/webservices/ssodnet/api/ssocard.php?q={id_ssodnet}"

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

    with Progress(disable=not progress) as progress_bar:

        progress = progress_bar.add_task(
            "Getting catalogues" if len(catalogue) > 1 else catalogue[0],
            total=len(id_catalogue),
        )

        # Run async loop to get ssoCard
        loop = asyncio.get_event_loop()
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


async def _local_or_remote_catalogue(
    id_ssodnet, catalogue, session, progress_bar, progress, local
):
    """Check for presence of ssoCard in cache directory. Else, query from SsODNet."""

    PATH_CATALOGUE = config.PATH_CACHE / f"{id_ssodnet}_{catalogue}.json"

    if PATH_CATALOGUE.is_file() and local:
        with open(PATH_CATALOGUE, "r") as file_card:
            progress_bar.update(progress, advance=1)
            return json.load(file_card)

    # Local retrieval failed, do remote query
    cat = await _query_datacloud(id_ssodnet, catalogue, session)
    cat = cat["data"]

    # Always save the result, even if catalogue is empty
    if cat is not None:
        cat = cat[0]["datacloud"]
        if catalogue in cat:
            cat = cat[catalogue]
        else:
            cat = {}
    else:
        cat = {}

    # save to cache
    with open(PATH_CATALOGUE, "w") as file_card:
        json.dump(cat, file_card)

    progress_bar.update(progress, advance=1)
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
        f"https://ssp.imcce.fr/webservices/ssodnet/api/datacloud.php?-name=id:{id_ssodnet}"
        f"&-resource={catalogue}&-mime=json&-from=rocks"
    )

    response = await session.request(method="GET", url=URL)

    if not response.ok:
        logger.warning(f"Catalogue query failed for ID: {id_ssodnet} - {catalogue}")
        return {"data": {id_ssodnet: {"datacloud": None}}}

    response_json = await response.json()
    return response_json
