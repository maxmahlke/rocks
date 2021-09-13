#!/usr/bin/env python
"""Utility functions for rocks."""

from functools import reduce
import json
import os
import pickle
import urllib
import warnings

import numpy as np
import pandas as pd
import requests
from tqdm import tqdm

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


def create_index():
    """Create the asteroid name-number index using the list of numbered minor planets
    from the MPC and quaero.

    Notes
    =====
    The index file in the cache directory is changed in-place.
    """

    # Get list of numbered asteroids from MPC
    url = "https://www.minorplanetcenter.net/iau/lists/NumberedMPs.txt"
    numbered = pd.read_fwf(url, colspecs=[(0, 7)], names=["number"])
    numbered = np.array([int(n.strip(" (")) for n in numbered.number])  # type: ignore

    # These are problem cases that we take care of by hand
    numbered = np.setdiff1d(numbered, [1978, 1979, 1986, 1988, 1989, 1990])

    # Instantiate the index with some information pre-filled
    names = {
        "Patrice": (1978, "Patrice"),
        "Sakharov": (1979, "Sakharov"),
        "Plaut": (1986, "Plaut"),
        "Delores": (1988, "Delores"),
        "Tatry": (1989, "Tatry"),
        "Pilcher": (1990, "Pilcher"),
    }

    numbers = {number: (name, id_) for name, (number, id_) in names.items()}
    ids = {id_: (name, number) for name, (number, id_) in names.items()}

    # Identify the asteroids by in parts
    for subset in tqdm(np.array_split(numbered, 100), total=100, desc="Building Index"):

        subset_identified = rocks.identify(
            subset, return_id=True, progress=False, local=False
        )

        names.update({name: (number, id_) for name, number, id_ in subset_identified})
        numbers.update({number: (name, id_) for name, number, id_ in subset_identified})
        ids.update({id_: (name, number) for name, number, id_ in subset_identified})

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
        dictionary to speed up the name resolution. Please delete the index file
        located at '$USER/.cache/rocks/index.pkl' and rerun your command."""
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
        preferred = catalogue["preferred"]

    values = catalogue[parameter]
    errors = catalogue[f"err_{parameter}"]

    observable = np.array(values)[preferred]
    error = np.array(errors)[preferred]

    if all([np.isnan(value) for value in values]) or all(
        [np.isnan(error) for error in errors]
    ):
        warnings.warn(
            f"{catalogue.name[0]}: The values or errors of property '{parameter}' are all NaN. Average failed."
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


def cache_inventory():
    """Create lists of the cached ssoCards and datacloud catalogues.

    Returns
    =======
    list of tuple
        The SsODNet IDs and versions of the cached ssoCards.
    list of tuple
        The SsODNet IDs and names of the cached datacloud catalogues.
    """
    cached_cards = []
    cached_catalogues = []

    # Get all jsons in cache
    cached_jsons = set(
        file_ for file_ in os.listdir(rocks.PATH_CACHE) if file_.endswith(".json")
    )

    for file_ in cached_jsons:

        if file_ in [
            "ssoCard_template.json",
            "unit_aster-astorb.json",
            "description_aster-astorb.json",
        ]:
            continue

        # Datacloud catalogue?
        if any(
            [
                cat["ssodnet_name"] in file_
                for cat in rocks.datacloud.CATALOGUES.values()
            ]
        ):

            ssodnet_id = "_".join(file_.split("_")[:-1])
            catalogue = os.path.splitext(file_)[0].split("_")[-1]

            cached_catalogues.append((ssodnet_id, catalogue))
            continue

        # Likely an ssocard, check the version
        ssodnet_id = os.path.splitext(file_)[0]

        with open(os.path.join(rocks.PATH_CACHE, file_), "r") as ssocard:
            card = json.load(ssocard)

            if card[ssodnet_id] is None:
                cached_cards.append((ssodnet_id, "Failed"))
            else:
                cached_cards.append(
                    (ssodnet_id, card[ssodnet_id]["ssocard"]["version"])
                )

    return cached_cards, cached_catalogues
