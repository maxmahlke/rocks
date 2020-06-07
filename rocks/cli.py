#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    Author: Max Mahlke
    Date: 12 February 2020

    rocks command line suite

    Call as:	rocks --help
'''
import os
import sys
import webbrowser

import click
import numpy as np

from rocks import albedo as alb
from rocks import names
from rocks import properties
from rocks import taxonomy as tax
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
    path_index = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                              '../docs/_build/html/',
                                              'index.html'))
    webbrowser.open(path_index, new=1)  # open docs in new window
    click.echo('Opening documentation in new window of your browser.')
    click.echo(path_index)


@cli_rocks.command()
def index():
    '''Create or update index of numbered SSOs.

    The list is retrieved from the Minor Planet Center, at
    https://www.minorplanetcenter.net/iau/lists/NumberedMPs.txt
    '''
    tools.create_index()


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
    import os
    os.system('git branch --show-current')

    name, number = names.get_name_number(this, parallel=1,
                                         verbose=verbose, progress=False)

    if isinstance(name, (str)):
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
        this, _ = names.get_name_number(this, parallel=1, verbose=verbose,
                                        progress=False)

    # Build query
    url = 'https://ssp.imcce.fr/webservices/ssodnet/api/datacloud.php'

    payload = {
        '-name': this,
        '-mime': mime,
        '-from': 'rocks',
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

    selected, taxa = tax.get_taxonomy(this, parallel=1, progress=False,
                                      verbose=verbose)

    if isinstance(taxa, float):
        if np.isnan(taxa):
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

    averaged, albedos = alb.get_albedo(this, parallel=1, progress=False,
                                       verbose=verbose)

    if isinstance(albedos, float):
        if np.isnan(albedos):
            click.echo('No albedo on record.')
            sys.exit()

    # Print results
    click.echo(f'{"ref":20} {"albedo":5} '
               f'{"err":5} {"method":8}')

    for ind, a in albedos.iterrows():
        click.echo(f'{a["shortbib"]:20} {a["albedo"]:.3f}  '
                   f'{a["err_albedo"]:.3f} {a["method"]:8} '
                   f'[{"X" if a["selected"] else " "}]')

    # weighted mean albedo and error
    click.echo(f'\n{"":6}{averaged[0]:.3f} +- {averaged[1]:.3f}')


@cli_rocks.command()
@click.argument('this', default='')
@click.option('--verbose', '-v', is_flag=True,
              help='Flag to print SsODNet request diagnostics.')
def diameter(this, verbose):
    '''Get asteroid diameter measurements for a single minor body.

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

    averaged, diameters = properties.get_property('diameter', this,
                                                  progress=False,
                                                  parallel=1,
                                                  verbose=verbose)

    if diameters is False:
        click.echo('No diameter on record.')
        sys.exit()

    # Print results
    click.echo(f'{"ref":20} {"diameter":9} '
               f'{"err":7} {"method":8}')

    for ind, d in diameters.iterrows():
        click.echo(f'{d["shortbib"]:20} {d["diameter"]:8.3f}  '
                   f'{d["err_diameter"]:7.3f} {d["method"]:8} '
                   f'[{"X" if d["selected"] else " "}]')

    # weighted mean albedo and error
    click.echo(f'\n{"":6}{averaged[0]:.3f} +- {averaged[1]:.3f}')


@cli_rocks.command()
@click.argument('this', default='')
@click.option('--verbose', '-v', is_flag=True,
              help='Flag to print SsODNet request diagnostics.')
def mass(this, verbose):
    '''Get asteroid mass estimate for a single minor body.

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

    averaged, masses = properties.get_property('mass', this, progress=False,
                                               parallel=1, verbose=verbose)

    if masses is False:
        click.echo('No mass on record.')
        sys.exit()

    # Print results
    click.echo(f'{"ref":20} {"mass":5} '
               f'{"err":5} {"method":8}')

    for ind, m in masses.iterrows():
        click.echo(f'{m["shortbib"]:20} {m["mass"]:.4e}  '
                   f'{m["err_mass"]:.4e} {m["method"]:10} '
                   f'[{"X" if m["selected"] else " "}]')

    # weighted mean mass and error
    click.echo(f'\n{"":6}{averaged[0]:.4e} +- {averaged[1]:.4e}')
