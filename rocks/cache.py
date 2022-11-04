"""Cache management for rocks."""

import json
from pathlib import Path
import re
import tarfile

import requests
import rich

from rocks import config
from rocks import metadata
from rocks import resolve
from rocks import ssodnet


# ------
# Functions for cache management
def clear():
    """Remove the cached ssoCards and datacloud catalogues.

    Note
    ----
    This only removes ssoCards, datacloud catalogues, and metadata files.
    The index and unknown files are not touched. Use '$ rm -r ~/.cache/rocks'
    to delete the entire index.
    """
    cards, catalogues = take_inventory()

    for card in cards:
        (config.PATH_CACHE / f"{card}.json").unlink()

    for catalogue in catalogues:
        (config.PATH_CACHE / f"{'_'.join(catalogue)}.json").unlink()

    for path in [config.PATH_MAPPINGS, config.PATH_AUTHORS]:
        if path.is_file():
            path.unlink()


def take_inventory():
    """Create lists of the cached ssoCards and datacloud catalogues.

    Returns
    -------
    list of str
        The SsODNet IDs of the cached ssoCards.
    list of tuple
        The SsODNet IDs and names of the cached datacloud catalogues.
    """

    # Get all JSONs in cache
    cached_jsons = set(file_ for file_ in config.PATH_CACHE.glob("*.json"))

    cached_cards = []
    cached_catalogues = []

    for file_ in cached_jsons:

        # Is it metadata?
        if file_ in [config.PATH_MAPPINGS, config.PATH_AUTHORS]:
            continue

        # Datacloud catalogue or ssoCard?
        if any(cat["ssodnet_name"] in str(file_) for cat in config.DATACLOUD.values()):
            *ssodnet_id, catalogue = file_.stem.split("_")
            ssodnet_id = "_".join(ssodnet_id)  # in case of provisional designation
        else:
            ssodnet_id = file_.stem
            catalogue = ""

        # Is it valid?
        with open(file_, "r") as ssocard:
            try:
                _ = json.load(ssocard)
            except json.decoder.JSONDecodeError:
                # Empty card or catalogue, remove it
                file_.unlink()
                continue

        # Append to inventory
        if catalogue:
            cached_catalogues.append((ssodnet_id, catalogue))
        else:
            cached_cards.append(ssodnet_id)

    return cached_cards, cached_catalogues


def update_cards(ids):
    """Update the cached ssoCards belonging to the passed identifiers. Verify
    that asteroid SsODNet ID has not changed.

    Parameters
    ----------
    ids : list
        List of SsODNet IDs corresponding to the cards to update.
    """

    # ------
    # Verify that the IDs are the current ones
    if not ids:
        return  # nothing to do here

    elif len(ids) == 1:
        _, _, ids_new = resolve.identify(ids, return_id=True, local=False)
        ids_new = [ids_new]

    else:
        _, _, ids_new = zip(
            *resolve.identify(ids, return_id=True, local=False, progress=True)
        )

    # Did any ID change?
    for id_, id_new in zip(ids, ids_new):

        if id_ == id_new:
            continue

        # This is fun to know
        rich.print(f"{id_} is now known as {id_new}.")

        # Remove the outdated card
        (config.PATH_CACHE / f"{id_}.json").unlink()

    # Update all cards
    ssodnet.get_ssocard(ids, progress=True, local=False)


def update_catalogues(cached_catalogues):
    """Update the cached datacloud catalogues.

    Parameters
    ----------
    cached_catalogues: list of tuple
        The SsODNet IDs and names of the cached datacloud catalogues.
    """

    # Update catalogues on a per-type basis
    for catalogue in set(catalogues[1] for catalogues in cached_catalogues):

        ids = [id_ for id_, cat in cached_catalogues if cat == catalogue]
        ssodnet.get_datacloud_catalogue(ids, catalogue, local=False, progress=True)


def retrieve_all_ssocards():
    """Retrieves all ssoCards and stores them in the cache directory.

    Warning: This will slow down the '$ rocks status' command considerably.
    """

    # Retrieve archive of ssoCards
    PATH_ARCHIVE = "/tmp/ssoCard-latest.tar.gz"

    URL = "https://ssp.imcce.fr/webservices/ssodnet/api/ssocard/ssoCard-latest.tar.bz2"

    response = requests.get(URL, stream=True)

    with open(PATH_ARCHIVE, "wb") as fp:
        shutil.copyfileobj(response.raw, fp)

    # Extract to the cache directory
    cards = tarfile.open(PATH_ARCHIVE, mode="r:bz2")
    members = cards.getmembers()

    for member in track(members, total=len(members), description="Unpacking ssoCards"):

        if not member.name.endswith(".json"):
            continue

        member.path = member.path.split("/")[-1]
        cards.extract(member, config.PATH_CACHE)
