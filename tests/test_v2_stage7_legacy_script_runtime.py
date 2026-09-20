from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "V2_STAGING"


def test_v2_keeps_rc7_dearpygui_runtime_for_dynamic_mod_scripts():
    pyproject = (STAGE / "pyproject.toml").read_text(encoding="utf-8")
    lock = (STAGE / "uv.lock").read_text(encoding="utf-8")
    spec = (STAGE / "scripts" / "Minify.spec").read_text(encoding="utf-8")

    assert '"dearpygui>=2.1.1"' in pyproject
    assert 'name = "dearpygui"' in lock
    assert 'legacy_script_hiddenimports = ["dearpygui.dearpygui"]' in spec
    assert 'collect_submodules("dearpygui")' in spec
    assert '"DearPyGui native extension was not bundled"' in spec


def test_v2_initial_script_failure_does_not_crash_application_startup():
    helper = (STAGE / "Minify" / "helper.py").read_text(encoding="utf-8")
    start = helper.index("def bulk_exec_script")
    end = helper.index("def exec_script_function", start)
    body = helper[start:end]

    assert "except Exception:" in body
    assert 'if order_name != "initial":' in body
    assert "raise" in body
    assert "Startup lifecycle script failed for {mod_name}; continuing Minify startup." in body


def test_v2_skips_rc7_dearpygui_details_hook_when_manifest_settings_exist():
    helper = (STAGE / "Minify" / "helper.py").read_text(encoding="utf-8")

    for token in (
        "def _is_legacy_dearpygui_details_hook(script_path, cfg):",
        'isinstance(cfg.get("settings"), list)',
        '"dearpygui" in folded',
        '"from ui import details" in folded',
        'order_name == "initial" and _is_legacy_dearpygui_details_hook(script_path, cfg)',
        "v2 uses the mod manifest settings instead.",
    ):
        assert token in helper
