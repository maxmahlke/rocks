"""For space rocks."""
import json
import os
import sys

import pandas as pd

from .core import Rock
from .core import rocks_ as rocks
from .resolve import identify
from . import plots
from . import properties
from . import ssodnet
from . import resolve
from . import utils

# Package auxilliary files
PATH_CACHE = os.path.join(os.path.expanduser("~"), ".cache/rocks")
PATH_TEMPLATE = os.path.join(PATH_CACHE, "ssoCard_template.json")
PATH_INDEX = os.path.join(PATH_CACHE, "index.pkl")

os.makedirs(PATH_CACHE, exist_ok=True)

# Check for existence of index file
if not os.path.isfile(PATH_INDEX):
    response = input(
        "The index of numbered asteroids is not present on your "
        "system.\nRetrieve it now from the rocks GitHub repository? [Yn] "
    )

    if response in ["", "Y", "y"]:
        utils.retrieve_index_from_repository()

    else:
        print("The index file is required to run rocks. Exiting.")
        sys.exit()

# Read ssoCard template
# with open(PATH_TEMPLATE, "r") as file_:
#     TEMPLATE = json.load(file_)

# TEMPLATE_KEYS = pd.json_normalize(TEMPLATE)

# META_MAPPING = dict(
#     (meta, meta.replace(".uncertainty", ""))
#     for meta in TEMPLATE_KEYS
#     if "uncertainty" in meta
# )

# SHORTCUTS = {
#     "physical": set(
#         [attr.split(".")[2] for attr in TEMPLATE_KEYS if "physical" in attr]
#     ),
#     "dynamical": set(
#         [attr.split(".")[2] for attr in TEMPLATE_KEYS if "dynamical" in attr]
#     ),
# }
