#!/usr/bin/env python3
import json
import os

import pytest
import rocks


# Asteroids with datacloud catalogues in the test data directory
TEST_DATACLOUD = [("aams", "Massalia"), ("families", "Themis")]

# ------
# Monkeypatches for local data access
def get_ssocard_from_test_data(id_):
    """Monkeypatch function to read cached ssoCards from test files rather than
    query SsODNet.

    Parameter
    =========
    name : str
        The SsODNet ID of the object.

    Returns
    =======
    dict
        The ssoCard of the object.
    """
    PATH_DATA = os.path.join(os.path.dirname(__file__), f"data/ssocards/{id_}.json")

    with open(PATH_DATA, "r") as file_:
        data = json.load(file_)

    return data[id_]


def get_datacloud_from_test_data(id_, datacloud):
    """Monkeypatch function to read cached datacloud catalogue from test files rather than
    query SsODNet.

    Parameter
    =========
    name : str
        The SsODNet ID of the object.

    Returns
    =======
    list of dict
        The datacloud catalogue of the object.
    """
    PATH_DATA = os.path.join(
        os.path.dirname(__file__), f"data/datacloud/{datacloud}_{id_}.json"
    )

    with open(PATH_DATA, "r") as file_:
        data = json.load(file_)

    return [data]


# ------
# Test instantiation
@pytest.mark.parametrize("datacloud, id_", TEST_DATACLOUD, ids=str)
def test_single_datacloud(datacloud, id_, monkeypatch):
    """Test retrieval of single datacloud catalogues."""

    monkeypatch.setattr(rocks.ssodnet, "get_ssocard", get_ssocard_from_test_data)
    monkeypatch.setattr(
        rocks.ssodnet, "get_datacloud_catalogue", get_datacloud_from_test_data
    )

    # Test retrieval by passing string or list
    _ = rocks.Rock(id_, skip_id_check=True, datacloud=datacloud)
    _ = rocks.Rock(id_, skip_id_check=True, datacloud=[datacloud])
