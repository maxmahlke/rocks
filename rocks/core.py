"""Implement the Rock class and other core rocks functionality."""

from functools import reduce
import datetime as dt
import keyword
from typing import List, Generator

import numpy as np
import pandas as pd
import pydantic
import rich

from rocks import config
from rocks import datacloud as dc
from rocks.logging import logger
from rocks import metadata
from rocks import resolve
from rocks import ssodnet


# ------
# ssoCard as pydantic model
def add_paths(cls, values, parent):
    values["path"] = parent

    for name, value in values.items():
        if isinstance(value, (Parameter, FloatValue, StringValue, IntegerValue)):

            if keyword.iskeyword(name.strip("_")):
                name = name.strip("_")

            if any(
                parameter in parent for parameter in ["color", "phase_function", "spin"]
            ):
                value.path = f"{parent}.<id>.{name}"
            else:
                value.path = f"{parent}.{name}"
    return values


# The lowest level in the ssoCard tree is the are the differnt Values and the Error
class Error(pydantic.BaseModel):
    min_: float = pydantic.Field(np.nan, alias="min")
    max_: float = pydantic.Field(np.nan, alias="max")


# The second lowest level is the Parameter. Values inherit from Parameter.
class Parameter(pydantic.BaseModel):

    _label: str = pydantic.Field("", exclude=True)
    _format: str = pydantic.Field("", exclude=True)
    _symbol: str = pydantic.Field("", exclude=True)
    _description: str = pydantic.Field("", exclude=True)
    path: str = pydantic.Field("", exclude=True)

    def __str__(self):
        return self.json()

    @property
    def label(self):
        return self._label

    @label.getter
    def label(self):
        label = metadata.load_mappings()[self.path]["label"]
        return label

    @property
    def symbol(self):
        return self._symbol

    @symbol.getter
    def symbol(self):
        if "symbol" in metadata.load_mappings()[self.path]:
            return metadata.load_mappings()[self.path]["symbol"]
        return ""

    @property
    def format(self):
        return self._format

    @format.getter
    def format(self):
        if "format" in metadata.load_mappings()[self.path]:
            return metadata.load_mappings()[self.path]["format"]
        return ""

    @property
    def description(self):
        return self._description

    @description.getter
    def description(self):
        if "description" in metadata.load_mappings()[self.path]:
            return metadata.load_mappings()[self.path]["description"]
        return ""


class FloatValue(Parameter):
    _unit: str = ""
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

    @property
    def unit(self):
        return self._unit

    @unit.getter
    def unit(self):
        if "unit" in metadata.load_mappings()[self.path]:
            return metadata.load_mappings()[self.path]["unit"]
        return ""

    @pydantic.root_validator(pre=True)
    def _compute_mean_error(cls, values):

        if "error" in values:
            if "min" in values["error"] and "max" in values["error"]:
                values["error_"] = np.mean(
                    [np.abs(values["error"][which]) for which in ["min", "max"]]
                )

        return values


class IntegerValue(Parameter):
    _unit: str = ""
    value: int = None

    def __str__(self):
        """Print value of numerical parameter including errors and unit if available."""
        return f"{self.value:{self.format.strip('%')}}{self.unit}"

    def __bool__(self):
        return bool(self.value)

    @property
    def unit(self):
        return self._unit

    @unit.getter
    def unit(self):
        if "unit" in metadata.load_mappings()[self.path]:
            return metadata.load_mappings()[self.path]["unit"]
        return ""


class StringValue(Parameter):
    value: str = ""
    path: str = pydantic.Field("", exclude=True)

    def __str__(self):
        return self.value

    def __bool__(self):
        return bool(self.value)


class ListValue(Parameter):
    value: list = []

    def __bool__(self):
        return bool(self.value)


# Other common branches are bibref, links and method
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
class ListWithAttributes(list):
    """Subclass of <list> with a custom __str__ for the Spin parameters."""

    def __init__(self, values):
        """Convert the list items to Spin instances."""

        if isinstance(values, Generator):
            values = list(values)

        if values:  # is the list of parameters populated?
            if isinstance(values[0], dict):  # are we instantiating the parameter class
                if values:
                    list_ = [type(values[0])(**entry) for entry in values]
                else:
                    list_ = [type(values[0])(**{})]  # ensure its never empty
            else:
                list_ = values
        else:
            list_ = []

        return super().__init__(list_)

    def __getattr__(self, name):
        """Implement attribute shortcuts. Gets called if __getattribute__ fails."""
        # If it's a user attribute, we handle it here
        if not name.startswith("__"):
            if self:
                if hasattr(self[0], name):
                    return ListWithAttributes(
                        # type(getattr(self[0], name)),
                        [getattr(solution, name) for solution in self]
                    )
                else:
                    raise AttributeError(f"Parameter does not have attribute {name}")
            else:
                return []
        raise AttributeError


# ------
# Dynamical parameters
class OrbitalElements(Parameter):
    """parameters.dynamical.oribtal_elements"""

    ceu: FloatValue = FloatValue(**{})
    links: LinksParameter = LinksParameter(**{})
    author: StringValue = StringValue(**{})
    bibref: ListWithAttributes = [Bibref(**{})]
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

    @pydantic.root_validator()
    def _add_paths(cls, values):
        return add_paths(cls, values, "parameters.dynamical.orbital_elements")

    _convert_list_to_parameterlist: classmethod = pydantic.validator(
        "bibref", allow_reuse=True, pre=True
    )(lambda list_: ListWithAttributes([Bibref(**element) for element in list_]))


class ProperElements(Parameter):
    links: LinksParameter = LinksParameter(**{})
    bibref: ListWithAttributes = [Bibref(**{})]
    lyapunov_time: FloatValue = FloatValue(**{})
    integration_time: FloatValue = FloatValue(**{})
    proper_eccentricity: FloatValue = FloatValue(**{})
    proper_inclination: FloatValue = FloatValue(**{})
    proper_semi_major_axis: FloatValue = FloatValue(**{})
    proper_sine_inclination: FloatValue = FloatValue(**{})
    proper_frequency_mean_motion: FloatValue = FloatValue(**{})
    proper_frequency_nodal_longitude: FloatValue = FloatValue(**{})
    proper_frequency_perihelion_longitude: FloatValue = FloatValue(**{})

    @pydantic.root_validator()
    def _add_paths(cls, values):
        return add_paths(cls, values, "parameters.dynamical.proper_elements")


class Family(Parameter):
    links: LinksParameter = LinksParameter(**{})
    bibref: ListWithAttributes = [Bibref(**{})]
    method: List[Method] = [Method(**{})]
    family_name: StringValue = StringValue(**{})
    family_number: IntegerValue = IntegerValue(**{})
    family_status: StringValue = StringValue(**{})

    def __str__(self):
        if self.family_number.value is not None:
            return f"({self.family_number}) {self.family_name}"
        else:
            return "No family membership known."

    @pydantic.root_validator()
    def _add_paths(cls, values):
        return add_paths(cls, values, "parameters.dynamical.family")


class Pair(Parameter):
    age: FloatValue = FloatValue(**{})
    distance: FloatValue = FloatValue(**{})
    sibling_name: StringValue = StringValue(**{})
    sibling_number: IntegerValue = IntegerValue(**{})

    @pydantic.root_validator()
    def _add_paths(cls, values):
        return add_paths(cls, values, "parameters.dynamical.pair")


class TisserandParameter(Parameter):
    jupiter: FloatValue = pydantic.Field(FloatValue(**{}), alias="Jupiter")
    method: List[Method] = [Bibref(**{})]
    bibref: ListWithAttributes = [Method(**{})]

    @pydantic.root_validator()
    def _add_paths(cls, values):
        return add_paths(cls, values, "parameters.dynamical.tisserand_parameter")


class Yarkovsky(Parameter):
    S: FloatValue = FloatValue(**{})
    A2: FloatValue = FloatValue(**{})
    snr: FloatValue = FloatValue(**{})
    dadt: FloatValue = FloatValue(**{})
    bibref: ListWithAttributes = [Bibref(**{})]
    method: List[Method] = [Method(**{})]

    def __str__(self):
        return "\n".join([self.A2.__str__(), self.dadt.__str__()])

    @pydantic.root_validator()
    def _add_paths(cls, values):
        return add_paths(cls, values, "parameters.dynamical.yarkovsky")


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
    bibref: ListWithAttributes = []
    method: List[Method] = []

    path = "parameters.physical.albedo.albedo"


class ColorEntry(Parameter):
    color: FloatValue = FloatValue(**{})
    epoch: FloatValue = FloatValue(**{})
    links: LinksParameter = LinksParameter(**{})
    method: List[Method] = []
    bibref: ListWithAttributes = []
    facility: StringValue = StringValue(**{})
    observer: StringValue = StringValue(**{})
    phot_sys: StringValue = StringValue(**{})
    technique: StringValue = StringValue(**{})
    delta_time: FloatValue = FloatValue(**{})
    id_filter_1: StringValue = StringValue(**{})
    id_filter_2: StringValue = StringValue(**{})

    def __bool__(self):
        return bool(np.isfinite(self.color.value))

    def __str__(self):
        if not np.isnan(self.color.value):
            if self.color.error.max_ == self.color.error.min_:
                return rf"{self.color.value:.2f} +- {self.color.error.max_:.2f}  {self.bibref.shortbib}"
            return rf"{self.color.value:.2f} + {self.color.error.max_:.2f} - {self.color.error.min_:.2f}  {self.bibref.shortbib}"
        return "No color on record in this filter."

    @pydantic.root_validator()
    def _add_paths(cls, values):
        return add_paths(cls, values, "parameters.physical.colors.<id>.color")

    _convert_list_to_parameterlist: classmethod = pydantic.validator(
        "bibref", allow_reuse=True, pre=True
    )(lambda list_: ListWithAttributes([Bibref(**element) for element in list_]))


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

    @pydantic.root_validator()
    def _add_paths(cls, values):
        return add_paths(cls, values, "parameters.physical.colors")

    def __str__(self):
        observed = []

        for filter_ in [
            "g_i",
            "g_r",
            "g_z",
            "i_z",
            "r_i",
            "r_z",
            "u_g",
            "u_g",
            "u_r",
            "u_z",
            "J_K",
            "Y_J",
            "Y_K",
            "c_o",
            "v_g",
            "v_i",
            "v_r",
            "v_z",
            "H_K",
            "J_H",
            "Y_H",
            "u_v",
            "V_I",
            "V_R",
            "B_V",
        ]:
            entry = getattr(self, filter_)
            if not np.isnan(entry.color.value):
                observed.append(rf"[{filter_}] {entry.color.value:.2f}")
        if observed:
            return "\n".join(observed)
        return "No color on record."


class Density(FloatValue):
    method: List[Method] = []
    bibref: ListWithAttributes = []

    @pydantic.root_validator()
    def _add_paths(cls, values):
        return add_paths(cls, values, "parameters.physical.density.density")

    _convert_list_to_parameterlist: classmethod = pydantic.validator(
        "bibref", allow_reuse=True, pre=True
    )(lambda list_: ListWithAttributes([Bibref(**element) for element in list_]))


class Diameter(FloatValue):
    links: LinksParameter = LinksParameter(**{})
    method: List[Method] = [Method(**{})]
    bibref: ListWithAttributes = [Bibref(**{})]

    @pydantic.root_validator()
    def _add_paths(cls, values):
        return add_paths(cls, values, "parameters.physical.diameter.diameter")

    _convert_list_to_parameterlist: classmethod = pydantic.validator(
        "bibref", allow_reuse=True, pre=True
    )(lambda list_: ListWithAttributes([Bibref(**element) for element in list_]))


class Mass(FloatValue):
    links: LinksParameter = LinksParameter(**{})
    bibref: ListWithAttributes = [Bibref(**{})]
    method: List[Method] = [Method(**{})]

    @pydantic.root_validator()
    def _add_paths(cls, values):
        return add_paths(cls, values, "parameters.physical.mass.mass")

    _convert_list_to_parameterlist: classmethod = pydantic.validator(
        "bibref", allow_reuse=True, pre=True
    )(lambda list_: ListWithAttributes([Bibref(**element) for element in list_]))


class Phase(Parameter):
    H: FloatValue = FloatValue(**{})
    N: FloatValue = FloatValue(**{})
    G1: FloatValue = FloatValue(**{})
    G2: FloatValue = FloatValue(**{})
    rms: FloatValue = FloatValue(**{})
    phase: Error = Error(**{})
    links: LinksParameter = LinksParameter(**{})
    bibref: ListWithAttributes = [Bibref(**{})]
    facility: StringValue = StringValue(**{})
    name_filter: StringValue = StringValue(**{})

    def __bool__(self):
        return bool(np.isfinite(self.H.value))

    def __str__(self):
        if not np.isnan(self.H.value):
            return rf"H: {self.H.value:.2f}  G1: {self.G1.value:.2f}  G2: {self.G2.value:.2f} {self.bibref.shortbib}"
        return "No phase function on record in this filter."

    _convert_list_to_parameterlist: classmethod = pydantic.validator(
        "bibref", allow_reuse=True, pre=True
    )(lambda list_: ListWithAttributes([Bibref(**element) for element in list_]))


class PhaseFunction(Parameter):
    # Generic
    generic_johnson_V: Phase = pydantic.Field(Phase(**{}), alias="Generic/Johnson.V")
    # ATLAS
    misc_atlas_cyan: Phase = pydantic.Field(Phase(**{}), alias="Misc/Atlas.cyan")
    misc_atlas_orange: Phase = pydantic.Field(Phase(**{}), alias="Misc/Atlas.orange")

    def __getattr__(self, name):
        """Implement attribute shortcuts. Gets called if __getattribute__ fails."""

        if name in config.ALIASES["phase_function"].keys():
            return getattr(self, config.ALIASES["phase_function"][name])
        raise AttributeError

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

    def __str__(self):
        observed = []

        for filter_ in ["generic_johnson_V", "misc_atlas_cyan", "misc_atlas_orange"]:
            entry = getattr(self, filter_)
            if not np.isnan(entry.H.value):
                observed.append(
                    rf"H: {entry.H.value:.2f}  G1: {entry.G1.value:.2f}  G2: {entry.G2.value:.2f}  [{filter_}]"
                )
        if observed:
            return "\n".join(observed)
        return "No phase function on record."

    @pydantic.root_validator()
    def _add_paths(cls, values):
        return add_paths(cls, values, "parameters.physical.phase_functions")


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
    bibref: ListWithAttributes = [Bibref(**{})]
    technique: StringValue = StringValue(**{})

    @pydantic.root_validator()
    def _add_paths(cls, values):
        return add_paths(cls, values, "parameters.physical.spins")

    _convert_list_to_parameterlist: classmethod = pydantic.validator(
        "bibref", allow_reuse=True, pre=True
    )(lambda list_: ListWithAttributes([Bibref(**element) for element in list_]))


class Taxonomy(Parameter):
    links: LinksParameter = LinksParameter(**{})
    class_: StringValue = pydantic.Field(StringValue(**{}), alias="class")
    bibref: ListWithAttributes = [Bibref(**{})]
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

    @pydantic.root_validator()
    def _add_paths(cls, values):
        return add_paths(cls, values, "parameters.physical.taxonomy")

    _convert_list_to_parameterlist: classmethod = pydantic.validator(
        "bibref", allow_reuse=True, pre=True
    )(lambda list_: ListWithAttributes([Bibref(**element) for element in list_]))


class ThermalInertia(FloatValue):
    dsun: FloatValue = FloatValue(**{})
    links: LinksParameter = LinksParameter(**{})
    bibref: ListWithAttributes = [Bibref(**{})]
    method: List[Method] = [Method(**{})]

    @pydantic.root_validator()
    def _add_paths(cls, values):
        return add_paths(
            cls, values, "parameters.physical.thermal_inertia.thermal_inertia"
        )


class AbsoluteMagnitude(FloatValue):
    G: FloatValue = FloatValue(**{})
    bibref: ListWithAttributes = [Bibref(**{})]

    @pydantic.root_validator()
    def _add_paths(cls, values):
        return add_paths(
            cls, values, "parameters.physical.absolute_magnitude.absolute_magnitude"
        )

    _convert_list_to_parameterlist: classmethod = pydantic.validator(
        "bibref", allow_reuse=True, pre=True
    )(lambda list_: ListWithAttributes([Bibref(**element) for element in list_]))


class PhysicalParameters(Parameter):
    mass: Mass = Mass(**{})
    spin: ListWithAttributes = [Spin(**{})]
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
    )(lambda list_: ListWithAttributes([Spin(**element) for element in list_]))


# ------
# Equation of state
class EqStateVector(Parameter):
    ref_epoch: FloatValue = FloatValue(**{})
    position: ListValue = ListValue(**{})
    velocity: ListValue = ListValue(**{})

    @pydantic.root_validator()
    def _add_paths(cls, values):
        return add_paths(cls, values, "parameters.eq_state_vector")


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
    astorb: dc.Astorb = dc.Astorb(**{})
    binaries: dc.Binarymp = dc.Binarymp(**{})
    colors: dc.Colors = dc.Colors(**{})
    densities: dc.Density = dc.Density(**{})
    diamalbedo: dc.Diamalbedo = dc.Diamalbedo(**{})
    families: dc.Families = dc.Families(**{})
    masses: dc.Masses = dc.Masses(**{})
    mpcatobs: dc.Mpcatobs = dc.Mpcatobs(**{})
    mpcorb: dc.Mpcorb = dc.Mpcorb(**{})
    pairs: dc.Pairs = dc.Pairs(**{})
    proper_elements_: dc.Proper_elements = dc.Proper_elements(**{})
    phase_functions: dc.Phase_function = dc.Phase_function(**{})
    taxonomies: dc.Taxonomies = dc.Taxonomies(**{})
    thermal_inertias: dc.Thermal_inertia = dc.Thermal_inertia(**{})
    shapes: dc.Shape = dc.Shape(**{})
    spins: dc.Spin = dc.Spin(**{})
    yarkovskys: dc.Yarkovsky = dc.Yarkovsky(**{})

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
        >>> ceres.taxonomy.class_.value
        'C'
        >>> ceres.taxonomy.shortbib.value
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
            _, _, id_ = resolve.identify(id_, return_id=True)  # type: ignore

        # Get ssoCard and datcloud catalogues
        if not pd.isnull(id_):
            if ssocard is None:
                ssocard = ssodnet.get_ssocard(id_)

            if ssocard is None:
                # Asteroid does not have an ssoCard
                # Instantiate minimal ssoCard for meaningful error output.
                ssocard = {"name": id_provided}

                logger.error(
                    f"Error 404: missing ssoCard for {id_provided}. For help: \n"
                    "https://rocks.readthedocs.io/en/latest/tutorials.html#error-404"
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
                    catalogue_instance = dc.DataCloudDataFrame(
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
                    catalogue_instance = dc.DataCloudDataFrame(
                        data=getattr(self, catalogue).dict()
                    )

                setattr(self, catalogue, catalogue_instance)

    def __getattr__(self, name):
        """Implement attribute shortcuts. Gets called if __getattribute__ fails."""

        # These are shortcuts
        if name in config.ALIASES["physical"].values():
            return getattr(self.parameters.physical, name)

        if name in config.ALIASES["dynamical"].values():
            return getattr(self.parameters.dynamical, name)

        if name in config.ALIASES["eq_state_vector"].values():
            return getattr(self.parameters.eq_state_vector, name)

        # TODO This could be coded in a more abstract way
        # These are proper aliases
        if name in config.ALIASES["orbital_elements"].keys():
            return getattr(
                self.parameters.dynamical.orbital_elements,
                config.ALIASES["orbital_elements"][name],
            )

        if name in config.ALIASES["proper_elements"].keys():
            return getattr(
                self.parameters.dynamical.proper_elements,
                config.ALIASES["proper_elements"][name],
            )

        if name in config.ALIASES["physical"].keys():
            return getattr(
                self.parameters.physical,
                config.ALIASES["physical"][name],
            )

        if name in config.ALIASES["diamalbedo"]:
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

        if catalogue not in config.DATACLOUD.keys():
            raise ValueError(
                f"Unknown datacloud catalogue name: '{catalogue}'"
                f"\nChoose from {config.DATACLOUD.keys()}"
            )

        # get the SsODNet catalogue and the Rock's attribute names
        catalogue_attribute = config.DATACLOUD[catalogue]["attr_name"]
        catalogue_ssodnet = config.DATACLOUD[catalogue]["ssodnet_name"]

        # retrieve the catalogue
        cat = ssodnet.get_datacloud_catalogue(id_, catalogue_ssodnet)

        if cat is None or not cat:
            return data

        # turn list of dict (catalogue entries) into dict of list
        cat = {key: [c[key] if key in c else "" for c in cat] for key in cat[0].keys()}

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

            logger.warning(
                f"object:{id_}[/] Invalid value for {'.'.join([str(e) for e in error['loc']])}"
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
    if isinstance(ids, (float, int, str)) or len(ids) == 1:
        ids = [resolve.identify(ids, return_id=True, progress=progress)[-1]]

    else:
        _, _, ids = zip(*resolve.identify(ids, return_id=True, progress=progress))

    # Load ssoCards asynchronously
    ssodnet.get_ssocard([id_ for id_ in ids if not id_ is None], progress=progress)

    if datacloud is not None:

        if isinstance(datacloud, str):
            datacloud = [datacloud]

        # Load datacloud catalogues asynchronously
        for cat in datacloud:

            if cat not in config.DATACLOUD.keys():
                raise ValueError(
                    f"Unknown datacloud catalogue name: '{cat}'"
                    f"\nChoose from {config.DATACLOUD.keys()}"
                )

            ssodnet.get_datacloud_catalogue(
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


# ------
# ssoCard utility functions
def rgetattr(obj, attr):
    """Deep version of getattr. Retrieve nested attributes."""

    def _getattr(obj, attr):
        return getattr(obj, attr)

    return reduce(_getattr, [obj] + attr.split("."))
