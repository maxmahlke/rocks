def pytest_collection_modifyitems(items):
    """Ensure that the build-index test is executed first if it is among the tests to run."""

    for idx, item in enumerate(items):
        if item.originalname == "test_build_index":
            break
    else:
        return

    build_index_test = items.pop(idx)
    items.insert(0, build_index_test)
