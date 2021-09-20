#!/usr/bin/env python
"""rocks command line suite."""
import json
import keyword
import os
import sys
import webbrowser

import click
import rich
from rich import prompt

import rocks


class AliasedGroup(click.Group):
    """Click group with custom default mode implementation."""

    def get_command(self, ctx, cmd_name):

        rv = click.Group.get_command(self, ctx, cmd_name)

        # ------
        # If it's a known subcommand, execute it
        if rv is not None:
            return rv

        # ------
        # Unknown subcommand -> echo asteroid parameter and optionally plot
        for arg in ["-p", "--plot"]:

            if arg in sys.argv:
                sys.argv.remove(arg)

                plot = True
                break
        else:
            plot = False

        return echo(plot)


@click.group(cls=AliasedGroup)
@click.version_option(version=rocks.__version__, message="%(version)s")
def cli_rocks():
    """CLI for minor body exploration."""
    pass


@cli_rocks.command()
def docs():
    """Open rocks documentation in browser."""
    webbrowser.open("https://rocks.readthedocs.io/en/latest/", new=2)


@cli_rocks.command()
@click.argument("id_")
def id(id_):
    """Get asteroid name and number from string input."""
    name, number = rocks.identify(id_)  # type: ignore

    if isinstance(name, (str)):
        click.echo(f"({number}) {name}")


@cli_rocks.command()
@click.argument("id_")
def info(id_):
    """Print ssoCard of minor body."""
    _, _, id_ = rocks.identify(id_, return_id=True)  # type: ignore

    if not isinstance(id_, str):
        sys.exit()

    ssoCard = rocks.ssodnet.get_ssocard(id_)
    rich.print(ssoCard)


@cli_rocks.command()
def parameters():
    """Print the ssoCard and its description."""

    if not os.path.isfile(rocks.PATH_TEMPLATE):
        rocks.utils.retrieve_json_from_ssodnet("template")

    with open(rocks.PATH_TEMPLATE, "r") as file_:
        TEMPLATE = json.load(file_)

    rich.print(TEMPLATE)


@cli_rocks.command()
def update():
    """Update the cached asteroid data."""

    # Get set of ssoCards and datacloud catalogues in cache
    cached_cards, cached_catalogues = rocks.utils.cache_inventory()

    rich.print(
        f"""\nContents of {rocks.PATH_CACHE}:

        {len(cached_cards)} ssoCards
        {len(cached_catalogues)} datacloud catalogues\n"""
    )

    # Get the current SsODNet version
    current_version = rocks.utils.get_current_version()

    # ------
    # Update ssoCards
    out_of_date = [card for card, version in cached_cards if version != current_version]

    if cached_cards and out_of_date:

        # Ensure that the IDs are current
        rocks.utils.confirm_identify(out_of_date)

        # Optionally update the ssoCards
        update_cards = prompt.Confirm.ask("Update the ssoCards?", default=True)

        if update_cards:
            rocks.utils.update_cards(out_of_date)

    elif cached_cards and not out_of_date:
        rich.print("\nAll ssoCards are up-to-date.")

    # ------
    # Update datacloud catalogues
    if cached_catalogues:
        update_datacloud = prompt.Confirm.ask(
            "\nDatacloud catalogues do not have versions. Update all of them?",
            default=False,
        )

        if update_datacloud:
            rocks.utils.update_datacloud_catalogues(cached_catalogues)

    # ------
    # Update metadata
    rich.print("\nUpdating the metadata files..", end=" ")

    for meta in ["template", "units", "description"]:
        rocks.utils.retrieve_json_from_ssodnet(meta)

    rich.print("Done.")

    # ------
    # Update asteroi name-number index
    response = prompt.Prompt.ask(
        "\nUpdate the asteroid name-number index? "
        "[blue][0][/blue] No "
        "[blue][1][/blue] From GitHub (updated ~weekly) "
        "[blue][2][/blue] Locally (takes 30min - 1h)",
        choices=["0", "1", "2"],
        default="1",
    )

    if response == "1":
        rocks.utils.retrieve_index_from_repository()
        rich.print("Retrieved index from repository.")

    elif response == "2":
        rocks.utils.create_index()


def echo(plot):
    """Echos asteroid parameter to command line. Optionally opens plot.

    Parameters
    ==========
    plot : bool
        If the paramter values should be plotted.
    """

    # Get parameter and asteroid id
    _, parameter, *id_ = sys.argv
    id_ = " ".join(id_)

    # Check if the parameter might be missing an underscore
    if keyword.iskeyword(parameter.split(".")[-1]):
        parameter = f"{parameter}_"

    if parameter.split(".")[0] in rocks.datacloud.CATALOGUES.keys():
        datacloud = parameter.split(".")[0]
    else:
        datacloud = []

    rock = rocks.Rock(id_, datacloud=datacloud)

    # Pretty-print the paramter
    if not datacloud:
        rich.print(rocks.utils.rgetattr(rock, parameter))
    else:
        rocks.datacloud.pretty_print(
            rock, rocks.utils.rgetattr(rock, parameter), parameter
        )

    if plot:
        if not datacloud:
            print(
                f"Only datacloud collections can be plotted. "
                f"Try the plural of {parameter}."
            )
            sys.exit()

        rocks.plots.plot(rocks.utils.rgetattr(rock, parameter), parameter)

    sys.exit()
