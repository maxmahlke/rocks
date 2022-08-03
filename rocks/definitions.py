#!/usr/bin/env python3
import numpy as np
import pandas as pd


def rank_properties(prop_name, obs):
    """Select ranking method based on property name.

    Parameters
    ----------
    prop_name : str
        The property to rank.
    obs : dict
        The observations including metadata


    Returns
    -------
    list of bool
        Entry "preferred" in propertyCollection, True if preferred, else False
    """
    if prop_name in ["taxonomy", "taxonomies"]:
        return select_taxonomy(obs)
    elif prop_name in ["mass", "masses"]:
        return select_numeric_property(obs, "mass")
    elif prop_name in ["albedo", "albedos"]:
        return select_numeric_property(obs, "albedo")
    elif prop_name in ["diameter", "diameters"]:
        return select_numeric_property(obs, "diameter")
    else:
        return [True for i in obs]


def select_taxonomy(taxonomies):
    """Select a single taxonomic classification from multiple choices.

    Evaluates the wavelength ranges, methods, schemes, and recency of
    classification.

    Parameters
    ----------
    taxonomies: dict
        Taxonomic classifications retrieved from SsODNet:datacloud.

    Returns
    -------
    list of bool
        True if preferred, else False
    """
    POINTS = {
            "scheme": {"mahlke": 5, "bus-demeo": 3, "bus": 2, "smass": 2, "tholen": 1, "sdss": 1},
        "waverange": {"vis": 1, "nir": 3, "visnir": 6, "mix": 4},
        "method": {"spec": 7, "phot": 3, "mix": 4},
    }

    # Make sure that all entries have the same length
    lengths = [len(values) for values in taxonomies.values()]

    if not all([max(lengths) == l for l in lengths]):
        for key, values in taxonomies.copy().items():
            if len(values) != max(lengths):
                del taxonomies[key]

    # Turn dicts of lists into list of dicts
    taxonomies = pd.DataFrame(taxonomies).to_dict(orient="records")

    # Compute points of each classification
    points = []

    for row in taxonomies:
        points.append(
            sum(
                [
                    POINTS[crit][row[crit].lower()]
                    for crit in ["scheme", "waverange", "method"]
                ]
            )
        )

    # Convert points to boolean
    preferred = [True if p == max(points) else False for p in points]
    return preferred


def select_numeric_property(obs, prop_name):
    """Select preferred observations ranking methods.

    Parameters
    ----------
    obs : dict
        Property measurements and metadata retrieved from SsODNet:datacloud.
    prop_name : str
        Name of the asteroid property.

    Returns
    -------
    list of bool
        True if selected, else False.

    Notes
    -----
    The method ranking depends on the observable.
    """
    RANKING = PROPERTIES[prop_name]["ranking"]
    methods = set(obs["method"])

    for method in RANKING:

        if set(method) & methods:  # method used at least once

            # Ensure that rows do not contain all 0 values, as can be the case
            # for albedo in diamalbedo
            if all(
                obs[prop_name][i] == 0
                for i, m in enumerate(obs["method"])
                if m in method
            ):
                continue

            # All entries using this method are preferred
            preferred = [True if m in method else False for m in obs["method"]]
            return preferred

    # No property entry is preferred (likely all 0), return list of False
    return [False for o in obs["number"]]


# In alphabetic order
PROPERTIES = {
    # TEMPLATE
    # property_name: Rock instance attribute name
    #   attribute: attribute key in datacloud
    #   collection: Rock instance attribute name for collection of parameters
    #               Use plural form
    #   extra_columns: names of additional columns to output on CLI
    #   ssodnet_path: json path to asteroid property
    #                 (to be replaced by ssoCard
    #   type: asteroid property type, float or str
    "albedo": {
        "ranking": [
            ["SPACE"],
            ["ADAM", "KOALA", "SAGE", "Radar"],
            ["LC+TPM", "TPM", "LC+AO", "LC+Occ", "TE-IM", "TE-Occ"],
            ["AO", "Occ", "IM"],
            ["NEATM"],
            ["STM"],
        ],
    },
    "diameter": {
        "ranking": [
            ["SPACE"],
            ["ADAM", "KOALA", "SAGE", "Radar"],
            ["LC+TPM", "TPM", "LC+AO", "LC+Occ", "TE-IM", "TE-Occ"],
            ["AO", "Occ", "IM"],
            ["NEATM"],
            ["STM"],
        ],
    },
    "mass": {
        "ranking": [
            ["SPACE"],
            ["Bin-Genoid"],
            ["Bin-IM", "Bin-Radar", "Bin-PheMu"],
            ["EPHEM", "DEFLECT"],
        ],
    },
}
