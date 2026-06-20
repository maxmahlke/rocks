import pandas as pd
from pathlib import Path

from rocks import bft


# Flip to True to use tests/data/ssoBFT-latest_Asteroid.parquet as the BFT source
# for non-cache-miss tests.
USE_SEPARATE_TEST_BFT_FILE = True
TEST_BFT_FILE = Path(__file__).parent / "data" / "ssoBFT-latest_Asteroid.parquet"


def _configure_bft_source(monkeypatch, tmp_path, cacheless=False):
    """Set bft source path, optionally using a dedicated fixture parquet file."""
    if USE_SEPARATE_TEST_BFT_FILE:
        if not TEST_BFT_FILE.is_file():
            raise FileNotFoundError(f"Missing test BFT file: {TEST_BFT_FILE}")
        source = TEST_BFT_FILE
    else:
        source = tmp_path / "ssoBFT-latest_Asteroid.parquet"
        source.touch()

    monkeypatch.setattr(bft, "PATH", source)
    monkeypatch.setattr(bft.config, "CACHELESS", cacheless)
    return source


def _patch_read_parquet(monkeypatch, frame):
    calls = {}

    def fake_read_parquet(load, **kwargs):
        calls["load"] = load
        calls["kwargs"] = kwargs
        return frame.copy()

    monkeypatch.setattr(bft.pd, "read_parquet", fake_read_parquet)
    return calls


def test_load_bft_uses_cached_path_and_default_columns(monkeypatch, tmp_path):
    cache_path = _configure_bft_source(monkeypatch, tmp_path)

    frame = pd.DataFrame({"sso_number": [1, 2], "foo": [10, 20]})
    calls = _patch_read_parquet(monkeypatch, frame)

    loaded = bft.load_bft()

    assert calls["load"] == cache_path
    assert calls["kwargs"]["columns"] == bft.COLUMNS
    assert str(loaded["sso_number"].dtype) == "Int64"


def test_load_bft_full_does_not_force_default_columns(monkeypatch, tmp_path):
    cache_path = _configure_bft_source(monkeypatch, tmp_path)

    frame = pd.DataFrame({"sso_number": [1]})
    calls = _patch_read_parquet(monkeypatch, frame)

    _ = bft.load_bft(full=True)

    assert calls["load"] == cache_path
    assert "columns" not in calls["kwargs"]


def test_load_bft_respects_explicit_columns(monkeypatch, tmp_path):
    _configure_bft_source(monkeypatch, tmp_path)

    frame = pd.DataFrame({"sso_number": [1]})
    calls = _patch_read_parquet(monkeypatch, frame)

    custom_columns = ["sso_id"]
    _ = bft.load_bft(columns=custom_columns)

    assert calls["kwargs"]["columns"] == custom_columns


def test_load_bft_cache_miss_decline_download_returns_none(monkeypatch, tmp_path):
    cache_path = tmp_path / "ssoBFT-latest_Asteroid.parquet"

    monkeypatch.setattr(bft, "PATH", cache_path)
    monkeypatch.setattr(bft.config, "CACHELESS", False)

    monkeypatch.setattr(bft.prompt.Confirm, "ask", lambda *_args, **_kwargs: False)

    read_called = {"value": False}

    def fake_read_parquet(*_args, **_kwargs):
        read_called["value"] = True
        return pd.DataFrame()

    monkeypatch.setattr(bft.pd, "read_parquet", fake_read_parquet)

    loaded = bft.load_bft()

    assert loaded is None
    assert not read_called["value"]


def test_load_bft_cache_miss_accept_download(monkeypatch, tmp_path):
    cache_path = tmp_path / "ssoBFT-latest_Asteroid.parquet"

    monkeypatch.setattr(bft, "PATH", cache_path)
    monkeypatch.setattr(bft.config, "CACHELESS", False)
    monkeypatch.setattr(bft.prompt.Confirm, "ask", lambda *_args, **_kwargs: True)

    get_bft_called = {"value": False}

    def fake_get_bft():
        get_bft_called["value"] = True

    monkeypatch.setattr(bft.ssodnet, "_get_bft", fake_get_bft)

    frame = pd.DataFrame({"sso_number": [7]})
    calls = _patch_read_parquet(monkeypatch, frame)

    loaded = bft.load_bft()

    assert get_bft_called["value"]
    assert calls["load"] == cache_path
    assert str(loaded["sso_number"].dtype) == "Int64"


def test_load_bft_cacheless_reads_remote_url(monkeypatch, tmp_path):
    _configure_bft_source(monkeypatch, tmp_path, cacheless=True)
    monkeypatch.setattr(bft.ssodnet, "URL_SSODNET", "https://example.test")

    frame = pd.DataFrame({"foo": [1, 2, 3]})
    calls = _patch_read_parquet(monkeypatch, frame)

    loaded = bft.load_bft()

    assert calls["load"] == "https://example.test/data/ssoBFT-latest_Asteroid.parquet"
    assert calls["kwargs"]["columns"] == bft.COLUMNS
    assert list(loaded.columns) == ["foo"]
