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
import shutil
import sys

import click
from iterfzf import iterfzf
import requests


def create_index():
    '''Create or update index of numbered SSOs.

    The list is retrieved from the Minor Planet Center, at
    https://www.minorplanetcenter.net/iau/lists/NumberedMPs.txt
    '''
    path_index = path.join(path.dirname(path.abspath(__file__)),
                           '.index')

    click.echo('Retrieving index from MPC..')
    r = requests.get(f'https://www.minorplanetcenter.net/'
                     f'iau/lists/NumberedMPs.txt', stream=True)

    # ------
    # Check that query worked
    total = r.headers.get('content-length')

    if total is None:
        click.echo('Remote query failed.')
        sys.exit()

    total = int(total)

    # Set up progress bar
    width, _ = shutil.get_terminal_size()
    width -= 2
    num_chunks = 1000

    response = []

    for data in r.iter_content(chunk_size=int(total / num_chunks)):

        response.append(data.decode('utf-8'))
        done = int(width * len(response) / num_chunks)

        sys.stdout.write('\r[{}{}]'.format('=' * done, ' ' * (width - done)))
        sys.stdout.flush()

    sys.stdout.write('\n')

    # ------
    # Parse index into number,name format
    response = ''.join(response)
    with open(path_index, 'w') as ind:
        for line in response.split('\n'):

            if not line:
                continue

            number, name = line.split()[:2]

            if name.isnumeric():  # it's a designation
                name = ' '.join(line.split()[1:3])

            number = number.strip('()')
            ind.write(f'{number},{name}\n')


def _fuzzy_desig_selection():
    '''Fuzzy search of asteroid index file.

    '''
    path_index = path.join(path.dirname(path.abspath(__file__)),
                           '.index')

    with click.open_file(path_index) as ind:
        for line in ind:
            number, name = line.strip().split(',')
            yield f'{number} {name}'


def select_sso_from_index():
    ''' Selcet SSO numbers and designations from interactive fuzzy search.

    The index is created with `rocks index`.
    The list is retrieved from the Minor Planet Center, at
    https://www.minorplanetcenter.net/iau/lists/NumberedMPs.txt


    Returns
    ------
    str
        asteroid name or designation
    int
        asteroid number

    '''
    numbername = iterfzf(_fuzzy_desig_selection(), exact=True)

    try:
        number, *name = numbername.split()
    except AttributeError:  # no SSO selected
        sys.exit()

    return ' '.join(name), int(number)


# ------
# SsODNet functions
@lru_cache(128)
def get_data(this, verbose=True):
    '''Get asteroid data from SsODNet:datacloud.

    Performs a GET request to SsODNet:datacloud for a single asteroid and
    property.

    Parameters
    ----------
    this : str, int
        Asteroid name, designation, or number.
    verbose : bool
        Print request diagnostics.

    Returns
    -------

    dict, bool
        Asteroid data, False if query failed or no data is available
    '''
    url = 'https://ssp.imcce.fr/webservices/ssodnet/api/datacloud.php'

    payload = {
        '-name': this,
        '-mime': 'json',
        '-from': 'rocks',
    }

    response = query_ssodnet(url, payload, verbose)

    # Check if query failed
    if response.status_code in [422, 500]:

        # Query SsODNet:quaero and repeat
        if verbose:
            click.echo(f'Query failed for {this}.')
        return False

    # See if there is data available
    try:
        data = response.json()['data']
    except (json.decoder.JSONDecodeError, KeyError):
        if verbose:
            click.echo(f'Encountered JSON error for {this}.')
        return False

    # Select the right data entry
    if len(data.keys()) > 1:
        for k in [this, f'{this}_(Asteroid)']:
            if k in data.keys():
                key = k
                break
        else:
            key = list(data.keys())[0]
    else:
        key = list(data.keys())[0]

    data = data[key]['datacloud']

    if data is None:
        if verbose:
            click.echo(f'No data in SsODNet for {this}')
        return False
    return data


def query_ssodnet(url, payload, verbose):
    '''Query SsODNet services.

    Includes validity check of response.

    Parameters
    ----------

    url : str
        Base url of GET request.
    payload : dict
        The GET request parameters. See
        https://ssp.imcce.fr/webservices/ssodnet/api/
        for options.
    verbose : bool
        Print request diagnostics.

    Returns
    -------
    r - requests.models.Response
        GET request response from SsODNet

    '''
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
    return r


def echo_response(response, payload):
    '''Echo the formatted SsODNet response to STDOUT.

    The echo function is based on the query mime type.

    Parameters
    ----------

    response : requests.models.Response
        SsODNet GET query response.
    payload : dict
        GET query payload.
    '''

    if '-mime' in payload.keys():
        if payload['-mime'] == 'json':
            data = response.json()
            click.echo(json.dumps(data, indent=2))

        elif payload['-mime'] == 'votable':
            for line in response.content.decode('utf-8').split('\n')[1:]:
                click.echo(line)
        else:
            click.echo(response.text)
    else:
        click.echo(response.text)


def read_index():
    '''Read local index of asteroid numbers and names.

    The index is created with `rocks index`.
    The list is retrieved from the Minor Planet Center, at
    https://www.minorplanetcenter.net/iau/lists/NumberedMPs.txt

    Returns
    -------

    dict
        Asteroid name: number
    dict
        Asteroid number: name
    '''
    path_index = path.join(path.dirname(path.abspath(__file__)),
                           '.index')

    NAME_NUMBER = {}
    NUMBER_NAME = {}

    with open(path_index) as index:
        for line in index:
            number, name = line.strip().split(',')

            number = int(number)

            NUMBER_NAME[number] = name
            NAME_NUMBER[name] = number
    return NAME_NUMBER, NUMBER_NAME
