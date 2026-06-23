import pandas as pd
from pathlib import Path

import rocks


# Change to True to use tests/data/ssoBFT-latest_Asteroid.parquet as the BFT source
USE_TEST_BFT = True

def test_load_bft():
    """Load BFT with default columns"""

    if USE_TEST_BFT:
        prev_cache_path = rocks.config.PATH_CACHE
        rocks.config.PATH_CACHE = Path(__file__).parent / "data"

    bft = rocks.load_bft()
    rocks.config.PATH_CACHE = prev_cache_path