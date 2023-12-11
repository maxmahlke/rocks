"""For space rocks."""

import inspect

# Welcome to rocks
__version__ = "1.9.1"

# Only define user API if rocks is not called via command line
context = inspect.stack()[-1].code_context
if context is None or "rocks.cli" not in context[0]:
    # Expose API to user
    from .bft import load_bft  # noqa
    from .core import Rock  # noqa
    from .core import rocks_ as rocks  # noqa
    from .resolve import identify  # noqa
    from .logging import set_log_level  # noqa

    # Alias id to identify
    id = identify
