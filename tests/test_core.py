#!/usr/bin/env python
"""Test serialization and deserialization of ssoCard and Rock class."""
import json

import numpy as np
import pytest

import rocks
from rocks.core import OrbitalElements, Spin

# Mock the get_ssocard function to read from test data instead of making remote calls
def load_ssocard_from_test_data(id_):
    """Load ssoCard from test data. """

    USE_UNRELEASED_SSOCARDS = True
    PATH_TEST_DATA = "tests/data/1.2.0" if USE_UNRELEASED_SSOCARDS else "tests/data"

    with open(f"{PATH_TEST_DATA}/{id_}.json", "r") as f:
        return json.load(f)

rocks.ssodnet.get_ssocard = lambda x: load_ssocard_from_test_data(x)

# ------
# Instantiation

# ------
# Parameter Access

# Albedo
ALBEDO_EXISTS = [1, 221]
ALBEDO_MISSING = [92384, 385188]


@pytest.mark.parametrize(
    "id_, exists",
    [(id_, True) for id_ in ALBEDO_EXISTS] + [(id_, False) for id_ in ALBEDO_MISSING],  # type: ignore
    ids=str,
)
def test_albedo(id_, exists):
    """Verify albedo parameter access."""

    rock = rocks.Rock(id_)

    if exists:
        # Albedo is instantiated
        assert isinstance(rock.albedo.value, float)

        # Albedo is not NaN
        assert np.isfinite(rock.albedo.value)

        # Albedo evaluates as True
        assert rock.albedo

    else:
        # Albedo is instantiated and NaN
        assert np.isnan(rock.albedo.value)

        # Albedo evaluates as False
        assert not rock.albedo


# COLOR
COLOR_EXISTS = [221, 494721]
COLOR_MISSING = [594721]

# Misc/Atlas.orange
# Generic/Johnson.V


@pytest.mark.parametrize(
    "id_, exists",
    [(id_, True) for id_ in COLOR_EXISTS] + [(id_, False) for id_ in COLOR_MISSING],  # type: ignore
    ids=str,
)
def test_color(id_, exists):
    """Verify color parameter access."""

    rock = rocks.Rock(id_)

    if exists:
        # Color behaves like a mapping from color index to ColorEntry
        assert rock.color
        assert len(rock.color) > 0

        keys = list(rock.color.keys())
        assert all(isinstance(key, str) for key in keys)

        first_key = keys[0]
        first_entry = rock.color[first_key]

        assert first_entry.index.value == first_key
        assert isinstance(first_entry.color.value, float)
        assert any(np.isfinite(entry.color.value) for entry in rock.color.values())

        # Spot checks for known indices in test fixtures
        if id_ == 221:
            assert "B-V" in rock.color
            assert np.isfinite(rock.color["B-V"].color.value)
        if id_ == 494721:
            assert "g-i" in rock.color
            assert np.isfinite(rock.color["g-i"].color.value)

    else:
        # Empty mapping if no color is available
        assert len(rock.color) == 0
        assert not rock.color
        assert "B-V" not in rock.color
        assert rock.color.get("B-V") is None

# Phase
PHASE_EXISTS = [221]
PHASE_MISSING = [494721, 594721]

# Misc/Atlas.orange
# Generic/Johnson.V


@pytest.mark.parametrize(
    "id_, exists",
    [(id_, True) for id_ in PHASE_EXISTS] + [(id_, False) for id_ in PHASE_MISSING],  # type: ignore
    ids=str,
)
def test_phase_function(id_, exists):
    """Verify phase_function parameter access."""

    rock = rocks.Rock(id_)

    if exists:
        # Phase function behaves like a mapping from filter id to Phase entries
        assert rock.phase_function
        assert len(rock.phase_function) > 0

        keys = list(rock.phase_function.keys())
        assert all(isinstance(key, str) for key in keys)

        first_key = keys[0]
        first_entry = rock.phase_function[first_key]
        assert first_entry.id_filter.value == first_key

        # Backward-compatible shortcuts
        assert rock.phase_function.cyan is rock.phase_function["Misc/Atlas.cyan"]
        assert rock.phase_function.orange is rock.phase_function["Misc/Atlas.orange"]
        if "Generic/Johnson.V" in rock.phase_function:
            assert rock.phase_function.V is rock.phase_function["Generic/Johnson.V"]
        else:
            assert not rock.phase_function.V

        # Known finite filter in the test fixture
        assert np.isfinite(rock.phase_function.cyan.H.value)

    else:
        # Empty mapping if no phase function is available
        assert len(rock.phase_function) == 0
        assert not rock.phase_function
        assert "Misc/Atlas.cyan" not in rock.phase_function
        assert not rock.phase_function.cyan


# Spin
SPIN_EXISTS = ["Eos", "Ceres"]
SPIN_MISSING = ["2005_SO191", "2017_UE95"]


@pytest.mark.parametrize(
    "id_, exists",
    [(id_, True) for id_ in SPIN_EXISTS] + [(id_, False) for id_ in SPIN_MISSING],  # type: ignore
    ids=str,
)
def test_spin(id_, exists):
    """Verify spin parameter access for known and unknown spin states."""

    card = load_ssocard_from_test_data(id_)
    spins = card["parameters"]["physical"].get("spins", "")

    if exists:
        assert isinstance(spins, list)
        assert len(spins) > 0

        spin = Spin.model_validate(spins[0])
        assert isinstance(spin.id_.value, int)
        assert isinstance(spin.W0.value, float)
        assert spin.period_flag.value
        assert np.isfinite(spin.period.value)
        assert spin.period

    else:
        # v1.2.0 cards serialize unknown spin as an empty string
        assert spins == ""

        spin = Spin.model_validate({})
        assert not spin.period
        assert not spin.period_flag


def test_orbital_elements():
    """Verify OrbitalElements parses v1.2.0 dynamical fields."""

    card = load_ssocard_from_test_data("Eos")
    entry = card["parameters"]["dynamical"]["orbital_elements"]
    oe = OrbitalElements.model_validate(entry)

    assert isinstance(oe.number_observations.value, int)
    assert oe.number_observation is oe.number_observations
    assert np.isfinite(oe.ceu_epoch.value)
    assert np.isfinite(oe.pericenter_date.value)
    assert oe.ref_center.value
    assert oe.ref_plane.value
    assert oe.ref_epoch_timescale.value

    missing = OrbitalElements.model_validate({})
    assert missing.number_observations.value is None
    assert not missing.ceu_epoch
    assert not missing.pericenter_date
    assert not missing.ref_center



# Taxonomy
TAX_EXISTS = [1, 221]
TAX_MISSING = [293142, 385188]


@pytest.mark.parametrize(
    "id_, exists",
    [(id_, True) for id_ in TAX_EXISTS] + [(id_, False) for id_ in TAX_MISSING],  # type: ignore
    ids=str,
)
def test_taxonomy(id_, exists):
    """Verify taxonomy parameter access."""

    rock = rocks.Rock(id_)

    if exists:
        # Taxonomy is instantiated
        assert isinstance(rock.taxonomy.class_.value, str)

        # Taxonomy is not NaN
        assert rock.taxonomy.class_.value

        # Taxonomy evaluates as True
        assert rock.taxonomy

    else:
        # Taxonomy is instantiated and NaN
        assert not rock.taxonomy.class_.value

        # Taxonomy evaluates as False
        assert not rock.taxonomy


# ------
# Metadata access
def test_units():
    """Verify unit access."""

    rock = rocks.Rock(1)

    assert rock.diameter.unit == "km"
    assert rock.albedo.unit == ""
    assert rock.thermal_inertia.unit == "J.s^{-1/2}.K^{-1}.m^{-2}"


# ------
# Shortcuts


# @pytest.mark.parametrize("number_name_id", TEST_CASES, ids=str)
# def test_skip_id_check(number_name_id, monkeypatch):
#     """Verify class instantiation when providing SsODNet ID.

#     Parameters
#     ==========
#     number_name_id : list
#         List containing the asteroid's name, number, and SsODNet ID.
#     """

#     monkeypatch.setattr(rocks.ssodnet, "get_ssocard", get_ssocard_from_test_data)

#     _, _, id_ = number_name_id
#     _ = Rock(id_, skip_id_check=True)


# @pytest.mark.parametrize("name, number, id_", TEST_CASES[:-1], ids=str)
# def test_custom_ssocard(name, number, id_, monkeypatch):
#     """Test parsing ssoCards provided by user."""

#     ssocard = get_ssocard_from_test_data(id_)

#     # Adapt the ssoCard to verify that the custom own is used
#     ssocard["parameters"]["physical"]["albedo"]["value"] = 44

#     # Test retrieval by passing string or list
#     ast = Rock(id_, skip_id_check=True, ssocard=ssocard)
#     assert ast.albedo.value == 44


# # ------
# # Test parameter access
# @pytest.mark.parametrize("number, name, id_", TEST_CASES[:-1], ids=str)
# def test_parameter_access(number, name, id_, monkeypatch):
#     """Test retrieval of single datacloud catalogues."""

#     monkeypatch.setattr(rocks.ssodnet, "get_ssocard", get_ssocard_from_test_data)

#     # Ensure that the input from the JSON corresponds to the serialized parameters
#     # in the Rock instances
#     sso = Rock(id_, skip_id_check=True)

#     # Read JSON file
#     data = get_ssocard_from_test_data(id_)

#     # Flatten the json into a single-level dictionary for easy dereferencing
#     flattened_json = pd.json_normalize(data).to_dict(orient="records")[0]

#     # For some chosen end-members in the JSON card, ensure that the value
#     # corresponds to the value in the Rock instance
#     for key, value_json in flattened_json.items():

#         # Phase and colour à la Generic/Johnson are annoying to parse
#         if "/" in key:
#             continue

#         # these get unpacked into lists
#         if "spin" in key:
#             continue

#         # Only check the end-members as the other objects get de-serialized
#         if key.endswith("value"):

#             value_rock = rocks.utils.rgetattr(sso, key)

#             if isinstance(value_rock, float):
#                 assert float(value_rock) == float(value_json)
#             else:
#                 assert value_rock == value_json


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
