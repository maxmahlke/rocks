#!/usr/bin/env python

"""Test rocks.identify module
"""
import asyncio

import aiohttp
import numpy as np
import pandas as pd
import pytest

from .context import rocks

# ------
# Test identifiers and expected results

# Format: ID - Expected Name, Number - Boolean locaal resolution
IDS_RESULTS_LOCAL = [
    [19, ("Fortuna", 19), True],
    ["192", ("Nausikaa", 192), True],
    ["Astraea", ("Astraea", 5), True],
    [5, ("Astraea", 5), True],
    ["eos", ("Eos", 221), True],
    ["SCHWARTZ", ("Schwartz", 13820), True],
    ["G!kun||'homdima", ("G!kun||'homdima", 229762), True],
    ["1290 T-1", ("1290 T-1", 12946), True],
    ["1290_T-1", ("1290 T-1", 12946), True],
    ["P/PANSTARRS", ("P/2014 M4", np.nan), False],
    ["1950 RW", ("Gyldenkerne", 5030), False],
    ["2001je2", ("2001 JE2", 131353), True],
    ["2001_JE2", ("2001 JE2", 131353), True],
    ["2010 OR", ("2010 OR", np.nan), False],
    ["2014_ye64", ("2014 YE64", 545135), True],
    ["2004BQ102", ("2004 BQ102", 450274), True],
    ["A999AB2", ("1999 AB2", 53103), True],
    [9e7, (np.nan, np.nan), False],
    [None, (np.nan, np.nan), True],
    [np.nan, (np.nan, np.nan), True],
]

# ------
# Test quaero, no local resolution of identifier.
SSO_IDS = [it[0] for it in IDS_RESULTS_LOCAL]
EXPECTED = [it[1] for it in IDS_RESULTS_LOCAL]
LOCAL = [it[2] for it in IDS_RESULTS_LOCAL]

NUMBER_NAME, NAME_NUMBER = tools.read_index()


@pytest.mark.parametrize("id_, expected", zip(SSO_IDS, EXPECTED), ids=str)
def test_query_and_resolve(id_, expected):
    """Test response of quaero queries."""

    async def _identify(identifier):
        async with aiohttp.ClientSession() as session:
            results = await asyncio.gather(
                *[
                    identify._query_and_resolve(i, session, NUMBER_NAME, NAME_NUMBER)
                    for i in identifier
                ]
            )
        return results

    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(_identify([id_]))
    name, number = results[0]
    np.testing.assert_equal((name, number), expected)


@pytest.mark.parametrize(
    "identifier",
    [SSO_IDS, np.array(SSO_IDS), pd.Series(SSO_IDS)],
    ids=["list", "array", "series"],
)
def test_many_identifiers(identifier):
    """Common-case lookups of many SSO ids, passed as list, array, Series"""
    identify.identify(identifier)


@pytest.mark.parametrize("identifier, expected, local", IDS_RESULTS_LOCAL)
def test_local_vs_remote(identifier, expected, local, monkeypatch):
    """Ensure that queries which can be resolved locally are run locally"""

    # Mock return for quaero query
    async def mockreturn(identifier, session):
        return False

    monkeypatch.setattr(identify, "_query_quaero", mockreturn)

    async def _identify(identifier):
        async with aiohttp.ClientSession() as session:
            results = await asyncio.gather(
                *[
                    identify._query_and_resolve(i, session, NUMBER_NAME, NAME_NUMBER)
                    for i in identifier
                ]
            )
        return results

    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(_identify([identifier]))

    if local:
        np.testing.assert_equal(result[0], expected)
    else:
        np.testing.assert_equal(result[0], (np.nan, np.nan))
