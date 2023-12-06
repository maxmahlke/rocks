import pandas as pd
from rich import prompt

from rocks import config
from rocks import ssodnet

PATH = config.PATH_CACHE / "ssoBFT-latest.parquet"

COLUMNS = [
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


def load_bft(full=False, **kwargs):
    """Load the BFT from the cache or optionally from remote.

    Parameters
    ----------
    full : bool
        Return the full version of the ssoBFT. Default is False.
    kwargs
        Passed on to pd.read_parquet

    Returns
    -------
    pd.DataFrame
        The ssoBFT.

    Notes
    -----
    By default, only the subset of columns defined in rocks.bft.COLUMNS is
    loaded.
    """

    if not PATH.is_file() and not config.CACHELESS:
        if prompt.Confirm.ask("The ssoBFT is not in the cache. Download it [~600MB]?"):
            ssodnet._get_bft()
        else:
            return None

    if config.CACHELESS:
        URL = f"{ssodnet.URL_SSODNET}/data/ssoBFT-latest.parquet"

    if "columns" not in kwargs and not full:
        kwargs["columns"] = COLUMNS

    LOAD = PATH if not config.CACHELESS else URL
    return pd.read_parquet(LOAD, **kwargs)
