import io
import os
import sys
import tarfile
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../Minify")))

from core.fs import download_file, extract_archive


def test_extract_archive_rejects_traversal_archive_atomically(tmp_path):
    tar_path = tmp_path / "malicious.tar.gz"
    extract_dir = tmp_path / "extract_dir"
    extract_dir.mkdir()

    with tarfile.open(tar_path, "w:gz") as tar:
        safe_info = tarfile.TarInfo(name="safe.txt")
        safe_info.size = len(b"safe")
        tar.addfile(safe_info, io.BytesIO(b"safe"))

        malicious_info = tarfile.TarInfo(name="../malicious.txt")
        malicious_info.size = len(b"malicious payload")
        tar.addfile(malicious_info, io.BytesIO(b"malicious payload"))

    success = extract_archive(str(tar_path), extract_dir=str(extract_dir))

    assert success is False
    assert not (extract_dir / "safe.txt").exists()
    assert not (tmp_path / "malicious.txt").exists()


def test_extract_archive_target_file_safe(tmp_path):
    tar_path = tmp_path / "test.tar.gz"
    extract_dir = tmp_path / "extract_dir"
    extract_dir.mkdir()

    with tarfile.open(tar_path, "w:gz") as tar:
        info = tarfile.TarInfo(name="safe.txt")
        info.size = len(b"safe")
        tar.addfile(info, io.BytesIO(b"safe"))

    success = extract_archive(str(tar_path), extract_dir=str(extract_dir), target_file="safe.txt")
    assert success is True
    assert (extract_dir / "safe.txt").exists()


def test_extract_archive_rejects_malicious_target_file(tmp_path):
    tar_path = tmp_path / "test.tar.gz"
    extract_dir = tmp_path / "extract_dir"
    extract_dir.mkdir()

    with tarfile.open(tar_path, "w:gz") as tar:
        info = tarfile.TarInfo(name="../malicious.txt")
        info.size = len(b"payload")
        tar.addfile(info, io.BytesIO(b"payload"))

    success = extract_archive(str(tar_path), extract_dir=str(extract_dir), target_file="../malicious.txt")

    assert success is False
    assert not (tmp_path / "malicious.txt").exists()


@patch("core.fs.output.add_text")
def test_extract_archive_unsupported_format(mock_add_text, tmp_path):
    dummy_file = tmp_path / "test.txt"
    dummy_file.write_text("not an archive")

    success = extract_archive(str(dummy_file), extract_dir=str(tmp_path))
    assert success is False
    mock_add_text.assert_called()
    args, kwargs = mock_add_text.call_args
    assert "Unsupported archive format" in args[0]
    assert kwargs["msg_type"] == "error"


@patch("core.fs.output.add_text")
def test_extract_archive_nonexistent_file(mock_add_text, tmp_path):
    nonexistent = tmp_path / "ghost.tar.gz"

    success = extract_archive(str(nonexistent), extract_dir=str(tmp_path))
    assert success is False
    args, kwargs = mock_add_text.call_args
    assert "Extraction failed" in args[0]
    assert kwargs["msg_type"] == "error"


class _FakeResponse:
    def __init__(self, chunks, content_length=0, status_code=200, headers=None, url=""):
        self._chunks = chunks
        self.headers = dict(headers or {})
        if content_length:
            self.headers["content-length"] = str(content_length)
        self.status_code = status_code
        self.closed = False
        self.url = url

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")
        return None

    def iter_content(self, chunk_size=8192):
        yield from self._chunks

    def close(self):
        self.closed = True


@patch("core.fs.output.add_text")
@patch("core.fs.requests.get")
def test_download_file_rejects_declared_oversize(mock_get, mock_add_text, tmp_path):
    response = _FakeResponse([b"ignored"], content_length=101)
    mock_get.return_value = response
    target = tmp_path / "payload.bin"

    assert download_file("https://example.invalid/payload", str(target), max_bytes=100) is False
    assert not target.exists()
    assert response.closed is True
    assert mock_get.call_args.kwargs["timeout"] == (10, 60)
    assert "safety limit" in mock_add_text.call_args.args[0]


@patch("core.fs.output.add_text")
@patch("core.fs.requests.get")
def test_download_file_aborts_stream_over_limit_without_replacing_target(mock_get, mock_add_text, tmp_path):
    response = _FakeResponse([b"12345", b"67890", b"X"])
    mock_get.return_value = response
    target = tmp_path / "payload.bin"
    target.write_bytes(b"existing")

    assert download_file("https://example.invalid/payload", str(target), max_bytes=10) is False
    assert target.read_bytes() == b"existing"
    assert not list(tmp_path.glob(".minify-download-*"))
    assert response.closed is True
    assert "safety limit" in mock_add_text.call_args.args[0]


@patch("core.fs.output.add_text")
@patch("core.fs.requests.get")
def test_download_file_validates_every_redirect_before_request(mock_get, mock_add_text, tmp_path):
    redirect = _FakeResponse(
        [],
        status_code=302,
        headers={"location": "https://blocked.invalid/file.bin"},
        url="https://public.invalid/start",
    )
    mock_get.return_value = redirect
    validated = []

    def validator(url):
        validated.append(url)
        if "blocked.invalid" in url:
            raise ValueError("blocked target")

    target = tmp_path / "payload.bin"
    assert download_file(
        "https://public.invalid/start",
        str(target),
        url_validator=validator,
    ) is False

    assert validated == ["https://public.invalid/start", "https://blocked.invalid/file.bin"]
    assert mock_get.call_count == 1
    assert mock_get.call_args.kwargs["allow_redirects"] is False
    assert redirect.closed is True
    assert not target.exists()
    assert "blocked target" in mock_add_text.call_args.args[0]


@patch("core.fs.output.add_text")
@patch("core.fs.requests.get")
def test_download_file_accepts_validated_redirect_chain(mock_get, mock_add_text, tmp_path):
    first = _FakeResponse(
        [],
        status_code=302,
        headers={"location": "/final.bin"},
        url="https://public.invalid/start",
    )
    final = _FakeResponse([b"payload"], status_code=200, url="https://public.invalid/final.bin")
    mock_get.side_effect = [first, final]
    validated = []

    target = tmp_path / "payload.bin"
    assert download_file(
        "https://public.invalid/start",
        str(target),
        max_bytes=100,
        url_validator=validated.append,
    ) is True

    assert target.read_bytes() == b"payload"
    assert validated == [
        "https://public.invalid/start",
        "https://public.invalid/final.bin",
        "https://public.invalid/final.bin",
    ]
    assert first.closed is True
    assert final.closed is True
    assert mock_get.call_count == 2
    mock_add_text.assert_not_called()
