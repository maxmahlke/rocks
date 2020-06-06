#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Author: Max Mahlke
    Date: 01 April 2020

    Retrieve asteroid properties

    Part of the rocks CLI suite
'''
from functools import partial
import multiprocessing as mp

import numpy as np
import pandas as pd
from tqdm import tqdm

from rocks import names
from rocks import tools


def get_property(property_, sso, parallel=4, verbose=True,
                 progress=True, skip_quaero=False):
    '''Get asteroid property from SsODNet.

    Queries SsODNet datacloud. Can be passed a list of identifiers.
    First performs a quaero query to verify the asteroid identitfy.

    Parameters
    ----------
    property_ : str
        Asteroid property to get.
    sso : str, int, float, list, np.array, pd.Series
        Asteroid name, designation, or number.
    parallel : int
        Number of cores to use for queries. Default is 4.
    verbose : bool
        Print request diagnostics.
    progress : bool
        Show query progress. Default is True.
    skip_quaero: bool
        Skip initial quaero query to verify asteroid identity.

    Returns
    -------
    tuple, list
        Depending on the requested property. The tuple contains the aggregated
        or most likely value of the property. The list contains all available
        data on this property. If input was list of
        identifiers, returns a list of tuples

    np.nan, np.nan
        Both return values are NaN if the query failed.
    '''
    if isinstance(sso, pd.Series):
        sso = sso.values
    if not isinstance(sso, (list, np.ndarray)):
        sso = [sso]

    # Implemented properties
    PROPS = {
        'albedo': {
            'datacloud_key': 'diamalbedo',
        },
        'diameter': {
            'datacloud_key': 'diamalbedo',
        },
        'mass': {
            'datacloud_key': 'masses',
        },
        'taxonomy': {
            'datacloud_key': 'taxonomy',
        },
    }

    # Get name and number
    if not skip_quaero:
        names_numbers = names.get_name_number(sso, parallel=parallel,
                                              verbose=verbose, progress=False)

        if isinstance(names_numbers, (tuple)):
            sso = [names_numbers[0]]
        elif isinstance(names_numbers, (list)):
            sso = [nn[0] for nn in names_numbers]

    # Query the property
    pool = mp.Pool(processes=parallel)
    qq = partial(_query_property, dkey=PROPS[property_]['datacloud_key'],
                 verbose=verbose)

    if progress:
        properties = list(tqdm(pool.imap(qq, sso),
                               total=len(sso)))
    else:
        properties = list(pool.imap(qq, sso))

    pool.close()
    pool.join()

    # TMP
    if property_ == 'diameter':
        properties = [select_diameter(p) for p in properties]
    elif property_ == 'mass':
        properties = [select_mass(p) for p in properties]

    if len(properties) == 1:
        return properties[0]
    else:
        return properties


def _query_property(sso, dkey, verbose):
    '''Helper function performing the data query and selection for single
    identifer.

    Parameters
    ----------
    sso : str, int, float
        Asteroid name, designation, or number.
    dkey : str
        Asteroid property to get, given as datacloud key.
    verbose : bool
        Print request diagnostics.

    Returns
    -------
    dict
        Datacloud data corresponding to the asteroid property.
    np.nan
        NaN if no data found.
    '''
    if isinstance(sso, (float)):
        if np.isnan(sso):
            return np.nan

    data = tools.get_data(sso, verbose)

    # Check if query failed
    if data is False or dkey not in data.keys():
        return np.nan

    return data[dkey]


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
            averaged = (mmass, emmass)
            break

    return averaged, masses
