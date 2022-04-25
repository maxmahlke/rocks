#!/usr/bin/env python
"""Asteroid name-number index functions for rocks."""

import pickle
import pickletools
import re
import string
import typing

import numpy as np
import pandas as pd
from rich import progress

import rocks

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

    Returns
    -------

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


def _write_to_cache(obj, filename):
    """Save the pickled object to the path in the rocks cache.

    Parameters
    ----------
    obj : any
        The python object to pickle.
    filename : str
        The output filename, relative to the index directory.
    """

    with open(rocks.PATH_INDEX / filename, "wb") as file_:
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
    with open(rocks.PATH_INDEX / "aliases.pkl", "rb") as ind:
        return pickle.load(ind)[ssodnetid]


def get_index_file(id_: typing.Union[int, str]) -> dict:
    """Get absolute path to the index chunk where id_ is located.

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

        if id_[0] == "'":  # catch 'aylo'chaxnim
            path = rocks.PATH_INDEX / "a.pkl"
        else:
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
        path = rocks.PATH_INDEX / f"d{year}.pkl"

    # Should be in this one then
    else:
        path = rocks.PATH_INDEX / "PLT.pkl"

    if not path in rocks.INDEX:
        with open(path, "rb") as ind:
            rocks.INDEX[path] = pickle.load(ind)

    return rocks.INDEX[path]
