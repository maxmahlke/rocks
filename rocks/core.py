"""Implement the Rock class and other core rocks functionality."""

from functools import reduce
import datetime as dt
import keyword
from typing import ClassVar, List, Generator

import numpy as np
import pandas as pd
import pydantic

from rocks import config
from rocks import datacloud as dc
from rocks.logging import logger
from rocks import metadata
from rocks import resolve
from rocks import ssodnet


# ------
# ssoCard as pydantic model
def add_paths(cls, instance, parent):
    instance.path = parent

    for name, value in instance:
        if isinstance(value, (Parameter, FloatValue, StringValue, IntegerValue)):
            if keyword.iskeyword(name.strip("_")):
                name = name.strip("_")

            if any(
                parameter in parent for parameter in ["color", "phase_function", "spin"]
            ):
                value.path = f"{parent}.<id>.{name}"
            else:
                value.path = f"{parent}.{name}"
    return instance


def _build_rich_repr(obj, params: dict) -> str:
    """Build repr for rich output of parameter on console.

    Parameters
    ----------
    obj : object
        The parameter class instance.
    params : dict
        Dict of parameters to echo with parameter attribute name : parameter repr structure.

    Returns
    -------
    str
        The parameter repr.
    """
    return "\n".join(
        f"{repr:>9} {getattr(obj, prop).__rich__()}" for prop, repr in params.items()
    )


# The lowest level in the ssoCard tree is the are the differnt Values and the Error
class Error(pydantic.BaseModel):
    min: float = np.nan
    max: float = np.nan

    @property
    def min_(self):
        logger.warning(
            "Use 'max' and 'min' to access the errors. The 'max_' and 'min_' attributes will soon be removed."
        )
        return self.min

    @property
    def max_(self):
        logger.warning(
            "Use 'max' and 'min' to access the errors. The 'max_' and 'min_' attributes will soon be removed."
        )
        return self.max


# The second lowest level is the Parameter. Values inherit from Parameter.
class Parameter(pydantic.BaseModel):
    label_: str = pydantic.Field("", exclude=True)
    format_: str = pydantic.Field("", exclude=True)
    symbol_: str = pydantic.Field("", exclude=True)
    description_: str = pydantic.Field("", exclude=True)
    path: str = pydantic.Field("", exclude=True)

    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    def __str__(self):
        return self.json()

    @property
    def label(self):
        return self.label_

    @label.getter
    def label(self):
        mappings = metadata.load_mappings()
        if "label" in mappings[self.path]:
            return mappings[self.path]["label"]
        return ""

    @property
    def symbol(self):
        return self.symbol_

    @symbol.getter
    def symbol(self):
        mappings = metadata.load_mappings()
        if "symbol" in mappings[self.path]:
            return mappings[self.path]["symbol"]
        return ""

    @property
    def format(self):
        return self.format_

    @format.getter
    def format(self):
        mappings = metadata.load_mappings()
        if mappings and "format" in mappings[self.path]:
            return mappings[self.path]["format"]
        return ""

    @property
    def description(self):
        return self.description_

    @description.getter
    def description(self):
        mappings = metadata.load_mappings()
        if mappings and "description" in mappings[self.path]:
            return mappings[self.path]["description"]
        return ""


class FloatValue(Parameter):
    _unit: str = ""
    error: Error = Error(**{})  # min and max values
    value: float = np.nan
    error_: float = np.nan  # average of min and max

    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    def __str__(self):
        """Print value of numerical parameter including errors and unit if available."""

        if np.isnan(self.value):
            return "[dim]unknown[/dim]"

        format = self.format.strip("%")

        if np.isnan(self.error.min) and np.isnan(self.error.max):
            return f"{self.value:{format}} {self.unit}"

        if abs(self.error.min) == abs(self.error.max):
            return f"{self.value:{format}} +- {self.error.max:{format}} {self.unit}"
        else:
            return f"{self.value:{format}} +- ({self.error.max:{format}}, {self.error.min:{format}}) {self.unit}"

    def __rich__(self):
        return self.__str__()

    def __bool__(self):
        if np.isnan(self.value):
            return False
        return True

    @property
    def unit(self):
        return self._unit

    @unit.getter
    def unit(self):
        mappings = metadata.load_mappings()
        if mappings and "unit" in mappings[self.path]:
            return mappings[self.path]["unit"]
        return ""

    @pydantic.model_validator(mode="before")
    def _compute_mean_error(cls, values):
        # If the value is a float, convert it to a dict with value and error keys
        if isinstance(values, float):
            values = {"value": values, "error": {"min": np.nan, "max": np.nan}}
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
        if self.value is None:
            return "None"
        if self.unit:
            return f"{self.value:{self.format.strip('%')}} {self.unit}"
        else:
            return f"{self.value:{self.format.strip('%')}}"

    def __rich__(self):
        return self.__str__()

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

    def __rich__(self):
        return self.__str__()

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
    source: str = ""
    bibcode: str = ""
    shortbib: str = ""


class Bibref(Parameter):
    doi: str = ""
    year: int = None
    title: str = ""
    bibcode: str = ""
    shortbib: str = ""

    def __bool__(self):
        return bool(self.shortbib)


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

    def __rich__(self):
        if isinstance(self[0], Bibref):
            return " ".join(ref.shortbib for ref in self)


# ------
# Dynamical parameters
class OrbitalElements(Parameter):
    """parameters.dynamical.oribtal_elements"""

    ceu: FloatValue = FloatValue(**{})
    ceu_epoch: FloatValue = FloatValue(**{})
    links: LinksParameter = LinksParameter(**{})
    author: StringValue = StringValue(**{})
    bibref: ListWithAttributes = ListWithAttributes([Bibref(**{})])
    ceu_rate: FloatValue = FloatValue(**{})
    ref_epoch: FloatValue = FloatValue(**{})
    ref_epoch_timescale: StringValue = StringValue(**{})
    ref_plane: StringValue = StringValue(**{})
    ref_center: StringValue = StringValue(**{})
    inclination: FloatValue = FloatValue(**{})
    mean_motion: FloatValue = FloatValue(**{})
    orbital_arc: IntegerValue = IntegerValue(**{})
    eccentricity: FloatValue = FloatValue(**{})
    mean_anomaly: FloatValue = FloatValue(**{})
    node_longitude: FloatValue = FloatValue(**{})
    orbital_period: FloatValue = FloatValue(**{})
    semi_major_axis: FloatValue = FloatValue(**{})
    apoapsis_distance: FloatValue = FloatValue(**{})
    number_observations: IntegerValue = pydantic.Field(
        IntegerValue(**{}),
        validation_alias=pydantic.AliasChoices(
            "number_observations", "number_observation"
        ),
    )
    periapsis_argument: FloatValue = FloatValue(**{})
    periapsis_distance: FloatValue = FloatValue(**{})
    pericenter_date: FloatValue = FloatValue(**{})

    @pydantic.model_validator(mode="before")
    def _normalize_values(cls, values):
        """Normalize raw v1.2.0 orbital elements into Value-like dictionaries."""

        if not isinstance(values, dict):
            return values

        normalized = dict(values)

        for key in ["author", "ref_epoch_timescale", "ref_plane", "ref_center"]:
            if (
                key in normalized
                and normalized[key] is not None
                and not isinstance(normalized[key], dict)
            ):
                normalized[key] = {"value": normalized[key]}

        for key in ["orbital_arc", "number_observations", "number_observation"]:
            if (
                key in normalized
                and normalized[key] is not None
                and not isinstance(normalized[key], dict)
            ):
                normalized[key] = {"value": int(normalized[key])}

        return normalized

    @property
    def number_observation(self):
        """Backward-compatible alias for number_observations."""

        return self.number_observations

    @pydantic.model_validator(mode="after")
    def _add_paths(cls, values):
        return add_paths(cls, values, "parameters.dynamical.orbital_elements")

    # TODO: The _convert_list_to_parameterlist validator and class Config could
    # be inherited from the Parameter class instead of defining them for each
    # parameter
    _convert_list_to_parameterlist: classmethod = pydantic.field_validator(
        "bibref", mode="before"
    )(lambda list_: ListWithAttributes([Bibref(**element) for element in list_]))


class ProperElements(Parameter):
    links: LinksParameter = LinksParameter(**{})
    bibref: ListWithAttributes = ListWithAttributes([Bibref(**{})])
    lyapunov_time: FloatValue = FloatValue(**{})
    integration_time: FloatValue = FloatValue(**{})
    proper_eccentricity: FloatValue = FloatValue(**{})
    proper_inclination: FloatValue = FloatValue(**{})
    proper_semi_major_axis: FloatValue = FloatValue(**{})
    proper_sine_inclination: FloatValue = FloatValue(**{})
    proper_frequency_mean_motion: FloatValue = FloatValue(**{})
    proper_frequency_nodal_longitude: FloatValue = FloatValue(**{})
    proper_frequency_perihelion_longitude: FloatValue = FloatValue(**{})

    @pydantic.model_validator(mode="after")
    def _add_paths(cls, values):
        return add_paths(cls, values, "parameters.dynamical.proper_elements")

    _convert_list_to_parameterlist: classmethod = pydantic.field_validator(
        "bibref", mode="before"
    )(lambda list_: ListWithAttributes([Bibref(**element) for element in list_]))


class SourceRegions(Parameter):
    hun: FloatValue = FloatValue(**{})
    jfc: FloatValue = FloatValue(**{})
    nu6: FloatValue = FloatValue(**{})
    pho: FloatValue = FloatValue(**{})
    mm31: FloatValue = FloatValue(**{})
    mm21: FloatValue = FloatValue(**{})
    mm52: FloatValue = FloatValue(**{})
    method: List[Method] = [Method(**{})]
    links: LinksParameter = LinksParameter(**{})

    def __rich__(self):
        return _build_rich_repr(
            self,
            {
                "hun": "Hungaria",
                "nu6": "nu6",
                "pho": "Phocaea",
                "mm31": "MMR 3:1",
                "mm21": "MMR 2:1",
                "mm52": "MMR 5:2",
                "jfc": "JFC",
            },
        )

    @pydantic.model_validator(mode="after")
    def _add_paths(cls, values):
        return add_paths(cls, values, "parameters.dynamical.source_regions")


class Family(Parameter):
    links: LinksParameter = LinksParameter(**{})
    bibref: ListWithAttributes = ListWithAttributes([Bibref(**{})])
    method: List[Method] = [Method(**{})]
    family_name: StringValue = StringValue(**{})
    family_number: IntegerValue = IntegerValue(**{})
    family_status: StringValue = StringValue(**{})

    def __rich__(self):
        if self.family_number.value is not None:
            return f"({self.family_number}) {self.family_name}"
        else:
            return "No family membership known."

    def __bool__(self):
        return bool(self.family_name)

    @pydantic.model_validator(mode="after")
    def _add_paths(cls, values):
        return add_paths(cls, values, "parameters.dynamical.family")

    _convert_list_to_parameterlist: classmethod = pydantic.field_validator(
        "bibref", mode="before"
    )(lambda list_: ListWithAttributes([Bibref(**element) for element in list_]))


class MOID(Parameter):
    mercury: FloatValue = pydantic.Field(FloatValue(**{}), alias="Mercury")
    venus: FloatValue = pydantic.Field(FloatValue(**{}), alias="Venus")
    emb: FloatValue = pydantic.Field(
        FloatValue(**{}),
        alias="Earth",
        validation_alias=pydantic.AliasChoices("Earth", "EMB"),
    )
    mars: FloatValue = pydantic.Field(FloatValue(**{}), alias="Mars")
    jupiter: FloatValue = pydantic.Field(FloatValue(**{}), alias="Jupiter")
    saturn: FloatValue = pydantic.Field(FloatValue(**{}), alias="Saturn")
    uranus: FloatValue = pydantic.Field(FloatValue(**{}), alias="Uranus")
    neptune: FloatValue = pydantic.Field(FloatValue(**{}), alias="Neptune")
    method: List[Method] = [Method(**{})]
    links: LinksParameter = LinksParameter(**{})

    @property
    def earth(self):
        """Alias for emb to match v1.2.0 naming."""

        return self.emb

    @pydantic.model_validator(mode="after")
    def _add_paths(cls, values):
        return add_paths(cls, values, "parameters.dynamical.moid")


class Pair(Parameter):
    age: FloatValue = FloatValue(**{})
    links: LinksParameter = LinksParameter(**{})
    bibref: ListWithAttributes = ListWithAttributes([Bibref(**{})])
    method: List[Method] = [Method(**{})]
    distance: FloatValue = FloatValue(**{})
    sibling_name: StringValue = StringValue(**{})
    sibling_number: IntegerValue = IntegerValue(**{})

    def __rich__(self):
        return _build_rich_repr(
            self,
            {
                "age": "age",
                "distance": "distance",
                "sibling_name": "sibling_name",
                "sibling_number": "sibling_number",
            },
        )

    @pydantic.model_validator(mode="after")
    def _add_paths(cls, values):
        return add_paths(cls, values, "parameters.dynamical.pair")

    _convert_list_to_parameterlist: classmethod = pydantic.field_validator(
        "bibref", mode="before"
    )(lambda list_: ListWithAttributes([Bibref(**element) for element in list_]))


class DeltaV(Parameter):
    delta_v: FloatValue = FloatValue(**{})
    transfer_time: FloatValue = FloatValue(**{})
    n_burns: IntegerValue = IntegerValue(**{})
    method: List[Method] = [Method(**{})]
    bibref: ListWithAttributes = ListWithAttributes([Bibref(**{})])

    @pydantic.model_validator(mode="after")
    def _add_paths(cls, values):
        return add_paths(cls, values, "parameters.dynamical.delta_v")

    def __rich__(self):
        return _build_rich_repr(
            self,
            {
                "delta_v": "Delta V",
                "transfer_time": "Transfer Time",
                "n_burns": "N Burns",
            },
        )

    _convert_list_to_parameterlist: classmethod = pydantic.field_validator(
        "bibref", mode="before"
    )(lambda list_: ListWithAttributes([Bibref(**element) for element in list_]))


class TisserandParameters(Parameter):
    jupiter: FloatValue = pydantic.Field(FloatValue(**{}), alias="Jupiter")
    saturn: FloatValue = pydantic.Field(FloatValue(**{}), alias="Saturn")
    uranus: FloatValue = pydantic.Field(FloatValue(**{}), alias="Uranus")
    neptune: FloatValue = pydantic.Field(FloatValue(**{}), alias="Neptune")
    method: List[Method] = [Method(**{})]
    bibref: ListWithAttributes = ListWithAttributes([Bibref(**{})])

    @pydantic.model_validator(mode="after")
    def _add_paths(cls, values):
        return add_paths(cls, values, "parameters.dynamical.tisserand_parameters")

    _convert_list_to_parameterlist: classmethod = pydantic.field_validator(
        "bibref", mode="before"
    )(lambda list_: ListWithAttributes([Bibref(**element) for element in list_]))


class Yarkovsky(Parameter):
    S: FloatValue = FloatValue(**{})
    A2: FloatValue = FloatValue(**{})
    snr: FloatValue = FloatValue(**{})
    dadt: FloatValue = FloatValue(**{})
    links: LinksParameter = LinksParameter(**{})
    bibref: ListWithAttributes = ListWithAttributes([Bibref(**{})])
    method: List[Method] = [Method(**{})]

    def __rich__(self):
        return _build_rich_repr(
            self,
            {"a2": "a2", "dadt": "da/dt", "s": "s", "snr": "snr"},
        )

    @pydantic.model_validator(mode="after")
    def _add_paths(cls, values):
        return add_paths(cls, values, "parameters.dynamical.yarkovsky")

    _convert_list_to_parameterlist: classmethod = pydantic.field_validator(
        "bibref", mode="before"
    )(lambda list_: ListWithAttributes([Bibref(**element) for element in list_]))


class DynamicalParameters(Parameter):
    moid: MOID = MOID(**{})
    pair: Pair = pydantic.Field(Pair(**{}), alias="pair")
    family: Family = Family(**{})
    delta_v: DeltaV = DeltaV(**{})
    source_regions: SourceRegions = SourceRegions(**{})
    tisserand_parameters: TisserandParameters = TisserandParameters(**{})
    yarkovsky: Yarkovsky = Yarkovsky(**{})
    proper_elements: ProperElements = ProperElements(**{})
    orbital_elements: OrbitalElements = OrbitalElements(**{})

    def __str__(self):
        return self.json()


# ------
# Physical Value
class Albedo(FloatValue):
    links: LinksParameter = LinksParameter(**{})
    bibref: ListWithAttributes = ListWithAttributes([Bibref(**{})])
    method: List[Method] = []

    path: str = "parameters.physical.albedo.albedo"

    _convert_list_to_parameterlist: classmethod = pydantic.field_validator(
        "bibref", mode="before"
    )(lambda list_: ListWithAttributes([Bibref(**element) for element in list_]))


class ColorEntry(Parameter):
    index: StringValue = StringValue(**{})
    color: FloatValue = FloatValue(**{})
    epoch: FloatValue = FloatValue(**{})
    links: LinksParameter = LinksParameter(**{})
    method: List[Method] = []
    bibref: ListWithAttributes = ListWithAttributes([Bibref(**{})])
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
            if self.color.error.max == self.color.error.min:
                return rf"{self.color.value:.2f} +- {self.color.error.max:.2f}  {self.bibref.shortbib}"
            return rf"{self.color.value:.2f} + {self.color.error.max:.2f} - {self.color.error.min:.2f}  {self.bibref.shortbib}"
        return "No color on record in this filter."

    @pydantic.model_validator(mode="after")
    def _add_paths(cls, values):
        return add_paths(cls, values, "parameters.physical.colors.<id>.color")

    _convert_list_to_parameterlist: classmethod = pydantic.field_validator(
        "bibref", mode="before"
    )(lambda list_: ListWithAttributes([Bibref(**element) for element in list_]))


class Color(Parameter):
    entries: dict = pydantic.Field(default_factory=dict)

    @pydantic.model_validator(mode="before")
    def _parse_entries(cls, values):
        """Parse v1.2.0 list schema into an index->ColorEntry mapping."""

        if values in (None, ""):
            return {"entries": {}}

        if isinstance(values, dict) and "entries" in values:
            return values

        # Legacy/object schema where each key is already a color index.
        if isinstance(values, dict):
            converted = {}
            for index, entry in values.items():
                if not isinstance(entry, dict):
                    continue
                normalized = dict(entry)
                normalized["index"] = {"value": index}
                for key in [
                    "facility",
                    "observer",
                    "phot_sys",
                    "technique",
                    "id_filter_1",
                    "id_filter_2",
                ]:
                    if key in normalized and not isinstance(normalized[key], dict):
                        normalized[key] = {"value": normalized[key]}
                converted[index] = ColorEntry(**normalized)
            return {"entries": converted}

        if isinstance(values, list):
            converted = {}
            for entry in values:
                if not isinstance(entry, dict):
                    continue

                index = entry.get("index")
                if not index:
                    continue

                normalized = dict(entry)
                normalized["index"] = {"value": index}

                for key in [
                    "facility",
                    "observer",
                    "phot_sys",
                    "technique",
                    "id_filter_1",
                    "id_filter_2",
                ]:
                    if key in normalized and not isinstance(normalized[key], dict):
                        normalized[key] = {"value": normalized[key]}

                converted[index] = ColorEntry(**normalized)

            return {"entries": converted}

        return {"entries": {}}

    def __getitem__(self, key):
        return self.entries[key]

    def __contains__(self, key):
        return key in self.entries

    def get(self, key, default=None):
        return self.entries.get(key, default)

    def keys(self):
        return self.entries.keys()

    def values(self):
        return self.entries.values()

    def items(self):
        return self.entries.items()

    def __iter__(self):
        return iter(self.entries.items())

    def __len__(self):
        return len(self.entries)

    def __bool__(self):
        return any(bool(entry) for entry in self.entries.values())

    @pydantic.model_validator(mode="after")
    def _add_paths(cls, values):
        values.path = "parameters.physical.colors"

        for index, entry in values.entries.items():
            entry.path = f"parameters.physical.colors.{index}.color"
            entry.index.path = f"parameters.physical.colors.{index}.index"

        return values

    def __str__(self):
        observed = []

        for filter_, entry in self.entries.items():
            if not np.isnan(entry.color.value):
                observed.append(rf"[{filter_}] {entry.color.value:.2f}")
        if observed:
            return "\n".join(observed)
        return "No color on record."


class Density(FloatValue):
    links: LinksParameter = LinksParameter(**{})
    method: List[Method] = []
    bibref: ListWithAttributes = ListWithAttributes([Bibref(**{})])

    @pydantic.model_validator(mode="after")
    def _add_paths(cls, values):
        return add_paths(cls, values, "parameters.physical.density.density")

    _convert_list_to_parameterlist: classmethod = pydantic.field_validator(
        "bibref", mode="before"
    )(lambda list_: ListWithAttributes([Bibref(**element) for element in list_]))


class Diameter(FloatValue):
    links: LinksParameter = LinksParameter(**{})
    ratio: FloatValue = FloatValue(**{})
    method: List[Method] = [Method(**{})]
    bibref: ListWithAttributes = ListWithAttributes([Bibref(**{})])

    @pydantic.model_validator(mode="after")
    def _add_paths(cls, values):
        return add_paths(cls, values, "parameters.physical.diameter.diameter")

    _convert_list_to_parameterlist: classmethod = pydantic.field_validator(
        "bibref", mode="before"
    )(lambda list_: ListWithAttributes([Bibref(**element) for element in list_]))


class Mass(FloatValue):
    links: LinksParameter = LinksParameter(**{})
    ratio: FloatValue = FloatValue(**{})
    bibref: ListWithAttributes = ListWithAttributes([Bibref(**{})])
    method: List[Method] = [Method(**{})]

    @pydantic.model_validator(mode="after")
    def _add_paths(cls, values):
        return add_paths(cls, values, "parameters.physical.mass.mass")

    _convert_list_to_parameterlist: classmethod = pydantic.field_validator(
        "bibref", mode="before"
    )(lambda list_: ListWithAttributes([Bibref(**element) for element in list_]))


class HillSphereRadius(FloatValue):
    bibref: ListWithAttributes = ListWithAttributes([Bibref(**{})])

    @pydantic.model_validator(mode="before")
    def _normalize_values(cls, values):
        if values in (None, ""):
            return {}
        return values

    @pydantic.model_validator(mode="after")
    def _add_paths(cls, values):
        return add_paths(
            cls, values, "parameters.physical.hill_sphere_radius.hill_sphere_radius"
        )

    _convert_list_to_parameterlist: classmethod = pydantic.field_validator(
        "bibref", mode="before"
    )(lambda list_: ListWithAttributes([Bibref(**element) for element in list_]))


class Ellipsoid(Parameter):
    a_b: FloatValue = pydantic.Field(FloatValue(**{}), alias="a/b")
    a_c: FloatValue = pydantic.Field(FloatValue(**{}), alias="a/c")
    b_c: FloatValue = pydantic.Field(FloatValue(**{}), alias="b/c")
    links: LinksParameter = LinksParameter(**{})
    method: List[Method] = [Method(**{})]
    bibref: ListWithAttributes = ListWithAttributes([Bibref(**{})])

    @pydantic.model_validator(mode="before")
    def _normalize_values(cls, values):
        if values in (None, ""):
            return {}
        return values

    @pydantic.model_validator(mode="after")
    def _add_paths(cls, values):
        return add_paths(cls, values, "parameters.physical.ellipsoid")

    def __bool__(self):
        return any(
            np.isfinite(getattr(self, axis).value) for axis in ["a_b", "a_c", "b_c"]
        )

    def __str__(self):
        if self.__bool__():
            return (
                f"a/b: {self.a_b.value:.2f}  a/c: {self.a_c.value:.2f}  b/c: {self.b_c.value:.2f}"
            )
        return "No ellipsoid on record."

    def __rich__(self):
        return self.__str__()

    _convert_list_to_parameterlist: classmethod = pydantic.field_validator(
        "bibref", mode="before"
    )(lambda list_: ListWithAttributes([Bibref(**element) for element in list_]))


class Phase(Parameter):
    id_filter: StringValue = StringValue(**{})
    H: FloatValue = FloatValue(**{})
    N: FloatValue = FloatValue(**{})
    G1: FloatValue = FloatValue(**{})
    G2: FloatValue = FloatValue(**{})
    rms: FloatValue = FloatValue(**{})
    phase: Error = Error(**{})
    links: LinksParameter = LinksParameter(**{})
    bibref: ListWithAttributes = ListWithAttributes([Bibref(**{})])
    facility: StringValue = StringValue(**{})
    technique: StringValue = StringValue(**{})
    name_filter: StringValue = StringValue(**{})

    def __bool__(self):
        return bool(np.isfinite(self.H.value))

    def __str__(self):
        if not np.isnan(self.H.value):
            return rf"H: {self.H.value:.2f}  G1: {self.G1.value:.2f}  G2: {self.G2.value:.2f} {self.bibref.shortbib}"
        return "No phase function on record in this filter."

    _convert_list_to_parameterlist: classmethod = pydantic.field_validator(
        "bibref", mode="before"
    )(lambda list_: ListWithAttributes([Bibref(**element) for element in list_]))

    @pydantic.model_validator(mode="after")
    def _add_paths(cls, values):
        return add_paths(cls, values, "parameters.physical.phase_functions")


class PhaseFunction(Parameter):
    entries: dict = pydantic.Field(default_factory=dict)

    _LEGACY_FIELD_TO_FILTER: ClassVar[dict] = {
        "generic_johnson_V": "Generic/Johnson.V",
        "generic_johnson_R": "Generic/Johnson.R",
        "gaia_gaia3_G": "GAIA/GAIA3.G",
        "misc_atlas_cyan": "Misc/Atlas.cyan",
        "misc_atlas_orange": "Misc/Atlas.orange",
        "palomar_ztf_g": "Palomar/ZTF.g",
        "palomar_ztf_r": "Palomar/ZTF.r",
    }

    @pydantic.model_validator(mode="before")
    def _parse_entries(cls, values):
        """Parse phase function entries from list or dictionary schemas."""

        def _normalize(entry, filter_id):
            normalized = dict(entry)
            normalized["id_filter"] = {"value": filter_id}

            for key in ["H", "N", "G1", "G2", "rms"]:
                if key in normalized and not isinstance(normalized[key], dict):
                    normalized[key] = {"value": float(normalized[key])}

            for key in ["name_filter", "facility", "technique"]:
                if key in normalized and not isinstance(normalized[key], dict):
                    normalized[key] = {"value": normalized[key]}

            return normalized

        if values in (None, ""):
            return {"entries": {}}

        if isinstance(values, dict) and "entries" in values:
            return values

        # Legacy/object schema where each key is already a filter identifier.
        if isinstance(values, dict):
            converted = {}
            for key, entry in values.items():
                if not isinstance(entry, dict):
                    continue

                normalized = _normalize(entry, key)
                converted[key] = Phase(**normalized)

            return {"entries": converted}

        if isinstance(values, list):
            converted = {}
            for entry in values:
                if not isinstance(entry, dict):
                    continue

                filter_id = entry.get("id_filter")
                if not filter_id:
                    continue

                normalized = _normalize(entry, filter_id)
                converted[filter_id] = Phase(**normalized)

            return {"entries": converted}

        return {"entries": {}}

    def __getattr__(self, name):
        """Implement attribute shortcuts. Gets called if __getattribute__ fails."""

        if name in config.ALIASES["phase_function"]:
            name = config.ALIASES["phase_function"][name]

        if name in type(self)._LEGACY_FIELD_TO_FILTER:
            return self.entries.get(
                type(self)._LEGACY_FIELD_TO_FILTER[name], Phase(**{})
            )

        if name in self.entries:
            return self.entries[name]

        raise AttributeError

    def __getitem__(self, key):
        return self.entries[key]

    def __contains__(self, key):
        return key in self.entries

    def get(self, key, default=None):
        return self.entries.get(key, default)

    def keys(self):
        return self.entries.keys()

    def values(self):
        return self.entries.values()

    def items(self):
        return self.entries.items()

    def __iter__(self):
        return iter(self.entries.items())

    def __len__(self):
        return len(self.entries)

    def __bool__(self):
        return any(bool(entry) for entry in self.entries.values())

    def __str__(self):
        observed = []

        for filter_, entry in self.entries.items():
            if not np.isnan(entry.H.value):
                observed.append(
                    rf"H: {entry.H.value:.2f}  G1: {entry.G1.value:.2f}  G2: {entry.G2.value:.2f}  \[{filter_}]"
                )
        if observed:
            return "\n".join(observed)
        return "No phase function on record."

    def __rich__(self):
        return self.__str__()

    @pydantic.model_validator(mode="after")
    def _add_paths(cls, values):
        values.path = "parameters.physical.phase_functions"

        for filter_id, entry in values.entries.items():
            entry.path = f"parameters.physical.phase_functions.{filter_id}"
            entry.id_filter.path = (
                f"parameters.physical.phase_functions.{filter_id}.id_filter"
            )

        return values


class Spin(Parameter):
    t0: FloatValue = FloatValue(**{})
    W0: FloatValue = FloatValue(**{})
    Wp: FloatValue = FloatValue(**{})
    id_: IntegerValue = pydantic.Field(
        IntegerValue(**{}),
        alias="id_spin",
        validation_alias=pydantic.AliasChoices("id_spin", "id_"),
    )
    lat: FloatValue = FloatValue(**{})
    RA0: FloatValue = FloatValue(**{})
    DEC0: FloatValue = FloatValue(**{})
    links: LinksParameter = LinksParameter(**{})
    long_: FloatValue = pydantic.Field(FloatValue(**{}), alias="long")
    bibref: ListWithAttributes = ListWithAttributes([Bibref(**{})])
    method: List[Method] = [Method(**{})]
    period: FloatValue = FloatValue(**{})
    obliquity: FloatValue = FloatValue(**{})
    technique: StringValue = StringValue(**{})
    period_type: StringValue = StringValue(**{})
    period_flag: StringValue = StringValue(**{})

    @pydantic.model_validator(mode="before")
    def _normalize_values(cls, values):
        """Normalize raw v1.2.0 spin entries into Value-like dictionaries."""

        if not isinstance(values, dict):
            return values

        normalized = dict(values)

        if "id_spin" not in normalized and "id_" in normalized:
            normalized["id_spin"] = normalized["id_"]

        if "id_spin" in normalized and not isinstance(normalized["id_spin"], dict):
            normalized["id_spin"] = {"value": int(normalized["id_spin"])}

        for key in [
            "t0",
            "W0",
            "Wp",
            "lat",
            "RA0",
            "DEC0",
            "long",
            "period",
            "obliquity",
        ]:
            if (
                key in normalized
                and normalized[key] is not None
                and not isinstance(normalized[key], dict)
            ):
                normalized[key] = {"value": float(normalized[key])}

        for key in ["technique", "period_type", "period_flag"]:
            if (
                key in normalized
                and normalized[key] is not None
                and not isinstance(normalized[key], dict)
            ):
                normalized[key] = {"value": normalized[key]}

        return normalized

    @pydantic.model_validator(mode="after")
    def _add_paths(cls, values):
        return add_paths(cls, values, "parameters.physical.spins")

    def __str__(self):
        if not np.isnan(self.period.value):
            return f"{self.period.value:.2f}{self.period.unit} [{self.technique.value}, {self.bibref.shortbib[0]}]"
        return "No spin on record."

    _convert_list_to_parameterlist: classmethod = pydantic.field_validator(
        "bibref", mode="before"
    )(lambda list_: ListWithAttributes([Bibref(**element) for element in list_]))


class Taxonomy(Parameter):
    links: LinksParameter = LinksParameter(**{})
    class_: StringValue = pydantic.Field(StringValue(**{}), alias="class")
    bibref: ListWithAttributes = ListWithAttributes([Bibref(**{})])
    method: List[Method] = [Method(**{})]
    scheme: StringValue = StringValue(**{})
    complex: StringValue = StringValue(**{})
    technique: StringValue = StringValue(**{})
    waverange: StringValue = StringValue(**{})

    @pydantic.model_validator(mode="before")
    def _normalize_values(cls, values):
        """Wrap raw v1.2.0 string leaves into StringValue-compatible dicts."""
        if not isinstance(values, dict):
            return values
        normalized = dict(values)
        for key in ["class", "scheme", "complex", "technique", "waverange"]:
            if key in normalized and not isinstance(normalized[key], dict):
                normalized[key] = {"value": normalized[key]}
        return normalized

    def __bool__(self):
        return bool(self.class_.value)

    def __str__(self):
        if not self.class_:
            return "No taxonomy on record."
        return self.class_.value

    def __rich__(self):
        return self.__str__()

    @pydantic.model_validator(mode="after")
    def _add_paths(cls, values):
        return add_paths(cls, values, "parameters.physical.taxonomy")

    _convert_list_to_parameterlist: classmethod = pydantic.field_validator(
        "bibref", mode="before"
    )(lambda list_: ListWithAttributes([Bibref(**element) for element in list_]))


class ThermalInertia(FloatValue):
    dsun: FloatValue = FloatValue(**{})
    links: LinksParameter = LinksParameter(**{})
    bibref: ListWithAttributes = ListWithAttributes([Bibref(**{})])
    method: List[Method] = [Method(**{})]

    @pydantic.model_validator(mode="after")
    def _add_paths(cls, values):
        return add_paths(
            cls, values, "parameters.physical.thermal_inertia.thermal_inertia"
        )

    _convert_list_to_parameterlist: classmethod = pydantic.field_validator(
        "bibref", mode="before"
    )(lambda list_: ListWithAttributes([Bibref(**element) for element in list_]))


class AbsoluteMagnitude(Parameter):
    H: FloatValue = FloatValue(**{})
    G: FloatValue = FloatValue(**{})
    bibref: ListWithAttributes = ListWithAttributes([Bibref(**{})])

    @pydantic.model_validator(mode="after")
    def _add_paths(cls, values):
        return add_paths(
            cls, values, "parameters.physical.absolute_magnitude.absolute_magnitude"
        )

    def __bool__(self):
        return bool(self.H.value)

    def __str__(self):
        if not self.H.value:
            return "No absolute magnitude on record."
        return f"H={self.H.value}+-{self.H.error_} G={self.G.value}+-{self.G.error_}"

    def __rich__(self):
        return self.__str__()

    _convert_list_to_parameterlist: classmethod = pydantic.field_validator(
        "bibref", mode="before"
    )(lambda list_: ListWithAttributes([Bibref(**element) for element in list_]))


class PhysicalParameters(Parameter):
    mass: Mass = Mass(**{})
    spin: ListWithAttributes = pydantic.Field(
        [Spin(**{})],
        validation_alias=pydantic.AliasChoices("spins", "spin"),
    )
    color: Color = pydantic.Field(Color(**{}), alias="colors")
    albedo: Albedo = Albedo(**{})
    density: Density = Density(**{})
    diameter: Diameter = Diameter(**{})
    hill_sphere_radius: HillSphereRadius = HillSphereRadius(**{})
    ellipsoid: Ellipsoid = Ellipsoid(**{})
    taxonomy: Taxonomy = Taxonomy(**{})
    phase_function: PhaseFunction = pydantic.Field(
        PhaseFunction(**{}), alias="phase_functions"
    )
    thermal_inertia: ThermalInertia = ThermalInertia(**{})
    absolute_magnitude: AbsoluteMagnitude = AbsoluteMagnitude(**{})

    @pydantic.field_validator("spin", mode="before")
    def _parse_spin(cls, value):
        """Accept both the old postprocessed 'spin' list and raw v1.2.0 'spins' list."""
        if isinstance(value, list):
            return ListWithAttributes([Spin(**element) for element in value])
        # Empty string (missing spin in v1.2.0) or None
        return ListWithAttributes([Spin(**{})])


# ------
# Equation of state
class EqStateVector(Parameter):
    ref_epoch: FloatValue = FloatValue(**{})
    position: ListValue = ListValue(**{})
    velocity: ListValue = ListValue(**{})

    @pydantic.model_validator(mode="after")
    def _add_paths(cls, values):
        return add_paths(cls, values, "parameters.eq_state_vector")


# ------
# Highest level branches
class Parameters(Parameter):
    physical: PhysicalParameters = PhysicalParameters(**{})
    dynamical: DynamicalParameters = DynamicalParameters(**{})
    eq_state_vector: EqStateVector = EqStateVector(**{})


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
    type: str = ""
    class_: str = pydantic.Field("", alias="class")
    number: int = None
    parent: str = ""
    system: str = ""
    filename: str = ""
    siblings: list = []
    is_valid: bool = True

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
    ellipsoids: dc.Ellipsoids = dc.Ellipsoids(**{})
    families: dc.Families = dc.Families(**{})
    masses: dc.Masses = dc.Masses(**{})
    mpcatobs: dc.Mpcatobs = dc.Mpcatobs(**{})
    mpcorb: dc.Mpcorb = dc.Mpcorb(**{})
    pairs: dc.Pairs = dc.Pairs(**{})
    polarimetric_observations: dc.Polarimetric_observations = (
        dc.Polarimetric_observations(**{})
    )
    proper_elements_: dc.Proper_elements = dc.Proper_elements(**{})
    phase_functions: dc.Phase_function = dc.Phase_function(**{})
    taxonomies: dc.Taxonomies = dc.Taxonomies(**{})
    thermal_inertias: dc.Thermal_inertia = dc.Thermal_inertia(**{})
    spins: dc.Spin = dc.Spin(**{})
    yarkovskys: dc.Yarkovsky = dc.Yarkovsky(**{})
    yorps: dc.Yorp = dc.Yorp(**{})

    def __init__(
        self,
        id_,
        ssocard=None,
        datacloud=None,
        skip_id_check=False,
        on_404="warning",
    ):
        """Identify a minor body  and retrieve its properties from SsODNet.

        Parameters
        ----------
        id_ : str, int, float
            Identifying asteroid name, designation, or number
        ssocard : dict
            Optional argument providing a dictionary to use as ssoCard.
            Default is None, triggering the query of an ssoCard.
        datacloud : list of str
            Optional list of additional catalogues to retrieve from datacloud.
            Default is no additional catalogues.
        skip_id_check : bool
            Optional argument to prevent resolution of ID before getting ssoCard.
            Default is False.
        on_404: str
            Action to take when encountering a 404 error. Choose from ["error", "warning", "ignore"].

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

        if on_404 not in ["ignore", "warning", "error"]:
            raise ValueError(
                f"on_404 is {on_404}, expected one of ['ignore', 'warning' , 'error']."
            )

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

                MESSAGE = (
                    f"Error 404: missing ssoCard for {id_provided}. For help: \n"
                    "https://rocks.readthedocs.io/en/latest/tutorials.html#error-404"
                )

                if on_404 == "warning":
                    logger.error(MESSAGE)
                elif on_404 == "error":
                    raise ValueError(MESSAGE)

            else:
                if datacloud is not None:
                    for catalogue in datacloud:
                        ssocard = self.__add_datacloud_catalogue(
                            id_, catalogue, ssocard
                        )
        else:
            # Something failed. Instantiate minimal ssoCard for meaningful error output.
            ssocard = {"name": id_provided, "is_valid": False}

        # Add filename attribute
        ssocard["filename"] = "".join(
            char.lower() for char in ssocard["name"] if char.isalnum()
        )

        # Deserialize the asteroid data
        try:
            if ssocard["ssocard"]["version"] < "1.2.0":
                raise ValueError(
                    f"Unsupported ssoCard version {ssocard['ssocard']['version']}.\n"
                    "Please update your ssoCard to version 1.2.0 or later using `rocks status` -> `Clear cache`."
                )

            super().__init__(**ssocard)  # type: ignore
        except pydantic.ValidationError as message:
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

                # Ensure that all catalogue entries have the right length
                catalogue_dict = getattr(self, catalogue).dict()

                REQUIRED_LENGTH = max(len(val) for val in catalogue_dict.values())

                for key, value in catalogue_dict.items():
                    if len(value) == REQUIRED_LENGTH:
                        continue

                    # Malformed entry, make all entries None
                    catalogue_dict[key] = REQUIRED_LENGTH * [None]

                # Instantiate catalogue and assign to Rock
                catalogue_instance = dc.DataCloudDataFrame(data=catalogue_dict)
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
        keys = set().union(*(entry.keys() for entry in cat))
        cat = {key: [c[key] if key in c else None for c in cat] for key in keys}

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

            logger.debug(
                f"{id_}: Invalid value for {'.'.join([str(e) for e in error['loc']])}"
            )
            logger.debug(f"Passed value: {value}")

    def get_parameter(self, param: str):
        """Get the parameter of a Rock by passing the name as a string."""
        return rgetattr(self, param)


def rocks_(ids, datacloud=None, progress=False, on_404="warning"):
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
    on_404: str
        Action to take when encountering a 404 error. Choose from ["error", "warning", "ignore"].

    Returns
    -------
    list of rocks.core.Rock
        A list of Rock instances
    """
    if isinstance(ids, pd.DataFrame):
        if "sso_id" not in ids.columns or "sso_number" not in ids.columns:
            raise ValueError(
                "If passing a pd.DataFrame, it has to be (a subset of) the ssoBFT."
            )
        ids = ids.sort_values("sso_number")
        return rocks_(ids.sso_id)

    if on_404 not in ["ignore", "warning", "error"]:
        raise ValueError(
            f"on_404 is {on_404}, expected one of ['ignore', 'warning' , 'error']."
        )

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

    result = [
        Rock(id_, skip_id_check=True, datacloud=datacloud) if not id_ is None else None
        for id_ in ids
    ]

    return result


# ------
# ssoCard utility functions
def rgetattr(obj, attr):
    """Deep version of getattr. Retrieve nested attributes."""

    def _getattr(obj, attr):
        return getattr(obj, attr)

    return reduce(_getattr, [obj] + attr.split("."))
