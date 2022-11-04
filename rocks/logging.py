import logging
from rich.logging import RichHandler

logging.basicConfig(
    level=logging.INFO,
    format="[%(name)s] %(message)s",
    handlers=[RichHandler(rich_tracebacks=True, show_path=False, show_time=False)],
)

logger = logging.getLogger("rocks")
logger.setLevel(logging.INFO)
