from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN = (ROOT / "Minify" / "__main__.py").read_text(encoding="utf-8")
THEME = (ROOT / "Minify" / "ui" / "theme.py").read_text(encoding="utf-8")
CHECKBOXES = (ROOT / "Minify" / "ui" / "checkboxes.py").read_text(encoding="utf-8")
D2PFX = (ROOT / "Minify" / "browsers" / "d2pfx" / "ui.py").read_text(encoding="utf-8")
WINDOW = (ROOT / "Minify" / "ui" / "window.py").read_text(encoding="utf-8")


def test_stale_workspace_badge_removed():
    assert "LOCAL MOD WORKSPACE" not in MAIN
    assert 'tag="header_context"' not in MAIN
    assert 'tag="header_badge"' not in MAIN


def test_prismatic_foundry_palette_is_materialized():
    assert "# v21.4: Prismatic Foundry release visual system." in THEME
    assert "BACKGROUND = (6, 8, 16, 255)" in THEME
    assert "ACCENT = (121, 92, 255, 255)" in THEME
    assert "CYAN = (48, 218, 255, 255)" in THEME
    assert "MAGENTA = (239, 68, 168, 255)" in THEME
    assert "EMBER = (255, 112, 70, 255)" in THEME
    assert "UI_ACCENT = (121, 92, 255, 255)" in CHECKBOXES


def test_release_console_has_dense_command_hierarchy():
    for tag in (
        "header_engine_chip",
        "header_accent_rail",
        "nav_status_card",
        "dashboard_hero_card",
        "dashboard_metric_strip",
        "dashboard_status_panel",
        "dashboard_action_bar",
        "dashboard_flow_card",
        "dashboard_signal_card",
        "dashboard_safety_card",
    ):
        assert f'tag="{tag}"' in MAIN


def test_release_console_has_multichannel_status_language():
    for label in (
        "PATCH MATRIX  /  RELEASE CONSOLE",
        "RESTORE // ARMED",
        "COLLISION // INDEXED",
        "DEPLOYMENT SEQUENCE",
        "GUARD MATRIX",
        "LIVE ACTIVITY",
        "STREAM ONLINE",
    ):
        assert label in MAIN


def test_prismatic_theme_binds_new_surfaces():
    for pair in (
        '("header_engine_chip", "header_engine_chip_theme")',
        '("header_accent_rail", "header_accent_rail_theme")',
        '("nav_status_card", "nav_status_card_theme")',
        '("dashboard_metric_strip", "dashboard_metric_strip_theme")',
        '("dashboard_signal_card", "dashboard_signal_card_theme")',
    ):
        assert pair in THEME


def test_prismatic_ui_uses_modern_depth_geometry():
    assert "dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)" in THEME
    assert "dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 7)" in THEME
    assert "dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)" in CHECKBOXES
    assert "shell_body_height = max(340, min(454, int(shared.window_height * 0.43)))" in WINDOW


def test_d2pfx_uses_prismatic_network_cyan():
    assert "(48, 178, 211, 255)" in D2PFX
    assert "color=(48, 218, 255)" in D2PFX
    assert "color=(0, 255, 255)" not in D2PFX
