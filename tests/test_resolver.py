#!/usr/bin/env python
#
"""Test rocks.resolve module.
 """

import asyncio
import json
import os

import aiohttp
import numpy as np
import pandas as pd
import pytest

import rocks


@pytest.mark.parametrize("id_", ["Mette", "Vesta"])
def test_parsing_quaero_query(id_):
    """Test locally parsing of quaero response, one succesful and one failed.

    Parameters
    ==========
    id_ : str
        Identifier passed to quaero query.

    Notes
    =====
    Depends on Mette Quaero query in tests/data.
    """
    with open(
        os.path.join(os.path.dirname(__file__), "data/quaero/mette.json"), "r"
    ) as file_:
        data_json = json.load(file_)

    name, _, _ = rocks.resolve._parse_quaero_response([data_json], id_)

    if id_ == "Mette":
        name == "Mette"
    else:
        name is None


# Name resolution starts with parsing input identifier
@pytest.mark.parametrize(
    "id_, expected",
    [
        # float, int
        (19, 19),
        (19.0, 19),
        # Nones
        (None, None),
        ("", None),
        (np.nan, None),
        # str
        ("19", 19),
        ("19.0", 19),
        ("Astraea", "Astraea"),
        ("eos", "Eos"),
        ("SCHWARTZ", "Schwartz"),
        ("G!kun||'homdima", "G!kun||'homdima"),
        ("1290 T-1", "1290 T-1"),
        ("2010 OR", "2010 OR"),
        ("1290_T-1", "1290 T-1"),
        ("2001je2", "2001 JE2"),
        ("2001_JE2", "2001 JE2"),
        ("2014_ye64", "2014 YE64"),
        ("2004BQ102", "2004 BQ102"),
        ("A999AB2", "1999 AB2"),
    ],
    ids=str,
)
def test_id_standardization(id_, expected):
    """Ensure correct handling of floats, ints, NaNs, Nones, and parsing of str."""

    parsed_id = rocks.resolve.standardize_id_(id_)
    np.testing.assert_equal(parsed_id, expected)


# Format: ID - Expected Name, Number - Boolean local resolution
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
    ["New Hampshire", ("New Hampshire", 503033), True],
    # ["P/PANSTARRS", ("P/2014 M4", np.nan), False],  # not supporting comets
    # for now
    ["1950 RW", ("Gyldenkerne", 5030), False],
    ["2001je2", ("2001 JE2", 131353), True],
    ["2001_JE2", ("2001 JE2", 131353), True],
    ["2010 OR", ("2010 OR", np.nan), False],
    ["2014_ye64", ("2014 YE64", 545135), True],
    ["2004BQ102", ("2004 BQ102", 450274), True],
    ["A999AB2", ("1999 AB2", 53103), True],
    [9e7, (None, np.nan), False],
    [None, (None, np.nan), True],
    [np.nan, (None, np.nan), True],
]

SSO_IDS = [it[0] for it in IDS_RESULTS_LOCAL]
EXPECTED = [it[1] for it in IDS_RESULTS_LOCAL]
LOCAL = [it[2] for it in IDS_RESULTS_LOCAL]
# ------
@pytest.mark.parametrize("id_, expected", zip(SSO_IDS, EXPECTED), ids=str)
def test_query_and_resolve(id_, expected):
    """Test response of quaero queries. These can be local or remote queries."""

    name, number = rocks.identify(id_)
    np.testing.assert_equal((name, number), expected)


@pytest.mark.parametrize(
    "identifier",
    [SSO_IDS, np.array(SSO_IDS), pd.Series(SSO_IDS), set(SSO_IDS), ("invalid")],
    ids=["list", "array", "series", "set", "tuple"],
)
def test_many_identifiers(identifier):
    """Common-case lookups of many SSO ids, passed as list, array, Series"""
    if isinstance(identifier, tuple):
        with pytest.raises(ValueError):
            rocks.identify(identifier)
    else:
        rocks.identify(identifier)


@pytest.mark.parametrize("identifier, expected, local", IDS_RESULTS_LOCAL)
def test_local_vs_remote(identifier, expected, local, monkeypatch):
    """Ensure that queries which can be resolved locally are run locally"""

    # Mock return for quaero query
    async def mockreturn(identifier, session):
        return False

    monkeypatch.setattr(rocks.resolve, "_query_quaero", mockreturn)
    INDEX = rocks.utils.read_index()

    async def _identify(identifier):
        async with aiohttp.ClientSession() as session:
            results = await asyncio.gather(
                *[
                    rocks.resolve._query_and_resolve(i, session, INDEX, progress=False)
                    for i in identifier
                ]
            )
        return results

    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(_identify([identifier]))

    if local:
        np.testing.assert_equal(result[0][:2], expected)
    else:
        np.testing.assert_equal(result[0][:2], (None, np.nan))
