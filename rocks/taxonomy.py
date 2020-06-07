#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Author: Max Mahlke
    Date: 11 February 2020

    Library for rocks functions related to taxonomy
'''
import numpy as np

from rocks import properties


def get_taxonomy(sso, **kwargs):

    data = properties.get_property('taxonomy', sso, **kwargs)

    # Merge the results, identify the most likely
    if isinstance(data, float):
        if np.isnan(data):
            return (np.nan, np.nan)

    selected, data = select_taxonomy(data)
    return (selected, data)


def select_taxonomy(taxa):
    '''Select a single taxonomic classification from multiple choices.

    Evaluates the wavelength ranges, methods, schemes, and recency of
    classification.

    Parameters
    ----------
    taxa : dict
        Taxonomic classifications retrieved from SsODNet:datacloud.

    Returns
    -------
    (class, complex) : tuple of str
        The selected taxonomic classification and the complex.
    taxa : dict
        The input dictionary, with an additional key 'selected'. True if the
        item was selected, else False.

    Notes
    -----
    .. code-block:: python

        POINTS = {
            'scheme': {
                'bus-demeo': 3,
                'bus': 2,
                'smass': 2,
                'tholen': 1,
                'sdss': 1,
            },

            'waverange': {
                'vis': 1,
                'nir': 3,
                'visnir': 6,
                'mix': 4
            },

            'method': {
                'spec': 7,
                'phot': 3,
                'mix': 4
            }
        }

    CLASS_TO_COMPLEX = {
        'A': 'A', 'AQ': 'A',
        'B': 'B', 'BU': 'B', 'F': 'B', 'FC': 'B',
        'C': 'C', 'Cb': 'C', 'Cg': 'C', 'Cgx': 'C', 'CX': 'C',
        'c': 'C', 'CB': 'C', 'CD': 'C', 'CX': 'C', 'CF': 'C', 'CG': 'C',
        'CL': 'C', 'Co': 'C', 'CO': 'C', 'CQ': 'C',
        'Cgh': 'Ch', 'Ch': 'Ch',
        'D': 'D', 'DP': 'D', 'DU': 'D', 'DS': 'D',
        'K': 'K',
        'L': 'L', 'Ld': 'L', 'LA': 'L', 'LQ': 'L',
        'Q': 'Q',
        'S': 'S', 'Sa': 'S', 'SD': 'S', 'Sk': 'S', 'Sl': 'S', 'Sq': 'S',
        'SQ': 'S', 'Sqw': 'S', 'Sr': 'S', 'Srw': 'S', 'Sw': 'S',
        's': 'S', 'SA': 'S', 'Sp': 'S', 'SV': 'S',
        'Sv': 'S',
        'T': 'T',
        'O': 'O',
        'R': 'R',
        'Q': 'Q', 'QV': 'Q', 'QO': 'Q',
        'V': 'V',
        'Xc': 'X', 'XC': 'X', 'Xe': 'X', 'Xk': 'X', 'XL': 'X', 'X': 'X',
        'Xn': 'X', 'XL': 'X', 'Xt': 'X', 'XC': 'X',
        'XD': 'X',
        'E': 'E',
        'M': 'M',
        'PD': 'P',
        'P': 'P', 'PC': 'P',
    }
    '''
    # Compute points of each classification
    points = []

    for c in taxa:

        points.append(sum([POINTS[crit][c[crit].lower()] for crit in
                          ['scheme', 'waverange', 'method']]))

        c['selected'] = False

    # Find index of entry with most points. If maximum is shared,
    # return the most recent classification
    selected_taxonomy = taxa[-1 - np.argmax(points[::-1])]
    selected_taxonomy['selected'] = True

    # return (selected['class'], CLASS_TO_COMPLEX[selected['class']]), taxa
    return selected_taxonomy


def class_to_complex(class_):
    '''Returns the complex that the input class belongs to.

    Can be passed single or multiple values.

    Parameters
    ----------
    class_ : str, list of str, np.ndarray
        The input class.

    Returns
    -------
    complex : str, list of str, np.ndarray, float
        The associated complex. Mirrors input variable type. NaN if class is
        unknown.

    Example
    -------
    >>> from rocks import taxonomy
    >>> taxonomy.class_to_complex('Sk')
    'S'
    >>> taxonomy.class_to_complex(['Sw', 'V', 'Cb', np.nan])
    ['S', 'V', 'C', nan]

    Notes
    -----
    The class-to-complex mapping is given below.
    '''

    if isinstance(class_, str):
        if class_ in CLASS_TO_COMPLEX.keys():
            return CLASS_TO_COMPLEX[class_]
        else:
            return np.nan
    elif isinstance(class_, float):
        if np.isnan(class_):
            return np.nan
    elif isinstance(class_, list):
        return [class_to_complex(c) for c in class_]
    elif isinstance(class_, np.ndarray):
        return np.array([class_to_complex(c) for c in class_])

    raise TypeError(f'Received unexpected type {type(class_)}, expected '
                    f'one of: str, list, np.ndarray')


POINTS = {
    'scheme': {
        'bus-demeo': 3,
        'bus': 2,
        'smass': 2,
        'tholen': 1,
        'sdss': 1,
    },

    'waverange': {
        'vis': 1,
        'nir': 3,
        'visnir': 6,
        'mix': 4
    },
    'method': {
        'spec': 7,
        'phot': 3,
        'mix': 4
    }
}

# Classes to complexes mapping
CLASS_TO_COMPLEX = {
    'A': 'A', 'AQ': 'A',
    'B': 'B', 'BU': 'B', 'F': 'B', 'FC': 'B',
    'C': 'C', 'Cb': 'C', 'Cg': 'C', 'Cgx': 'C', 'CX': 'C',
    'c': 'C', 'CB': 'C', 'CD': 'C', 'CX': 'C', 'CF': 'C', 'CG': 'C',
    'CL': 'C', 'Co': 'C', 'CO': 'C', 'CQ': 'C',
    'Cgh': 'Ch', 'Ch': 'Ch',
    'D': 'D', 'DP': 'D', 'DU': 'D', 'DS': 'D',
    'K': 'K',
    'L': 'L', 'Ld': 'L', 'LA': 'L', 'LQ': 'L',
    'Q': 'Q',
    'S': 'S', 'Sa': 'S', 'SD': 'S', 'Sk': 'S', 'Sl': 'S', 'Sq': 'S',
    'SQ': 'S', 'Sqw': 'S', 'Sr': 'S', 'Srw': 'S', 'Sw': 'S',
    's': 'S', 'SA': 'S', 'Sp': 'S', 'SV': 'S',
    'Sv': 'S',
    'T': 'T',
    'O': 'O',
    'R': 'R',
    'Q': 'Q', 'QV': 'Q', 'QO': 'Q',
    'V': 'V',
    'Xc': 'X', 'XC': 'X', 'Xe': 'X', 'Xk': 'X', 'XL': 'X', 'X': 'X',
    'Xn': 'X', 'XL': 'X', 'Xt': 'X', 'XC': 'X',
    'XD': 'X',
    'E': 'E',
    'M': 'M',
    'PD': 'P',
    'P': 'P', 'PC': 'P',
}
