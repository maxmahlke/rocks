import re

import aiohttp
import numpy as np
import requests


from rocks.logging import logger

URL = "https://api.ssodnet.imcce.fr/quaero/1/sso/search"


async def query(id, type: str = "asteroid", session=None) -> dict:
    """Query quaero to identify an asteroid, a comet, or a satellite.

    Parameters
    ----------
    id : str, int, float
        Unique identifier of object.
    type: str
        The type of the minor body. One of ['asteroid', 'comet', 'satellite'].
        Optional, default is 'asteroid'.
    session : aiohttp.ClientSession
        aiohttp session for asyncronous queries. Optional, default is None.

    Returns
    -------
    dict
        Dictionary containing the quaero response of the unique match if successful.
        Empty dictionary otherwise.
    """

    # ------
    # Define query Parameters
    if type not in ["asteroid", "comet", "satellite"]:
        raise ValueError(
            "Quaero query type must be one of ['asteroid', 'comet', 'satellite']."
        )

    query_type = (
        'Asteroid OR "Dwarf Planet"' if type == "asteroid" else type.capitalize()
    )
    params = {"q": f'type:({query_type}) AND  "{id}"~0', "from": "rocks", "limit": 100}

    # ------
    # Run query in async session or in sync
    if session is not None:
        try:
            response = await session.request(method="GET", url=URL, params=params)
        except aiohttp.client_exceptions.ClientConnectorError:
            logger.error(f"Failed to establish connection to\n {URL}")
            return {}
        try:
            response = await response.json(content_type=None)
        except aiohttp.ContentTypeError:
            return {}

    else:
        response = requests.get(url=URL, params=params)
        if not response.ok:
            logger.error(f"Quaero query failed with URL\n {response.url}")
            return {}
        response = response.json()

    if "data" not in response.keys():  # no match found
        logger.error(f"Could not identify {type} '{id}' [invalid server response]")
        return {}

    elif not response["data"]:  # empty response
        logger.error(f"Could not identify {type} '{id}' [no match found]")
        return {}

    # Identify matching response entry based on minor body type
    match = identify_unique_match(id, response["data"], type)

    # Remove unnecessary keys
    for key in list(match.keys()):
        if key not in ["name", "number", "type", "id", "aliases", "links"]:
            del match[key]

    if not match:
        logger.warning(f"Could not identify {type} '{id}' [non-unique match]")

    return match


def identify_unique_match(id, matches, type):
    """Identify and post-process quaero query response.

    Parameters
    ----------
    id : str, int, float
        Unique identifier of object.
    matches : list of dict
        List of dict containing quaero matches for a single query.
    type: str
        The type of the minor body. One of ['asteroid', 'comet', 'satellite'].

    Returns
    -------
    dict
        Dictionary containing the quaero response of the unique match if successful.
        Empty dictionary otherwise.
    """
    if type == "asteroid":
        return _identify_unique_asteroid(id, matches)
    if type == "comet":
        return _identify_unique_comet(id, matches)
    if type == "satellite":
        return _identify_unique_satellite(id, matches)


def _identify_unique_asteroid(id, matches):
    """Identify and post-process quaero query response for asteroids.

    Notes
    -----
    Unique match is based on exact match with name, id, or any alias.
    'number' is set to the smallest numeric alias.
    """
    id = str(id).lower()

    for match in matches:
        if match["name"].lower() == id:
            break
        elif match["id"].lower() == id:
            break
        elif any(alias.lower() == id for alias in match["aliases"]):
            break
    else:
        # Unclear which match is correct.
        return {}

    # Add 'number' key for asteroids
    numeric = [int(alias) for alias in match["aliases"] if alias.isnumeric()]
    match["number"] = min(numeric) if numeric else np.nan
    return match


def _identify_unique_comet(id, matches):
    """Identify and post-process quaero query response for comets.

    Notes
    -----
    If multiple matches due to name and fragmets, return main piece
    """
    id = str(id).lower()

    # NOTE: This check is already done on SsODNet server side
    candidates = [
        match
        for match in matches
        if match["name"].lower() == id
        or match["id"].lower() == id
        or any(alias.lower() == id for alias in match["aliases"])
    ]

    if not candidates:
        # No match found
        return {}

    if len(candidates) == 1:
        match = candidates[0]
    else:
        # Multiple matches found
        # Check if they are all fragments of the same comet
        main_piece = min(match["name"] for match in candidates)
        if all(main_piece in match["name"] for match in candidates):
            # return main fragment
            match = [match for match in candidates if match["name"] == main_piece][0]

        else:  # ambiguous
            return {}

    # match["number"] = match["name"]
    # match["name"] = match["aliases"][0]
    return match


def _identify_unique_satellite(id, matches):
    """Identify and post-process quaero query response for satellites.

    Notes
    -----
    Unique match is based on exact match with name, id, or any alias.
    'number' is set to the smallest numeric alias.
    """
    id = str(id).lower()

    for match in matches:
        if match["name"].lower() == id:
            break
        elif match["id"].lower() == id:
            break
        elif any(alias.lower() == id for alias in match["aliases"]):
            break
    else:
        # Unclear which match is correct.
        return {}

    # Add 'number' key
    numeric = [
        int(alias)
        for alias in match["aliases"]
        if alias.isnumeric() and int(alias) > 300
    ]
    match["number"] = min(numeric) if numeric else np.nan
    return match


def standardize_id(id_):
    """Try to infer id_ type and re-format if necessary to ensure
    successful remote lookup.

    Parameters
    ----------
    id_ : str, int, float
        The minor body's name, designation, or number.

    Returns
    -------
    str, int, None
        The standardized name, designation, or number. None if id_ is NaN or None.
    """
    if isinstance(id_, (int, float)):
        return int(id_)

    elif isinstance(id_, str):
        # Strip leading and trailing whitespace
        id_ = id_.strip()

        # String id_. Perform some regex tests to make sure it's well formatted

        # Asteroid number
        try:
            id_ = int(float(id_))
            return id_
        except ValueError:
            pass

        # Ensure that there is no suffix
        id_ = id_.replace("_(Asteroid)", "")

        # Asteroid name
        if re.match(r"^[A-Za-z _]*$", id_):
            # make case-independent
            id_ = id_.lower()

        # Asteroid designation
        elif re.match(
            r"(^([1A][8-9][0-9]{2}[ _]?[A-Za-z]{2}[0-9]{0,3}$)|"
            r"(^20[0-9]{2}[_ ]?[A-Za-z]{2}[0-9]{0,3}$))",
            id_,
        ):
            # Ensure whitespace between year and id_
            id_ = re.sub(r"[\W_]+", "", id_)
            ind = re.search(r"[A18920]{1,2}[0-9]{2}", id_).end()  # type: ignore
            id_ = f"{id_[:ind]} {id_[ind:]}"

            # Replace A by 1
            id_ = re.sub(r"^A", "1", id_)

            # Ensure uppercase
            id_ = id_.upper()

        # Palomar-Leiden / Transit
        elif re.match(r"^[1-9][0-9]{3}[ _]?(P-L|T-[1-3])$", id_):
            # Ensure whitespace
            id_ = re.sub(r"[ _]+", "", id_)
            id_ = f"{id_[:4]} {id_[4:]}"

        # Comet
        elif re.match(r"(^[PDCXAI]/[- 0-9A-Za-z]*)", id_):
            pass

        # Remaining should be unconventional asteroid names like
        # "G!kun||'homdima" or packed designations
        else:
            pass
    else:
        logger.warning(
            f"Did not understand type of id: {type(id_)}"
            "\nShould be integer, float, or string."
        )
    return id_
