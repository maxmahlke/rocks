#!/usr/bin/env python
"""rocks command line suite."""
import json
import keyword
import os
import sys
import webbrowser

import click
import requests
import rich

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
        # Command aliases
        if cmd_name == "id":
            return identify

        # ------
        # Unknown subcommand -> echo asteroid property and optionally plot
        return echo()


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
    name, number = rocks.identify(this)  # type: ignore

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
    this : str
        Minor body name, designation, or number.
        If empty, a selection is prompted.
    minimal : str
        Print a minimal overview of SSO properties. Default is False.
    """
    if not this:
        _, _, this = rocks.utils.select_sso_from_index()
    else:  # passed identified string, ensure that we know it
        _, _, this = rocks.identify(this, return_id=True)  # type: ignore

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
    """Echo the number of ssoCards in the cache directory. Offer to update the out-of-date ones."""

    # Get set of ssoCards and datacloud catalogues in cache
    cached_jsons = set(
        file_
        for file_ in os.listdir(rocks.PATH_CACHE)
        if file_.endswith(".json") and file_ not in ["ssoCard_template.json"]
    )

    datacloud_catalogues = set(
        c["ssodnet_name"] for c in rocks.datacloud.CATALOGUES.values()
    )
    cached_catalogues = set(
        file_
        for file_ in cached_jsons
        if any([cat in file_ for cat in datacloud_catalogues])
    )

    cached_ssocards = cached_jsons - cached_catalogues

    print(
        f"There are {len(cached_ssocards)} ssoCards cached locally in {rocks.PATH_CACHE}"
    )

    # Read the versions of the cached ssoCards
    card_version = {}

    for card in cached_ssocards:

        ssodnet_id = os.path.splitext(card)[0]

        with open(os.path.join(rocks.PATH_CACHE, card), "r") as ssocard:
            card = json.load(ssocard)

            # TODO Currently, some ssoCards are None. This should be fixed on SsODNet side soon.
            if card[ssodnet_id] is None:
                card_version[ssodnet_id] = "Failed"
            else:
                card_version[ssodnet_id] = card[ssodnet_id]["ssocard"]["version"]

    # Get the current SsODNet version
    # TODO There will soon be a stub card online to check this
    # For now, we just check the version of Ceres
    URL = "https://ssp.imcce.fr/webservices/ssodnet/api/ssocard/Ceres"
    response = requests.get(URL)

    if response.ok:
        card_ceres = response.json()
    else:
        warnings.warn(f"Retrieving the current ssoCard version failed.")
        sys.exit()

    current_version = card_ceres["Ceres"]["ssocard"]["version"]

    out_of_date = [
        card for card, version in card_version.items() if version != current_version
    ]

    if out_of_date:

        if len(out_of_date) == 1:
            print(f"1 ssoCard is out-of-date.", end=" ")
        else:
            print(f"{len(out_of_date)} cards are out-of-date.", end=" ")

        response = input("Update the out-of-date cards? [Y/n] ")

        if response in ["", "Y", "y"]:
            print(f"Updating the ssoCards...", end=" ")
            rocks.ssodnet.get_ssocard(out_of_date, no_cache=True)
            print("Done.")
        else:
            print("Exiting without updating.")

    else:
        print("All cards are up-to-date.")


def echo():
    """Echos asteroid property to command line. Optionally opens plot."""

    # Check if we're plotting the property
    plot = False

    for arg in ["-p", "--plot"]:

        if arg in sys.argv:
            sys.argv.remove(arg)

            plot = True

    # Get property and asteroid id
    _, prop, *id_ = sys.argv
    id_ = " ".join(id_)

    # Check if the property might be missing an underscore
    if keyword.iskeyword(prop):
        prop = f"{prop}_"

    if prop.split(".")[0] in rocks.datacloud.CATALOGUES.keys():
        datacloud = prop.split(".")[0]
    else:
        datacloud = []

    rock = rocks.Rock(id_, datacloud=datacloud)

    # Pretty-printing is implemented in the properties __str__
    rich.print(rocks.utils.rgetattr(rock, prop))

    if rock.name == "Benoitcarry" and os.getenv("USER") == "bcarry":
        print(
            '\n"This [minor] planet has - or rather had - a problem, which was this: most of the people [it was named after] were [looking up their rock at work] for pretty much all of the time."\n'
        )

    sys.exit()
