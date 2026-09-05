from pathlib import Path


BACKUP = Path("Minify/core/backup_manager.py")
TESTS = Path("tests/test_backup_security.py")


def replace_once(text: str, old: str, new: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected exactly one replacement target, found {count}: {old[:80]!r}")
    return text.replace(old, new, 1)


text = BACKUP.read_text(encoding="utf-8")
text = replace_once(text, "import shutil\nimport tempfile\n", "import shutil\nimport stat\nimport tempfile\n")

old_read = '''def _read_manifest(snapshot: str) -> dict:
    try:
        path = _manifest_path(snapshot)
        if os.path.islink(path) or not os.path.isfile(path):
            return {}
        if os.path.getsize(path) > MAX_MANIFEST_BYTES:
            return {}
        with open(path, encoding="utf-8-sig") as file:
            data = json.load(file)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}
'''
new_read = '''def _read_manifest(snapshot: str) -> dict:
    fd = None
    try:
        path = _manifest_path(snapshot)
        before = os.stat(path, follow_symlinks=False)
        if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_MANIFEST_BYTES:
            return {}

        flags = os.O_RDONLY
        if hasattr(os, "O_BINARY"):
            flags |= os.O_BINARY
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        fd = os.open(path, flags)
        opened = os.fstat(fd)
        if not stat.S_ISREG(opened.st_mode) or opened.st_size > MAX_MANIFEST_BYTES:
            return {}
        if (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino):
            return {}

        with os.fdopen(fd, "r", encoding="utf-8-sig") as file:
            fd = None
            data = json.load(file)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}
    finally:
        if fd is not None:
            try:
                os.close(fd)
            except OSError:
                pass
'''
text = replace_once(text, old_read, new_read)

anchor = '''def _validated_manifest_outputs(value) -> list[str]:
'''
helper = '''def _managed_output_path(output_path: str, relative: str) -> str:
    canonical = str(relative).replace("\\\\", "/").strip("/")
    if canonical not in _MANAGED_CANONICAL:
        raise ValueError(f"Unmanaged output path: {relative!r}")
    _, destination = security.confined_destination(output_path, canonical)
    return destination


'''
if helper not in text:
    text = replace_once(text, anchor, helper + anchor)

old_create = '''def create_restore_point(output_path: str, selected_mods=None, reason="pre-patch") -> str:
    output_path = _validated_output_path(output_path)
    os.makedirs(_root(), exist_ok=True)
'''
new_create = '''def create_restore_point(output_path: str, selected_mods=None, reason="pre-patch") -> str:
    output_path = _validated_output_path(output_path)
    live_paths = {
        relative.replace(os.sep, "/"): _managed_output_path(output_path, relative) for relative in MANAGED_OUTPUTS
    }
    os.makedirs(_root(), exist_ok=True)
'''
text = replace_once(text, old_create, new_create)
text = replace_once(
    text,
    '''    for relative in MANAGED_OUTPUTS:
        source = os.path.join(output_path, relative)
        destination = os.path.join(snapshot, "output", relative)
''',
    '''    for relative in MANAGED_OUTPUTS:
        source = live_paths[relative.replace(os.sep, "/")]
        destination = os.path.join(snapshot, "output", relative)
''',
)

old_restore = '''    output_path = _validated_output_path(manifest.get("output_path"))
    existing = _validated_manifest_outputs(manifest.get("existing_managed_outputs", []))

    sources: dict[str, str] = {}
'''
new_restore = '''    output_path = _validated_output_path(manifest.get("output_path"))
    existing = _validated_manifest_outputs(manifest.get("existing_managed_outputs", []))
    live_paths = {
        relative.replace(os.sep, "/"): _managed_output_path(output_path, relative) for relative in MANAGED_OUTPUTS
    }

    sources: dict[str, str] = {}
'''
text = replace_once(text, old_restore, new_restore)

expected_current_count = text.count("current = os.path.join(output_path, relative)")
if expected_current_count != 3:
    raise RuntimeError(f"Expected 3 live-output current-path sites, found {expected_current_count}")
text = text.replace(
    "current = os.path.join(output_path, relative)",
    'current = live_paths[relative.replace(os.sep, "/")]',
)
text = replace_once(
    text,
    '''                destination = os.path.join(output_path, relative)
                os.makedirs(os.path.dirname(destination), exist_ok=True)
''',
    '''                destination = live_paths[canonical]
                os.makedirs(os.path.dirname(destination), exist_ok=True)
''',
)

BACKUP.write_text(text, encoding="utf-8")


tests = TESTS.read_text(encoding="utf-8")
marker = "def test_backup_manifest_reader_rejects_swap_to_symlink"
if marker not in tests:
    tests += '''\n\ndef _configure_backup_paths(monkeypatch, tmp_path):
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
'''
    TESTS.write_text(tests, encoding="utf-8")

print("Backup path hardening applied")
