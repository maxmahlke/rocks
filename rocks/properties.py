# -*- coding: utf-8 -*-
'''
    Author: Max Mahlke
    Date: 01 April 2020

    Retrieve asteroid properties

    Part of the rocks CLI suite
'''
import numpy as np
import pandas as pd


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

    return selected_taxonomy


def select_albedo(albedos):
    '''Compute a single albedo value from multiple measurements.

    Evaluates the methods and computes the weighted average of equally ranked
    methods.

    Parameters
    ----------
    albedos : dict
        Albedo measurements and metadata retrieved from SsODNet:datacloud.

    Returns
    -------
    averaged, tuple
        The average albedo and its uncertainty.
    albedos, dict
        The input dictionary, with an additional key 'selected'. True if the
        item was used in the computation of the average, else False.


    Notes
    -----

    The method ranking is given below. Albeods acquired with the top-ranked
    method available are used for the weighted average computation. Albedos
    observed with NEATM or STM get an additional 10% uncertainty added.

    .. code-block:: python

      ['SPACE']
      ['ADAM', 'KOALA', 'SAGE', 'Radar']
      ['LC+TPM', 'TPM', 'LC+AO', 'LC+Occ', 'TE-IM']
      ['AO', 'Occ', 'IM']
      ['NEATM']
      ['STM']

    '''
    albedos = pd.DataFrame.from_dict(albedos)
    albedos['albedo'] = albedos['albedo'].astype(float)
    albedos['err_albedo'] = albedos['err_albedo'].astype(float)

    # Remove entries containing only diameters
    albedos = albedos[albedos.albedo > 0]
    methods = set(albedos.method.values)

    # Check methods by hierarchy. If several results on
    # same level, compute weighted mean
    albedos['selected'] = False  # keep track of albedos used for mean

    RANKING = [['SPACE'], ['ADAM', 'KOALA', 'SAGE', 'Radar'],
               ['LC+TPM', 'TPM', 'LC+AO', 'LC+Occ', 'TE-IM'],
               ['AO', 'Occ', 'IM'],
               ['NEATM'], ['STM']]

    for method in RANKING:

        if set(method) & methods:  # at least one element in common

            albs = albedos.loc[albedos.method.isin(method),
                               'albedo'].values
            ealbs = albedos.loc[albedos.method.isin(method),
                                'err_albedo'].values

            # NEATM and STM are inherently inaccurate
            if 'NEATM' in method or 'STM' in method:
                ealbs = np.array([np.sqrt(ea**2 + (0.1 * a)**2) for
                                  ea, a in zip(ealbs, albs)])

                albedos.loc[albedos.method.isin(method),
                            'err_albedo'] = ealbs

            # Compute weighted mean
            weights = 1 / ealbs

            malb = np.average(albs, weights=weights)
            emalb = 1 / np.sum(weights)

            # Mark albedos used in computation
            albedos.loc[albedos.method.isin(method),
                        'selected'] = True
            break

    # Return dictionary with averaged, uncertainty, and merged attirbutes of
    # used data entries
    merged = albedos[albedos.selected].to_dict(orient='list')
    merged['albedo'] = malb
    merged['error'] = emalb
    return merged


def select_diameter(diameters):
    '''Compute a single diameter value from multiple measurements.

    Evaluates the methods and computes the weighted average of equally ranked
    methods.

    Parameters
    ----------
    diameters : dict
        Diameter measurements and metadata retrieved from SsODNet:datacloud.

    Returns
    -------
    averaged, tuple
        The average diameter and its uncertainty.
    diameters, dict
        The input dictionary, with an additional key 'selected'. True if the
        item was used in the computation of the average, else False.

    Notes
    -----
    The method ranking is given below. Diameters acquired with the top-ranked
    method available are used for the weighted average computation. Diameters
    observed with NEATM or STM get an additional 10% uncertainty added.

    .. code-block:: python

      ['SPACE']
      ['ADAM', 'KOALA', 'SAGE', 'Radar']
      ['LC+TPM', 'TPM', 'LC+AO', 'LC+Occ', 'TE-IM']
      ['AO', 'Occ', 'IM']
      ['NEATM']
      ['STM']

    '''
    if diameters is False:
        return np.nan

    diameters = pd.DataFrame.from_dict(diameters)
    diameters['diameter'] = diameters['diameter'].astype(float)
    diameters['err_diameter'] = diameters['err_diameter'].astype(float)

    # Extract methods
    methods = set(diameters.method.values)

    # Check methods by hierarchy. If several results on
    # same level, compute weighted mean
    diameters['selected'] = False  # keep track of albedos used for mean

    for method in [['SPACE'], ['ADAM', 'KOALA', 'SAGE', 'Radar'],
                   ['LC+TPM', 'LC-TPM', 'TPM', 'LC+AO', 'LC+IM',
                    'LC+Occ', 'TE-IM'],
                   ['AO', 'Occ', 'IM'],
                   ['NEATM'], ['STM']]:

        if set(method) & methods:  # at least one element in common

            diams = diameters.loc[diameters.method.isin(method),
                                  'diameter'].values
            ediams = diameters.loc[diameters.method.isin(method),
                                   'err_diameter'].values

            # NEATM and STM are inherently inaccurate
            if 'NEATM' in method or 'STM' in method:
                ediams = np.array([np.sqrt(ea**2 + (0.1 * a)**2) for
                                   ea, a in zip(ediams, diams)])

                diameters.loc[diameters.method.isin(method),
                              'err_albedo'] = ediams

            # Compute weighted mean
            weights = 1 / ediams

            mdiam = np.average(diams, weights=weights)
            emdiam = 1 / np.sum(weights)

            # Mark diameters used in computation
            diameters.loc[diameters.method.isin(method),
                          'selected'] = True
            break

    # Return dictionary with averaged, uncertainty, and merged attirbutes of
    # used data entries
    merged = diameters[diameters.selected].to_dict(orient='list')
    merged['diameter'] = mdiam
    merged['error'] = emdiam
    return merged


def select_mass(masses):
    '''Compute a single mass estimate from multiple measurements.

    Evaluates the methods and computes the weighted average of equally ranked
    methods.

    Parameters
    ----------
    masses : dict
        Mass estimates and metadata retrieved from SsODNet:datacloud.

    Returns
    -------
    averaged, tuple
        The average mass and its uncertainty.
    masses, dict
        The input dictionary, with an additional key 'selected'. True if the
        item was used in the computation of the average, else False.

    Notes
    -----
    The method ranking is given below. Masses acquired with the top-ranked
    method available are used for the weighted average computation.

    .. code-block:: python

      ['SPACE']
      ['Bin-Genoid']
      ['Bin-IM', 'Bin-Radar', 'Bin-PheMu']
      ['EPHEM', 'DEFLECT']

    '''
    if masses is False:
        return np.nan

    masses = pd.DataFrame.from_dict(masses)
    masses['mass'] = masses['mass'].astype(float)
    masses['err_mass'] = masses['err_mass'].astype(float)

    # Extract methods
    methods = set(masses.method.values)

    # Check methods by hierarchy. If several results on
    # same level, compute weighted mean
    masses['selected'] = False  # keep track of albedos used for mean

    for method in [['SPACE'], ['Bin-Genoid'],
                   ['Bin-IM', 'Bin-Radar', 'Bin-PheMu'],
                   ['EPHEM', 'DEFLECT']]:

        if set(method) & methods:  # at least one element in common

            m = masses.loc[masses.method.isin(method),
                           'mass'].values
            dm = masses.loc[masses.method.isin(method),
                            'err_mass'].values

            # Compute weighted mean
            weights = 1 / dm

            mmass = np.average(m, weights=weights)
            emmass = 1 / np.sum(weights)

            # Mark masses used in computation
            masses.loc[masses.method.isin(method),
                       'selected'] = True
            break

    # Return dictionary with averaged, uncertainty, and merged attirbutes of
    # used data entries
    merged = masses[masses.selected].to_dict(orient='list')
    merged['mass'] = mmass
    merged['error'] = emmass
    return merged


# In alphabetic order
PROPERTIES = {

    # TEMPLATE
    # property_name : Rock instance attribute name
    #   attribute: attribute key in datacloud
    #   collection: Rock instance attribute name for collection of parameters
    #               Use plural form
    #   ssodnet_path: json path to asteroid property
    #                 (to be replaced by ssoCard
    #   type: asteroid property type, float or str

    'albedo': {
        'attribute': 'albedo',
        'collection': 'albedos',
        'selection': select_albedo,
        'ssodnet_path': ['datacloud', 'diamalbedo'],
        'type': float,
    },

    'diameter': {
        'attribute': 'diameter',
        'collection': 'diameters',
        'selection': select_diameter,
        'ssodnet_path': ['datacloud', 'diamalbedo'],
        'type': float,
    },

    'mass': {
        'attribute': 'mass',
        'collection': 'masses',
        'selection': select_mass,
        'ssodnet_path': ['datacloud', 'masses'],
        'type': float,
    },

    'taxonomy': {
        'attribute': 'class',
        'collection': 'taxonomies',
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
