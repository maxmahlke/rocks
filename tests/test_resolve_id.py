"""Test class ID implementation."""

import rocks


def test_id():
    """Ensure that ID class works as expected."""

    match = {
        "name": "Ceres",
        "class_": ["MB"],
        "number": 1,
        "aliases": ["Ceres"],
        "ephemeris": False,
        "links": {"self": "https://api.ssodnet.imcce.fr/quaero/1/sso/101P"},
        "parent": "Sun",
        "physical_ephemeris": False,
        "physical_models": [1],
        "system": "Earth",
        "type": "Asteroid",
        "updated": "2024-04-08",
        "id": "101P",
    }

    id = rocks.resolve.id.ID(**match)

    for key, val in match.items():
        assert getattr(id, key) == val
