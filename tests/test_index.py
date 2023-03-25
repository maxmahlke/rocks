import rocks


def test_build_index():
    """Build the asteroid name-number index."""
    rocks.index._build_index()


def test_load_partial():
    """Load part of the index and look up asteroid."""

    for id_ in ["mette", "2012aa14", 230, 12301]:
        partial = rocks.index._get_index_file(id_)
        assert id_ in partial
