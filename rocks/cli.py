#!/usr/bin/env python
"""rocks command line suite."""

import json
import keyword
import sys
import subprocess
import shutil
import textwrap
import time
import webbrowser

import click
import numpy as np
import rich
from rich import prompt
from rich.console import Console
from rich import traceback

# pretty-print tracebacks with rich
traceback.install()

from rocks import core
from rocks import cache
from rocks import datacloud
from rocks import definitions
from rocks import index
from rocks import resolve
from rocks import Rock
from rocks import rocks
from rocks import ssodnet
from rocks import __version__


class AliasedGroup(click.Group):
    """Click group with custom default mode implementation."""

    def get_command(self, ctx, cmd_name):

        # ------
        # Resolve known commands

        # Add command aliases
        if cmd_name == "identify":
            cmd_name = "id"
        elif cmd_name == "aliases":
            cmd_name = "ids"
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
@click.version_option(version=__version__, message="%(version)s")
def cli_rocks():
    """CLI for minor body exploration."""
    pass


@cli_rocks.command()
def docs():
    """Open the rocks documentation in browser."""
    webbrowser.open("https://rocks.readthedocs.io/en/latest/", new=2)


@cli_rocks.command()
@click.argument("name", nargs=1)
def author(name):
    """Check presence of peer-rievewed article based on first-author name."""
    metadata.find_author(name)


@cli_rocks.command()
@click.argument("id_", nargs=-1)
def id(id_):
    """Resolve the asteroid name and number from string input."""

    if not id_:
        id_ = resolve._interactive()
    else:
        id_ = id_[0]

    name, number = resolve.identify(id_)  # type: ignore

    if isinstance(name, (str)):
        click.echo(f"({number}) {name}")
    else:
        utils.list_candidate_ssos(id_)


@cli_rocks.command()
@click.argument("id_", nargs=-1)
def info(id_):
    """Print the ssoCard of an asteroid."""

    if not id_:
        id_ = resolve._interactive()
    else:
        id_ = id_[0]

    _, _, id_ = resolve.identify(id_, return_id=True)  # type: ignore

    if not isinstance(id_, str):
        sys.exit()

    ssoCard = ssodnet.get_ssocard(id_)
    rich.print(ssoCard)


@cli_rocks.command()
def parameters():
    """Print the ssoCard structure and its description."""

    if not metadata.PATH.is_file():
        utils.retrieve_metadata("mappings")

    with open(metadata.PATH, "r") as file_:
        DESC = json.load(file_)

    rich.print(DESC)


@cli_rocks.command(hidden=True)
@click.argument("id_", nargs=-1)
def ids(id_):
    """Echo the aliases of an asteroid."""

    if not id_:
        id_ = resolve._interactive()
    else:
        id_ = id_[0]

    name, number, ssodnetid = identify(id_, return_id=True)  # type: ignore

    if name is None:
        sys.exit()

    aliases = index.get_aliases(ssodnetid)

    rich.print(f"({number}) {name}, aka \n {aliases}")


@cli_rocks.command()
@click.option(
    "--clear",
    "-c",
    help="Don't ask, clear cached cards and update index.",
    is_flag=True,
)
@click.option(
    "--update", "-u", help="Don't ask, update cached cards and index.", is_flag=True
)
def status(clear, update):
    """Echo the status of the ssoCards and datacloud catalogues."""

    # ------
    # Echo inventory
    cached_cards, cached_catalogues = cache.take_inventory()
    date_index = index.get_modification_date()

    rich.print(
        f"""\nContents of {cache.PATH}:

        {len(cached_cards)} ssoCards
        {len(cached_catalogues)} datacloud catalogues\n
        Asteroid name-number index updated on {date_index}\n"""
    )

    # ------
    # Echo update recommendations
    rich.print("Checking if rocks is up-to-date..", end="")

    if metadata.rocks_is_outdated():
        rich.print(
            f"\n[red]The running [green]rocks[/green] version ({__version__}) is behind the "
            f"latest version ({latest_rocks}). The ssoCard structure might have changed.[/red]\n"
            f"You should run [green]$ pip install -U space-rocks[/green] and clear the cache directory.\n"
        )
    else:
        rich.print(
            f"[green] the latest version ({__version__}) is installed.[/green]\n"
        )

    # Update or clear
    if cached_cards:

        decision = prompt.Prompt.ask(
            "Update or clear the cached ssoCards and datacloud catalogues?\n"
            "[blue][0][/blue] Do nothing "
            "[blue][1][/blue] Clear the cache "
            "[blue][2][/blue] Update the data",
            choices=["0", "1", "2", "3"],
            show_choices=False,
            default="1",
        )

        if decision == "1":
            rich.print("\nClearing the cached ssoCards and datacloud catalogues..")
            cache.clear()

        elif decision == "2":

            # Update metadata
            metadata.retrieve("mappings")

            # Update ssoCards
            rich.print("\n(1/2) Updating the cached ssoCards..")
            cache.update_cards(cached_cards)

            # Update datacloud catalogues
            rich.print("\n(2/2) Updating the cached datacloud catalogues..")
            cache.update_catalogues(cached_catalogues)

        elif decision == "3":
            with Console().status("Observing all asteroids.. [~11GB]", spinner="earth"):
                cache.retrieve_all_ssocards()

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
        click.echo()
        index._build_index()


@cli_rocks.command()
@click.argument("id_", nargs=-1)
def who(id_):
    """Get name citation of asteroid from MPC."""

    if not id_:
        id_ = resolve._interactive()
    else:
        id_ = id_[0]

    name, number = identify(id_)

    if name is None:
        sys.exit()

    if not np.isnan(number):
        id_ = number
    else:
        id_ = name

    citation = utils.get_citation_from_mpc(id_)

    if citation is None:
        rich.print(f"({number}) {name} has no citation attached to its name.")
        sys.exit()

    # Pretty-print citation
    rich.print(f"({number}) {name}")
    rich.print(
        textwrap.fill(
            citation,
            width=shutil.get_terminal_size()[0] - 2,
            initial_indent="  ",
            subsequent_indent="  ",
        ),
    )


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

    # Verbose output?
    for arg in ["-v", "--verbose"]:

        if arg in sys.argv:
            sys.argv.remove(arg)

            verbose = True
            break
    else:
        verbose = False

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
    catalogues = [
        p.split(".")[0]
        for p in parameter
        if p.split(".")[0] in definitions.DATACLOUD.keys()
    ]

    # And let's go
    rock = Rock(id_, datacloud=catalogues, suppress_errors=not verbose)

    # Identifier could not be resolved
    if not rock.id_:
        index.list_candidate_ssos(id_)
        sys.exit()

    # Pretty-print the paramter
    for param in parameter:
        if param in catalogues:
            datacloud.pretty_print(rock, utils.rgetattr(rock, param), param)
        else:
            value = core.rgetattr(rock, param)

            if isinstance(value, core.ListWithAttributes):
                # if verbose:
                #     for entry in value:
                #         rich.print_json(entry.json(), sort_keys=True)
                # else:
                #     for entry in value:
                #         rich.print(entry)
                rich.print(value)

            else:
                if verbose:
                    rich.print_json(value.json(), sort_keys=True)
                else:
                    print(value)

        if plot:
            if param not in datacloud:
                print(
                    "Only datacloud collections can be plotted. "
                    f"Try the plural of {param}."
                )
                sys.exit()

            utils.rgetattr(rock, param).plot(param)

    # Avoid error message from click
    sys.exit()


def _interactive(LINES):
    """Launch interactive selection using fzf."""

    PATH_EXECUTABLE = shutil.which("fzf")

    if PATH_EXECUTABLE is None:
        rich.print(
            "Interactive selection is not possible as the fzf tool is not installed.\n"
            "Either install fzf or specify an asteroid identifier.\n"
            "Refer to https://rocks.readthedocs.io/en/latest/getting_started.html#optional-interactive-search"
        )
        sys.exit()

    FZF_OPTIONS = []

    # Open fzf subprocess
    process = subprocess.Popen(
        [shutil.which("fzf"), *FZF_OPTIONS],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=None,
    )

    for line in LINES:
        process.stdin.write(line)
        process.stdin.flush()

    # Run process and wait for user selection
    process.stdin.close()
    process.wait()

    # Extract selected line
    try:
        choice = [line for line in process.stdout][0].decode()
    except IndexError:  # no choice was made, c-c c-c
        sys.exit()
    return choice
