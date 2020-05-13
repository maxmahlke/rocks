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

import pandas as pd
import numpy as np
import requests
from tqdm import tqdm


def get_name_number(this, parallel=4, verbose=True, progress=True):
    ''' Get SSO name and number from an identifier.

    Queries SsODNet:quaero. Can be passed a list of identifiers.
    Parallel queries by default.

    Parameters
    ----------

    this : str, int, float, list, np.array, pd.Series
        Asteroid name, designation, or number.
    parallel : int
        Number of cores to use for queries. Default is 4.
        0 and 1 trigger serial querying.
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
    Use asteroid numbers as identifiers for fastest queries. Asteroid
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

    # Query
    if parallel in [0, 1]:
        if progress:
            names_numbers = list(tqdm(map(lambda x: _query_quaero(x, verbose),
                                          this), total=len(this)))
        else:
            names_numbers = list(map(lambda x: _query_quaero(x, verbose),
                                     this))
    else:
        pool = mp.Pool(processes=parallel)
        qq = partial(_query_quaero, verbose=verbose)

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


@lru_cache(128)
def _query_quaero(sso, verbose=False):
    '''Quaero query and result parsing for a single object.

    Parameters
    ----------

    sso : str, int, float
        Asteroid name, number, or designation
    verbose : bool
        Print request diagnostics

    Returns
    -------
    tuple, (str, int or float)
        Tuple containing asteroid name or designation as str and
        asteroid number as int, NaN if not numbered. If input was list of
        identifiers, returns a list of tuples
    '''
    if isinstance(sso, (int, float, np.int64)) or sso.isnumeric():
        sso = int(sso)
        fuzzy = False  # no fuzzy search
    elif isinstance(sso, str):
        sso = sso.replace(' ', '')
        fuzzy = True   # allow 2 character of fuzziness
    else:
        print(f'Did not understand type of identifier: {type(sso)}'
              f'\nShould be integer, float, or string.')
        return (np.nan, np.nan)

    # Build query
    url = 'https://api.ssodnet.imcce.fr/quaero/1/sso/search'

    params = {'q': f'type:("Dwarf Planet" OR Asteroid OR Comet)'
                   f' AND {sso}~{"1" if fuzzy else "0"}',
              'from': 'rocks',
              'limit': 100}

    # Send GET request
    r = requests.get(url, params=params, timeout=5)
    j = r.json()

    # No match found
    if 'data' not in j.keys():
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
    if not fuzzy:
        data = j['data'][0]
        name = data['name']
        number = sso
        return (name, number)

    # Fuzzy search performed
    if fuzzy:
        # Checks for:
        #    - whitespaces
        #    - capitalization
        for match in j['data']:

            sso = re.sub(r'\s+', '', sso.lower())

            aliases = [re.sub(r'\s+', '', a.lower()) for a in
                       match['aliases'] + [match['name']]]

            # If we find our match
            if sso in aliases:
                name = match['name']

                # Take lowest numeric alias as number
                numeric = [int(a) for a in aliases if a.isnumeric()]
                if numeric:
                    number = min(numeric)
                else:
                    number = np.nan

                return (name, number)
        else:
            if verbose:
                print(f'Could not find match for identifier {sso}')
                print(r.url)
            return (np.nan, np.nan)


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
    >>> names.to_filename('2012 P-L')
    2012P-L
    '''
    return re.sub(r'[^\w-]', '', name)
