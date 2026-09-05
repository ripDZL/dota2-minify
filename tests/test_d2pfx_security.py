import gzip
import json
import os
import sys
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../Minify")))

from browsers.d2pfx import data as d2pfx_data


class _FakeResponse:
    def __init__(self, payload, status_code=200):
        self.payload = payload
        self.status_code = status_code
        self.closed = False

    def iter_content(self, chunk_size=65536):
        for index in range(0, len(self.payload), chunk_size):
            yield self.payload[index : index + chunk_size]

    def close(self):
        self.closed = True


def _manager(monkeypatch, tmp_path):
    cache = tmp_path / "d2pfx"
    previews = cache / "previews"
    monkeypatch.setattr(d2pfx_data, "CACHE_DIR", str(cache))
    monkeypatch.setattr(d2pfx_data, "PREVIEWS_CACHE_DIR", str(previews))
    return d2pfx_data.DataManager()


@patch("browsers.d2pfx.data.requests.get")
def test_d2pfx_catalogue_uses_bounded_stream_and_atomic_cache(mock_get, monkeypatch, tmp_path):
    manager = _manager(monkeypatch, tmp_path)
    payload = gzip.compress(json.dumps({"modsData": {"terrain": []}}).encode())
    response = _FakeResponse(payload)
    mock_get.return_value = response

    result = manager.fetch_gz_json("mods.json.gz", force_refresh=True)

    assert result == {"modsData": {"terrain": []}}
    assert response.closed is True
    assert mock_get.call_args.kwargs["stream"] is True
    assert mock_get.call_args.kwargs["timeout"] == (10, 30)
    assert json.loads((tmp_path / "d2pfx" / "mods.json").read_text()) == result
    assert not list((tmp_path / "d2pfx").glob(".d2pfx-catalogue-*"))


@patch("browsers.d2pfx.data.requests.get")
def test_d2pfx_catalogue_rejects_decompression_over_limit(mock_get, monkeypatch, tmp_path):
    manager = _manager(monkeypatch, tmp_path)
    monkeypatch.setattr(d2pfx_data.security, "D2PFX_MAX_MANIFEST_BYTES", 64)
    payload = gzip.compress(json.dumps({"modsData": {"x": "A" * 256}}).encode())
    response = _FakeResponse(payload)
    mock_get.return_value = response

    assert manager.fetch_gz_json("mods.json.gz", force_refresh=True) is None
    assert response.closed is True
    assert not (tmp_path / "d2pfx" / "mods.json").exists()


def test_d2pfx_rejects_oversized_cached_catalogue(monkeypatch, tmp_path):
    manager = _manager(monkeypatch, tmp_path)
    monkeypatch.setattr(d2pfx_data.security, "D2PFX_MAX_MANIFEST_BYTES", 32)
    cached = tmp_path / "d2pfx" / "mods.json"
    cached.write_text("{" + ' "x": "' + "A" * 80 + '"}')

    with patch("browsers.d2pfx.data.requests.get", side_effect=RuntimeError("offline")):
        assert manager.fetch_gz_json("mods.json.gz") is None


@patch("browsers.d2pfx.data.requests.get")
def test_d2pfx_catalogue_closes_non_200_response(mock_get, monkeypatch, tmp_path):
    manager = _manager(monkeypatch, tmp_path)
    response = _FakeResponse(b"", status_code=503)
    mock_get.return_value = response

    assert manager.fetch_gz_json("mods.json.gz", force_refresh=True) is None
    assert response.closed is True


def test_d2pfx_catalogue_rejects_unknown_filename_before_network(monkeypatch, tmp_path):
    manager = _manager(monkeypatch, tmp_path)
    with patch("browsers.d2pfx.data.requests.get") as mock_get:
        assert manager.fetch_gz_json("../../outside.json.gz", force_refresh=True) is None
    mock_get.assert_not_called()


def test_d2pfx_cached_catalogue_rejects_symlink(monkeypatch, tmp_path):
    manager = _manager(monkeypatch, tmp_path)
    outside = tmp_path / "outside.json"
    outside.write_text(json.dumps({"modsData": {"terrain": []}}))
    cached = tmp_path / "d2pfx" / "mods.json"
    try:
        cached.symlink_to(outside)
    except OSError:
        pytest.skip("symlink creation is unavailable on this platform")

    with patch("browsers.d2pfx.data.requests.get", side_effect=RuntimeError("offline")):
        assert manager.fetch_gz_json("mods.json.gz") is None
    assert outside.read_text() == json.dumps({"modsData": {"terrain": []}})


@patch("browsers.d2pfx.data.requests.get")
def test_d2pfx_mods_catalogue_requires_modsdata_object(mock_get, monkeypatch, tmp_path):
    manager = _manager(monkeypatch, tmp_path)
    payload = gzip.compress(json.dumps({"modsData": []}).encode())
    response = _FakeResponse(payload)
    mock_get.return_value = response

    assert manager.fetch_gz_json("mods.json.gz", force_refresh=True) is None
    assert response.closed is True
    assert not (tmp_path / "d2pfx" / "mods.json").exists()


def test_d2pfx_categories_filter_unsafe_ids(monkeypatch, tmp_path):
    manager = _manager(monkeypatch, tmp_path)
    manager.metadata = {
        "modsData": {
            "heroes": [],
            "../escape": [],
            "nested/path": [],
            "fonts": [],
        }
    }

    assert manager.get_categories() == ["heroes"]


def test_d2pfx_asset_urls_reject_traversal_and_quote_safe_paths(monkeypatch, tmp_path):
    manager = _manager(monkeypatch, tmp_path)

    with pytest.raises(ValueError):
        manager.get_file_url("heroes", "../escape.vpk")
    with pytest.raises(ValueError):
        manager.get_file_url("heroes", "%2e%2e/escape.vpk")
    with pytest.raises(ValueError):
        manager.get_preview_url("../heroes", "preview.jpg")

    url = manager.get_file_url("hero-items", "Pudge Set/mod file.vpk")
    assert url.endswith("hero-items/Pudge%20Set/mod%20file.vpk")


def test_d2pfx_mod_flattening_is_bounded_and_handles_malformed_links(monkeypatch, tmp_path):
    manager = _manager(monkeypatch, tmp_path)
    monkeypatch.setattr(d2pfx_data, "MAX_FLATTEN_DEPTH", 3)
    monkeypatch.setattr(d2pfx_data, "MAX_MODS_PER_CATEGORY", 2)

    deep = {"name": "Too Deep"}
    for _ in range(10):
        deep = {"groups": [deep]}
    manager.metadata = {
        "modsData": {
            "heroes": [
                {"name": "One", "links": "not-a-list"},
                {"name": "Two", "links": [{"type": "author", "name": "Alice"}]},
                deep,
                {"name": "Three"},
            ]
        }
    }

    mods = manager.get_mods("heroes")
    assert len(mods) == 2
    assert [mod["name"] for mod in mods] == ["One", "Two"]
    assert mods[0]["author"] is None
    assert mods[1]["author"] == "Alice"
