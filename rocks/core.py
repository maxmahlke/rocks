#!/usr/bin/env python
"""Implement the Rock class and other core rocks functionality.
"""
from typing import List, Optional

import numpy as np
import pandas as pd
import pydantic
import rich
from tqdm import tqdm

import rocks


# ------
# Validators
def ensure_list(value):
    """Ensure that parameters are always a list.
    Some parameters are a dict if it's a single reference and a list otherwise.

    Further replaces all None values by empty dictionaries.
    """
    if isinstance(value, dict):
        value = [value]

    for i, v in enumerate(value):
        if v is None:
            value[i] = {}
    return value


# ------
# ssoCard as pydantic model
class MinMax(pydantic.BaseModel):
    min_: Optional[float] = pydantic.Field(np.nan, alias="min")
    max_: Optional[float] = pydantic.Field(np.nan, alias="max")


class Method(pydantic.BaseModel):
    doi: Optional[str] = ""
    name: Optional[str] = ""
    year: Optional[int] = None
    title: Optional[str] = ""
    bibcode: Optional[str] = ""
    shortbib: Optional[str] = ""


class Bibref(pydantic.BaseModel):
    doi: Optional[str] = ""
    year: Optional[int] = None
    title: Optional[str] = ""
    bibcode: Optional[str] = ""
    shortbib: Optional[str] = ""


class OrbitalElements(pydantic.BaseModel):
    ceu: Optional[float] = np.nan
    author: Optional[str] = ""
    bibref: List[Bibref] = [Bibref(**{})]
    err_ceu: MinMax = MinMax(**{})
    ceu_rate: Optional[float] = np.nan
    ref_epoch: Optional[float] = np.nan
    inclination: Optional[float] = np.nan
    mean_motion: Optional[float] = np.nan
    orbital_arc: Optional[int] = None
    eccentricity: Optional[float] = np.nan
    err_ceu_rate: MinMax = MinMax(**{})
    mean_anomaly: Optional[float] = np.nan
    node_longitude: Optional[float] = np.nan
    orbital_period: Optional[float] = np.nan
    semi_major_axis: Optional[float] = np.nan
    err_inclination: MinMax = MinMax(**{})
    err_mean_motion: MinMax = MinMax(**{})
    err_eccentricity: MinMax = MinMax(**{})
    err_mean_anomaly: MinMax = MinMax(**{})
    err_node_longitude: MinMax = MinMax(**{})
    err_orbital_period: MinMax = MinMax(**{})
    err_semi_major_axis: MinMax = MinMax(**{})
    perihelion_argument: Optional[float] = np.nan
    err_perihelion_argument: MinMax = MinMax(**{})

    _ensure_list: classmethod = pydantic.validator(
        "bibref", allow_reuse=True, pre=True
    )(ensure_list)

    def __str__(self):
        return self.json()


class ProperElements(pydantic.BaseModel):
    bibref: List[Bibref] = [Bibref(**{})]
    proper_g: Optional[float] = np.nan
    proper_s: Optional[float] = np.nan
    err_proper_g: MinMax = MinMax(**{})
    err_proper_s: MinMax = MinMax(**{})
    proper_eccentricity: Optional[float] = np.nan
    proper_inclination: Optional[float] = np.nan
    err_proper_inclination: MinMax = MinMax(**{})
    proper_semi_major_axis: Optional[float] = np.nan
    err_proper_eccentricity: MinMax = MinMax(**{})
    proper_sine_inclination: Optional[float] = np.nan
    err_proper_semi_major_axis: MinMax = MinMax(**{})

    _ensure_list: classmethod = pydantic.validator(
        "bibref", allow_reuse=True, pre=True
    )(ensure_list)

    def __str__(self):
        return self.json()


class Family(pydantic.BaseModel):
    bibref: List[Bibref] = [Bibref(**{})]
    family_name: Optional[str] = ""
    family_number: Optional[int] = None
    family_status: Optional[str] = ""
    family_membership: Optional[int] = None

    _ensure_list: classmethod = pydantic.validator(
        "bibref", allow_reuse=True, pre=True
    )(ensure_list)

    def __str__(self):
        return self.json()


class Yarkovsky(pydantic.BaseModel):
    S: Optional[float] = np.nan
    A2: Optional[float] = np.nan
    snr: Optional[float] = np.nan
    dadt: Optional[float] = np.nan
    bibref: List[Bibref] = [Bibref(**{})]
    err_A2: MinMax = MinMax(**{})
    err_dadt: MinMax = MinMax(**{})

    _ensure_list: classmethod = pydantic.validator(
        "bibref", allow_reuse=True, pre=True
    )(ensure_list)

    def __str__(self):
        return self.json()


class PairMembers(pydantic.BaseModel):
    sibling_name: Optional[str] = ""
    pair_delta_v: Optional[float] = np.nan
    pair_delta_a: Optional[float] = np.nan
    pair_delta_e: Optional[float] = np.nan
    pair_delta_i: Optional[float] = np.nan
    sibling_number: Optional[int] = None


class Pair(pydantic.BaseModel):
    pair_members: List[PairMembers] = [PairMembers(**{})]
    pair_membership: Optional[int] = None

    _ensure_list: classmethod = pydantic.validator(
        "pair_members", allow_reuse=True, pre=True
    )(ensure_list)

    def __str__(self):
        return self.json()


class DynamicalParameters(pydantic.BaseModel):

    pair: Pair = Pair(**{})
    family: Family = Family(**{})
    yarkovsky: Yarkovsky = Yarkovsky(**{})
    proper_elements: ProperElements = ProperElements(**{})
    orbital_elements: OrbitalElements = OrbitalElements(**{})

    def __str__(self):
        return self.json()

    class Config:
        arbitrary_types_allowed = True


class Taxonomy(pydantic.BaseModel):
    class_: Optional[str] = pydantic.Field("", alias="class")
    scheme: Optional[str] = ""
    bibref: List[Bibref] = [Bibref(**{})]
    method: List[Method] = [Method(**{})]
    waverange: Optional[str] = ""

    _ensure_list: classmethod = pydantic.validator(
        "bibref", "method", allow_reuse=True, pre=True
    )(ensure_list)

    def __str__(self):
        return self.json()


class Phase(pydantic.BaseModel):
    """Superclass for all phase function measurements."""

    H: Optional[float] = np.nan
    N: Optional[float] = np.nan
    G1: Optional[float] = np.nan
    G2: Optional[float] = np.nan
    err_H: MinMax = MinMax(**{})
    phase: MinMax = MinMax(**{})
    bibref: List[Bibref] = [Bibref(**{})]
    err_G1: MinMax = MinMax(**{})
    err_G2: MinMax = MinMax(**{})
    name_filter: Optional[str] = ""

    _ensure_list: classmethod = pydantic.validator(
        "bibref", allow_reuse=True, pre=True
    )(ensure_list)

    def __str__(self):
        return self.json()


class PhaseFunction(pydantic.BaseModel):

    # ATLAS
    misc_atlas_cyan: Phase = pydantic.Field(Phase(**{}), alias="Misc/Atlas.cyan")
    misc_atlas_orange: Phase = pydantic.Field(Phase(**{}), alias="Misc/Atlas.orange")


class Spin(pydantic.BaseModel):
    period: Optional[float] = np.nan
    err_period: MinMax = MinMax(**{})
    t0: Optional[float] = np.nan
    RA0: Optional[float] = np.nan
    DEC0: Optional[float] = np.nan
    Wp: Optional[float] = np.nan
    long_: Optional[float] = pydantic.Field(np.nan, alias="long")
    lat: Optional[float] = np.nan
    method: Optional[List[Method]] = [Method(**{})]
    bibref: Optional[List[Bibref]] = [Bibref(**{})]

    def __str__(self):
        return self.json()

    _ensure_list: classmethod = pydantic.validator(
        "bibref", "method", allow_reuse=True, pre=True
    )(ensure_list)


class Diameter(pydantic.BaseModel):
    diameter: Optional[float] = np.nan
    err_diameter: MinMax = MinMax(**{})
    method: List[Method] = []
    bibref: List[Bibref] = []

    _ensure_list: classmethod = pydantic.validator(
        "bibref", "method", allow_reuse=True, pre=True
    )(ensure_list)


class Albedo(pydantic.BaseModel):
    albedo: Optional[float] = np.nan
    bibref: List[Bibref] = []
    method: List[Method] = []
    err_albedo: MinMax = MinMax(**{})

    _ensure_list: classmethod = pydantic.validator(
        "bibref", "method", allow_reuse=True, pre=True
    )(ensure_list)


class Mass(pydantic.BaseModel):
    mass: Optional[float] = np.nan
    bibref: List[Bibref] = [Bibref(**{})]
    method: List[Method] = [Method(**{})]
    err_mass: MinMax = MinMax(**{})

    _ensure_list: classmethod = pydantic.validator(
        "bibref", "method", allow_reuse=True, pre=True
    )(ensure_list)


class Color(pydantic.BaseModel):
    """Superclass for all colours."""

    color: Optional[float] = np.nan
    epoch: Optional[float] = np.nan
    from_: Optional[str] = pydantic.Field("", alias="from")
    bibref: Bibref = Bibref(**{})
    observer: Optional[str] = ""
    phot_sys: Optional[str] = ""
    err_color: MinMax = MinMax(**{})
    delta_time: Optional[float] = np.nan
    id_filter_1: Optional[str] = ""
    id_filter_2: Optional[str] = ""


class Colors(pydantic.BaseModel):

    # Atlas
    c_o: List[Color] = [pydantic.Field(Color(**{}), alias="c-o")]

    # 2MASS / VISTA
    J_H: List[Color] = [pydantic.Field(Color(**{}), alias="J-H")]
    J_K: List[Color] = [pydantic.Field(Color(**{}), alias="J-K")]
    H_K: List[Color] = [pydantic.Field(Color(**{}), alias="H-K")]

    # SDSS

    _ensure_list: classmethod = pydantic.validator("*", allow_reuse=True, pre=True)(
        ensure_list
    )


class ThermalProperties(pydantic.BaseModel):
    TI: Optional[float] = np.nan
    dsun: Optional[float] = np.nan
    bibref: List[Bibref] = []
    err_TI: MinMax = MinMax(**{})
    method: List[Method] = []

    _ensure_list: classmethod = pydantic.validator(
        "bibref", "method", allow_reuse=True, pre=True
    )(ensure_list)


class PhysicalParameters(pydantic.BaseModel):
    mass: Mass = Mass(**{})
    spin: List[Spin] = [Spin(**{})]
    phase_function: PhaseFunction = PhaseFunction(**{})
    colors: Colors = Colors(**{})
    albedo: Albedo = Albedo(**{})
    diameter: Diameter = Diameter(**{})
    taxonomy: List[Taxonomy] = [Taxonomy(**{})]
    thermal_properties: ThermalProperties = ThermalProperties(**{})

    def __str__(self):
        return self.json()

    _ensure_list: classmethod = pydantic.validator(
        "spin", "taxonomy", allow_reuse=True, pre=True
    )(ensure_list)

    class Config:
        arbitrary_types_allowed = True


class EqStateVector(pydantic.BaseModel):
    ref_epoch: Optional[float] = np.nan
    px: Optional[float] = np.nan
    py: Optional[float] = np.nan
    pz: Optional[float] = np.nan
    vx: Optional[float] = np.nan
    vy: Optional[float] = np.nan
    vz: Optional[float] = np.nan

    def __str__(self):
        return self.json()


class Parameters(pydantic.BaseModel):

    dynamical: DynamicalParameters = DynamicalParameters(**{})
    physical: PhysicalParameters = PhysicalParameters(**{})
    eq_state_vector: EqStateVector = EqStateVector(**{})

    def __str__(self):
        return self.json()

    class Config:
        arbitrary_types_allowed = True


class Datacloud(pydantic.BaseModel):
    aams: Optional[str] = ""
    astdys: Optional[str] = ""
    astorb: Optional[str] = ""
    binarymp_tab: Optional[str] = ""
    binarymp_ref: Optional[str] = ""
    diamalbedo: Optional[str] = ""
    families: Optional[str] = ""
    masses: Optional[str] = ""
    mpcatobs: Optional[str] = ""
    mpcorb: Optional[str] = ""
    pairs: Optional[str] = ""
    taxonomy: Optional[str] = ""

    def __str__(self):
        return self.json()


class Pairs(pydantic.BaseModel):
    id_: Optional[int] = pydantic.Field(None, alias="id")
    number: Optional[int] = pydantic.Field(None, alias="num")
    name: Optional[str] = ""
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


class AAMS(pydantic.BaseModel):
    id_: Optional[int] = pydantic.Field(None, alias="id")
    number: Optional[int] = pydantic.Field(None, alias="num")
    name: Optional[str] = ""

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


class Astorb(pydantic.BaseModel):
    id_: Optional[int] = pydantic.Field(None, alias="id")
    number: Optional[int] = pydantic.Field(None, alias="num")
    name: Optional[str] = ""
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


class AstDyS(pydantic.BaseModel):
    id_: Optional[int] = pydantic.Field(None, alias="id")
    number: Optional[int] = pydantic.Field(None, alias="num")
    name: Optional[str] = ""
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


class Taxonomies(pydantic.BaseModel):
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
    name: List[str] = [""]
    complex_: List[str] = pydantic.Field([""], alias="complex")
    class_: List[str] = pydantic.Field([""], alias="class")

    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    idcollection: List[Optional[int]] = [None]
    iddataset: List[Optional[int]] = [None]
    year: List[Optional[int]] = [None]
    id_: List[Optional[int]] = pydantic.Field([None], alias="id")

    preferred: List[bool] = [False]

    @pydantic.validator("preferred", pre=True)
    def select_preferred_taxonomy(cls, v, values):
        return rocks.properties.rank_properties("taxonomy", values)

    def __len__(self):
        return len(self.class_)

    def __str__(self):

        if len(self) == 1 and not self.class_[0]:
            return "No taxonomies on record."

        table = rich.table.Table(
            header_style="bold blue",
            # caption=f"({rock.number}) {rock.name}",
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


class Masses(pydantic.BaseModel):
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
    name: List[str] = [""]

    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    idcollection: List[Optional[int]] = [None]
    iddataset: List[Optional[int]] = [None]
    year: List[Optional[int]] = [None]
    id_: List[Optional[int]] = pydantic.Field([None], alias="id")
    mass: List[float] = [np.nan]
    err_mass: List[float] = [np.nan]

    preferred: List[bool] = [False]

    @pydantic.validator("preferred", pre=True)
    def select_preferred_mass(cls, v, values):
        return rocks.properties.rank_properties("mass", values)


class Mpcatobs(pydantic.BaseModel):
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
    id_: List[Optional[int]] = pydantic.Field([None], alias="id")
    type_: List[str] = pydantic.Field([""], alias="type")
    number: List[Optional[int]] = pydantic.Field([None], alias="num")
    name: List[str] = [""]


class Diamalbedo(pydantic.BaseModel):

    link: List[str] = [""]
    datasetname: List[str] = [""]
    resourcename: List[str] = [""]
    doi: List[str] = [""]
    bibcode: List[str] = [""]
    url: List[str] = [""]
    title: List[str] = [""]
    name: List[str] = [""]
    iddataset: List[Optional[int]] = [None]
    method: List[str] = [""]
    shortbib: List[str] = [""]
    year: List[Optional[int]] = [None]
    source: List[str] = [""]

    idcollection: List[Optional[int]] = [None]
    id_: List[Optional[int]] = pydantic.Field([None], alias="id")
    number: List[Optional[int]] = pydantic.Field([None], alias="num")
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
        return rocks.properties.rank_properties("albedo", values)

    @pydantic.validator("preferred_diameter", pre=True)
    def select_preferred_diameter(cls, v, values):
        return rocks.properties.rank_properties("diameter", values)


class Ssocard(pydantic.BaseModel):
    href: Optional[str] = ""
    version: Optional[str] = ""
    datetime: Optional[str] = ""


class Rock(pydantic.BaseModel):

    id_: Optional[str] = pydantic.Field("", alias="id")
    name: Optional[str] = ""
    type_: Optional[str] = pydantic.Field("", alias="type")
    class_: Optional[str] = pydantic.Field("", alias="class")
    number: Optional[int] = np.nan
    parent: Optional[str] = ""
    system: Optional[str] = ""
    aliases: List[str] = []
    quaero_link: Optional[str] = ""

    parameters: Parameters = Parameters(**{})
    datacloud: Datacloud = Datacloud(**{})
    ssocard: Ssocard = Ssocard(**{})

    aams: AAMS = AAMS(**{})
    astdys: AstDyS = AstDyS(**{})
    astorb: Astorb = Astorb(**{})
    diamalbedo: Diamalbedo = Diamalbedo(**{})
    masses: Masses = Masses(**{})
    mpcatobs: Mpcatobs = Mpcatobs(**{})
    pairs: Pairs = Pairs(**{})
    taxonomies: Taxonomies = Taxonomies(**{})

    def __init__(self, id_, ssocard={}, datacloud=[], skip_id_check=False):
        """Identify a minor body  and retrieve its properties from SsODNet.

        Parameters
        ==========
        id_ : str, int, float
            Identifying asteroid name, designation, or number
        ssocard : dict
            Optional argument providing a dictionary to use as ssoCard.
            Default is empty dictionary, triggering the query of an ssoCard.
        datacloud : list of str
            Optional list of additional catalogues to retrieve from datacloud.
            Default is no additional catalogues.
        skip_id_check : bool
            Optional argument to prevent resolution of ID before getting ssoCard.
            Default is False.

        Returns
        =======
        rocks.core.Rock
            An asteroid class instance, with its properties as attributes.

        Notes
        =====
        If the asteroid could not be identified or the data contains invalid
        types, the number is None and no further attributes but the name are set.

        Example
        =======
        >>> from rocks import Rock
        >>> ceres = Rock('ceres')
        >>> ceres.taxonomy.class_
        'C'
        >>> ceres.taxonomy.shortbib
        'DeMeo+2009'
        >>> ceres.diameter
        848.4
        >>> ceres.diameter.unit
        'km'
        """
        if isinstance(datacloud, str):
            datacloud = [datacloud]

        id_provided = id_

        if not skip_id_check:
            _, _, id_ = rocks.identify(id_)  # type: ignore

        # Get ssoCard and datcloud catalogues
        if not pd.isnull(id_):
            if not ssocard:
                ssocard = rocks.ssodnet.get_ssocard(id_)

            for catalogue in datacloud:
                ssocard = self.__add_datacloud_catalogue(id_, catalogue, ssocard)
        else:
            # Something failed. Instantiate minimal ssoCard for meaningful error outpu.
            ssocard = {"name": id_provided}

        # Deserialize the asteroid data
        try:
            super().__init__(**ssocard)  # type: ignore
        except pydantic.ValidationError as message:
            self.__parse_error_message(message, id_, ssocard)
            return super().__init__(**{"name": id_provided})

    def __getattr__(self, name):
        """Implement attribute shortcuts: omission of parameters.physical/dynamical.
        Gets called if getattribute fails."""

        if name in self.__aliases["physical"].values():
            return getattr(self.parameters.physical, name)

        if name in self.__aliases["dynamical"].values():
            return getattr(self.parameters.dynamical, name)

        raise AttributeError(f"'Rock' object has no attribute '{name}'")

    def __repr__(self):
        return (
            self.__class__.__qualname__
            + f"(number={self.number!r}, name={self.name!r})"
        )

    def __str__(self):
        return f"({self.number}) {self.name}"

    def __hash__(self):
        return hash(self.id_)

    def __add_datacloud_catalogue(self, id_, catalogue, data):
        """Retrieve datacloud catalogue for asteroid and deserialize."""
        catalogue_attribute = rocks.properties.DATACLOUD_META[catalogue]["attr_name"]

        cat = rocks.ssodnet.get_datacloud_catalogue(id_, catalogue)
        breakpoint()

        if cat is None:
            return data

        # turn list of dict (catalogue entries) into dict of list
        cat = {
            key: [c[key] for c in cat]
            if catalogue not in ["aams", "astdys", "astorb", "pairs", "families"]
            else cat[0][key]
            for key in cat[0].keys()
        }  # type: ignore

        if catalogue in ["taxonomy", "masses"]:
            cat["preferred"] = [False] * len(list(cat.values())[0])
        elif catalogue in ["diamalbedo"]:
            cat["preferred_albedo"] = [False] * len(list(cat.values())[0])
            cat["preferred_diameter"] = [False] * len(list(cat.values())[0])

        data[catalogue_attribute] = cat
        return data

    def __parse_error_message(self, message, id_, data):
        """Print informative error message if ssocard data is invalid."""
        print(f"{id_}:")

        # Look up offending value in ssoCard
        for error in message.errors():
            value = data
            for loc in error["loc"]:
                value = value[loc]

            rich.print(
                f"Error: {' -> '.join([str(e) for e in error['loc']])} is invalid: {error['msg']}\n"
                f"Passed value: {value}\n"
            )

    __aliases = {
        "dynamical": {
            "parameters.dynamical.orbital_elements": "orbital_elements",
            "parameters.dynamical.proper_elements": "proper_elements",
            "parameters.dynamical.yarkovsky": "yarkovsky",
            "parameters.dynamical.family": "family",
            "parameters.dynamical.pair": "pair",
        },
        "physical": {
            "parameters.physical.diameter": "diameter",
            "parameters.physical.albedo": "albedo",
            "parameters.physical.colors": "colors",
            "parameters.physical.mass": "mass",
            "parameters.physical.thermal_properties": "thermal_properties",
            "parameters.physical.spin": "spin",
            "parameters.physical.taxonomy": "taxonomy",
            "parameters.physical.phase": "phase",
        },
    }


def rocks_(identifier, datacloud=[], progress=False):
    """Create multiple Rock instances.

    Parameters
    ==========
    identifier : list of str, list of int, list of float, np.array, pd.Series
        An iterable containing minor body identifiers.
    datacloud : list of str
        List of additional catalogues to retrieve from datacloud.
        Default is no additional catalogues.
    progress : bool
        Show progress of instantiation. Default is False.

    Returns
    =======
    list of rocks.core.Rock
        A list of Rock instances
    """
    if isinstance(identifier, pd.Series):
        identifier = identifier.values

    ids = [id_ for _, _, id_ in rocks.identify(identifier, datacloud, progress)]  # type: ignore

    rocks_ = [
        Rock(id_, skip_id_check=True)
        for id_ in tqdm(
            ids, desc="Building rocks : ", total=len(ids), disable=~progress
        )
    ]

    return rocks_


# class propertyCollection(SimpleNamespace):
#     """For collections of data, e.g. taxonomy -> class, method, shortbib.

#     Collections ofOptional[float]properties have plotting and averaging methods.
#     """

#     #  def __repr__(self):
#     #  return self.__class__.__qualname__ + json.dumps(self.__dict__, indent=2)

#     #  def __str__(self):
#     #  return self.__class__.__qualname__ + json.dumps(self.__dict__, indent=2)

#     def __len__(self):

#         _value_sample = list(self.__dict__.values())[0]

#         if isinstance(_value_sample, list):
#             return len(_value_sample)
#         else:
#             return 1

#     def __iter__(self):
#         self._iter_index = -1
#         return self

#     def __next__(self):
#         self._iter_index += 1

#         if len(self) == 1 and self._iter_index == 0:
#             return self
#         elif self._iter_index < len(self):
#             return SimpleNamespace(
#                 **dict(
#                     (k, v[self._iter_index])
#                     for k, v in self.__dict__.items()
#                     if k != "_iter_index"
#                 )
#             )
#         raise StopIteration

#     def scatter(self, prop_name, **kwargs):
#         return rocks.plots.scatter(self, prop_name, **kwargs)

#     def hist(self, prop_name, **kwargs):
#         return rocks.plots.hist(self, prop_name, **kwargs)

#     def select_preferred(self, prop_name):
#         """Select the preferred values based on the observation methods.

#         Parameters
#         ==========
#         prop_name : str
#             The property to rank.

#         Returns
#         =======
#         list of bool
#             Entry "preferred" in propertyCollection, True if preferred, else False
#         """
#         if prop_name == "diamalbedo":
#             setattr(
#                 self,
#                 "preferred_albedo",
#                 rocks.properties.rank_properties("albedo", self),
#             )
#             setattr(
#                 self,
#                 "preferred_diameter",
#                 rocks.properties.rank_properties("diameter", self),
#             )
#             setattr(
#                 self,
#                 "preferred",
#                 [
#                     any([di, ai])
#                     for di, ai in zip(self.preferred_diameter, self.preferred_albedo)
#                 ],
#             )
#         else:
#             self.preferred = rocks.properties.rank_properties(prop_name, self)


# class listSameTypeParameter(list):
#     """For several measurements of a single parameters of any type
#     in datcloud catalogues.
#     """

#     def __init__(self, data):
#         """Construct list which allows for assigning attributes.

#         Parameters
#         ==========
#         data : iterable
#             The minor body data from datacloud.
#         """
#         self.datatype = self.__get_type(data)

#         if self.datatype is not None:
#             list.__init__(self, [self.datatype(d) for d in data])
#         else:
#             list.__init__(self, [None for d in data])


#     def weighted_average(self, errors=None, preferred=[]):
#         """Compute weighted average of float-type parameters.

#         Parameters
#         ==========
#         errors : list of floats, np.ndarraya of floats
#             Optional list of associated uncertainties. Default is unit
#             unceratinty.
#         preferred : list of bools
#             Compute average only from values where preferred is True.

#         Returns
#         ======
#         (float, float)
#         Weighted average and its uncertainty.
#         """
#         if self.datatype is not float:
#             raise TypeError("Property is not of type float.")

#         observable = np.array(self)

#         # Make uniform weights in case no errors are provided
#         if errors is None:
#             warnings.warn("No error provided, using uniform weights.")
#             errors = np.ones(len(self))
#         else:
#             # Remove measurements where the error is zero
#             errors = np.array(errors)

#         if preferred:
#             observable = observable[preferred]
#             errors = errors[preferred]

#         return rocks.utils.weighted_average(observable, errors)
