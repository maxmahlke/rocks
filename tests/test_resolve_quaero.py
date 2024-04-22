"""Test quaero-query functionality."""

import asyncio
import numpy as np
import pytest

from rocks.resolve import quaero

ASTEROIDS = {
    # query string: expected result
    "1": {"name": "Ceres", "number": 1, "type": "Dwarf Planet"},
    "pallas": {"name": "Pallas", "number": 2, "type": "Asteroid"},
    67: {"name": "Asia", "number": 67, "type": "Asteroid"},
    "2022ab": {"name": "2022 AB", "number": None, "type": "Asteroid"},
    "'Aylo'chaxnim": {"name": "'Aylo'chaxnim", "number": 594913, "type": "Asteroid"},
}

COMETS = {
    # comets
    #   - if multiple matches due to name and fragmets, return main piece
    #   e.g. 'Chernykh' -> '101P', '101P-A', '101P-B', always return '101P'
    #   name, number: name is first alias, number is name in ssodnet database
    "Chernykh": {"name": "Chernykh", "number": "101P", "type": "Comet"},
    "101P-A": {"name": "Chernykh", "number": "101P-A", "type": "Comet"},
    "P/1977 Q1": {"name": "Chernykh", "number": "101P", "type": "Comet"},
    "67p": {"name": "Churyumov-Gerasimenko", "number": "67P", "type": "Comet"},
}

SATELLITES = {
    # satellites
    #   - number is secondary, name is more important, and parent body
    "moon": {"name": "Moon", "number": 301, "type": "Satellite"},
}

GARBAGE = {
    "N/A": {"name": None, "number": None, "type": None},
    None: {"name": None, "number": None, "type": None},
    np.nan: {"name": None, "number": None, "type": None},
    "": {"name": None, "number": None, "type": None},
    "[]": {"name": None, "number": None, "type": None},
    "0": {"name": None, "number": None, "type": None},
    "039123901239410": {"name": None, "number": None, "type": None},
}

AMBIGUOUS = {
    "Io": {"name": "Io", "number": 501, "type": "Satellite"},
}


@pytest.mark.parametrize("id", ASTEROIDS.keys())
def test_query_asteroids(id):
    """Ensure that query returns valid JSON with expected type of body."""

    match = asyncio.run(quaero.query(id=id, type="asteroid"))

    for key in ["name", "number", "type"]:
        assert key in match
        assert match[key] == ASTEROIDS[id][key]


@pytest.mark.parametrize("id", COMETS.keys())
def test_query_comets(id):
    """Ensure that query returns valid JSON with expected type of body."""

    match = asyncio.run(quaero.query(id=id, type="comet"))

    for key in ["name", "number", "type"]:
        assert key in match
        assert match[key] == COMETS[id][key]


@pytest.mark.parametrize("id", SATELLITES.keys())
def test_query_satellites(id):
    """Ensure that query returns valid JSON with expected type of body."""

    match = asyncio.run(quaero.query(id=id, type="satellite"))

    for key in ["name", "number", "type"]:
        assert key in match
        assert match[key] == SATELLITES[id][key]


def test_query_mixed():
    pass


@pytest.mark.parametrize("id", GARBAGE.keys())
def test_query_garbage(id):
    """Ensure that query returns valid JSON with expected type of body."""

    match = asyncio.run(quaero.query(id=id, type="asteroid"))

    for key in ["name", "number", "type"]:
        assert key in match
        assert match[key] == GARBAGE[id][key]


# @pytest.mark.parametrize("id", AMBIGUOUS.keys())
# def test_query_ambiguous(id):
#     """Ensure that query returns valid JSON with expected type of body."""
#
#     match = asyncio.run(quaero.query(id=id, type=['asteroid', 'satellite']))
#
#     for key in ["name", "number", "type"]:
#         assert key in match
#         assert match[key] == AMBIGUOUS[(id, type)][key]
