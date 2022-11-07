#!/usr/bin/env python
"""Implement the Datacloud catalogue pydantic models."""

import re
from typing import List, Optional

import numpy as np
import pandas as pd
import pydantic
import rich
from rich.table import Table

from rocks import config
from rocks import core
from rocks.logging import logger

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

    # Sort catalogue by year of reference
    if "year" in catalogue.columns:
        catalogue = catalogue.sort_values("year").reset_index()

    # ------
    # Create table to echo
    if parameter in ["diameters", "albedos"]:
        if parameter == "diameters":
            preferred = catalogue.preferred_diameter
        elif parameter == "albedos":
            preferred = catalogue.preferred_albedo
    elif hasattr(catalogue, "preferred"):
        preferred = catalogue.preferred
    else:
        preferred = [False for _ in range(len(catalogue))]

    # Only show the caption if there is a preferred entry
    if any(preferred):
        caption = "Green: preferred entry"
    else:
        caption = None

    table = Table(
        header_style="bold blue",
        box=rich.box.SQUARE,
        footer_style="dim",
        title=f"({rock.number}) {rock.name}",
        caption=caption,
    )

    # The columns depend on the catalogue
    columns = [""] + config.DATACLOUD[parameter]["print_columns"]

    for c in columns:
        table.add_column(c)

    # Some catalogues do not have a "preferred" attribute
    # if not hasattr(catalogue, "preferred"):
    #     preferred = [False for _ in range(len(catalogue))]
    # else:

    # Add rows to table, styling by preferred-state of entry
    for i, pref in enumerate(preferred):

        if parameter in ["diamalbedos"]:
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
            *[str(catalogue[c][i]) if c else str(i + 1) for c in columns],
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
        return weighted_average(self, parameter)


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


def empty_str_to_none(value):
    for i, v in enumerate(value[:]):
        if v == "":
            value[i] = None
    return value


def empty_str_to_nan(value):
    for i, v in enumerate(value[:]):
        if v == "":
            value[i] = np.nan
    return value


def get_preferred(name, parameter, ids):
    """Get the preferred values for this catalogue from the ssoCard of the object.

    Parameters
    ----------
    name : str
        The asteroid name, extracted from the datacloud catalogue.
    parameter : str
        The full parameter path in the ssoCard.
    ids : list of int
        List of dataset ids present in the datacloud catalogue.

    Returns
    -------
    list of bool
        True if the id belongs to a preferred entry, else False.
    """

    # Get ssoCard
    ssoCard = core.Rock(name)

    # Get selected parameters
    link_selection = core.rgetattr(ssoCard, f"{parameter}.links.selection")

    if not link_selection:
        return [False for id_ in ids]

    # Parse selection link for preferred dataset ids
    match = re.search(r"(.+)(:id=)([0-9,]+)(.*)", link_selection)
    ids_preferred = match.group(3)
    ids_preferred = [int(id_) for id_ in ids_preferred.split(",")]

    # Create list of preferred dataset ids
    preferred = [True if id_ in ids_preferred else False for id_ in ids]

    # If all are preferred, none are preferred
    if all(preferred):
        preferred = [False for _ in preferred]

    return preferred


# ------
# SsODNet catalogues as pydantic model
# https://ssp.imcce.fr/data/ssodnet_datacloud.sql

# Metacatalogues
class Collection(pydantic.BaseModel):
    """Table de definition des references des jeux de donnees de la base SsODNet.datacloud"""

    link: List[str] = [""]
    title: List[str] = [""]
    shortbib: List[str] = [""]
    datasetname: List[str] = [""]
    idcollection: List[int] = [None]
    resourcename: List[str] = [""]
    bibcode: List[str] = [""]
    doi: List[str] = [""]
    year: List[int] = [None]


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
    bibtex: List[str] = [""]


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
    orbit_computer: List[str] = [""]
    H: List[float] = [np.nan]
    G: List[float] = [np.nan]
    B_V: List[float] = [np.nan]
    IRAS_diameter: List[float] = [np.nan]
    IRAS_class: List[str] = [""]
    note_1: List[int] = [None]
    note_2: List[int] = [None]
    note_3: List[int] = [None]
    note_4: List[int] = [None]
    note_5: List[int] = [None]
    note_6: List[int] = [None]
    orbital_arc: List[int] = [None]
    number_observation: List[int] = [None]
    yy_osc: List[int] = [None]
    mm_osc: List[int] = [None]
    dd_osc: List[int] = [None]
    mean_anomaly: List[float] = [np.nan]
    perihelion_argument: List[float] = [np.nan]
    node_longitude: List[float] = [np.nan]
    inclination: List[float] = [np.nan]
    eccentricity: List[float] = [np.nan]
    semi_major_axis: List[float] = [np.nan]
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
    jd_osc: List[float] = [np.nan]
    px: List[float] = [np.nan]
    py: List[float] = [np.nan]
    pz: List[float] = [np.nan]
    vx: List[float] = [np.nan]
    vy: List[float] = [np.nan]
    vz: List[float] = [np.nan]
    mean_motion: List[float] = [np.nan]
    orbital_period: List[float] = [np.nan]
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
    mean_anomaly: List[float] = [np.nan]
    perihelion_argument: List[float] = [np.nan]
    node_longitude: List[float] = [np.nan]
    inclination: List[float] = [np.nan]
    eccentricity: List[float] = [np.nan]
    mean_motion: List[float] = [np.nan]
    semi_major_axis: List[float] = [np.nan]
    U: List[str] = [""]
    reference: List[str] = [""]
    number_observation: List[int] = [None]
    number_opposition: List[int] = [None]
    start_obs: List[int] = [None]
    end_obs: List[int] = [None]
    orbital_arc: List[float] = [np.nan]
    rms: List[float] = [np.nan]
    coarse_indic: List[str] = [""]
    precise_indic: List[str] = [""]
    orbit_computer: List[str] = [""]
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
    perihelion_distance: List[float] = [np.nan]
    eccentricity: List[float] = [np.nan]
    perihelion_argument: List[float] = [np.nan]
    node_longitude: List[float] = [np.nan]
    inclination: List[float] = [np.nan]
    mag_H1: List[float] = [np.nan]
    mag_R1: List[float] = [np.nan]
    mag_D1: List[float] = [np.nan]
    mag_H2: List[float] = [np.nan]
    mag_R2: List[float] = [np.nan]
    mag_D2: List[float] = [np.nan]
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


class Diamalbedo(Collection):
    """Diameters and Albedos database from literature"""

    id_: List[int] = pydantic.Field([None], alias="id")
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
    bibcode: List[str] = [""]

    preferred_albedo: List[bool] = [False]
    preferred_diameter: List[bool] = [False]
    preferred: List[bool] = [False]

    @pydantic.validator("preferred_albedo", pre=True, allow_reuse=True)
    def select_preferred(cls, _, values):
        return get_preferred(
            values["name"][0], "parameters.physical.albedo", values["id_"]
        )

    @pydantic.validator("preferred_diameter", pre=True, allow_reuse=True)
    def select_preferred(cls, _, values):
        return get_preferred(
            values["name"][0], "parameters.physical.diameter", values["id_"]
        )

    @pydantic.validator("preferred", pre=True)
    def preferred_albedo_or_diameter(cls, _, values):
        return [
            True if pref_alb or pref_diam else False
            for pref_alb, pref_diam in zip(
                values["preferred_albedo"], values["preferred_diameter"]
            )
        ]


class Masses(Collection):
    """Mass database from literature"""

    id_: List[int] = pydantic.Field([None], alias="id")
    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    name: List[str] = [""]
    mass: List[float] = [np.nan]
    err_mass_up: List[float] = [np.nan]
    err_mass_down: List[float] = [np.nan]
    method: List[str] = [""]
    selection: List[int] = [None]
    iddataset: List[int] = [None]

    preferred: List[bool] = [False]

    @pydantic.validator("preferred", pre=True)
    def select_preferred(cls, _, values):
        return get_preferred(
            values["name"][0], "parameters.physical.mass", values["id_"]
        )


class Taxonomies(Collection):
    """Taxonomy database from literature"""

    id_: List[int] = pydantic.Field([None], alias="id")
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

    preferred: List[bool] = [False]

    @pydantic.validator("preferred", pre=True)
    def select_preferred(cls, _, values):
        return get_preferred(
            values["name"][0], "parameters.physical.taxonomy", values["id_"]
        )


class Proper_elements(Collection):
    """Proper Elements from literature"""

    id_: List[int] = pydantic.Field([None], alias="id")
    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    name: List[str] = [""]
    H: List[float] = [np.nan]
    proper_semi_major_axis: List[float] = [np.nan]
    err_proper_semi_major_axis: List[float] = [np.nan]
    proper_eccentricity: List[float] = [np.nan]
    err_proper_eccentricity: List[float] = [np.nan]
    proper_sine_inclination: List[float] = [np.nan]
    err_proper_sine_inclination: List[float] = [np.nan]
    proper_inclination: List[float] = [np.nan]
    err_proper_inclination: List[float] = [np.nan]
    proper_frequency_mean_motion: List[float] = [np.nan]
    err_proper_frequency_mean_motion: List[float] = [np.nan]
    proper_frequency_perihelion_longitude: List[float] = [np.nan]
    err_proper_frequency_perihelion_longitude: List[float] = [np.nan]
    proper_frequency_nodal_longitude: List[float] = [np.nan]
    err_proper_frequency_nodal_longitude: List[float] = [np.nan]
    lyapunov_time: List[float] = [np.nan]
    integration_time: List[float] = [np.nan]
    identfrom: List[str] = [""]
    iddataset: List[int] = [None]


class Phase_function(Collection):
    """Database of asteroid phase function"""

    id_: List[int] = pydantic.Field([None], alias="id")
    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    name: List[str] = [""]
    H: List[float] = [np.nan]
    G1: List[float] = [np.nan]
    G2: List[float] = [np.nan]
    err_H_down: List[float] = [np.nan]
    err_H_up: List[float] = [np.nan]
    err_G1_down: List[float] = [np.nan]
    err_G1_up: List[float] = [np.nan]
    err_G2_down: List[float] = [np.nan]
    err_G2_up: List[float] = [np.nan]
    N: List[int] = [None]
    phase_min: List[float] = [np.nan]
    phase_max: List[float] = [np.nan]
    rms: List[float] = [np.nan]
    facility: List[str] = [""]
    name_filter: List[str] = [""]
    id_filter: List[str] = [""]
    selection: List[int] = [None]
    iddataset: List[int] = [None]


class Families(Collection):
    """Database of Sso families"""

    id_: List[int] = pydantic.Field([None], alias="id")
    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    name: List[str] = [""]
    family_status: List[str] = [""]
    family_number: List[int] = pydantic.Field([None], alias="family_num")
    family_name: List[str] = [""]
    membership: List[int] = [None]
    selection: List[int] = [None]
    method: List[str] = [""]
    iddataset: List[int] = [None]


class Pairs(Collection):
    """Database of Sso pairs"""

    id_: List[int] = pydantic.Field([None], alias="id")
    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    name: List[str] = [""]
    sibling_number: List[int] = pydantic.Field([None], alias="sibling_num")
    sibling_name: List[str] = [""]
    distance: List[float] = [np.nan]
    age: List[float] = [np.nan]
    err_age_up: List[float] = [np.nan]
    err_age_down: List[float] = [np.nan]
    selection: List[int] = [None]
    method: List[str] = [""]
    iddataset: List[int] = [None]


class Spin(Collection):
    """Database of Sso spin coordiantes"""

    id_: List[int] = pydantic.Field([None], alias="id")
    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    name: List[str] = [""]
    model_dbid: List[str] = [""]
    model_name: List[str] = [""]
    model_id: List[str] = [""]
    t0: List[float] = [np.nan]
    W0: List[float] = [np.nan]
    Wp: List[float] = [np.nan]
    RA0: List[float] = [np.nan]
    DEC0: List[float] = [np.nan]
    err_RA0: List[float] = [np.nan]
    err_DEC0: List[float] = [np.nan]
    period: List[float] = [np.nan]
    err_period: List[float] = [np.nan]
    period_flag: List[float] = [np.nan]
    period_type: List[str] = [""]
    long_: List[float] = pydantic.Field([np.nan], alias="long")
    lat: List[float] = [np.nan]
    err_long: List[float] = [np.nan]
    err_lat: List[float] = [np.nan]
    selection: List[int] = [None]
    method: List[str] = [""]
    iddataset: List[str] = [""]

    _empty_str_to_nan: classmethod = pydantic.validator(
        "Wp",
        "RA0",
        "DEC0",
        "err_RA0",
        "period",
        "err_period",
        "err_long",
        "err_lat",
        "err_DEC0",
        "long_",
        "lat",
        allow_reuse=True,
        pre=True,
    )(empty_str_to_nan)

    _empty_str_to_none: classmethod = pydantic.validator(
        "number",
        allow_reuse=True,
        pre=True,
    )(empty_str_to_none)


class Yarkovsky(Collection):
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


class Thermal_inertia(Collection):
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

    preferred: List[bool] = [False]

    @pydantic.validator("preferred", pre=True)
    def select_preferred(cls, _, values):
        return get_preferred(
            values["name"][0], "parameters.physical.thermal_inertia", values["id_"]
        )


class Colors(Collection):
    """Database of asteroid colors"""

    id_: List[int] = pydantic.Field([None], alias="id")
    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    name: List[str] = [""]
    color: List[str] = [""]
    value: List[float] = [np.nan]
    uncertainty: List[float] = [np.nan]
    facility: List[str] = [""]
    observer: List[str] = [""]
    epoch: List[str] = [""]
    delta_time: List[str] = [""]
    color_type: List[str] = [""]
    id_filter_1: List[str] = [""]
    id_filter_2: List[str] = [""]
    phot_sys: List[str] = [""]
    selection: List[int] = [None]
    iddataset: List[int] = [None]


class Density(Collection):
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


class Mpcatobs(Collection):
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
    obs_long: List[float] = [np.nan]
    obs_lat: List[float] = [np.nan]
    obs_alt: List[float] = [np.nan]
    vgs_x: List[float] = [np.nan]
    vgs_y: List[float] = [np.nan]
    vgs_z: List[float] = [np.nan]
    iddataset: List[int] = [None]


class Shape(Collection):
    """Database of Sso triaxial ellipsoid and shape models"""

    id_: List[int] = pydantic.Field([None], alias="id")
    iddataset: List[int] = [None]
    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    name: List[str] = [""]
    model_dbid: List[str] = [""]
    model_name: List[str] = [""]
    model_id: List[str] = [""]
    scaled: List[int] = [None]
    radius_a: List[float] = [np.nan]
    radius_b: List[float] = [np.nan]
    radius_c: List[float] = [np.nan]
    selected: List[int] = [None]


def weighted_average(catalogue, parameter):
    """Computes weighted average of observable.

    Parameters
    ----------
    observable : np.ndarray
        Float values of observable
    error : np.ndarray
        Corresponding errors of observable.

    Returns
    -------
    float
        The weighted average.

    float
        The standard error of the weighted average.
    """
    catalogue = catalogue[catalogue[parameter] != 0]

    values = catalogue[parameter]

    if parameter in ["albedo", "diameter"]:
        preferred = catalogue[f"preferred_{parameter}"]

        if not any(preferred):
            preferred = ~preferred

        errors = catalogue[f"err_{parameter}_up"]
    else:
        preferred = catalogue["preferred"]
        errors = catalogue[f"err_{parameter}"]

    observable = np.array(values)[preferred]
    error = np.array(errors)[preferred]

    if all(np.isnan(value) for value in values) or all(
        np.isnan(error) for error in errors
    ):
        logger.error(
            f"{catalogue.name[0]}: The values or errors of property '{parameter}' are all NaN. Average failed."
        )
        return np.nan, np.nan

    # If no data was passed (happens when no preferred entry in table)
    if not observable.size:
        return (np.nan, np.nan)

    if len(observable) == 1:
        return (observable[0], error[0])

    if any(e == 0 for e in error):
        weights = np.ones(observable.shape)
        logger.debug("Encountered zero in errors array. Setting all weights to 1.")
    else:
        # Compute normalized weights
        weights = 1 / np.array(error) ** 2

    # Compute weighted average and uncertainty
    avg = np.average(observable, weights=weights)

    # Kirchner Case II
    # http://seismo.berkeley.edu/~kirchner/Toolkits/Toolkit_12.pdf
    var_avg = (
        len(observable)
        / (len(observable) - 1)
        * (
            sum(w * o**2 for w, o in zip(weights, observable)) / sum(weights)
            - avg**2
        )
    )
    std_avg = np.sqrt(var_avg / len(observable))
    return avg, std_avg
