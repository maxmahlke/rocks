#!/usr/bin/env python
"""Utility functions for rocks."""

import copy
from functools import reduce
import json
import pickle
import pickletools
import re
import string
import typing
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
    index_ssodnet.drop(columns=["Type", "Aliases", "Reduced"])
    index_ssodnet["Number"] = index_ssodnet["Number"].astype("Int64")

    # ------
    # Split index into chunks

    # Numbers
    step = 1e3  # Build chunks of 1k entries
    number_max = (
        np.ceil(index_ssodnet.Number.max() / step) * step
    )  # Find next 10,000 to largest number
    number_chunks = np.arange(1, number_max, step, dtype=int)

    # Names
    name_chunks = string.ascii_lowercase  # first character of name

    # Designation
    designations = set(
        red
        for red in index_ssodnet.Reduced
        if re.match(
            r"(^([11][8-9][0-9]{2}[a-z]{2}[0-9]{0,3}$)|"
            r"(^20[0-9]{2}[a-z]{2}[0-9]{0,3}$))",
            red,
        )
    )
    max_year = max([int(year[2:4]) for year in designations if year.startswith("20")])
    designation_chunks = [
        "18",
        "19",
        *[f"20{year:02}" for year in range(0, max_year)],
    ]

    with progress.Progress() as progress_bar:
        ntasks = len(number_chunks) + len(name_chunks) + len(designation_chunks)
        +1  # +1 for the rest
        task = progress_bar.add_task("Building index", total=ntasks)

        # Create number index chunks
        for number_min in number_chunks:

            index_chunk = {}

            # Asteroids in this chunk
            asts = index_ssodnet.loc[
                (number_min <= index_ssodnet.Number)
                & (index_ssodnet.Number < number_min + step)
            ]

            for _, ast in asts.iterrows():

                index_chunk[ast.Number] = [ast.Name, ast.SsODNetID]

            with open(rocks.PATH_INDEX / f"{number_min}.pkl", "wb") as file_:
                index_pickled = pickle.dumps(index_chunk, protocol=4)
                index_pickled_opt = pickletools.optimize(index_pickled)
                file_.write(index_pickled_opt)
            progress_bar.update(task, advance=1)

        # -----
        # Reduced

        # Names
        names = set(
            red for red in index_ssodnet.Reduced if re.match(r"^[a-z\'-]*$", red)
        )
        names.add(r"g!kun||'homdima")  # everyone's favourite shell injection

        # Create name index chunks
        for char in name_chunks:

            index_chunk = {}

            names_subset = set(name for name in names if name.startswith(char))

            # Asteroids in this chunk
            asts = index_ssodnet.loc[index_ssodnet.Reduced.isin(names_subset)]

            for _, ast in asts.iterrows():

                if pd.isna(ast.Number):
                    index_chunk[ast.Reduced] = [ast.Name, ast.SsODNetID]
                else:
                    index_chunk[ast.Reduced] = [ast.Name, ast.Number, ast.SsODNetID]

            with open(rocks.PATH_INDEX / f"{char}.pkl", "wb") as file_:
                index_pickled = pickle.dumps(index_chunk, protocol=4)
                index_pickled_opt = pickletools.optimize(index_pickled)
                file_.write(index_pickled_opt)

            progress_bar.update(task, advance=1)
        # Designations

        # Create designation index chunks
        for year in designation_chunks:

            index_chunk = {}

            designations_subset = set(
                desi for desi in designations if desi.startswith(year)
            )

            # Asteroids in this chunk
            asts = index_ssodnet.loc[index_ssodnet.Reduced.isin(designations_subset)]

            for _, ast in asts.iterrows():

                if pd.isna(ast.Number):
                    index_chunk[ast.Reduced] = [ast.Name, ast.SsODNetID]
                else:
                    index_chunk[ast.Reduced] = [ast.Name, ast.Number, ast.SsODNetID]

            with open(rocks.PATH_INDEX / f"{year}.pkl", "wb") as file_:
                index_pickled = pickle.dumps(index_chunk, protocol=4)
                index_pickled_opt = pickletools.optimize(index_pickled)
                file_.write(index_pickled_opt)

            progress_bar.update(task, advance=1)
        # And the rest
        rest = set(
            red
            for red in index_ssodnet.Reduced
            if red not in names and red not in designations
        )

        index_chunk = {}

        # Asteroids in this chunk
        asts = index_ssodnet.loc[index_ssodnet.Reduced.isin(rest)]

        for _, ast in asts.iterrows():

            if pd.isna(ast.Number):
                index_chunk[ast.Reduced] = [ast.Name, ast.SsODNetID]
            else:
                index_chunk[ast.Reduced] = [ast.Name, ast.Number, ast.SsODNetID]

        with open(rocks.PATH_INDEX / f"PLT.pkl", "wb") as file_:
            index_pickled = pickle.dumps(index_chunk, protocol=4)
            index_pickled_opt = pickletools.optimize(index_pickled)
            file_.write(index_pickled_opt)

        progress_bar.update(task, advance=1)


def get_index_file(id_: typing.Union[int, str]) -> dict:
    """Get absolute path to the index chunk where id_ should be located it.

    Parameters
    ----------
    id_ : str, int
        The asteroid identifier.

    Returns
    -------
    str
        The absolute path to the index chunk.
    """

    # Is it numeric?
    if isinstance(id_, int):
        index_range = np.arange(1, int(1e6), int(1e3))
        try:
            index_number = index_range[index_range <= id_][-1]
        # The passed id_ is larger than 1e6
        except IndexError:
            index_number = 1
        path = rocks.PATH_INDEX / f"{index_number}.pkl"

    # Is it a name?
    elif re.match(r"^[a-z\'-]*$", id_) or id_ == r"g!kun||'homdima":
        path = rocks.PATH_INDEX / f"{id_[0]}.pkl"

    # Is it a designation?
    elif re.match(
        r"(^([11][8-9][0-9]{2}[a-z]{2}[0-9]{0,3}$)|"
        r"(^20[0-9]{2}[a-z]{2}[0-9]{0,3}$))",
        id_,
    ):
        if id_.startswith("20"):
            year = f"20{id_[2:4]}"
        else:
            year = id_[:2]
        path = rocks.PATH_INDEX / f"{year}.pkl"

    # Should be in this one then
    else:
        path = rocks.PATH_INDEX / f"PLT.pkl"

    if not path in rocks.INDEX:
        with open(path, "rb") as ind:
            rocks.INDEX[path] = pickle.load(ind)
    return rocks.INDEX[path]


# ------
# ssoCard utility functions
def rgetattr(obj, attr):
    """Deep version of getattr. Retrieve nested attributes."""

    def _getattr(obj, attr):
        return getattr(obj, attr)

    return reduce(_getattr, [obj] + attr.split("."))


def get_unit(path_unit: str) -> str:
    """Get unit from units JSON file.

    Parameters
    ----------
    path_unit : str
        Path to the parameter in the JSON tree, starting at unit and
        separating the levels with periods.

    Returns
    -------
    str
        The unit of the requested parameter.
    """
    if not rocks.PATH_META["units"].is_file():
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
    ----------
    observable : np.ndarray
        Float values of observable
    error : np.ndarray
        Corresponding errors of observable.

    Returns
    -------
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
    cached_jsons = set(file_ for file_ in rocks.PATH_CACHE.glob("*.json"))

    cached_cards = []
    cached_catalogues = []

    for file_ in cached_jsons:

        # Is it metadata?
        if file_ in rocks.PATH_META.values():
            continue

        # Datacloud catalogue or ssoCard?
        if any(
            [
                cat["ssodnet_name"] in str(file_)
                for cat in rocks.datacloud.CATALOGUES.values()
            ]
        ):
            *ssodnet_id, catalogue = file_.stem.split("_")
            ssodnet_id = "_".join(ssodnet_id)
        else:
            ssodnet_id = file_.stem
            catalogue = ""

        # Is it valid?
        with open(file_, "r") as ssocard:

            card = json.load(ssocard)

            if not card:
                # Empty card or catalogue, remove it
                file_.unlink()
                continue

            if not catalogue:
                if card[ssodnet_id] is None:
                    # Faulty card, remove it
                    file_.unlink()
                    continue

        # Append to inventory
        if catalogue:
            cached_catalogues.append((ssodnet_id, catalogue))
        else:
            cached_cards.append(ssodnet_id)

    # Get cached metadata files
    cached_meta = [f.stem for f in rocks.PATH_META.values() if f.is_file()]
    return cached_cards, cached_catalogues, cached_meta


def clear_cache():
    """Remove the cached ssoCards, datacloud catalogues, and metadata files."""
    cards, catalogues, _ = cache_inventory()

    for card in cards:
        PATH_CARD = rocks.PATH_CACHE / f"{card}.json"
        PATH_CARD.unlink()

    for catalogue in catalogues:
        PATH_CATALOGUE = rocks.PATH_CACHE / f"{'_'.join(catalogue)}.json"
        PATH_CATALOGUE.unlink()

    for file_ in rocks.PATH_META.values():
        if file_.is_file():
            file_.unlink()


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
    ----------
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
        (rocks.PATH_CACHE / f"{old_id}.json").unlink()

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
    index = {}

    for char in string.ascii_lowercase:
        idx = get_index_file(char)
        index = {**index, **idx}

    # Use Levenshtein distance to identify potential matches
    candidates = []
    max_distance = 1  # found by trial and error
    id_ = reduce_id(id_)

    for name in index.keys():
        distance = lev.distance(id_, name)

        if distance <= max_distance:
            candidates.append(index[name][:-1])

    # Sort by number
    candidates = sorted(candidates, key=lambda x: x[1])
    return candidates


def list_candidate_ssos(id_):
    # The query failed. Propose some names if the id_ looks like a name,
    # designations give too many false positives
    if not re.match(r"^[A-Za-z ]*$", id_):
        return

    candidates = rocks.utils.find_candidates(id_)

    if candidates:
        rich.print(
            f"\nCould {'this' if len(candidates) == 1 else 'these'} be the "
            f"{'rock' if len(candidates) == 1 else 'rocks'} you're looking for?"
        )

        for name, number in candidates:
            rich.print(f"{f'({number})':>8} {name}")
