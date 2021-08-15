#! /usr/bin/env python
"""Test suit for rocks.utils module.
"""

import json
import os
import pickle
import warnings

import pandas as pd
import pickle
import pytest
import requests

import rocks


# def test_create_index(monkeypatch):
#     """Tests index creation routine with cached file and no missing entries."""

#     def read_fwf_monkey(url, colspecs, names):

#         PATH_INDEX = pd.read_csv(
#             os.path.join(os.path.expanduser("~"), ".cache/rocks/index.pkl")
#         )

#         with open(PATH_INDEX, "rb") as file_:
#             index = pickle.load(file_)
#         print(index)

#         return index[:1000]

#     monkeypatch.setattr(pd, "read_fwf", read_fwf_monkey)
#     rocks.utils.create_index()


def test_read_index():
    """Test availability and readability of index."""

    # Availability
    assert os.path.isfile(rocks.PATH_INDEX)

    # Readability
    index = rocks.utils.read_index()
    assert isinstance(index, pd.DataFrame)
