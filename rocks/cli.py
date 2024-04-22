#!/usr/bin/env python
"""rocks command line suite."""

import os
import re
import sys
import shutil

import click
import pandas as pd
import rich

from rocks import config
from rocks import index
from rocks import logging
from rocks.logging import logger
from rocks import metadata
from rocks import resolve
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
    import webbrowser

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
    from rocks import resolve

    if not id_:
        id_ = resolve._interactive()
        id_ = " ".join(id_.split()[:-1])
    else:
        id_ = id_[0]

    # Keep track of if we found a match
    found = False
    logger.addFilter(lambda s: not re.match("Could not identify", s.getMessage()))

    for type in ["asteroid", "comet", "satellite"]:
        match = resolve.identify(id_, type=type)  # type: ignore

        if match:
            rich.print(str(match))
            found = True

    if not found:
        logger.error(f"could not identify '{id_}'.")
        list_candidate_ssos(id_)


@cli_rocks.command()
@click.argument("id_", nargs=-1)
def info(id_):
    """Print the ssoCard of an asteroid."""
    from rocks import ssodnet

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
    mappings = metadata.load_mappings()
    rich.print(mappings)


@cli_rocks.command(hidden=True)
@click.argument("id", nargs=-1)
def ids(id):
    """Echo the aliases of an asteroid."""

    if not id:
        id = resolve._interactive()
    else:
        id = id[0]

    for type in ["asteroid", "comet", "satellite"]:
        match = resolve.identify(id, type=type)  # type: ignore
        rich.print(f"{str(match)}, aka \n {match.aliases}")


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
    from rich import prompt

    from rocks import bft
    from rocks import cache
    from rocks import ssodnet

    # ------
    # Echo inventory
    cached_cards, cached_catalogues = cache.take_inventory()
    date_index = index.get_modification_date()

    rich.print(
        f"""\nContents of {config.PATH_CACHE}:

        {len(cached_cards)} ssoCards
        {len(cached_catalogues)} datacloud catalogues\n
        {'1 ssoBFT' if bft.PATH.is_file() else ''}
        Index updated on:  {date_index}\n"""
    )

    # ------
    # Echo update recommendations
    rich.print("Checking if rocks is up-to-date..", end="")

    outdated, latest_rocks = metadata.rocks_is_outdated()

    if outdated:
        rich.print(
            f"\n[red]The running [green]rocks[/green] version ({__version__}) is behind"
            f" the latest version ({latest_rocks}).\nYou should run [green]$ pip install"
            f" -U space-rocks[/green] and clear the cache directory.\n[/red]"
        )
    else:
        rich.print(
            f"[green] the latest version ({__version__}) is installed.[/green]\n"
        )

    # Update or clear
    if cached_cards:
        if not clear and not update:
            decision = prompt.Prompt.ask(
                "Update or clear the cached ssoCards and datacloud catalogues?\n"
                "[blue][0][/blue] No "
                "[blue][1][/blue] Clear cache "
                "[blue][2][/blue] Update data "
                "[blue][3][/blue] Download ssoBFT",
                choices=["0", "1", "2", "3", "4"],
                show_choices=False,
                default="0",
            )
        else:
            decision = "none"

        if clear or decision == "1":
            rich.print("\nClearing the cached ssoCards and datacloud catalogues..")
            cache.clear()

        elif update or decision == "2":
            # Update metadata
            metadata.retrieve("mappings")

            # Update ssoCards
            rich.print("\n(1/2) Updating the cached ssoCards..")
            cache.update_cards(cached_cards)

            # Update datacloud catalogues
            rich.print("\n(2/2) Updating the cached datacloud catalogues..")
            cache.update_catalogues(cached_catalogues)

        elif decision == "3":
            rich.print("")
            ssodnet._get_bft()

        elif decision == "4":
            from rich.console import Console

            with Console().status("Observing all asteroids.. [~11GB]", spinner="earth"):
                cache.retrieve_all_ssocards()

    # ------
    # Update minor body index
    if not clear and not update:
        decision = prompt.Prompt.ask(
            "\nUpdate the minor body index?\n"
            "[blue][0][/blue] No "
            "[blue][1][/blue] Yes",
            choices=["0", "1"],
            show_choices=False,
            default="1",
        )

        if decision == "1":
            click.echo()
            index._build_index()
    if update:
        index._build_index()


@cli_rocks.command()
@click.argument("id_", nargs=-1)
def who(id_):
    """Get name citation of asteroid from MPC."""
    import textwrap

    if not id_:
        id_ = resolve._interactive()
    else:
        id_ = id_[0]

    name, number = resolve.identify(id_)

    if name is None:
        sys.exit()

    citation = metadata.get_citation(number)

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


@cli_rocks.command()
def recent():
    """Echo recently named asteroids."""

    recent = pd.read_json("https://www.wgsbn-iau.org/files/json/latest.json")

    for _, row in recent.iterrows():
        rich.print(f"({row.mp_number}) {row['name']:<10}")
        rich.print(
            f"    [dim]{row.citation[:100].replace('  ', ' ')}[...][/dim]", end="\n\n"
        )


@cli_rocks.command(hidden=True)
def debug():
    """Echo rocks configuration variables"""

    rich.print("--- cache")
    rich.print(f"using cache: {not config.CACHELESS}")
    rich.print(f"cache directory: {config.PATH_CACHE}")

    rocks_cache_dir_set = "ROCKS_CACHE_DIR" in os.environ
    rich.print(f"ROCKS_CACHE_DIR set: {rocks_cache_dir_set}")

    if rocks_cache_dir_set:
        rich.print(f"ROCKS_CACHE_DIR value: {os.environ['ROCKS_CACHE_DIR']}")

    rich.print("\n--- metadata")
    rich.print(f"metadata path: {config.PATH_MAPPINGS}")

    path_mappings_set = "ROCKS_PATH_MAPPINGS" in os.environ
    rich.print(f"ROCKS_PATH_MAPPINGS set: {path_mappings_set}")

    if path_mappings_set:
        rich.print(f"ROCKS_PATH_MAPPINGS value: {os.environ['ROCKS_PATH_MAPPINGS']}")

    rich.print("\n--- ssodnet")
    rich.print(f"url ssodnet: {ssodnet.URL_SSODNET}")

    url_ssodnet_set = "ROCKS_URL_SSODNET" in os.environ
    rich.print(f"ROCKS_URL_SSODNET set: {url_ssodnet_set}")

    if url_ssodnet_set:
        rich.print(f"ROCKS_URL_SSODNET value: {os.environ['ROCKS_URL_SSODNET']}")


def echo():
    """Echos asteroid parameter to command line. Optionally opens plot."""
    import keyword

    from rocks import core
    from rocks import datacloud

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
        p.split(".")[0] for p in parameter if p.split(".")[0] in config.DATACLOUD.keys()
    ]

    # Increase the default log level unless user requests verbose output
    if not verbose:
        logging.set_log_level("ERROR")
    else:
        logging.set_log_level("DEBUG")

    # And let's go
    rock = core.Rock(id_, datacloud=catalogues)

    # Identifier could not be resolved
    if not rock.id_:
        list_candidate_ssos(id_)
        sys.exit()

    # Pretty-print the paramter
    for param in parameter:
        if param in catalogues:
            datacloud.pretty_print(rock, core.rgetattr(rock, param), param)
        else:
            value = core.rgetattr(rock, param)

            if isinstance(value, core.ListWithAttributes):
                if param == "spin" and not verbose:
                    for v in value:
                        print(v)  # uses __str__
                else:
                    rich.print(value)  # uses __rich__

            else:
                if verbose:
                    rich.print_json(value.json(), sort_keys=True)
                else:
                    from rich.console import Console
                    from rich.theme import Theme

                    console = Console(theme=Theme({"repr.number": ""}))
                    console.print(value)

        if plot:
            if param not in datacloud:
                print(
                    "Only datacloud collections can be plotted. "
                    f"Try the plural of {param}."
                )
                sys.exit()

            core.rgetattr(rock, param).plot(param)

    # Avoid error message from click
    sys.exit()


def _interactive(LINES):
    """Launch interactive selection using fzf."""
    import subprocess

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


def list_candidate_ssos(id_):
    """Propose matches for failed id queries based on Levenshtein distance if
    the passed identifier is a name.

    Parameters
    ----------
    id_ : str
        The passed asteroid identifier.

    Note
    ----
    The proposed matches are printed to stdout.
    """

    # This only makes sense for named asteroids
    if not re.match(r"^[A-Za-z ]*$", id_):
        return

    candidates = index.find_candidates(id_)

    if candidates:
        rich.print(
            f"\nCould {'this' if len(candidates) == 1 else 'these'} be the "
            f"{'rock' if len(candidates) == 1 else 'rocks'} you're looking for?"
        )

        for name, number in candidates:
            rich.print(f"{f'({number})':>8} {name}")
