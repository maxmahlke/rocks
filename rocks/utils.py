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
    PATH_UNITS = os.path.join(rocks.PATH_CACHE, "unit_aster-astorb.json")

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


# ------
# Numerical methods
def weighted_average(catalogue, parameter):
    """Computes weighted average of observable.

    Parameters
    ==========
    observable : np.ndarray
        Float values of observable
    error : np.ndarray
        Corresponding errors of observable.

    Returns
    =======
    float
        The weighted average.

    float
        The standard error of the weighted average.
    """

    if parameter in ["albedo", "diameter"]:
        preferred = catalogue[f"preferred_{parameter}"]
    else:
        preferred = catalogue[f"preferred"]

    values = catalogue[parameter]
    errors = catalogue[f"err_{parameter}"]

    observable = np.array(values)[preferred]
    error = np.array(errors)[preferred]

    if all([np.isnan(value) for value in values]) or all(
        [np.isnan(error) for error in errors]
    ):
        warnings.warn(
            f"{self.name[0]}: The values or errors of property '{property_}' are all NaN. Average failed."
        )
        return np.nan, np.nan

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
    return avg, std_avg


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
        "template": "ssoCard_template.json",
        "units": "unit_aster-astorb.json",
        "description": "description_aster-astorb.json",
    }

    if response.ok:
        ssoCard = response.json()

        with open("/".join([rocks.PATH_CACHE, PATH_JSON[which]]), "w") as file_:
            json.dump(ssoCard, file_)

    else:
        warnings.warn(f"Retrieving the ssoCard {which} failed with url:\n{URL}")
