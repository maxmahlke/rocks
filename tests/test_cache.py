import pytest

from rocks import cache


def test_inventory():
    """Ensure that the inventory identifies ssoCards and catalogues."""
    ssocards, catalogues = cache.take_inventory()
