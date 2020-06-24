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

from rocks.core import listParameter, Rock
from rocks import names
from rocks.properties import PROPERTIES as PROPS
from rocks import tools


class AliasedGroup(click.Group):
    """Click group with custom default mode implementation. """

    def get_command(self, ctx, cmd_name):

        rv = click.Group.get_command(self, ctx, cmd_name)

        # If it's a known subcommand, execute it
        if rv is not None:
            return rv

        # If unknown subcommand, check if it's a valid property
        valid_props = [k for k in PROPS.keys()]  # properties
        valid_props[-1:-1] = [v['collection'] for _, v in PROPS.items()
                              if 'collection' in v.keys()]  # collections

        if cmd_name not in valid_props:
            return None

        # Parse arguments
        args = sys.argv[1:]

        for i, arg in enumerate(args):

            if arg in ['-s', '--scatter']:
                args.pop(i)
                scatter = True
                break
        else:
            scatter = False

        for i, arg in enumerate(args):

            if arg in ['-h', '--hist']:
                args.pop(i)
                hist = True
                break
        else:
            hist = False

        if len(args) > 2:
            raise TooManyRocksError('Provide one or no asteroid identifiers.')
        elif len(args) == 2:
            property_, name = args
        elif len(args) == 1:
            property_ = args[0]
            name = False

        # Perform property query
        return echo_property(property_, name, scatter=scatter, hist=hist)


@click.group(cls=AliasedGroup)
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
    webbrowser.open(path_index, new=2)  # open docs in new tab
    click.echo('Opening documentation in new tab of your browser.')
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
    # Execute query and handle response
    response = tools.query_ssodnet(this, mime, verbose)

    if response is not False:
        tools.echo_response(response, mime)


@cli_rocks.command()
def properties():
    '''Echo valid asteroid properties for rocks query. '''
    from rich.columns import Columns
    from rich.panel import Panel
    from rich import print

    valid = [(k, v['collection']) if 'collection' in v.keys() else (k, None)
             for k, v in PROPS.items()]

    prop_columns = [Panel(f'[b]{prop}[/b]\n[yellow]{col}', expand=True)
                    if col is not None else
                    Panel(f'[b]{prop}[/b]\n ', expand=True)
                    for prop, col in valid]

    print(Columns(prop_columns))


@cli_rocks.command()
def status():
    '''Prints the availability of SsODNet:datacloud. '''
    import warnings
    warnings.filterwarnings('ignore')

    from rich import print

    Ceres = Rock(1, only=['taxonomy'])

    if hasattr(Ceres, 'taxonomy'):
        print(r'[bold green]Datacloud is available.[\bold green]')
    else:
        print(r'[bold red]Datacloud is not available.[\bold red]')


def echo_property(property_, name=False, scatter=False, hist=False):
    '''Echo asteroid property for a single minor body.

    Queries SsODNet:datacloud with the string input. If no identifier is
    provided, launches selection from index.

    Parameters
    ----------
    property_ : str
        Asteroid property from properites.PROPERTIES.keys()
    name : str
        Asteroid name, optional
    scatter : bool, otional
        Show scatter plot of floatParameter proptery. Default if False.
    hist : bool, otional
        Show histogram plot of floatParameter proptery. Default if False.
    '''
    if name is False:
        name, _ = tools.select_sso_from_index()

    SSO = Rock(name)

    if hasattr(SSO, property_):
        tools.pretty_print(SSO, property_)

        property_ = getattr(SSO, property_)

        if hist or scatter:

            if not isinstance(property_, listParameter):
                click.echo('\nPlotting is only implemented for property'
                           ' collections.')
                sys.exit()

            if property_.datatype is not float:
                click.echo('\nCan only plot properties of type float.')
                sys.exit()

            if hist:
                property_.hist(show=True)
            if scatter:
                property_.scatter(show=True)

    sys.exit()  # otherwise click prints Error


class TooManyRocksError(Exception):
    pass
