#!/usr/bin/env python
"""Implement the Datacloud catalogue pydantic models."""
from typing import List, Optional
import warnings

import numpy as np
import pandas as pd
import pydantic
import rich

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
    },
    "astdys": {
        "attr_name": "astdys",
        "ssodnet_name": "astdys",
    },
    "astorb": {
        "attr_name": "astorb",
        "ssodnet_name": "astorb",
    },
    "binarymp_tab": {
        "attr_name": "binaries",
        "ssodnet_name": "binarymp_tab",
    },
    "diamalbedo": {
        "attr_name": "diamalbedo",
        "ssodnet_name": "diamalbedo",
    },
    "diameters": {
        "attr_name": "diamalbedo",
        "ssodnet_name": "diamalbedo",
    },
    "families": {
        "attr_name": "families",
        "ssodnet_name": "families",
    },
    "masses": {
        "attr_name": "masses",
        "ssodnet_name": "masses",
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
    },
}


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
    bibcode: List[str] = [""]
    iddataset: List[str] = [""]
    datasetname: List[str] = [""]
    idcollection: List[int] = [None]
    resourcename: List[str] = [""]

    _ensure_int: classmethod = pydantic.validator(
        "id_", "number", allow_reuse=True, pre=True
    )(ensure_int)
    _ensure_list: classmethod = pydantic.validator("name", allow_reuse=True, pre=True)(
        ensure_list
    )


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
    OrbComputer: Optional[str] = ""
    H: Optional[float] = np.nan
    G: Optional[float] = np.nan
    B_V: Optional[float] = np.nan
    IRAS_Diameter: Optional[float] = np.nan
    IRAS_Class: Optional[str] = ""
    OrbArc: Optional[int] = None
    NumberObs: Optional[int] = None
    MeanAnomaly: Optional[float] = np.nan
    ArgPerihelion: Optional[float] = np.nan
    LongAscNode: Optional[float] = np.nan
    Inclination: Optional[float] = np.nan
    Eccentricity: Optional[float] = np.nan
    SemimajorAxis: Optional[float] = np.nan
    CEU_value: Optional[float] = np.nan
    CEU_rate: Optional[float] = np.nan
    PEU_value: Optional[float] = np.nan
    GPEU_fromCEU: Optional[float] = np.nan
    GPEU_fromPEU: Optional[float] = np.nan
    Note_1: Optional[int] = None
    Note_2: Optional[int] = None
    Note_3: Optional[int] = None
    Note_4: Optional[int] = None
    Note_5: Optional[int] = None
    Note_6: Optional[int] = None
    YY_calulation: Optional[int] = None
    MM_calulation: Optional[int] = None
    DD_calulation: Optional[int] = None
    YY_osc: Optional[int] = None
    MM_osc: Optional[int] = None
    DD_osc: Optional[int] = None
    CEU_yy: Optional[int] = None
    CEU_mm: Optional[int] = None
    CEU_dd: Optional[int] = None
    PEU_yy: Optional[int] = None
    PEU_mm: Optional[int] = None
    PEU_dd: Optional[int] = None
    GPEU_yy: Optional[int] = None
    GPEU_mm: Optional[int] = None
    GPEU_dd: Optional[int] = None
    GGPEU_yy: Optional[int] = None
    GGPEU_mm: Optional[int] = None
    GGPEU_dd: Optional[int] = None
    JD_osc: Optional[float] = np.nan
    px: Optional[float] = np.nan
    py: Optional[float] = np.nan
    pz: Optional[float] = np.nan
    vx: Optional[float] = np.nan
    vy: Optional[float] = np.nan
    vz: Optional[float] = np.nan
    MeanMotion: Optional[float] = np.nan
    OrbPeriod: Optional[float] = np.nan


class Diamalbedo(Catalogue):

    doi: List[str] = [""]
    url: List[str] = [""]
    title: List[str] = [""]
    method: List[str] = [""]
    shortbib: List[str] = [""]
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

    def __len__(self):
        return len(self.albedo)

    def __str__(self):

        if len(self) == 1 and not self.albedo[0] and not self.diameter[0]:
            return "No diameters on record."

        # Compute weighted averages of albedo and diameter
        alb_avg, err_alb_avg = rocks.utils.weighted_average(
            np.array(self.albedo)[self.preferred_albedo],
            np.array(self.err_albedo)[self.preferred_albedo],
        )
        alb_diam, err_alb_diam = rocks.utils.weighted_average(
            np.array(self.diameter)[self.preferred_diameter],
            np.array(self.err_diameter)[self.preferred_diameter],
        )

        table = rich.table.Table(
            header_style="bold blue",
            box=rich.box.SQUARE,
            footer_style="dim",
            caption=f"""Blue: preferred diameters, yellow: preferred albedos, green: both preferred

            Albedo: {alb_avg:.2f} +- {err_alb_avg:.3f}
            Diameter: {alb_diam:.2f} +- {err_alb_diam:.2f}km
            """,
        )

        columns = [
            "albedo",
            "err_albedo",
            "diameter",
            "err_diameter",
            "method",
            "shortbib",
        ]

        for c in columns:
            table.add_column(c)

        # Values are entries for each field
        for i, preferred in enumerate(self.preferred_diameter):

            # blue for preferred diameter, yellow for preferred albedo, green for both,
            # else white
            if preferred:
                style = "bold green" if self.preferred_albedo[i] else "bold blue"
            elif self.preferred_albedo[i]:
                style = "bold yellow"
            else:
                style = "white"
            table.add_row(
                *[str(getattr(self, c)[i]) for c in columns],
                style=style,
            )
        rich.print(table)
        return ""


class Masses(Catalogue):
    doi: List[str] = [""]
    url: List[str] = [""]
    source: List[str] = [""]
    shortbib: List[str] = [""]
    method: List[str] = [""]

    year: List[Optional[int]] = [None]
    mass: List[float] = [np.nan]
    err_mass: List[float] = [np.nan]

    preferred: List[bool] = [False]

    @pydantic.validator("preferred", pre=True)
    def select_preferred_mass(cls, v, values):
        return rocks.definitions.rank_properties("mass", values)

    def __len__(self):
        return len(self.mass)

    def __str__(self):

        if len(self) == 1 and not self.mass[0]:
            return "No masses on record."

        table = rich.table.Table(
            header_style="bold blue",
            box=rich.box.SQUARE,
            footer_style="dim",
        )

        columns = ["mass", "err_mass", "method", "shortbib"]

        for c in columns:
            table.add_column(c)

        # Values are entries for each field
        for i, preferred in enumerate(self.preferred):
            table.add_row(
                *[str(getattr(self, c)[i]) for c in columns],
                style="bold green" if preferred else "white",
            )
        rich.print(table)
        return ""


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

    def __len__(self):
        return len(self.class_)

    def __str__(self):

        if len(self) == 1 and not self.class_[0]:
            return "No taxonomies on record."

        table = rich.table.Table(
            header_style="bold blue",
            box=rich.box.SQUARE,
            footer_style="dim",
        )

        columns = ["class_", "complex_", "method", "waverange", "scheme", "shortbib"]

        for c in columns:
            table.add_column(c)

        # Values are entries for each field
        for i, preferred in enumerate(self.preferred):
            table.add_row(
                *[str(getattr(self, c)[i]) for c in columns],
                style="bold green" if preferred else "white",
            )
        rich.print(table)
        return ""
