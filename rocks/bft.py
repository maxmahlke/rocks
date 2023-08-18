import pandas as pd
from rich import prompt

from rocks import config
from rocks import ssodnet

PATH = config.PATH_CACHE / "ssoBFT-latest.parquet"


def load_bft():
    """Load the BFT from the cache or optionally from remote.

    Returns
    -------
    pd.DataFrame
        The ssoBFT.
    """

    if not PATH.is_file():
        if prompt.Confirm.ask("The ssoBFT is not in the cache. Download it [~600MB]?"):
            ssodnet._get_bft()
        else:
            return None

    bft = pd.read_parquet(PATH)
    return bft
