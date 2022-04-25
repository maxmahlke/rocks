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
            "diameter",
            "err_albedo_down",
            "err_diameter_up",
            "err_diameter_down",
            "method",
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
        "print_columns": ["color", "value", "uncertainty", "phot_sys", "shortbib"],
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
        "print_columns": [],
    },
    "pairs": {
        "attr_name": "pairs",
        "ssodnet_name": "pairs",
        "print_columns": ["sibling_number", "sibling_name", "delta_v", "membership"],
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
            "complex",
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
    ----------
    rock : rocks.Rock
        The Rock instance the catalogue is associated to.
    catalogue : pd.DataFrame
        The datacloud catalogue to print.
    parameter : str
        The name of the user-requested parameter to echo.
    """
    if len(catalogue) == 1 and pd.isna(catalogue.number[0]):
        print(f"No {parameter} on record for ({rock.number}) {rock.name}.")
        return

    # ------
    # Create table to echo
    if parameter in ["diamalbedo", "diameters", "albedos"]:
        caption = (
            "Blue: preferred diameter, yellow: preferred albedo, green: both preferred"
        )
    else:
        caption = "Green: preferred entry" if hasattr(catalogue, "selection") else ""

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
    if not hasattr(catalogue, "selection"):
        preferred = [False for _ in range(len(catalogue))]
    else:
        preferred = [bool(s) for s in catalogue.selection]

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
        from . import plots

        return plots.plot(self, parameter, **kwargs)

    def weighted_average(self, parameter):
        """Compute the weighted average of the parameter using the preferred values only."""
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
    if isinstance(value, str):
        return [int(value)]
    return [int(v) if v else None for v in value]


# ------
# SsODNet catalogues as pydantic model
# https://ssp.imcce.fr/webservices/ssodnet/api/datacloud/templates/ssodnet_datacloud.sql

# Metacatalogues
class Collection(pydantic.BaseModel):
    """Table de definition des references des jeux de donnees de la base SsODNet.datacloud"""

    idcollection: List[int] = [None]
    resourcename: List[str] = [""]
    datasetname: List[str] = [""]
    title: List[str] = [""]
    link: List[str] = [""]


class Methods(pydantic.BaseModel):
    """Table of definition of the methods used to determine the data"""

    idmethod: List[int] = [None]
    method: List[str] = [""]
    fullname: List[str] = [""]
    description: List[str] = [""]
    shortbib: List[str] = [""]
    year: List[int] = [None]
    source: List[str] = [""]
    title: List[str] = [""]
    bibcode: List[str] = [""]
    doi: List[str] = [""]


class Dataset_ref(pydantic.BaseModel):
    """Dataset references"""

    iddataset: List[int] = [None]
    shortbib: List[str] = [""]
    year: List[int] = [None]
    source: List[str] = [""]
    title: List[str] = [""]
    url: List[str] = [""]
    bibcode: List[str] = [""]
    doi: List[str] = [""]
    idcollection: List[int] = [None]
    bibtex: List[str] = [""]


class Dataset_list(pydantic.BaseModel):
    """Dataset list"""

    idsso: List[int] = [None]
    name: List[str] = [""]
    datasetlist: List[str] = [""]


# Parameter Catalogues
class Astorb(pydantic.BaseModel):
    """ASTORB database"""

    id_: List[int] = pydantic.Field([None], alias="id")
    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    name: List[str] = [""]
    OrbComputer: List[str] = [""]
    H: List[float] = [np.nan]
    G: List[float] = [np.nan]
    B_V: List[float] = [np.nan]
    IRAS_Diameter: List[float] = [np.nan]
    IRAS_Class: List[str] = [""]
    Note_1: List[int] = [None]
    Note_2: List[int] = [None]
    Note_3: List[int] = [None]
    Note_4: List[int] = [None]
    Note_5: List[int] = [None]
    Note_6: List[int] = [None]
    OrbArc: List[int] = [None]
    NumberObs: List[int] = [None]
    YY_osc: List[int] = [None]
    MM_osc: List[int] = [None]
    DD_osc: List[int] = [None]
    MeanAnomaly: List[float] = [np.nan]
    ArgPerihelion: List[float] = [np.nan]
    LongAscNode: List[float] = [np.nan]
    Inclination: List[float] = [np.nan]
    Eccentricity: List[float] = [np.nan]
    SemimajorAxis: List[float] = [np.nan]
    YY_calulation: List[int] = [None]
    MM_calulation: List[int] = [None]
    DD_calulation: List[int] = [None]
    CEU_value: List[float] = [np.nan]
    CEU_rate: List[float] = [np.nan]
    CEU_yy: List[int] = [None]
    CEU_mm: List[int] = [None]
    CEU_dd: List[int] = [None]
    PEU_value: List[float] = [np.nan]
    PEU_yy: List[int] = [None]
    PEU_mm: List[int] = [None]
    PEU_dd: List[int] = [None]
    GPEU_fromCEU: List[float] = [np.nan]
    GPEU_yy: List[int] = [None]
    GPEU_mm: List[int] = [None]
    GPEU_dd: List[int] = [None]
    GPEU_fromPEU: List[float] = [np.nan]
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
    iddataset: List[int] = [None]


class Mpcorb(pydantic.BaseModel):
    """MPCORB database"""

    id_: List[int] = pydantic.Field([None], alias="id")
    packed_name: List[str] = [""]
    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    name: List[str] = [""]
    H: List[float] = [np.nan]
    G: List[float] = [np.nan]
    ref_date: List[str] = [""]
    MeanAnomaly: List[float] = [np.nan]
    ArgPerihelion: List[float] = [np.nan]
    LongAscNode: List[float] = [np.nan]
    Inclination: List[float] = [np.nan]
    Eccentricity: List[float] = [np.nan]
    MeanMotion: List[float] = [np.nan]
    SemimajorAxis: List[float] = [np.nan]
    U: List[str] = [""]
    reference: List[str] = [""]
    NumberObs: List[int] = [None]
    NumberOpp: List[int] = [None]
    start_obs: List[int] = [None]
    end_obs: List[int] = [None]
    OrbArc: List[float] = [np.nan]
    rms: List[float] = [np.nan]
    coarse_indic: List[str] = [""]
    precise_indic: List[str] = [""]
    OrbComputer: List[str] = [""]
    orbit_type: List[str] = [""]
    last_obs_date: List[str] = [""]
    iddataset: List[int] = [None]


class Cometpro(pydantic.BaseModel):
    """COMETRO database"""

    id_: List[int] = pydantic.Field([None], alias="id")
    note: List[int] = [None]
    updated: List[str] = [""]
    name: List[str] = [""]
    iau_name: List[str] = [""]
    author: List[str] = [""]
    epoch: List[float] = ([np.nan],)
    force_relat: List[int] = [None]
    nb_obs: List[int] = [None]
    sigma: List[float] = ([np.nan],)
    start_date: List[str] = [""]
    end_date: List[str] = [""]
    px: List[float] = [np.nan]
    py: List[float] = [np.nan]
    pz: List[float] = [np.nan]
    vx: List[float] = [np.nan]
    vy: List[float] = [np.nan]
    vz: List[float] = [np.nan]
    fngA1: List[float] = [np.nan]
    fngA2: List[float] = [np.nan]
    fngA3: List[float] = [np.nan]
    tau: List[float] = [np.nan]
    PerihelionDist: List[float] = [np.nan]
    Eccentricity: List[float] = [np.nan]
    ArgPerihelion: List[float] = [np.nan]
    LongAscNode: List[float] = [np.nan]
    Inclination: List[float] = [np.nan]
    magH1: List[float] = [np.nan]
    magR1: List[float] = [np.nan]
    magD1: List[float] = [np.nan]
    magH2: List[float] = [np.nan]
    magR2: List[float] = [np.nan]
    magD2: List[float] = [np.nan]
    iddataset: List[int] = [None]


class Exoplanets(pydantic.BaseModel):
    """Exoplanet database"""

    id_: List[int] = pydantic.Field([None], alias="id")
    name: List[str] = [""]
    ra_j2000: List[float] = [np.nan]
    dec_j2000: List[float] = [np.nan]
    star_name: List[str] = [""]
    star_distance: List[float] = [np.nan]
    star_spec_type: List[str] = [""]
    iddataset: List[int] = [None]


class Spacecrafts(pydantic.BaseModel):
    """Spacecraft database"""

    id_: List[int] = pydantic.Field([None], alias="id")
    international_designator: List[str] = [""]
    norad_number: List[int] = [None]
    multiple_name_flag: List[str] = [""]
    payload_flag: List[str] = [""]
    operational_status_code: List[str] = [""]
    norad_name: List[str] = [""]
    source_ownership: List[str] = [""]
    launch_date: List[str] = [""]
    launch_site: List[str] = [""]
    orbital_period: List[float] = [np.nan]
    inclination: List[float] = [np.nan]
    apogee_altitude: List[float] = [np.nan]
    perigee_altitude: List[float] = [np.nan]
    radar_cross_section: List[float] = [np.nan]
    orbital_status_code: List[str] = [""]
    operational_status: List[str] = [""]
    orbital_status: List[str] = [""]
    central_body: List[str] = [""]
    orbit_type: List[str] = [""]
    iddataset: List[int] = [None]


class Binarymp(pydantic.BaseModel):
    """Orbital properties of multiple asteroidal systems"""

    id_: List[int] = pydantic.Field([None], alias="id")
    system_type: List[str] = [""]
    system_id: List[int] = [None]
    system_name: List[str] = [""]
    sol_id: List[str] = [""]
    method: List[str] = [""]
    f_omc: List[float] = [np.nan]
    proba: List[float] = [np.nan]
    name: List[str] = [""]
    t0_orbit: List[float] = [np.nan]
    period: List[float] = [np.nan]
    err_period: List[float] = [np.nan]
    a: List[float] = [np.nan]
    err_a: List[float] = [np.nan]
    e: List[float] = [np.nan]
    err_e: List[float] = [np.nan]
    i: List[float] = [np.nan]
    err_i: List[float] = [np.nan]
    omega: List[float] = [np.nan]
    err_omega: List[float] = [np.nan]
    omegap: List[float] = [np.nan]
    err_omegap: List[float] = [np.nan]
    tpp: List[float] = [np.nan]
    err_tpp: List[float] = [np.nan]
    am: List[float] = [np.nan]
    err_am: List[float] = [np.nan]
    n: List[float] = [np.nan]
    err_n: List[float] = [np.nan]
    a_over_d1: List[float] = [np.nan]
    err_a_over_d1: List[float] = [np.nan]
    d2_over_d1: List[float] = [np.nan]
    err_d2_over_d1: List[float] = [np.nan]
    alpha: List[float] = [np.nan]
    err_alpha: List[float] = [np.nan]
    delta: List[float] = [np.nan]
    err_delta: List[float] = [np.nan]
    lambda_: List[float] = pydantic.Field([np.nan], alias="lambda")
    err_lambda: List[float] = [np.nan]
    beta: List[float] = [np.nan]
    err_beta: List[float] = [np.nan]
    mass: List[float] = [np.nan]
    err_mass: List[float] = [np.nan]
    density: List[float] = [np.nan]
    err_density: List[float] = [np.nan]
    mean_radius: List[float] = [np.nan]
    err_mean_radius: List[float] = [np.nan]
    j2: List[float] = [np.nan]
    err_j2: List[float] = [np.nan]
    j4: List[float] = [np.nan]
    err_j4: List[float] = [np.nan]
    t0_spin: List[float] = [np.nan]
    pn0: List[float] = [np.nan]
    err_pn0: List[float] = [np.nan]
    pn1: List[float] = [np.nan]
    err_pn1: List[float] = [np.nan]
    ap0: List[float] = [np.nan]
    err_ap0: List[float] = [np.nan]
    ap1: List[float] = [np.nan]
    err_ap1: List[float] = [np.nan]
    dp0: List[float] = [np.nan]
    err_dp0: List[float] = [np.nan]
    dp1: List[float] = [np.nan]
    err_dp1: List[float] = [np.nan]
    iddataset: List[int] = [None]


class Diamalbedo(pydantic.BaseModel):
    """Diameters and Albedos database from literature"""

    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    name: List[str] = [""]
    diameter: List[float] = [np.nan]
    err_diameter_up: List[float] = [np.nan]
    err_diameter_down: List[float] = [np.nan]
    albedo: List[float] = [np.nan]
    err_albedo_up: List[float] = [np.nan]
    err_albedo_down: List[float] = [np.nan]
    beaming: List[float] = [np.nan]
    err_beaming: List[float] = [np.nan]
    emissivity: List[float] = [np.nan]
    err_emissivity: List[float] = [np.nan]
    selection: List[int] = [None]
    method: List[str] = [""]

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


class Masses(pydantic.BaseModel):
    """Mass database from literature"""

    id_: List[int] = pydantic.Field([None], alias="id")
    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    name: List[str] = [""]
    mass: List[float] = [np.nan]
    err_mass_max: List[float] = [np.nan]
    err_mass_min: List[float] = [np.nan]
    method: List[str] = [""]
    selection: List[int] = [None]
    iddataset: List[int] = [None]

    preferred: List[bool] = [False]

    @pydantic.validator("preferred", pre=True)
    def select_preferred_mass(cls, _, values):
        return rocks.definitions.rank_properties("mass", values)


class Taxonomies(pydantic.BaseModel):
    """Taxonomy database from literature"""

    # id_: List[int] = pydantic.Field([None], alias="id")
    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    name: List[str] = [""]
    year: List[int] = [None]
    scheme: List[str] = [""]
    class_: List[str] = pydantic.Field([""], alias="class")
    complex: List[str] = [""]
    selection: List[int] = [None]
    method: List[str] = [""]
    shortbib: List[str] = [""]
    waverange: List[str] = [""]
    # iddataset: List[int] = [None]


class Proper_elements(pydantic.BaseModel):
    """Proper Elements from literature"""

    id_: List[int] = pydantic.Field([None], alias="id")
    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    name: List[str] = [""]
    H: List[float] = [np.nan]
    ProperSemimajorAxis: List[float] = [np.nan]
    err_ProperSemimajorAxis: List[float] = [np.nan]
    ProperEccentricity: List[float] = [np.nan]
    err_ProperEccentricity: List[float] = [np.nan]
    ProperSinI: List[float] = [np.nan]
    err_ProperSinI: List[float] = [np.nan]
    ProperInclination: List[float] = [np.nan]
    err_ProperInclination: List[float] = [np.nan]
    n: List[float] = [np.nan]
    err_n: List[float] = [np.nan]
    g: List[float] = [np.nan]
    err_g: List[float] = [np.nan]
    s: List[float] = [np.nan]
    err_s: List[float] = [np.nan]
    LCE: List[float] = [np.nan]
    My: List[float] = [np.nan]
    lam_fit: List[float] = pydantic.Field([np.nan], alias="lam-fit")
    identfrom: List[str] = [""]
    iddataset: List[int] = [None]


class Phase_function(pydantic.BaseModel):
    """Database of asteroid phase function"""

    id_: List[int] = pydantic.Field([None], alias="id")
    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    name: List[str] = [""]
    H: List[float] = [np.nan]
    G1: List[float] = [np.nan]
    G2: List[float] = [np.nan]
    H_min: List[float] = [np.nan]
    H_max: List[float] = [np.nan]
    G1_min: List[float] = [np.nan]
    G1_max: List[float] = [np.nan]
    G2_min: List[float] = [np.nan]
    G2_max: List[float] = [np.nan]
    N: List[int] = [None]
    phase_min: List[float] = [np.nan]
    phase_max: List[float] = [np.nan]
    rms: List[float] = [np.nan]
    facility: List[str] = [""]
    name_filter: List[str] = [""]
    id_filter: List[str] = [""]
    selection: List[int] = [None]
    iddataset: List[int] = [None]


class Families(pydantic.BaseModel):
    """Database of Sso families"""

    id_: List[int] = pydantic.Field([None], alias="id")
    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    name: List[str] = [""]
    family_status: List[str] = [""]
    family_number: List[int] = [None]
    family_name: List[str] = [""]
    membership: List[int] = [None]
    selection: List[int] = [None]
    iddataset: List[int] = [None]


class Pairs(pydantic.BaseModel):
    """Database of Sso pairs"""

    id_: List[int] = pydantic.Field([None], alias="id")
    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    name: List[str] = [""]
    sibling_number: List[int] = pydantic.Field([None], alias="sibling_num")
    sibling_name: List[str] = [""]
    delta_v: List[float] = [np.nan]
    delta_a: List[float] = [np.nan]
    delta_e: List[float] = [np.nan]
    delta_sini: List[float] = [np.nan]
    delta_i: List[float] = [np.nan]
    membership: List[int] = [None]
    selection: List[int] = [None]
    iddataset: List[int] = [None]


class Spin(pydantic.BaseModel):
    """Database of Sso spin coordiantes"""

    id_: List[int] = pydantic.Field([None], alias="id")
    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    name: List[str] = [""]
    model_dbid: List[str] = [""]
    model_name: List[str] = [""]
    model_id: List[str] = [""]
    t0: List[float] = [np.nan]
    RA0: List[float] = [np.nan]
    DEC0: List[float] = [np.nan]
    W0: List[float] = [np.nan]
    Wp: List[float] = [np.nan]
    period: List[float] = [np.nan]
    err_period: List[float] = [np.nan]
    period_flag: List[float] = [np.nan]
    period_type: List[str] = [""]
    long: List[float] = [np.nan]
    lat: List[float] = [np.nan]
    err_long: List[float] = [np.nan]
    err_lat: List[float] = [np.nan]
    selection: List[int] = [None]
    method: List[str] = [""]
    iddataset: List[str] = [""]


class Yarkovsky(pydantic.BaseModel):
    """Database of Sso Yarkovsky accelerations"""

    id_: List[int] = pydantic.Field([None], alias="id")
    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    name: List[str] = [""]
    A2: List[float] = [np.nan]
    err_A2: List[float] = [np.nan]
    dadt: List[float] = [np.nan]
    err_dadt: List[float] = [np.nan]
    snr: List[float] = [np.nan]
    S: List[float] = [np.nan]
    selection: List[int] = [None]
    method: List[str] = [""]
    iddataset: List[int] = [None]


class Thermal_properties(pydantic.BaseModel):
    """Database of asteroid thermal properties"""

    id_: List[int] = pydantic.Field([None], alias="id")
    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    name: List[str] = [""]
    TI: List[float] = [np.nan]
    err_TI_up: List[float] = [np.nan]
    err_TI_down: List[float] = [np.nan]
    dsun: List[float] = [np.nan]
    selection: List[int] = [None]
    method: List[str] = [""]
    iddataset: List[int] = [None]


class Colors(pydantic.BaseModel):
    """Database of asteroid colors"""

    id_: List[int] = pydantic.Field([None], alias="id")
    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    name: List[str] = [""]
    color: List[str] = [""]
    value: List[float] = [np.nan]
    uncertainty: List[float] = [np.nan]
    from_: List[str] = pydantic.Field([""], alias="from")
    observer: List[str] = [""]
    epoch: List[str] = [""]
    delta_time: List[str] = [""]
    color_type: List[str] = [""]
    id_filter_1: List[str] = [""]
    id_filter_2: List[str] = [""]
    phot_sys: List[str] = [""]
    selection: List[int] = [None]
    iddataset: List[int] = [None]


class Density(pydantic.BaseModel):
    """Database of asteroid density"""

    id_: List[int] = pydantic.Field([None], alias="id")
    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    name: List[str] = [""]
    density: List[float] = [np.nan]
    err_density_up: List[float] = [np.nan]
    err_density_down: List[float] = [np.nan]
    method: List[str] = [""]
    selection: List[int] = [None]
    iddataset: List[int] = [None]


class Mpcatobs(pydantic.BaseModel):
    """MPCAT-OBS database"""

    id_: List[int] = pydantic.Field([None], alias="id")
    type: List[str] = [""]
    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    packed_name: List[str] = [""]
    name: List[str] = [""]
    orb_type: List[str] = [""]
    discovery: List[str] = [""]
    note1: List[str] = [""]
    note2: List[str] = [""]
    date_obs: List[str] = [""]
    jd_obs: List[float] = [np.nan]
    ra_obs: List[float] = [np.nan]
    dec_obs: List[float] = [np.nan]
    mag: List[float] = [np.nan]
    filter: List[str] = [""]
    note3: List[str] = [""]
    note4: List[str] = [""]
    iau_code: List[str] = [""]
    vgs_x: List[float] = [np.nan]
    vgs_y: List[float] = [np.nan]
    vgs_z: List[float] = [np.nan]
    iddataset: List[int] = [None]
