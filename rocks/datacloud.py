#!/usr/bin/env python
"""Implement the Datacloud catalogue pydantic models."""
from typing import List, Optional
import warnings

import numpy as np
import pydantic
import rich

import rocks

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
    number: List[int] = pydantic.Field([np.nan], alias="num")
    name: List[str] = [""]

    _ensure_int: classmethod = pydantic.validator(
        "id_", "number", allow_reuse=True, pre=True
    )(ensure_int)
    _ensure_list: classmethod = pydantic.validator("name", allow_reuse=True, pre=True)(
        ensure_list
    )

    def weighted_average(self, property_=None):
        """Compute the weighted average of the preferred entries of a catalogued property.

        Parameters
        ==========
        property_ : str
            The name of the property to average. Default is None, where the name will be inferred
            based on the parent catalogue. For diamalbedo, the property has to be specified.

        Returns
        =======
        float
            The weighted average of the property.
        float
            The error on the weighted average of the property.
        """

        if property_ is None:
            property_ = self.property_to_average
            preferred = self.preferred
        else:
            preferred = getattr(self, f"preferred_{property_}")

        values = getattr(self, property_)
        errors = getattr(self, f"err_{property_}")

        preferred_values = np.array(values)[preferred]
        preferred_errors = np.array(errors)[preferred]

        if all([np.isnan(value) for value in preferred_values]) or all([np.isnan(error) for error in preferred_errors]):
            warnings.warn(f"{self.name[0]}: The values or errors of property '{property_}' are all NaN. Average failed.")
            return np.nan, np.nan

        average, error = rocks.utils.weighted_average(preferred_values, preferred_errors)
        return average, error

class Pairs(Catalogue):
    sibling_num: Optional[float] = np.nan
    sibling_name: Optional[str] = ""
    delta_v: Optional[float] = np.nan
    delta_a: Optional[float] = np.nan
    delta_e: Optional[float] = np.nan
    delta_sini: Optional[float] = np.nan
    delta_i: Optional[float] = np.nan
    membership: Optional[int] = None
    iddataset: Optional[str] = ""
    idcollection: Optional[int] = None
    resourcename: Optional[str] = ""
    datasetname: Optional[str] = ""
    bibcode: Optional[str] = ""
    title: Optional[str] = ""
    link: Optional[str] = ""


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
    iddataset: Optional[str] = ""
    idcollection: Optional[int] = None
    resourcename: Optional[str] = ""
    datasetname: Optional[str] = ""
    bibcode: Optional[str] = ""
    title: Optional[str] = ""
    link: Optional[str] = ""


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
    iddataset: Optional[str] = ""
    idcollection: Optional[int] = None
    resourcename: Optional[str] = ""
    datasetname: Optional[str] = ""
    bibcode: Optional[str] = ""
    title: Optional[str] = ""
    link: Optional[str] = ""


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
    iddataset: Optional[str] = ""
    idcollection: Optional[int] = None
    resourcename: Optional[str] = ""
    datasetname: Optional[str] = ""
    bibcode: Optional[str] = ""
    title: Optional[str] = ""
    link: Optional[str] = ""


class Taxonomies(Catalogue):
    link: List[str] = [""]
    datasetname: List[str] = [""]
    resourcename: List[str] = [""]
    doi: List[str] = [""]
    bibcode: List[str] = [""]
    url: List[str] = [""]
    title: List[str] = [""]
    source: List[str] = [""]
    shortbib: List[str] = [""]
    waverange: List[str] = [""]
    method: List[str] = [""]
    scheme: List[str] = [""]
    complex_: List[str] = pydantic.Field([""], alias="complex")
    class_: List[str] = pydantic.Field([""], alias="class")

    idcollection: List[Optional[int]] = [None]
    iddataset: List[Optional[int]] = [None]
    year: List[Optional[int]] = [None]

    preferred: List[bool] = [False]

    @pydantic.validator("preferred", pre=True)
    def select_preferred_taxonomy(cls, v, values):
        return rank_properties("taxonomy", values)

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


class Masses(Catalogue):
    link: List[str] = [""]
    datasetname: List[str] = [""]
    resourcename: List[str] = [""]
    doi: List[str] = [""]
    bibcode: List[str] = [""]
    url: List[str] = [""]
    title: List[str] = [""]
    source: List[str] = [""]
    shortbib: List[str] = [""]
    method: List[str] = [""]

    idcollection: List[Optional[int]] = [None]
    iddataset: List[Optional[int]] = [None]
    year: List[Optional[int]] = [None]
    mass: List[float] = [np.nan]
    err_mass: List[float] = [np.nan]

    preferred: List[bool] = [False]

    @pydantic.validator("preferred", pre=True)
    def select_preferred_mass(cls, v, values):
        return rank_properties("mass", values)

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
    bibcode: List[str] = [""]
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


class Diamalbedo(Catalogue):

    link: List[str] = [""]
    datasetname: List[str] = [""]
    resourcename: List[str] = [""]
    doi: List[str] = [""]
    bibcode: List[str] = [""]
    url: List[str] = [""]
    title: List[str] = [""]
    iddataset: List[Optional[int]] = [None]
    method: List[str] = [""]
    shortbib: List[str] = [""]
    year: List[Optional[int]] = [None]
    source: List[str] = [""]

    idcollection: List[Optional[int]] = [None]
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

    @pydantic.validator("preferred_albedo", pre=True)
    def select_preferred_albedo(cls, v, values):
        return rank_properties("albedo", values)

    @pydantic.validator("preferred_diameter", pre=True)
    def select_preferred_diameter(cls, v, values):
        return rank_properties("diameter", values)

    def __len__(self):
        return len(self.albedo)

    def __str__(self):

        if len(self) == 1 and not self.albedo[0] and not self.diameter[0]:
            return "No diameters on record."

        # Compute weighted averages of albedo and diameter
        alb_avg, err_alb_avg = rocks.utils.weighted_average(np.array(self.albedo)[self.preferred_albedo],
                                                            np.array(self.err_albedo)[self.preferred_albedo])
        alb_diam, err_alb_diam = rocks.utils.weighted_average(np.array(self.diameter)[self.preferred_diameter],
                                                            np.array(self.err_diameter)[self.preferred_diameter])

        table = rich.table.Table(
            header_style="bold blue",
            box=rich.box.SQUARE,
            footer_style="dim",
            caption=f"""Blue: preferred diameters, yellow: preferred albedos, green: both preferred

            Albedo: {alb_avg:.2f} +- {err_alb_avg:.3f}
            Diameter: {alb_diam:.2f} +- {err_alb_diam:.2f}km
            """
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
        # "prop_name": {"diameters": "diameter", "albedos": "albedo"},
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
        # "prop_name": {"diameters": "diameter", "albedos": "albedo"},
        "ssodnet_name": "diamalbedo",
    },
    "diameters": {
        "attr_name": "diamalbedo",
        # "prop_name": {"diameters": "diameter", "albedos": "albedo"},
        "ssodnet_name": "diamalbedo",
    },
    "families": {
        "attr_name": "families",
        "ssodnet_name": "families",
    },
    "masses": {
        "attr_name": "masses",
        # "prop_name": {"masses": "mass"},
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


def rank_properties(prop_name, obs):
    """Select ranking method based on property name.

    Parameters
    ==========
    prop_name : str
        The property to rank.
    obs : dict
        The observations including metadata


    Returns
    =======
    list of bool
        Entry "preferred" in propertyCollection, True if preferred, else False
    """
    if prop_name in ["taxonomy", "taxonomies"]:
        return select_taxonomy(obs)
    elif prop_name in ["mass", "masses"]:
        return select_numeric_property(obs, "mass")
    elif prop_name in ["albedo", "albedos"]:
        return select_numeric_property(obs, "albedo")
    elif prop_name in ["diameter", "diameters"]:
        return select_numeric_property(obs, "diameter")
    else:
        return [True for i in obs]


def select_taxonomy(taxonomies):
    """Select a single taxonomic classification from multiple choices.

    Evaluates the wavelength ranges, methods, schemes, and recency of
    classification.

    Parameters
    ----------
    taxonomies: dict
        Taxonomic classifications retrieved from SsODNet:datacloud.

    Returns
    -------
    list of bool
        True if preferred, else False
    """
    POINTS = {
        "scheme": {"bus-demeo": 3, "bus": 2, "smass": 2, "tholen": 1, "sdss": 1},
        "waverange": {"vis": 1, "nir": 3, "visnir": 6, "mix": 4},
        "method": {"spec": 7, "phot": 3, "mix": 4},
    }

    taxonomies = [dict(zip(taxonomies, t)) for t in zip(*taxonomies.values())]

    # Compute points of each classification
    points = []

    for row in taxonomies:
        points.append(
            sum(
                [
                    POINTS[crit][row[crit].lower()]
                    for crit in ["scheme", "waverange", "method"]
                ]
            )
        )

    # Convert points to boolean
    preferred = [True if p == max(points) else False for p in points]
    return preferred


def select_numeric_property(obs, prop_name):
    """Select preferred observations ranking methods.

    Parameters
    ==========
    obs : dict
        Property measurements and metadata retrieved from SsODNet:datacloud.
    prop_name : str
        Name of the asteroid property.

    Returns
    =======
    list of bool
        True if selected, else False.

    Notes
    =====
    The method ranking depends on the observable.
    """
    RANKING = PROPERTIES[prop_name]["ranking"]
    methods = set(obs["method"])

    for method in RANKING:

        if set(method) & methods:  # method used at least once

            # Ensure that rows do not contain all 0 values, as can be the case
            # for albedo in diamalbedo
            if all(
                [
                    obs[prop_name][i] == 0
                    for i, m in enumerate(obs["method"])
                    if m in method
                ]
            ):
                continue

            # All entries using this method are preferred
            preferred = [True if m in method else False for m in obs["method"]]
            return preferred


    # No property entry is preferred (likely all 0), return list of False
    return [False for o in obs['number']]


# In alphabetic order
PROPERTIES = {
    # TEMPLATE
    # property_name: Rock instance attribute name
    #   attribute: attribute key in datacloud
    #   collection: Rock instance attribute name for collection of parameters
    #               Use plural form
    #   extra_columns: names of additional columns to output on CLI
    #   ssodnet_path: json path to asteroid property
    #                 (to be replaced by ssoCard
    #   type: asteroid property type, float or str
    "albedo": {
        "ranking": [
            ["SPACE"],
            ["ADAM", "KOALA", "SAGE", "Radar"],
            ["LC+TPM", "TPM", "LC+AO", "LC+Occ", "TE-IM", "TE-Occ"],
            ["AO", "Occ", "IM"],
            ["NEATM"],
            ["STM"],
        ],
    },
    "diameter": {
        "ranking": [
            ["SPACE"],
            ["ADAM", "KOALA", "SAGE", "Radar"],
            ["LC+TPM", "TPM", "LC+AO", "LC+Occ", "TE-IM", "TE-Occ"],
            ["AO", "Occ", "IM"],
            ["NEATM"],
            ["STM"],
        ],
    },
    "mass": {
        "ranking": [
            ["SPACE"],
            ["Bin-Genoid"],
            ["Bin-IM", "Bin-Radar", "Bin-PheMu"],
            ["EPHEM", "DEFLECT"],
        ],
    },
}


# Classes to complexes mapping
CLASS_TO_COMPLEX = {
    "A": "A",
    "Ad": "U",
    "AQ": "U",
    "AS": "U",
    "AU": "U",
    "AV": "U",
    "B": "B",
    "BC": "C",
    "BCF": "C",
    "BCU": "U",
    "BFC": "C",
    "BFU": "U",
    "BFX": "U",
    "Bk": "U",
    "BU": "B",
    "C": "C",
    "Caa": "C",
    "Cb": "C",
    "CB": "C",
    "CBU": "C",
    "CD": "U",
    "CDX": "U",
    "CF": "C",
    "CFB": "C",
    "CFU": "U",
    "CFXU": "U",
    "Cg": "C",
    "CG": "C",
    "CGSU": "U",
    "CGTP": "U",
    "CGU": "U",
    "Cgx": "C",
    "CL": "U",
    "CO": "U",
    "CP": "U",
    "CPF": "U",
    "CPU": "U",
    "CQ": "U",
    "CS": "U",
    "CSGU": "U",
    "CSU": "U",
    "CTGU": "U",
    "CU": "U",
    "CX": "U",
    "CXF": "U",
    "Cgh": "Ch",
    "Ch": "Ch",
    "D": "D",
    "DCX": "U",
    "DL": "D",
    "DP": "D",
    "DU": "D",
    "Ds": "D",
    "DS": "D",
    "DSU": "D",
    "DT": "D",
    "DTU": "D",
    "DU": "D",
    "DX": "D",
    "DXCU": "D",
    "E": "E",
    "EM": "X",
    "EU": "U",
    "F": "C",
    "FBCU": "U",
    "FC": "C",
    "FCB": "C",
    "FCU": "U",
    "FCX": "U",
    "FP": "U",
    "FU": "U",
    "FX": "U",
    "FXU": "U",
    "G": "C",
    "GC": "C",
    "GS": "U",
    "G": "U",
    "J": "V",
    "K": "K",
    "Kl": "U",
    "L": "L",
    "LA": "U",
    "Ld": "L",
    "LQ": "U",
    "LS": "U",
    "M": "M",
    "MU": "U",
    "O": "O",
    "OV": "U",
    "P": "P",
    "PC": "U",
    "PCD": "U",
    "PD": "U",
    "PDC": "U",
    "PF": "U",
    "PU": "U",
    "Q": "Q",
    "QO": "Q",
    "QRS": "U",
    "QSV": "U",
    "QV": "U",
    "Qw": "Q",
    "R": "R",
    "S": "S",
    "SA": "S",
    "Sa": "S",
    "SC": "U",
    "SCTU": "U",
    "SD": "U",
    "SDU": "U",
    "SG": "U",
    "Sk": "S",
    "Sl": "S",
    "SMU": "U",
    "SO": "S",
    "Sq": "S",
    "SQ": "S",
    "Sqw": "S",
    "Sr": "S",
    "SR": "S",
    "Srw": "S",
    "ST": "U",
    "STD": "U",
    "STGD": "U",
    "STU": "U",
    "SU": "U",
    "SV": "S",
    "Sv": "S",
    "Svw": "S",
    "Sw": "S",
    "SX": "U",
    "T": "T",
    "TCG": "U",
    "TD": "U",
    "TDG": "U",
    "TDS": "U",
    "TS": "U",
    "TSD": "U",
    "TX": "U",
    "V": "V",
    "Vw": "V",
    "X": "X",
    "XB": "U",
    "Xc": "X",
    "XC": "U",
    "XCU": "U",
    "XD": "U",
    "XDC": "U",
    "Xe": "X",
    "XF": "U",
    "XFC": "U",
    "XFCU": "U",
    "XFU": "U",
    "Xk": "X",
    "XL": "U",
    "Xn": "X",
    "XS": "U",
    "XSC": "U",
    "XSCU": "U",
    "XT": "U",
    "Xt": "X",
    "XU": "U",
    "Z": "U",
    np.nan: np.nan,
    None: np.nan,
    float("nan"): np.nan,
}
