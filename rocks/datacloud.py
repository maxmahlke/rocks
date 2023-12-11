"""Implement the Datacloud catalogue pydantic models."""

import re
from typing import List, Optional, Union

import numpy as np
import pandas as pd
import pydantic
import rich

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
    from rich.table import Table

    if len(catalogue) == 1 and pd.isna(catalogue["name"][0]):
        rich.print(f"No {parameter} on record for {rock.name}.")
        return

    # Sort catalogue by year of reference
    if "year" in catalogue.columns:
        catalogue = catalogue.sort_values("year").reset_index()

    # ------
    # Create table to echo
    if parameter in ["diameters", "albedos"]:
        if parameter == "diameters":
            catalogue = catalogue.dropna(subset=["diameter"])
            preferred = catalogue.preferred_diameter
        elif parameter == "albedos":
            catalogue = catalogue.dropna(subset=["albedo"])
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
        box=rich.box.ASCII2,
        header_style="dim",
        footer_style="dim",
        title_style="dim",
        caption_style="dim",
        caption=caption,
    )

    table.title = f"({rock.number}) {rock.name}"

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
                    style = "bold"
            else:
                style = "white"

        else:
            style = "bold" if pref else "dim"

        table.add_row(
            *[str(catalogue[c].values[i]) if c else str(i + 1) for c in columns],
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

    link: List[Optional[str]] = [""]
    title: List[Optional[str]] = [""]
    shortbib: List[Optional[str]] = [""]
    datasetname: List[Optional[str]] = [""]
    idcollection: List[Optional[int]] = [None]
    resourcename: List[Optional[str]] = [""]
    bibcode: List[Optional[str]] = [""]
    doi: List[Optional[str]] = [""]
    year: List[Optional[int]] = [None]


class Methods(pydantic.BaseModel):
    """Table of definition of the methods used to determine the data"""

    idmethod: List[Optional[int]] = [None]
    method: List[Optional[str]] = [""]
    fullname: List[Optional[str]] = [""]
    description: List[Optional[str]] = [""]
    shortbib: List[Optional[str]] = [""]
    year: List[Optional[int]] = [None]
    source: List[Optional[str]] = [""]
    title: List[Optional[str]] = [""]
    bibcode: List[Optional[str]] = [""]
    doi: List[Optional[str]] = [""]
    bibtex: List[Optional[str]] = [""]


class Dataset_ref(pydantic.BaseModel):
    """Dataset references"""

    iddataset: List[Optional[int]] = [None]
    shortbib: List[Optional[str]] = [""]
    year: List[Optional[int]] = [None]
    source: List[Optional[str]] = [""]
    title: List[Optional[str]] = [""]
    url: List[Optional[str]] = [""]
    bibcode: List[Optional[str]] = [""]
    doi: List[Optional[str]] = [""]
    idcollection: List[Optional[int]] = [None]
    bibtex: List[Optional[str]] = [""]


class Dataset_list(pydantic.BaseModel):
    """Dataset list"""

    idsso: List[Optional[int]] = [None]
    name: List[Optional[str]] = [""]
    datasetlist: List[Optional[str]] = [""]


# Parameter Catalogues
class Astorb(pydantic.BaseModel):
    """ASTORB database"""

    id_: List[Optional[int]] = pydantic.Field([None], alias="id")
    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    name: List[Optional[str]] = [""]
    orbit_computer: List[Optional[str]] = [""]
    H: List[Optional[float]] = [np.nan]
    G: List[Optional[float]] = [np.nan]
    B_V: List[Optional[float]] = [np.nan]
    IRAS_diameter: List[Optional[float]] = [np.nan]
    IRAS_class: List[Optional[str]] = [""]
    note_1: List[Optional[int]] = [None]
    note_2: List[Optional[int]] = [None]
    note_3: List[Optional[int]] = [None]
    note_4: List[Optional[int]] = [None]
    note_5: List[Optional[int]] = [None]
    note_6: List[Optional[int]] = [None]
    orbital_arc: List[Optional[int]] = [None]
    number_observation: List[Optional[int]] = [None]
    yy_osc: List[Optional[int]] = [None]
    mm_osc: List[Optional[int]] = [None]
    dd_osc: List[Optional[int]] = [None]
    mean_anomaly: List[Optional[float]] = [np.nan]
    perihelion_argument: List[Optional[float]] = [np.nan]
    node_longitude: List[Optional[float]] = [np.nan]
    inclination: List[Optional[float]] = [np.nan]
    eccentricity: List[Optional[float]] = [np.nan]
    semi_major_axis: List[Optional[float]] = [np.nan]
    YY_calulation: List[Optional[int]] = [None]
    MM_calulation: List[Optional[int]] = [None]
    DD_calulation: List[Optional[int]] = [None]
    CEU_value: List[Optional[float]] = [np.nan]
    CEU_rate: List[Optional[float]] = [np.nan]
    CEU_yy: List[Optional[int]] = [None]
    CEU_mm: List[Optional[int]] = [None]
    CEU_dd: List[Optional[int]] = [None]
    PEU_value: List[Optional[float]] = [np.nan]
    PEU_yy: List[Optional[int]] = [None]
    PEU_mm: List[Optional[int]] = [None]
    PEU_dd: List[Optional[int]] = [None]
    GPEU_fromCEU: List[Optional[float]] = [np.nan]
    GPEU_yy: List[Optional[int]] = [None]
    GPEU_mm: List[Optional[int]] = [None]
    GPEU_dd: List[Optional[int]] = [None]
    GPEU_fromPEU: List[Optional[float]] = [np.nan]
    GGPEU_yy: List[Optional[int]] = [None]
    GGPEU_mm: List[Optional[int]] = [None]
    GGPEU_dd: List[Optional[int]] = [None]
    jd_osc: List[Optional[float]] = [np.nan]
    px: List[Optional[float]] = [np.nan]
    py: List[Optional[float]] = [np.nan]
    pz: List[Optional[float]] = [np.nan]
    vx: List[Optional[float]] = [np.nan]
    vy: List[Optional[float]] = [np.nan]
    vz: List[Optional[float]] = [np.nan]
    mean_motion: List[Optional[float]] = [np.nan]
    orbital_period: List[Optional[float]] = [np.nan]
    iddataset: List[Optional[int]] = [None]


class Mpcorb(pydantic.BaseModel):
    """MPCORB database"""

    id_: List[Optional[int]] = pydantic.Field([None], alias="id")
    packed_name: List[Optional[str]] = [""]
    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    name: List[Optional[str]] = [""]
    H: List[Optional[float]] = [np.nan]
    G: List[Optional[float]] = [np.nan]
    ref_date: List[Optional[str]] = [""]
    mean_anomaly: List[Optional[float]] = [np.nan]
    perihelion_argument: List[Optional[float]] = [np.nan]
    node_longitude: List[Optional[float]] = [np.nan]
    inclination: List[Optional[float]] = [np.nan]
    eccentricity: List[Optional[float]] = [np.nan]
    mean_motion: List[Optional[float]] = [np.nan]
    semi_major_axis: List[Optional[float]] = [np.nan]
    U: List[Optional[str]] = [""]
    reference: List[Optional[str]] = [""]
    number_observation: List[Optional[int]] = [None]
    number_opposition: List[Optional[int]] = [None]
    start_obs: List[Optional[int]] = [None]
    end_obs: List[Optional[int]] = [None]
    orbital_arc: List[Optional[float]] = [np.nan]
    rms: List[Optional[float]] = [np.nan]
    coarse_indic: List[Optional[str]] = [""]
    precise_indic: List[Optional[str]] = [""]
    orbit_computer: List[Optional[str]] = [""]
    orbit_type: List[Optional[str]] = [""]
    last_obs_date: List[Optional[str]] = [""]
    iddataset: List[Optional[int]] = [None]


class Cometpro(pydantic.BaseModel):
    """COMETRO database"""

    id_: List[Optional[int]] = pydantic.Field([None], alias="id")
    note: List[Optional[int]] = [None]
    updated: List[Optional[str]] = [""]
    name: List[Optional[str]] = [""]
    iau_name: List[Optional[str]] = [""]
    author: List[Optional[str]] = [""]
    epoch: List[Optional[float]] = ([np.nan],)
    force_relat: List[Optional[int]] = [None]
    nb_obs: List[Optional[int]] = [None]
    sigma: List[Optional[float]] = ([np.nan],)
    start_date: List[Optional[str]] = [""]
    end_date: List[Optional[str]] = [""]
    px: List[Optional[float]] = [np.nan]
    py: List[Optional[float]] = [np.nan]
    pz: List[Optional[float]] = [np.nan]
    vx: List[Optional[float]] = [np.nan]
    vy: List[Optional[float]] = [np.nan]
    vz: List[Optional[float]] = [np.nan]
    fngA1: List[Optional[float]] = [np.nan]
    fngA2: List[Optional[float]] = [np.nan]
    fngA3: List[Optional[float]] = [np.nan]
    tau: List[Optional[float]] = [np.nan]
    perihelion_distance: List[Optional[float]] = [np.nan]
    eccentricity: List[Optional[float]] = [np.nan]
    perihelion_argument: List[Optional[float]] = [np.nan]
    node_longitude: List[Optional[float]] = [np.nan]
    inclination: List[Optional[float]] = [np.nan]
    mag_H1: List[Optional[float]] = [np.nan]
    mag_R1: List[Optional[float]] = [np.nan]
    mag_D1: List[Optional[float]] = [np.nan]
    mag_H2: List[Optional[float]] = [np.nan]
    mag_R2: List[Optional[float]] = [np.nan]
    mag_D2: List[Optional[float]] = [np.nan]
    iddataset: List[Optional[int]] = [None]


class Exoplanets(pydantic.BaseModel):
    """Exoplanet database"""

    id_: List[Optional[int]] = pydantic.Field([None], alias="id")
    name: List[Optional[str]] = [""]
    ra_j2000: List[Optional[float]] = [np.nan]
    dec_j2000: List[Optional[float]] = [np.nan]
    star_name: List[Optional[str]] = [""]
    star_distance: List[Optional[float]] = [np.nan]
    star_spec_type: List[Optional[str]] = [""]
    iddataset: List[Optional[int]] = [None]


class Spacecrafts(pydantic.BaseModel):
    """Spacecraft database"""

    id_: List[Optional[int]] = pydantic.Field([None], alias="id")
    international_designator: List[Optional[str]] = [""]
    norad_number: List[Optional[int]] = [None]
    multiple_name_flag: List[Optional[str]] = [""]
    payload_flag: List[Optional[str]] = [""]
    operational_status_code: List[Optional[str]] = [""]
    norad_name: List[Optional[str]] = [""]
    source_ownership: List[Optional[str]] = [""]
    launch_date: List[Optional[str]] = [""]
    launch_site: List[Optional[str]] = [""]
    orbital_period: List[Optional[float]] = [np.nan]
    inclination: List[Optional[float]] = [np.nan]
    apogee_altitude: List[Optional[float]] = [np.nan]
    perigee_altitude: List[Optional[float]] = [np.nan]
    radar_cross_section: List[Optional[float]] = [np.nan]
    orbital_status_code: List[Optional[str]] = [""]
    operational_status: List[Optional[str]] = [""]
    orbital_status: List[Optional[str]] = [""]
    central_body: List[Optional[str]] = [""]
    orbit_type: List[Optional[str]] = [""]
    iddataset: List[Optional[int]] = [None]


class Binarymp(pydantic.BaseModel):
    """Orbital properties of multiple asteroidal systems"""

    id_: List[Optional[int]] = pydantic.Field([None], alias="id")
    system_type: List[Optional[str]] = [""]
    system_id: List[Optional[int]] = [None]
    system_name: List[Optional[str]] = [""]
    sol_id: List[Optional[str]] = [""]
    method: List[Optional[str]] = [""]
    f_omc: List[Optional[float]] = [np.nan]
    proba: List[Optional[float]] = [np.nan]
    name: List[Optional[str]] = [""]
    t0_orbit: List[Optional[float]] = [np.nan]
    period: List[Optional[float]] = [np.nan]
    err_period: List[Optional[float]] = [np.nan]
    a: List[Optional[float]] = [np.nan]
    err_a: List[Optional[float]] = [np.nan]
    e: List[Optional[float]] = [np.nan]
    err_e: List[Optional[float]] = [np.nan]
    i: List[Optional[float]] = [np.nan]
    err_i: List[Optional[float]] = [np.nan]
    omega: List[Optional[float]] = [np.nan]
    err_omega: List[Optional[float]] = [np.nan]
    omegap: List[Optional[float]] = [np.nan]
    err_omegap: List[Optional[float]] = [np.nan]
    tpp: List[Optional[float]] = [np.nan]
    err_tpp: List[Optional[float]] = [np.nan]
    am: List[Optional[float]] = [np.nan]
    err_am: List[Optional[float]] = [np.nan]
    n: List[Optional[float]] = [np.nan]
    err_n: List[Optional[float]] = [np.nan]
    a_over_d1: List[Optional[float]] = [np.nan]
    err_a_over_d1: List[Optional[float]] = [np.nan]
    d2_over_d1: List[Optional[float]] = [np.nan]
    err_d2_over_d1: List[Optional[float]] = [np.nan]
    alpha: List[Optional[float]] = [np.nan]
    err_alpha: List[Optional[float]] = [np.nan]
    delta: List[Optional[float]] = [np.nan]
    err_delta: List[Optional[float]] = [np.nan]
    lambda_: List[Optional[float]] = pydantic.Field([np.nan], alias="lambda")
    err_lambda: List[Optional[float]] = [np.nan]
    beta: List[Optional[float]] = [np.nan]
    err_beta: List[Optional[float]] = [np.nan]
    mass: List[Optional[float]] = [np.nan]
    err_mass: List[Optional[float]] = [np.nan]
    density: List[Optional[float]] = [np.nan]
    err_density: List[Optional[float]] = [np.nan]
    mean_radius: List[Optional[float]] = [np.nan]
    err_mean_radius: List[Optional[float]] = [np.nan]
    j2: List[Optional[float]] = [np.nan]
    err_j2: List[Optional[float]] = [np.nan]
    j4: List[Optional[float]] = [np.nan]
    err_j4: List[Optional[float]] = [np.nan]
    t0_spin: List[Optional[float]] = [np.nan]
    pn0: List[Optional[float]] = [np.nan]
    err_pn0: List[Optional[float]] = [np.nan]
    pn1: List[Optional[float]] = [np.nan]
    err_pn1: List[Optional[float]] = [np.nan]
    ap0: List[Optional[float]] = [np.nan]
    err_ap0: List[Optional[float]] = [np.nan]
    ap1: List[Optional[float]] = [np.nan]
    err_ap1: List[Optional[float]] = [np.nan]
    dp0: List[Optional[float]] = [np.nan]
    err_dp0: List[Optional[float]] = [np.nan]
    dp1: List[Optional[float]] = [np.nan]
    err_dp1: List[Optional[float]] = [np.nan]
    iddataset: List[Optional[int]] = [None]


class Diamalbedo(Collection):
    """Diameters and Albedos database from literature"""

    id_: List[Optional[int]] = pydantic.Field([None], alias="id")
    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    name: List[Optional[str]] = [""]
    diameter: List[Optional[float]] = [np.nan]
    err_diameter_up: List[Optional[float]] = [np.nan]
    err_diameter_down: List[Optional[float]] = [np.nan]
    albedo: List[Optional[float]] = [np.nan]
    err_albedo_up: List[Optional[float]] = [np.nan]
    err_albedo_down: List[Optional[float]] = [np.nan]
    beaming: List[Optional[float]] = [np.nan]
    err_beaming: List[Optional[float]] = [np.nan]
    emissivity: List[Optional[float]] = [np.nan]
    err_emissivity: List[Optional[float]] = [np.nan]
    selection: List[Optional[int]] = [None]
    method: List[Optional[str]] = [""]
    bibcode: List[Optional[str]] = [""]

    preferred_albedo: List[bool] = [False]
    preferred_diameter: List[bool] = [False]
    preferred: List[bool] = [False]

    @pydantic.field_validator("preferred_albedo", mode="after")
    def select_preferred_albedo(cls, _, values):
        return get_preferred(
            values.data["name"][0], "parameters.physical.albedo", values.data["id_"]
        )

    @pydantic.field_validator("preferred_diameter", mode="after")
    def select_preferred_diameter(cls, _, values):
        return get_preferred(
            values.data["name"][0], "parameters.physical.diameter", values.data["id_"]
        )

    @pydantic.field_validator("preferred", mode="after")
    def preferred_albedo_or_diameter(cls, _, values):
        return [
            True if pref_alb or pref_diam else False
            for pref_alb, pref_diam in zip(
                values.data["preferred_albedo"], values.data["preferred_diameter"]
            )
        ]


class Masses(Collection):
    """Mass database from literature"""

    id_: List[Optional[int]] = pydantic.Field([None], alias="id")
    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    name: List[Optional[str]] = [""]
    mass: List[Optional[float]] = [np.nan]
    err_mass_up: List[Optional[float]] = [np.nan]
    err_mass_down: List[Optional[float]] = [np.nan]
    method: List[Optional[str]] = [""]
    selection: List[Optional[int]] = [None]
    iddataset: List[Optional[int]] = [None]

    preferred: List[bool] = [False]

    @pydantic.field_validator("preferred", mode="after")
    def select_preferred(cls, _, values):
        return get_preferred(
            values.data["name"][0], "parameters.physical.mass", values.data["id_"]
        )


class Taxonomies(Collection):
    """Taxonomy database from literature"""

    id_: List[Optional[int]] = pydantic.Field([None], alias="id")
    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    name: List[Optional[str]] = [""]
    year: List[Optional[int]] = [None]
    scheme: List[Optional[str]] = [""]
    class_: List[Optional[str]] = pydantic.Field([""], alias="class")
    complex: List[Optional[str]] = [""]
    selection: List[Optional[int]] = [None]
    method: List[Optional[str]] = [""]
    shortbib: List[Optional[str]] = [""]
    waverange: List[Optional[str]] = [""]

    preferred: List[bool] = [False]

    @pydantic.field_validator("preferred", mode="before")
    def select_preferred(cls, _, values):
        return get_preferred(
            values.data["name"][0], "parameters.physical.taxonomy", values.data["id_"]
        )


class Proper_elements(Collection):
    """Proper Elements from literature"""

    id_: List[Optional[int]] = pydantic.Field([None], alias="id")
    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    name: List[Optional[str]] = [""]
    H: List[Optional[float]] = [np.nan]
    proper_semi_major_axis: List[Optional[float]] = [np.nan]
    err_proper_semi_major_axis: List[Optional[float]] = [np.nan]
    proper_eccentricity: List[Optional[float]] = [np.nan]
    err_proper_eccentricity: List[Optional[float]] = [np.nan]
    proper_sine_inclination: List[Optional[float]] = [np.nan]
    err_proper_sine_inclination: List[Optional[float]] = [np.nan]
    proper_inclination: List[Optional[float]] = [np.nan]
    err_proper_inclination: List[Optional[float]] = [np.nan]
    proper_frequency_mean_motion: List[Optional[float]] = [np.nan]
    err_proper_frequency_mean_motion: List[Optional[float]] = [np.nan]
    proper_frequency_perihelion_longitude: List[Optional[float]] = [np.nan]
    err_proper_frequency_perihelion_longitude: List[Optional[float]] = [np.nan]
    proper_frequency_nodal_longitude: List[Optional[float]] = [np.nan]
    err_proper_frequency_nodal_longitude: List[Optional[float]] = [np.nan]
    lyapunov_time: List[Optional[float]] = [np.nan]
    integration_time: List[Optional[float]] = [np.nan]
    identfrom: List[Optional[str]] = [""]
    iddataset: List[Optional[int]] = [None]


class Phase_function(Collection):
    """Database of asteroid phase function"""

    id_: List[Optional[int]] = pydantic.Field([None], alias="id")
    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    name: List[Optional[str]] = [""]
    H: List[Optional[float]] = [np.nan]
    G1: List[Optional[float]] = [np.nan]
    G2: List[Optional[float]] = [np.nan]
    err_H_down: List[Optional[float]] = [np.nan]
    err_H_up: List[Optional[float]] = [np.nan]
    err_G1_down: List[Optional[float]] = [np.nan]
    err_G1_up: List[Optional[float]] = [np.nan]
    err_G2_down: List[Optional[float]] = [np.nan]
    err_G2_up: List[Optional[float]] = [np.nan]
    N: List[Optional[int]] = [None]
    phase_min: List[Optional[float]] = [np.nan]
    phase_max: List[Optional[float]] = [np.nan]
    rms: List[Optional[float]] = [np.nan]
    facility: List[Optional[str]] = [""]
    name_filter: List[Optional[str]] = [""]
    id_filter: List[Optional[str]] = [""]
    selection: List[Optional[int]] = [None]
    iddataset: List[Optional[int]] = [None]


class Families(Collection):
    """Database of Sso families"""

    id_: List[Optional[int]] = pydantic.Field([None], alias="id")
    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    name: List[Optional[str]] = [""]
    family_status: List[Optional[str]] = [""]
    family_number: List[Optional[int]] = pydantic.Field([None], alias="family_num")
    family_name: List[Optional[str]] = [""]
    membership: List[Optional[int]] = [None]
    selection: List[Optional[int]] = [None]
    method: List[Optional[str]] = [""]
    iddataset: List[Optional[int]] = [None]


class Pairs(Collection):
    """Database of Sso pairs"""

    id_: List[Optional[int]] = pydantic.Field([None], alias="id")
    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    name: List[Optional[str]] = [""]
    sibling_number: List[Optional[int]] = pydantic.Field([None], alias="sibling_num")
    sibling_name: List[Optional[str]] = [""]
    distance: List[Optional[float]] = [np.nan]
    age: List[Optional[float]] = [np.nan]
    err_age_up: List[Optional[float]] = [np.nan]
    err_age_down: List[Optional[float]] = [np.nan]
    selection: List[Optional[int]] = [None]
    method: List[Optional[str]] = [""]
    iddataset: List[Optional[int]] = [None]


class Spin(Collection):
    """Database of Sso spin coordiantes"""

    id_: List[Optional[int]] = pydantic.Field([None], alias="id")
    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    name: List[Optional[str]] = [""]
    model_dbid: List[Optional[str]] = [""]
    model_name: List[Optional[str]] = [""]
    model_id: List[Optional[int]] = [None]
    t0: List[Optional[float]] = [np.nan]
    W0: List[Optional[float]] = [np.nan]
    Wp: List[Optional[float]] = [np.nan]
    RA0: List[Optional[float]] = [np.nan]
    DEC0: List[Optional[float]] = [np.nan]
    err_RA0: List[Optional[float]] = [np.nan]
    err_DEC0: List[Optional[float]] = [np.nan]
    period: List[Optional[float]] = [np.nan]
    err_period: List[Optional[float]] = [np.nan]
    # NOTE: period_flag type should be str only, current datacloud issue
    period_flag: List[Optional[Union[str, int]]] = [""]
    period_type: List[Optional[str]] = [""]
    long_: List[Optional[float]] = pydantic.Field([np.nan], alias="long")
    lat: List[Optional[float]] = [np.nan]
    err_long: List[Optional[float]] = [np.nan]
    err_lat: List[Optional[float]] = [np.nan]
    selection: List[Optional[int]] = [None]
    method: List[Optional[str]] = [""]
    iddataset: List[Optional[str]] = [""]

    # pydantic does not like attributes with "model_" prefix
    model_config = pydantic.ConfigDict(protected_namespaces=())


class Yarkovsky(Collection):
    """Database of Sso Yarkovsky accelerations"""

    id_: List[Optional[int]] = pydantic.Field([None], alias="id")
    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    name: List[Optional[str]] = [""]
    A2: List[Optional[float]] = [np.nan]
    err_A2: List[Optional[float]] = [np.nan]
    dadt: List[Optional[float]] = [np.nan]
    err_dadt: List[Optional[float]] = [np.nan]
    snr: List[Optional[float]] = [np.nan]
    S: List[Optional[float]] = [np.nan]
    selection: List[Optional[int]] = [None]
    method: List[Optional[str]] = [""]
    iddataset: List[Optional[int]] = [None]


class Thermal_inertia(Collection):
    """Database of asteroid thermal properties"""

    id_: List[Optional[int]] = pydantic.Field([None], alias="id")
    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    name: List[Optional[str]] = [""]
    TI: List[Optional[float]] = [np.nan]
    err_TI_up: List[Optional[float]] = [np.nan]
    err_TI_down: List[Optional[float]] = [np.nan]
    dsun: List[Optional[float]] = [np.nan]
    selection: List[Optional[int]] = [None]
    method: List[Optional[str]] = [""]
    iddataset: List[Optional[int]] = [None]

    preferred: List[bool] = [False]

    @pydantic.field_validator("preferred", mode="after")
    def select_preferred(cls, _, values):
        return get_preferred(
            values.data["name"][0],
            "parameters.physical.thermal_inertia",
            values.data["id_"],
        )


class Colors(Collection):
    """Database of asteroid colors"""

    id_: List[Optional[int]] = pydantic.Field([None], alias="id")
    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    name: List[Optional[str]] = [""]
    color: List[Optional[str]] = [""]
    value: List[Optional[float]] = [np.nan]
    uncertainty: List[Optional[float]] = [np.nan]
    facility: List[Optional[str]] = [""]
    observer: List[Optional[str]] = [""]
    epoch: List[Optional[float]] = [""]
    delta_time: List[Optional[float]] = [""]
    color_type: List[Optional[str]] = [""]
    id_filter_1: List[Optional[str]] = [""]
    id_filter_2: List[Optional[str]] = [""]
    phot_sys: List[Optional[str]] = [""]
    selection: List[Optional[int]] = [None]
    iddataset: List[Optional[int]] = [None]

    @pydantic.model_validator(mode="before")
    def _convert_to_str(cls, values):
        if "observer" in values:
            values["observer"] = [str(o) for o in values["observer"]]

        return values


class Density(Collection):
    """Database of asteroid density"""

    id_: List[Optional[int]] = pydantic.Field([None], alias="id")
    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    name: List[Optional[str]] = [""]
    density: List[Optional[float]] = [np.nan]
    err_density_up: List[Optional[float]] = [np.nan]
    err_density_down: List[Optional[float]] = [np.nan]
    method: List[Optional[str]] = [""]
    selection: List[Optional[int]] = [None]
    iddataset: List[Optional[int]] = [None]


class Mpcatobs(Collection):
    """MPCAT-OBS database"""

    id_: List[Optional[int]] = pydantic.Field([None], alias="id")
    type: List[Optional[str]] = [""]
    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    packed_name: List[Optional[str]] = [""]
    name: List[Optional[str]] = [""]
    orb_type: List[Optional[str]] = [""]
    discovery: List[Optional[str]] = [""]
    note1: List[Optional[str]] = [""]
    note2: List[Optional[str]] = [""]
    date_obs: List[Optional[str]] = [""]
    jd_obs: List[Optional[float]] = [np.nan]
    ra_obs: List[Optional[float]] = [np.nan]
    dec_obs: List[Optional[float]] = [np.nan]
    mag: List[Optional[float]] = [np.nan]
    filter: List[Optional[str]] = [""]
    note3: List[Optional[str]] = [""]
    note4: List[Optional[str]] = [""]
    iau_code: List[Optional[str]] = [""]
    obs_long: List[Optional[float]] = [np.nan]
    obs_lat: List[Optional[float]] = [np.nan]
    obs_alt: List[Optional[float]] = [np.nan]
    vgs_x: List[Optional[float]] = [np.nan]
    vgs_y: List[Optional[float]] = [np.nan]
    vgs_z: List[Optional[float]] = [np.nan]
    iddataset: List[Optional[int]] = [None]


class Shape(Collection):
    """Database of Sso triaxial ellipsoid and shape models"""

    id_: List[Optional[int]] = pydantic.Field([None], alias="id")
    iddataset: List[Optional[int]] = [None]
    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    name: List[Optional[str]] = [""]
    model_dbid: List[Optional[str]] = [""]
    model_name: List[Optional[str]] = [""]
    model_id: List[Optional[str]] = [""]
    scaled: List[Optional[int]] = [None]
    radius_a: List[Optional[float]] = [np.nan]
    radius_b: List[Optional[float]] = [np.nan]
    radius_c: List[Optional[float]] = [np.nan]
    selected: List[Optional[int]] = [None]

    model_config = pydantic.ConfigDict(protected_namespaces=())


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
        * (sum(w * o**2 for w, o in zip(weights, observable)) / sum(weights) - avg**2)
    )
    std_avg = np.sqrt(var_avg / len(observable))
    return avg, std_avg
