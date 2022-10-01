#!/usr/bin/env python
"""Test serialization and deserialization of ssoCard and Rock class."""

import numpy as np
import pytest

import rocks

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
        # Phase is instantiated
        assert isinstance(rock.phase_function.misc_atlas_cyan.H.value, float)

        # Shortcuts works
        assert rock.phase_function.cyan is rock.phase_function.misc_atlas_cyan
        assert rock.phase_function.orange is rock.phase_function.misc_atlas_orange
        assert rock.phase_function.V is rock.phase_function.generic_johnson_V

        # Phase is not NaN
        assert np.isfinite(rock.phase_function.cyan.H.value)

        # Phase evaluates as True
        assert rock.phase_function

    else:
        # Phase is instantiated and NaN
        assert not rock.phase_function.cyan

        # Phase evaluates as False
        assert not rock.phase_function


# # Spin
# SPIN_EXISTS = [1, 221]
# SPIN_MISSING = [92384, 385186]


# @pytest.mark.parametrize(
#     "id_",
#     "exists",
#     SPIN_EXISTS + SPIN_MISSING,
#     [True] * len(SPIN_EXISTS) + [False] * len(SPIN_EXISTS),
#     ids=str,
# )
# def test_spin(id_, exists):
#     """Verify spin parameter access."""

#     rock = rocks.Rock(id_)

#     if exists:
#         # Spin is instantiated
#         assert isinstance(rock.spin.class_.value, str)

#         # Spin is not NaN
#         assert rock.spin.class_.value

#         # Spin evaluates as True
#         assert rock.spin

#     else:
#         # Spin is instantiated and NaN
#         assert not rock.spin.class_.value

#         # Spin evaluates as False
#         assert not rock.spin


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
