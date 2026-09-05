import json
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../Minify")))

from core import backup_manager


def test_backup_manifest_reader_rejects_symlink(tmp_path):
    snapshot = tmp_path / "snapshot"
    snapshot.mkdir()
    outside = tmp_path / "outside.json"
    outside.write_text(json.dumps({"schema_version": 1, "output_path": "outside"}))
    link = snapshot / "manifest.json"
    try:
        link.symlink_to(outside)
    except OSError:
        pytest.skip("symlink creation is unavailable on this platform")

    assert backup_manager._read_manifest(str(snapshot)) == {}


def test_backup_manifest_reader_accepts_small_regular_object(tmp_path):
    snapshot = tmp_path / "snapshot"
    snapshot.mkdir()
    manifest = {"schema_version": 1, "status": "created"}
    (snapshot / "manifest.json").write_text(json.dumps(manifest))

    assert backup_manager._read_manifest(str(snapshot)) == manifest
