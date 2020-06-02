#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Author: Max Mahlke
    Date: 27 May 2020

    Albedo methods for rocks CLI suite
'''
import numpy as np
import pandas as pd

from rocks import properties


RANKING = [['SPACE'], ['ADAM', 'KOALA', 'SAGE', 'Radar'],
           ['LC+TPM', 'TPM', 'LC+AO', 'LC+Occ', 'TE-IM'],
           ['AO', 'Occ', 'IM'],
           ['NEATM'], ['STM']]


def get_albedo(sso, **kwargs):

    data = properties.get_property('albedo', sso, **kwargs)

    # Merge the results, identify the most likely
    if isinstance(data, float):
        if np.isnan(data):
            return (np.nan, np.nan)

    selected, data = select_albedo(data)
    return (selected, data)


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
            averaged = (malb, emalb)
            break

    return averaged, albedos
