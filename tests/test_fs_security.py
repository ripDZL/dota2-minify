import io
import os
import sys
import tarfile
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../Minify")))

from core.fs import extract_archive


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
