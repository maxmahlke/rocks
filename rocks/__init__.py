"""For space rocks."""
from pathlib import Path

import rich
from rich import traceback

# pretty-print tracebacks with rich
traceback.install()

# rocks modules
# rocks.plots is lazy-loaded as it is expensive
from . import datacloud, definitions, ssodnet, utils, index

# Expose API to user
from .core import Rock
from .core import rocks_ as rocks
from .resolve import identify

# ------
# Path definitions required throughout the code
PATH_CACHE = Path.home() / ".cache/rocks"
PATH_INDEX = PATH_CACHE / "index"
PATH_MAPPING = PATH_CACHE / "mapping_aster-astorb.json"

# Dict to hold the asteroid name-number indices at runtime
INDEX = {}

# ------
# Welcome to rocks
__version__ = "1.5.8"

GREETING = rf"""
                _
               | |
 _ __ ___   ___| | _____
| '__/ _ \ / __| |/ / __|
| | | (_) | (__|   <\__ \
|_|  \___/ \___|_|\_\___/

version: {__version__}
cache:   {PATH_CACHE}

It looks like this is the first time you run [green]rocks[/green].
Some metadata is required to be present in the cache directory.
[green]rocks[/green] will download it now.
"""


# ------
# Check for existence of index file and cache directory
if not PATH_INDEX.is_dir():

    rich.print(GREETING)

    # Just for a while
    if (Path.home() / ".cache/rocks/index.pkl").is_file():
        (Path.home() / ".cache/rocks/index.pkl").unlink()

    PATH_INDEX.mkdir(parents=True)
    index._build_index()

    rich.print("\nAll done. Find out more by running [green]$ rocks docs[/green]\n")
