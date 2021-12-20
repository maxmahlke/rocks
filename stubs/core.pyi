"""
This type stub file was generated by pyright.
"""

import datetime as dt
import pydantic
import rocks
from typing import Dict, List, Optional, Union

"""Implement the Rock class and other core rocks functionality."""

def ensure_list(value):  # -> list[dict[Unknown, Unknown]]:
    """Ensure that parameters are always a list.
    Some parameters are a dict if it's a single reference and a list otherwise.

    Further replaces all None values by empty dictionaries.
    """
    ...

def merge_entries(value):  # -> dict[Unknown, Unknown]:
    """Turn list of dicts into dict of lists."""
    ...

class Error(pydantic.BaseModel):
    min_: Optional[float] = ...
    max_: Optional[float] = ...

class Value(pydantic.BaseModel):
    error: Error = ...
    value: Optional[float] = ...
    def __str__(self) -> str:
        """Print the value of a numerical parameter including
        its errors and its unit if available.
        """
        ...

class Parameter(pydantic.BaseModel):
    def __str__(self) -> str: ...

class Method(Parameter):
    doi: Optional[str] = ...
    name: Optional[str] = ...
    year: Optional[int] = ...
    title: Optional[str] = ...
    bibcode: Optional[str] = ...
    shortbib: Optional[str] = ...

class Bibref(Parameter):
    doi: Optional[str] = ...
    year: Optional[int] = ...
    title: Optional[str] = ...
    bibcode: Optional[str] = ...
    shortbib: Optional[str] = ...

class OrbitalElements(Parameter):
    ceu: Value = ...
    author: Optional[str] = ...
    bibref: List[Bibref] = ...
    ceu_rate: Value = ...
    ref_epoch: Optional[float] = ...
    inclination: Value = ...
    mean_motion: Value = ...
    orbital_arc: Optional[int] = ...
    eccentricity: Value = ...
    mean_anomaly: Value = ...
    node_longitude: Value = ...
    orbital_period: Value = ...
    semi_major_axis: Value = ...
    number_observation: Optional[int] = ...
    perihelion_argument: Value = ...

class ProperElements(Parameter):
    bibref: List[Bibref] = ...
    proper_g: Value = ...
    proper_s: Value = ...
    proper_eccentricity: Value = ...
    proper_inclination: Value = ...
    proper_semi_major_axis: Value = ...
    proper_sine_inclination: Value = ...

class Family(Parameter):
    bibref: List[Bibref] = ...
    family_name: Optional[str] = ...
    family_number: Optional[int] = ...
    family_status: Optional[str] = ...

class PairMembers(Parameter):
    sibling_name: Optional[str] = ...
    pair_delta_v: Optional[float] = ...
    pair_delta_a: Optional[float] = ...
    pair_delta_e: Optional[float] = ...
    pair_delta_i: Optional[float] = ...
    sibling_number: Optional[int] = ...

class Pair(Parameter):
    members: List[PairMembers] = ...
    bibref: List[Bibref] = ...

class Yarkovsky(Parameter):
    S: Optional[float] = ...
    A2: Value = ...
    snr: Optional[float] = ...
    dadt: Value = ...
    bibref: List[Bibref] = ...
    def __str__(self) -> str: ...

class DynamicalParameters(Parameter):
    pair: Pair = ...
    family: Family = ...
    yarkovsky: Yarkovsky = ...
    proper_elements: ProperElements = ...
    orbital_elements: OrbitalElements = ...
    def __str__(self) -> str: ...

class Albedo(Value):
    bibref: List[Bibref] = ...
    method: List[Method] = ...
    _ensure_list: classmethod = ...

class Color(Value):
    color: Value = ...
    epoch: Optional[float] = ...
    from_: Optional[str] = ...
    bibref: Bibref = ...
    observer: Optional[str] = ...
    phot_sys: Optional[str] = ...
    delta_time: Optional[float] = ...
    id_filter_1: Optional[str] = ...
    id_filter_2: Optional[str] = ...

class Colors(Parameter):
    c_o: List[Color] = ...
    J_H: List[Color] = ...
    J_K: List[Color] = ...
    H_K: List[Color] = ...

class Density(Value):
    method: List[Method] = ...
    bibref: List[Bibref] = ...
    path_unit: str = ...
    _ensure_list: classmethod = ...

class Diameter(Value):
    method: List[Method] = ...
    bibref: List[Bibref] = ...
    path_unit: str = ...

class Mass(Value):
    bibref: List[Bibref] = ...
    method: List[Method] = ...
    path_unit: str = ...

class Phase(Parameter):
    H: Value = ...
    N: Optional[float] = ...
    G1: Value = ...
    G2: Value = ...
    rms: Optional[float] = ...
    phase: Error = ...
    bibref: List[Bibref] = ...
    facility: Optional[str] = ...
    name_filter: Optional[str] = ...

class PhaseFunction(Parameter):
    generic_johnson_v: Phase = ...
    misc_atlas_cyan: Phase = ...
    misc_atlas_orange: Phase = ...

class Spin(Parameter):
    period: List[Value] = ...
    t0: List[float] = ...
    Wp: List[float] = ...
    lat: List[Value] = ...
    RA0: List[float] = ...
    DEC0: List[float] = ...
    long_: List[Value] = ...
    method: List[List[Method]] = ...
    bibref: List[List[Bibref]] = ...
    path_unit: str = ...

class Taxonomy(Parameter):
    class_: List[str] = ...
    scheme: List[str] = ...
    bibref: List[List[Bibref]] = ...
    method: List[List[Method]] = ...
    waverange: List[str] = ...
    def __str__(self) -> str: ...

class ThermalInertia(Parameter):
    TI: Value = ...
    dsun: Optional[float] = ...
    bibref: List[Bibref] = ...
    method: List[Method] = ...

class AbsoluteMagnitude(Value):
    G: Optional[float] = ...
    bibref: List[Bibref] = ...

class PhysicalParameters(Parameter):
    mass: Mass = ...
    spin: Spin = ...
    colors: Colors = ...
    albedo: Albedo = ...
    density: Density = ...
    diameter: Diameter = ...
    taxonomy: Taxonomy = ...
    phase_function: PhaseFunction = ...
    thermal_inertia: ThermalInertia = ...
    absolute_magnitude: AbsoluteMagnitude = ...
    _ensure_list: classmethod = ...
    _merge_entries: classmethod = ...

class EqStateVector(Parameter):
    ref_epoch: Optional[float] = ...
    position: List[float] = ...
    velocity: List[float] = ...

class Parameters(Parameter):
    physical: PhysicalParameters = ...
    dynamical: DynamicalParameters = ...
    eq_state_vector: EqStateVector = ...
    class Config:
        arbitrary_types_allowed = ...

class Link(Parameter):
    unit: Optional[str] = ...
    self_: Optional[str] = ...
    quaero: Optional[str] = ...
    description: Optional[str] = ...

class Ssocard(Parameter):
    version: Optional[str] = ...
    datetime: Optional[dt.datetime] = ...

class Datacloud(Parameter):
    """The collection of links to datacloud catalogue associated to this ssoCard."""

    astdys: Optional[str] = ...
    astorb: Optional[str] = ...
    binarymp: Optional[str] = ...
    diamalbedo: Optional[str] = ...
    families: Optional[str] = ...
    masses: Optional[str] = ...
    mpcatobs: Optional[str] = ...
    mpcorb: Optional[str] = ...
    pairs: Optional[str] = ...
    taxonomy: Optional[str] = ...

class Rock(pydantic.BaseModel):
    """Instantiate a specific asteroid with data from its ssoCard."""

    id_: Optional[str] = ...
    name: Optional[str] = ...
    type_: Optional[str] = ...
    class_: Optional[str] = ...
    number: Optional[int] = ...
    parent: Optional[str] = ...
    system: Optional[str] = ...
    parameters: Parameters = ...
    link: Link = ...
    ssocard: Ssocard = ...
    datacloud: Datacloud = ...
    astdys: rocks.datacloud.AstDyS = ...
    astorb: rocks.datacloud.Astorb = ...
    binarymp: rocks.datacloud.Binarymp = ...
    colors: rocks.datacloud.Colors = ...
    diamalbedo: rocks.datacloud.Diamalbedo = ...
    families: rocks.datacloud.Families = ...
    masses: rocks.datacloud.Masses = ...
    mpcatobs: rocks.datacloud.Mpcatobs = ...
    mpcorb: rocks.datacloud.Mpcorb = ...
    pairs: rocks.datacloud.Pairs = ...
    phase_functions: rocks.datacloud.PhaseFunction = ...
    taxonomies: rocks.datacloud.Taxonomies = ...
    thermal_properties: rocks.datacloud.ThermalProperties = ...
    yarkovskies: rocks.datacloud.Yarkovskies = ...
    def __init__(
        self,
        id_: Union[str, float, int],
        ssocard: Dict = ...,
        datacloud: List = ...,
        skip_id_check: bool = ...,
    ) -> None:
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
        ...
    def __getattr__(self, name):  # -> Any:
        """Implement attribute shortcuts. Gets called if __getattribute__ fails."""
        ...
    def __repr__(self): ...
    def __str__(self) -> str: ...
    def __hash__(self) -> int: ...
    __aliases = ...

def rocks_(
    identifier: List, datacloud: List = ..., progress: bool = ...
) -> List[rocks.Rock]: ...