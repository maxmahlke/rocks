#!/usr/bin/env python

"""Implement asteroid identification module.
"""
import asyncio
import re
import warnings

import aiohttp
import nest_asyncio
import numpy as np
import pandas as pd
from tqdm import tqdm

import rocks

# Run asyncio nested for jupyter notebooks, GUIs, ...
nest_asyncio.apply()


def identify(id_, progress=False):
    """Resolve names and numbers of one or more minor bodies using identifiers.

    Parameters
    ==========
    id_ : str, int, float, list, set, np.ndarray, pd.Series
        One or more identifying names or numbers to resolve.
    progress : bool or tdqm.std.tqdm
       If progress is True, this is a progress bar instance. Else, it's False.

    Returns
    =======
    tuple, list of tuple : (str, int, str), (None, np.nan, None)
        List containing len(id_) tuples. Each tuple contains the asteroid's
        name, number, and SsODNet ID if the identifier was resolved. Otherwise,
        the values are None for name and SsODNet and np.nan for the number.
        If a single asteroid is identified, a tuple is returned.

    Notes
    =====
    Name resolution is first attempted locally, then remotely via quaero. If
    the asteroid is unnumbered, it's number is returned as np.nan.
    """
    if isinstance(id_, (str, int, float)):
        id_ = [id_]
    elif isinstance(id_, pd.Series):
        id_ = id_.values
    elif isinstance(id_, (set, range)):
        id_ = list(id_)
    elif id_ is None:
        warnings.warn(f"Received id_ of type {type(id_)}.")
        return [(None, np.nan, None)]
    elif not isinstance(id_, (list, np.ndarray)):
        raise TypeError(
            f"Received id_ of type {type(id_)}, expected one of: "
            f"str, int, float, list, np.ndarray, pd.Series"
        )

    if progress:
        progress = tqdm(desc="Identifying rocks : ", total=len(id_))

    # Run async loop to resolve names
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(_identify(id_, progress))

    if progress:
        progress.close()

    if len(id_) == 1:
        results = results[0]

    return results


async def _identify(id_, progress):
    """Resolve asteroid name asynchronously. First attempts local lookup, then
    queries quaero.

    Parameters
    ==========
    id_ : str, int, float, list, set, np.ndarray, pd.Series
        One or more identifying names or numbers to resolve.

    Returns
    =======
    tuple : (str, int or float, str), (None, np.nan, None)
        Tuple containing the asteroid's name, number, and SsODNet ID if the
        identifier was resolved. Otherwise, the values are None for name and
        SsODNet and np.nan for the number.
    progress : bool or tdqm.std.tqdm
       If progress is True, this is a progress bar instance. Else, it's False.
    """
    INDEX = rocks.utils.read_index()

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout()) as session:

        tasks = [
            asyncio.ensure_future(_query_and_resolve(i, session, INDEX, progress))
            for i in id_
        ]

        results = await asyncio.gather(*tasks)

    return results


async def _query_and_resolve(id_, session, INDEX, progress):
    """Standardize identifier, do local look-up, else query quaero and parser
    methods asynchronously. Call with identify function."""

    if progress:
        progress.update()

    id_ = standardize_id_(id_)

    # Try local resolution
    if isinstance(id_, (int)):
        if id_ in INDEX.number.values:
            name, ssodnet_id = INDEX.loc[INDEX.number == id_, ["name", "id_"]].iloc[0]
            return (name, id_, ssodnet_id)
    elif isinstance(id_, (str)):
        if id_ in INDEX.name.values:
            number, ssodnet_id = INDEX.loc[INDEX.name == id_, ["number", "id_"]].iloc[0]
            return (id_, number, ssodnet_id)
        elif id_ in INDEX.id_.values:
            name, number = INDEX.loc[INDEX.id_ == id_, ["name", "number"]].iloc[0]
            return (name, number, id_)

    if pd.isnull(id_) or not id_:  # covers None, np.nan, empty string
        return (None, np.nan, None)

    # Local resolution failed, do remote query
    response = await _query_quaero(id_, session)

    if response:
        name, number, ssodnet_id = _parse_quaero_response(response["data"], str(id_))
        if isinstance(ssodnet_id, str):
            return (name, number, ssodnet_id)

    return (None, np.nan, None)


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
        try:
            id_ = int(float(id_))
            return id_
        except ValueError:
            pass

        # Empty string
        if not id_:
            return None

        # Asteroid name
        elif re.match(r"^[A-Za-z ]*$", id_):
            # guess correct capitalization
            id_ = " ".join([sub.capitalize() for sub in id_.split(" ")])  # type: ignore

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
async def _query_quaero(id_, session):
    """Query quaero and parse result for a single object.

    Parameters
    ==========
    id_ : str, int, float
        Asteroid name, number, or designation.
    session : aiohttp.ClientSession
        asyncio session

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

    response = await session.request(method="GET", url=url, params=params)
    response_json = await response.json()

    # No match found
    if "data" not in response_json.keys():
        warnings.warn(f"Could not find data for id {id_}.")
        return False
    # Data is empty
    elif not response_json["data"]:
        warnings.warn(f"Could not find match for id {id_}.")
        return False
    else:
        return response_json


def _parse_quaero_response(data_json, id_):
    """Parse JSON response from Quaero.

    Parameters
    ==========
    data_json : list of dict
        Quaero query response in json format.
    id_ : str, int, float
        Asteroid name, number, or designation.

    Returns
    =======
    tuple : (str, int, str), (None, np.nan, None)
        Tuple containing the asteroid's name, number, and SsODNet ID if the
        identifier was resolved. Otherwise, the values are None for name and
        SsODNet and np.nan for the number.
    """

    # convert all ids to lowercase strings for capitals-agnostic comparison
    id_ = str(id_).lower()

    for match in data_json:
        if match["name"].lower() == id_:
            break
        elif any([alias.lower() == id_ for alias in match["aliases"]]):
            break
    else:
        # Unclear which match is correct.
        warnings.warn(f"Could not find match for id {id_}.")
        return (None, np.nan, None)

    # Found match
    numeric = [int(alias) for alias in match["aliases"] if alias.isnumeric()]
    number = min(numeric) if numeric else np.nan
    return (match["name"], number, match["id"])
