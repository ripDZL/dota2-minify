from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "V2_STAGING" / "Minify"


def test_v2_developer_tools_restore_rc7_named_actions():
    app = (STAGE / "ui" / "app.py").read_text(encoding="utf-8")
    settings = (
        STAGE / "ui" / "web" / "src" / "lib" / "components" / "Settings.svelte"
    ).read_text(encoding="utf-8")
    types = (STAGE / "ui" / "web" / "src" / "global.d.ts").read_text(encoding="utf-8")

    assert "def run_developer_action(self, action: str)" in app
    for action in (
        "open_output",
        "open_output_vpk",
        "open_root",
        "open_logs",
        "open_config",
        "open_mods",
        "open_dota",
        "open_dota_pak",
        "open_core_pak",
        "launch_dota_tools",
        "launch_dota",
        "create_debug_zip",
        "tick_all",
        "untick_all",
        "compile_folder",
        "wipe_language_paths",
        "extract_workshop_tools",
        "launch_steam",
        "kill_steam",
        "validate_dota",
    ):
        assert f'"{action}"' in app

    assert "if item.get(\"always\") or item.get(\"untickable\"):" in app
    assert "run_developer_action?:" in types

    for label in (
        "Compile output",
        "Compiled pak66",
        "Create debug ZIP",
        "Compile folder…",
        "Untick all mods",
        "Tick all mods",
        "Wipe language paths",
        "Extract Workshop Tools",
        "Launch Dota 2 Tools",
        "Validate Dota 2",
    ):
        assert label in settings
