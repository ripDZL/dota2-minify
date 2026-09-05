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


def test_crimson_slate_palette_is_materialized():
    assert "# v21.4: Crimson Slate release visual system." in THEME
    assert "BACKGROUND = (18, 18, 24, 255)" in THEME
    assert "SURFACE = (28, 28, 37, 255)" in THEME
    assert "ACCENT = (190, 39, 77, 255)" in THEME
    assert "EMBER = (207, 43, 79, 255)" in THEME
    assert "UI_ACCENT = (190, 39, 77, 255)" in CHECKBOXES


def test_release_dashboard_keeps_layered_cards():
    for tag in (
        "dashboard_hero_card",
        "dashboard_action_bar",
        "dashboard_flow_card",
        "dashboard_safety_card",
    ):
        assert f'tag="{tag}"' in MAIN
        assert f'("{tag}",' in THEME


def test_crimson_slate_uses_compact_geometry():
    assert "dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 2)" in THEME
    assert "dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 3)" in THEME
    assert "dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 2)" in CHECKBOXES


def test_d2pfx_selected_state_matches_release_accent():
    assert "(184, 43, 79, 255)" in D2PFX
    assert "color=(224, 54, 94)" in D2PFX
    assert "color=(0, 255, 255)" not in D2PFX
