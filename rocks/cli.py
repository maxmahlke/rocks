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

        # ------
        # Resolve known commands

        # Add command aliases
        if cmd_name == "identify":
            cmd_name = "id"
        elif cmd_name == "parameter":
            cmd_name = "parameters"
        elif cmd_name == "update":
            cmd_name = "status"

        # If it's a known subcommand, execute it
        rv = click.Group.get_command(self, ctx, cmd_name)

        if rv is not None:
            return rv

        # ------
        # Unknown subcommand -> echo asteroid parameter
        return echo()


@click.group(cls=AliasedGroup)
@click.version_option(version=rocks.__version__, message="%(version)s")
def cli_rocks():
    """CLI for minor body exploration."""
    pass


@cli_rocks.command()
def docs():
    """Open the rocks documentation in browser."""
    webbrowser.open("https://rocks.readthedocs.io/en/latest/", new=2)


@cli_rocks.command()
@click.argument("id_")
def id(id_):
    """Resolve the asteroid name and number from string input."""
    name, number = rocks.identify(id_)  # type: ignore

    if isinstance(name, (str)):
        click.echo(f"({number}) {name}")
    else:
        rocks.utils.list_candidate_ssos(id_)


@cli_rocks.command()
@click.argument("id_")
def info(id_):
    """Print the ssoCard of an asteroid."""
    _, _, id_ = rocks.identify(id_, return_id=True)  # type: ignore

    if not isinstance(id_, str):
        sys.exit()

    ssoCard = rocks.ssodnet.get_ssocard(id_)
    rich.print(ssoCard)


@cli_rocks.command()
def parameters():
    """Print the ssoCard structure and its description."""

    if not rocks.PATH_META["description"].is_file():
        rocks.utils.retrieve_json_from_ssodnet("description")

    with open(rocks.PATH_META["description"], "r") as file_:
        DESC = json.load(file_)

    rich.print(DESC)


@cli_rocks.command()
def status():
    """Echo the status of the ssoCards and datacloud catalogues."""

    # ------
    # Echo inventory

    # Get set of ssoCards and datacloud catalogues in cache
    cached_cards, cached_catalogues, cached_meta = rocks.utils.cache_inventory()

    # Get the modification date of the index
    date_index = os.path.getmtime(rocks.PATH_INDEX)
    date_index = time.strftime("%d %b %Y", time.localtime(date_index))

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

    if latest_rocks and latest_rocks != rocks.__version__:
        rich.print(
            f"[red]The running [green]rocks[/green] version ({rocks.__version__}) is behind the "
            f"latest version ({latest_rocks}). The ssoCard structure might have changed.[/red]"
        )
        rich.print(
            f"You should run [green]$ pip install -U space-rocks[/green] and clear the cache directory.\n"
        )

    # Update or clear
    if cached_cards:

        decision = prompt.Prompt.ask(
            "Update or clear the cached ssoCards and datacloud catalogues?\n"
            "[blue][0][/blue] Do nothing "
            "[blue][1][/blue] Clear the cache "
            "[blue][2][/blue] Update the data",
            choices=["0", "1", "2"],
            show_choices=False,
            default="1",
        )

        if decision == "1":
            rich.print("\nClearing the cached ssoCards and datacloud catalogues..")
            rocks.utils.clear_cache()

        elif decision == "2":

            # Update metadata
            for meta in rocks.PATH_META.keys():
                rocks.utils.retrieve_json_from_ssodnet(meta)

            # Update the cached data
            ids = [ssodnet_id for ssodnet_id in cached_cards]

            # Ensure that the IDs are current
            rich.print("\n(1/3) Verifying the ID of the cached ssoCards..")
            rocks.utils.confirm_identity(ids)

            # Update ssoCards
            rich.print("\n(2/3) Updating the cached ssoCards..")
            rocks.ssodnet.get_ssocard(ids, progress=True, local=False)

            # ------
            # Update datacloud catalogues
            rich.print("\n(3/3) Updating the cached datacloud catalogues..")
            rocks.utils.update_datacloud_catalogues(cached_catalogues)

    # ------
    # Update asteroid name-number index
    response = prompt.Prompt.ask(
        "\nUpdate the asteroid name-number index?\n"
        "[blue][0][/blue] No "
        "[blue][1][/blue] Yes",
        choices=["0", "1"],
        show_choices=False,
        default="1",
    )

    if response == "1":
        rocks.utils._build_index()


def echo():
    """Echos asteroid parameter to command line. Optionally opens plot."""

    # Should we plot?
    for arg in ["-p", "--plot"]:

        if arg in sys.argv:
            sys.argv.remove(arg)

            plot = True
            break
    else:
        plot = False

    # Are there enough arguments to continue?
    if len(sys.argv) == 2:
        print(f"\nUnknown command '{sys.argv[-1]}'.\n")
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        ctx.exit()

    # Get parameter and asteroid id
    _, parameter, *id_ = sys.argv
    id_ = " ".join(id_)

    # Allow for comma-separated parameter chaining
    parameter = parameter.split(",")

    # Check if any of the parameters might be missing an underscore
    parameter = [
        f"{p}_" if keyword.iskeyword(p.split(".")[-1]) else p for p in parameter
    ]

    # Check what datacloud properties we need
    datacloud = [
        p.split(".")[0]
        for p in parameter
        if p.split(".")[0] in rocks.datacloud.CATALOGUES.keys()
    ]

    # And let's go
    rock = rocks.Rock(id_, datacloud=datacloud)

    # Identifier could not be resolved
    if not rock.id_:
        rocks.utils.list_candidate_ssos(id_)
        sys.exit()

    # Pretty-print the paramter
    for param in parameter:
        if param in datacloud:
            rocks.datacloud.pretty_print(rock, rocks.utils.rgetattr(rock, param), param)
        else:
            print(rocks.utils.rgetattr(rock, param))

        if plot:
            if param not in datacloud:
                print(
                    f"Only datacloud collections can be plotted. "
                    f"Try the plural of {param}."
                )
                sys.exit()

            rocks.utils.rgetattr(rock, param).plot(param)

    # Avoid error message from click
    sys.exit()
