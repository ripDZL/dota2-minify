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


def test_backup_manifest_reader_rejects_non_file_manifest(tmp_path):
    snapshot = tmp_path / "snapshot"
    snapshot.mkdir()
    (snapshot / "manifest.json").mkdir()

    assert backup_manager._read_manifest(str(snapshot)) == {}


def _configure_backup_paths(monkeypatch, tmp_path):
    config_dir = tmp_path / "config"
    output_dir = tmp_path / "output"
    config_dir.mkdir()
    output_dir.mkdir()
    monkeypatch.setattr(backup_manager.base, "config_dir", str(config_dir))
    monkeypatch.setattr(backup_manager.base, "mods_config_dir", str(config_dir / "mods.json"))
    monkeypatch.setattr(backup_manager.constants, "minify_dota_possible_language_output_paths", [str(output_dir)])
    return config_dir, output_dir


def test_backup_manifest_reader_rejects_swap_to_symlink(monkeypatch, tmp_path):
    snapshot = tmp_path / "snapshot"
    snapshot.mkdir()
    manifest_path = snapshot / "manifest.json"
    manifest_path.write_text(json.dumps({"schema_version": 1, "status": "created"}))
    outside = tmp_path / "outside.json"
    outside.write_text(json.dumps({"schema_version": 1, "status": "attacker"}))

    real_open = backup_manager.os.open
    swapped = False

    def racing_open(path, flags, *args, **kwargs):
        nonlocal swapped
        if not swapped and os.path.abspath(path) == os.path.abspath(manifest_path):
            swapped = True
            manifest_path.unlink()
            try:
                manifest_path.symlink_to(outside)
            except OSError:
                pytest.skip("symlink creation is unavailable on this platform")
        return real_open(path, flags, *args, **kwargs)

    monkeypatch.setattr(backup_manager.os, "open", racing_open)
    assert backup_manager._read_manifest(str(snapshot)) == {}


def test_create_restore_point_rejects_managed_parent_symlink_escape(monkeypatch, tmp_path):
    config_dir, output_dir = _configure_backup_paths(monkeypatch, tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "dota.vpk").write_bytes(b"outside")
    try:
        (output_dir / "maps").symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("directory symlink creation is unavailable on this platform")

    with pytest.raises(ValueError, match="escapes destination root"):
        backup_manager.create_restore_point(str(output_dir), selected_mods=[])

    assert (outside / "dota.vpk").read_bytes() == b"outside"
    assert not (config_dir / backup_manager.BACKUP_DIR_NAME).exists()


def test_restore_rejects_managed_parent_symlink_escape_before_mutation(monkeypatch, tmp_path):
    config_dir, output_dir = _configure_backup_paths(monkeypatch, tmp_path)
    snapshot = config_dir / backup_manager.BACKUP_DIR_NAME / "snapshot"
    payload = snapshot / "output" / "maps"
    payload.mkdir(parents=True)
    (payload / "dota.vpk").write_bytes(b"backup")
    (snapshot / "manifest.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "status": "created",
                "output_path": str(output_dir),
                "existing_managed_outputs": ["maps/dota.vpk"],
            }
        )
    )

    keep = output_dir / "pak65_dir.vpk"
    keep.write_bytes(b"keep")
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "dota.vpk").write_bytes(b"outside")
    try:
        (output_dir / "maps").symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("directory symlink creation is unavailable on this platform")

    with pytest.raises(ValueError, match="escapes destination root"):
        backup_manager.restore_restore_point(str(snapshot), restore_selection=False)

    assert keep.read_bytes() == b"keep"
    assert (outside / "dota.vpk").read_bytes() == b"outside"
