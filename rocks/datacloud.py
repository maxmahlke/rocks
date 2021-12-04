#!/usr/bin/env python
"""Implement the Datacloud catalogue pydantic models."""
from typing import List, Optional

import numpy as np
import pandas as pd
import pydantic
import rich
from rich.table import Table

import rocks


# ------
# Definitions
CATALOGUES = {
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
            "err_albedo_down",
            "diameter",
            "err_diameter_up",
            "err_diameter_down",
            "method",
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
            "IRAS_Diameter",
            "IRAS_Class",
            "SemimajorAxis",
            "Eccentricity",
            "Inclination",
        ],
    },
    "binarymp": {
        "attr_name": "binaries",
        "ssodnet_name": "binarymp",
        "print_columns": [""],
    },
    "colors": {
        "attr_name": "colors",
        "ssodnet_name": "colors",
        "print_columns": [""],
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
            "shortbib",
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
            "shortbib",
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
        "print_columns": ["mass", "err_mass", "method", "shortbib"],
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
        "print_columns": [],
    },
    "pairs": {
        "attr_name": "pairs",
        "ssodnet_name": "pairs",
        "print_columns": [],
    },
    "phase_functions": {
        "attr_name": "phase_functions",
        "ssodnet_name": "phase_function",
        "print_columns": [],
    },
    "taxonomies": {
        "attr_name": "taxonomies",
        "ssodnet_name": "taxonomy",
        "print_columns": [
            "class_",
            "complex_",
            "method",
            "waverange",
            "scheme",
            "shortbib",
        ],
    },
    "thermal_properties": {
        "attr_name": "thermal_properties",
        "ssodnet_name": "thermal_properties",
        "print_columns": [],
    },
    "yarkovskies": {
        "attr_name": "yarkovskies",
        "ssodnet_name": "yarkovsky",
        "print_columns": [],
    },
}

# ------
# Pretty-printing
def pretty_print(rock, catalogue, parameter):
    """Print datacloud catalogue using a nice table format.

    Parameters
    ==========
    rock : rocks.Rock
        The Rock instance the catalogue is associated to.
    catalogue : pd.DataFrame
        The datacloud catalogue to print.
    parameter : str
        The name of the user-requested parameter to echo.
    """

    if len(catalogue) == 1 and pd.isna(catalogue.id_[0]):
        print(f"No {parameter} on record for ({rock.number}) {rock.name}.")
        return

    # ------
    # Create table to echo
    if parameter in ["diamalbedo", "diameters", "albedos"]:
        caption = (
            "Blue: preferred diameter, yellow: preferred albedo, green: both preferred"
        )
    else:
        caption = "Green: preferred entry" if hasattr(catalogue, "preferred") else ""

    table = Table(
        header_style="bold blue",
        box=rich.box.SQUARE,
        footer_style="dim",
        title=f"({rock.number}) {rock.name}",
        caption=caption,
    )

    # Sort catalogue by year of reference
    if "year" in catalogue.columns:
        catalogue = catalogue.sort_values("year").reset_index()

    # The columns depend on the catalogue
    columns = CATALOGUES[parameter]["print_columns"]

    for c in columns:
        table.add_column(c)

    # Some catalogues do not have a "preferred" attribute
    if not hasattr(catalogue, "preferred"):
        preferred = [False for _ in range(len(catalogue))]
    else:
        preferred = catalogue.preferred

    # Add rows to table, styling by preferred-state of entry
    for i, pref in enumerate(preferred):

        if parameter in ["diamalbedo", "diameters", "albedos"]:
            if pref:
                if (
                    catalogue.preferred_albedo[i]
                    and not catalogue.preferred_diameter[i]
                ):
                    style = "bold yellow"
                elif (
                    not catalogue.preferred_albedo[i]
                    and catalogue.preferred_diameter[i]
                ):
                    style = "bold blue"
                else:
                    style = "bold green"
            else:
                style = "white"

        else:
            style = "bold green" if pref else "white"

        table.add_row(
            *[str(catalogue[c][i]) for c in columns],
            style=style,
        )

    rich.print(table)


# ------
# Subclass the pd.DataFrame to add rocks-specific functionality
class DataCloudDataFrame(pd.DataFrame):
    @property
    def _constructor(self):
        return DataCloudDataFrame

    @property
    def _constructor_sliced(self):
        return DataCloudSeries

    def plot(self, parameter, **kwargs):
        """Plot the parameter of the catalogue."""
        return rocks.plots.plot(self, parameter, **kwargs)

    def weighted_average(self, parameter):
        """Compute the weighted average of the parameter using the preferred
        values only."""
        return rocks.utils.weighted_average(self, parameter)


class DataCloudSeries(pd.Series):
    @property
    def _constructor(self):
        return DataCloudSeries

    @property
    def _constructor_expanddim(self):
        return DataCloudDataFrame


# ------
# Validators
def ensure_list(value):
    """Ensure that parameters are always a list.

    Further replaces all None values by empty dictionaries.
    """
    if isinstance(value, (dict, int, float, str)):
        value = [value]

    return value


def ensure_int(value):
    return [int(v) if v else None for v in value]


# ------
# SsODNet catalogues as pydantic model
class Catalogue(pydantic.BaseModel):
    """The abstraction of a general datacloud catalogue on SsODNet."""

    id_: List[int] = pydantic.Field([None], alias="id")
    link: List[str] = [""]
    name: List[str] = [""]
    title: List[str] = [""]
    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    iddataset: List[str] = [""]
    datasetname: List[str] = [""]
    idcollection: List[int] = [None]
    resourcename: List[str] = [""]

    _ensure_list: classmethod = pydantic.validator("*", allow_reuse=True, pre=True)(
        ensure_list
    )
    _ensure_int: classmethod = pydantic.validator(
        "id_", "number", allow_reuse=True, pre=True
    )(ensure_int)


# class AstDyS(Catalogue):
#     H: List[float] = [np.nan]
#     ProperSemimajorAxis: List[float] = [np.nan]
#     err_ProperSemimajorAxis: List[float] = [np.nan]
#     ProperEccentricity: List[float] = [np.nan]
#     err_ProperEccentricity: List[float] = [np.nan]
#     ProperSinI: List[float] = [np.nan]
#     err_ProperSinI: List[float] = [np.nan]
#     ProperInclination: List[float] = [np.nan]
#     err_ProperInclination: List[float] = [np.nan]
#     n: List[float] = [np.nan]
#     err_n: List[float] = [np.nan]
#     g: List[float] = [np.nan]
#     err_g: List[float] = [np.nan]
#     s: List[float] = [np.nan]
#     err_s: List[float] = [np.nan]
#     LCE: List[float] = [np.nan]
#     My: List[float] = [np.nan]
#     lam_fit: List[float] = pydantic.Field([np.nan], alias="lam-fit")


class Astorb(Catalogue):
    OrbComputer: List[str] = [""]
    H: List[float] = [np.nan]
    G: List[float] = [np.nan]
    B_V: List[float] = [np.nan]
    IRAS_Diameter: List[float] = [np.nan]
    IRAS_Class: List[str] = [""]
    OrbArc: List[int] = [None]
    NumberObs: List[int] = [None]
    MeanAnomaly: List[float] = [np.nan]
    ArgPerihelion: List[float] = [np.nan]
    LongAscNode: List[float] = [np.nan]
    Inclination: List[float] = [np.nan]
    Eccentricity: List[float] = [np.nan]
    SemimajorAxis: List[float] = [np.nan]
    CEU_value: List[float] = [np.nan]
    CEU_rate: List[float] = [np.nan]
    PEU_value: List[float] = [np.nan]
    GPEU_fromCEU: List[float] = [np.nan]
    GPEU_fromPEU: List[float] = [np.nan]
    Note_1: List[int] = [None]
    Note_2: List[int] = [None]
    Note_3: List[int] = [None]
    Note_4: List[int] = [None]
    Note_5: List[int] = [None]
    Note_6: List[int] = [None]
    YY_calulation: List[int] = [None]
    MM_calulation: List[int] = [None]
    DD_calulation: List[int] = [None]
    YY_osc: List[int] = [None]
    MM_osc: List[int] = [None]
    DD_osc: List[int] = [None]
    CEU_yy: List[int] = [None]
    CEU_mm: List[int] = [None]
    CEU_dd: List[int] = [None]
    PEU_yy: List[int] = [None]
    PEU_mm: List[int] = [None]
    PEU_dd: List[int] = [None]
    GPEU_yy: List[int] = [None]
    GPEU_mm: List[int] = [None]
    GPEU_dd: List[int] = [None]
    GGPEU_yy: List[int] = [None]
    GGPEU_mm: List[int] = [None]
    GGPEU_dd: List[int] = [None]
    JD_osc: List[float] = [np.nan]
    px: List[float] = [np.nan]
    py: List[float] = [np.nan]
    pz: List[float] = [np.nan]
    vx: List[float] = [np.nan]
    vy: List[float] = [np.nan]
    vz: List[float] = [np.nan]
    MeanMotion: List[float] = [np.nan]
    OrbPeriod: List[float] = [np.nan]


class Binarymp(Catalogue):
    pass


class Colors(Catalogue):
    pass


class Diamalbedo(Catalogue):

    doi: List[str] = [""]
    url: List[str] = [""]
    title: List[str] = [""]
    method: List[str] = [""]
    year: List[Optional[int]] = [None]
    source: List[str] = [""]
    shortbib: List[str] = [""]

    albedo: List[float] = [np.nan]
    err_albedo_up: List[float] = [np.nan]
    err_albedo_down: List[float] = [np.nan]
    diameter: List[float] = [np.nan]
    err_diameter_up: List[float] = [np.nan]
    err_diameter_down: List[float] = [np.nan]
    beaming: List[float] = [np.nan]
    err_beaming: List[float] = [np.nan]
    emissivity: List[float] = [np.nan]
    err_emissivity: List[float] = [np.nan]

    preferred_albedo: List[bool] = [False]
    preferred_diameter: List[bool] = [False]
    preferred: List[bool] = [False]

    @pydantic.validator("preferred_albedo", pre=True)
    def select_preferred_albedo(cls, _, values):
        return rocks.definitions.rank_properties("albedo", values)

    @pydantic.validator("preferred_diameter", pre=True)
    def select_preferred_diameter(cls, _, values):
        return rocks.definitions.rank_properties("diameter", values)

    @pydantic.validator("preferred", pre=True)
    def preferred_albedo_or_diameter(cls, _, values):
        return [
            True if pref_alb or pref_diam else False
            for pref_alb, pref_diam in zip(
                values["preferred_albedo"], values["preferred_diameter"]
            )
        ]


class Families(Catalogue):
    membership: List[float] = [np.nan]
    family_name: List[str] = [""]
    family_number: List[float] = [np.nan]
    family_status: List[str] = [""]


class Masses(Catalogue):
    doi: List[str] = [""]
    url: List[str] = [""]
    source: List[str] = [""]
    method: List[str] = [""]
    shortbib: List[str] = [""]

    year: List[Optional[int]] = [None]
    mass: List[float] = [np.nan]
    err_mass: List[float] = [np.nan]

    preferred: List[bool] = [False]

    @pydantic.validator("preferred", pre=True)
    def select_preferred_mass(cls, _, values):
        return rocks.definitions.rank_properties("mass", values)


class Mpcatobs(Catalogue):
    link: List[str] = [""]
    datasetname: List[str] = [""]
    resourcename: List[str] = [""]
    title: List[str] = [""]
    iddataset: List[str] = [""]
    idcollection: List[Optional[int]] = [None]
    jd_obs: List[float] = [np.nan]
    ra_obs: List[float] = [np.nan]
    dec_obs: List[float] = [np.nan]
    mag: List[float] = [np.nan]
    vgs_x: List[float] = [np.nan]
    vgs_y: List[float] = [np.nan]
    vgs_z: List[float] = [np.nan]
    packed_name: List[str] = [""]
    orb_type: List[str] = [""]
    discovery: List[str] = [""]
    note1: List[str] = [""]
    note2: List[str] = [""]
    note3: List[str] = [""]
    note4: List[str] = [""]
    iau_code: List[str] = [""]
    date_obs: List[str] = [""]
    filter_: List[str] = pydantic.Field([""], alias="type")
    type_: List[str] = pydantic.Field([""], alias="type")


class Mpcorb(Catalogue):
    pass


class Pairs(Catalogue):
    sibling_num: List[float] = [np.nan]
    sibling_name: List[str] = [""]
    delta_v: List[float] = [np.nan]
    delta_a: List[float] = [np.nan]
    delta_e: List[float] = [np.nan]
    delta_sini: List[float] = [np.nan]
    delta_i: List[float] = [np.nan]
    membership: List[int] = [None]


class PhaseFunction(Catalogue):
    pass


class Taxonomies(Catalogue):
    doi: List[str] = [""]
    source: List[str] = [""]
    waverange: List[str] = [""]
    method: List[str] = [""]
    scheme: List[str] = [""]
    complex_: List[str] = pydantic.Field([""], alias="complex")
    class_: List[str] = pydantic.Field([""], alias="class")
    shortbib: List[str] = [""]

    year: List[Optional[int]] = [None]

    preferred: List[bool] = [False]

    @pydantic.validator("preferred", pre=True)
    def select_preferred_taxonomy(cls, _, values):
        return rocks.definitions.rank_properties("taxonomy", values)


class ThermalProperties(Catalogue):
    pass


class Yarkovskies(Catalogue):
    pass
