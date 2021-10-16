"""For space rocks."""
import os
import sys

from . import datacloud, definitions, plots, ssodnet, utils

# Expose API to user
from .core import Rock
from .core import rocks_ as rocks
from .resolve import identify

__version__ = "1.3.2"

# Path to rocks auxilliary files
PATH_CACHE = os.path.join(os.path.expanduser("~"), ".cache/rocks")

PATH_META = {
    "description": os.path.join(PATH_CACHE, "ssoCard_description.json"),
    "template": os.path.join(PATH_CACHE, "ssoCard_template.json"),
    "units": os.path.join(PATH_CACHE, "ssoCard_units.json"),
}

PATH_INDEX = os.path.join(PATH_CACHE, "index.pkl")

# Check for existence of index file and cache directory
os.makedirs(PATH_CACHE, exist_ok=True)

if not os.path.isfile(PATH_INDEX):
    utils.retrieve_index_from_repository()
