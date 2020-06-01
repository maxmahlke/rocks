#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    Author: Max Mahlke
    Date: 01 April 2020

    Retrieve asteroid properties

    Part of the rocks CL tool
'''
import numpy as np
import pandas as pd

from rocks import names
from rocks import tools


# ------
# Retrieval methods
def get_property(property_, this, verbose, skip_quaero=False):
    '''Get asteroid property from SsODNet.

    Queries SsODNet datacloud. Can be passed a list of identifiers.
    First performs a quaero query to verify the asteroid identitfy.

    Parameters
    ----------

    property_ : str
        Asteroid property to get.
    this : str, int, float, list, np.array
        Asteroid name, designation, or number.
    verbose : bool
        Print request diagnostics.
    skip_quaero: bool
        Skip initial quaero query to verify asteroid identity.

    Returns
    -------
    tuple, list
        Depending on the requested property. The tuple contains the aggregated
        or most likely value of the property. The list contains all available
        data on this property. If input was list of
        identifiers, returns a list of tuples

    False, False
        Both return values are False if the query failed.
    '''
    if not isinstance(this, (list, np.ndarray)):
        this = [this]

    if not skip_quaero:
        names_numbers = names.get_name_number(this, verbose, progress=False)

        if isinstance(names_numbers, (tuple)):
            this = [names_numbers[0]]
        elif isinstance(names_numbers, (list)):
            this = [nn[0] for nn in names_numbers]

    properties = []

    for sso in this:

        data = tools.get_data(sso, verbose)

        # Check if query failed
        if data is False or\
                PROPS[property_]['datacloud_key'] not in data.keys():
            properties.append((False, False))
            continue

        # Get property
        data = data[PROPS[property_]['datacloud_key']]

        # Merge the results, identify the most likely
        selected, data = PROPS[property_]['select_one'](data)
        properties.append((selected, data))

    if len(properties) == 1:
        return properties[0]
    else:
        return properties


# ------
# Selection functions for different properties
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
    selected, str
        The selected taxonomic classification.
    taxa, dict
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

    '''

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

    # Compute points of each classification

    points = []

    for c in taxa:

        points.append(sum([POINTS[crit][c[crit].lower()] for crit in
                          ['scheme', 'waverange', 'method']]))

        c['selected'] = False

    # Find index of entry with most points. If maximum is shared,
    # return the most recent classification
    selected = taxa[-1 - np.argmax(points[::-1])]
    selected['selected'] = True

    return selected['class'], taxa


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

    The method ranking is given below. Albedos acquired with the top-ranked
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

    for method in [['SPACE'], ['ADAM', 'KOALA', 'SAGE', 'Radar'],
                   ['LC+TPM', 'TPM', 'LC+AO', 'LC+Occ', 'TE-IM'],
                   ['AO', 'Occ', 'IM'],
                   ['NEATM'], ['STM']]:

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
            averaged = (malb, emalb)
            break

    return averaged, albedos


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

    diameters = pd.DataFrame.from_dict(diameters)
    diameters['diameter'] = diameters['diameter'].astype(float)
    diameters['err_diameter'] = diameters['err_diameter'].astype(float)

    # Extract methods
    methods = set(diameters.method.values)

    # Check methods by hierarchy. If several results on
    # same level, compute weighted mean
    diameters['selected'] = False  # keep track of albedos used for mean

    for method in [['SPACE'], ['ADAM', 'KOALA', 'SAGE', 'Radar'],
                   ['LC+TPM', 'TPM', 'LC+AO', 'LC+Occ', 'TE-IM'],
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
            averaged = (mdiam, emdiam)
            break

    return averaged, diameters



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
            averaged = (mmass, emmass)
            break

    return averaged, masses



# ------
# Properties metadata
PROPS = {
    'taxonomy': {

        # Selection logic for multiple results
        'select_one': select_taxonomy,
        'datacloud_key': 'taxonomy',

    },

    'albedo': {
        'select_one': select_albedo,
        'datacloud_key': 'diamalbedo',
    },

    'diameter': {
        'select_one': select_diameter,
        'datacloud_key': 'diamalbedo',
    },

    'mass': {
        'select_one': select_mass,
        'datacloud_key': 'masses',
    },
}
