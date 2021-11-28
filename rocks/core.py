#!/usr/bin/env python
"""Implement the Rock class and other core rocks functionality."""
import datetime as dt
import json
from typing import List, Optional
import warnings

import numpy as np
import pandas as pd
import pydantic
import rich

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


def merge_entries(value):
    """Turn list of dicts into dict of lists."""

    if isinstance(value, list):  # taxonomy
        pass
    elif isinstance(value, dict):  # spin
        value = list(value.values())

    return_dict = {}

    # Take keys of first dict
    for key in value[0]:

        # Turn all dicts in the list into lists
        return_dict[key] = []

        for v in value:
            if key in v:
                return_dict[key].append(v[key])
            else:
                # This entry of the current parameter does not have all
                # values (eg "period" for Spin)

                # Add the correct NaN value
                if isinstance(value[0][key], dict):
                    return_dict[key].append({})
                elif isinstance(value[0][key], (float, int)):
                    return_dict[key].append(np.nan)
                elif isinstance(value[0][key], str):
                    return_dict[key].append(None)
    return return_dict

    # return {key: [entry[key] for entry in value] for key in value[0]}


# ------
# ssoCard as pydantic model

# The lowest level in the ssoCard tree is the Value
class Error(pydantic.BaseModel):
    min_: float = pydantic.Field(np.nan, alias="min")
    max_: float = pydantic.Field(np.nan, alias="max")


class Value(pydantic.BaseModel):
    error: Error = Error(**{})
    value: Optional[float] = np.nan
    path_unit: str = ""

    def __str__(self):
        """Print the value of a numerical parameter including
        its errors and its unit if available.
        """

        unit = rocks.utils.get_unit(self.path_unit) if self.path_unit else ""

        if abs(self.error.min_) == abs(self.error.max_):
            return f"{self.value:.4} +- {self.error.max_:.4} {unit}"
        else:
            return f"{self.value:.4} +- ({self.error.max_:.4}, {self.error.min_:.4}) {unit}"


# The second lowest level is the Parameter
class Parameter(pydantic.BaseModel):
    def __str__(self):
        return json.dumps(json.loads(self.json()), indent=2, sort_keys=True)


# Other common branches are method and bibref
class Method(Parameter):
    doi: Optional[str] = ""
    name: Optional[str] = ""
    year: Optional[int] = None
    title: Optional[str] = ""
    bibcode: Optional[str] = ""
    shortbib: Optional[str] = ""


class Bibref(Parameter):
    doi: Optional[str] = ""
    year: Optional[int] = None
    title: Optional[str] = ""
    bibcode: Optional[str] = ""
    shortbib: Optional[str] = ""


# ------
# Dynamical parameters
class OrbitalElements(Parameter):
    ceu: Value = Value(**{})
    author: Optional[str] = ""
    bibref: List[Bibref] = [Bibref(**{})]
    ceu_rate: Value = Value(**{})
    ref_epoch: Optional[float] = np.nan
    inclination: Value = Value(**{})
    mean_motion: Value = Value(**{})
    orbital_arc: Optional[int] = None
    eccentricity: Value = Value(**{})
    mean_anomaly: Value = Value(**{})
    node_longitude: Value = Value(**{})
    orbital_period: Value = Value(**{})
    semi_major_axis: Value = Value(**{})
    number_observation: Optional[int] = None
    perihelion_argument: Value = Value(**{})


class ProperElements(Parameter):
    bibref: List[Bibref] = [Bibref(**{})]
    proper_g: Value = Value(**{})
    proper_s: Value = Value(**{})
    proper_eccentricity: Value = Value(**{})
    proper_inclination: Value = Value(**{})
    proper_semi_major_axis: Value = Value(**{})
    proper_sine_inclination: Value = Value(**{})


class Family(Parameter):
    bibref: List[Bibref] = [Bibref(**{})]
    family_name: Optional[str] = ""
    family_number: Optional[int] = None
    family_status: Optional[str] = ""


class PairMembers(Parameter):
    sibling_name: Optional[str] = ""
    pair_delta_v: Optional[float] = np.nan
    pair_delta_a: Optional[float] = np.nan
    pair_delta_e: Optional[float] = np.nan
    pair_delta_i: Optional[float] = np.nan
    sibling_number: Optional[int] = None


class Pair(Parameter):
    members: List[PairMembers] = [PairMembers(**{})]
    bibref: List[Bibref] = [Bibref(**{})]


class Yarkovsky(Parameter):
    S: Optional[float] = np.nan
    A2: Value = Value(**{})
    snr: Optional[float] = np.nan
    dadt: Value = Value(**{})
    bibref: List[Bibref] = [Bibref(**{})]

    def __str__(self):
        return "\n".join([self.A2.__str__(), self.dadt.__str__()])


class DynamicalParameters(Parameter):
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


class Colors(Parameter):
    # Atlas
    c_o: List[Color] = [pydantic.Field(Color(**{}), alias="c-o")]
    # 2MASS / VISTA
    J_H: List[Color] = [pydantic.Field(Color(**{}), alias="J-H")]
    J_K: List[Color] = [pydantic.Field(Color(**{}), alias="J-K")]
    H_K: List[Color] = [pydantic.Field(Color(**{}), alias="H-K")]


class Density(Value):
    method: List[Method] = []
    bibref: List[Bibref] = []

    path_unit: str = "unit.physical.density.value"

    _ensure_list: classmethod = pydantic.validator(
        "bibref", "method", allow_reuse=True, pre=True
    )(ensure_list)


class Diameter(Value):
    method: List[Method] = [Method(**{})]
    bibref: List[Bibref] = [Bibref(**{})]

    path_unit: str = "unit.physical.diameter.value"


class Mass(Value):
    bibref: List[Bibref] = [Bibref(**{})]
    method: List[Method] = [Method(**{})]

    path_unit: str = "unit.physical.mass.value"


class Phase(Parameter):
    H: Value = Value(**{})
    N: Optional[float] = np.nan
    G1: Value = Value(**{})
    G2: Value = Value(**{})
    rms: Optional[float] = np.nan
    phase: Error = Error(**{})
    bibref: List[Bibref] = [Bibref(**{})]
    facility: Optional[str] = ""
    name_filter: Optional[str] = ""


class PhaseFunction(Parameter):
    # Generic
    generic_johnson_v: Phase = pydantic.Field(Phase(**{}), alias="Generic/Johnson.V")
    # ATLAS
    misc_atlas_cyan: Phase = pydantic.Field(Phase(**{}), alias="Misc/Atlas.cyan")
    misc_atlas_orange: Phase = pydantic.Field(Phase(**{}), alias="Misc/Atlas.orange")


class Spin(Parameter):
    period: List[Value] = [Value(**{})]
    t0: List[float] = [np.nan]
    Wp: List[float] = [np.nan]
    lat: List[Value] = [Value(**{})]
    RA0: List[float] = [np.nan]
    DEC0: List[float] = [np.nan]
    long_: List[Value] = pydantic.Field([Value(**{})], alias="long")
    method: List[List[Method]] = [[Method(**{})]]
    bibref: List[List[Bibref]] = [[Bibref(**{})]]

    path_unit: str = "unit.physical.spin.value"


class Taxonomy(Parameter):
    class_: List[str] = pydantic.Field([""], alias="class")
    scheme: List[str] = [""]
    bibref: List[List[Bibref]] = [[Bibref(**{})]]
    method: List[List[Method]] = [[Method(**{})]]
    waverange: List[str] = [""]

    def __str__(self):
        if not self.class_:
            return "No taxonomy on record."
        return ", ".join(self.class_)


class ThermalInertia(Parameter):
    TI: Value = Value(**{})
    dsun: Optional[float] = np.nan
    bibref: List[Bibref] = []
    method: List[Method] = []


class AbsoluteMagnitude(Value):
    G: Optional[float] = np.nan
    bibref: List[Bibref] = []


class PhysicalParameters(Parameter):
    mass: Mass = Mass(**{})
    spin: Spin = Spin(**{})
    colors: Colors = Colors(**{})
    albedo: Albedo = Albedo(**{})
    density: Density = Density(**{})
    diameter: Diameter = Diameter(**{})
    taxonomy: Taxonomy = Taxonomy(**{})
    phase_function: PhaseFunction = PhaseFunction(**{})
    thermal_inertia: ThermalInertia = ThermalInertia(**{})
    absolute_magnitude: AbsoluteMagnitude = AbsoluteMagnitude(**{})

    _ensure_list: classmethod = pydantic.validator(
        "taxonomy", allow_reuse=True, pre=True
    )(ensure_list)

    _merge_entries: classmethod = pydantic.validator(
        "spin", "taxonomy", allow_reuse=True, pre=True
    )(merge_entries)


# ------
# Equation of state
class EqStateVector(Parameter):
    ref_epoch: Optional[float] = np.nan
    position: List[float] = [np.nan, np.nan, np.nan]
    velocity: List[float] = [np.nan, np.nan, np.nan]


# ------
# Highest level branches
class Parameters(Parameter):
    physical: PhysicalParameters = PhysicalParameters(**{})
    dynamical: DynamicalParameters = DynamicalParameters(**{})
    eq_state_vector: EqStateVector = EqStateVector(**{})

    class Config:
        arbitrary_types_allowed = True


class Link(Parameter):
    unit: Optional[str] = ""
    self_: Optional[str] = pydantic.Field("", alias="self")
    quaero: Optional[str] = ""
    description: Optional[str] = ""


class Ssocard(Parameter):
    version: Optional[str] = ""
    datetime: Optional[dt.datetime] = None


class Datacloud(Parameter):
    """The collection of links to datacloud catalogue associated to this ssoCard."""

    astorb: Optional[str] = ""
    binarymp: Optional[str] = ""
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
    number: Optional[int] = None
    parent: Optional[str] = ""
    system: Optional[str] = ""

    # the heart
    parameters: Parameters = Parameters(**{})

    # the meta
    link: Link = Link(**{})
    ssocard: Ssocard = Ssocard(**{})
    datacloud: Datacloud = Datacloud(**{})

    # the catalogues
    astorb: rocks.datacloud.Astorb = rocks.datacloud.Astorb(**{})
    binarymp: rocks.datacloud.Binarymp = rocks.datacloud.Binarymp(**{})
    colors: rocks.datacloud.Colors = rocks.datacloud.Colors(**{})
    diamalbedo: rocks.datacloud.Diamalbedo = rocks.datacloud.Diamalbedo(**{})
    families: rocks.datacloud.Families = rocks.datacloud.Families(**{})
    masses: rocks.datacloud.Masses = rocks.datacloud.Masses(**{})
    mpcatobs: rocks.datacloud.Mpcatobs = rocks.datacloud.Mpcatobs(**{})
    mpcorb: rocks.datacloud.Mpcorb = rocks.datacloud.Mpcorb(**{})
    pairs: rocks.datacloud.Pairs = rocks.datacloud.Pairs(**{})
    phase_functions: rocks.datacloud.PhaseFunction = rocks.datacloud.PhaseFunction(**{})
    taxonomies: rocks.datacloud.Taxonomies = rocks.datacloud.Taxonomies(**{})
    thermal_properties: rocks.datacloud.ThermalProperties = (
        rocks.datacloud.ThermalProperties(**{})
    )
    yarkovskies: rocks.datacloud.Yarkovskies = rocks.datacloud.Yarkovskies(**{})

    def __init__(self, id_, ssocard=None, datacloud=None, skip_id_check=False):
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
        >>> ceres.diameter.value
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
            if ssocard is None:
                ssocard = rocks.ssodnet.get_ssocard(id_)

            if ssocard is None:
                # Asteroid does not have an ssoCard
                # Instantiate minimal ssoCard for meaningful error output.
                ssocard = {"name": id_provided}

                rich.print(
                    f"Error 404: missing ssoCard for [green]{id_provided}[/green]."
                )
                # This only gets printed once
                warnings.warn(
                    "See https://rocks.readthedocs.io/en/latest/tutorials.html#error-404 for help."
                )

            else:
                if datacloud is not None:
                    for catalogue in datacloud:
                        ssocard = self.__add_datacloud_catalogue(
                            id_, catalogue, ssocard
                        )
        else:
            # Something failed. Instantiate minimal ssoCard for meaningful error output.
            ssocard = {"name": id_provided}

        # Deserialize the asteroid data
        try:
            super().__init__(**ssocard)  # type: ignore
        except pydantic.ValidationError as message:

            self.__parse_error_message(message, id_, ssocard)

            # Set the offending properties to None to allow for instantiation anyway
            for error in message.errors():

                # Dynamically remove offending parts of the ssoCard
                offending_part = ssocard

                for location in error["loc"][:-1]:
                    offending_part = offending_part[location]

                del offending_part[error["loc"][-1]]

            super().__init__(**ssocard)  # type: ignore

        # Convert the retrieve datacloud catalogues into DataCloudDataFrame objects
        if datacloud is not None:
            for catalogue in datacloud:

                if catalogue in ["diameters", "albedos"]:
                    catalogue = "diamalbedo"

                setattr(
                    self,
                    catalogue,
                    rocks.datacloud.DataCloudDataFrame(
                        data=getattr(self, catalogue).dict()
                    ),
                )

    def __getattr__(self, name):
        """Implement attribute shortcuts. Gets called if __getattribute__ fails."""

        # These are shortcuts
        if name in self.__aliases["physical"].values():
            return getattr(self.parameters.physical, name)

        if name in self.__aliases["dynamical"].values():
            return getattr(self.parameters.dynamical, name)

        # TODO This could be coded in a more abstract way
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

        if name in self.__aliases["physical"].keys():
            return getattr(
                self.parameters.physical,
                self.__aliases["physical"][name],
            )

        if name in self.__aliases["diamalbedo"]:
            return getattr(self, "diamalbedo")

        raise AttributeError(
            f"'Rock' object has no attribute '{name}'. Run "
            f"'rocks parameters' to get a list of accepted properties."
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
        """Retrieve datacloud catalogue for asteroid and deserialize into
        pydantic model."""

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

        if cat is None or not cat:
            return data

        # turn list of dict (catalogue entries) into dict of list
        cat = {
            key: [c[key] for c in cat]
            if catalogue not in ["aams", "astorb", "pairs", "families"]
            else cat[0][key]
            for key in cat[0].keys()
        }

        # add 'preferred' attribute where applicable
        if catalogue_ssodnet in ["taxonomy", "masses", "diamalbedo"]:
            cat["preferred"] = [False] * len(list(cat.values())[0])
        if catalogue_ssodnet in ["diamalbedo"]:
            cat["preferred_albedo"] = [False] * len(list(cat.values())[0])
            cat["preferred_diameter"] = [False] * len(list(cat.values())[0])

        # add catalogue to Rock
        data[catalogue_attribute] = cat
        return data

    def __parse_error_message(self, message, id_, data):
        """Print informative error message if ssocard data is invalid."""
        print(f"\n{id_}:")

        # Look up offending value in ssoCard
        for error in message.errors():
            value = data

            for loc in error["loc"]:
                try:
                    value = value[loc]
                except TypeError:
                    break

            rich.print(
                f"Error: {' -> '.join([str(e) for e in error['loc']])} is invalid: {error['msg']}\n"
                f"Passed value: {value}\n"
                f"Replacing value with empty default to continue.\n"
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
            "H": "absolute_magnitude",
            "parameters.physical.absolute_magnitude": "absolute_magnitude",
            "parameters.physical.albedo": "albedo",
            "parameters.physical.colors": "colors",
            "parameters.physical.diameter": "diameter",
            "parameters.physical.density": "density",
            "parameters.physical.mass": "mass",
            "parameters.physical.phase_function": "phase_function",
            "parameters.physical.spin": "spin",
            "parameters.physical.taxonomy": "taxonomy",
            "parameters.physical.thermal_properties": "thermal_properties",
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


def rocks_(ids, datacloud=None, progress=False):
    """Create multiple Rock instances.

    Parameters
    ==========
    ids : list of str, list of int, list of float, np.array, pd.Series
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

    # Get IDs
    if len(ids) == 1 or isinstance(ids, str):
        ids = [rocks.identify(ids, return_id=True, progress=progress)[-1]]

    else:
        _, _, ids = zip(*rocks.identify(ids, return_id=True, progress=progress))

    # Load ssoCards asynchronously
    rocks.ssodnet.get_ssocard(
        [id_ for id_ in ids if not id_ is None], progress=progress
    )

    if datacloud is not None:

        if isinstance(datacloud, str):
            datacloud = [datacloud]

        # Load datacloud catalogues asynchronously
        for cat in datacloud:

            if cat not in rocks.datacloud.CATALOGUES.keys():
                raise ValueError(
                    f"Unknown datacloud catalogue name: '{cat}'"
                    f"\nChoose from {rocks.datacloud.CATALOGUES.keys()}"
                )

            rocks.ssodnet.get_datacloud_catalogue(
                [id_ for id_ in ids if not id_ is None], cat, progress=progress
            )

    rocks_ = [
        Rock(id_, skip_id_check=True, datacloud=datacloud) if not id_ is None else None
        for id_ in ids
    ]

    return rocks_
