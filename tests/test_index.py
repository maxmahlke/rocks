import rocks


def test_load_partial():
    """Load part of the index and look up asteroid."""

    for id_ in ["mette", "2012aa14", 230, 12301]:
        partial = rocks.index._get_index_file(id_)
        assert id_ in partial
