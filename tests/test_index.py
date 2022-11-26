import pytest

from rocks import index


def test_load_partial():
    """Load part of the index and look up asteroid."""

    for id_ in ["mette", "2012aa14", 230, 12301]:
        partial = rocks.index._get_index_file(id_)
        assert id_ in partial


def test_index_parts():
    """Test availability and readability of index."""

    # Availability
    assert rocks.config.PATH_INDEX.is_dir()

    # Readability
    assert isinstance(index, dict)
    assert id_ in index
