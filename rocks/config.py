"""Definitions concerning the ssoCard and datacloud representation in rocks."""

from pathlib import Path


PATH_CACHE = Path.home() / ".cache/rocks"

PATH_AUTHORS = PATH_CACHE / "ssodnet_biblio.json"
PATH_INDEX = PATH_CACHE / "index"
PATH_MAPPINGS = PATH_CACHE / "metadata_aster.json"


# ------
# ssoCard
ALIASES = {
    "dynamical": {
        "parameters.dynamical.orbital_elements": "orbital_elements",
        "parameters.dynamical.family": "family",
        "parameters.dynamical.pair": "pair",
        "parameters.dynamical.proper_elements": "proper_elements",
        "parameters.dynamical.tisserand_parameter": "tisserand_parameter",
        "parameters.dynamical.yarkovsky": "yarkovsky",
    },
    "physical": {
        "D": "diameter",
        "H": "absolute_magnitude",
        "parameters.physical.absolute_magnitude": "absolute_magnitude",
        "parameters.physical.albedo": "albedo",
        "parameters.physical.colors": "color",
        "parameters.physical.diameter": "diameter",
        "parameters.physical.density": "density",
        "parameters.physical.mass": "mass",
        "parameters.physical.phase_function": "phase_function",
        "parameters.physical.spin": "spin",
        "parameters.physical.taxonomy": "taxonomy",
        "parameters.physical.thermal_inertia": "thermal_inertia",
    },
    "eq_state_vector": {
        "parameters.eq_state_vector.ref_epoch": "ref_epoch",
        "parameters.eq_state_vector.position": "position",
        "parameters.eq_state_vector.velocity": "velocity",
    },
    "orbital_elements": {
        "a": "semi_major_axis",
        "e": "eccentricity",
        "i": "inclination",
        "P": "orbital_period",
    },
    "proper_elements": {
        "ap": "proper_semi_major_axis",
        "ep": "proper_eccentricity",
        "ip": "proper_inclination",
        "sinip": "proper_sine_inclination",
    },
    "diamalbedo": ["albedos", "diameters"],
    "phase_function": {
        "V": "generic_johnson_V",
        "cyan": "misc_atlas_cyan",
        "orange": "misc_atlas_orange",
    },
}

# ------
# datacloud
DATACLOUD = {
    # the catalogues as defined by rocks
    # rocks name :
    #     attr_name : Rock.xyz
    #     ssodnet_name : Name of catalogue in SsODNet
    "albedos": {
        "attr_name": "diamalbedo",
        "ssodnet_name": "diamalbedo",
        "print_columns": [
            "albedo",
            "err_albedo_up",
            "diameter",
            "err_albedo_down",
            "err_diameter_up",
            "err_diameter_down",
            "method",
            # "bibcode",
            "shortbib",
        ],
    },
    "astdys": {
        "attr_name": "astdys",
        "ssodnet_name": "astdys",
        "print_columns": [
            "H",
            "ProperSemimajorAxis",
            "ProperEccentricity",
            "ProperInclination",
            "ProperSinI",
            "n",
            "s",
            "LCE",
        ],
    },
    "astorb": {
        "attr_name": "astorb",
        "ssodnet_name": "astorb",
        "print_columns": [
            "H",
            "G",
            "B_V",
            "IRAS_diameter",
            "IRAS_class",
            "semi_major_axis",
            "eccentricity",
            "inclination",
        ],
    },
    "binarymp": {
        "attr_name": "binaries",
        "ssodnet_name": "binarymp",
        "print_columns": [
            "system_type",
            "system_name",
            "period",
            "a",
            "alpha",
            "shortbib",
        ],
    },
    "colors": {
        "attr_name": "colors",
        "ssodnet_name": "colors",
        "print_columns": ["color", "value", "uncertainty", "phot_sys"],
    },
    "diamalbedo": {
        "attr_name": "diamalbedo",
        "ssodnet_name": "diamalbedo",
        "print_columns": [
            "albedo",
            "err_albedo_up",
            "err_albedo_down",
            "diameter",
            "err_diameter_up",
            "err_diameter_down",
            "method",
            "bibcode",
        ],
    },
    "diameters": {
        "attr_name": "diamalbedo",
        "ssodnet_name": "diamalbedo",
        "print_columns": [
            "albedo",
            "err_albedo_up",
            "err_albedo_down",
            "diameter",
            "err_diameter_up",
            "err_diameter_down",
            "method",
            "bibcode",
        ],
    },
    "families": {
        "attr_name": "families",
        "ssodnet_name": "families",
        "print_columns": [
            "family_number",
            "family_name",
            "family_status",
            "membership",
        ],
    },
    "masses": {
        "attr_name": "masses",
        "ssodnet_name": "masses",
        "print_columns": ["mass", "err_mass_up", "err_mass_down", "method", "shortbib"],
    },
    "mpcatobs": {
        "attr_name": "mpcatobs",
        "ssodnet_name": "mpcatobs",
        "print_columns": [
            "packed_name",
            "discovery",
            "date_obs",
            "ra_obs",
            "dec_obs",
            "mag",
            "filter_",
            "iau_code",
        ],
    },
    "mpcorb": {
        "attr_name": "mpcorb",
        "ssodnet_name": "mpcorb",
        "print_columns": [
            "H",
            "G",
            "semi_major_axis",
            "eccentricity",
            "inclination",
            "orbital_arc",
        ],
    },
    "pairs": {
        "attr_name": "pairs",
        "ssodnet_name": "pairs",
        "print_columns": ["sibling_number", "sibling_name", "delta_v", "membership"],
    },
    "phase_functions": {
        "attr_name": "phase_functions",
        "ssodnet_name": "phase_function",
        "print_columns": [
            "name_filter",
            "H",
            "G1",
            "G2",
            "phase_min",
            "phase_max",
            "shortbib",
        ],
    },
    "spins": {
        "attr_name": "spins",
        "ssodnet_name": "spin",
        "print_columns": ["period", "long_", "lat", "RA0", "DEC0", "Wp", "shortbib"],
    },
    "taxonomies": {
        "attr_name": "taxonomies",
        "ssodnet_name": "taxonomy",
        "print_columns": [
            "class_",
            "complex",
            "method",
            "waverange",
            "scheme",
            "shortbib",
        ],
    },
    "thermal_inertias": {
        "attr_name": "thermal_inertias",
        "ssodnet_name": "thermal_inertia",
        "print_columns": [
            "TI",
            "err_TI_up",
            "err_TI_down",
            "dsun",
            "method",
            "shortbib",
        ],
    },
    "yarkovskys": {
        "attr_name": "yarkovskys",
        "ssodnet_name": "yarkovsky",
        "print_columns": [
            "A2",
            "err_A2",
            "dadt",
            "err_dadt",
            "S",
            "snr",
            "method",
            "shortbib",
        ],
    },
}
