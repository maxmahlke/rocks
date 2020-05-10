#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    Author: Max Mahlke
    Date: 11 February 2020

    rocks functions relating to names and designations
'''
import re

import numpy as np
import requests

from rocks import tools


def get_name_number(this, verbose=True):
    ''' Get SSO name and number from an identifier.

    Queries SsODNet:quaero. Can be passed a list of identifiers. In this case,
    the local asteroid name index is checked for matches first.

    Parameters
    ----------

    this : str, int, float, list, np.array
        Asteroid name, designation, or number.
    verbose : bool
        Print request diagnostics.

    Returns
    -------
    tuple, (str, int or float)
        Tuple containing asteroid name or designation as str and
        asteroid number as int, NaN if not numbered. If input was list of
        identifiers, returns a list of tuples

    Notes
    -----
    Asteroid names or designations are queried case- and
    whitespace-insensitive.

    Examples
    --------
    >>> from rocks import names
    >>> names_numbers = names.get_name_number(['1950 RW', '2001je2', 'VESTA'])
    >>> print(names_numbers)
    [('Gyldenkerne', 5030), ('2001 JE2', 131353), ('Vesta', 4)]
    '''
    # Check if it is a single asteroid or many
    if not isinstance(this, (list, np.ndarray)):
        this = [this]
        local = False
    else:
        # Read local index to speed up query
        NAME_NUMBER, NUMBER_NAME = tools.read_index()
        local = True

    names_numbers = []

    for sso in this:

        # Check nature of 'sso' identifier string
        if isinstance(sso, (int, float, np.int64)) or sso.isnumeric():
            sso = int(sso)
            fuzzy = False  # no fuzzy search

            if local:
                # Check in list of numbered asteroids for number
                if sso in NUMBER_NAME.keys():
                    names_numbers.append((NUMBER_NAME[sso], sso))
                    continue

        elif isinstance(sso, str):
            fuzzy = True   # allow 2 character of fuzziness

            if local:
                # Check in list of numbered asteroids for designation or name
                if sso in NAME_NUMBER.keys():
                    names_numbers.append((sso, NAME_NUMBER[sso]))
                    continue

        else:
            print(f'Did not understand type of identifier: {type(sso)}'
                  f'\nShould be integer, float, or string.')
            names_numbers.append((np.nan, np.nan))
            continue

        # Build query
        url = 'https://api.ssodnet.imcce.fr/quaero/1/sso/search'

        params = {'q': f'type:("Dwarf Planet" OR Asteroid OR Comet)'
                       f' AND {sso}~{"2" if fuzzy else "0"}',
                  'from': 'rocks',
                  'limit': 100}

        # Send GET request
        r = requests.get(url, params=params, timeout=5)
        j = r.json()

        # No match found
        if not j['data']:
            if verbose:
                print(f'Could not find match for identifier {sso}.')
                print(r.url)
            names_numbers.append((np.nan, np.nan))
            continue

        # Exact search performed
        if not fuzzy:
            data = j['data'][0]
            name = data['name']
            number = sso
            names_numbers.append((name, number))
            continue

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

                    names_numbers.append((name, number))
                    break
            else:
                if verbose:
                    print(f'Could not find match for identifier {sso}')
                    print(r.url)
                names_numbers.append((np.nan, np.nan))
                continue

    if len(names_numbers) == 1:
        return names_numbers[0]
    else:
        return names_numbers


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
