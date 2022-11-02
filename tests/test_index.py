import pytest

from rocks import index


def test_load_partial():
    """Load part of the index and look up asteroid."""

    name = "massalia"
    part = index._get_index_file("massalia")

    assert "massalia" in part


def test_index_modification_date():
    """Get the modification date of the index."""
    index.get_modification_date()
