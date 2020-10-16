#!/usr/bin/env python
""" Utility functions for rocks
"""
import collections.abc
from functools import reduce, lru_cache
import json
import keyword
import os
import sys
import time
from types import SimpleNamespace
import warnings

import click
from iterfzf import iterfzf
import numpy as np
import pandas as pd
import requests
import rich.progress

import rocks

PATH_CACHE = os.path.join(os.path.expanduser("~"), ".cache/rocks")
os.makedirs(PATH_CACHE, exist_ok=True)


def progress_context():
    """docstring for progress_context"""
    return rich.progress.Progress(
        "[progress.description]{task.description}",
        rich.progress.BarColumn(),
        "{task.completed:,}/{task.total:,}",
        rich.progress.TimeRemainingColumn(),
    )


def update_ssoCard(dict_, update):
    for key, val in update.items():
        if isinstance(val, collections.abc.Mapping):
            dict_[key] = update_ssoCard(dict_.get(key, {}), val)
        else:
            if isinstance(dict_, list):  # multiple pair members
                dict_ = dict_[-1]
            if isinstance(val, list):  # multiple taxonomies
                val = val[-1]
            dict_[key] = val
    return dict_


def rsetattr(obj, attr, val):
    pre, _, post = attr.rpartition(".")
    return setattr(rgetattr(obj, pre) if pre else obj, post, val)


def rgetattr(obj, attr, *args):
    def _getattr(obj, attr):
        return getattr(obj, attr, *args)

    return reduce(_getattr, [obj] + attr.split("."))


def create_index():
    """Create or update index of numbered SSOs.

    Notes
    -----
    The list is retrieved from the Minor Planet Center, at
    https://www.minorplanetcenter.net/iau/lists/NumberedMPs.txt
    Each number is associated to its SsODNet id.
    """
    # Get list of numbered asteroids from MPC
    url = "https://www.minorplanetcenter.net/iau/lists/NumberedMPs.txt"

    numbered = pd.read_fwf(
        url,
        colspecs=[(0, 7), (9, 29), (29, 41)],
        names=["number", "name", "designation"],
        dtype={"name": str, "designation": str},
        converters={"number": lambda x: int(x.replace("(", ""))},
    )

    # Compare list to index
    index = read_index()
    missing = numbered.loc[~numbered.number.isin(index["number"]), "number"]

    # Get ids of missing entries, append to index
    names, numbers, ids = zip(
        *rocks.identify(sorted(missing), return_id=True, verbose=False, progress=True)
    )

    index = index.append(pd.DataFrame({"name": names, "number": numbers, "id_": ids}))

    # Save index to file
    path_index = os.path.join(PATH_CACHE, "index")

    index = (
        index.dropna(how="any")
        .drop_duplicates("number")
        .sort_values("number", ascending=True)
        .astype({"number": np.int64, "name": str, "id_": str})
    )
    index.to_csv(path_index, index=False)


def read_index():
    """Read local index of asteroid numbers, names, SsODNet IDs.

    Returns
    =======
    pd.DataFrame
        Asteroid index with three columns.

    Notes
    =====
    If the index file is older than 30 days, a reminder to update is
    displayed.
    """
    path_index = os.path.join(PATH_CACHE, "index")

    if not os.path.isfile(path_index):
        if sys.argv[-1] != "update":
            click.echo("No index file found. Run 'rocks update' to create it.")
        return pd.DataFrame(data={"name": [], "number": [], "id_": []})

    # Check age of index file
    days_since_mod = (time.time() - os.path.getmtime(path_index)) / (3600 * 24)

    if days_since_mod > 30:
        click.echo(
            "The index file is more than 30 days old. "
            "Consider updating with 'rocks update' and removing cached "
            "values under $HOME/.cache/rocks"
        )
        time.sleep(1)  # so user doesn't miss the message

    index = pd.read_csv(path_index, dtype={"number": int, "name": str, "id_": str})
    return index


def _fuzzy_desig_selection(index):
    """Generator for fuzzy search of asteroid index file. """
    for number, name in zip(index.number, index["name"]):
        yield f"{number} {name}"


def select_sso_from_index():
    """Select SSO numbers and designations from interactive fuzzy search.

    Returns
    =======
    str
        asteroid name or designation
    int
        asteroid number

    Notes
    -----
    If the selection is interrupted with ctrl-c, ``(None, None)`` is returned.

    Examples
    --------
    >>> from rocks import utils
    >>> name, number, id_ = utils.select_sso_from_index()
    """
    index = read_index()

    try:
        nunaid = iterfzf(_fuzzy_desig_selection(index), exact=True)
        number, *name = nunaid.split()
    except AttributeError:  # no SSO selected
        return None, None, None

    id_ = index.loc[index.number == int(number), "id_"].values[0]
    return " ".join(name), int(number), id_


def create_ssocard_template():
    """Retrieves current ssoCard template from SsODNet and saves
    simplified version to file.
    """

    # Retrieve current template from SsODNet
    url = "https://ssp.imcce.fr/webservices/ssodnet/api/"
    url = f"{url}ssocard/templates/catalogue-template_aster-astorb.json"

    response = requests.get(url)
    ssoCard = response.json()

    # Simplify unit and uncertainty acces
    ssoCard = __set_endpoints_to_none(ssoCard)

    # Add missing recods
    ssoCard["datacloud"] = {
        "aams": np.nan,
        "astdys": np.nan,
        "astorb": np.nan,
        "binarymp_tab": np.nan,
        "binarymp_ref": np.nan,
        "diamalbedo": np.nan,
        "families": np.nan,
        "masses": np.nan,
        "mpcatobs": np.nan,
        "mpcorb": np.nan,
        "pairs": np.nan,
        "taxonomy": np.nan,
    }

    ssoCard["source"] = {
        "osculating_elements": np.nan,
        "proper_elements": np.nan,
        "family": np.nan,
        "pair": np.nan,
    }

    path_template = os.path.join(PATH_CACHE, "ssoCard_template.json")
    with open(path_template, "w") as file_:
        json.dump(ssoCard, file_)


def sanitize_keys(dict_):
    """docstring for __find_endpoint"""
    for key, value in dict_.copy().items():
        if isinstance(value, dict):
            dict_[key] = sanitize_keys(dict_[key])
        else:
            if keyword.iskeyword(key):
                dict_[f"{key}_"] = dict_.pop(key)
    return dict_


def __move_level_up(dict_, key):
    """Moves nested dictionatry level to top level and removes original key.

    Parameters
    ==========
    dict_ : dict
        Dictionary to adapt.
    key : str
        Dictionary key to flatten and remove.

    Returns
    =======
    dict
        Updated dictionary.
    """
    for k, v in dict_[key].items():
        dict_[k] = v

    dict_.pop(key, None)
    return dict_


def __set_endpoints_to_none(dict_):
    """docstring for __find_endpoint"""
    for key, value in dict_.copy().items():
        if isinstance(value, dict):
            dict_[key] = __set_endpoints_to_none(dict_[key])
        else:
            if key == "unit":
                continue
            else:
                dict_[key] = np.nan
    return dict_


def __sanitize_keyword(k):
    """docstring for __sanitize_keyword"""
    if keyword.iskeyword(k):
        return f"{k}_"
    else:
        return k


# ------
# SsODNet functions
def retrieve_catalogue(url):
    """Retrieve catalogue from datacloud."""

    response = requests.get(url.replace("SsODNetSsoCard", "rocks"))
    catalogue = response.json()["data"]

    catalogue = sanitize_keys(catalogue)
    return catalogue


@lru_cache(128)
def get_data(id_, verbose=True):
    """Get asteroid data from SsODNet:datacloud.

    Performs a GET request to SsODNet:datacloud for a single asteroid and
    property. Checks validity of data and extracts it from response.

    Parameters
    ----------
    id_ : str, int
        Asteroid name, designation, or number.
    verbose : bool
        Print request diagnostics.

    Returns
    -------
    dict, bool
        Asteroid data, False if query failed or no data is available
    """
    response = query_ssodnet(id_, verbose=verbose)

    # Check if query failed
    if response.status_code in [422, 500]:

        # Query SsODNet:quaero and repeat
        if verbose:
            click.echo(f"Query failed for {id_}.")
        return False

    # See if there is data available
    try:
        data = response.json()["data"]
    except (json.decoder.JSONDecodeError, KeyError):
        if verbose:
            click.echo(f'Encountered JSON error for "{id_}".')
        return False

    # Select the right data entry
    if len(data.keys()) > 1:
        for k in [id_, f"{id_}_(Asteroid)"]:
            if k in data.keys():
                key = k
                break
        else:
            key = list(data.keys())[0]
    else:
        key = list(data.keys())[0]
    return data[key]


def query_ssodnet(name, mime="json", verbose=False):
    """Query SsODNet services.

    Includes validity check of response.

    Parameters
    ----------
    name : str, float
        Asteroid identifier
    mime : str
        Response mime type. Default is json.
    verbose : bool
        Print request diagnostics. Default is False.

    Returns
    -------
    r - requests.models.Response
        GET request response from SsODNet
    """
    url = "https://ssp.imcce.fr/webservices/ssodnet/api/datacloud.php"

    payload = {
        "-name": f"{name}",
        "-mime": mime,
        "-from": "rocks",
    }

    r = requests.get(url, params=payload)

    _RESPONSES = {
        400: "Bad request",
        422: "Unprocessable Entity",
        500: "Internal Error",
        404: "Not found",
    }

    if r.status_code != 200:
        if r.status_code in _RESPONSES.keys() and verbose:
            message = f"HTTP code {r.status_code}: {_RESPONSES[r.status_code]}"
        else:
            message = f"HTTP code {r.status_code}: Unknown error"

        if verbose:
            click.echo(message)
            click.echo(r.url)
        return False
    return r


def echo_response(response, mime):
    """Echo the formatted SsODNet response to STDOUT.

    The echo function is based on the query mime type.

    Parameters
    ----------
    response : requests.models.Response
        SsODNet GET query response.
    mime : str
        Mime-type of response.
    """
    if mime == "json":
        data = response.json()
        click.echo(json.dumps(data, indent=2))

    elif mime == "votable":
        for line in response.content.decode("utf-8").split("\n")[1:]:
            click.echo(line)
    else:
        click.echo(response.text)


def get_ssoCard(ids):
    """Return target ssoCard. Use cache if existant, else, query SsODNet and cache results.

    Parameters
    ==========
    ids : str, list, np.array, pd.Series
        Single Minor body target id from SsODNet or list of several.
        Pass SsODNet ID for fast access.

    Returns
    =======
    dict, list of dict, None
        Sinlgle or list of ssoCards in json format if successful.
        None if query failed.
    """
    if isinstance(ids, str):
        ids = [ids]
    elif isinstance(ids, pd.Series):
        ids = ids.values

    path_ssocards = os.path.join(PATH_CACHE, "ssoCards")
    os.makedirs(path_ssocards, exist_ok=True)

    missing = []

    for id_ in ids:
        if not isinstance(id_, str):
            warnings.warn(f"Expected string identifier, got {type(id_)}.")
            id_ = None
            continue

        # Check presence in cache
        path_card = os.path.join(path_ssocards, f"{id_}.json")
        if not os.path.isfile(path_card):
            missing.append(id_)

    # Perform POST query for missing cards.
    ssoCards = __query_ssoCards(missing)

    if len(ids) == 1:
        ssoCards = [ssoCards]

    # Save to cache
    for id_, ssoCard in zip(missing, ssoCards):

        if ssoCard is None:
            continue

        #  ssoCard = simplify_ssoCard(ssoCard)

        path_card = os.path.join(path_ssocards, f"{id_}.json")

        with open(path_card, "w") as file_:
            json.dump(ssoCard, file_)

    # Return requested ssoCards
    ssoCards = []

    for id_ in ids:

        if id_ is None:
            ssoCards.append(None)

        path_card = os.path.join(path_ssocards, f"{id_}.json")

        if os.path.isfile(path_card):

            with open(path_card, "r") as file_:
                ssoCard = json.load(file_)

            ssoCards.append(ssoCard)

        else:
            ssoCards.append(None)

    if len(ids) == 1:
        return ssoCards[0]
    else:
        return ssoCards


def __query_ssoCards(ids):
    """Retrieve ssoCards for targets from SsODNet via POST request.

    Parameters
    ==========
    ids : str, list, np.array, pd.Series
        Single Minor body target id from SsODNet or list of several.

    Returns
    =======
    dict, list of dict, None
        Sinlgle or list of ssoCards in json format if successful.
        None if query failed.

    Notes
    =====
    Performs output check and tries to infer correct target string if query failed.
    """
    if isinstance(ids, str):
        ids = [ids]
    elif isinstance(ids, pd.Series):
        ids = ids.values

    url = f"https://asterws2.imcce.fr/webservices/ssodnet/api/ssocard/"

    params = {"from": "rocks"}
    file_ = {"targets": ("\n".join([id_ for id_ in ids]))}

    try:
        response = requests.post(url=f"{url}mytargets", params=params, files=file_)
        response.encoding = "UTF-8"
        response = response.json()
    except requests.exceptions.RequestException as e:
        warnings.warn(f"An error occurred when retrieving the ssoCards: {e}")
        return False

    if len(ids) > 100:
        ssoCards = []
        with progress_context() as prog:
            for id_ in prog.track(ids, description=("Retrieving ssoCards")):
                ssoCards.append(response[id_])
    else:
        ssoCards = [response[id_] for id_ in ids]

    if len(ids) == 1:
        return ssoCards[0]
    else:
        return ssoCards


def pretty_print_card(ssoCard, minimal):
    """Pretty-print ssoCard to terminal.

    Parameters
    ==========
    ssoCard : dict
        Minor body ssoCard.
    minimal : bool
        Reduce information to basics.
    """
    from rich.console import Console

    console = Console()

    if not minimal:
        console.print(ssoCard)
    else:

        from rich.panel import Panel
        from rocks.core import Rock

        rock = Rock(ssoCard["id"], ssoCard, skip_id_check=True)

        minimal_card = f"""

        type: {rock.type:<12} class: {rock.class_}
        taxonomy: {rock.taxonomy.class_:<12} ap: {rock.proper_elements.proper_semi_major_axis:.4}

        """  # {rock.proper_elements.semi_major_axis.unit}
        console.print(Panel(minimal_card, title=f"({rock.number}) {rock.name}"))


def pretty_print(SSO, property_name):
    """Pretty-print asteroid property to console.

    Parameters
    ==========
    SSO : rocks.core.Rock
        The Rock instance representing the asteroid.
    property_name : str
        The attribute name of property to pretty-print.
    """
    from rich import print as rprint
    from rocks import core
    from rocks.properties import PROPERTIES as PROPS

    property_value = getattr(SSO, property_name)

    if property_value is np.nan or property_value is None:
        print(f"No {property_name} on record for ({SSO.number}) {SSO.name}")
        sys.exit()

    # Output type depends on property type
    if isinstance(property_value, (int, str)):
        print(property_value)

    elif isinstance(property_value, float):
        formatting = ".2E" if property_value >= 1000 else ".3f"

        if "error" in dir(property_value):
            print(
                " \u00B1 ".join(
                    [  # unicode string is +-
                        f"{property_value:{formatting}}",
                        f"{property_value.error:{formatting}}",
                    ]
                ),
                "[unit]",
            )
        else:
            print(f"{property_value:{formatting}}", "[unit]")

    elif isinstance(property_value, core.listSameTypeParameter):
        from rich import box
        from rich.table import Table

        # ------
        # build table
        table = Table(
            header_style="bold blue",
            caption=f"({SSO.number}) {SSO.name}",
            box=box.SQUARE,
            show_footer=property_value.datatype is float,
            footer_style="dim",
        )

        # ------
        # add columns to table
        columns = ["shortbib", property_name, "method"]

        # add property dependent columns
        for property_singular, setup in PROPS.items():
            if "collection" in setup.keys() and setup["collection"] == property_name:
                break
        columns[-1:-1] = PROPS[property_singular]["extra_columns"]

        if property_value.datatype is float:
            columns[2:2] = ["error"]

        for c in columns:
            table.add_column(
                c,
                justify="right" if c != "shortbib" else "left",
                style=None if c != "shortbib" else "dim",
                footer="unit" if c in [property_name, "error"] else "",
            )

        # find column indices of preferred solution
        preferred_solution = getattr(SSO, property_singular).shortbib
        preferred_solution = [
            i
            for i, bib in enumerate(getattr(SSO, property_name).shortbib)
            if bib in preferred_solution
        ]

        # ------
        # add rows by evaluating values
        for i, p in enumerate(property_value):

            values = []

            for c in columns:

                # Get column value
                if c == property_name:
                    value = property_value[i]

                else:
                    value = getattr(property_value, c)[i]

                # Select formatting
                if isinstance(value, str):
                    values.append(value)
                elif isinstance(value, float):
                    formatting = ".2E" if value >= 1000 else ".3f"
                    values.append(f"{value:{formatting}}")

                # Bold print row if it belongs to the preferred solution
                #  if i in preferred_solution:
                #  values = [rf"[bold green]{v}[\bold green]" for v in values]

            table.add_row(
                *values, style="bold green" if i in preferred_solution else None
            )

        rprint(table)


def weighted_average(observable, error):
    """Computes weighted average of observable.

    Parameters
    ----------
    observable : np.ndarray
        Float values of observable
    error : np.ndarray
        Corresponding errors of observable.

    Returns
    -------
    (float, float)
        Weighted average and its standard error.
    """
    if len(observable) == 1:
        return (observable[0], error[0])

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
    return (avg, std_avg)


def echo_property(rock, prop):
    """Echo asteroid property for a single minor body.
    Print datacloud collections. Optionally open plots.

    Parameters
    ==========
    rock : rocks.Rock
        The asteroid Rock instance
    prop : str
        Asteroid property, attribute from JSON template
    """
    # TODO Add these as __str__ to classes
    if isinstance(prop, rocks.core.stringParameter):
        _echo_stringParameter(prop)
    elif isinstance(prop, rocks.core.intParameter):
        _echo_intParameter(prop)
    elif isinstance(prop, rocks.core.floatParameter):
        _echo_floatParameter(prop)
    elif isinstance(prop, rocks.core.propertyCollection):
        _echo_propertyCollection(rock, prop)
    elif isinstance(prop, rocks.core.listSameTypeParameter):
        _echo_listSameTyeParameter(prop)
    else:
        print(prop)

    sys.exit()
    # Check type: floatParameter, intParameter, strParameter, propertyCollection
    #  sys.exit()  # required for click


def _echo_stringParameter(prop):
    print(prop)


def _echo_intParameter(prop):
    if hasattr(prop, "unit"):
        unit = getattr(prop, "unit")
    else:
        unit = ""
    if hasattr(prop, "uncertainty"):
        uncert = getattr(prop, "uncertainty")
    else:
        uncert = ""

    if uncert:
        print(f"{prop:,} +- {uncert:,} {unit}")
    else:
        print(f"{prop}")


def _echo_floatParameter(prop):
    if hasattr(prop, "unit"):
        unit = getattr(prop, "unit")
    else:
        unit = ""
    if hasattr(prop, "uncertainty"):
        uncert = getattr(prop, "uncertainty")
    else:
        uncert = ""

    if uncert:
        print(f"{float(prop):.4} +- {float(uncert):.3} {unit}")
    else:
        print(f"{prop}")


def _echo_propertyCollection(rock, prop):
    from rich import box
    from rich.table import Table
    from rich import print as rprint

    # ------
    # build table
    table = Table(
        header_style="bold blue",
        caption=f"({rock.number}) {rock.name}",
        box=box.SQUARE,
        footer_style="dim",
    )

    DONT_PRINT = [
        "num",
        "name",
        "id",
        "iddataset",
        "title",
        "url",
        "doi",
        "bibcode",
        "link",
        "datasetname",
        "idcollection",
        "selection",
        "source",
        "resourcename"
    ]
    # keys are table property names
    keys = list(prop.__dict__.keys())
    for key in keys:

        # don't print all keys
        if key in DONT_PRINT:
            continue
        table.add_column(key)

    # values are entries for each field
    values = list(prop.__dict__.values())

    if isinstance(values[0], list):
        n = len(values[0])
    else:
        n = 1

    for i, entry in enumerate(range(n)):

        row = []

        for j, p in enumerate(prop.__dict__.values()):
            if keys[j] in DONT_PRINT:
                continue
            if isinstance(p, list):
                row.append(str(p[i]))
            else:
                row.append(str(p))

        style = "white"
        # TODO Implement decision trees
        #  if "selection" in keys:
        #  if prop.__dict__["selection"][i]:
        #  style = "bold green"

        table.add_row(*row, style=style)

    rprint(table)

    #  if hasattr(rock, prop):
    #  rocks.utils.pretty_print(rock, prop)

    #  prop = getattr(rock, prop)

    #  if hist or scatter:

    #  if not isinstance(prop, rocks.core.listSameTypeParameter):
    #  click.echo("\nPlotting is only implemented for property collections.")
    #  sys.exit()

    #  if prop.datatype is not float:
    #  click.echo("\nCan only plot properties of type float.")
    #  sys.exit()

    #  if hist:
    #  prop.hist(show=True)
    #  if scatter:
    #  prop.scatter(show=True)

    sys.exit()  # otherwise click prints Error


def _echo_listSameTyeParameter(prop):
    print(prop)
    # TODO Add weighted average for floatParameters
    # TODO Plots
    prop.scatter()




    # collection is attr_name in DATACLOUD_META
    # Parse arguments
    #  args = sys.argv[1:]

    #  for i, arg in enumerate(args):

    #  if arg in ["-s", "--scatter"]:
    #  args.pop(i)
    #  scatter = True
    #  break
    #  else:
    #  scatter = False

    #  for i, arg in enumerate(args):

    #  if arg in ["-h", "--hist"]:
    #  args.pop(i)
    #  hist = True
    #  break
    #  else:
    #  hist = False

    #  if len(args) > 2:
    #  raise TooManyRocksError("Provide one or no asteroid identifiers.")
    #  elif len(args) == 2:
    #  property_, name = args
    #  elif len(args) == 1:
    #  property_ = args[0]
    #  name = False

    #  # Perform property query
    #  return echo_property(property_, name, scatter=scatter, hist=hist)


# This needs to be available for name lookups and index selection
#  try:
#  NUMBER_NAME, NAME_NUMBER = read_index()
#  except FileNotFoundError:
#  click.echo("Asteroid index could not be found. " 'Run "rocks index" first.')
#  sys.exit()

# ------
# Measurement Methods Defintions
METHODS = {
    "avg": {"color": "black"},
    "std": {"color": "darkgrey"},
    # Space mission
    "SPACE": {"color": "gold", "marker": "X"},
    # 3D shape modeling
    "ADAM": {"color": "navy", "marker": "v"},
    "SAGE": {"color": "mediumblue", "marker": "^"},
    "KOALA": {"color": "slateblue", "marker": "<"},
    "Radar": {"color": "cornflowerblue", "marker": ">"},
    # LC with scaling
    "LC+OCC": {"color": "lightgreen", "marker": "v"},
    "LC+AO": {"color": "forestgreen", "marker": "^"},  # deprecated =LC+IM
    "LC+IM": {"color": "forestgreen", "marker": "^"},
    "LC+TPM": {"color": "darkgreen", "marker": "<"},
    "LC-TPM": {"color": "green", "marker": ">"},
    # Thermal models
    "STM": {"color": "grey", "marker": "D"},
    "NEATM": {"color": "grey", "marker": "o"},
    "TPM": {"color": "darkgrey", "marker": "s"},
    # Triaxial ellipsoid
    "TE-IM": {"color": "blue", "marker": "o"},
    # 2D on sky
    "OCC": {"color": "brown", "marker": "P"},
    "IM": {"color": "orange", "marker": "p"},
    "IM-PSF": {"color": "tomato", "marker": "H"},
    # Mass from binary
    "Bin-IM": {"color": "navy", "marker": "v"},
    "Bin-Genoid": {"color": "mediumblue", "marker": "^"},
    "Bin-PheMu": {"color": "slateblue", "marker": "<"},
    "Bin-Radar": {"color": "cornflowerblue", "marker": ">"},
    # Mass from deflection
    "DEFLECT": {"color": "brown", "marker": "D"},
    "EPHEM": {"color": "red", "marker": "o"},
    # Taxonomy
    "Phot": {"color": "red", "marker": "s"},
    "Spec": {"color": "red", "marker": "s"},
}


# ------
# Plotting definitions
PLOTTING = {
    "LABELS": {
        "diameter": "Diameter (km)",
        "mass": "Mass (kg)",
        "albedo": "Albedo",
    }
}

DATACLOUD_META = {
    "aams": {
        "attr_name": "aams",
    },
    "astdys": {
        "attr_name": "astdys",
    },
    "astorb": {
        "attr_name": "astorb",
    },
    "binarymp_tab": {
        "attr_name": "binaries",
    },
    "diamalbedo": {
        "attr_name": "diamalbedo",
    },
    "families": {
        "attr_name": "families",
    },
    "masses": {
        "attr_name": "masses",
    },
    "mpcatobs": {
        "attr_name": "mpc",
    },
    "pairs": {
        "attr_name": "pairs",
    },
    "taxonomy": {
        "attr_name": "taxonomies",
    },
}


class TooManyRocksError(Exception):
    pass
