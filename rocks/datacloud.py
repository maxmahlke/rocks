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
    "aams": {
        "attr_name": "aams",
        "ssodnet_name": "aams",
    },
    "albedos": {
        "attr_name": "diamalbedo",
        "ssodnet_name": "diamalbedo",
        "print_columns": [
            "albedo",
            "err_albedo",
            "diameter",
            "err_diameter",
            "method",
            "shortbib",
        ],
    },
    "astdys": {
        "attr_name": "astdys",
        "ssodnet_name": "astdys",
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
    "binarymp_tab": {
        "attr_name": "binaries",
        "ssodnet_name": "binarymp_tab",
    },
    "diamalbedo": {
        "attr_name": "diamalbedo",
        "ssodnet_name": "diamalbedo",
        "print_columns": [
            "albedo",
            "err_albedo",
            "diameter",
            "err_diameter",
            "method",
            "shortbib",
        ],
    },
    "diameters": {
        "attr_name": "diamalbedo",
        "ssodnet_name": "diamalbedo",
        "print_columns": [
            "albedo",
            "err_albedo",
            "diameter",
            "err_diameter",
            "method",
            "shortbib",
        ],
    },
    "families": {
        "attr_name": "families",
        "ssodnet_name": "families",
    },
    "masses": {
        "attr_name": "masses",
        "ssodnet_name": "masses",
        "print_columns": ["mass", "err_mass", "method", "shortbib"],
    },
    "mpcatobs": {
        "attr_name": "mpcatobs",
        "ssodnet_name": "mpcatons",
    },
    "pairs": {
        "attr_name": "pairs",
        "ssodnet_name": "pairs",
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

    if len(catalogue) == 1 and np.isnan(catalogue.id_[0]):
        print(f"No {parameter} on record for ({rock.number}) {rock.name}.")
        return

    # ------
    # Create table to echo
    if parameter in ["diamalbedo", "diameters", "albedos"]:
        caption = (
            "Blue: preferred diameter, yellow: preferred albedo, green: both preferred"
        )
    else:
        caption = "Green: preferred entry"

    table = Table(
        header_style="bold blue",
        box=rich.box.SQUARE,
        footer_style="dim",
        title=f"({rock.number}) {rock.name}",
        caption=caption,
    )

    # The columns depend on the catalogue
    columns = CATALOGUES[parameter]["print_columns"]

    for c in columns:
        table.add_column(c)

    # Some catalogues do not have a "preferred" attribute
    if not hasattr(catalogue, "preferred"):
        preferred = [False for i in range(len(catalogue))]
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
            *[str(getattr(catalogue, c)[i]) for c in columns],
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
    return [int(v) for v in value]


# ------
# SsODNet catalogues as pydantic model
class Catalogue(pydantic.BaseModel):
    """The abstraction of a general datacloud catalogue on SsODNet."""

    id_: List[int] = pydantic.Field([np.nan], alias="id")
    link: List[str] = [""]
    name: List[str] = [""]
    title: List[str] = [""]
    number: List[int] = pydantic.Field([np.nan], alias="num")
    shortbib: List[str] = [""]
    iddataset: List[str] = [""]
    datasetname: List[str] = [""]
    idcollection: List[int] = [None]
    resourcename: List[str] = [""]

    _ensure_list: classmethod = pydantic.validator("*", allow_reuse=True, pre=True)(
        ensure_list
    )
    # _ensure_int: classmethod = pydantic.validator(
    #     "id_", "number", allow_reuse=True, pre=True
    # )(ensure_int)


class AAMS(Catalogue):
    HG_H: Optional[float] = np.nan
    HG_G: Optional[float] = np.nan
    HG_r_err_H: Optional[float] = np.nan
    HG_l_err_H: Optional[float] = np.nan
    HG_r_err_G: Optional[float] = np.nan
    HG_l_err_G: Optional[float] = np.nan
    HG_rms: Optional[float] = np.nan
    HG_convergence: Optional[float] = np.nan
    HG1G2_H: Optional[float] = np.nan
    HG1G2_G1: Optional[float] = np.nan
    HG1G2_G2: Optional[float] = np.nan
    HG1G2_r_err_H: Optional[float] = np.nan
    HG1G2_l_err_H: Optional[float] = np.nan
    HG1G2_r_err_G1: Optional[float] = np.nan
    HG1G2_l_err_G1: Optional[float] = np.nan
    HG1G2_r_err_G2: Optional[float] = np.nan
    HG1G2_l_err_G2: Optional[float] = np.nan
    HG1G2_rms: Optional[float] = np.nan
    HG1G2_convergence: Optional[float] = np.nan
    HG12_H: Optional[float] = np.nan
    HG12_G12: Optional[float] = np.nan
    HG12_r_err_H: Optional[float] = np.nan
    HG12_l_err_H: Optional[float] = np.nan
    HG12_r_err_G12: Optional[float] = np.nan
    HG12_l_err_G12: Optional[float] = np.nan
    HG12_rms: Optional[float] = np.nan
    HG12_convergence: Optional[float] = np.nan
    HG_err_H: Optional[float] = np.nan
    HG_err_G: Optional[float] = np.nan
    HG1G2_err_H: Optional[float] = np.nan
    HG1G2_err_G1: Optional[float] = np.nan
    HG1G2_err_G2: Optional[float] = np.nan
    HG12_err_H: Optional[float] = np.nan
    HG12_err_G12: Optional[float] = np.nan


class AstDyS(Catalogue):
    H: Optional[float] = np.nan
    ProperSemimajorAxis: Optional[float] = np.nan
    err_ProperSemimajorAxis: Optional[float] = np.nan
    ProperEccentricity: Optional[float] = np.nan
    err_ProperEccentricity: Optional[float] = np.nan
    ProperSinI: Optional[float] = np.nan
    err_ProperSinI: Optional[float] = np.nan
    ProperInclination: Optional[float] = np.nan
    err_ProperInclination: Optional[float] = np.nan
    n: Optional[float] = np.nan
    err_n: Optional[float] = np.nan
    g: Optional[float] = np.nan
    err_g: Optional[float] = np.nan
    s: Optional[float] = np.nan
    err_s: Optional[float] = np.nan
    LCE: Optional[float] = np.nan
    My: Optional[float] = np.nan
    lam_fit: Optional[float] = pydantic.Field(np.nan, alias="lam-fit")


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


class Diamalbedo(Catalogue):

    doi: List[str] = [""]
    url: List[str] = [""]
    title: List[str] = [""]
    method: List[str] = [""]
    year: List[Optional[int]] = [None]
    source: List[str] = [""]

    albedo: List[float] = [np.nan]
    err_albedo: List[float] = [np.nan]
    diameter: List[float] = [np.nan]
    err_diameter: List[float] = [np.nan]
    beaming: List[float] = [np.nan]
    err_beaming: List[float] = [np.nan]
    emissivity: List[float] = [np.nan]
    err_emissivity: List[float] = [np.nan]

    preferred_albedo: List[bool] = [False]
    preferred_diameter: List[bool] = [False]
    preferred: List[bool] = [False]

    @pydantic.validator("preferred_albedo", pre=True)
    def select_preferred_albedo(cls, v, values):
        return rocks.definitions.rank_properties("albedo", values)

    @pydantic.validator("preferred_diameter", pre=True)
    def select_preferred_diameter(cls, v, values):
        return rocks.definitions.rank_properties("diameter", values)

    @pydantic.validator("preferred", pre=True)
    def preferred_albedo_or_diameter(cls, v, values):
        return [
            True if pref_alb or pref_diam else False
            for pref_alb, pref_diam in zip(
                values["preferred_albedo"], values["preferred_diameter"]
            )
        ]


class Masses(Catalogue):
    doi: List[str] = [""]
    url: List[str] = [""]
    source: List[str] = [""]
    method: List[str] = [""]

    year: List[Optional[int]] = [None]
    mass: List[float] = [np.nan]
    err_mass: List[float] = [np.nan]

    preferred: List[bool] = [False]

    @pydantic.validator("preferred", pre=True)
    def select_preferred_mass(cls, v, values):
        return rocks.definitions.rank_properties("mass", values)


class Mpcatobs(Catalogue):
    link: List[str] = [""]
    datasetname: List[str] = [""]
    resourcename: List[str] = [""]
    doi: List[str] = [""]
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


class Pairs(Catalogue):
    sibling_num: Optional[float] = np.nan
    sibling_name: Optional[str] = ""
    delta_v: Optional[float] = np.nan
    delta_a: Optional[float] = np.nan
    delta_e: Optional[float] = np.nan
    delta_sini: Optional[float] = np.nan
    delta_i: Optional[float] = np.nan
    membership: Optional[int] = None


class Taxonomies(Catalogue):
    doi: List[str] = [""]
    source: List[str] = [""]
    waverange: List[str] = [""]
    method: List[str] = [""]
    scheme: List[str] = [""]
    complex_: List[str] = pydantic.Field([""], alias="complex")
    class_: List[str] = pydantic.Field([""], alias="class")

    year: List[Optional[int]] = [None]

    preferred: List[bool] = [False]

    @pydantic.validator("preferred", pre=True)
    def select_preferred_taxonomy(cls, v, values):
        return rocks.definitions.rank_properties("taxonomy", values)
