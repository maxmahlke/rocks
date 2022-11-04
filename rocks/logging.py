import logging

from rich.logging import RichHandler

FORMAT = "[%(name)s] %(message)s"

logging.basicConfig(
    level=logging.ERROR,
    format=FORMAT,
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, show_path=False, show_time=False)],
)

logger = logging.getLogger("rocks")
logger.setLevel(logging.INFO)
