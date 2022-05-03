#!/usr/bin/env python
"""Implement the Rock class and other core rocks functionality."""
import datetime as dt
import json
from typing import Dict, List, Optional
import warnings

import numpy as np
import pandas as pd
import pydantic
import rich

import rocks


# ------
# ssoCard as pydantic model

# The lowest level in the ssoCard tree is the Value
class Error(pydantic.BaseModel):
    min_: float = pydantic.Field(np.nan, alias="min")
    max_: float = pydantic.Field(np.nan, alias="max")


class Value(pydantic.BaseModel):
    error: Error = Error(**{})
    error_: Optional[float] = np.nan
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

    def __bool__(self):
        if np.isnan(self.value):
            return False
        return True

    @pydantic.root_validator(pre=True)
    def _compute_mean_error(cls, values):

        if "error" in values:
            if "min" in values["error"] and "max" in values["error"]:
                values["error_"] = np.mean(
                    [np.abs(values["error"][which]) for which in ["min", "max"]]
                )

        return values


# The second lowest level is the Parameter
class Parameter(pydantic.BaseModel):
    def __str__(self):
        return str(rich.print_json(data=json.loads(self.json()), sort_keys=True))


# Other common branches are bibred, links and method
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


class LinksParameter(Parameter):
    datacloud: Optional[str] = ""


# And a special class for the Spin list
class ParameterList(list):
    """Subclass of <list> with a custom __str__ for the Spin parameters."""

    def __init__(self, list_):
        """Convert the list items to Spin instances."""
        list_ = [Spin(**entry) for entry in list_]

        return super().__init__(list_)

    def __str__(self) -> str:

        return super().__str__()


# ------
# Validators
def convert_spin_to_list(spins: Dict) -> List:
    """Convert the Spin dictionary from the ssoCard into a list.
    Add the spin index as parameter to the Spin entries.

    Parameters
    ----------
    spin : dict
        The dictionary located at parameters.physical.spin in the ssoCard.

    Returns
    -------
    list
        A list of dictionaries, with one dictionary for each entry in parameters.physical.spin
        after removing the index layer.
    """

    spin_dicts = []

    for spin_id, spin_dict in spins.items():
        spin_dict["id_"] = spin_id
        spin_dicts.append(spin_dict)

    return spin_dicts


# ------
# Dynamical parameters
class OrbitalElements(Parameter):
    ceu: Value = Value(**{})
    links: LinksParameter = LinksParameter(**{})
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
    links: LinksParameter = LinksParameter(**{})
    bibref: List[Bibref] = [Bibref(**{})]
    proper_g: Value = Value(**{})
    proper_s: Value = Value(**{})
    proper_eccentricity: Value = Value(**{})
    proper_inclination: Value = Value(**{})
    proper_semi_major_axis: Value = Value(**{})
    proper_sine_inclination: Value = Value(**{})


class Family(Parameter):
    links: LinksParameter = LinksParameter(**{})
    bibref: List[Bibref] = [Bibref(**{})]
    family_name: Optional[str] = ""
    family_number: Optional[int] = None
    family_status: Optional[str] = ""


class PairMember(Parameter):
    age: Value = Value(**{})
    distance: Optional[float] = np.nan
    sibling_name: Optional[str] = ""
    sibling_number: Optional[int] = None


class TisserandParameter(Value):
    method: List[Method] = []
    bibref: List[Bibref] = []


class Yarkovsky(Parameter):
    S: Optional[float] = np.nan
    A2: Value = Value(**{})
    snr: Optional[float] = np.nan
    dadt: Value = Value(**{})
    bibref: List[Bibref] = [Bibref(**{})]

    def __str__(self):
        return "\n".join([self.A2.__str__(), self.dadt.__str__()])


class DynamicalParameters(Parameter):
    pair: List[PairMember] = pydantic.Field([PairMember(**{})], alias="pairs")
    family: Family = Family(**{})
    tisserand_parameter: TisserandParameter = TisserandParameter(**{})
    yarkovsky: Yarkovsky = Yarkovsky(**{})
    proper_elements: ProperElements = ProperElements(**{})
    orbital_elements: OrbitalElements = OrbitalElements(**{})

    def __str__(self):
        return self.json()


# ------
# Physical Value
class Albedo(Value):
    links: LinksParameter = LinksParameter(**{})
    bibref: List[Bibref] = []
    method: List[Method] = []


class ColorEntry(Parameter):
    color: Value = Value(**{})
    epoch: Optional[float] = np.nan
    links: LinksParameter = LinksParameter(**{})
    method: List[Method] = []
    bibref: List[Bibref] = []
    facility: Optional[str] = ""
    observer: Optional[str] = ""
    phot_sys: Optional[str] = ""
    technique: Optional[str] = ""
    delta_time: Optional[float] = np.nan
    id_filter_1: Optional[str] = ""
    id_filter_2: Optional[str] = ""


class Color(Parameter):
    g_i: ColorEntry = pydantic.Field(ColorEntry(**{}), alias="g-i")
    g_r: ColorEntry = pydantic.Field(ColorEntry(**{}), alias="g-r")
    g_z: ColorEntry = pydantic.Field(ColorEntry(**{}), alias="g-z")
    i_z: ColorEntry = pydantic.Field(ColorEntry(**{}), alias="i-z")
    r_i: ColorEntry = pydantic.Field(ColorEntry(**{}), alias="r-i")
    r_z: ColorEntry = pydantic.Field(ColorEntry(**{}), alias="r-z")
    u_g: ColorEntry = pydantic.Field(ColorEntry(**{}), alias="u-g")
    u_g: ColorEntry = pydantic.Field(ColorEntry(**{}), alias="u-g")
    u_r: ColorEntry = pydantic.Field(ColorEntry(**{}), alias="u-r")
    u_z: ColorEntry = pydantic.Field(ColorEntry(**{}), alias="u-z")
    J_K: ColorEntry = pydantic.Field(ColorEntry(**{}), alias="J-K")
    Y_J: ColorEntry = pydantic.Field(ColorEntry(**{}), alias="Y-J")
    Y_K: ColorEntry = pydantic.Field(ColorEntry(**{}), alias="Y-K")
    c_o: ColorEntry = pydantic.Field(ColorEntry(**{}), alias="c-o")
    v_g: ColorEntry = pydantic.Field(ColorEntry(**{}), alias="v-g")
    v_i: ColorEntry = pydantic.Field(ColorEntry(**{}), alias="v-i")
    v_r: ColorEntry = pydantic.Field(ColorEntry(**{}), alias="v-r")
    v_z: ColorEntry = pydantic.Field(ColorEntry(**{}), alias="v-z")
    H_K: ColorEntry = pydantic.Field(ColorEntry(**{}), alias="H-K")
    J_H: ColorEntry = pydantic.Field(ColorEntry(**{}), alias="J-H")
    Y_H: ColorEntry = pydantic.Field(ColorEntry(**{}), alias="Y-H")
    u_v: ColorEntry = pydantic.Field(ColorEntry(**{}), alias="u-v")
    V_I: ColorEntry = pydantic.Field(ColorEntry(**{}), alias="V-I")
    V_R: ColorEntry = pydantic.Field(ColorEntry(**{}), alias="V-R")
    B_V: ColorEntry = pydantic.Field(ColorEntry(**{}), alias="B-V")


class Density(Value):
    method: List[Method] = []
    bibref: List[Bibref] = []

    path_unit: str = "parameters.physical.density"


class Diameter(Value):
    links: LinksParameter = LinksParameter(**{})
    method: List[Method] = [Method(**{})]
    bibref: List[Bibref] = [Bibref(**{})]

    path_unit: str = "parameters.physical.diameter"


class Mass(Value):
    links: LinksParameter = LinksParameter(**{})
    bibref: List[Bibref] = [Bibref(**{})]
    method: List[Method] = [Method(**{})]

    path_unit: str = "parameters.physical.mass"


class Phase(Parameter):
    H: Value = Value(**{})
    N: Optional[float] = np.nan
    G1: Value = Value(**{})
    G2: Value = Value(**{})
    rms: Optional[float] = np.nan
    phase: Error = Error(**{})
    links: LinksParameter = LinksParameter(**{})
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
    t0: Optional[float] = np.nan
    Wp: Optional[float] = np.nan
    id_: Optional[int] = None
    lat: Optional[Value] = Value(**{})
    RA0: Optional[Value] = Value(**{})
    DEC0: Optional[Value] = Value(**{})
    links: LinksParameter = LinksParameter(**{})
    long_: Optional[Value] = pydantic.Field(Value(**{}), alias="long")
    period: Optional[Value] = Value(**{})
    method: Optional[List[Method]] = [Method(**{})]
    bibref: Optional[List[Bibref]] = [Bibref(**{})]
    technique: Optional[str] = ""

    path_unit: str = "parameters.physical.spin"


class Taxonomy(Parameter):
    links: LinksParameter = LinksParameter(**{})
    class_: Optional[str] = pydantic.Field("", alias="class")
    bibref: Optional[List[Bibref]] = [Bibref(**{})]
    method: Optional[List[Method]] = [Method(**{})]
    scheme: Optional[str] = ""
    complex: Optional[str] = ""
    technique: Optional[str] = ""
    waverange: Optional[str] = ""

    def __str__(self):
        if not self.class_:
            return "No taxonomy on record."
        return self.class_


class ThermalInertia(Parameter):
    TI: Value = Value(**{})
    dsun: Optional[float] = np.nan
    links: LinksParameter = LinksParameter(**{})
    bibref: List[Bibref] = []
    method: List[Method] = []


class AbsoluteMagnitude(Value):
    G: Optional[float] = np.nan
    bibref: List[Bibref] = []


class PhysicalParameters(Parameter):
    mass: Mass = Mass(**{})
    spin: ParameterList = ParameterList([{}])
    color: Color = pydantic.Field(Color(**{}), alias="colors")
    albedo: Albedo = Albedo(**{})
    density: Density = Density(**{})
    diameter: Diameter = Diameter(**{})
    taxonomy: Taxonomy = Taxonomy(**{})
    phase_function: PhaseFunction = PhaseFunction(**{})
    thermal_inertia: ThermalInertia = ThermalInertia(**{})
    absolute_magnitude: AbsoluteMagnitude = AbsoluteMagnitude(**{})

    _convert_spin_to_list: classmethod = pydantic.validator("spin", pre=True)(
        convert_spin_to_list
    )
    _convert_list_to_parameterlist: classmethod = pydantic.validator(
        "spin", allow_reuse=True, pre=True
    )(lambda list_: ParameterList(list_))


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


class Ssocard(Parameter):
    version: Optional[str] = ""
    datetime: Optional[dt.datetime] = None


class Links(Parameter):
    self_: Optional[str] = pydantic.Field("", alias="self")
    quaero: Optional[str] = ""
    mapping: Optional[str] = ""


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
    links: Links = Links(**{})
    ssocard: Ssocard = Ssocard(**{})

    # the catalogues
    astorb: rocks.datacloud.Astorb = rocks.datacloud.Astorb(**{})
    binarymp: rocks.datacloud.Binarymp = rocks.datacloud.Binarymp(**{})
    colors: rocks.datacloud.Colors = rocks.datacloud.Colors(**{})
    densities: rocks.datacloud.Density = rocks.datacloud.Density(**{})
    diamalbedo: rocks.datacloud.Diamalbedo = rocks.datacloud.Diamalbedo(**{})
    families: rocks.datacloud.Families = rocks.datacloud.Families(**{})
    masses: rocks.datacloud.Masses = rocks.datacloud.Masses(**{})
    mpcatobs: rocks.datacloud.Mpcatobs = rocks.datacloud.Mpcatobs(**{})
    mpcorb: rocks.datacloud.Mpcorb = rocks.datacloud.Mpcorb(**{})
    pairs: rocks.datacloud.Pairs = rocks.datacloud.Pairs(**{})
    proper_elements: rocks.datacloud.Proper_elements = rocks.datacloud.Proper_elements(
        **{}
    )
    phase_function: rocks.datacloud.Phase_function = rocks.datacloud.Phase_function(
        **{}
    )
    taxonomies: rocks.datacloud.Taxonomies = rocks.datacloud.Taxonomies(**{})
    thermal_inertia: rocks.datacloud.Thermal_inertia = rocks.datacloud.Thermal_inertia(
        **{}
    )
    shapes: rocks.datacloud.Shape = rocks.datacloud.Shape(**{})
    spins: rocks.datacloud.Taxonomies = rocks.datacloud.Taxonomies(**{})
    yarkovsky: rocks.datacloud.Yarkovsky = rocks.datacloud.Yarkovsky(**{})

    def __init__(
        self,
        id_,
        ssocard=None,
        datacloud=None,
        skip_id_check=False,
        suppress_errors=False,
    ):
        """Identify a minor body  and retrieve its properties from SsODNet.

        Parameters
        ----------
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
        suppress_errors: bool
            Do not print errors in the ssoCard. Default is False.

        Returns
        -------
        rocks.core.Rock
            An asteroid class instance, with its properties as attributes.

        Notes
        -----
        If the asteroid could not be identified or the data contains invalid
        types, the number is None and no further attributes but the name are set.

        Example
        -------
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

            if not suppress_errors:
                self.__parse_error_message(message, id_, ssocard)

            # Set the offending properties to None to allow for instantiation anyway
            for error in message.errors():

                # Dynamically remove offending parts of the ssoCard
                offending_part = ssocard

                location_list = error["loc"][:-1]

                if any(
                    property_ in location_list for property_ in ["taxonomy", "spin"]
                ):
                    for property_ in ["taxonomy", "spin"]:
                        if property_ in location_list:
                            # these are lists instead of dicts and the indices are flipped
                            # eg taxonomy bibref 0 becomes taxonomy 0 bibref
                            idx = location_list.index(property_)
                            entry, idx_list = location_list[idx + 1 : idx + 3]

                            try:
                                del ssocard["parameters"]["physical"][property_]
                            except KeyError:
                                pass
                else:

                    for location in error["loc"][:-1]:
                        offending_part = offending_part[location]

                    del offending_part[error["loc"][-1]]

            super().__init__(**ssocard)  # type: ignore

        # Convert the retrieve datacloud catalogues into DataCloudDataFrame objects
        if datacloud is not None:
            for catalogue in datacloud:

                if catalogue in ["diameters", "albedos"]:
                    catalogue = "diamalbedo"

                try:
                    catalogue_instance = rocks.datacloud.DataCloudDataFrame(
                        data=getattr(self, catalogue).dict()
                    )

                # Common occurence of
                # ValueError: All arrays must be of the same length
                # due to malformed datacloud catalogue
                except ValueError:
                    # Drop catalogue attributes with a single entry
                    to_drop = []

                    for attribute, entries in getattr(self, catalogue).dict().items():
                        if len(entries) == 1:
                            to_drop.append(attribute)

                    for attribute in to_drop:
                        delattr(getattr(self, catalogue), attribute)

                    # Let's try this again
                    catalogue_instance = rocks.datacloud.DataCloudDataFrame(
                        data=getattr(self, catalogue).dict()
                    )

                    warnings.warn(
                        f"Removed malformed attributes {to_drop} from datacloud catalogue {catalogue}"
                    )

                setattr(self, catalogue, catalogue_instance)

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
            "'rocks parameters' to get a list of accepted properties."
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
            key: [c[key] if key in c else "" for c in cat]
            if catalogue not in ["aams", "astorb", "families"]
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

        # Look up offending value in ssoCard
        for error in message.errors():
            value = data

            for loc in error["loc"]:
                try:
                    value = value[loc]
                except KeyError:
                    # for Spin entries, the location list is messed up
                    # disabling the entire Spin parameter
                    if "spin" in error["loc"]:
                        error["loc"] = ("parameters", "physical", "spin")
                        break
                except TypeError:
                    break

            rich.print(
                f"[blue]Warning[/] [magenta]object:{id_}[/] Invalid value for {'.'.join([str(e) for e in error['loc']])}"
                # f"\nPassed value: {value}"
            )

    __aliases = {
        "dynamical": {
            "parameters.dynamical.orbital_elements": "orbital_elements",
            "parameters.dynamical.family": "family",
            "parameters.dynamical.pair": "pair",
            "parameters.dynamical.proper_elements": "proper_elements",
            "parameters.dynamical.tisserand_parameter": "tisserand_parameter",
            "parameters.dynamical.yarkovsky": "yarkovsky",
        },
        "physical": {
            "D": "diameter",
            "H": "absolute_magnitude",
            "parameters.physical.absolute_magnitude": "absolute_magnitude",
            "parameters.physical.albedo": "albedo",
            "parameters.physical.colors": "color",
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
            "sinip": "proper_sine_inclination",
        },
        "diamalbedo": ["albedos", "diameters"],
    }


def rocks_(ids, datacloud=None, progress=False, suppress_errors=False):
    """Create multiple Rock instances.

    Parameters
    ----------
    ids : list of str, list of int, list of float, np.array, pd.Series
        An iterable containing minor body identifiers.
    datacloud : list of str
        List of additional catalogues to retrieve from datacloud.
        Default is no additional catalogues.
    progress : bool
        Show progress of instantiation. Default is False.
    suppress_errors: bool
        Do not print errors in the ssoCard. Default is False.

    Returns
    -------
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
        Rock(
            id_,
            skip_id_check=True,
            datacloud=datacloud,
            suppress_errors=suppress_errors,
        )
        if not id_ is None
        else None
        for id_ in ids
    ]

    return rocks_
