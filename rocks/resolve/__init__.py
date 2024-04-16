import asyncio

from . import quaero
from . import id

from rocks import config


def get_or_create_eventloop():
    """Enable asyncio to get the event loop in a thread other than the main thread

    Returns
    --------
    out: asyncio.unix_events._UnixSelectorEventLoop
    """
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()


# TODO: Use singledispatch to simplify the function call and return structure
def identify(id_, type_=None, local=True, progress=False):
    """Resolve names and numbers of one or more minor bodies using identifiers.

    Parameters
    ----------
    id_ : str, int, float, list, range, set, np.ndarray, pd.Series
        One or more identifying names or numbers to resolve.
    type_: str
        The type of the minor body. Choose one of ['Asteroid', 'Comet', 'Satellite'].
        Default is None, which includes asteroids (and dwarf planets).
    local : bool
        Try resolving the name locally first. Default is True.
    progress : bool
        Show progress bar. Default is False.

    Returns
    -------
    tuple, list of tuple : (str, int, str), (None, np.nan, None)
        List containing len(id_) tuples. Each tuple contains the minor body's
        name and number. If the resolution failed, the values are None for name
        and SsODNet and np.nan for the number. If a single identifier is
        resolved, a tuple is returned.
    """

    # Ensure the asteroid name-number index exists
    if not config.PATH_INDEX.is_dir() and not config.CACHELESS:
        index._ensure_index_exists()

    type_ = "Asteroid" if type_ is None else type_

    if type_ not in ["Asteroid", "Comet", "Satellite", "Dwarf Planet"]:
        raise ValueError("'type_' must one of: 'Asteroid', 'Comet', 'Satellite'")

    # ------
    # Verify input
    if isinstance(id_, (str, int, float)):
        id_ = [id_]
    elif isinstance(id_, np.ndarray):
        id_ = id_.tolist()
    elif isinstance(id_, (set, range)):
        id_ = list(id_)
    elif id_ is None:
        logger.warning(f"Received id_ of type {type(id_)}.")
        return (None, np.nan)
    elif not isinstance(id_, (list, np.ndarray)):
        try:
            id_ = id_.to_list()  # pandas Series
        except AttributeError:
            raise TypeError(
                f"Received id_ of type {type(id_)}, expected one of: "
                "str, int, float, list, set, range, np.ndarray"
            )

    if not id_:
        logger.warning("Received empty list of identifiers.")
        return (None, np.nan)

    # ------
    # For a single name, try local lookup right away, async process has overhead
    if config.CACHELESS:
        local = False

    if len(id_) == 1 and local:
        success, (name, number) = _local_lookup(id_[0], type_)

        if success:
            return (name, number)
        else:
            # Local lookup just failed, no need to try it again
            local = False

    # ------
    # Run asynchronous event loop for name resolution
    with Progress(disable=not progress) as progress_bar:
        task = progress_bar.add_task("Identifying rocks", total=len(id_))  # type: ignore
        loop = get_or_create_eventloop()
        results = loop.run_until_complete(
            _identify(id_, type_, local, progress_bar, task)
        )

        # ------
        # Check if any failed due to 502 and rerun them
        idx_failed = [
            i for i, result in enumerate(results) if result == (None, None, None)
        ]

        if idx_failed:
            # avoid repeating error messages
            level = logger.level
            logger.setLevel("CRITICAL")
            results = np.array(results)
            results[idx_failed] = loop.run_until_complete(
                _identify(np.array(id_)[idx_failed], type_, local, progress_bar, task)
            )
            results = results.tolist()
            logger.setLevel(level)

    # ------
    # Verify the output format
    results = [r[:2] for r in results]

    if len(id_) == 1:  # type: ignore
        results = results[0]

    return results  # type: ignore
