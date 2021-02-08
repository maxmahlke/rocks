#!/usr/bin/env python
"""rocks command line suite."""
import os
import sys
import webbrowser

import click
import pandas as pd

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
        # Unknown subcommand, check if it's a valid property
        valid = False

        # ssoCard properties
        valid_props = [
            p for p in rocks.TEMPLATE_KEYS.columns if not p.startswith("datacloud")
        ]
        # missing intermediate levels
        valid_props = set(
            valid_props + [".".join(v.split(".")[:-1]) for v in valid_props if "." in v]
        )

        valid_props = sorted(list(valid_props), key=len)

        # Check if valid ssoCard property
        for prop in valid_props:

            if prop.endswith("class") or prop.endswith("complex"):
                prop += "_"

            if prop.endswith(cmd_name):
                valid = True
                datacloud = []
                break

        # datacloud properties
        if not valid:
            valid_catalogues = [
                (datacloud, cat["attr_name"])
                for datacloud, cat in rocks.utils.DATACLOUD_META.items()
            ]

            requested_catalogue = cmd_name.split(".")[0]

            if requested_catalogue in ["diameters", "albedos"]:
                requested_catalogue = "diamalbedo"

            for datacloud, cat in valid_catalogues:

                if cat == requested_catalogue:
                    valid = True
                    if len(cmd_name.split(".")) > 1:
                        # single property
                        prop = ".".join([cat, *cmd_name.split(".")[1:]])
                    else:
                        # catalogue overview
                        prop = cat
                    datacloud = [datacloud]
                    break

        if valid:

            arguments = sys.argv.copy()

            plot = False
            for p in ["-h", "--hist", "-s", "--scatter"]:
                if p in arguments:
                    plot = True
                    arguments.remove(p)

            # Identify rock and check datacloud catalogue
            if len(arguments) == 3:
                id_ = arguments[-1]
                skip_id_check = False
            else:
                _, _, id_ = rocks.utils.select_sso_from_index()
                skip_id_check = True

            rock = rocks.Rock(id_, datacloud=datacloud, skip_id_check=skip_id_check)
            if not isinstance(rock.id, str):
                sys.exit()

            prop = rocks.utils.rgetattr(rock, prop)
            return rocks.utils.pretty_print_property(rock, prop, plot=plot)
        else:
            return None


@click.group(cls=AliasedGroup)
def cli_rocks():
    """CLI suite for minor body exploration.

    For more information: rocks docs
    """
    pass


@cli_rocks.command()
def docs():
    """Open rocks documentation in browser."""
    path_docs = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../docs/_build/html/", "index.html")
    )
    webbrowser.open(path_docs, new=2)  # open docs in new tab


@cli_rocks.command()
def update():
    """Update index of numbered SSOs and SsODNet metadata.

    The list is retrieved from the Minor Planet Center, at
    https://www.minorplanetcenter.net/iau/lists/NumberedMPs.txt
    """
    rocks.utils.create_index()
    rocks.utils.create_ssoCard_template()


@cli_rocks.command()
@click.argument("this", required=1)
def identify(this):
    """Get asteroid name and number from string input.

    Parameters
    ----------
    this : str
        String to identify asteroid.
    """
    name, number, _ = rocks.identify(this)[0]

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
        _, _, this = rocks.identify(this, return_id=True)

    if not isinstance(this, str):
        sys.exit()

    ssoCard = rocks.utils.get_ssoCard(this)

    if ssoCard is not None:
        rocks.utils.pretty_print_card(ssoCard, minimal)


@cli_rocks.command()
def properties():
    """Prints the ssoCard JSON keys."""
    keys = sorted(pd.json_normalize(rocks.TEMPLATE).columns, key=len)
    import pprint

    pprint.pprint(keys)


@cli_rocks.command()
def status():
    """Prints the availability of SsODNet:datacloud. """
    import warnings

    warnings.filterwarnings("ignore")

    from rich import print

    Ceres = rocks.Rock(1)

    if hasattr(Ceres, "taxonomy"):
        print(r"[bold green]Datacloud is available.")
    else:
        print(r"[bold red]Datacloud is not available.")
