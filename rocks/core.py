#!/usr/bin/env python
"""Implement the Rock class and other core rocks functionality."""
import datetime as dt
from typing import List, Optional, Union

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
def print_parameter(param, path_unit):
    """Print the value of a numerical parameter including
    its errors and its unit.

    Parameters
    ==========
    param : rocks.core.Parameter
        The Parameter instance containing the values to print.
    path_unit : str
        Path to the parameter in the JSON tree, starting at unit and
        separating the levels with periods.
    """
    if path_unit is not None:
        unit = rocks.utils.get_unit(path_unit)
    else:
        unit = ""

    if param.error.min_ == -param.error.max_:
        return f"{param.value:.2f} +- {param.error.max_:.2f} {unit}"
    else:
        return f"{param.value:.2f} +- ({param.error.max_:.2f}, {-param.error.min_:.2f}) {unit}"


# ------
# ssoCard as pydantic model

# The lowest level in the ssoCard tree is the Parameter
class Error(pydantic.BaseModel):
    min_: Optional[float] = pydantic.Field(np.nan, alias="min")
    max_: Optional[float] = pydantic.Field(np.nan, alias="max")


class Parameter(pydantic.BaseModel):
    error: Error = Error(**{})
    value: Union[int, float, None] = np.nan


# Other common branches are method and bibref
class Method(pydantic.BaseModel):
    doi: Optional[str] = ""
    name: Optional[str] = ""
    year: Optional[int] = np.nan
    title: Optional[str] = ""
    bibcode: Optional[str] = ""
    shortbib: Optional[str] = ""


class Bibref(pydantic.BaseModel):
    doi: Optional[str] = ""
    year: Optional[int] = np.nan
    title: Optional[str] = ""
    bibcode: Optional[str] = ""
    shortbib: Optional[str] = ""


# ------
# Dynamical parameters
class OrbitalElements(pydantic.BaseModel):
    ceu: Parameter = Parameter(**{})
    author: Optional[str] = ""
    bibref: List[Bibref] = [Bibref(**{})]
    ceu_rate: Parameter = Parameter(**{})
    ref_epoch: Optional[float] = np.nan
    inclination: Parameter = Parameter(**{})
    mean_motion: Parameter = Parameter(**{})
    orbital_arc: Optional[int] = np.nan
    eccentricity: Parameter = Parameter(**{})
    mean_anomaly: Parameter = Parameter(**{})
    node_longitude: Parameter = Parameter(**{})
    orbital_period: Parameter = Parameter(**{})
    semi_major_axis: Parameter = Parameter(**{})
    number_observation: Optional[int] = np.nan
    perihelion_argument: Parameter = Parameter(**{})

    _ensure_list: classmethod = pydantic.validator(
        "bibref", allow_reuse=True, pre=True
    )(ensure_list)

    def __str__(self):
        return self.json()


class ProperElements(pydantic.BaseModel):
    bibref: List[Bibref] = [Bibref(**{})]
    proper_g: Parameter = Parameter(**{})
    proper_s: Parameter = Parameter(**{})
    proper_eccentricity: Parameter = Parameter(**{})
    proper_inclination: Parameter = Parameter(**{})
    proper_semi_major_axis: Parameter = Parameter(**{})
    proper_sine_inclination: Parameter = Parameter(**{})

    _ensure_list: classmethod = pydantic.validator(
        "bibref", allow_reuse=True, pre=True
    )(ensure_list)

    def __str__(self):
        return self.json()


class Family(pydantic.BaseModel):
    bibref: List[Bibref] = [Bibref(**{})]
    family_name: Optional[str] = ""
    family_number: Optional[int] = np.nan
    family_status: Optional[str] = ""

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
    sibling_number: Optional[int] = np.nan


class Pair(pydantic.BaseModel):
    members: List[PairMembers] = [PairMembers(**{})]
    bibref: List[Bibref] = [Bibref(**{})]

    _ensure_list: classmethod = pydantic.validator(
        "members", "bibref", allow_reuse=True, pre=True
    )(ensure_list)

    def __str__(self):
        return self.json()


class Yarkovsky(pydantic.BaseModel):
    S: Optional[float] = np.nan
    A2: Parameter = Parameter(**{})
    snr: Optional[float] = np.nan
    dadt: Parameter = Parameter(**{})
    bibref: List[Bibref] = [Bibref(**{})]

    _ensure_list: classmethod = pydantic.validator(
        "bibref", allow_reuse=True, pre=True
    )(ensure_list)

    def __str__(self):
        print_A2 = print_parameter(self.A2, "unit.dynamical.yarkovsky.A2.value")
        print_dadt = print_parameter(self.dadt, "unit.dynamical.yarkovsky.dadt.value")
        return "\n".join([print_A2, print_dadt])


class DynamicalParameters(pydantic.BaseModel):
    pair: Pair = Pair(**{})
    family: Family = Family(**{})
    yarkovsky: Yarkovsky = Yarkovsky(**{})
    proper_elements: ProperElements = ProperElements(**{})
    orbital_elements: OrbitalElements = OrbitalElements(**{})

    def __str__(self):
        return self.json()


# ------
# Physical Parameter
class Albedo(pydantic.BaseModel):
    albedo: Parameter = Parameter(**{})
    bibref: List[Bibref] = []
    method: List[Method] = []

    _ensure_list: classmethod = pydantic.validator(
        "bibref", "method", allow_reuse=True, pre=True
    )(ensure_list)

    def __str__(self):
        return print_parameter(self.albedo, path_unit=None)


class Color(pydantic.BaseModel):
    color: Parameter = Parameter(**{})
    epoch: Optional[float] = np.nan
    from_: Optional[str] = pydantic.Field("", alias="from")
    bibref: Bibref = Bibref(**{})
    observer: Optional[str] = ""
    phot_sys: Optional[str] = ""
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

    _ensure_list: classmethod = pydantic.validator("*", allow_reuse=True, pre=True)(
        ensure_list
    )


class Diameter(pydantic.BaseModel):
    diameter: Parameter = Parameter(**{})
    method: List[Method] = []
    bibref: List[Bibref] = []

    _ensure_list: classmethod = pydantic.validator(
        "bibref", "method", allow_reuse=True, pre=True
    )(ensure_list)

    def __str__(self):
        return print_parameter(self.diameter, "unit.physical.diameter.diameter.value")


class Mass(pydantic.BaseModel):
    mass: Parameter = Parameter(**{})
    bibref: List[Bibref] = [Bibref(**{})]
    method: List[Method] = [Method(**{})]

    _ensure_list: classmethod = pydantic.validator(
        "bibref", "method", allow_reuse=True, pre=True
    )(ensure_list)

    def __str__(self):
        return print_parameter(self.mass, "unit.physical.mass.mass.value")


class Phase(pydantic.BaseModel):
    H: Parameter = Parameter(**{})
    N: Optional[float] = np.nan
    G1: Parameter = Parameter(**{})
    G2: Parameter = Parameter(**{})
    rms: Optional[float] = np.nan
    phase: Error = Error(**{})
    bibref: List[Bibref] = [Bibref(**{})]
    facility: Optional[str] = ""
    name_filter: Optional[str] = ""

    _ensure_list: classmethod = pydantic.validator(
        "bibref", allow_reuse=True, pre=True
    )(ensure_list)

    def __str__(self):
        return self.json()


class PhaseFunction(pydantic.BaseModel):
    # Generic
    generic_johnson_v: Phase = pydantic.Field(Phase(**{}), alias="Generic/Johnson.V")
    # ATLAS
    misc_atlas_cyan: Phase = pydantic.Field(Phase(**{}), alias="Misc/Atlas.cyan")
    misc_atlas_orange: Phase = pydantic.Field(Phase(**{}), alias="Misc/Atlas.orange")


class Spin(pydantic.BaseModel):
    period: Parameter = Parameter(**{})
    t0: Optional[float] = np.nan
    Wp: Optional[float] = np.nan
    lat: Parameter = Parameter(**{})
    RA0: Optional[float] = np.nan
    DEC0: Optional[float] = np.nan
    long_: Parameter(**{}) = pydantic.Field(Parameter(**{}), alias="long")
    method: Optional[List[Method]] = [Method(**{})]
    bibref: Optional[List[Bibref]] = [Bibref(**{})]

    def __str__(self):
        return self.json()

    _ensure_list: classmethod = pydantic.validator(
        "bibref", "method", allow_reuse=True, pre=True
    )(ensure_list)


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
        if not self.class_:
            return "No taxonomy on record."
        return self.class_


class ThermalProperties(pydantic.BaseModel):
    TI: Parameter = Parameter(**{})
    dsun: Optional[float] = np.nan
    bibref: List[Bibref] = []
    method: List[Method] = []

    _ensure_list: classmethod = pydantic.validator(
        "bibref", "method", allow_reuse=True, pre=True
    )(ensure_list)


class PhysicalParameters(pydantic.BaseModel):
    mass: Mass = Mass(**{})
    spin: List[Spin] = [Spin(**{})]
    colors: Colors = Colors(**{})
    albedo: Albedo = Albedo(**{})
    diameter: Diameter = Diameter(**{})
    taxonomy: Taxonomy = Taxonomy(**{})
    phase_function: PhaseFunction = PhaseFunction(**{})
    thermal_properties: ThermalProperties = ThermalProperties(**{})

    def __str__(self):
        return self.json()

    _ensure_list: classmethod = pydantic.validator("spin", allow_reuse=True, pre=True)(
        ensure_list
    )


# ------
# Equation of state
class EqStateVector(pydantic.BaseModel):
    ref_epoch: Optional[float] = np.nan
    position: List[float] = [np.nan, np.nan, np.nan]
    velocity: List[float] = [np.nan, np.nan, np.nan]


# ------
# Highest level branches
class Parameters(pydantic.BaseModel):
    physical: PhysicalParameters = PhysicalParameters(**{})
    dynamical: DynamicalParameters = DynamicalParameters(**{})
    eq_state_vector: EqStateVector = EqStateVector(**{})

    def __str__(self):
        return self.json()

    class Config:
        arbitrary_types_allowed = True


class Link(pydantic.BaseModel):
    unit: Optional[str] = ""
    self_: Optional[str] = pydantic.Field("", alias="self")
    quaero: Optional[str] = ""
    description: Optional[str] = ""


class Ssocard(pydantic.BaseModel):
    version: Optional[str] = ""
    datetime: Optional[dt.datetime] = None


class Rock(pydantic.BaseModel):
    """Instantiate a specific asteroid with data from its ssoCard."""

    id_: Optional[str] = pydantic.Field("", alias="id")
    name: Optional[str] = ""
    type_: Optional[str] = pydantic.Field("", alias="type")
    class_: Optional[str] = pydantic.Field("", alias="class")
    number: Optional[int] = np.nan
    parent: Optional[str] = ""
    system: Optional[str] = ""

    link: Link = Link(**{})
    ssocard: Ssocard = Ssocard(**{})
    datacloud: rocks.datacloud.Datacloud = rocks.datacloud.Datacloud(**{})
    parameters: Parameters = Parameters(**{})

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
            _, _, id_ = rocks.identify(id_, return_id=True)  # type: ignore

        # Get ssoCard and datcloud catalogues
        if not pd.isnull(id_):
            if not ssocard:
                ssocard = rocks.ssodnet.get_ssocard(id_)

            for catalogue in datacloud:
                ssocard = self.__add_datacloud_catalogue(id_, catalogue, ssocard)
        else:
            # Something failed. Instantiate minimal ssoCard for meaningful error output.
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

        if catalogue not in rocks.properties.PROP_TO_DATACLOUD.keys():
            raise ValueError(
                f"Unknown datacloud catalogue name: '{catalogue}'"
                f"\nChoose from {rocks.properties.PROP_TO_DATACLOUD.keys()}"
            )

        catalogue = rocks.properties.PROP_TO_DATACLOUD[catalogue]

        catalogue_attribute = rocks.properties.DATACLOUD_META[catalogue]["attr_name"]
        cat = rocks.ssodnet.get_datacloud_catalogue(id_, catalogue)

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

            data["diameters"] = cat
            data["albedos"] = cat

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

    ids = [id_ for _, _, id_ in rocks.identify(identifier, return_id=True, progress=progress)]  # type: ignore

    rocks_ = [
        Rock(id_, skip_id_check=True, datacloud=datacloud)
        for id_ in tqdm(
            ids, desc="Building rocks : ", total=len(ids), disable=~progress
        )
    ]

    return rocks_
