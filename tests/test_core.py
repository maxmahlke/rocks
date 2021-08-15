#!/usr/bin/env python

""" Test serialization and deserialization of ssoCard into Rock class. """

import keyword
import os
import json

import numpy as np
import pandas as pd
import pytest

import rocks
from rocks import Rock

# Asteroids with cached ssoCards for testing
TEST_CASES = [
    (1, "Ceres", "Ceres"),
    (4, "Vesta", "Vesta"),
    (20, "Massalia", "Massalia"),
    (24, "Themis", "Themis"),
    (158, "Koronis", "Koronis"),
    (1002, "Olbersia", "Olbersia"),
    (101955, "Bennu", "Bennu"),
    (385186, "1994 AW1", "1994_AW1"),
    (np.nan, "2016 FJ", "2016_FJ"),
]

# ------
# Monkeypatches for local data access
def get_ssocard_from_test_data(id_):
    """Monkeypatch function to read cached ssoCards from test files rather than
    query SsODNet.

    Parameter
    =========
    name : str
        The SsODNet ID of the object.

    Returns
    =======
    dict
        The ssoCard of the object.
    """
    PATH_DATA = os.path.join(os.path.dirname(__file__), f"data/ssocards/{id_}.json")

    with open(PATH_DATA, "r") as file_:
        data = json.load(file_)

    return data[id_]


# ------
# Test instantiation
@pytest.mark.parametrize("number_name_id", TEST_CASES, ids=str)
def test_instantiation_with_types(number_name_id, monkeypatch):
    """Verify class instantiation with str, int, float with local ssoCards.

    Parameters
    ==========
    number_name_id : list
        List containing the asteroid's name, number, and SsODNet ID.
    """
    monkeypatch.setattr(rocks.ssodnet, "get_ssocard", get_ssocard_from_test_data)

    number, name, id_ = number_name_id

    for identifier in [number, name, id_, float(number), str(number)]:
        _ = Rock(identifier)


@pytest.mark.parametrize("number_name_id", TEST_CASES, ids=str)
def test_skip_id_check(number_name_id, monkeypatch):
    """Verify class instantiation when providing SsODNet ID.

    Parameters
    ==========
    number_name_id : list
        List containing the asteroid's name, number, and SsODNet ID.
    """

    monkeypatch.setattr(rocks.ssodnet, "get_ssocard", get_ssocard_from_test_data)

    _, _, id_ = number_name_id
    _ = Rock(id_, skip_id_check=True)


@pytest.mark.parametrize("name, number, id_", TEST_CASES[:-1], ids=str)
def test_custom_ssocard(name, number, id_, monkeypatch):
    """Test parsing ssoCards provided by user."""

    ssocard = get_ssocard_from_test_data(id_)

    # Adapt the ssoCard to verify that the custom own is used
    ssocard["parameters"]["physical"]["albedo"]["value"] = 44

    # Test retrieval by passing string or list
    ast = Rock(id_, skip_id_check=True, ssocard=ssocard)
    assert ast.albedo.value == 44


# ------
# Test parameter access
@pytest.mark.parametrize("number, name, id_", TEST_CASES[:-1], ids=str)
def test_parameter_access(number, name, id_, monkeypatch):
    """Test retrieval of single datacloud catalogues."""

    monkeypatch.setattr(rocks.ssodnet, "get_ssocard", get_ssocard_from_test_data)

    # Ensure that the input from the JSON corresponds to the serialized parameters
    # in the Rock instances
    sso = Rock(id_, skip_id_check=True)

    # Read JSON file
    data = get_ssocard_from_test_data(id_)

    # Flatten the json into a single-level dictionary for easy dereferencing
    flattened_json = pd.json_normalize(data).to_dict(orient="records")[0]

    # For some chosen end-members in the JSON card, ensure that the value
    # corresponds to the value in the Rock instance
    for key, value_json in flattened_json.items():

        # Phase and colour à la Generic/Johnson are annoying to parse
        if "/" in key:
            continue

        # these get unpacked into lists
        if "spin" in key:
            continue

        # Only check the end-members as the other objects get de-serialized
        if key.endswith("value"):

            value_rock = rocks.utils.rgetattr(sso, key)

            if isinstance(value_rock, float):
                assert float(value_rock) == float(value_json)
            else:
                assert value_rock == value_json


# @pytest.mark.parametrize("id_, nanu, tax", zip(IDs, NANUS, TAX), ids=str)
# def test_partial_instantiation(id_, nanu, tax, monkeypatch):
#     """Verify partial class instantiation with "only"-keyword."""

#     monkeypatch.setattr(tools, "get_data", read_data)

#     SSO = Rock(id_, ["taxonomy"])
#     assert (SSO.number, SSO.name) == nanu
#     assert SSO.taxonomy == tax
#     assert not hasattr(SSO, "albedo")


# def test_failed_instantiation(monkeypatch):
#     """Verify failed class instantiation."""
#     SSO = Rock(None)
#     np.testing.assert_equal(SSO.name, np.nan)

#     with pytest.raises(TypeError):
#         SSO = Rock(1, only={})
#     with pytest.raises(TypeError):
#         SSO = Rock(1, only=[2])

#     monkeypatch.setattr(tools, "get_data", lambda x: False)
#     SSO = Rock(1)
#     assert hasattr(SSO, "albedo") is False

#     monkeypatch.setattr(tools, "get_data", lambda x: {"datacloud": None})
#     SSO = Rock(1)
#     assert hasattr(SSO, "albedo") is False

#     monkeypatch.setattr(tools, "get_data", lambda x: {"datacloud": {}})
#     SSO = Rock(1)
#     np.testing.assert_equal(SSO.albedo, np.nan)
#     np.testing.assert_equal(SSO.taxonomy, None)
#     np.testing.assert_equal(SSO.taxonomies, [])


# def test_class_dunders(monkeypatch):
#     """Verifies class dunder methods."""
#     monkeypatch.setattr(tools, "get_data", read_data)

#     ceres = Rock(1)
#     pallas = Rock(2)

#     # hash
#     my_ssos = {ceres: "1", "Pallas": pallas}

#     # repr and str
#     print(my_ssos)
#     print(ceres)

#     # comparison
#     assert ceres != pallas
#     assert ceres != 1

#     my_ssos = [ceres, pallas]
#     my_ssos = sorted(my_ssos)

#     assert ceres <= pallas
#     assert pallas >= ceres
#     assert ceres < pallas
#     assert pallas > ceres


# def test_weighted_average():
#     """Verify input check and computation of weighted average."""
#     ceres = Rock(1)
#     ceres.albedos.weighted_average()

#     with pytest.raises(TypeError):
#         ceres.taxonomies.weighted_average()


# def test_plots():
#     """Verify scatter plot and histogram creation."""
#     ceres = Rock(1)
#     ceres.albedos.scatter()
#     ceres.albedos.hist()
