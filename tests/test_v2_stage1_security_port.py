from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import stat
import zipfile
import zlib

import pytest


ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "V2_STAGING" / "Minify"
SECURITY_PATH = STAGE / "core" / "security.py"
FS_PATH = STAGE / "core" / "fs.py"


def _load_security():
    spec = spec_from_file_location("v2_staging_security", SECURITY_PATH)
    module = module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_v2_stage1_files_track_exact_target():
    readme = (ROOT / "V2_STAGING" / "README.md").read_text(encoding="utf-8")
    assert "Minify-v2rc4" in readme
    assert "e444454684c2d7f809e7eef20a1b72d4422c50d7" in readme


def test_v2_security_rejects_path_escape_shapes():
    security = _load_security()
    for value in ("../escape", "/absolute", "C:/drive", r"..\escape", r"\\server\share"):
        with pytest.raises(ValueError):
            security.safe_relative_path(value)


def test_v2_security_rejects_private_https_targets():
    security = _load_security()
    with pytest.raises(ValueError):
        security.validate_public_https_url("https://127.0.0.1/payload.zip")
    with pytest.raises(ValueError):
        security.validate_public_https_url("http://8.8.8.8/payload.zip")
    security.validate_public_https_url("https://8.8.8.8/payload.zip")


def test_v2_security_safe_download_name_is_flat_and_extension_gated():
    security = _load_security()
    assert security.safe_download_filename(
        "https://example.invalid/path/mod.zip?token=secret",
        allowed_extensions={".zip"},
    ) == "mod.zip"
    assert security.safe_download_filename(
        "https://example.invalid/path/CON.zip",
        allowed_extensions={".zip"},
    ) == "_CON.zip"
    with pytest.raises(ValueError):
        security.safe_download_filename(
            "https://example.invalid/path/mod.exe",
            allowed_extensions={".zip", ".vpk"},
        )


def test_v2_security_bounded_zlib_rejects_oversized_output():
    security = _load_security()
    payload = zlib.compress(b"A" * 4096)
    with pytest.raises(ValueError):
        security.bounded_zlib_decompress(payload, max_output=128)


def test_v2_security_zip_rejects_traversal_and_symlink(tmp_path):
    security = _load_security()

    traversal = tmp_path / "traversal.zip"
    with zipfile.ZipFile(traversal, "w") as archive:
        archive.writestr("../escape.txt", b"x")
    with pytest.raises(ValueError):
        security.safe_extract_zip(str(traversal), str(tmp_path / "out1"))

    symlink = tmp_path / "symlink.zip"
    info = zipfile.ZipInfo("link")
    info.create_system = 3
    info.external_attr = (stat.S_IFLNK | 0o777) << 16
    with zipfile.ZipFile(symlink, "w") as archive:
        archive.writestr(info, b"target")
    with pytest.raises(ValueError):
        security.safe_extract_zip(str(symlink), str(tmp_path / "out2"))


def test_v2_fs_port_uses_atomic_bounded_download_and_shared_archive_security():
    source = FS_PATH.read_text(encoding="utf-8")
    for token in (
        "tempfile.mkstemp",
        "os.replace(temporary, target_path)",
        "max_bytes: int | None = security.ARCHIVE_MAX_FILE_BYTES",
        "allow_redirects=False",
        "_validated_stream_response",
        "security.safe_extract_archive",
        "emit_progress: bool = True",
        "task_id: Optional[str] = None",
    ):
        assert token in source
    assert "zip_ref.extractall" not in source
    assert "tar.extractall" not in source
