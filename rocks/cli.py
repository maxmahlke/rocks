#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    Author: Max Mahlke
    Date: 12 February 2020

    rocks command line suite

    Call as:	rocks --help
'''

import os
import shutil
import sys
import webbrowser

import click
import requests

from rocks import names
from rocks import properties
from rocks import tools


@click.group()
def cli_rocks():
    '''CLI suite for minor body exploration.

    For more information: rocks docs

    '''
    pass


@cli_rocks.command()
def docs():
    '''Open rocks documentation in browser.

    '''
    path_to_index = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                 '../docs/_build/html/',
                                                 'index.html'))
    webbrowser.open(path_to_index, new=1)  # open docs in new window
    click.echo('Opening documentation in new window of your browser.')
    click.echo(path_to_index)


@cli_rocks.command()
def index():
    '''Create or update index of numbered SSOs.

    The list is retrieved from the Minor Planet Center, at
    https://www.minorplanetcenter.net/iau/lists/NumberedMPs.txt
    '''
    path_index = os.path.join(os.path.dirname(os.path.abspath(__file__)),
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


@cli_rocks.command()
@click.argument('this', required=1)
@click.option('--verbose', '-v', is_flag=True,
              help='Show request diagnostics.')
def identify(this, verbose):
    '''Get asteroid name and number from string input.

    Queries SsODNet:quaero with the string input. The output is
    printed to STDOUT.

    Parameters
    ----------

    this : str
        String to identify asteroid.
    verbose : bool, optional
        Flag to print SsODNet request diagnostics.
    '''
    name, number = names.get_name_number(this, verbose)
    click.echo(f'({number}) {name}')


@cli_rocks.command()
@click.argument('this', default='')
@click.option('--mime', '-m', default='json',
              type=click.Choice(['votable', 'html', 'text', 'json'],
                                case_sensitive=False),
              help='Mime type of SsODNet response')
@click.option('--verbose', '-v', is_flag=True,
              help='Show request diagnostics.')
def info(this, mime, verbose):
    '''Print available data on asteroid.

    Queries SsODNet:datacloud with the provided identification string
    or select asteroid from index.

    Parameters
    ----------

    this : str, optional
        Identification string for asteroid: name, designation, or number.
        If empty, the user can select the asteroid from the index.
    mime : {'votable', 'html', 'text', 'json'}, optional
        Mime-type of printed SsODNet:datacloud response. Default is json.
    verbose : bool, optional
        Flag to print SsODNet request diagnostics.
    '''

    if not this:
        this, _ = tools.select_sso_from_index()
    else:  # passed identified string, ensure that we know it
        this, _ = names.get_name_number(this, verbose)

    # Build query
    url = 'https://ssp.imcce.fr/webservices/ssodnet/api/datacloud.php'

    payload = {
        '-name': this,
        '-mime': mime,
        '-from': 'pythonClient',
    }

    # Execute query and handle responser
    response = tools.query_ssodnet(url, payload, verbose)
    tools.echo_response(response, payload)


@cli_rocks.command()
@click.argument('this', default='')
@click.option('--verbose', '-v', is_flag=True,
              help='Flag to print SsODNet request diagnostics.')
def taxonomy(this, verbose):
    '''Get asteroid taxonomic classification for a single minor body.

    Queries SsODNet:datacloud with the string input. SsODNet:quaero is used to
    identify the asteroid from the input string.  The output is printed
    to STDOUT.

    Parameters
    ----------

    this : str
        String to identify asteroid.
    verbose : bool, optional
    '''
    if not this:
        this, _ = tools.select_sso_from_index()

    selected, taxa = properties.get_property('taxonomy', this, verbose)

    if taxa is False:
        click.echo('No taxonomy on record.')
        sys.exit()

    # Print results
    click.echo(f'{"ref":20} {"class":5} {"scheme":11}'
               f'{"method":7} {"waverange":6}')
    for c in taxa:
        click.echo(f'{c["shortbib"]:20} {c["class"]:5} {c["scheme"]:11}'
                   f'{c["method"]:7} {c["waverange"]:10} '
                   f'[{"X" if c["selected"] else " "}]')


@cli_rocks.command()
@click.argument('this', default='')
@click.option('--verbose', '-v', is_flag=True,
              help='Flag to print SsODNet request diagnostics.')
def albedo(this, verbose):
    '''Get asteroid albedo measurements for a single minor body.

    Queries SsODNet:datacloud with the string input. SsODNet:quaero is used to
    identify the asteroid from the input string.  The output is printed
    to STDOUT.

    Parameters
    ----------

    this : str
        String to identify asteroid.
    verbose : bool, optional
    '''
    if not this:
        this, _ = tools.select_sso_from_index()

    averaged, albedos = properties.get_property('albedo', this, verbose)

    if albedos is False:
        click.echo('No albedo on record.')
        sys.exit()

    # Print results
    click.echo(f'{"ref":5} {"albedo":5} '
               f'{"err":5} {"method":8}')

    for ind, a in albedos.iterrows():
        click.echo(f'{a["iddataset"]:5} {a["albedo"]:.3f}  '
                   f'{a["err_albedo"]:.3f} {a["method"]:8} '
                   f'[{"X" if a["selected"] else " "}]')

    # weighted mean albedo and error
    click.echo(f'\n{"":6}{averaged[0]:.3f} +- {averaged[1]:.3f}')
