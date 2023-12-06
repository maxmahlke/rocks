"""Asteroid name-number index functions for rocks."""

from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache
import multiprocessing
import pickle
import pickletools
import re
import string
import sys
import typing
import time

import numpy as np
import rich
from rich import console, progress
from rich.prompt import Confirm

from rocks import __version__
from rocks import config
from rocks import resolve
from rocks.logging import logger


# ------
# Building the index
def _build_index():
    """Build asteroid name-number index from SsODNet sso_index."""

    config.PATH_INDEX.mkdir(exist_ok=True, parents=True)

    tasks_descs = [
        (_build_fuzzy_searchable_index, f"[dim]{'Differentiating Parent Bodies':>36}"),
        (_build_number_index, f"[dim]{'Gardening Regolith':>36}"),
        (_build_name_index, f"[dim]{'Clearing out Resonances':>36}"),
        (_build_designation_index, f"[dim]{'Populating near-Earth Space':>36}"),
        (_build_palomar_transit_index, f"[dim]{'Separating Trojans':>36}"),
    ]

    # ------
    # Retrieve index while showing spinner
    c = console.Console()
    with c.status("Searching for minor bodies...", spinner="dots8Bit"):
        index = _retrieve_index_from_ssodnet()

    # ------
    # Process index with multiple process
    N_WORKERS = 5  # number of processes to launch

    with progress.Progress(
        "[progress.description]{task.description}",
        progress.BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
    ) as pbar:
        futures = []

        with multiprocessing.Manager() as manager:
            _progress = manager.dict()
            overall_progress_task = pbar.add_task(
                f"Processing {len(index):,} minor bodies..."
            )

            with ProcessPoolExecutor(max_workers=N_WORKERS) as executor:
                for task, desc in tasks_descs:  # iterate over the jobs we need to run
                    task_id = pbar.add_task(desc, visible=True)
                    futures.append(executor.submit(task, index, _progress, task_id))

                # monitor the progress
                n_finished = 0
                while n_finished < len(futures):
                    # Update overall bar
                    pbar.update(
                        overall_progress_task, completed=n_finished, total=len(futures)
                    )
                    for task_id, update_data in _progress.items():
                        latest = update_data["progress"]
                        total = update_data["total"]

                        # update the progress bar for task
                        pbar.update(
                            task_id,
                            completed=latest,
                            total=total,
                            visible=latest < total,
                        )
                    # see if we're done
                    n_finished = sum([future.done() for future in futures])

                # raise any errors:
                for future in futures:
                    future.result()

            pbar.update(
                overall_progress_task,
                completed=len(futures),
                total=len(futures),
                description="All done!",
            )


def _build_number_index(index, pbar, task_id):
    """Build the number -> name,SsODNetID index parts.

    Parameters
    ----------
    index : pd.DataFrame
        The formatted index from SsODNet.
    """

    import pandas as pd

    SIZE = 1e3  # Build chunks of 1k entries

    # Find next 10,000 to largest number
    numbered = index[~pd.isna(index.Number)]
    parts = np.arange(1, np.ceil(numbered.Number.max() / SIZE) * SIZE, SIZE, dtype=int)
    pbar[task_id] = {"progress": 0, "total": len(parts)}

    for i, part in enumerate(parts):
        part_index = numbered.loc[
            (part <= numbered.Number) & (numbered.Number < part + SIZE)
        ]

        part_index = dict(
            zip(
                part_index.Number,
                part_index[["Name", "SsODNetID"]].to_numpy().tolist(),
            )
        )

        _write_to_cache(part_index, f"{part}.pkl")

        pbar[task_id] = {"progress": i + 1, "total": len(parts)}


def _build_name_index(index, pbar, task_id):
    """Build the reduced -> number,SsODNetID index.

    Parameters
    ----------
    index : pd.DataFrame
        The formatted index from SsODNet.
    """

    import pandas as pd

    parts = string.ascii_lowercase  # first character of name
    pbar[task_id] = {"progress": 0, "total": len(parts)}

    index = index[~pd.isna(index.Number)]

    names = set(red for red in index.Reduced if re.match(r"^[a-z\'-]*$", red))
    names.add(r"g!kun||'homdima")  # everyone's favourite shell injection

    for i, part in enumerate(parts):
        names_subset = set(name for name in names if name.startswith(part))

        if part == "a":
            names_subset.add(
                "'aylo'chaxnim"
            )  # another edge case for the daughter of venus
        part_index = index.loc[index.Reduced.isin(names_subset)]
        part_index = dict(
            zip(
                part_index.Reduced,
                part_index[["Name", "Number", "SsODNetID"]].to_numpy().tolist(),
            )
        )

        _write_to_cache(part_index, f"{part}.pkl")
        pbar[task_id] = {"progress": i + 1, "total": len(parts)}


def _build_designation_index(index, pbar, task_id):
    """Build the designation -> name,number,SsODNetID index.

    Parameters
    ----------
    index : pd.DataFrame
        The formatted index from SsODNet.
    """
    import pandas as pd

    def _convert_part(part, part_index):
        no_number = pd.isna(part_index.Number)
        has_number = part_index[~no_number]
        no_number = part_index[no_number]

        part_index = dict(
            zip(
                has_number.Reduced,
                has_number[["Name", "Number", "SsODNetID"]].values.tolist(),
            )
        )

        part_index.update(
            zip(
                no_number.Reduced,
                no_number[["Name", "SsODNetID"]].values.tolist(),
            )
        )

        _write_to_cache(part_index, f"d{part}.pkl")

    designations = set(
        red
        for red in index.Reduced
        if re.match(
            r"(^([11][8-9][0-9]{2}[a-z]{2}[0-9]{0,3}$)|"
            r"(^20[0-9]{2}[a-z]{2}[0-9]{0,3}$))",
            red,
        )
    )

    index = index[index.Reduced.isin(designations)]

    # treat 18xx and 19xx separately
    part_18 = index.Reduced.str.startswith("18")
    pbar[task_id] = {"progress": 1, "total": 26}
    part_19 = index.Reduced.str.startswith("19")
    pbar[task_id] = {"progress": 2, "total": 26}

    _convert_part("18", index[part_18])
    _convert_part("19", index[part_19])

    index = index[(~part_18) & (~part_19)]

    # now divide by year
    index["parts"] = index.Reduced.str[:4]
    for i, (part, part_index) in enumerate(index.groupby("parts")):
        _convert_part(part, part_index)
        pbar[task_id] = {"progress": i + 3, "total": 26}


def _build_palomar_transit_index(index, pbar, task_id):
    """Build the reduced -> name,number,SsODNetID index for anything that is not
    a name and not a designation.

    Parameters
    ----------
    index : pd.DataFrame
        The formatted index from SsODNet.
    """

    import pandas as pd

    pbar[task_id] = {"progress": 1, "total": 2}
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

    no_number = pd.isna(part_index.Number)
    has_number = part_index[~no_number]
    no_number = part_index[no_number]

    part_index = dict(
        zip(
            has_number.Reduced,
            has_number[["Name", "Number", "SsODNetID"]].to_numpy().tolist(),
        )
    )

    part_index.update(
        zip(
            no_number.Reduced,
            no_number[["Name", "SsODNetID"]].to_numpy().tolist(),
        )
    )

    _write_to_cache(part_index, "PLT.pkl")
    pbar[task_id] = {"progress": 2, "total": 2}


def _build_fuzzy_searchable_index(index, pbar, task_id):
    """Merge name, number and SsODNet ID of all entries to fuzzy-searchable lines.

    Parameters
    ----------
    index : pd.DataFrame
        The formatted index from SsODNet.
    """

    import pandas as pd

    pbar[task_id] = {"progress": 1, "total": 2}

    index = index.sort_values(["Number", "Name"])

    no_number = pd.isna(index.Number)
    has_number = index[~no_number]
    no_number = index[no_number]

    numbered = (
        "(" + has_number["Number"].astype(str) + ") " + has_number["Name"].astype(str)
    )
    unnumbered = "     " + no_number["Name"].astype(str)
    LINES = [
        line.encode(sys.getdefaultencoding()) + b"\n"
        for line in numbered.to_numpy().tolist()
    ]
    LINES += [
        line.encode(sys.getdefaultencoding()) + b"\n"
        for line in unnumbered.to_numpy().tolist()
    ]

    _write_to_cache(LINES, "fuzzy_index.pkl")
    pbar[task_id] = {"progress": 2, "total": 2}


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

    import pandas as pd

    # The gzipped index is exposed under this address
    URL_INDEX = "https://asterm.imcce.fr/public/ssodnet/sso_index.csv.gz"
    index = pd.read_csv(URL_INDEX)

    # There are some spurious spaces in the column headers
    index = index.rename(columns={c: c.replace(" ", "") for c in index.columns})

    # Don't need other columns
    index = index[["Name", "Number", "SsODNetID", "Reduced"]]

    # We use NaNs instead of 0 for unnumbered objects
    index.loc[index["Number"] == 0, "Number"] = np.nan
    index["Number"] = index["Number"].astype("Int64")

    return index


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

        if not (config.PATH_INDEX / which).exists():
            logger.warning(
                f"Could not resolve asteroid number {id_}. Either the number is "
                "larger than that of any asteroid or the rocks index is outdated."
            )
            return {}

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
        logger.error(
            "The asteroid name-number index is malformed. Run '$ rocks status' to rebuild it."
        )
        return {}

    with open(config.PATH_INDEX / which, "rb") as file_:
        return pickle.load(file_)


def get_modification_date():
    """Get modification date of index pickle files."""
    check_file = config.PATH_INDEX / "1.pkl"
    if not check_file.is_file():
        return "[red][No Index Found][/red]"
    date_index = check_file.stat().st_mtime
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

    It looks like this is the first time you run [green]rocks[/green]. By storing some
    data on your machine, [green]rocks[/green] can run much faster. You can set the location
    of this directory using the [dim]ROCKS_CACHE_DIR[/dim] environment variable.
    """

    # Cache directory is missing: first time running rocks
    if not config.PATH_CACHE.is_dir():
        rich.print(GREETING)

        use_cache = Confirm.ask(
            f"    Use cache directory [[dim]{config.PATH_CACHE}[/dim]]?"
        )

        if not use_cache:
            rich.print(
                "\n    Not using a cache. Set [dim]ROCKS_CACHE_DIR='no-cache'[/dim] to make this\n"
                "    decision permanent.\n"
            )
            config.CACHELESS = True
            return

        config.PATH_CACHE.mkdir(parents=True)

    # Cache exists but index is missing
    else:
        logger.warning(
            "The local asteroid name-number index is missing. Downloading it now."
        )

    config.PATH_INDEX.mkdir(parents=True)
    _build_index()

    rich.print("\nAll done. Find out more by running [green]$ rocks docs[/green]\n")
