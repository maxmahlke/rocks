#!/usr/bin/env python

"""Implement SsODNet:Datacloud queries.
"""
import asyncio
from itertools import product
import os
import warnings

import aiohttp
import json
import numpy as np
import pandas as pd
from tqdm import tqdm

import rocks


def get_ssocard(id_ssodnet, progress=False, no_cache=False):
    """Retrieve the ssoCard of one or many asteroids, using their SsODNet IDs.

    Parameters
    ==========
    id_ssodnet : str, list, np.ndarray, pd.series
        one or more ssodnet ids.
    progress : bool
        Show progressbar. Default is False.
    no_cache : bool
        If True, forces the remote query of the ssoCard. Default is False.

    Returns
    =======
    dict, list of dict
        list containing len(id_) dictionaries corresponding to the ssocards of
        the passed identifiers. if the card is not available, the dict is empty.
        If a single card is retrieved, a dict is returned.

    Notes
    =====
    card retrieval is first attempted locally, then remotely via datacloud.
    """
    if isinstance(id_ssodnet, str):
        id_ssodnet = [id_ssodnet]
    elif isinstance(id_ssodnet, pd.Series):
        id_ssodnet = id_ssodnet.values
    elif isinstance(id_ssodnet, set):
        id_ssodnet = list(id_ssodnet)
    elif id_ssodnet is None:
        warnings.warn(f"Received SsODNet ID of type {type(id_ssodnet)}.")
        return [(None, np.nan, None)]
    elif not isinstance(id_ssodnet, (list, np.ndarray)):
        raise TypeError(
            f"Received SsODNet ID of type {type(id_ssodnet)}, expected one of: "
            f"str, list, np.ndarray, pd.Series"
        )

    if progress:
        progress = tqdm(desc="Getting ssoCards : ", total=len(id_ssodnet))

    # ---
    # Run async loop to get ssoCard
    loop = asyncio.get_event_loop()
    cards = loop.run_until_complete(_get_ssocard(id_ssodnet, progress, no_cache))

    if len(id_ssodnet) == 1:
        cards = cards[0]

    return cards


async def _get_ssocard(id_ssodnet, progress, no_cache):
    """Get ssoCard asynchronously. First attempts local lookup, then
    queries SsODNet.

    Parameters
    ==========
    id_ssodnet : str, list, np.ndarray, pd.series
        one or more ssodnet ids.
    progress : bool or tdqm.std.tqdm
       If progress is True, this is a progress bar instance. Else, it's False.
    no_cache : bool
        If True, forces the remote query of the ssoCard.

    Returns
    =======
    list of dict
        list containing len(id_) dictionaries corresponding to the ssocards of
    the passed identifiers. if the card is not available, the dict is empty.
    """
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout()) as session:

        tasks = [
            asyncio.ensure_future(_local_or_remote(i, session, progress, no_cache))
            for i in id_ssodnet
        ]

        results = await asyncio.gather(*tasks)

    return results


async def _local_or_remote(id_ssodnet, session, progress, no_cache):
    """Check for presence of ssoCard in cache directory. Else, query from SsODNet."""

    if progress:
        progress.update()

    PATH_CARD = os.path.join(rocks.PATH_CACHE, f"{id_ssodnet}.json")

    if os.path.isfile(PATH_CARD) and not no_cache:
        with open(PATH_CARD, "r") as file_card:
            return json.load(file_card)[id_ssodnet]

    # Local retrieval failed, do remote query
    card = await _query_ssodnet(id_ssodnet, session)

    # save to cache
    if card:
        with open(PATH_CARD, "w") as file_card:
            json.dump(card, file_card)

    return card[id_ssodnet]


async def _query_ssodnet(id_ssodnet, session):
    """Query quaero and parse result for a single object.

    Parameters
    ==========
    id_ssodnet : str
        Asteroid ID from SsODNet.
    session : aiohttp.ClientSession
        asyncio session

    Returns
    =======
    dict
        SsODNet response as dict if successful. Empty if query failed.
    """

    URL = f"https://ssp.imcce.fr/webservices/ssodnet/api/ssocard.php?q=" f"{id_ssodnet}"

    response = await session.request(method="GET", url=URL)

    if not response.ok:
        warnings.warn(f"ssoCard query failed for ID: {id_ssodnet}")
        return {}

    response_json = await response.json()
    return response_json


# ------
def get_datacloud_catalogue(id_ssodnet, catalogue, progress=False, no_cache=False):
    """Retrieve the datacloud catalogue of one or many asteroids, using their SsODNet IDs.

    Parameters
    ==========
    id_ssodnet : str, list, np.ndarray, pd.series
        The ssodnet id of the asteroid
    catalogue : str
        The name of the datacloud catalogue to retrieve.
    progress : bool
        Show progressbar. Default is False.
    no_cache : bool
        If True, forces the remote query of the ssoCard. Default is False.

    Returns
    =======
    list of dict, list of list of dict
        list containing len(catalogue) dictionaries corresponding to
        the catalogues of the passed identifier. If the catalogue is
        not available, the dict is empty.
    progress : bool or tdqm.std.tqdm
       If progress is True, this is a progress bar instance. Else, it's False.

    Notes
    =====
    Catalogue retrieval is first attempted locally, then remotely via datacloud.
    """
    if isinstance(id_ssodnet, str):
        id_ssodnet = [id_ssodnet]
    elif isinstance(id_ssodnet, pd.Series):
        id_ssodnet = id_ssodnet.values
    elif isinstance(id_ssodnet, set):
        id_ssodnet = list(id_ssodnet)
    elif id_ssodnet is None:
        warnings.warn(f"Received SsODNet ID of type {type(id_ssodnet)}.")
        return [(None, np.nan, None)]
    elif not isinstance(id_ssodnet, (list, np.ndarray)):
        raise TypeError(
            f"Received SsODNet ID of type {type(id_ssodnet)}, expected one of: "
            f"str, list, np.ndarray, pd.Series"
        )

    if isinstance(catalogue, str):
        catalogue = [catalogue]
    elif not isinstance(catalogue, (list, np.ndarray)):
        raise TypeError(
            f"Received catalogue of type {type(catalogue)}, expected one of: "
            f"str, list, np.ndarray"
        )

    # Flatten input for easier calling
    id_catalogue = list(product(id_ssodnet, catalogue))

    if progress:
        progress = tqdm(desc="Getting catalogues : ", total=len(id_catalogue))

    # Run async loop to get ssoCard
    loop = asyncio.get_event_loop()
    catalogues = loop.run_until_complete(
        _get_datacloud_catalogue(id_catalogue, progress, no_cache)
    )[0]

    return catalogues


async def _get_datacloud_catalogue(id_catalogue, progress, no_cache):
    """Get catalogue asynchronously. First attempts local lookup, then
    queries SsODNet.

    Parameters
    ==========
    id_catalogue : list
        Asteroid - catalogue combinations.
    progress : bool or tdqm.std.tqdm
        If progress is True, this is a progress bar instance. Else, it's False.
    no_cache : bool
        If True, forces the remote query of the ssoCard. Default is False.

    Returns
    =======
    list of dict
        list containing len(id_) list with dictionaries corresponding to the
    catalogues of the passed identifiers. If the catalogue is not available, the dict
    is empty.
    """
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout()) as session:

        tasks = [
            asyncio.ensure_future(
                _local_or_remote_catalogue(i[0], i[1], session, progress, no_cache)
            )
            for i in id_catalogue
        ]

        results = await asyncio.gather(*tasks)

    return results


async def _local_or_remote_catalogue(
    id_ssodnet, catalogue, session, progress, no_cache
):
    """Check for presence of ssoCard in cache directory. Else, query from SsODNet."""

    if progress:
        progress.update()

    PATH_CATALOGUE = os.path.join(rocks.PATH_CACHE, f"{id_ssodnet}_{catalogue}.json")

    if os.path.isfile(PATH_CATALOGUE) and not no_cache:
        with open(PATH_CATALOGUE, "r") as file_card:
            return json.load(file_card)

    # Local retrieval failed, do remote query
    cat = await _query_datacloud(id_ssodnet, catalogue, session)
    cat = cat["data"][id_ssodnet]["datacloud"]

    if cat:
        cat = cat[catalogue]
        # save to cache
        with open(PATH_CATALOGUE, "w") as file_card:
            json.dump(cat, file_card)

    return cat


async def _query_datacloud(id_ssodnet, catalogue, session):
    """Query quaero and parse result for a single object.

    Parameters
    ==========
    id_ssodnet : str
        Asteroid ID from SsODNet.
    catalogue : str
        Datacloud catalogue name.
    session : aiohttp.ClientSession
        asyncio session

    Returns
    =======
    dict
        SsODNet response as dict if successful. Empty if query failed.
    """
    URL = (
        f"https://ssp.imcce.fr/webservices/ssodnet/api/datacloud.php?-name=id:{id_ssodnet}"
        f"&-resource={catalogue}&-mime=json&-from=rocks"
    )

    response = await session.request(method="GET", url=URL)

    if not response.ok:
        warnings.warn(f"Catalogue query failed for ID: {id_ssodnet} - {catalogue}")
        return {}

    response_json = await response.json()
    return response_json
