#!/usr/bin/env python3
import numpy as np


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
        "scheme": {"bus-demeo": 3, "bus": 2, "smass": 2, "tholen": 1, "sdss": 1},
        "waverange": {"vis": 1, "nir": 3, "visnir": 6, "mix": 4},
        "method": {"spec": 7, "phot": 3, "mix": 4},
    }

    taxonomies = [dict(zip(taxonomies, t)) for t in zip(*taxonomies.values())]

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
                [
                    obs[prop_name][i] == 0
                    for i, m in enumerate(obs["method"])
                    if m in method
                ]
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


# Classes to complexes mapping
CLASS_TO_COMPLEX = {
    "A": "A",
    "Ad": "U",
    "AQ": "U",
    "AS": "U",
    "AU": "U",
    "AV": "U",
    "B": "B",
    "BC": "C",
    "BCF": "C",
    "BCU": "U",
    "BFC": "C",
    "BFU": "U",
    "BFX": "U",
    "Bk": "U",
    "BU": "B",
    "C": "C",
    "Caa": "C",
    "Cb": "C",
    "CB": "C",
    "CBU": "C",
    "CD": "U",
    "CDX": "U",
    "CF": "C",
    "CFB": "C",
    "CFU": "U",
    "CFXU": "U",
    "Cg": "C",
    "CG": "C",
    "CGSU": "U",
    "CGTP": "U",
    "CGU": "U",
    "Cgx": "C",
    "CL": "U",
    "CO": "U",
    "CP": "U",
    "CPF": "U",
    "CPU": "U",
    "CQ": "U",
    "CS": "U",
    "CSGU": "U",
    "CSU": "U",
    "CTGU": "U",
    "CU": "U",
    "CX": "U",
    "CXF": "U",
    "Cgh": "Ch",
    "Ch": "Ch",
    "D": "D",
    "DCX": "U",
    "DL": "D",
    "DP": "D",
    "DU": "D",
    "Ds": "D",
    "DS": "D",
    "DSU": "D",
    "DT": "D",
    "DTU": "D",
    "DU": "D",
    "DX": "D",
    "DXCU": "D",
    "E": "E",
    "EM": "X",
    "EU": "U",
    "F": "C",
    "FBCU": "U",
    "FC": "C",
    "FCB": "C",
    "FCU": "U",
    "FCX": "U",
    "FP": "U",
    "FU": "U",
    "FX": "U",
    "FXU": "U",
    "G": "C",
    "GC": "C",
    "GS": "U",
    "J": "V",
    "K": "K",
    "Kl": "U",
    "L": "L",
    "LA": "U",
    "Ld": "L",
    "LQ": "U",
    "LS": "U",
    "M": "M",
    "MU": "U",
    "O": "O",
    "OV": "U",
    "P": "P",
    "PC": "U",
    "PCD": "U",
    "PD": "U",
    "PDC": "U",
    "PF": "U",
    "PU": "U",
    "Q": "Q",
    "QO": "Q",
    "QRS": "U",
    "QSV": "U",
    "QV": "U",
    "Qw": "Q",
    "R": "R",
    "S": "S",
    "SA": "S",
    "Sa": "S",
    "SC": "U",
    "SCTU": "U",
    "SD": "U",
    "SDU": "U",
    "SG": "U",
    "Sk": "S",
    "Sl": "S",
    "SMU": "U",
    "SO": "S",
    "Sq": "S",
    "SQ": "S",
    "Sqw": "S",
    "Sr": "S",
    "SR": "S",
    "Srw": "S",
    "ST": "U",
    "STD": "U",
    "STGD": "U",
    "STU": "U",
    "SU": "U",
    "SV": "S",
    "Sv": "S",
    "Svw": "S",
    "Sw": "S",
    "SX": "U",
    "T": "T",
    "TCG": "U",
    "TD": "U",
    "TDG": "U",
    "TDS": "U",
    "TS": "U",
    "TSD": "U",
    "TX": "U",
    "V": "V",
    "Vw": "V",
    "X": "X",
    "XB": "U",
    "Xc": "X",
    "XC": "U",
    "XCU": "U",
    "XD": "U",
    "XDC": "U",
    "Xe": "X",
    "XF": "U",
    "XFC": "U",
    "XFCU": "U",
    "XFU": "U",
    "Xk": "X",
    "XL": "U",
    "Xn": "X",
    "XS": "U",
    "XSC": "U",
    "XSCU": "U",
    "XT": "U",
    "Xt": "X",
    "XU": "U",
    "Z": "U",
    np.nan: np.nan,
    None: np.nan,
    float("nan"): np.nan,
}
