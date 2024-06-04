#!/usr/bin/env python
"""Test rocks.resolve module."""

import asyncio
import json
import os

import aiohttp
import numpy as np
import pandas as pd
import pytest

import rocks


@pytest.mark.parametrize(
    "id_, expected",
    [
        # (1, ("Ceres", 1, "Ceres")),
        ("Mette", ("Mette", 1727, "Mette")),
        ("europa", ("Europa", 52, "Europa_(Asteroid)")),
        ("EOS", ("Eos", 221, "Eos")),
        ("edUARda", ("Eduarda", 340, "Eduarda")),
        ("1999 vh114", ("1999 VH114", 23004, "1999_VH114")),
        ("z1882", ("2007 HE45", 611882, "2007_HE45")),
        ("Z1882", ("2006 SQ139", 351882, "2006_SQ139")),
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
        # (1, ("Ceres", 1, "Ceres")),
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
