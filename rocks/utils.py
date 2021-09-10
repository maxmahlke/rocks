#!/usr/bin/env python
"""Utility functions for rocks."""

import json
import os
import pickle
import urllib
import warnings
from functools import reduce

import numpy as np
import pandas as pd
import requests

import rocks


# ------
# Simplify error messages
def warning_on_one_line(message, category, filename, lineno, file=None, line=None):
    if "rocks/" in filename:
        return f"rocks: {message}\n"
    else:
        return "%s:%s: %s: %s\n" % (filename, lineno, category.__name__, message)


warnings.formatwarning = warning_on_one_line

# ------
# Functions for the asteroid name-number index
def retrieve_index_from_repository():
    """Download the index of numbered asteroids from the rocks GitHub
    repository and saves it to the cache directory."""

    URL = "https://github.com/maxmahlke/rocks/blob/master/data/index.pkl?raw=True"

    index = pickle.load(urllib.request.urlopen(URL))

    with open(rocks.PATH_INDEX, "wb") as ind:
        pickle.dump(index, ind, protocol=4)


def update_index():
    """Update index of numbered SSOs using the MPC database.
    The index file in the cache directory is changed in-place.
    """
    print("Updating the asteroid name-number index..")

    # Get current index
    names, numbers, ids = read_index()

    # Get list of numbered asteroids from MPC
    url = "https://www.minorplanetcenter.net/iau/lists/NumberedMPs.txt"
    numbered = pd.read_fwf(url, colspecs=[(0, 7)], names=["number"])
    numbered = set(int(n.strip(" (")) for n in numbered.number)  # type: ignore

    # Compare list to index
    missing = set(numbers) ^ set(numbered)

    if not missing:
        return

    # Get ids of missing entries, append to index
    miss_names, miss_numbers, miss_ids = zip(*rocks.identify(missing, return_id=True))

    # Add the missing items to the index
    for name, number, id_ in zip(miss_names, miss_numbers, miss_ids):
        numbers[number] = (name, id_)
        names[name] = (number, id_)
        ids[id_] = (name, number)

    # And save to file
    with open(rocks.PATH_INDEX, "wb") as ind:
        pickle.dump([names, numbers, ids], ind, protocol=4)


def read_index():
    """Read local index of asteroid numbers, names, SsODNet IDs.

    Returns
    =======
    pd.DataFrame
        Asteroid index with three columns.
    """
    with open(rocks.PATH_INDEX, "rb") as ind:
        index = pickle.load(ind)

    # TODO: Switched from pd.DataFrame to dicts. Can remove this check in 2022.
    if isinstance(index, pd.DataFrame):
        raise TypeError(
            """The asteroid name-number index has been changed in version 1.3 to a
        simple dictionary to speed up the name resolution. Please delete the
        index file located at '$USER/.cache/rocks/index.pkl' and rerun your
        command."""
        )
    return index


# ------
# ssoCard utility functions
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
        print(
            "The ssoCard units not present in cache directory, retrieving them from SsODNet..\n"
        )
        retrieve_json_from_ssodnet("units")

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
    if not observable.size:
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


# ------
# Misc
def retrieve_json_from_ssodnet(which):
    """Retrieve the ssoCard template, units, or descriptions from SsODNet.

    Parameters
    ==========
    which : str
        The JSON file to download. Choose from ['template', 'units', 'description']

    """

    # Construct URL
    URL_BASE = "https://ssp.imcce.fr/webservices/ssodnet/api/ssocard/"

    URL_JSON = {
        "template": "templates/catalogue-template_aster-astorb.json",
        "units": "unit_aster-astorb.json",
        "description": "description_aster-astorb.json",
    }

    # Query and save to file
    response = requests.get("".join([URL_BASE, URL_JSON[which]]))

    PATH_JSON = {
        "template": "catalogue-template_aster-astorb.json",
        "units": "unit_aster-astorb.json",
        "description": "description_aster-astorb.json",
    }

    if response.ok:
        ssoCard = response.json()

        with open("".join([rocks.PATH_CACHE, PATH_JSON[which]]), "w") as file_:
            json.dump(ssoCard, file_)

    else:
        warnings.warn(f"Retrieving the ssoCard {which} failed with url:\n{URL}")
