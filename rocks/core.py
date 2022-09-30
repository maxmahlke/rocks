#!/usr/bin/env python
"""Implement the Rock class and other core rocks functionality."""
import datetime as dt
from typing import List
import warnings

import numpy as np
import pandas as pd
import pydantic
import rich

import rocks


# ------
# ssoCard as pydantic model
ALIASES = {
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
        "parameters.physical.thermal_inertia": "thermal_inertia",
    },
    "orbital_elements": {
        "a": "semi_major_axis",
        "e": "eccentricity",
        "i": "inclination",
        "P": "orbital_period",
    },
    "proper_elements": {
        "ap": "proper_semi_major_axis",
        "ep": "proper_eccentricity",
        "ip": "proper_inclination",
        "sinip": "proper_sine_inclination",
    },
    "diamalbedo": ["albedos", "diameters"],
    "phase_function": {
        "V": "generic_johnson_V",
        "cyan": "misc_atlas_cyan",
        "orange": "misc_atlas_orange",
    },
}

# The lowest level in the ssoCard tree is the Value
class Error(pydantic.BaseModel):
    min_: float = pydantic.Field(np.nan, alias="min")
    max_: float = pydantic.Field(np.nan, alias="max")


class Value(pydantic.BaseModel):
    label: str = ""
    format: str = ""
    symbol: str = ""
    description: str = ""


class FloatValue(Value):
    unit: str = ""
    error: Error = Error(**{})  # min_ and max_ values
    value: float = np.nan
    error_: float = np.nan  # average of min_ and max_

    def __str__(self):
        """Print value of numerical parameter including errors and unit if available."""

        format = self.format.strip("%")

        if abs(self.error.min_) == abs(self.error.max_):
            return f"{self.value:{format}} +- {self.error.max_:{format}} {self.unit}"
        else:
            return f"{self.value:{format}} +- ({self.error.max_:{format}}, {self.error.min_:{format}}) {self.unit}"

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


class IntegerValue(Value):
    unit: str = ""
    value: int = None

    def __str__(self):
        """Print value of numerical parameter including errors and unit if available."""
        return f"{self.value:{self.format.strip('%')}}{self.unit}"

    def __bool__(self):
        return bool(self.value)


class StringValue(Value):
    value: str = ""

    def __str__(self):
        return self.value

    def __bool__(self):
        return bool(self.value)


class ListValue(Value):
    value: list = []

    def __str__(self):
        return self.value

    def __bool__(self):
        return bool(self.value)


# The second lowest level is the Parameter
class Parameter(pydantic.BaseModel):

    label: str = ""
    description: str = ""

    def __str__(self):
        return self.json()


# Other common branches are bibred, links and method
class Method(Parameter):
    doi: str = ""
    name: str = ""
    year: int = None
    title: str = ""
    bibcode: str = ""
    shortbib: str = ""


class Bibref(Parameter):
    doi: str = ""
    year: int = None
    title: str = ""
    bibcode: str = ""
    shortbib: str = ""


class LinksParameter(Parameter):
    datacloud: str = ""
    selection: str = ""


# And a special class for the Spin list
class SpinList(list):
    """Subclass of <list> with a custom __str__ for the Spin parameters."""

    def __init__(self, list_):
        """Convert the list items to Spin instances."""

        if list_:  # spin list is populated
            list_ = [Spin(**entry) for entry in list_]
        else:
            list_ = [Spin(**{})]  # ensure it's never empty

        return super().__init__(list_)

    def __str__(self) -> str:
        return "\n".join(entry.json() for entry in self)

    def __bool__(self) -> bool:
        return any(np.isfinite(entry.period.value) for entry in self)


# ------
# Dynamical parameters
class OrbitalElements(Parameter):
    """parameters.dynamical.oribtal_elements"""

    ceu: FloatValue = FloatValue(**{})
    links: LinksParameter = LinksParameter(**{})
    author: StringValue = StringValue(**{})
    bibref: List[Bibref] = [Bibref(**{})]
    ceu_rate: FloatValue = FloatValue(**{})
    ref_epoch: FloatValue = FloatValue(**{})
    inclination: FloatValue = FloatValue(**{})
    mean_motion: FloatValue = FloatValue(**{})
    orbital_arc: IntegerValue = IntegerValue(**{})
    eccentricity: FloatValue = FloatValue(**{})
    mean_anomaly: FloatValue = FloatValue(**{})
    node_longitude: FloatValue = FloatValue(**{})
    orbital_period: FloatValue = FloatValue(**{})
    semi_major_axis: FloatValue = FloatValue(**{})
    number_observation: FloatValue = FloatValue(**{})
    perihelion_argument: FloatValue = FloatValue(**{})


class ProperElements(Parameter):
    links: LinksParameter = LinksParameter(**{})
    bibref: List[Bibref] = [Bibref(**{})]
    lyapunov_time: FloatValue = FloatValue(**{})
    integration_time: FloatValue = FloatValue(**{})
    proper_eccentricity: FloatValue = FloatValue(**{})
    proper_inclination: FloatValue = FloatValue(**{})
    proper_semi_major_axis: FloatValue = FloatValue(**{})
    proper_sine_inclination: FloatValue = FloatValue(**{})
    proper_frequency_mean_motion: FloatValue = FloatValue(**{})
    proper_frequency_nodal_longitude: FloatValue = FloatValue(**{})
    proper_frequency_perihelion_longitude: FloatValue = FloatValue(**{})


class Family(Parameter):
    links: LinksParameter = LinksParameter(**{})
    bibref: List[Bibref] = [Bibref(**{})]
    method: List[Method] = [Method(**{})]
    family_name: StringValue = StringValue(**{})
    family_number: IntegerValue = IntegerValue(**{})
    family_status: StringValue = StringValue(**{})

    def __str__(self):
        if self.family_number is not None:
            return f"({self.family_number}) {self.family_name}"
        else:
            return "No family membership known."


class Pair(Parameter):
    age: FloatValue = FloatValue(**{})
    distance: FloatValue = FloatValue(**{})
    sibling_name: StringValue = StringValue(**{})
    sibling_number: IntegerValue = IntegerValue(**{})


class TisserandParameter(Parameter):
    jupiter: FloatValue = pydantic.Field(FloatValue(**{}), alias="Jupiter")
    method: List[Method] = [Bibref(**{})]
    bibref: List[Bibref] = [Method(**{})]


class Yarkovsky(Parameter):
    S: FloatValue = FloatValue(**{})
    A2: FloatValue = FloatValue(**{})
    snr: FloatValue = FloatValue(**{})
    dadt: FloatValue = FloatValue(**{})
    bibref: List[Bibref] = [Bibref(**{})]
    method: List[Method] = [Method(**{})]

    def __str__(self):
        return "\n".join([self.A2.__str__(), self.dadt.__str__()])


class DynamicalParameters(Parameter):
    pair: Pair = pydantic.Field(Pair(**{}), alias="pairs")
    family: Family = Family(**{})
    tisserand_parameter: TisserandParameter = TisserandParameter(**{})
    yarkovsky: Yarkovsky = Yarkovsky(**{})
    proper_elements: ProperElements = ProperElements(**{})
    orbital_elements: OrbitalElements = OrbitalElements(**{})

    def __str__(self):
        return self.json()


# ------
# Physical Value
class Albedo(FloatValue):
    links: LinksParameter = LinksParameter(**{})
    bibref: List[Bibref] = []
    method: List[Method] = []


class ColorEntry(Parameter):
    color: FloatValue = FloatValue(**{})
    epoch: FloatValue = FloatValue(**{})
    links: LinksParameter = LinksParameter(**{})
    method: List[Method] = []
    bibref: List[Bibref] = []
    facility: StringValue = StringValue(**{})
    observer: StringValue = StringValue(**{})
    phot_sys: StringValue = StringValue(**{})
    technique: StringValue = StringValue(**{})
    delta_time: FloatValue = FloatValue(**{})
    id_filter_1: StringValue = StringValue(**{})
    id_filter_2: StringValue = StringValue(**{})


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


class Density(FloatValue):
    method: List[Method] = []
    bibref: List[Bibref] = []


class Diameter(FloatValue):
    links: LinksParameter = LinksParameter(**{})
    method: List[Method] = [Method(**{})]
    bibref: List[Bibref] = [Bibref(**{})]


class Mass(FloatValue):
    links: LinksParameter = LinksParameter(**{})
    bibref: List[Bibref] = [Bibref(**{})]
    method: List[Method] = [Method(**{})]


class Phase(Parameter):
    H: FloatValue = FloatValue(**{})
    N: FloatValue = FloatValue(**{})
    G1: FloatValue = FloatValue(**{})
    G2: FloatValue = FloatValue(**{})
    rms: FloatValue = FloatValue(**{})
    phase: Error = Error(**{})
    links: LinksParameter = LinksParameter(**{})
    bibref: List[Bibref] = [Bibref(**{})]
    facility: StringValue = StringValue(**{})
    name_filter: StringValue = StringValue(**{})

    def __bool__(self):
        return bool(np.isfinite(self.H.value))

    def __str__(self):
        if not np.isnan(self.H.value):
            return rf"H: {self.H.value:.2f}  G1: {self.G1.value:.2f}  G2: {self.G2.value:.2f}  [{self.bibref[0].shortbib}]"
        return "No phase function on record in this filter."


class PhaseFunction(Parameter):
    # Generic
    generic_johnson_V: Phase = pydantic.Field(Phase(**{}), alias="Generic/Johnson.V")
    # ATLAS
    misc_atlas_cyan: Phase = pydantic.Field(Phase(**{}), alias="Misc/Atlas.cyan")
    misc_atlas_orange: Phase = pydantic.Field(Phase(**{}), alias="Misc/Atlas.orange")

    def __getattr__(self, name):
        """Implement attribute shortcuts. Gets called if __getattribute__ fails."""

        if name in ALIASES["phase_function"].keys():
            return getattr(self, ALIASES["phase_function"][name])

    def __bool__(self):
        return any(
            [
                np.isfinite(getattr(self, filter_).H.value)
                for filter_ in [
                    "generic_johnson_V",
                    "misc_atlas_cyan",
                    "misc_atlas_orange",
                ]
            ]
        )

    def __repr__(self):
        observed = []

        for filter_ in ["generic_johnson_V", "misc_atlas_cyan", "misc_atlas_orange"]:
            entry = getattr(self, filter_)
            if not np.isnan(entry.H.value):
                observed.append(
                    rf"H: {entry.H.value:.2f}  G1: {entry.G1.value:.2f}  G2: {entry.G2.value:.2f}  \[{filter_}]"
                )
        if observed:
            return "\n".join(observed)
        return "No phase function on record."


class Spin(Parameter):
    t0: FloatValue = FloatValue(**{})
    Wp: FloatValue = FloatValue(**{})
    id_: IntegerValue = IntegerValue(**{})
    lat: FloatValue = FloatValue(**{})
    RA0: FloatValue = FloatValue(**{})
    DEC0: FloatValue = FloatValue(**{})
    links: LinksParameter = LinksParameter(**{})
    long_: FloatValue = pydantic.Field(FloatValue(**{}), alias="long")
    period: FloatValue = FloatValue(**{})
    obliquity: FloatValue = FloatValue(**{})
    method: List[Method] = [Method(**{})]
    bibref: List[Bibref] = [Bibref(**{})]
    technique: StringValue = StringValue(**{})


class Taxonomy(Parameter):
    links: LinksParameter = LinksParameter(**{})
    class_: StringValue = pydantic.Field(StringValue(**{}), alias="class")
    bibref: List[Bibref] = [Bibref(**{})]
    method: List[Method] = [Method(**{})]
    scheme: StringValue = StringValue(**{})
    complex: StringValue = StringValue(**{})
    technique: StringValue = StringValue(**{})
    waverange: StringValue = StringValue(**{})

    def __bool__(self):
        return bool(self.class_.value)

    def __str__(self):
        if not self.class_:
            return "No taxonomy on record."
        return self.class_.value


class ThermalInertia(FloatValue):
    dsun: FloatValue = FloatValue(**{})
    links: LinksParameter = LinksParameter(**{})
    bibref: List[Bibref] = [Bibref(**{})]
    method: List[Method] = [Method(**{})]


class AbsoluteMagnitude(FloatValue):
    G: FloatValue = FloatValue(**{})
    bibref: List[Bibref] = [Bibref(**{})]
    links: LinksParameter = LinksParameter(**{})


class PhysicalParameters(Parameter):
    mass: Mass = Mass(**{})
    spin: SpinList = SpinList([])
    color: Color = pydantic.Field(Color(**{}), alias="colors")
    albedo: Albedo = Albedo(**{})
    density: Density = Density(**{})
    diameter: Diameter = Diameter(**{})
    taxonomy: Taxonomy = Taxonomy(**{})
    phase_function: PhaseFunction = pydantic.Field(
        PhaseFunction(**{}), alias="phase_functions"
    )
    thermal_inertia: ThermalInertia = ThermalInertia(**{})
    absolute_magnitude: AbsoluteMagnitude = AbsoluteMagnitude(**{})

    _convert_list_to_parameterlist: classmethod = pydantic.validator(
        "spin", allow_reuse=True, pre=True
    )(lambda list_: SpinList(list_))


# ------
# Equation of state
class EqStateVector(Parameter):
    ref_epoch: FloatValue = FloatValue(**{})
    position: ListValue = ListValue(**{})
    velocity: ListValue = ListValue(**{})


# ------
# Highest level branches
class Parameters(Parameter):
    physical: PhysicalParameters = PhysicalParameters(**{})
    dynamical: DynamicalParameters = DynamicalParameters(**{})
    eq_state_vector: EqStateVector = EqStateVector(**{})

    class Config:
        arbitrary_types_allowed = True


class Ssocard(Parameter):
    version: str = ""
    datetime: dt.datetime = None


class Links(Parameter):
    self_: str = pydantic.Field("", alias="self")
    quaero: str = ""
    mapping: str = ""


class Rock(pydantic.BaseModel):
    """Instantiate a specific asteroid with data from its ssoCard."""

    # the basics
    id_: str = pydantic.Field("", alias="id")
    name: str
    type_: str = pydantic.Field("", alias="type")
    class_: str = pydantic.Field("", alias="class")
    number: int = None
    parent: str = ""
    system: str = ""

    # the heart
    parameters: Parameters = Parameters(**{})

    # the meta
    links: Links = Links(**{})
    ssocard: Ssocard = Ssocard(**{})

    # the catalogues
    astorb: rocks.datacloud.Astorb = rocks.datacloud.Astorb(**{})
    binaries: rocks.datacloud.Binarymp = rocks.datacloud.Binarymp(**{})
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
    phase_functions: rocks.datacloud.Phase_function = rocks.datacloud.Phase_function(
        **{}
    )
    taxonomies: rocks.datacloud.Taxonomies = rocks.datacloud.Taxonomies(**{})
    thermal_inertias: rocks.datacloud.Thermal_inertia = rocks.datacloud.Thermal_inertia(
        **{}
    )
    shapes: rocks.datacloud.Shape = rocks.datacloud.Shape(**{})
    spins: rocks.datacloud.Spin = rocks.datacloud.Spin(**{})
    yarkovskys: rocks.datacloud.Yarkovsky = rocks.datacloud.Yarkovsky(**{})

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

                # rename 'spins' to 'spin' so it does not shadow the datacloud property
                # TODO this should be done at the parameter-name level
                if "spins" in ssocard["parameters"]["physical"]:
                    ssocard["parameters"]["physical"]["spin"] = ssocard["parameters"][
                        "physical"
                    ]["spins"]

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

                    # warnings.warn(
                    #     f"Removed malformed attributes {to_drop} from datacloud catalogue {catalogue}"
                    # )

                setattr(self, catalogue, catalogue_instance)

    def __getattr__(self, name):
        """Implement attribute shortcuts. Gets called if __getattribute__ fails."""

        # These are shortcuts
        if name in ALIASES["physical"].values():
            return getattr(self.parameters.physical, name)

        if name in ALIASES["dynamical"].values():
            return getattr(self.parameters.dynamical, name)

        # TODO This could be coded in a more abstract way
        # These are proper aliases
        if name in ALIASES["orbital_elements"].keys():
            return getattr(
                self.parameters.dynamical.orbital_elements,
                ALIASES["orbital_elements"][name],
            )

        if name in ALIASES["proper_elements"].keys():
            return getattr(
                self.parameters.dynamical.proper_elements,
                ALIASES["proper_elements"][name],
            )

        if name in ALIASES["physical"].keys():
            return getattr(
                self.parameters.physical,
                ALIASES["physical"][name],
            )

        if name in ALIASES["diamalbedo"]:
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
            if catalogue not in ["aams", "families"]
            else cat[0][key]
            for key in cat[0].keys()
        }

        # add 'preferred' attribute where applicable
        if catalogue_ssodnet in ["thermal_inertia", "taxonomy", "masses", "diamalbedo"]:
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
                f"\nPassed value: {value}"
            )


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
