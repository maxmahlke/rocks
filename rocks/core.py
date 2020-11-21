#!/usr/bin/env python
"""Implement the Rock class and other core rocks functionality.
"""
import copy
from functools import singledispatch
from types import SimpleNamespace
import warnings

import numpy as np
import pandas as pd
from tqdm import tqdm

import rocks


class Rock:
    "For space rocks."

    def __init__(self, identifier, ssoCard=None, datacloud=[], skip_id_check=False):
        """Identify a minor body  and retrieve its properties from SsODNet.

        Parameters
        ==========
        identifier : str, int, float
            Identifying asteroid name, designation, or number
        ssoCard : dict
            Optional previously acquired ssoCard.
        datacloud : list of str
            List of additional catalogues to retrieve from datacloud.
            Default is no additional catalogues.

        Returns
        =======
        rocks.core.Rock
            An asteroid class instance, with its properties as attributes.

        Notes
        =====
        If the asteroid could not be identified, the name and number are None
        and no further attributes are set.

        Example
        =======
        >>> from rocks.core import Rock
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

        # Identify minor body
        if not skip_id_check:
            self.name, self.number, self.id = rocks.resolve.identify(
                identifier, return_id=True
            )
        else:
            self.id = identifier

        if not isinstance(self.id, str):
            return

        ssoCard = ssoCard if ssoCard is not None else rocks.utils.get_ssoCard(self.id)

        if ssoCard is None:
            # Every object needs a name and a number
            if not hasattr(self, "name"):
                self.name, self.number = rocks.resolve.identify(
                    self.id, return_id=False
                )
            # No data to update
            ssoCard = {}

        # Fill attributes from argument, cache, or query
        ssoCard = rocks.utils.sanitize_keys(ssoCard)
        attributes = copy.deepcopy(rocks.TEMPLATE)
        attributes = rocks.utils.update_ssoCard(attributes, ssoCard)

        # Add JSON keys as attributes, mapping to the appropriate type
        for attribute in attributes.keys():
            setattr(
                self,
                attribute,
                cast_types(attributes[attribute]),
            )

        if self.number == 0:
            self.number = np.nan

        # Set uncertainties and values
        self.__add_metadata()

        # Add datacloud list attributes
        for catalogue in datacloud:
            self.__add_datacloud_catalogue(catalogue)

            # Add preferred entries
            getattr(
                self, rocks.utils.DATACLOUD_META[catalogue]["attr_name"]
            ).select_preferred(catalogue)

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return (
            self.__class__.__qualname__
            + f"(number={self.number!r}, name={self.name!r})"
        )

    def __str__(self):
        return f"({self.number}) {self.name}"

    def __eq__(self, other):
        if self.__class__ is other.__class__:
            return self.name == other.name
        return NotImplemented

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return (self.number, self.name) < (other.number, other.name)
        return NotImplemented  # pragma: no cover

    def __le__(self, other):
        if self.__class__ is other.__class__:
            return (self.number, self.name) <= (other.number, other.name)
        return NotImplemented  # pragma: no cover

    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return (self.number, self.name) > (other.number, other.name)
        return NotImplemented  # pragma: no cover

    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return (self.number, self.name) >= (other.number, other.name)
        return NotImplemented  # pragma: no cover

    def __getattr__(self, name):
        """Implement attribute shortcuts.
        Gets called if getattribute fails."""
        # Implements shortcuts: omission of parameters.physical/dynamical
        if name in rocks.SHORTCUTS["physical"]:
            return getattr(self.parameters.physical, name)
        elif name in rocks.SHORTCUTS["dynamical"]:
            return getattr(self.parameters.dynamical, name)
        raise AttributeError(f"Unknown attribute {name}")

    def __add_metadata(self):
        """docstring for __add_metadata"""
        for meta, target in rocks.META_MAPPING.items():
            try:
                setattr(
                    rocks.utils.rgetattr(self, target),
                    "uncertainty",
                    rocks.utils.rgetattr(self, meta),
                )
            except AttributeError:
                # some unit paths are currently ill-defined
                pass
            try:
                setattr(
                    rocks.utils.rgetattr(self, target),
                    "unit",
                    rocks.utils.rgetattr(self, meta.replace("uncertainty", "unit")),
                )
            except AttributeError:
                # some unit paths are currently ill-defined
                pass

    def __add_datacloud_catalogue(self, catalogue):
        """docstring for __add_datacloud_catalogue"""
        if not hasattr(getattr(self, "datacloud"), catalogue):
            warnings.warn(f"Unknown datacloud catalogue requested: {catalogue}")
            return

        catalogue_dict = rocks.utils.retrieve_catalogue(
            getattr(getattr(self, "datacloud"), catalogue)
        )

        if catalogue_dict[self.id]["datacloud"] is None:
            setattr(
                self,
                rocks.utils.DATACLOUD_META[catalogue]["attr_name"],
                None,
            )
            return

        catalogue_list = catalogue_dict[self.id]["datacloud"][catalogue]
        catalogue_list = [rocks.utils.sanitize_keys(dict_) for dict_ in catalogue_list]

        setattr(
            self,
            rocks.utils.DATACLOUD_META[catalogue]["attr_name"],
            cast_types(catalogue_list),
        )


class stringParameter(str):
    """For minor body parameters which are strings, e.g. taxonomy."""

    def __new__(self, value):
        return str.__new__(self, value)

    def __init__(self, value):
        str.__init__(value)


class floatParameter(float):
    """For minor body parameters which are floats, e.g. albedo.

    Allows to assign attributes.
    """

    def __new__(self, value):
        return float.__new__(self, value)

    def __init__(self, value):
        float.__init__(value)


class intParameter(int):
    """For minor body parameters which are floats, e.g. number.

    Allows to assign attributes.
    """

    def __new__(self, value):
        return int.__new__(self, value)

    def __init__(self, value):
        float.__init__(value)


class propertyCollection(SimpleNamespace):
    """For collections of data, e.g. taxonomy -> class, method, shortbib.

    Collections of float properties have plotting and averaging methods.
    """

    #  def __repr__(self):
        #  return self.__class__.__qualname__ + json.dumps(self.__dict__, indent=2)

    #  def __str__(self):
        #  return self.__class__.__qualname__ + json.dumps(self.__dict__, indent=2)

    def __len__(self):

        _value_sample = list(self.__dict__.values())[0]

        if isinstance(_value_sample, list):
            return len(_value_sample)
        else:
            return 1

    def __iter__(self):
        self._iter_index = -1
        return self

    def __next__(self):
        self._iter_index += 1

        if len(self) == 1 and self._iter_index == 0:
            return self
        elif self._iter_index < len(self):
            return SimpleNamespace(
                **dict(
                    (k, v[self._iter_index])
                    for k, v in self.__dict__.items()
                    if k != "_iter_index"
                )
            )
        raise StopIteration

    def scatter(self, prop_name, **kwargs):
        return rocks.plots.scatter(self, prop_name, **kwargs)

    def hist(self, prop_name, **kwargs):
        return rocks.plots.hist(self, prop_name, **kwargs)

    def select_preferred(self, prop_name):
        """Select the preferred values based on the observation methods.

        Parameters
        ==========
        prop_name : str
            The property to rank.

        Returns
        =======
        list of bool
            Entry "preferred" in propertyCollection, True if preferred, else False
        """
        if prop_name == "diamalbedo":
            setattr(
                self,
                "preferred_albedo",
                rocks.properties.rank_properties("albedo", self),
            )
            setattr(
                self,
                "preferred_diameter",
                rocks.properties.rank_properties("diameter", self),
            )
            setattr(
                self,
                "preferred",
                [
                    any([di, ai])
                    for di, ai in zip(self.preferred_diameter, self.preferred_albedo)
                ],
            )
        else:
            self.preferred = rocks.properties.rank_properties(prop_name, self)


class listSameTypeParameter(list):
    """For several measurements of a single parameters of any type
    in datcloud catalogues.
    """

    def __init__(self, data):
        """Construct list which allows for assigning attributes.

        Parameters
        ==========
        data : iterable
            The minor body data from datacloud.
        """
        self.datatype = self.__get_type(data)

        if self.datatype is not None:
            list.__init__(self, [self.datatype(d) for d in data])
        else:
            list.__init__(self, [None for d in data])

    def __get_type(self, values):
        """Infers type from str variable."""
        if not values:
            return None
        else:
            try:
                values = [float(value) for value in values]
                if all(
                    [
                        value.is_integer()
                        and "e" not in str(value)
                        and "E" not in str(value)
                        for value in values
                    ]
                ):
                    return int
                else:
                    return float
            except ValueError:
                return str

    def weighted_average(self, errors=None, preferred=[]):
        """Compute weighted average of float-type parameters.

        Parameters
        ==========
        errors : list of floats, np.ndarraya of floats
            Optional list of associated uncertainties. Default is unit
            unceratinty.
        preferred : list of bools
            Compute average only from values where preferred is True.

        Returns
        ======
        (float, float)
        Weighted average and its uncertainty.
        """
        if self.datatype is not float:
            raise TypeError("Property is not of type float.")

        observable = np.array(self)

        # Make uniform weights in case no errors are provided
        if errors is None:
            warnings.warn("No error provided, using uniform weights.")
            errors = np.ones(len(self))
        else:
            # Remove measurements where the error is zero
            errors = np.array(errors)

        if preferred:
            observable = observable[preferred]
            errors = errors[preferred]

        return rocks.utils.weighted_average(observable, errors)


def rocks_(identifier, datacloud=[], progress=False):
    """Create multiple Rock instances via POST request.

    Parameters
    ==========
    identifier : list of str, list of int, list of float, np.array, pd.Series
        An iterable containing minor body identifiers.
    datacloud : list of str
        List of additional catalogues to retrieve from datacloud. Default is
        [], no additional data.
    progress : bool
        Show progress of instantiation. Default is False.

    Returns
    =======
    list of rocks.core.Rock
        A list of Rock instances
    """
    if isinstance(identifier, pd.Series):
        identifier = identifier.values

    # Ensure we know these objects
    ids = [
        id_
        for _, _, id_ in rocks.resolve.identify(
            identifier, return_id=True, progress=progress, rocks_=True
        )
    ]

    ssoCards = rocks.utils.get_ssoCards(ids, progress=progress)

    if progress:
        progressbar = tqdm(desc="Building rocks", total=len(ids))

    rocks_ = []

    for id_, ssoCard in zip(ids, ssoCards):
        rocks_.append(Rock(id_, ssoCard, datacloud, skip_id_check=True))
        if progress:
            progressbar.update()
    return rocks_


@singledispatch
def cast_types(value):
    return value


@cast_types.register(dict)
def _cast_dict(value):
    return propertyCollection(
        **{
            k: cast_types(v) if isinstance(v, dict) else __TYPES[type(v)](v)
            for k, v in value.items()
        }
    )


@cast_types.register(list)
def _cast_list(list_):
    """Turn lists of dicts into a dict of lists."""
    #  breakpoint()
    if len(list_) == 1:
        return cast_types(list_[0])
    return propertyCollection(
        **{k: listSameTypeParameter([dic[k] for dic in list_]) for k in list_[0]}
    )


__TYPES = {
    type(None): lambda v: None,
    None: lambda v: None,
    int: intParameter,
    str: stringParameter,
    float: floatParameter,
    dict: propertyCollection,
    list: _cast_list,
}
