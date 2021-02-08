#! /usr/bin/env python
"""Test suit for rocks.utils module.
"""

import json
import os
import warnings

import pandas as pd
import pickle
import pytest
import requests

import rocks


def test_create_index(monkeypatch):
    """Tests index creation routine with cached file and no missing entries."""

    def read_fwf_monkey(url, colspecs, names):
        numbered = pd.read_csv(
            os.path.join(os.path.dirname(__file__), "data/mpc_numbered.csv")
        )
        return numbered[:1000]  # type: ignore

    monkeypatch.setattr(pd, "read_fwf", read_fwf_monkey)
    rocks.utils.create_index()


def test_read_index():
    """Test availability and readability of index."""

    # Availability
    assert os.path.isfile(rocks.PATH_INDEX)

    # Readability
    index = rocks.utils.read_index()
    assert isinstance(index, pd.DataFrame)


@pytest.mark.parametrize(
    "update",
    [
        {"parameters": {"osculating_elements": {"semi_major_axis": 0}}},
        {"parameters": {"osculating_elements": None}},
        {"parameters": {"osculating_elements": [{"semi_major_axis": 0}]}},
    ],
)
def test_update_ssoCard(update):
    """Test updating of nested dict."""
    rocks.utils.update_ssoCard(rocks.TEMPLATE, update)


@pytest.mark.parametrize("id_", [9, "doesnotexist", "Ceres"])
def test_get_ssoCard(id_):
    warnings.filterwarnings("ignore", "UserWarning")
    card = rocks.utils.get_ssoCard(id_, only_cache=True)

    if id_ == "Ceres":
        assert isinstance(card, dict)
    else:
        assert card is None
