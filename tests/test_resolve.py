#!/usr/bin/env python
"""Test rocks.resolve module."""

import numpy as np
import pandas as pd
import pytest

import rocks


@pytest.mark.parametrize(
    "id, type, props",
    [
        (1, "asteroid", {"name": "Ceres", "number": 1, "id": "Ceres"}),
        ("Mette", "asteroid", {"name": "Mette", "number": 1727, "id": "Mette"}),
        ("67P", "comet", {"name": "67P", "id": "67P"}),
        ("moon", "satellite", {"name": "Moon", "id": "Moon"}),
        (
            "europa",
            "asteroid",
            {"name": "Europa", "number": 52, "id": "Europa_(Asteroid)"},
        ),
        ("EOS", "asteroid", {"name": "Eos", "number": 221, "id": "Eos"}),
        ("edUARda", "asteroid", {"name": "Eduarda", "number": 340, "id": "Eduarda"}),
        (
            "1999 vh114",
            "asteroid",
            {"name": "1999 VH114", "number": 23004, "id": "1999_VH114"},
        ),
    ],
)
def test_id_sync(id, type, props):
    """Test rocks.id function with single asteroids, comets, satellites."""

    id = rocks.id(id, type=type)
    assert isinstance(id, rocks.resolve.Id)

    for key, val in props.items():
        assert getattr(id, key) == val


@pytest.mark.parametrize(
    "id, type, props",
    [
        ([1, 2], "asteroid", [{"name": "Ceres"}, {"name": "Pallas"}]),
        (["67P", "101P"], "comet", [{"name": "67P"}, {"name": "101P"}]),
        (["moon", "io"], "satellite", [{"name": "Moon"}, {"name": "Io"}]),
        # set, np.ndarray, pd.Series
        (set([1, 2]), "asteroid", [{"name": "Ceres"}, {"name": "Pallas"}]),
        (np.array([1, 2]), "asteroid", [{"name": "Ceres"}, {"name": "Pallas"}]),
        (pd.Series(data=[1, 2]), "asteroid", [{"name": "Ceres"}, {"name": "Pallas"}]),
    ],
)
def test_id_async(id, type, props):
    """Test rocks.id function with list of asteroids, comets, satellites."""

    ids = rocks.id(id, type=type)
    assert all(isinstance(id, rocks.resolve.Id) for id in ids)

    for id, prop in zip(ids, props):
        for key, val in prop.items():
            assert getattr(id, key) == val


@pytest.mark.parametrize("id", [np.nan, None, 0])
def test_id_sync_bad_input(id):
    """Test rocks.id function for single queries with bad input."""
    id = rocks.id(id)
    assert isinstance(id, rocks.resolve.Id)
    assert id.name is None


@pytest.mark.parametrize("ids", [[], [np.nan, None, 0]])
def test_id_async_bad_input(ids):
    """Test rocks.id function for multiple queries with bad input."""
    ids = rocks.id(ids)

    for id in ids:
        assert isinstance(id, rocks.resolve.Id)
        assert id.name is None


@pytest.mark.parametrize(
    "id_, expected",
    [
        (1, ("Ceres", 1, "Ceres")),
        ("Mette", ("Mette", 1727, "Mette")),
    ],
)
def test_local_resolution(id_, expected, monkeypatch):
    """Ensure that local resolution works. Remote resolution is supressed."""

    # Mock return for quaero query so remote queries fail
    async def mockreturn(identifier, session):
        return None

    monkeypatch.setattr(rocks.resolve, "_query_quaero", mockreturn)

    # Run local name resolution
    name_expected, number_expected, id_expected = expected

    name_local, number_local, id_local = rocks.id(id_, return_id=True)

    np.testing.assert_equal(name_local, name_expected)
    np.testing.assert_equal(number_local, number_expected)
    np.testing.assert_equal(id_local, id_expected)


@pytest.mark.parametrize(
    "id_, expected",
    [
        (1, ("Ceres", 1, "Ceres")),
        ("Mette", ("Mette", 1727, "Mette")),
        ("europa", ("Europa", 52, "Europa_(Asteroid)")),
        ("1882_BA", ("Eos", 221, "Eos")),
        ("edUARda", ("Eduarda", 340, "Eduarda")),
        ("1999 vh114", ("1999 VH114", 23004, "1999_VH114")),
        ("K20A01B", ("2020 AB1", np.nan, "2020_AB1")),
    ],
)
def test_remote_resolution(id_, expected):
    """Ensure that remote resolution works. Local resolution is supressed."""

    # Run remote name resolution
    name_expected, number_expected, id_expected = expected

    name_local, number_local, id_local = rocks.id(id_, return_id=True, local=False)

    np.testing.assert_equal(name_local, name_expected)
    np.testing.assert_equal(number_local, number_expected)
    np.testing.assert_equal(id_local, id_expected)


# def test_comet_remote(id_, expected):
#     """Testing cometary designation resolution. Should be merged with other tests."""
#
#     "P/Schwassmann-Wachmann"
