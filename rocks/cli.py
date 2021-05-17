#!/usr/bin/env python
"""rocks command line suite."""
import json
import os
import sys
import webbrowser

import click
import rich

import rocks


class AliasedGroup(click.Group):
    """Click group with custom default mode implementation. """

    def get_command(self, ctx, cmd_name):

        rv = click.Group.get_command(self, ctx, cmd_name)

        # ------
        # If it's a known subcommand, execute it
        if rv is not None:
            return rv

        # ------
        # Command aliases
        if cmd_name == "id":
            return identify

        # ------
        # Unknown subcommand -> echo asteroid property and optionally plot
        return echo()


@click.group(cls=AliasedGroup)
def cli_rocks():
    """CLI for minor body exploration."""
    pass


@cli_rocks.command()
def docs():
    """Open rocks documentation in browser."""
    webbrowser.open("https://rocks.readthedocs.io/en/latest/", new=2)


@cli_rocks.command()
def update():
    """Update index of numbered SSOs and SsODNet metadata.

    The list is retrieved from the Minor Planet Center, at
    https://www.minorplanetcenter.net/iau/lists/NumberedMPs.txt
    """
    rocks.utils.create_index()
    rocks.utils.retrieve_ssocard_template()


@cli_rocks.command()
def clear():
    """Clear the cached ssoCards."""
    for file_ in os.listdir(rocks.PATH_CACHE):
        if file_.endswith(".json") and file_ != "ssoCard_template.json":
            os.remove(os.path.join(rocks.PATH_CACHE, file_))


@cli_rocks.command()
@click.argument("this")
def identify(this):
    """Get asteroid name and number from string input.

    Parameters
    ==========
    this : str
        String to identify asteroid.
    """
    name, number, _ = rocks.identify(this)  # type: ignore

    if isinstance(name, (str)):
        click.echo(f"({number}) {name}")


@cli_rocks.command()
@click.argument("this", default="")
@click.option(
    "-m", "--minimal", is_flag=True, help="Reduce output to basic information."
)
def info(this, minimal):
    """Print ssoCard of minor body.

    Parameters
    ==========
    this : str, optional
        Minor body name, designation, or number.
        If empty, a selection is prompted.
    """
    if not this:
        _, _, this = rocks.utils.select_sso_from_index()
    else:  # passed identified string, ensure that we know it
        _, _, this = rocks.identify(this)  # type: ignore

    if not isinstance(this, str):
        sys.exit()

    ssoCard = rocks.ssodnet.get_ssocard(this)

    if ssoCard is not None:
        rocks.utils.pretty_print_card(ssoCard, minimal)


@cli_rocks.command()
def properties():
    """Prints the ssoCard JSON keys and description using the template."""

    if not os.path.isfile(rocks.PATH_TEMPLATE):
        rocks.utils.retrieve_ssocard_template()

    with open(rocks.PATH_TEMPLATE, "r") as file_:
        TEMPLATE = json.load(file_)

    rich.print(TEMPLATE)


@cli_rocks.command()
def status():
    """Prints the availability of SsODNet:datacloud. """
    ceres = rocks.Rock(1)

    if hasattr(ceres, "taxonomy"):
        rich.print(r"[bold green]Datacloud is available.")
    else:
        print(r"[bold red]Datacloud is not available.")


def echo():
    """Echos asteroid property to command line. Optionally opens plot."""

    # Check if we're plotting the property
    plot = False

    for arg in ["-p", "--plot"]:

        if arg in sys.argv:
            sys.argv.remove(arg)

            plot = True

    # Get data and echo
    _, prop, *id_ = sys.argv
    id_ = " ".join(id_)

    if prop in rocks.properties.PROP_TO_DATACLOUD:
        datacloud = [rocks.properties.PROP_TO_DATACLOUD[prop]]
    else:
        datacloud = []

    rock = rocks.Rock(id_, datacloud=datacloud)

    # Pretty-printing is implemented in the properties __str__
    rich.print(rocks.utils.rgetattr(rock, prop))
    sys.exit()
