"""Asteroid name-number index functions for rocks."""

from functools import lru_cache
import pickle
import pickletools
import re
import string
import sys
import typing
import time

import numpy as np
import rich
from rich import progress

from rocks import __version__
from rocks import config
from rocks import resolve


# ------
# Building the index
def _build_index():
    """Build asteroid name-number index from SsODNet sso_index."""

    tasks = [
        _build_index_of_aliases,
        _build_number_index,
        _build_name_index,
        _build_designation_index,
        _build_palomar_transit_index,
        _build_fuzzy_searchable_index,
    ]

    with progress.Progress(
        "[progress.description]{task.description}",
        progress.BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
    ) as progress_bar:

        steps = progress_bar.add_task("Building index", total=len(tasks) + 1)

        index = _retrieve_index_from_ssodnet()
        progress_bar.update(steps, advance=1)

        for task in tasks:
            task(index)
            progress_bar.update(steps, advance=1)


def _build_index_of_aliases(index):
    """Create the SsODNetID -> aliases index.

    Parameters
    ----------
    index : pd.DataFrame
        The formatted index from SsODNet.
    """

    aliases = dict(
        zip(index.SsODNetID, [aliases.split(";") for aliases in index.Aliases])
    )

    _write_to_cache(aliases, "aliases.pkl")


def _build_number_index(index):
    """Build the number -> name,SsODNetID index parts.

    Parameters
    ----------
    index : pd.DataFrame
        The formatted index from SsODNet.
    """

    SIZE = 1e3  # Build chunks of 1k entries

    # Find next 10,000 to largest number
    parts = np.arange(1, np.ceil(index.Number.max() / SIZE) * SIZE, SIZE, dtype=int)

    for part in parts:

        part_index = index.loc[(part <= index.Number) & (index.Number < part + SIZE)]

        part_index = dict(
            zip(
                part_index.Number,
                [[sso.Name, sso.SsODNetID] for _, sso in part_index.iterrows()],
            )
        )

        _write_to_cache(part_index, f"{part}.pkl")


def _build_name_index(index):
    """Build the reduced -> number,SsODNetID index.

    Parameters
    ----------
    index : pd.DataFrame
        The formatted index from SsODNet.
    """

    import pandas as pd

    parts = string.ascii_lowercase  # first character of name

    names = set(red for red in index.Reduced if re.match(r"^[a-z\'-]*$", red))
    names.add(r"g!kun||'homdima")  # everyone's favourite shell injection

    for part in parts:

        names_subset = set(name for name in names if name.startswith(part))

        if part == "a":
            names_subset.add(
                "'aylo'chaxnim"
            )  # another edge case for the daughter of venus
        part_index = index.loc[index.Reduced.isin(names_subset)]

        part_index = dict(
            zip(
                part_index.Reduced,
                [
                    [sso.Name, sso.SsODNetID]
                    if pd.isna(sso.Number)
                    else [sso.Name, sso.Number, sso.SsODNetID]
                    for _, sso in part_index.iterrows()
                ],
            )
        )

        _write_to_cache(part_index, f"{part}.pkl")


def _build_designation_index(index):
    """Build the designation -> name,number,SsODNetID index.

    Parameters
    ----------
    index : pd.DataFrame
        The formatted index from SsODNet.
    """

    designations = set(
        red
        for red in index.Reduced
        if re.match(
            r"(^([11][8-9][0-9]{2}[a-z]{2}[0-9]{0,3}$)|"
            r"(^20[0-9]{2}[a-z]{2}[0-9]{0,3}$))",
            red,
        )
    )
    max_year = max([int(year[2:4]) for year in designations if year.startswith("20")])
    parts = [
        "18",
        "19",
        *[f"20{year:02}" for year in range(0, max_year + 1)],
    ]

    for part in parts:

        part_designations = set(desi for desi in designations if desi.startswith(part))

        # Asteroids in this chunk
        part_index = index.loc[index.Reduced.isin(part_designations)]

        part_index = dict(
            zip(
                part_index.Reduced,
                [
                    [sso.Name, sso.SsODNetID]
                    if pd.isna(sso.Number)
                    else [sso.Name, sso.Number, sso.SsODNetID]
                    for _, sso in part_index.iterrows()
                ],
            )
        )

        _write_to_cache(part_index, f"d{part}.pkl")


def _build_palomar_transit_index(index):
    """Build the reduced -> name,number,SsODNetID index for anything that is not
    a name and not a designation.

    Parameters
    ----------
    index : pd.DataFrame
        The formatted index from SsODNet.
    """

    rest = set(
        red
        for red in index.Reduced
        if not re.match(
            r"(^([11][8-9][0-9]{2}[a-z]{2}[0-9]{0,3}$)|"
            r"(^20[0-9]{2}[a-z]{2}[0-9]{0,3}$))",
            red,
        )
        and not re.match(r"^[a-z\'-]*$", red)
    )

    part_index = index.loc[index.Reduced.isin(rest)]

    part_index = dict(
        zip(
            part_index.Reduced,
            [
                [sso.Name, sso.SsODNetID]
                if pd.isna(sso.Number)
                else [sso.Name, sso.Number, sso.SsODNetID]
                for _, sso in part_index.iterrows()
            ],
        )
    )

    _write_to_cache(part_index, "PLT.pkl")


def _build_fuzzy_searchable_index(index):
    """Merge name, number and SsODNet ID of all entries to fuzzy-searchable lines.

    Parameters
    ----------
    index : pd.DataFrame
        The formatted index from SsODNet.
    """

    LINES = []

    for _, row in index.sort_values(["Number", "Name"]).iterrows():

        number = f"({int(row.Number)})" if not pd.isna(row.Number) else ""
        name = row.Name

        LINE = (
            f"{number.ljust(9)} {name.ljust(20)}".encode(sys.getdefaultencoding())
            + b"\n"
        )

        LINES.append(LINE)

    _write_to_cache(LINES, "fuzzy_index.pkl")


def _write_to_cache(obj, filename):
    """Save the pickled object to the path in the rocks cache.

    Parameters
    ----------
    obj : any
        The python object to pickle.
    filename : str
        The output filename, relative to the index directory.
    """

    with open(config.PATH_INDEX / filename, "wb") as file_:
        obj_pickled = pickle.dumps(obj, protocol=4)
        file_.write(pickletools.optimize(obj_pickled))


# ------
# Retrieving the index
def _retrieve_index_from_ssodnet():
    """Download and format asteroid name-number index from SsODNet.

    Returns
    -------
    pd.DataFrame
        The formatted index.
    """

    # The gzipped index is exposed under this address
    URL_INDEX = "https://asterm.imcce.fr/public/ssodnet/sso_index.csv.gz"
    index = pd.read_csv(URL_INDEX)

    # There are some spurious spaces in the column headers
    index = index.rename(columns={c: c.replace(" ", "") for c in index.columns})

    # We use NaNs instead of 0 for unnumbered objects
    index.loc[index["Number"] == 0, "Number"] = np.nan
    index["Number"] = index["Number"].astype("Int64")

    return index


def get_aliases(ssodnetid):
    """Return the aliases of the passed reduced identifier.

    Parameters
    ----------
    ssodnetid :  str
        The SsODNetID of the asteroid to alias.

    Returns
    -------
    list
        The list of aliases of the asteroid.
    """
    return _load("aliases.pkl")[ssodnetid]


def _get_index_file(id_: typing.Union[int, str]) -> dict:
    """Get part of the index where id_ is located.

    Parameters
    ----------
    id_ : str, int
        The asteroid identifier.

    Returns
    -------
    dict
        Part of the index.
    """

    # Is it numeric?
    if isinstance(id_, int):
        index_range = np.arange(1, int(1e6), int(1e3))
        try:
            index_number = index_range[index_range <= id_][-1]
        # The passed id_ is larger than 1e6
        except IndexError:
            index_number = 1
        which = f"{index_number}.pkl"

    # Is it a name?
    elif re.match(r"^[a-z\'-]*$", id_) or id_ == r"g!kun||'homdima":

        if id_[0] == "'":  # catch 'aylo'chaxnim
            which = f"{id_[0]}.pkl"
        else:
            which = config.PATH_INDEX / f"{id_[0]}.pkl"

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
        which = f"d{year}.pkl"

    # Should be in this one then
    else:
        which = "PLT.pkl"
    return _load(which)


@lru_cache(None)
def _load(which):
    """Load a pickled index file."""
    if not (config.PATH_INDEX / which).exists():
        rich.print(
            "The asteroid name-number index is malformed. Run '$ rocks status' to update it."
        )
        sys.exit()

    with open(config.PATH_INDEX / which, "rb") as file_:
        return pickle.load(file_)


def get_modification_date():
    """Get modification date of index pickle files."""
    date_index = (config.PATH_INDEX / "1.pkl").stat().st_mtime
    return time.strftime("%d %b %Y", time.localtime(date_index))


def find_candidates(id_):
    """Identify possible matches among all asteroid names based on Levenshtein distance.

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
    from Levenshtein import distance

    # Get list of named asteroids
    index_ = {}

    for char in string.ascii_lowercase:
        idx = _get_index_file(char)
        index_ = {**index_, **idx}

    # Use Levenshtein distance to identify potential matches
    candidates = []
    max_distance = 1  # found by trial and error
    id_ = resolve._reduce_id_for_local(id_)

    for name in index_.keys():
        dist = distance(id_, name)

        if dist <= max_distance:
            candidates.append(index_[name][:-1])

    # Sort by number
    candidates = sorted(candidates, key=lambda x: x[1])
    return candidates


def _ensure_index_exists():
    """Ensure that the local index exists. Else, retrieve it."""

    GREETING = rf"""
                    _
                   | |
     _ __ ___   ___| | _____
    | '__/ _ \ / __| |/ / __|
    | | | (_) | (__|   <\__ \
    |_|  \___/ \___|_|\_\___/

    version: {__version__}
    cache:   {config.PATH_CACHE}

    It looks like this is the first time you run [green]rocks[/green].
    Some metadata is required to be present in the cache directory.
    [green]rocks[/green] will download it now.
    """

    if not config.PATH_INDEX.is_dir():

        # Cache directory is missing: first time running rocks
        if not config.PATH_CACHE.is_dir():

            rich.print(GREETING)
            config.PATH_CACHE.mkdir(parents=True)

        # Cache exists but index is missing
        else:
            rich.print(
                "Could not find the local asteroid name-number index. Downloading it now..."
            )

        _build_index()

        rich.print("\nAll done. Find out more by running [green]$ rocks docs[/green]\n")
