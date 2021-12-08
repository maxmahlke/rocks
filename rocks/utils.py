#!/usr/bin/env python
"""Utility functions for rocks."""

from functools import reduce
import json
import os
import pickle
import pickletools
import re
import warnings

import numpy as np
import Levenshtein as lev
import pandas as pd
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
    """Build asteroid name-number index from SsODNet sso_index."""

    # The gzipped index is exposed under this address
    URL_INDEX = "https://asterm.imcce.fr/public/ssodnet/sso_index.csv.gz"
    index_ssodnet = pd.read_csv(URL_INDEX)

    # There are some spurious spaces in the column headers
    index_ssodnet = index_ssodnet.rename(
        columns={c: c.replace(" ", "") for c in index_ssodnet.columns}
    )

    # We use NaNs instead of 0 for unnumbered objects
    index_ssodnet.loc[index_ssodnet["Number"] == 0, "Number"] = np.nan

    # Reformat the index to a dictionary
    index_ssodnet = (
        index_ssodnet.drop(columns="Type")
        .set_index("SsODNetID")
        .to_dict(orient="index")
    )

    INDEX = {"number": {}, "reduced": {}}

    for id_, values in progress.track(
        index_ssodnet.items(),
        total=len(index_ssodnet),
        description="Building Index",
    ):

        name = values["Name"]
        number = values["Number"]
        reduced = reduce_id(id_)

        if not np.isnan(number):
            number = int(number)

        INDEX["reduced"][reduced] = (name, number, id_)

        if not np.isnan(number):
            INDEX["number"][number] = (name, id_)

    with open(rocks.PATH_INDEX, "wb") as file_:
        index_pickled = pickle.dumps(INDEX, protocol=4)
        index_pickled_opt = pickletools.optimize(index_pickled)
        file_.write(index_pickled_opt)


def load_index():
    """Load local index of asteroid numbers, names, SsODNet IDs."""
    with open(rocks.PATH_INDEX, "rb") as ind:
        return pickle.load(ind)


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
    if not os.path.isfile(rocks.PATH_META["units"]):
        retrieve_json_from_ssodnet("units")

    with open(rocks.PATH_META["units"], "r") as units:
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

    values = catalogue[parameter]

    if parameter in ["albedo", "diameter"]:
        preferred = catalogue[f"preferred_{parameter}"]
        errors = catalogue[f"err_{parameter}_up"]
    else:
        preferred = catalogue["preferred"]
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
    """Retrieve the ssoCard units, or descriptions from SsODNet.

    Parameters
    ----------
    which : str
        The JSON file to download. Choose from ['units', 'description']
    """

    # Construct URL
    URL_BASE = "https://ssp.imcce.fr/webservices/ssodnet/api/ssocard/"

    URL_JSON = {
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
    list of str
        The cached metadata files.
    """

    # Get all JSONs in cache
    cached_jsons = set(
        file_ for file_ in os.listdir(rocks.PATH_CACHE) if file_.endswith(".json")
    )

    cached_cards = []
    cached_catalogues = []

    for file_ in cached_jsons:

        # Is it metadata?
        if file_ in [os.path.basename(f) for f in rocks.PATH_META.values()]:
            continue

        # Datacloud catalogue or ssoCard?
        if any(
            [
                cat["ssodnet_name"] in file_
                for cat in rocks.datacloud.CATALOGUES.values()
            ]
        ):
            ssodnet_id = "_".join(file_.split("_")[:-1])
            catalogue = os.path.splitext(file_)[0].split("_")[-1]
        else:
            ssodnet_id = os.path.splitext(file_)[0]
            catalogue = ""
        # Is it valid?
        with open(os.path.join(rocks.PATH_CACHE, file_), "r") as ssocard:

            card = json.load(ssocard)

            if not card:
                # Empty card or catalogue, remove it
                os.remove(os.path.join(rocks.PATH_CACHE, file_))
                continue

            if not catalogue:
                if card[ssodnet_id] is None:
                    # Faulty card, remove it
                    os.remove(os.path.join(rocks.PATH_CACHE, file_))
                    continue

        # Append to inventory
        if catalogue:
            cached_catalogues.append((ssodnet_id, catalogue))
        else:
            cached_cards.append(ssodnet_id)

    # Get cached metadata files
    cached_meta = [
        os.path.basename(f) for f in rocks.PATH_META.values() if os.path.isfile(f)
    ]
    return cached_cards, cached_catalogues, cached_meta


def clear_cache():
    """Remove the cached ssoCards, datacloud catalogues, and metadata files."""
    cards, catalogues, _ = cache_inventory()

    for card in cards:
        PATH_CARD = os.path.join(rocks.PATH_CACHE, f"{card}.json")
        os.remove(PATH_CARD)

    for catalogue in catalogues:
        PATH_CATALOGUE = os.path.join(rocks.PATH_CACHE, f"{'_'.join(catalogue)}.json")
        os.remove(PATH_CATALOGUE)

    for file_ in rocks.PATH_META.values():
        if os.path.isfile(file_):
            os.remove(file_)


def update_datacloud_catalogues(cached_catalogues):
    for catalogue in set(catalogues[1] for catalogues in cached_catalogues):

        ids = [id_ for id_, cat in cached_catalogues if cat == catalogue]

        rocks.ssodnet.get_datacloud_catalogue(
            ids, catalogue, local=False, progress=True
        )


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

    if not ids:
        return  # nothing to do here
    elif len(ids) == 1:
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

    try:
        response = requests.get(URL, timeout=10)
    except requests.exceptions.ReadTimeout:
        version = ""
    finally:
        if response.status_code == 200:
            version = re.findall(r"\d\.\d\.?\d?", response.text)[0]
        else:
            version = ""

    return version


def find_candidates(id_):
    """Propose a match among the named asteroids for the pass id_.

    Parameters
    ----------
    id_ : str
        The user-provided asteroid identifier.

    Returns
    -------
    list of tuple
        The name-number pairs of possible matches.

    Notes
    -----
    The matches are found using the Levenshtein distance metric.
    """

    # Get list of named asteroids
    index = load_index()

    # Use Levenshtein distance to identify potential matches
    candidates = []
    max_distance = 1  # found by trial and error
    id_ = id_.capitalize()  # remove one possible dof

    for name in index["name"].keys():
        distance = lev.distance(id_, name)

        if distance <= max_distance:
            candidates.append((name, index["name"][name][0]))

    # Sort by number
    candidates = sorted(candidates, key=lambda x: x[1])
    return candidates
