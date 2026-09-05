import os
import socket
import sys
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../Minify")))

from browsers.d2pfx import data as d2pfx_data


def test_d2pfx_remote_url_rejects_http_private_and_credentials():
    with pytest.raises(ValueError):
        d2pfx_data.validate_public_https_url("http://example.com/file.vpk")
    with pytest.raises(ValueError):
        d2pfx_data.validate_public_https_url("https://127.0.0.1/file.vpk")
    with pytest.raises(ValueError):
        d2pfx_data.validate_public_https_url("https://10.1.2.3/file.vpk")
    with pytest.raises(ValueError):
        d2pfx_data.validate_public_https_url("https://user:pass@example.com/file.vpk")
    with pytest.raises(ValueError):
        d2pfx_data.validate_public_https_url("https://example.com:8443/file.vpk")


def test_d2pfx_remote_url_accepts_public_dns(monkeypatch):
    monkeypatch.setattr(
        d2pfx_data.socket,
        "getaddrinfo",
        lambda *args, **kwargs: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443))],
    )

    d2pfx_data.validate_public_https_url("https://example.com/file.vpk")


def test_d2pfx_remote_url_rejects_mixed_public_private_dns(monkeypatch):
    monkeypatch.setattr(
        d2pfx_data.socket,
        "getaddrinfo",
        lambda *args, **kwargs: [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443)),
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("192.168.1.10", 443)),
        ],
    )

    with pytest.raises(ValueError):
        d2pfx_data.validate_public_https_url("https://mixed.example/file.vpk")


def test_d2pfx_remote_url_fails_closed_on_dns_error(monkeypatch):
    def fail(*args, **kwargs):
        raise OSError("dns failed")

    monkeypatch.setattr(d2pfx_data.socket, "getaddrinfo", fail)
    with pytest.raises(ValueError):
        d2pfx_data.validate_public_https_url("https://unresolved.example/file.vpk")


def test_d2pfx_data_manager_forwards_validator_and_limit(monkeypatch, tmp_path):
    manager = d2pfx_data.DataManager.__new__(d2pfx_data.DataManager)
    captured = {}

    def fake_download(url, dest, **kwargs):
        captured.update(url=url, dest=dest, **kwargs)
        return True

    monkeypatch.setattr(d2pfx_data.fs, "download_file", fake_download)
    target = tmp_path / "mod.vpk"

    assert manager.download_file("https://example.com/mod.vpk", str(target), max_bytes=1234) is True
    assert captured["max_bytes"] == 1234
    assert captured["url_validator"] is d2pfx_data.validate_public_https_url
    assert captured["max_redirects"] == 5


def test_safe_download_filename_uses_url_path_not_query():
    assert (
        d2pfx_data.safe_download_filename(
            "https://example.com/files/mod%20name.vpk?token=a%3Fb&download=1",
            allowed_extensions={".vpk", ".zip"},
        )
        == "mod name.vpk"
    )


def test_safe_download_filename_rejects_bad_extension_and_guards_reserved_name():
    with pytest.raises(ValueError):
        d2pfx_data.safe_download_filename("https://example.com/file.exe", allowed_extensions={".vpk", ".zip"})

    assert d2pfx_data.safe_download_filename("https://example.com/CON.vpk") == "_CON.vpk"


def test_safe_download_filename_bounds_long_names():
    name = "a" * 400 + ".zip"
    result = d2pfx_data.safe_download_filename(f"https://example.com/{name}", allowed_extensions={".zip"})
    assert len(result) <= 180
    assert result.endswith(".zip")
