from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKUP = ROOT / "Minify" / "core" / "backup_manager.py"
TEST = ROOT / "tests" / "test_backup_security.py"

text = BACKUP.read_text(encoding="utf-8")
old = '''        path = _manifest_path(snapshot)\n        if os.path.getsize(path) > MAX_MANIFEST_BYTES:\n            return {}\n        with open(path, encoding="utf-8-sig") as file:\n'''
new = '''        path = _manifest_path(snapshot)\n        if os.path.islink(path) or not os.path.isfile(path):\n            return {}\n        if os.path.getsize(path) > MAX_MANIFEST_BYTES:\n            return {}\n        with open(path, encoding="utf-8-sig") as file:\n'''
if old not in text:
    raise SystemExit("backup manifest read anchor not found")
BACKUP.write_text(text.replace(old, new, 1), encoding="utf-8")

TEST.write_text('''import json\nimport os\nimport sys\n\nimport pytest\n\nsys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../Minify")))\n\nfrom core import backup_manager\n\n\ndef test_backup_manifest_reader_rejects_symlink(tmp_path):\n    snapshot = tmp_path / "snapshot"\n    snapshot.mkdir()\n    outside = tmp_path / "outside.json"\n    outside.write_text(json.dumps({"schema_version": 1, "output_path": "outside"}))\n    link = snapshot / "manifest.json"\n    try:\n        link.symlink_to(outside)\n    except OSError:\n        pytest.skip("symlink creation is unavailable on this platform")\n\n    assert backup_manager._read_manifest(str(snapshot)) == {}\n\n\ndef test_backup_manifest_reader_accepts_small_regular_object(tmp_path):\n    snapshot = tmp_path / "snapshot"\n    snapshot.mkdir()\n    manifest = {"schema_version": 1, "status": "created"}\n    (snapshot / "manifest.json").write_text(json.dumps(manifest))\n\n    assert backup_manager._read_manifest(str(snapshot)) == manifest\n''', encoding="utf-8")
