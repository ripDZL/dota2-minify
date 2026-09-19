from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "V2_STAGING" / "scripts" / "build.py"


def test_v2_build_uses_current_interpreter_not_nested_uv():
    source = BUILD.read_text(encoding="utf-8")
    assert 'sys.executable,' in source
    assert '"-m",' in source
    assert '"PyInstaller",' in source
    assert '["uv", "run", "pyinstaller"' not in source
    assert 'executable = "uv" if shutil.which("uv") else "pyinstaller"' not in source
