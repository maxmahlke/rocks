#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    Author: Max Mahlke
    Date: 11 February 2020

    rocks functions relating to names and designations
'''
from functools import lru_cache, partial
import multiprocessing as mp
import re
import warnings

import pandas as pd
import numpy as np
import requests
from tqdm import tqdm

from rocks import tools


def get_name_number(this, parallel=4, verbose=True, progress=True):
    ''' Get SSO name and number from an identifier.

    Does a local lookup for asteroid identifier in the index. If this fails,
    queries SsODNet:quaero. Can be passed a list of identifiers.
    Parallel queries by default.

    Parameters
    ----------

    this : str, int, float, list, np.array, pd.Series
        Asteroid name, designation, or number.
    parallel : int
        Number of cores to use for queries. Default is 4.
    verbose : bool
        Print request diagnostics. Default is True.
    progress : bool
        Show query progress. Default is True.

    Returns
    -------
    tuple, (str, int or float)
        Tuple containing asteroid name or designation as str and
        asteroid number as int, NaN if not numbered. If input was list of
        identifiers, returns a list of tuples

    Notes
    -----
    Use integer asteroid numbers as identifiers for fastest queries. Asteroid
    names or designations are queried case- and whitespace-insensitive.

    Examples
    --------
    >>> from rocks import names
    >>> names_numbers = names.get_name_number(['1950 RW', '2001je2', 'VESTA'])
    >>> print(names_numbers)
    [('Gyldenkerne', 5030), ('2001 JE2', 131353), ('Vesta', 4)]
    '''
    if isinstance(this, pd.Series):
        this = this.values
    if not isinstance(this, (list, np.ndarray)):
        this = [this]

    pool = mp.Pool(processes=parallel)
    qq = partial(_lookup_or_query, verbose=verbose)

    if progress:
        names_numbers = list(tqdm(pool.imap(qq, this),
                                  total=len(this)))
    else:
        names_numbers = list(pool.imap(qq, this))

    pool.close()
    pool.join()

    if len(names_numbers) == 1:
        return names_numbers[0]
    else:
        return names_numbers


def _lookup_or_query(sso, verbose=False):
    '''Tries local lookup of asteroid identifier, else calls quaero query.

    Parameters
    ----------
    sso : str, int, float
        Asteroid name, number, or designation.
    verbose : bool
        Print request diagnostics.

    Returns
    -------
    tuple, (str, int or float)
        Tuple containing asteroid name or designation as str and
        asteroid number as int, NaN if not numbered. If input was list of
        identifiers, returns a list of tuples.
    '''
    if isinstance(sso, (int, float, np.int64)):

        try:
            sso = int(sso)
        except ValueError:  # np.nan
            warnings.warn('This identifier appears to be NaN: {sso}')
            return np.nan, np.nan

        # Try local lookup
        if sso in tools.NUMBER_NAME.keys():
            return (tools.NUMBER_NAME[sso], sso)

    elif isinstance(sso, str):

        # String identifier. Perform some regex
        # tests to make sure it's well formatted

        # Asteroid number
        if sso.isnumeric():
            sso = int(sso)

            # Try local lookup
            if sso in tools.NUMBER_NAME.keys():
                return (tools.NUMBER_NAME[sso], sso)
            else:
                return _query_quaero(sso, verbose)

        # Asteroid name
        if re.match(r'^[A-Za-z]*$', sso):

            # Ensure proper capitalization
            sso = sso.capitalize()

        # Asteroid designation
        elif re.match(r'(^([1A][8-9][0-9]{2}[ _]?[A-Za-z]{2}[0-9]{0,3}$)|'
                      r'(^20[0-9]{2}[_ ]?[A-Za-z]{2}[0-9]{0,3}$))', sso):

            # Ensure whitespace between year and identifier
            sso = re.sub(r'[\W_]+', '', sso)
            ind = re.search(r'[A18920]{1,2}[0-9]{2}', sso).end()
            sso = f'{sso[:ind]} {sso[ind:]}'

            # Replace A by 1
            sso = re.sub(r'^A', '1', sso)

            # Ensure uppercase
            sso = sso.upper()

        # Palomar-Leiden / Transit
        if re.match(r'^[1-9][0-9]{3}[ _]?(P-L|T-[1-3])$', sso):

            # Ensure whitespace
            sso = re.sub(r'[ _]+', '', sso)
            sso = f'{sso[:4]} {sso[4:]}'

        # Comet
        if re.match(r'(^[PDCXAI]/[- 0-9A-Za-z]*)', sso):
            pass

        # Remaining should be unconvential asteroid names like
        # "G!kun||'homdima" or packed designaitons

        # Try local lookup
        if sso in tools.NAME_NUMBER.keys():
            return (sso, tools.NAME_NUMBER[sso])
    else:
        print(f'Did not understand type of identifier: {type(sso)}'
              f'\nShould be integer, float, or string.')
        return (np.nan, np.nan)

    # Else, query quaero
    return _query_quaero(sso, verbose)


@lru_cache(128)
def _query_quaero(sso, verbose=False):
    '''Quaero query and result parsing for a single object.

    Parameters
    ----------
    sso : str, int, float
        Asteroid name, number, or designation.
    verbose : bool
        Print request diagnostics. Default is False.

    Returns
    -------
    tuple, (str, int or float)
        Tuple containing asteroid name or designation as str and
        asteroid number as int, NaN if not numbered. If input was list of
        identifiers, returns a list of tuples.
    '''

    # Build query
    url = 'https://api.ssodnet.imcce.fr/quaero/1/sso/search'

    params = {'q': f'type:("Dwarf Planet" OR Asteroid OR Comet)'
                   f' AND "{sso}"~0',  # no fuzzy search
              'from': 'rocks',
              'limit': 10000}

    # Send GET request
    r = requests.get(url, params=params, timeout=5)
    j = r.json()

    # No match found
    if 'data' not in j.keys():  # pragma: no cover
        if verbose:
            print(f'Could not find data for identifier {sso}.')
            print(r.url)
        return (np.nan, np.nan)

    if not j['data']:
        if verbose:
            print(f'Could not find match for identifier {sso}.')
            print(r.url)
        return (np.nan, np.nan)

    # Exact search performed
    data = j['data'][0]
    name = data['name']

    # Take lowest numerical alias as number
    numeric = [int(a) for a in data['aliases'] if a.isnumeric()]
    number = min(numeric) if numeric else np.nan

    return (name, number)


def to_filename(name):
    '''Creates suitable filename from asteroid name or designation.

    Parameters
    ----------

    name : str
        Asteroid name or designation

    Returns
    -------

    str
        Sanitized asteroid name.

    Examples
    --------

    >>> from rocks import names
    >>> names.to_filename("G!kun||'homdima")
    'Gkunhomdima'
    '''
    return re.sub(r'[^\w-]', '', name)
