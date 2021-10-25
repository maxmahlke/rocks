"""For space rocks."""
import os
import sys

import rich

# rocks modules
from . import datacloud, definitions, plots, ssodnet, utils

# Expose API to user
from .core import Rock
from .core import rocks_ as rocks
from .resolve import identify

__version__ = "1.4"

GREETING = fr"""
               | |
 _ __ ___   ___| | _____
| '__/ _ \ / __| |/ / __|
| | | (_) | (__|   <\__ \
|_|  \___/ \___|_|\_\___/

version: {__version__}
cache:   {PATH_CACHE}

It looks like this is the first time you run 'rocks'.
Some metadata is required to be present in the cache directory.
'rocks' will download it now.

Find out more by running '$ rocks docs'
"""

# ------
# Path definitions required throughout the code
PATH_CACHE = os.path.join(os.path.expanduser("~"), ".cache/rocks")
PATH_INDEX = os.path.join(PATH_CACHE, "index.pkl")
PATH_META = {
    "description": os.path.join(PATH_CACHE, "ssoCard_description.json"),
    "template": os.path.join(PATH_CACHE, "ssoCard_template.json"),
    "units": os.path.join(PATH_CACHE, "ssoCard_units.json"),
}

# ------
# Check for existence of index file and cache directory
os.makedirs(PATH_CACHE, exist_ok=True)

if not os.path.isfile(PATH_INDEX):
    rich.print(GREETING)
    utils._build_index()
