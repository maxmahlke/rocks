#!/usr/bin/env python
"""rocks command line suite."""
import json
import keyword
import os
import sys
import time
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
    name, number = rocks.identify(id_)

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
def status():
    """Echo the status of the ssoCards and datacloud catalogues."""

    # ------
    # Echo inventory

    # Get set of ssoCards and datacloud catalogues in cache
    cached_cards, cached_catalogues = rocks.utils.cache_inventory()

    # Get cached metadata files
    cached_meta = [
        os.path.basename(f) for f in rocks.PATH_META.values() if os.path.isfile(f)
    ]

    # Get the modification date of the index
    date_index = os.path.getmtime(rocks.PATH_INDEX)
    date_index = time.ctime(date_index)

    # Print the findings
    rich.print(
        f"""\nContents of {rocks.PATH_CACHE}:

        {len(cached_cards)} ssoCards
        {len(cached_catalogues)} datacloud catalogues\n
        Asteroid name-number index [blue]\[index.pkl][/blue] updated on {date_index}
        Metadata files [blue]{cached_meta}[/blue]\n"""
    )

    # ------
    # Echo update recommendations
    latest_rocks = rocks.utils.retrieve_rocks_version()
    latest_card = rocks.utils.get_current_version()


    if latest_rocks != rocks.__version__ and False:
        rich.print(
            f"[red]The running 'rocks' version ({rocks.__version__}) is behind the latest version ({latest_rocks}). "
            f"The ssoCard structure might have changed. You should update 'rocks' and clear the cache directory.[/red]\n"
        )
    else:

        if cached_cards:
            oldest_card = min([version[1] for version in cached_cards])

            if latest_card != oldest_card:
                rich.print(
                    f"[red]The ssoCard version ({oldest_card}) is behind the latest version ({latest_card}). "
                    f"The ssoCard structure might have changed. You should clear the cache directory.[/red]\n"
                )

    # Update or clear
    if cached_cards:
        decision = prompt.Prompt.ask(
            "\nUpdate or clear the cached ssoCards and datacloud catalogues?\n"
            "[blue][0][/blue] Do nothing "
            "[blue][1][/blue] Clear the cache "
            "[blue][2][/blue] Update the data",
            choices=["0", "1", "2"],
            default="1",
        )

        if decision == "1":
            rich.print("\nClearing the cached ssoCards and datacloud catalogues..")
            rocks.utils.clear_cache()

        elif decision == "2":

            # Update the cached data
            ids = [ssodnet_id[0] for ssodnet_id in cached_cards]

            # Ensure that the IDs are current
            rich.print("\n(1/3) Verifying the ID of the cached ssoCards..")
            rocks.utils.confirm_identity(ids)

            # Update ssoCards
            rich.print("\n(2/3) Updating the cached ssoCards..")
            rocks.ssodnet.get_ssocard(ids, progress=True, local=False)

            # ------
            # Update datacloud catalogues
            rich.print("\n(3/3) Updating the cached datacloud catalogues..")

            for catalogue in set(catalogues[1] for catalogues in cached_catalogues):

                ids = [id_ for id_, cat in cached_catalogues if cat == catalogue]

                rocks.ssodnet.get_datacloud_catalogue(
                    ids, catalogue, local=False, progress=True
                )

            # Update metadata
            for meta in ["template", "units", "description"]:
                rocks.utils.retrieve_json_from_ssodnet(meta)

    # ------
    # Update asteroid name-number index
    response = prompt.Prompt.ask(
        "\nUpdate the asteroid name-number index?\n"
        "[blue][0][/blue] Do nothing "
        "[blue][1][/blue] From GitHub (updated ~weekly) "
        "[blue][2][/blue] Locally (takes >1h)",
        choices=["0", "1", "2"],
        default="1",
    )

    if response == "1":
        rocks.utils.retrieve_index()
        rich.print("Retrieved index from repository.")

    elif response == "2":
        rocks.utils.update_index()


def echo(plot):
    """Echos asteroid parameter to command line. Optionally opens plot.

    Parameters
    ==========
    plot : bool
        If the paramter values should be plotted.
    """

    if len(sys.argv) == 2:
        print(f"\nUnknown command '{sys.argv[-1]}'\n.")
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        ctx.exit()

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
