"""For space rocks."""

import inspect

# Welcome to rocks
__version__ = "1.8.8"

# Only define user API if rocks is not called via command line
context = inspect.stack()[-1].code_context
if context is None or "rocks.cli" not in context[0]:
    # Expose API to user
    from .bft import load_bft
    from .core import Rock
    from .core import rocks_ as rocks
    from .resolve import identify
    from .logging import set_log_level

    # Alias id to identify
    id = identify
