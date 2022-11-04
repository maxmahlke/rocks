"""For space rocks."""

# Welcome to rocks
__version__ = "1.6.4"

import inspect

if "rocks.cli" not in inspect.stack()[-1].code_context[0]:

    # Expose API to user
    from .core import Rock
    from .core import rocks_ as rocks
    from .resolve import identify

    # Alias id to identify
    id = identify


# print(globals())
# print("click" in globals())
# print("CLICKED" in globals())
