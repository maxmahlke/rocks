import json
import pytest

from rocks import metadata


def test_rocks_version_check():
    """Check rocks version lookup on GitHub and locally."""
    metadata.rocks_is_outdated()


def test_retrieve_mappings():
    """Retrieve mappings JSON from SsODNet."""
    metadata.PATH_MAPPINGS = "/tmp/mappings.json"
    metadata.retrieve("mappings")


def test_retrieve_authors():
    """Retrieve biblio JSON from SsODNet."""
    metadata.PATH_AUTHORS = "/tmp/authors.json"
    metadata.retrieve("authors")
