#!/usr/bin/env python
"""Test suit for rocks.utils module. """

import rocks


def test_index_parts():
    """Test availability and readability of index."""

    # Availability
    assert rocks.config.PATH_INDEX.is_dir()

    # Readability
    for id_ in ["mette", "2012aa14", 230, 12301]:
        index = rocks.index._get_index_file(id_)
        assert isinstance(index, dict)
        assert id_ in index
