import os
from pathlib import Path

import pandas as pd
import pytest
import rocks


# Change to True to use tests/data/ssoBFT-latest_Asteroid.parquet as the BFT source
USE_TEST_BFT = True
IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"


@pytest.mark.skipif(IN_GITHUB_ACTIONS, reason="Test doesn't work in Github Actions.")
def test_load_bft():
    """Load BFT with default columns"""

    if USE_TEST_BFT:
        prev_cache_path = rocks.config.PATH_CACHE
        rocks.config.PATH_CACHE = Path(__file__).parent / "data"

    bft = rocks.load_bft()
    rocks.config.PATH_CACHE = prev_cache_path
