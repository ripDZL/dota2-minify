import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../Minify")))

from browsers.d2pfx import build_hook


def _symlink_or_skip(link, target):
    try:
        link.symlink_to(target, target_is_directory=target.is_dir())
    except OSError:
        pytest.skip("symlink creation is unavailable on this platform")


def test_atomic_cursor_copy_accepts_regular_file(tmp_path):
    source_root = tmp_path / "source"
    destination_root = tmp_path / "destination"
    source_root.mkdir()
    destination_root.mkdir()
    source = source_root / "arrow.cur"
    destination = destination_root / "arrow.cur"
    source.write_bytes(b"cursor-data")

    build_hook._atomic_copy_regular_file(
        str(source),
        str(destination),
        source_root=str(source_root),
        destination_root=str(destination_root),
    )

    assert destination.read_bytes() == b"cursor-data"


def test_atomic_cursor_copy_rejects_symlink_source(tmp_path):
    source_root = tmp_path / "source"
    destination_root = tmp_path / "destination"
    source_root.mkdir()
    destination_root.mkdir()
    outside = tmp_path / "outside.cur"
    outside.write_bytes(b"outside")
    source = source_root / "arrow.cur"
    _symlink_or_skip(source, outside)

    with pytest.raises(ValueError):
        build_hook._atomic_copy_regular_file(
            str(source),
            str(destination_root / "arrow.cur"),
            source_root=str(source_root),
            destination_root=str(destination_root),
        )


def test_atomic_cursor_copy_rejects_symlink_destination(tmp_path):
    source_root = tmp_path / "source"
    destination_root = tmp_path / "destination"
    source_root.mkdir()
    destination_root.mkdir()
    source = source_root / "arrow.cur"
    source.write_bytes(b"new")
    outside = tmp_path / "outside.cur"
    outside.write_bytes(b"original")
    destination = destination_root / "arrow.cur"
    _symlink_or_skip(destination, outside)

    with pytest.raises(ValueError):
        build_hook._atomic_copy_regular_file(
            str(source),
            str(destination),
            source_root=str(source_root),
            destination_root=str(destination_root),
        )

    assert outside.read_bytes() == b"original"


def test_atomic_cursor_copy_rejects_symlink_parent_escape(tmp_path):
    source_root = tmp_path / "source"
    destination_root = tmp_path / "destination"
    outside = tmp_path / "outside"
    source_root.mkdir()
    destination_root.mkdir()
    outside.mkdir()
    source = source_root / "arrow.cur"
    source.write_bytes(b"cursor")
    escaped_parent = destination_root / "dota"
    _symlink_or_skip(escaped_parent, outside)

    with pytest.raises(ValueError):
        build_hook._atomic_copy_regular_file(
            str(source),
            str(escaped_parent / "resource" / "cursor" / "arrow.cur"),
            source_root=str(source_root),
            destination_root=str(destination_root),
        )

    assert not (outside / "resource" / "cursor" / "arrow.cur").exists()


def test_collect_cursor_files_rejects_symlink_file(tmp_path):
    mod = tmp_path / "mod"
    cursor = mod / "cursor"
    cursor.mkdir(parents=True)
    outside = tmp_path / "outside.cur"
    outside.write_bytes(b"outside")
    _symlink_or_skip(cursor / "arrow.cur", outside)

    with pytest.raises(ValueError):
        build_hook._collect_cursor_files([str(mod)])


def test_restore_cursor_backup_is_confined_and_removed_after_success(monkeypatch, tmp_path):
    minify_root = tmp_path / "minify"
    mods_dir = minify_root / "mods"
    mods_dir.mkdir(parents=True)
    game_root = tmp_path / "game"
    live_cursor = game_root / "dota" / "resource" / "cursor"
    live_cursor.mkdir(parents=True)
    live_file = live_cursor / "arrow.cur"
    live_file.write_bytes(b"modified")

    backup_file = minify_root / "backup" / "d2pfx_cursors" / "dota" / "resource" / "cursor" / "arrow.cur"
    backup_file.parent.mkdir(parents=True)
    backup_file.write_bytes(b"original")

    monkeypatch.setattr(build_hook.base, "mods_dir", str(mods_dir))
    monkeypatch.setattr(build_hook.constants, "dota_game_pak_path", str(game_root / "dota" / "pak01_dir.vpk"))
    monkeypatch.setattr(build_hook.output, "add_text", lambda *args, **kwargs: None)
    monkeypatch.setattr(build_hook.log, "write_warning", lambda *args, **kwargs: None)

    build_hook.restore_d2pfx_cursors()

    assert live_file.read_bytes() == b"original"
    assert not (minify_root / "backup" / "d2pfx_cursors").exists()


def test_restore_cursor_backup_rejects_symlink_and_keeps_recovery_tree(monkeypatch, tmp_path):
    minify_root = tmp_path / "minify"
    mods_dir = minify_root / "mods"
    mods_dir.mkdir(parents=True)
    game_root = tmp_path / "game"
    live_cursor = game_root / "dota" / "resource" / "cursor"
    live_cursor.mkdir(parents=True)
    live_file = live_cursor / "arrow.cur"
    live_file.write_bytes(b"live")

    backup_dir = minify_root / "backup" / "d2pfx_cursors" / "dota" / "resource" / "cursor"
    backup_dir.mkdir(parents=True)
    outside = tmp_path / "outside.cur"
    outside.write_bytes(b"outside")
    _symlink_or_skip(backup_dir / "arrow.cur", outside)

    monkeypatch.setattr(build_hook.base, "mods_dir", str(mods_dir))
    monkeypatch.setattr(build_hook.constants, "dota_game_pak_path", str(game_root / "dota" / "pak01_dir.vpk"))
    monkeypatch.setattr(build_hook.output, "add_text", lambda *args, **kwargs: None)
    monkeypatch.setattr(build_hook.log, "write_warning", lambda *args, **kwargs: None)

    build_hook.restore_d2pfx_cursors()

    assert live_file.read_bytes() == b"live"
    assert (minify_root / "backup" / "d2pfx_cursors").exists()
    assert outside.read_bytes() == b"outside"
