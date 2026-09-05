from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN = (ROOT / "Minify" / "__main__.py").read_text(encoding="utf-8")
THEME = (ROOT / "Minify" / "ui" / "theme.py").read_text(encoding="utf-8")
CHECKBOXES = (ROOT / "Minify" / "ui" / "checkboxes.py").read_text(encoding="utf-8")
D2PFX = (ROOT / "Minify" / "browsers" / "d2pfx" / "ui.py").read_text(encoding="utf-8")


def test_stale_workspace_badge_removed():
    assert "LOCAL MOD WORKSPACE" not in MAIN
    assert 'tag="header_context"' not in MAIN
    assert 'tag="header_badge"' not in MAIN


def test_obsidian_arc_release_palette_is_materialized():
    assert "# v21.4: Obsidian Arc release visual system." in THEME
    assert "ACCENT = (84, 151, 255, 255)" in THEME
    assert "EMBER = (240, 103, 70, 255)" in THEME
    assert "BEVEL_DARK = (1, 2, 5, 220)" in THEME
    assert "UI_EMBER = (240, 103, 70, 255)" in CHECKBOXES


def test_release_dashboard_uses_layered_cards():
    for tag in (
        "dashboard_hero_card",
        "dashboard_action_bar",
        "dashboard_flow_card",
        "dashboard_safety_card",
    ):
        assert f'tag="{tag}"' in MAIN
        assert f'("{tag}",' in THEME


def test_release_ui_uses_dual_accent_hierarchy():
    assert "dpg.add_theme_color(dpg.mvThemeCol_Button, EMBER)" in THEME
    assert "dpg.add_theme_color(dpg.mvThemeCol_Button, ACCENT_MUTED)" in THEME
    assert 'tag="dashboard_safety_title_theme"' in THEME


def test_d2pfx_uses_release_teal_instead_of_legacy_cyan():
    assert "color=(78, 208, 196)" in D2PFX
    assert "color=(0, 255, 255)" not in D2PFX
