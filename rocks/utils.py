#!/usr/bin/env python
"""Utility functions for rocks."""

from functools import reduce
import json
import os
import pickle
import re
import sys
import urllib
import warnings

import numpy as np
import requests
import rich
from rich import progress

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
def _build_index():
    """Build asteroid name-number index from ssoCard dump."""

    # Get all cards in data dump
    PATH_CARDS = os.path.join("/tmp/ssocards/")

    with open(os.path.join(PATH_CARDS, "ssocards.list"), "r") as file_:
        CARDS = [
            os.path.join(PATH_CARDS, path.split("store/")[-1])
            for path in file_.read().split()
        ]

    # Construct index from card content
    INDEX = {"name": {}, "number": {}, "id": {}, "reduced": {}}

    for card in progress.track(CARDS, total=len(CARDS), description="Building Index"):

        with open(card, "r") as file_:
            ssocard = json.load(file_)

        id_ = ssocard["id"]
        name = ssocard["name"]
        number = ssocard["number"] if ssocard["number"] else np.nan
        reduced = reduce_id(id_)

        INDEX["name"][name] = (number, id_)
        INDEX["number"][number] = (name, id_)
        INDEX["id"][id_] = (name, number)
        INDEX["reduced"][reduced] = (name, number, id_)

    with open(rocks.PATH_INDEX, "wb") as file_:
        pickle.dump(INDEX, file_, protocol=4)


def load_index():
    """Load local index of asteroid numbers, names, SsODNet IDs."""
    with open(rocks.PATH_INDEX, "rb") as ind:
        return pickle.load(ind)


def update_index():
    """Verify the names and numbers of asteroids in the name-number index."""

    INDEX = load_index()

    OLD_IDS = list(INDEX["id"].keys())
    OLD_IDS = set(id_ for id_ in OLD_IDS if not re.match(r"^[A-Za-z \(\)\_]*$", id_))
    NEW_IDS = rocks.identify(OLD_IDS, return_id=True, local=False, progress=True)

    for old_id, new_ids in zip(OLD_IDS, NEW_IDS):

        new_name, new_number, new_id = new_ids

        if old_id == new_id:
            continue

        # ------
        # Add new entry
        new_reduced = reduce_id(new_id)

        INDEX["name"][new_name] = (new_number, new_id)
        INDEX["number"][new_number] = (new_name, new_id)
        INDEX["id"][new_id] = (new_name, new_number)
        INDEX["reduced"][new_reduced] = (new_name, new_number, new_id)

        # ------
        # Remove old entry
        old_name, old_number = INDEX["id"][old_id]
        old_reduced = reduce_id(old_id)

        del INDEX["name"][old_name]
        del INDEX["number"][old_number]
        del INDEX["id"][old_id]
        del INDEX["reduced"][old_reduced]

    with open(rocks.PATH_INDEX, "wb") as file_:
        pickle.dump(INDEX, file_, protocol=4)


def retrieve_index():
    """Download the index of numbered asteroids from the rocks GitHub
    repository and saves it to the cache directory."""

    URL = "https://github.com/maxmahlke/rocks/blob/master/data/index.pkl?raw=True"

    index = pickle.load(urllib.request.urlopen(URL))

    with open(rocks.PATH_INDEX, "wb") as ind:
        pickle.dump(index, ind, protocol=4)


# ------
# ssoCard utility functions
def rgetattr(obj, attr):
    """Deep version of getattr. Retrieve nested attributes."""

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
        retrieve_json_from_ssodnet("units")

    with open(PATH_UNITS, "r") as units:
        units = json.load(units)

    try:
        for key in path_unit.split("."):
            units = units[key]
    except KeyError:
        unit = ""

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
def reduce_id(id_):
    """Reduce the SsODNet ID to a string with fewer free parameters."""
    return id_.replace("_(Asteroid)", "").replace("_", "").replace(" ", "").lower()


def retrieve_json_from_ssodnet(which):
    """Retrieve the ssoCard template, units, or descriptions from SsODNet.

    Parameters
    ----------
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

    if response.ok:
        ssoCard = response.json()

        with open(rocks.PATH_META[which], "w") as file_:
            json.dump(ssoCard, file_)

    else:
        warnings.warn(
            f"Retrieving metadata file '{which}' failed with url:\n"
            f"{URL_JSON[which]}"
        )


def cache_inventory():
    """Create lists of the cached ssoCards and datacloud catalogues.

    Returns
    -------
    list of tuple
        The SsODNet IDs and versions of the cached ssoCards.
    list of tuple
        The SsODNet IDs and names of the cached datacloud catalogues.
    """

    # Get all JSONs in cache
    cached_jsons = set(
        file_ for file_ in os.listdir(rocks.PATH_CACHE) if file_.endswith(".json")
    )

    cached_cards = []
    cached_catalogues = []

    for file_ in cached_jsons:

        if file_ in [os.path.basename(f) for f in rocks.PATH_META.values()]:
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

        # Likely an ssoCard, check the version
        ssodnet_id = os.path.splitext(file_)[0]

        with open(os.path.join(rocks.PATH_CACHE, file_), "r") as ssocard:
            card = json.load(ssocard)

            if card[ssodnet_id] is None:
                # Faulty card, remove it
                print(ssodnet_id)
                os.remove(os.path.join(rocks.PATH_CACHE, file_))
            else:
                cached_cards.append(
                    (
                        ssodnet_id,
                        card[ssodnet_id]["ssocard"]["version"],
                    )
                )
    return cached_cards, cached_catalogues


def clear_cache():
    """Remove the cached ssoCards, datacloud catalogues, and metadata files."""
    cards, catalogues = cache_inventory()

    for card in cards:
        PATH_CARD = os.path.join(rocks.PATH_CACHE, f"{card[0]}.json")
        os.remove(PATH_CARD)

    for catalogue in catalogues:
        PATH_CATALOGUE = os.path.join(rocks.PATH_CACHE, f"{'_'.join(catalogue)}.json")
        os.remove(PATH_CATALOGUE)

    for file_ in rocks.PATH_META.values():
        if os.path.isfile(file_):
            os.remove(file_)


def get_current_version():
    """Get the current version of ssoCards.

    Returns
    -------
    str
        The current version of ssoCards.

    Notes
    -----
    There will soon be a stub card online to check this. For now, we just check
    the version of Ceres.
    """

    URL = "https://ssp.imcce.fr/webservices/ssodnet/api/ssocard/Ceres"
    response = requests.get(URL)

    if response.ok:
        card = response.json()
    else:
        warnings.warn("Retrieving the current ssoCard version failed.")
        sys.exit()

    return card["Ceres"]["ssocard"]["version"]


def confirm_identity(ids):
    """Confirm the SsODNet ID of the passed identifier. Retrieve the current
    ssoCard and remove the former one if the ID has changed.

    Parameters
    ==========
    ids : list
        The list of SsODNet IDs to confirm.
    """

    # Drop the named asteroids - their identity won't change
    ids = set(id_ for id_ in ids if not re.match(r"^[A-Za-z \(\)\_]*$", id_))

    if len(ids) == 1:
        _, _, current_ids = rocks.identify(ids, return_id=True, local=False)
        current_ids = [current_ids]

    else:

        _, _, current_ids = zip(
            *rocks.identify(ids, return_id=True, local=False, progress=True)
        )

    # Swap the renamed ones
    updated = []

    for old_id, current_id in zip(ids, current_ids):

        if old_id == current_id:
            continue

        rich.print(f"{old_id} has been renamed to {current_id}. Swapping the ssoCards.")

        # Get new card and remove the old one
        rocks.ssodnet.get_ssocard(current_id, local=False)
        os.remove(os.path.join(rocks.PATH_CACHE, f"{old_id}.json"))

        # This is now up-to-date
        updated.append(old_id)

    for id_ in updated:
        ids.remove(id_)


def retrieve_rocks_version():
    """Retrieve the current rocks version from the GitHub repository."""

    URL = "https://github.com/maxmahlke/rocks/blob/master/pyproject.toml?raw=True"

    response = urllib.request.urlopen(URL).read().decode("utf-8")
    version = response.split("\n")[2].split('"')[1]

    return version


if __name__ == "__main__":
    _build_index()
