from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "V2_STAGING" / "Minify"


def test_v2_black_plum_theme_matches_rc7_visual_tokens():
    css = (STAGE / "themes" / "black-plum.css").read_text(encoding="utf-8")
    for token in (
        "--bg-primary: #46335a;",
        "--bg-secondary: #586c72;",
        "--header-bg: #000000;",
        "--accent-purple: #853894;",
        "--accent: #7ac143;",
        "--accent-divider: #df503b;",
        "--accent-gold: #ffc30f;",
        "--text-primary: #f7f0e7;",
        "--text-muted: #a48f7b;",
    ):
        assert token in css


def test_v2_black_plum_is_default_and_fallback_theme():
    settings = json.loads((STAGE / "bin" / "settings.json").read_text(encoding="utf-8"))
    theme = next(item for item in settings if item.get("key") == "theme")
    assert theme["default"] == "black-plum"

    service = (STAGE / "ui" / "services" / "config_service.py").read_text(encoding="utf-8")
    assert 'config.get("theme", "black-plum")' in service
    assert 'os.path.join(themes_dir, "black-plum.css")' in service

    app = (STAGE / "ui" / "web" / "src" / "App.svelte").read_text(encoding="utf-8")
    assert 'const initialTheme = "black-plum";' in app


def test_v2_window_restores_rc7_minimum_fit_invariant():
    source = (STAGE / "ui" / "app.py").read_text(encoding="utf-8")
    assert "initial_width < 960" in source
    assert "initial_height < 680" in source
    assert "min_size=(960, 680)" in source
    assert "w_int >= 960 and h_int >= 680" in source


def test_v2_header_keeps_essential_actions_at_compact_width():
    source = (
        STAGE / "ui" / "web" / "src" / "lib" / "components" / "Header.svelte"
    ).read_text(encoding="utf-8")
    assert "@media (max-width: 1050px)" in source
    assert ".header-links" in source
    assert "display: none;" in source
    assert 'class="restore-btn"' in source
    assert 'class="uninstall-btn"' in source
    assert 'class="patch-btn"' in source


def test_v2_settings_remain_scroll_owned_at_minimum_size():
    source = (
        STAGE / "ui" / "web" / "src" / "lib" / "components" / "Settings.svelte"
    ).read_text(encoding="utf-8")
    assert "overflow: hidden;" in source
    assert "overflow-y: auto;" in source
    assert "var(--workspace-bg" in source
