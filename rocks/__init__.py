"""For space rocks."""

# Welcome to rocks
__version__ = "1.6.4"

# Expose API to user
from .core import Rock
from .core import rocks_ as rocks
from .resolve import identify

# Alias id to identify
id = identify
