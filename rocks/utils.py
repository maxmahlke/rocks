#!/usr/bin/env python
"""Utility functions for rocks."""

from functools import reduce
import os
import pickle
import urllib
import warnings
import sys

import numpy as np
import pandas as pd
import requests
from tqdm import tqdm
import rich
from rich import progress
import ujson
import json

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


def __build_index():
    """Build asteroid name-number index from ssoCard dump."""

    # Get all cards in data dump
    PATH_CARDS = os.path.join(os.path.dirname(__file__), "../data/ssocards/")

    with open(os.path.join(PATH_CARDS, "ssocards.list"), "r") as file_:
        CARDS = [
            os.path.join(PATH_CARDS, path.split("store/")[-1])
            for path in file_.read().split()
        ]

    ids, names, numbers, reduced = {}, {}, {}, {}

    # Construct index from card content
    for card in tqdm(CARDS, total=len(CARDS), desc="Building Index"):

        with open(card, "r") as file_:
            ssocard = json.load(file_)

        id_ = ssocard["id"]
        name = ssocard["name"]
        number = ssocard["number"]
        id_reduced = id_.replace("_", "").lower()

        names[name] = (number, id_)
        numbers[number] = (name, id_)
        ids[id_] = (name, number)
        reduced[id_reduced] = (name, number, id_)

    with open("/tmp/new_index_cards.pkl", "wb") as ind:
        pickle.dump([names, numbers, ids, reduced], ind, protocol=4)


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

    # Smaller steps are less likely to overload SsODNet
    steps = 100

    # Identify the asteroids by in parts
    for subset in tqdm(
        np.array_split(numbered, steps), total=steps, desc="Building Index"
    ):

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
        units = ujson.load(units)

    for key in path_unit.split("."):
        units = units[key]

    return units


def update_cards(ids):
    """Update the cached ssoCards of the passed ids.

    Parameters
    ==========
    ids : list
        List of SsODNet IDs of ssoCards to update.
    """
    n_subsets = 20 if len(ids) > 1000 else 1

    for subset in progress.track(
        np.array_split(np.array(ids), n_subsets),
        description="Updating ssoCards : ",
    ):
        rocks.ssodnet.get_ssocard(subset, progress=False, no_cache=True)


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
            ujson.dump(ssoCard, file_)

    else:
        warnings.warn(
            f"Retrieving the ssoCard {which} failed with url:\n{URL_JSON[which]}"
        )


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
            card = ujson.load(ssocard)

            if card[ssodnet_id] is None:
                cached_cards.append((ssodnet_id, "Failed"))
            else:
                cached_cards.append(
                    (ssodnet_id, card[ssodnet_id]["ssocard"]["version"])
                )

    return cached_cards, cached_catalogues


def get_current_version():
    """Get the current version of ssoCards.

    Returns
    =======
    str
        The current version of ssoCards.

    Notes
    =====
    There will soon be a stub card online to check this. For now, we just check
    the version of Ceres.

    This function should be extended once datacoud catalogues have versions as well.
    """

    URL = "https://ssp.imcce.fr/webservices/ssodnet/api/ssocard/Ceres"
    response = requests.get(URL)

    if response.ok:
        card_ceres = response.json()
    else:
        warnings.warn("Retrieving the current ssoCard version failed.")
        print(response)
        sys.exit()

    return card_ceres["Ceres"]["ssocard"]["version"]


def confirm_identify(ids):
    """Confirm the SsODNet ID of the passed identifier. Retrieve the current
    ssoCard and remove the former one if the ID has changed.

    Parameters
    ==========
    ids : list
        The list of SsODNet IDs to confirm.
    """
    if len(ids) == 1:
        _, _, current_ids = rocks.identify(ids, return_id=True, local=False)
        current_ids = [current_ids]

    else:

        _, _, current_ids = zip(*rocks.identify(ids, return_id=True, local=False))

    # Swap the renamed ones
    updated = []

    for old_id, current_id in zip(ids, current_ids):

        if old_id == current_id:
            continue

        rich.print(f"{old_id} has been renamed to {current_id}. Swapping the ssoCards.")

        # Get new card and remove the old one
        rocks.ssodnet.get_ssocard(current_id, no_cache=True)
        os.remove(os.path.join(rocks.PATH_CACHE, f"{old_id}.json"))

        # This is now up-to-date
        updated.append(old_id)

    for id_ in updated:
        ids.remove(id_)

    # Update the outdated ones
    rich.print(
        f"\n{len(ids)} ssoCards {'is' if len(ids) == 1 else 'are'} out-of-date.",
        end=" ",
    )


def update_datacloud_catalogues(ids_catalogues):
    """Update the datacloud catalogues in the cache directory.

    Parameters
    ==========
    ids_catalogues : list of tuple
        The SsODNet IDs and catalogue names to update.
    """
    for catalogue in set([cat for _, cat in ids_catalogues]):
        ids = [id_ for id_, cat in ids_catalogues if cat == catalogue]

        n_subsets = 20 if len(ids) > 1000 else 1

        for subset in progress.track(
            np.array_split(np.array(ids), n_subsets),
            description=f"{catalogue:<12} : ",
        ):
            rocks.ssodnet.get_datacloud_catalogue(
                subset, catalogue, progress=False, no_cache=True
            )


if __name__ == "__main__":
    __build_index()
