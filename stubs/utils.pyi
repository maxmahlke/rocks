"""
This type stub file was generated by pyright.
"""
"""Utility functions for rocks."""

def warning_on_one_line(message, category, filename, lineno, file=..., line=...): ...
def load_index():  # -> Any:
    """Load local index of asteroid numbers, names, SsODNet IDs."""
    ...

def rgetattr(obj, attr):  # -> Any:
    """Deep version of getattr. Retrieve nested attributes."""
    ...

def get_unit(path_unit):  # -> Any:
    """Get unit from units JSON file.

    Parameters
    ==========
    path_unit : str
        Path to the parameter in the JSON tree, starting at unit and
        separating the levels with periods.

    Returns
    =======
    str
        The unit of the requested parameter.
    """
    ...

def weighted_average(
    catalogue, parameter
):  # -> tuple[float, float] | tuple[Any, Any] | tuple[Unknown, Any]:
    """Computes weighted average of observable.

    Parameters
    ==========
    observable : np.ndarray
        Float values of observable
    error : np.ndarray
        Corresponding errors of observable.

    Returns
    =======
    float
        The weighted average.

    float
        The standard error of the weighted average.
    """
    ...

def reduce_id(id_):
    """Reduce the SsODNet ID to a string with fewer free parameters."""
    ...

def retrieve_json_from_ssodnet(which):  # -> None:
    """Retrieve the ssoCard units, or descriptions from SsODNet.

    Parameters
    ----------
    which : str
        The JSON file to download. Choose from ['units', 'description']
    """
    ...

def cache_inventory():  # -> tuple[list[Unknown], list[Unknown], list[str]]:
    """Create lists of the cached ssoCards and datacloud catalogues.

    Returns
    -------
    list of tuple
        The SsODNet IDs and versions of the cached ssoCards.
    list of tuple
        The SsODNet IDs and names of the cached datacloud catalogues.
    list of str
        The cached metadata files.
    """
    ...

def clear_cache():  # -> None:
    """Remove the cached ssoCards, datacloud catalogues, and metadata files."""
    ...

def get_current_version():  # -> Any:
    """Get the current version of ssoCards.

    Returns
    -------
    str
        The current version of ssoCards.

    Notes
    -----
    There will soon be a stub card online to check this. For now, we just check
    the version of Ceres.
    """
    ...

def update_datacloud_catalogues(cached_catalogues): ...
def confirm_identity(ids):  # -> None:
    """Confirm the SsODNet ID of the passed identifier. Retrieve the current
    ssoCard and remove the former one if the ID has changed.

    Parameters
    ==========
    ids : list
        The list of SsODNet IDs to confirm.
    """
    ...

def retrieve_rocks_version():
    """Retrieve the current rocks version from the GitHub repository."""
    ...