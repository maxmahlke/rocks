#!/usr/bin/env python
"""Utility functions for rocks."""

import collections
from functools import reduce
import json
import keyword
import os
import pickle
import sys
import time
import urllib
import warnings

import click
from iterfzf import iterfzf
import numpy as np
import pandas as pd
import requests
from tqdm import tqdm

import rocks


def warning_on_one_line(message, category, filename, lineno, file=None, line=None):
    if "rocks/" in filename:
        return f"rocks: {message}\n"
    else:
        return "%s:%s: %s: %s\n" % (filename, lineno, category.__name__, message)


warnings.formatwarning = warning_on_one_line


def get_valid_ssocard_properties():
    if not os.path.isfile(rocks.PATH_TEMPLATE):
        rocks.utils.retrieve_ssoCard_template()

    with open(rocks.PATH_TEMPLATE, "r") as file_:
        TEMPLATE = json.load(file_)

    # ssoCard properties
    valid_props = [
        p for p in pd.json_normalize(TEMPLATE).columns if not p.startswith("datacloud")
    ]
    # missing intermediate levels
    valid_props = set(
        valid_props + [".".join(v.split(".")[:-1]) for v in valid_props if "." in v]
    )

    valid_props = sorted(list(valid_props), key=len)
    return valid_props


# ------
# Index functions
def read_index():
    """Read local index of asteroid numbers, names, SsODNet IDs.

    Returns
    =======
    pd.DataFrame
        Asteroid index with three columns.
    """
    with open(rocks.PATH_INDEX, "rb") as ind:
        return pickle.load(ind)


def create_index():
    """Update index of numbered SSOs."""

    # Get currently indexed objects
    index = read_index()

    # Get list of numbered asteroids from MPC
    url = "https://www.minorplanetcenter.net/iau/lists/NumberedMPs.txt"
    numbered = pd.read_fwf(url, colspecs=[(0, 7)], names=["number"])
    numbered = set(int(n.strip(" (")) for n in numbered.number)  # type: ignore

    # Compare list to index
    missing = set(index.number) ^ set(numbered)

    if not missing:
        return

    # Get ids of missing entries, append to index
    names, numbers, ids = zip(*rocks.identify(missing, return_id=True))

    index = index.append(
        pd.DataFrame(
            {
                "name": names,
                "number": numbers,
                "id_": ids,
            }
        )
    )

    # Save index to file
    index = (
        index.dropna(how="any")
        .drop_duplicates("number")
        .sort_values("number", ascending=True)
        .astype({"number": np.int64, "name": str, "id_": str})
    )

    index = index.reset_index()

    with open(rocks.PATH_INDEX, "wb") as ind:
        pickle.dump(index, ind, protocol=4)


def retrieve_index_from_repository():
    """Downloads the index of numbered asteroids from the rocks GitHub
    repository and saves it to the cache directory."""

    URL = "https://github.com/maxmahlke/rocks/blob/master/data/index.pkl?raw=True"

    index = pickle.load(urllib.request.urlopen(URL))
    index = index[["number", "name", "id_"]]

    with open(rocks.PATH_INDEX, "wb") as ind:
        pickle.dump(index, ind, protocol=4)


def select_sso_from_index():  # pragma: no cover
    """Select SSO numbers and designations from interactive fuzzy search.

    Returns
    =======
    str
        asteroid name or designation
    int
        asteroid number

    Notes
    -----
    If the selection is interrupted with ctrl-c, ``(None, None)`` is returned.

    Examples
    --------
    >>> import rocks
    >>> name, number, id_ = rocks.utils.select_sso_from_index()
    """
    INDEX = read_index()

    def _fuzzy_desig_selection(index):
        """Generator for fuzzy search of asteroid index file."""
        for number, name in zip(index.number, index["name"]):
            yield f"{number} {name}"

    try:
        nunaid = iterfzf(_fuzzy_desig_selection(INDEX), exact=True)
        number, *name = nunaid.split()

    except AttributeError:  # no SSO selected
        return None, np.nan, None

    id_ = INDEX.loc[INDEX.number == int(number), "id_"].values[0]

    return " ".join(name), int(number), id_


# ------
# ssoCard utility functions
# def rsetattr(obj, attr, val):  # pragma: no cover
#     """Deep version of setattr."""
#     pre, _, post = attr.rpartition(".")
#     return setattr(rgetattr(obj, pre) if pre else obj, post, val)
def rgetattr(obj, attr):
    """Deep version of getattr. Retrieve nested attributes.

    Parameters
    ==========
    obj
        Any python object with attributes.
    attr : str
        Attribut of obj. Nested attributes can be referrenced with '.'

    Returns
    =======
    _
        The requested attribute.
    """

    def _getattr(obj, attr):
        return getattr(obj, attr)

    return reduce(_getattr, [obj] + attr.split("."))


def retrieve_ssocard_template():
    """Retrieve current ssoCard template from SsODNet."""

    URL = (
        "https://ssp.imcce.fr/webservices/ssodnet/api/"
        "ssocard/templates/catalogue-template_aster-astorb.json"
    )

    response = requests.get(URL)

    if response.ok:
        ssoCard = response.json()

        with open(rocks.PATH_TEMPLATE, "w") as file_:
            json.dump(ssoCard, file_)

    else:
        warnings.warn(f"Retrieving the template failed with url:\n{URL}")


def get_unit(path_unit):
    """Get unit from units JSON file.

    Parameters
    ==========
    path_unit : str
        Path to the parameter in the JSON tree, starting at unit and
        separating the levels with periods.

    Returns
    =======
    str
        The unit of the requested parameter.
    """
    PATH_UNITS = os.path.join(rocks.PATH_CACHE, "unit-template_aster-astorb.json")

    if not os.path.isfile(PATH_UNITS):
        print("Units not present in cache directory, retrieving them from SsODNet..")

        # Retrieve unit list from SsODNet
        URL = "https://ssp.imcce.fr/webservices/ssodnet/api/ssocard/unit_aster-astorb.json"

        response = requests.get(URL)

        if response.ok:
            units = response.json()

            with open(PATH_UNITS, "w") as file_:
                json.dump(units, file_)

        else:
            warnings.warn(f"Retrieving the units failed with url:\n{URL}")

    with open(PATH_UNITS, "r") as units:
        units = json.load(units)

    for key in path_unit.split("."):
        units = units[key]

    return units


# def get_description(name):
#     PATH_UNITS = os.path.join(
#         os.path.expanduser("~"), "astro/rocks/data/unit-template_aster-astorb.json"
#     )

#     breakpoint()

#     print(pd.json_normalize(PATH_UNITS).columns)


# ------
# Pretty-print methods
def pretty_print_card(ssoCard, minimal):
    """Pretty-print ssoCard to terminal. Called by rocks info.

    Parameters
    ==========
    ssoCard : dict
        Minor body ssoCard.
    minimal : bool
        Reduce information to basics.
    """
    from rich.console import Console

    console = Console()

    if not minimal:
        # Print entire JSON
        console.print(ssoCard)
    else:

        from rich.panel import Panel
        from rocks.core import Rock

        rock = Rock(ssoCard["id"], ssoCard, skip_id_check=True)

        minimal_card = f"""

        type: {rock.type:<12} class: {rock.class_}
        taxonomy: {rock.taxonomy.class_:<12} ap: {rock.proper_elements.proper_semi_major_axis:.4}

        """  # {rock.proper_elements.semi_major_axis.unit}
        console.print(Panel(minimal_card, title=f"({rock.number}) {rock.name}"))


def pretty_print_property(rock, prop, plot=False):
    """Echo asteroid property for a single minor body.
    Print datacloud collections. Optionally open plots.

    Parameters
    ==========
    rock : rocks.Rock
        The asteroid Rock instance
    prop : str
        Asteroid property, attribute from JSON template
    plot : bool
        Plot propertyCollection. Default is False.
    """
    if isinstance(prop, rocks.core.stringParameter):
        _echo_stringParameter(prop)
    elif isinstance(prop, rocks.core.intParameter):
        _echo_intParameter(prop)
    elif isinstance(prop, rocks.core.floatParameter):
        _echo_floatParameter(prop)
    elif isinstance(prop, rocks.core.propertyCollection):
        _echo_propertyCollection(rock, prop, plot)
    elif isinstance(prop, rocks.core.listSameTypeParameter):
        _echo_listSameTyeParameter(prop, plot)
    else:
        print(prop)

    sys.exit()


def _echo_stringParameter(prop):
    """Echos stringParameter value."""
    print(prop)


def _echo_intParameter(prop):
    """Echos intParameter value."""
    if hasattr(prop, "unit"):
        unit = getattr(prop, "unit")
    else:
        unit = ""
    if hasattr(prop, "uncertainty"):
        uncert = getattr(prop, "uncertainty")
    else:
        uncert = ""

    if uncert:
        print(f"{prop:,} +- {uncert:,} {unit}")
    else:
        print(f"{prop}")


def _echo_floatParameter(prop):
    """Echos floatParameter value."""
    if hasattr(prop, "unit"):
        unit = getattr(prop, "unit")
    else:
        unit = ""
    if hasattr(prop, "uncertainty"):
        uncert = getattr(prop, "uncertainty")
    else:
        uncert = ""

    if uncert:
        print(f"{float(prop):.4} +- {float(uncert):.3} {unit}")
    else:
        print(f"{prop}")


def _echo_propertyCollection(rock, prop, plot):
    """Echos propertyCollection value.

    Parameters
    ==========
    rock : rocks.core.Rock
        The Rock instance.
    prop
        The attribute to print.
    """
    # TODO Add weighted average for floatParameters
    from rich import box
    from rich.table import Table
    from rich import print as rprint

    table = Table(
        header_style="bold blue",
        caption=f"({rock.number}) {rock.name}",
        box=box.SQUARE,
        footer_style="dim",
    )

    # Keys are table property names
    keys = [k for k in list(prop.__dict__.keys()) if k not in DONT_PRINT]

    for key in keys:
        table.add_column(key)

    if "diameters" in sys.argv:
        prop.preferred = prop.preferred_diameter
        prop_name = "diameter"
    elif "albedos" in sys.argv:
        prop.preferred = prop.preferred_albedo
        prop_name = "albedo"
    elif "masses" in sys.argv:
        prop_name = "mass"

    # Values are entries for each field
    for row in prop:
        table.add_row(
            *[str(getattr(row, key)) for key in keys],
            style="bold green"
            if hasattr(row, "preferred") and row.preferred
            else "white",
        )

    rprint(table)

    if plot:
        if any([p in sys.argv for p in ["-h", "--hist"]]):
            prop.hist(prop_name, show=True)
        if any([p in sys.argv for p in ["-s", "--scatter"]]):
            prop.scatter(prop_name, show=True)

    sys.exit()  # otherwise click prints Error


def _echo_listSameTyeParameter(prop):
    print(prop)


# ------
# Numerical methods
def weighted_average(observable, error):
    """Computes weighted average of observable.

    Parameters
    ==========
    observable : np.ndarray
        Float values of observable
    error : np.ndarray
        Corresponding errors of observable.

    Returns
    =======
    (float, float)
        Weighted average and its standard error.
    """

    # If no data was passed (happens when no preferred entry in table)
    if not observable:
        return (np.nan, np.nan)

    if len(observable) == 1:
        return (observable[0], error[0])

    if any([e == 0 for e in error]):
        weights = np.ones(observable.shape)
        warnings.warn("Encountered zero in errors array. Setting all weights to 1.")
    else:
        # Compute normalized weights
        weights = 1 / np.array(error) ** 2

    # Compute weighted average and uncertainty
    avg = np.average(observable, weights=weights)

    # Kirchner Case II
    # http://seismo.berkeley.edu/~kirchner/Toolkits/Toolkit_12.pdf
    var_avg = (
        len(observable)
        / (len(observable) - 1)
        * (
            sum(w * o ** 2 for w, o in zip(weights, observable)) / sum(weights)
            - avg ** 2
        )
    )
    std_avg = np.sqrt(var_avg / len(observable))
    return (avg, std_avg)


DONT_PRINT = [
    "num",
    "name",
    "id",
    "iddataset",
    "title",
    "url",
    "doi",
    "bibcode",
    "link",
    "datasetname",
    "idcollection",
    "selection",
    "source",
    "resourcename",
    "preferred",
    "preferred_albedo",
    "preferred_diameter",
    "_iter_index",
]
