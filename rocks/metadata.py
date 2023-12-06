"""Functionality for SsODNet metadata interaction with rocks."""
from functools import lru_cache
import html
import json
import re
import unicodedata
from urllib.request import urlretrieve, urlopen
from urllib.error import HTTPError

import requests
import rich

from rocks import config
from rocks.logging import logger
from rocks import __version__


@lru_cache(None)
def load_mappings():
    """Load SsODNet metadata mappings file from cache."""

    if config.CACHELESS or not config.PATH_MAPPINGS.is_file():
        mappings = retrieve("mappings")
    else:
        with open(config.PATH_MAPPINGS, "r") as file_:
            mappings = json.load(file_)

    if not config.PATH_MAPPINGS.is_file() and not config.CACHELESS:
        with open(config.PATH_MAPPINGS, "w") as file_:
            json.dump(mappings, file_)

    return mappings


def retrieve(which):
    """Retrieve the metadata JSON files from SsODNet to the cache directory.

    Parameter
    ---------
    which : str
        Which metadata to retrieve. Choose from ['mappings', 'authors'].
    """

    if which not in ["mappings", "authors", "citations"]:
        raise ValueError(
            f"'which' has to be in ['mappings', 'authors', 'citations'], received {which}."
        )

    if which == "citations":
        _retrieve_citations()
        return

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
    return metadata


# ------
# Miscellaneous
def find_author(author):
    """Print dataset and publication matching 'author' as first-author name."""

    if not config.PATH_AUTHORS.is_file() or config.CACHELESS:
        ssodnet_biblio = retrieve("authors")
    else:
        with open(config.PATH_AUTHORS, "r") as file_:
            ssodnet_biblio = json.load(file_)

    if not config.PATH_AUTHORS.is_file() and not config.CACHELESS:
        with open(config.PATH_AUTHORS, "w") as file_:
            json.dump(ssodnet_biblio, file_)

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


def get_citation(number):
    """Query asteroid information from MPC and extract citation from HTML response."""

    if not config.PATH_CITATIONS.is_file():
        logger.info("Retrieving citations from MPC and WGSBN..")
        _retrieve_citations()

    citations = json.load(config.PATH_CITATIONS.open("r"))

    if str(number) not in citations:
        return None

    return citations[str(number)]


def _retrieve_citations():
    urlretrieve(
        "https://minorplanetcenter.net/citations.txt",
        config.PATH_CITATIONS.with_suffix(".txt"),
    )

    citations = {}

    with config.PATH_CITATIONS.with_suffix(".txt").open("r", encoding="latin1") as file:
        # first four citations are on two lines
        for _ in range(4):
            id_ = file.readline()
            citation = file.readline()

            number = id_.split()[0]
            citation = citation.split("<br><br>")[-1]

            citations[number] = html.unescape(citation)

        # now single line
        for line in file:
            # line = line.encode("utf-8")
            number = line.split()[0]
            citation = line.split("<br><br>")[-1]
            citations[number] = html.unescape(citation)

    # Add most recent citations
    URL_BASE = "https://www.wgsbn-iau.org/files/json"
    for year in range(1, 5):
        for volume in range(1, 20):
            try:
                with urlopen(
                    f"{URL_BASE}/V0{year:>02}/WGSBNBull_V0{year:>02}_{volume:>03}.json"
                ) as url:
                    new = json.load(url)

                    new = {entry["mp_number"]: entry["citation"] for entry in new}

                    citations.update(new)
            except HTTPError:
                break

    with config.PATH_CITATIONS.open("w") as out:
        out.write(json.dumps(citations, sort_keys=True, indent=2))
