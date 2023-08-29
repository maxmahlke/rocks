import pandas as pd
from rich import prompt

from rocks import config
from rocks import ssodnet

PATH = config.PATH_CACHE / "ssoBFT-latest.parquet"
PATH_LITE = config.PATH_CACHE / "ssoBFT-latest-lite.parquet"

LITE_COLUMNS = [
    "sso_id",
    "sso_number",
    "sso_name",
    "sso_class",
    "orbital_elements.semi_major_axis.value",
    "orbital_elements.eccentricity.value",
    "orbital_elements.inclination.value",
    "orbital_elements.orbital_period.value",
    "orbital_elements.perihelion_distance.value",
    "proper_elements.proper_semi_major_axis.value",
    "proper_elements.proper_eccentricity.value",
    "proper_elements.proper_inclination.value",
    "proper_elements.proper_sine_inclination.value",
    "family.family_number",
    "family.family_name",
    "pair.sibling_number",
    "pair.sibling_name",
    "pair.distance",
    "pair.age.value",
    "yarkovsky.dadt.value",
    "yarkovsky.A2.value",
    "yarkovsky.S",
    "albedo.value",
    "absolute_magnitude.value",
    "density.value",
    "diameter.value",
    "mass.value",
    "taxonomy.class",
    "taxonomy.complex",
    "thermal_inertia.value",
    "spins.1.period.value",
]


def load_bft(lite=False):
    """Load the BFT from the cache or optionally from remote.

    Parameters
    ----------
    lite : bool
        Return the lite version of the ssoBFT. Default is False.

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

    if lite:
        if not PATH_LITE.is_file():
            build_lite()
        return pd.read_parquet(PATH_LITE)
    return pd.read_parquet(PATH)


def build_lite():
    """Build the lite version of the ssoBFT."""
    bft = pd.read_parquet(PATH)
    lite = bft[LITE_COLUMNS]
    lite.to_parquet(PATH_LITE)
