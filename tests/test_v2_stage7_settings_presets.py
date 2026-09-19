from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "V2_STAGING" / "Minify"


def test_v2_mod_settings_restore_preset_workflow():
    service = (STAGE / "ui" / "services" / "config_service.py").read_text(encoding="utf-8")
    app = (STAGE / "ui" / "app.py").read_text(encoding="utf-8")
    types = (STAGE / "ui" / "web" / "src" / "global.d.ts").read_text(encoding="utf-8")
    settings = (
        STAGE / "ui" / "web" / "src" / "lib" / "components" / "Settings.svelte"
    ).read_text(encoding="utf-8")

    for token in (
        'raw_presets = cfg.get("presets", [])',
        'presets[mod_id] = clean_presets',
        "def apply_mod_preset(",
        "config.set_mod(mod_name, modconf)",
    ):
        assert token in service

    assert "def apply_mod_preset(" in app
    assert "apply_mod_preset?:" in types
    assert "presets?: Record<string" in types

    for token in (
        "let presets:",
        "selectedPresets",
        "async function applyPreset(",
        "Choose preset…",
        "Apply preset",
    ):
        assert token in settings


def test_v2_black_plum_is_consistent_theme_fallback():
    service = (STAGE / "ui" / "services" / "config_service.py").read_text(encoding="utf-8")
    assert service.count('config.get("theme", "black-plum")') >= 2
    assert service.count('os.path.join(themes_dir, "black-plum.css")') >= 2
