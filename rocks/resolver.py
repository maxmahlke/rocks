#!/usr/bin/env python

"""Implement asteroid identification module.
"""
import asyncio
import re
import warnings

import aiohttp
import numpy as np
import pandas as pd
import requests

import rocks


def identify(id_, return_id=False, verbose=True, progress=True):
    """Resolve names and numbers of one or more minor bodies using identifiers.

    Parameters
    ==========
    id_ : str, int, float, list, np.ndarray, pd.Series
        One or more identifying names or numbers to resolve.
    return_id : bool
        Return asteroid SsODNet id as well. Default is False.
    verbose : bool
        Print query diagnostics. Default is True.
    progress : bool
        Display progress bar. Default is True.

    Returns
    =======
    tuple, (str, int or float, str), (np.nan, np.nan, np.nan)
        Tuple containing  asteroid name or designation and asteroid number, NaN
        if not numbered, and optionally the asteroid SsODNet id. If input was
        list of ids, returns a list of tuples. Tuple values are NaN if query
        failed.
    tuple, (str, str, int or float), (np.nan, np.nan, np.nan)
        Tuple containing asteroid SsODNet id , asteroid name or designation,
        and asteroid number, NaN if not numbered. If input was list of ids,
        returns a list of tuples. Tuple values are NaN if query failed.
    """
    if isinstance(id_, (str, int, float)):
        id_ = [id_]
    elif isinstance(id_, pd.Series):
        id_ = id_.values
    elif not isinstance(id_, (list, np.ndarray)):
        raise TypeError(
            f"Received id_ of type {type(id_)}, expected str, int, or list."
        )

    async def _identify(id_):

        index = rocks.utils.read_index()

        NUMBER_NAME_ID = dict(
            (number, (name, id_))
            for number, name, id_ in zip(
                index.number.values, index["name"].values, index.id_.values
            )
        )
        NAME_NUMBER_ID = dict(
            (name, (number, id_))
            for number, name, id_ in zip(
                index.number.values, index["name"].values, index.id_.values
            )
        )
        ID_NUMBER_NAME = dict(
            (id_, (number, name))
            for number, name, id_ in zip(
                index.number.values, index["name"].values, index.id_.values
            )
        )

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout()) as session:
            tasks = [
                _query_and_resolve(
                    i, session, NUMBER_NAME_ID, NAME_NUMBER_ID, ID_NUMBER_NAME, verbose
                )
                for i in id_
            ]

            if progress:

                with rocks.utils.progress_context() as prog:

                    results = [
                        await f
                        for f in prog.track(
                            asyncio.as_completed(tasks),
                            total=len(tasks),
                            description="Identifying rocks",
                        )
                    ]

            else:
                results = [await f for f in asyncio.as_completed(tasks)]

            return results

    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(_identify(id_))

    if not return_id:
        results = [r[:2] for r in results]

    if len(results) == 1:
        return results[0]
    else:
        return results


async def _query_and_resolve(
    id_, session, NUMBER_NAME_ID, NAME_NUMBER_ID, ID_NUMBER_NAME, verbose
):
    """Standardize id_, do local look-up, else query quaero and parser
    methods asynchronously. Call with identify function."""
    id_ = standardize_id_(id_)

    # Try local resolution
    if isinstance(id_, (int)):
        if id_ in NUMBER_NAME_ID.keys():
            name, ssodnet_id = NUMBER_NAME_ID[id_]
            return (name, id_, ssodnet_id)
    elif isinstance(id_, (str)):
        if id_ in NAME_NUMBER_ID.keys():
            number, ssodnet_id = NAME_NUMBER_ID[id_]
            return (id_, number, ssodnet_id)
        elif id_ in ID_NUMBER_NAME.keys():
            number, name = ID_NUMBER_NAME[id_]
            return (name, number, id_)
    elif id_ is None:
        return (np.nan, np.nan, np.nan)

    # Local resolution failed, do remote query
    response = await _query_quaero(id_, session, verbose)

    if response:
        name, number, ssodnet_id = _parse_quaero_response(response["data"], str(id_))
        if isinstance(ssodnet_id, str):
            return (name, number, ssodnet_id)
    return (np.nan, np.nan, np.nan)


def standardize_id_(id_):
    """Try to infer id_ type and re-format if necessary to ensure
    successful lookup.

    Parameters
    ==========
    id_ : str, int, float
        The minor body's name, designation, or number.

    Returns
    =======
    str, int, float, None
        The standardized name, designation, or number. None if id_ is NaN or None.
    """
    if isinstance(id_, (int, float, np.int64)):
        try:
            id_ = int(id_)
        except ValueError:  # np.nan
            if np.isnan(id_):
                warnings.warn(f"Received id 'NaN'.")
                return None

    elif isinstance(id_, str):
        # String id_. Perform some regex tests to make sure it's well formatted

        # Asteroid number
        if id_.isnumeric():
            id_ = int(id_)

        # Asteroid name
        elif re.match(r"^[A-Za-z]*$", id_):

            # Ensure proper capitalization
            id_ = id_.capitalize()

        # Asteroid designation
        elif re.match(
            r"(^([1A][8-9][0-9]{2}[ _]?[A-Za-z]{2}[0-9]{0,3}$)|"
            r"(^20[0-9]{2}[_ ]?[A-Za-z]{2}[0-9]{0,3}$))",
            id_,
        ):

            # Ensure whitespace between year and id_
            id_ = re.sub(r"[\W_]+", "", id_)
            ind = re.search(r"[A18920]{1,2}[0-9]{2}", id_).end()
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
        # "G!kun||'homdima" or packed designaitons
        else:
            pass
    else:
        if id_ is None:
            warnings.warn(f"Received id 'None'.")
            return None
        else:
            warnings.warn(
                f"Did not understand type of id: {type(id_)}"
                f"\nShould be integer, float, or string."
            )
    return id_


# ------
# Quaero query methods
async def _query_quaero(id_, session, verbose):
    """Query quaero and parse result for a single object.

    Parameters
    ==========
    id_ : str, int, float
        Asteroid name, number, or designation.
    session : aiohttp.ClientSession
        asyncio session
    verbose : bool
        Print query diagnostics. Default is True.

    Returns
    =======
    dict or False
        Quaero response in json format if successful. False if query failed.
    """
    # Build query
    url = "https://api.ssodnet.imcce.fr/quaero/1/sso/search"

    params = {
        "q": f'type:("Dwarf Planet" OR Asteroid)' f' AND "{id_}"~0',
        "from": "rocks",
        "limit": 10000,
    }

    try:
        response = await session.request(method="GET", url=url, params=params)
        response_json = await response.json()

    except (requests.exceptions.RequestException, asyncio.exceptions.TimeoutError) as e:
        if verbose:
            warnings.warn(f"An error occurred during the name resolution: {e}")
        return False
    else:
        # No match found
        if "data" not in response_json.keys():
            if verbose:
                warnings.warn(f"Could not find data for id {id_}.")
            return False
        # Data is empty
        elif not response_json["data"]:
            if verbose:
                warnings.warn(f"Could not find match for id {id_}.")
            return False
        else:
            return response_json


def _parse_quaero_response(data_json, id_):
    """Parse JSON response3 from Quaero.

    Parameters
    ==========
    data_json : dict
        Quaero query response in json format.
    id_ : str, int, float
        Asteroid name, number, or designation.

    Returns
    =======
    tuple, (str, int or float, str), (np.nan, np.nan, np.nan)
        Tuple containing  asteroid name or designation and asteroid number, NaN
        if not numbered, and optionally the asteroid SsODNet id. If input was
        list of ids, returns a list of tuples. Tuple values are NaN if query
        failed.
    """
    for match in data_json:
        if match["name"] == id_:
            break
        if any([alias == id_ for alias in match["aliases"]]):
            break
    else:
        # Unclear which match is correct.
        return (np.nan, np.nan, np.nan)

    # Found match
    numeric = [int(alias) for alias in match["aliases"] if alias.isnumeric()]
    number = min(numeric) if numeric else np.nan

    return (match["name"], number, match["id"])
