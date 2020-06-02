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
        'taxonomy': {
            'datacloud_key': 'taxonomy',
        },
        'albedo': {
            'datacloud_key': 'diamalbedo',
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
