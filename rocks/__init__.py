"""For space rocks."""
import os
import sys

from . import datacloud, definitions, plots, ssodnet, utils

# Expose API to user
from .core import Rock
from .core import rocks_ as rocks
from .resolve import identify

__version__ = "1.3.1"

# Path to rocks auxilliary files
PATH_CACHE = os.path.join(os.path.expanduser("~"), ".cache/rocks")
PATH_TEMPLATE = os.path.join(PATH_CACHE, "ssoCard_template.json")
PATH_INDEX = os.path.join(PATH_CACHE, "index.pkl")

# Check for existence of index file and cache directory
os.makedirs(PATH_CACHE, exist_ok=True)

if not os.path.isfile(PATH_INDEX):
    response = input(
        "The asteroid name-number index is not present on your "
        "system.\nRetrieve it now from the rocks GitHub repository? [Yn] "
    )

    if response in ["", "Y", "y"]:
        utils.retrieve_index_from_repository()

    else:
        print("The index file is required to run rocks. Exiting.")
        sys.exit()
