#!/usr/bin/env python3
import warnings

import pytest
import rocks


@pytest.mark.parametrize("id_", ["Fortuna", "doesnotexist", "Ceres"])
def test_get_ssoCard(id_):
    warnings.filterwarnings("ignore", "UserWarning")
    card = rocks.ssodnet.get_ssocard(id_)

    if id_ == "Ceres":
        assert isinstance(card, dict)
    else:
        assert card is None
