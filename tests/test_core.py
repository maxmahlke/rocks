#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Author: Max Mahlke
    Date: 02 June 2020

    Test Rock and other classes

    Call as:	pytest test_class.py
"""
from os import path

import json
import numpy as np
import pytest

from rocks.core import Rock

IDs = ["ceres", 2, 4.0]
NANUS = [(1, "Ceres"), (2, "Pallas"), (4, "Vesta")]
TAX = ["C", "B", "V"]


# MONKEYPATCH
# Read from file rather than query ssodnet for test
def read_data(name):
    path_data = path.join(path.dirname(__file__), f"data/{name}_datacloud.json")

    with open(path_data, "r") as file_:
        data = json.load(file_)

    return data["data"][name]


@pytest.mark.parametrize("id_, nanu, tax", zip(IDs, NANUS, TAX), ids=str)
def test_instantiation(id_, nanu, tax, monkeypatch):
    """Verify class instantiation with str, int, float."""

    monkeypatch.setattr(tools, "get_data", read_data)

    SSO = Rock(id_)
    assert (SSO.number, SSO.name) == nanu
    assert SSO.taxonomy == tax


@pytest.mark.parametrize("id_, nanu, tax", zip(IDs, NANUS, TAX), ids=str)
def test_partial_instantiation(id_, nanu, tax, monkeypatch):
    """Verify partial class instantiation with "only"-keyword."""

    monkeypatch.setattr(tools, "get_data", read_data)

    SSO = Rock(id_, ["taxonomy"])
    assert (SSO.number, SSO.name) == nanu
    assert SSO.taxonomy == tax
    assert not hasattr(SSO, "albedo")


def test_failed_instantiation(monkeypatch):
    """Verify failed class instantiation."""
    SSO = Rock(None)
    np.testing.assert_equal(SSO.name, np.nan)

    with pytest.raises(TypeError):
        SSO = Rock(1, only={})
    with pytest.raises(TypeError):
        SSO = Rock(1, only=[2])

    monkeypatch.setattr(tools, "get_data", lambda x: False)
    SSO = Rock(1)
    assert hasattr(SSO, "albedo") is False

    monkeypatch.setattr(tools, "get_data", lambda x: {"datacloud": None})
    SSO = Rock(1)
    assert hasattr(SSO, "albedo") is False

    monkeypatch.setattr(tools, "get_data", lambda x: {"datacloud": {}})
    SSO = Rock(1)
    np.testing.assert_equal(SSO.albedo, np.nan)
    np.testing.assert_equal(SSO.taxonomy, None)
    np.testing.assert_equal(SSO.taxonomies, [])


def test_class_dunders(monkeypatch):
    """Verifies class dunder methods."""
    monkeypatch.setattr(tools, "get_data", read_data)

    ceres = Rock(1)
    pallas = Rock(2)

    # hash
    my_ssos = {ceres: "1", "Pallas": pallas}

    # repr and str
    print(my_ssos)
    print(ceres)

    # comparison
    assert ceres != pallas
    assert ceres != 1

    my_ssos = [ceres, pallas]
    my_ssos = sorted(my_ssos)

    assert ceres <= pallas
    assert pallas >= ceres
    assert ceres < pallas
    assert pallas > ceres


def test_weighted_average():
    """Verify input check and computation of weighted average."""
    ceres = Rock(1)
    ceres.albedos.weighted_average()

    with pytest.raises(TypeError):
        ceres.taxonomies.weighted_average()


def test_plots():
    """Verify scatter plot and histogram creation."""
    ceres = Rock(1)
    ceres.albedos.scatter()
    ceres.albedos.hist()
