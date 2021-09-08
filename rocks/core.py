#!/usr/bin/env python
"""Implement the Rock class and other core rocks functionality."""
import datetime as dt
import json
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


def ensure_unique_taxonomy(value):
    """If there are several taxonomic classifications in the ssoCard, pick the most recent one."""
    if isinstance(value, list):

        value = {
            "class": ", ".join(v["class"] for v in value),
            "waverange": ", ".join(v["waverange"] for v in value),
            "scheme": ", ".join(v["scheme"] for v in value),
            "method": value[0]["method"],
            "bibref": [v["bibref"] for v in value],
        }
    return value


# ------
# ssoCard as pydantic model

# The lowest level in the ssoCard tree is the Value
class Error(pydantic.BaseModel):
    min_: Optional[float] = pydantic.Field(np.nan, alias="min")
    max_: Optional[float] = pydantic.Field(np.nan, alias="max")


class Value(pydantic.BaseModel):
    error: Error = Error(**{})
    value: Optional[float] = np.nan

    def __str__(self):
        """Print the value of a numerical parameter including
        its errors and its unit if available.
        """

        unit = (
            rocks.utils.get_unit(self.path_unit) if hasattr(self, "path_unit") else ""
        )

        if abs(self.error.min_) == abs(self.error.max_):
            return f"{self.value} +- {self.error.max_} {unit}"
        else:
            return f"{self.value} +- ({self.error.max_}, {self.error.min_}) {unit}"


# The second lowest level is the Property
class Property(pydantic.BaseModel):
    def __str__(self):
        return json.dumps(json.loads(self.json()), indent=2, sort_keys=True)


# Other common branches are method and bibref
class Method(Property):
    doi: Optional[str] = ""
    name: Optional[str] = ""
    year: Optional[int] = np.nan
    title: Optional[str] = ""
    bibcode: Optional[str] = ""
    shortbib: Optional[str] = ""


class Bibref(Property):
    doi: Optional[str] = ""
    year: Optional[int] = np.nan
    title: Optional[str] = ""
    bibcode: Optional[str] = ""
    shortbib: Optional[str] = ""


# ------
# Dynamical parameters
class OrbitalElements(Property):
    ceu: Value = Value(**{})
    author: Optional[str] = ""
    bibref: List[Bibref] = [Bibref(**{})]
    ceu_rate: Value = Value(**{})
    ref_epoch: Optional[float] = np.nan
    inclination: Value = Value(**{})
    mean_motion: Value = Value(**{})
    orbital_arc: Optional[int] = np.nan
    eccentricity: Value = Value(**{})
    mean_anomaly: Value = Value(**{})
    node_longitude: Value = Value(**{})
    orbital_period: Value = Value(**{})
    semi_major_axis: Value = Value(**{})
    number_observation: Optional[int] = np.nan
    perihelion_argument: Value = Value(**{})

    _ensure_list: classmethod = pydantic.validator(
        "bibref", allow_reuse=True, pre=True
    )(ensure_list)


class ProperElements(Property):
    bibref: List[Bibref] = [Bibref(**{})]
    proper_g: Value = Value(**{})
    proper_s: Value = Value(**{})
    proper_eccentricity: Value = Value(**{})
    proper_inclination: Value = Value(**{})
    proper_semi_major_axis: Value = Value(**{})
    proper_sine_inclination: Value = Value(**{})

    _ensure_list: classmethod = pydantic.validator(
        "bibref", allow_reuse=True, pre=True
    )(ensure_list)

    def __str__(self):
        return self.json()


class Family(Property):
    bibref: List[Bibref] = [Bibref(**{})]
    family_name: Optional[str] = ""
    family_number: Optional[int] = np.nan
    family_status: Optional[str] = ""

    _ensure_list: classmethod = pydantic.validator(
        "bibref", allow_reuse=True, pre=True
    )(ensure_list)

    def __str__(self):
        return self.json()


class PairMembers(Property):
    sibling_name: Optional[str] = ""
    pair_delta_v: Optional[float] = np.nan
    pair_delta_a: Optional[float] = np.nan
    pair_delta_e: Optional[float] = np.nan
    pair_delta_i: Optional[float] = np.nan
    sibling_number: Optional[int] = np.nan


class Pair(Property):
    members: List[PairMembers] = [PairMembers(**{})]
    bibref: List[Bibref] = [Bibref(**{})]

    _ensure_list: classmethod = pydantic.validator(
        "members", "bibref", allow_reuse=True, pre=True
    )(ensure_list)

    def __str__(self):
        return self.json()


class Yarkovsky(Property):
    S: Optional[float] = np.nan
    A2: Value = Value(**{})
    snr: Optional[float] = np.nan
    dadt: Value = Value(**{})
    bibref: List[Bibref] = [Bibref(**{})]

    _ensure_list: classmethod = pydantic.validator(
        "bibref", allow_reuse=True, pre=True
    )(ensure_list)

    def __str__(self):
        print_A2 = print_parameter(self.A2, "unit.dynamical.yarkovsky.A2.value")
        print_dadt = print_parameter(self.dadt, "unit.dynamical.yarkovsky.dadt.value")
        return "\n".join([print_A2, print_dadt])


class DynamicalParameters(Property):
    pair: Pair = Pair(**{})
    family: Family = Family(**{})
    yarkovsky: Yarkovsky = Yarkovsky(**{})
    proper_elements: ProperElements = ProperElements(**{})
    orbital_elements: OrbitalElements = OrbitalElements(**{})

    def __str__(self):
        return self.json()


# ------
# Physical Value
class Albedo(Value):
    bibref: List[Bibref] = []
    method: List[Method] = []

    _ensure_list: classmethod = pydantic.validator(
        "bibref", "method", allow_reuse=True, pre=True
    )(ensure_list)


class Color(Value):
    color: Value = Value(**{})
    epoch: Optional[float] = np.nan
    from_: Optional[str] = pydantic.Field("", alias="from")
    bibref: Bibref = Bibref(**{})
    observer: Optional[str] = ""
    phot_sys: Optional[str] = ""
    delta_time: Optional[float] = np.nan
    id_filter_1: Optional[str] = ""
    id_filter_2: Optional[str] = ""


class Colors(Property):
    # Atlas
    c_o: List[Color] = [pydantic.Field(Color(**{}), alias="c-o")]
    # 2MASS / VISTA
    J_H: List[Color] = [pydantic.Field(Color(**{}), alias="J-H")]
    J_K: List[Color] = [pydantic.Field(Color(**{}), alias="J-K")]
    H_K: List[Color] = [pydantic.Field(Color(**{}), alias="H-K")]

    _ensure_list: classmethod = pydantic.validator("*", allow_reuse=True, pre=True)(
        ensure_list
    )


class Diameter(Value):
    method: List[Method] = []
    bibref: List[Bibref] = []

    path_unit: str = "unit.physical.diameter.diameter"

    _ensure_list: classmethod = pydantic.validator(
        "bibref", "method", allow_reuse=True, pre=True
    )(ensure_list)


class Mass(Value):
    bibref: List[Bibref] = [Bibref(**{})]
    method: List[Method] = [Method(**{})]

    path_unit: str = "unit.physical.mass.mass"

    _ensure_list: classmethod = pydantic.validator(
        "bibref", "method", allow_reuse=True, pre=True
    )(ensure_list)


class Phase(Property):
    H: Value = Value(**{})
    N: Optional[float] = np.nan
    G1: Value = Value(**{})
    G2: Value = Value(**{})
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


class PhaseFunction(Property):
    # Generic
    generic_johnson_v: Phase = pydantic.Field(Phase(**{}), alias="Generic/Johnson.V")
    # ATLAS
    misc_atlas_cyan: Phase = pydantic.Field(Phase(**{}), alias="Misc/Atlas.cyan")
    misc_atlas_orange: Phase = pydantic.Field(Phase(**{}), alias="Misc/Atlas.orange")


class Spin(Property):
    period: Value = Value(**{})
    t0: Optional[float] = np.nan
    Wp: Optional[float] = np.nan
    lat: Value = Value(**{})
    RA0: Optional[float] = np.nan
    DEC0: Optional[float] = np.nan
    long_: Value(**{}) = pydantic.Field(Value(**{}), alias="long")
    method: Optional[List[Method]] = [Method(**{})]
    bibref: Optional[List[Bibref]] = [Bibref(**{})]

    def __str__(self):
        return self.json()

    _ensure_list: classmethod = pydantic.validator(
        "bibref", "method", allow_reuse=True, pre=True
    )(ensure_list)


class Taxonomy(Property):
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


class ThermalInertia(Property):
    TI: Value = Value(**{})
    dsun: Optional[float] = np.nan
    bibref: List[Bibref] = []
    method: List[Method] = []

    _ensure_list: classmethod = pydantic.validator(
        "bibref", "method", allow_reuse=True, pre=True
    )(ensure_list)


class PhysicalParameters(Property):
    mass: Mass = Mass(**{})
    spin: List[Spin] = [Spin(**{})]
    colors: Colors = Colors(**{})
    albedo: Albedo = Albedo(**{})
    diameter: Diameter = Diameter(**{})
    taxonomy: Taxonomy = Taxonomy(**{})
    phase_function: PhaseFunction = PhaseFunction(**{})
    thermal_inertia: ThermalInertia = ThermalInertia(**{})

    def __str__(self):
        return self.json()

    _ensure_list: classmethod = pydantic.validator("spin", allow_reuse=True, pre=True)(
        ensure_list
    )

    _ensure_unique_taxonomy: classmethod = pydantic.validator(
        "taxonomy", allow_reuse=True, pre=True
    )(ensure_unique_taxonomy)


# ------
# Equation of state
class EqStateVector(Property):
    ref_epoch: Optional[float] = np.nan
    position: List[float] = [np.nan, np.nan, np.nan]
    velocity: List[float] = [np.nan, np.nan, np.nan]


# ------
# Highest level branches
class Parameters(Property):
    physical: PhysicalParameters = PhysicalParameters(**{})
    dynamical: DynamicalParameters = DynamicalParameters(**{})
    eq_state_vector: EqStateVector = EqStateVector(**{})

    def __str__(self):
        return self.json()

    class Config:
        arbitrary_types_allowed = True


class Link(Property):
    unit: Optional[str] = ""
    self_: Optional[str] = pydantic.Field("", alias="self")
    quaero: Optional[str] = ""
    description: Optional[str] = ""


class Ssocard(Property):
    version: Optional[str] = ""
    datetime: Optional[dt.datetime] = None


class Datacloud(Property):
    """The collection of links to datacloud catalogue associated to this ssoCard."""

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


class Rock(pydantic.BaseModel):
    """Instantiate a specific asteroid with data from its ssoCard."""

    # the basics
    id_: Optional[str] = pydantic.Field("", alias="id")
    name: Optional[str] = ""
    type_: Optional[str] = pydantic.Field("", alias="type")
    class_: Optional[str] = pydantic.Field("", alias="class")
    number: Optional[int] = np.nan
    parent: Optional[str] = ""
    system: Optional[str] = ""

    # the heart
    parameters: Parameters = Parameters(**{})

    # the meta
    link: Link = Link(**{})
    ssocard: Ssocard = Ssocard(**{})
    datacloud: Datacloud = Datacloud(**{})

    # the catalogues
    taxonomies: rocks.datacloud.Taxonomies = rocks.datacloud.Taxonomies(**{})
    aams: rocks.datacloud.AAMS = rocks.datacloud.AAMS(**{})
    astdys: rocks.datacloud.AstDyS = rocks.datacloud.AstDyS(**{})
    astorb: rocks.datacloud.Astorb = rocks.datacloud.Astorb(**{})
    diamalbedo: rocks.datacloud.Diamalbedo = rocks.datacloud.Diamalbedo(**{})
    masses: rocks.datacloud.Masses = rocks.datacloud.Masses(**{})
    mpcatobs: rocks.datacloud.Mpcatobs = rocks.datacloud.Mpcatobs(**{})
    pairs: rocks.datacloud.Pairs = rocks.datacloud.Pairs(**{})
    taxonomies: rocks.datacloud.Taxonomies = rocks.datacloud.Taxonomies(**{})

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

            if ssocard is None:
                # Asteroid does not have an ssoCard. Instantiate minimal ssoCard for meaningful error output.
                ssocard = {"name": id_provided}
                print(f"Did not find ssoCard for asteroid '{id_provided}'.")

            else:
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

        # These are shortcuts
        if name in self.__aliases["physical"].values():
            return getattr(self.parameters.physical, name)

        if name in self.__aliases["dynamical"].values():
            return getattr(self.parameters.dynamical, name)

        # These are proper aliases
        if name in self.__aliases["orbital_elements"].keys():
            return getattr(
                self.parameters.dynamical.orbital_elements,
                self.__aliases["orbital_elements"][name],
            )

        if name in self.__aliases["proper_elements"].keys():
            return getattr(
                self.parameters.dynamical.proper_elements,
                self.__aliases["proper_elements"][name],
            )

        if name in self.__aliases["diamalbedo"]:
            return getattr(self, "diamalbedo")

        raise AttributeError(
            f"'Rock' object has no attribute '{name}'. Run "
            f"'rocks properties' to get a list of accepted properties."
        )

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

        if catalogue not in rocks.datacloud.CATALOGUES.keys():
            raise ValueError(
                f"Unknown datacloud catalogue name: '{catalogue}'"
                f"\nChoose from {rocks.datacloud.CATALOGUES.keys()}"
            )

        # get the SsODNet catalogue and the Rock's attribute names
        catalogue_attribute = rocks.datacloud.CATALOGUES[catalogue]["attr_name"]
        catalogue_ssodnet = rocks.datacloud.CATALOGUES[catalogue]["ssodnet_name"]

        # retrieve the catalogue
        cat = rocks.ssodnet.get_datacloud_catalogue(id_, catalogue_ssodnet)

        if cat is None:
            return data

        # turn list of dict (catalogue entries) into dict of list
        cat = {
            key: [c[key] for c in cat]
            if catalogue not in ["aams", "astdys", "astorb", "pairs", "families"]
            else cat[0][key]
            for key in cat[0].keys()
        }

        # add 'preferred' attribute where applicable
        if catalogue in ["taxonomies", "masses"]:
            cat["preferred"] = [False] * len(list(cat.values())[0])
        elif catalogue_ssodnet in ["diamalbedo"]:
            cat["preferred_albedo"] = [False] * len(list(cat.values())[0])
            cat["preferred_diameter"] = [False] * len(list(cat.values())[0])

        # add catalogue to Rock
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
        "orbital_elements": {
            "a": "semi_major_axis",
            "e": "eccentricity",
            "i": "inclination",
        },
        "proper_elements": {
            "ap": "proper_semi_major_axis",
            "ep": "proper_eccentricity",
            "ip": "proper_inclination",
        },
        "diamalbedo": ["albedos", "diameters"],
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

    if len(identifier) == 1:
        ids = [rocks.identify(identifier, return_id=True, progress=progress)[-1]]

    else:
        ids = [
            id_
            for _, _, id_ in rocks.identify(
                identifier, return_id=True, progress=progress
            )
        ]

    rocks_ = [
        Rock(id_, skip_id_check=True, datacloud=datacloud)
        for id_ in tqdm(
            ids, desc="Building rocks : ", total=len(ids), disable=not progress
        )
    ]

    return rocks_
