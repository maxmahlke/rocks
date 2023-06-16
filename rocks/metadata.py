"""Functionality for SsODNet metadata interaction with rocks."""

from functools import lru_cache
import json
import re
import unicodedata

import requests
import rich

from rocks import config
from rocks.logging import logger
from rocks import __version__


@lru_cache(None)
def load_mappings():
    """Load SsODNet metadata mappings file from cache."""

    if not config.PATH_MAPPINGS.is_file():
        retrieve("mappings")

    with open(config.PATH_MAPPINGS, "r") as file_:
        mappings = json.load(file_)

        # There are different capitalizations in MOIDs between rocks
        # and ssodnet. Ensure that the units are found anyway
        # This conversion is also done when retrieving the mappings,
        # the code here ensures compatibility with outdated mappings files
        # Remove in October 2023
        mappings = {
            k.lower(): {i.lower(): j for i, j in v.items()}
            if isinstance(v, dict)
            else v
            for k, v in mappings.items()
        }
        return mappings


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
        logger.warning(f"Retrieving {which} file failed with URL:\n{URL}")
        return

    metadata = response.json()

    if which == "mappings":
        metadata = metadata["display"]

        metadata = {
            k.lower(): {i.lower(): j for i, j in v.items()}
            if isinstance(v, dict)
            else v
            for k, v in metadata.items()
        }

    PATH_OUT = config.PATH_AUTHORS if which == "authors" else config.PATH_MAPPINGS

    with open(PATH_OUT, "w") as file_:
        json.dump(metadata, file_)


# ------
# Miscellaneous
def find_author(author):
    """Print dataset and publication matching 'author' as first-author name."""

    if not config.PATH_AUTHORS.is_file():
        retrieve("authors")

    with open(config.PATH_AUTHORS, "r") as file_:
        ssodnet_biblio = json.load(file_)

    author_found = False

    for category, datasets in ssodnet_biblio["ssodnet_biblio"]["datasets"].items():
        for dataset in datasets:
            if author.capitalize() in remove_diacritics(dataset["shortbib"]):
                rich.print(
                    f" [magenta]{dataset['bibcode']}[/magenta]  {dataset['shortbib']:<20} [{category}]"
                )
                author_found = True

    if not author_found:
        logger.info(
            f"Could not find articles by '{author.capitalize()}' in SsODNet. You can email 'benoit.carry (at) oca.eu' if you are missing data."
        )


def remove_diacritics(text):
    """Remove accents from characters for a wider search.

    Parameters
    ----------
    text : str
        The text to strip the accents from.

    Returns
    -------
    str
        The accent-free string.

    Notes
    -----
    Merci to https://stackoverflow.com/a/35783136
    """
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(c for c in normalized if unicodedata.category(c) != "Mn")


def rocks_is_outdated():
    """Compare the local rocks __version__ to the one on the GitHub repository.

    Returns
    -------
    bool, str
        True if the local version is below the one on GitHub, else
        False. String contains latest version if outdated, else it's
        empty.
    """

    URL = "https://github.com/maxmahlke/rocks/blob/master/pyproject.toml?raw=True"

    try:
        response = requests.get(URL, timeout=10)
    except requests.exceptions.ReadTimeout:
        return (False, "")

    if not response.ok:
        return (False, "")  # can't tell, assume it's ok

    version_remote = re.findall(r"\d+\.\d+[\.\d]*", response.text)[0]
    version_remote = tuple(map(int, version_remote.split(".")))

    version_local = tuple(map(int, __version__.split(".")))

    if version_remote > version_local:
        return (True, ".".join(str(v) for v in version_remote))

    return (False, "")
