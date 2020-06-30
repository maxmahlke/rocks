# -*- coding: utf-8 -*-
'''
    Author: Max Mahlke
    Date: 01 April 2020

    Retrieve asteroid properties

    Part of the rocks CLI suite
'''
import numpy as np
import pandas as pd

from rocks import tools


def select_taxonomy(taxa, from_Rock=False):
    '''Select a single taxonomic classification from multiple choices.

    Evaluates the wavelength ranges, methods, schemes, and recency of
    classification.

    Parameters
    ----------
    taxa : dict
        Taxonomic classifications retrieved from SsODNet:datacloud.
    from_Rock : bool
        Whether the call is done by a Rock instance.

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
    if not isinstance(taxa, (list, dict)):
        # no classification
        # hotfix for classy
        return {'class': np.nan, 'scheme': np.nan,
                'method': np.nan, 'shortbib': np.nan}

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
    # if we have several asteroids, the input will be a list of lists of
    # classifications
    if isinstance(taxa[0], list):
        return [select_taxonomy(t, from_Rock) for t in taxa]
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
    selected_taxonomy['index_selection'] = [-1 - np.argmax(points[::-1])]
    return selected_taxonomy


def select_numeric_property(measurements, property_name):
    '''Aggregate multiple measurements of property by ranking methods and
    computing the weighted average.

    Parameters
    ----------
    measurements : dict
        Property measurements and metadata retrieved from SsODNet:datacloud.
    property_name : str
        Name of the asteroid property to aggregate.

    Returns
    -------
    selected, dict
        The collapsed selected entries of the input measurements, with
        additional entries for the weighted average

    Notes
    -----
    The method ranking depends on the observable.
    '''
    obs = pd.DataFrame.from_dict(measurements)
    obs[property_name] = obs[property_name].astype(float)
    obs[f'err_{property_name}'] = obs[f'err_{property_name}'].astype(float)

    # Check methods by hierarchy. If several results on
    # same level, compute weighted mean
    obs['selected'] = False

    RANKING = PROPERTIES[property_name]['ranking']
    methods = set(obs.method.values)

    for method in RANKING:

        if set(method) & methods:  # method used at least once

            prop_values = obs.loc[
                obs.method.isin(method), property_name
            ].values
            prop_errors = obs.loc[
                obs.method.isin(method), f'err_{property_name}'
            ].values

            # NEATM and STM are inherently inaccurate
            if 'NEATM' in method or 'STM' in method:
                prop_errors = np.array([np.sqrt(ep**2 + (0.1 * p)**2)
                                        for ep, p in
                                        zip(prop_errors, prop_values)])

                obs.loc[obs.method.isin(method),
                        f'err_{property_name}'] = prop_errors

            # Compute weighted mean
            avg, std_avg = tools.weighted_average(prop_values, prop_errors)

            # Mark albedos used in computation
            obs.loc[obs.method.isin(method), 'selected'] = True
            break

    # Return dictionary with averaged, uncertainty, and merged attirbutes of
    # used data entries
    merged = obs[obs.selected].to_dict(orient='list')

    merged[property_name] = avg
    merged['error'] = std_avg
    merged['index_selection'] = obs.loc[obs.selected].index

    return merged


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

    'albedo': {
        'attribute': 'albedo',
        'collection': 'albedos',
        'extra_columns': [],
        'ranking': [['SPACE'], ['ADAM', 'KOALA', 'SAGE', 'Radar'],
                    ['LC+TPM', 'TPM', 'LC+AO', 'LC+Occ', 'TE-IM'],
                    ['AO', 'Occ', 'IM'],
                    ['NEATM'], ['STM']],
        'selection': select_numeric_property,
        'ssodnet_path': ['datacloud', 'diamalbedo'],
        'type': float,
    },

    'H': {
        'attribute': 'H',
        'ssodnet_path': ['datacloud', 'astdys'],
        'selection': lambda x, _: x[0],  # do nothing
        'type': float,
    },

    'eccentricity': {
        'attribute': 'Eccentricity',
        'ssodnet_path': ['datacloud', 'astorb'],
        'selection': lambda x, _: x[0],  # do nothing
        'type': float,
    },

    'diameter': {
        'attribute': 'diameter',
        'collection': 'diameters',
        'extra_columns': [],
        'ranking': [['SPACE'], ['ADAM', 'KOALA', 'SAGE', 'Radar'],
                    ['LC+TPM', 'LC-TPM', 'TPM', 'LC+AO', 'LC+IM',
                     'LC+Occ', 'TE-IM'],
                    ['AO', 'Occ', 'IM'],
                    ['NEATM'], ['STM']],
        'selection': select_numeric_property,
        'ssodnet_path': ['datacloud', 'diamalbedo'],
        'type': float,
    },

    'mass': {
        'attribute': 'mass',
        'collection': 'masses',
        'extra_columns': [],
        'ranking': [['SPACE'], ['Bin-Genoid'],
                    ['Bin-IM', 'Bin-Radar', 'Bin-PheMu'],
                    ['EPHEM', 'DEFLECT']],
        'selection': select_numeric_property,
        'ssodnet_path': ['datacloud', 'masses'],
        'type': float,
    },

    'semimajoraxis': {
        'attribute': 'SemimajorAxis',
        'ssodnet_path': ['datacloud', 'astorb'],
        'selection': lambda x, _: x[0],  # do nothing
        'type': float,
    },

    'taxonomy': {
        'attribute': 'class',
        'collection': 'taxonomies',
        'extra_columns': ['scheme', 'waverange'],
        'selection': select_taxonomy,
        'ssodnet_path': ['datacloud', 'taxonomy'],
        'type': str,
    },


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
    'Sv': 'S', 'Svw': 'S',
    'T': 'T',
    'O': 'O',
    'R': 'R',
    'Q': 'Q', 'QV': 'Q', 'QO': 'Q',
    'V': 'V',
    'Vw': 'V',
    'Xc': 'X', 'XC': 'X', 'Xe': 'X', 'Xk': 'X', 'XL': 'X', 'X': 'X',
    'Xn': 'X', 'XL': 'X', 'Xt': 'X', 'XC': 'X',
    'XD': 'X',
    'E': 'E',
    'M': 'M',
    'PD': 'P',
    'P': 'P', 'PC': 'P',
}
