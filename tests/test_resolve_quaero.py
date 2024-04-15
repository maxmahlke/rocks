"""Test quaero-query functionality."""

import asyncio
import pytest

from rocks.resolve import quaero

# fmt: off
QUERY_RESULT = {
    # query string, type: expected result

    # asteroids
    #   - straight-forward, not ambiguity
    ("1", "asteroid"): {"name": "Ceres", "number": 1, "type": "Dwarf Planet"},
    ("pallas", "asteroid"): {"name": "Pallas", "number": 2, "type": "Asteroid"},

    # comets
    #   - if multiple matches due to name and fragmets, return main piece
    #   e.g. 'Chernykh' -> '101P', '101P-A', '101P-B', always return '101P'
    #   name, number: name is first alias, number is name in ssodnet database
    ("Chernykh", "comet"): {"name": "Chernykh", "number": "101P", "type": "Comet"},
    ("101P-A", "comet"): {"name": "Chernykh", "number": "101P-A", "type": "Comet"},
    ("P/1977 Q1", "comet"): {"name": "Chernykh", "number": "101P", "type": "Comet"},
    ("67p", "comet"): { "name": "Churyumov-Gerasimenko", "number": "67P", "type": "Comet"},

    # satellites
    #   - number is secondary, name is more important, and parent body
    ("moon", "satellite"): {"name": "Moon", "number": 301, "type": "Satellite"},
}
# fmt:on


@pytest.mark.parametrize("id, type", QUERY_RESULT.keys())
def test_query(id, type):
    """Ensure that query returns valid JSON with expected type of body."""

    match = asyncio.run(quaero.query(id=id, type=type))

    for key in ["name", "number", "type"]:
        assert key in match
        assert match[key] == QUERY_RESULT[(id, type)][key]
