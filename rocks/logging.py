"""Configuration of rocks logging messages."""

import logging
from rich.logging import RichHandler

# Use rich to have colourful logging messages
handler = RichHandler(rich_tracebacks=True, show_path=False, show_time=False)
handler.setFormatter(logging.Formatter("[%(name)s] %(message)s"))

# Configure rocks logger
logger = logging.getLogger("rocks")
logger.addHandler(handler)
# TODO Set logging level based on CLI flag and module attribute
logger.setLevel(logging.INFO)
