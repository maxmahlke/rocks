#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    Author: Max Mahlke
    Date: 13 March 2020

    Utility functions for rocks
'''
from functools import lru_cache
import json
import os.path as path
import sys
import time

import click
from iterfzf import iterfzf
import pandas as pd
import requests


def create_index():
    '''Create or update index of numbered SSOs.

    Notes
    -----
    The list is retrieved from the Minor Planet Center, at
    https://www.minorplanetcenter.net/iau/lists/NumberedMPs.txt

    It is saved in CSV format as ``.index`` in the package directory.
    '''
    print('Retrieving index from MPC..\r', end='')
    url = 'https://www.minorplanetcenter.net/iau/lists/NumberedMPs.txt'

    index = pd.read_fwf(
        url, colspecs=[(0, 7), (9, 29), (29, 41)],
        names=['number', 'name', 'designation'],
        dtype={'name': str, 'designation': str},
        converters={'number': lambda x: int(x.replace('(', ''))}
    )

    index['name'] = index['name'].fillna(index.designation)
    index = index.drop(columns=['designation'])

    path_index = path.join(path.dirname(path.abspath(__file__)),
                           '.index')
    index.to_csv(path_index, index=False)
    print('Retrieving index from MPC.. done.')


def read_index():
    '''Read local index of asteroid numbers and names.

    Returns
    -------
    dict
        Asteroid number: name
    dict
        Asteroid name: number

    Notes
    -----
    If the index file is older than 30 days, a reminder to update is
    displayed.
    '''
    path_index = path.join(path.dirname(path.abspath(__file__)),
                           '.index')

    # Check age of index file
    days_since_modification = (time.time() - path.getmtime(path_index)) /\
        (3600 * 24)

    if days_since_modification > 30:
        click.echo('The index file is more than 30 days old. '
                   'Consider updating with "rocks index".')
        time.sleep(1)  # so user doesn't miss the message

    index = pd.read_csv(path_index, dtype={'number': int, 'name': str})

    NUMBER_NAME = dict(zip(index.number, index['name']))
    NAME_NUMBER = dict(zip(index['name'], index.number))

    return NUMBER_NAME, NAME_NUMBER


def _fuzzy_desig_selection():
    '''Generator for fuzzy search of asteroid index file. '''

    NUMBER_NAME, _ = read_index()

    for number, name in NUMBER_NAME.items():
        yield f'{number} {name}'


def select_sso_from_index():
    '''Select SSO numbers and designations from interactive fuzzy search.

    Returns
    ------
    str
        asteroid name or designation
    int
        asteroid number

    Notes
    -----
    If the selection is interrupted with ctrl-c, ``(None, None)`` is returned.

    Examples
    --------
    >>> from rocks import tools
    >>> name, number = tools.select_sso_from_index()
    '''
    try:
        nuna = iterfzf(_fuzzy_desig_selection(), exact=True)
        number, *name = nuna.split()
    except AttributeError:  # no SSO selected
        return None, None
    return ' '.join(name), int(number)


# ------
# SsODNet functions
@lru_cache(128)
def get_data(id_, verbose=True):
    '''Get asteroid data from SsODNet:datacloud.

    Performs a GET request to SsODNet:datacloud for a single asteroid and
    property. Checks validity of data and extracts it from response.

    Parameters
    ----------
    id_ : str, int
        Asteroid name, designation, or number.
    verbose : bool
        Print request diagnostics.

    Returns
    -------
    dict, bool
        Asteroid data, False if query failed or no data is available
    '''
    response = query_ssodnet(id_, verbose=verbose)

    # Check if query failed
    if response.status_code in [422, 500]:

        # Query SsODNet:quaero and repeat
        if verbose:
            click.echo(f'Query failed for {id_}.')
        return False

    # See if there is data available
    try:
        data = response.json()['data']
    except (json.decoder.JSONDecodeError, KeyError):
        if verbose:
            click.echo(f'Encountered JSON error for "{id_}".')
        return False

    # Select the right data entry
    if len(data.keys()) > 1:
        for k in [id_, f'{id_}_(Asteroid)']:
            if k in data.keys():
                key = k
                break
        else:
            key = list(data.keys())[0]
    else:
        key = list(data.keys())[0]

    # data = data[key]['datacloud']

    # if data is None:
        # if verbose:
            # click.echo(f'Datacloud is unavailable or no '
                       # f'data in SsODNet for {id_}')
        # return False
    return data[key]


def query_ssodnet(name, mime='json', verbose=False):
    '''Query SsODNet services.

    Includes validity check of response.

    Parameters
    ----------
    name : str, float
        Asteroid identifier
    mime : str
        Response mime type. Default is json.
    verbose : bool
        Print request diagnostics. Default is False.

    Returns
    -------
    r - requests.models.Response
        GET request response from SsODNet
    '''
    url = 'https://ssp.imcce.fr/webservices/ssodnet/api/datacloud.php'

    payload = {
        '-name': f'{name}',
        '-mime': mime,
        '-from': 'rocks',
    }

    r = requests.get(url, params=payload)

    _RESPONSES = {400: 'Bad request',
                  422: 'Unprocessable Entity',
                  500: 'Internal Error',
                  404: 'Not found'
                  }

    if r.status_code != 200:
        if r.status_code in _RESPONSES.keys() and verbose:
            message = f'HTTP code {r.status_code}: {_RESPONSES[r.status_code]}'
        else:
            message = f'HTTP code {r.status_code}: Unknown error'

        if verbose:
            click.echo(message)
            click.echo(r.url)
        return False
    return r


def echo_response(response, mime):
    '''Echo the formatted SsODNet response to STDOUT.

    The echo function is based on the query mime type.

    Parameters
    ----------
    response : requests.models.Response
        SsODNet GET query response.
    mime : str
        Mime-type of response.
    '''
    if mime == 'json':
        data = response.json()
        click.echo(json.dumps(data, indent=2))

    elif mime == 'votable':
        for line in response.content.decode('utf-8').split('\n')[1:]:
            click.echo(line)
    else:
        click.echo(response.text)


# This needs to be available for name lookups and index selection
try:
    NUMBER_NAME, NAME_NUMBER = read_index()
except FileNotFoundError:
    if sys.argv[1] != 'index':
        click.echo('Asteroid index could not be found. '
                   'Run "rocks index" first.')
        sys.exit()
