"""For space rocks. Interface for SsODNet."""
import json
import os

import pandas as pd

from .core import Rock
from .core import rocks_ as rocks
from .resolver import identify
from . import plots
from . import properties
from . import resolver
from . import utils

# Metadata
__version__ = "0.0.1"

# Package auxilliary files
PATH_CACHE = os.path.join(os.path.expanduser("~"), ".cache/rocks")
PATH_TEMPLATE = os.path.join(os.path.dirname(__file__), "../ssoCard_template.json")
PATH_INDEX = os.path.join(os.path.dirname(__file__), "../index.pkl")

os.makedirs(PATH_CACHE, exist_ok=True)

# Read ssoCard template
with open(PATH_TEMPLATE, "r") as file_:
    TEMPLATE = json.load(file_)
