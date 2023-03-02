"""For space rocks."""

import inspect
from pathlib import Path

from . import config

# Welcome to rocks
__version__ = "1.7.3"

# Only define user API if rocks is not called via command line
context = inspect.stack()[-1].code_context
if context is None or "rocks.cli" not in context[0]:

    # Expose API to user
    from .core import Rock
    from .core import rocks_ as rocks
    from .resolve import identify
    from .logging import set_log_level

    # Alias id to identify
    id = identify
