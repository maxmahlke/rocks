#!/usr/bin/env python
"""rocks command line suite."""
import json
import keyword
import os
import sys
import warnings
import webbrowser

import click
import numpy as np
import requests
import rich
from rich.prompt import Prompt
from rich.progress import track

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
    # TODO There will soon be a stub card online to check this
    # For now, we just check the version of Ceres
    URL = "https://ssp.imcce.fr/webservices/ssodnet/api/ssocard/Ceres"
    response = requests.get(URL)

    if response.ok:
        card_ceres = response.json()
    else:
        warnings.warn("Retrieving the current ssoCard version failed.")
        sys.exit()

    current_version = card_ceres["Ceres"]["ssocard"]["version"]

    # ------
    # Update ssoCards
    out_of_date = [card for card, version in cached_cards if version != current_version]

    if cached_cards:
        if out_of_date:

            # Ensure that the IDs are current
            if len(out_of_date) == 1:
                _, _, current_ids = rocks.identify(
                    out_of_date, return_id=True, local=False
                )
                current_ids = [current_ids]

            else:

                _, _, current_ids = zip(
                    *rocks.identify(out_of_date, return_id=True, local=False)
                )

            # Swap the renamed ones
            updated = []

            for old_id, current_id in zip(out_of_date, current_ids):

                if old_id == current_id:
                    continue

                rich.print(
                    f"{old_id} has been renamed to {current_id}. Swapping the ssoCards."
                )

                # Get new card and remove the old one
                rocks.ssodnet.get_ssocard(current_id, no_cache=True)
                os.remove(os.path.join(rocks.PATH_CACHE, f"{old_id}.json"))

                # This is now up-to-date
                updated.append(old_id)

            for id_ in updated:
                out_of_date.remove(id_)

            # Update the outdated ones
            rich.print(
                f"\n{len(out_of_date)} ssoCards {'is' if len(out_of_date) == 1 else 'are'} out-of-date.",
                end=" ",
            )

            response = Prompt.ask(
                "Update the ssoCards?",
                choices=["y", "n"],
                default="y",
            )

            if response in ["Y", "y"]:

                n_subsets = 20 if len(out_of_date) > 1000 else 1

                for subset in track(
                    np.array_split(np.array(out_of_date), n_subsets),
                    description="Updating ssoCards : ",
                ):
                    rocks.ssodnet.get_ssocard(subset, progress=False, no_cache=True)

        else:
            rich.print("\nAll ssoCards are up-to-date.")

    # ------
    # Update datacloud catalogues
    if cached_catalogues:
        response = Prompt.ask(
            "\nDatacloud catalogues do not have versions. Update all of them?",
            choices=["y", "n"],
            default="n",
        )

        if response in ["Y", "y"]:
            for catalogue in set([cat for _, cat in cached_catalogues]):
                ids = [id_ for id_, cat in cached_catalogues if cat == catalogue]

                n_subsets = 20 if len(ids) > 1000 else 1

                for subset in track(
                    np.array_split(np.array(ids), n_subsets),
                    description=f"{catalogue:<12} : ",
                ):
                    rocks.ssodnet.get_datacloud_catalogue(
                        subset, catalogue, progress=False, no_cache=True
                    )

    # ------
    # Update metadata
    rich.print("\nUpdating the metadata files..", end=" ")

    for meta in ["template", "units", "description"]:
        rocks.utils.retrieve_json_from_ssodnet(meta)

    rich.print("Done.")

    # ------
    # Update asteroi name-number index
    response = Prompt.ask(
        "\nUpdate the asteroid name-number index? This can take 30min - 1h.",
        choices=["y", "n"],
        default="n",
    )

    if response in ["", "Y", "y"]:
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
    if keyword.iskeyword(parameter):
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
