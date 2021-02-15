#!/usr/bin/env python

"""Implement SsODNet:Datacloud queries.
"""
import asyncio
import os
import urllib.parse
import warnings

import aiohttp
import json
import numpy as np
import pandas as pd

import rocks


def get_ssocard(id_ssodnet, progress=False):
    """Retrieve the ssoCard of one or many asteroids, using their SsODNet IDs.

    Parameters
    ==========
    id_ssodnet : str, list, np.ndarray, pd.series
        one or more ssodnet ids.

    Returns
    =======
    dict, list of dict
        list containing len(id_) dictionaries corresponding to the ssocards of
        the passed identifiers. if the card is not available, the dict is empty.
        If a single card is retrieved, a dict is returned.
    progress : bool or tdqm.std.tqdm
       If progress is True, this is a progress bar instance. Else, it's False.

    notes
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
        warnings.warn(f"Received id_ssodnet of type {type(id_ssodnet)}.")
        return [(None, np.nan, None)]
    elif not isinstance(id_ssodnet, (list, np.ndarray)):
        raise TypeError(
            f"Received id_ssodnet of type {type(id_ssodnet)}, expected one of: "
            f"str, list, np.ndarray, pd.Series"
        )

    # Run async loop to get ssoCard
    loop = asyncio.get_event_loop()
    cards = loop.run_until_complete(_get_ssocard(id_ssodnet, progress))

    if len(id_ssodnet) == 1:
        cards = cards[0]

    return cards


async def _get_ssocard(id_ssodnet, progress):
    """Get ssoCard asynchronously. First attempts local lookup, then
    queries SsODNet.

    Parameters
    ==========
    id_ssodnet : str, list, np.ndarray, pd.series
        one or more ssodnet ids.
    progress : bool or tdqm.std.tqdm
       If progress is True, this is a progress bar instance. Else, it's False.

    Returns
    =======
    list of dict
        list containing len(id_) dictionaries corresponding to the ssocards of
    the passed identifiers. if the card is not available, the dict is empty.
    """
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout()) as session:

        tasks = [
            asyncio.ensure_future(_local_or_remote(i, session, progress))
            for i in id_ssodnet
        ]

        results = await asyncio.gather(*tasks)

    return results


async def _local_or_remote(id_ssodnet, session, progress):
    """Check for presence of ssoCard in cache directory. Else, query from SsODNet."""

    if progress:
        progress.update()

    PATH_CARD = os.path.join(rocks.PATH_CACHE, f"{id_ssodnet}.json")

    if os.path.isfile(PATH_CARD):
        with open(PATH_CARD, "r") as file_card:
            return json.load(file_card)

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

    id_ssodnet_parsed = urllib.parse.quote(id_ssodnet)

    URL = (
        f"https://ssp.imcce.fr/webservices/ssodnet/api/ssocard.php?q="
        f"{id_ssodnet_parsed}"
    )

    response = await session.request(method="GET", url=URL)

    if not response.ok:
        warnings.warn(f"ssoCard query failed for ID: {id_ssodnet}")
        return {}

    response_json = await response.json()
    return response_json
