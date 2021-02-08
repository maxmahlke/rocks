"""For space rocks."""
import json
import os

import pandas as pd

from .core import Rock
from .core import rocks_ as rocks
from .resolve import identify
from . import plots
from . import properties
from . import resolve
from . import utils

# Metadata
#  __version__ = "0.1.0"

# Package auxilliary files
PATH_CACHE = os.path.join(os.path.expanduser("~"), ".cache/rocks")
PATH_TEMPLATE = os.path.join(os.path.dirname(__file__), "../data/ssoCard_template.json")
PATH_INDEX = os.path.join(os.path.dirname(__file__), "../data/index.pkl")

os.makedirs(PATH_CACHE, exist_ok=True)

# Read ssoCard template
with open(PATH_TEMPLATE, "r") as file_:
    TEMPLATE = json.load(file_)

TEMPLATE_KEYS = pd.json_normalize(TEMPLATE)

META_MAPPING = dict(
    (meta, meta.replace(".uncertainty", ""))
    for meta in TEMPLATE_KEYS
    if "uncertainty" in meta
)

SHORTCUTS = {
    "physical": set(
        [attr.split(".")[2] for attr in TEMPLATE_KEYS if "physical" in attr]
    ),
    "dynamical": set(
        [attr.split(".")[2] for attr in TEMPLATE_KEYS if "dynamical" in attr]
    ),
}
