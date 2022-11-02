"""Functionality for SsODNet metadata interaction with rocks."""

from functools import lru_cache
import json
from pathlib import Path
import re

import requests

from rocks import __version__

PATH_MAPPINGS = Path.home() / ".cache/rocks/metadata_aster.json"
PATH_AUTHORS = Path.home() / ".cache/rocks/ssodnet_biblio.json"


@lru_cache(None)
def load_mappings():
    """Load SsODNet metadata mappings file from cache."""

    if not PATH_MAPPINGS.is_file():
        retrieve("mappings")

    with open(PATH_MAPPINGS, "r") as file_:
        return json.load(file_)


def retrieve(which):
    """Retrieve the metadata JSON files from SsODNet to the cache directory.

    Parameter
    ---------
    which : str
        Which metadata to retrieve. Choose from ['mappings', 'authors'].
    """

    if which not in ["mappings", "authors"]:
        raise ValueError(
            f"'which' has to be in ['mappings', 'authors'], received {which}."
        )

    FILENAME = "ssodnet_biblio" if which == "authors" else "metadata_aster"
    URL = f"https://ssp.imcce.fr/data/{FILENAME}.json"

    # Retrieve requested file from SsODNet
    response = requests.get(URL)

    if not response.ok:
        warnings.error(f"Retrieving {which} file failed with URL:\n{URL}")
        return

    metadata = response.json()

    if which == "mappings":
        metadata = metadata["display"]

    PATH_OUT = PATH_AUTHORS if which == "authors" else PATH_MAPPINGS

    with open(PATH_OUT, "w") as file_:
        json.dump(metadata, file_)


# ------
# Miscellaneous
def find_author(author):
    """Print dataset and publication matching 'author' as first-author name."""

    if not PATH_AUTHORS.is_file():
        retrieve_metadata("authors")

    with open(PATH_AUTHORS, "r") as file_:
        ssodnet_biblio = json.load(file_)

    for category, datasets in ssodnet_biblio["ssodnet_biblio"]["datasets"].items():
        for dataset in datasets:
            if author.capitalize() in dataset["shortbib"]:
                print(f"  {dataset['shortbib']:<20} [{category}]")


def rocks_is_outdated():
    """Compare the local rocks __version__ to the one on the GitHub repository.

    Returns
    -------
    bool
        True if the local version is below the one on GitHub, else False.
    """

    URL = "https://github.com/maxmahlke/rocks/blob/master/pyproject.toml?raw=True"

    try:
        response = requests.get(URL, timeout=10)
    except requests.exceptions.ReadTimeout:
        return ""

    if not response.ok:
        return False  # can't tell, assume it's ok

    version_remote = re.findall(r"\d+\.\d+[\.\d]*", response.text)[0]
    version_remote = tuple(map(int, version_remote.split(".")))

    version_local = tuple(map(int, __version__.split(".")))

    if version_remote > version_local:
        return True

    return False
