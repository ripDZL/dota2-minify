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


def test_user_json_palette_is_materialized():
    assert "# v21.4: Plumfire Reactor release visual system." in THEME
    for token in (
        "JSON_ACCENT_DIVIDER = (223, 80, 59, 255)",
        "JSON_ACCENT_HIGHLIGHT = (122, 193, 67, 255)",
        "JSON_ACCENT_LINK = (255, 255, 0, 255)",
        "JSON_BASE_BG = (88, 108, 114, 255)",
        "JSON_BUTTON_BG = (133, 56, 148, 255)",
        "JSON_TEXT_BRIGHT = (255, 195, 15, 255)",
        "JSON_TEXT_DISABLED = (164, 143, 123, 255)",
        "JSON_TEXT_PLACEHOLDER = (217, 199, 176, 255)",
        "JSON_TEXT_PRIMARY = (247, 240, 231, 255)",
        "JSON_WINDOW_BG = (70, 51, 90, 255)",
    ):
        assert token in THEME
    assert "UI_ACCENT = (133, 56, 148, 255)" in CHECKBOXES
    assert "UI_SUCCESS = (122, 193, 67, 255)" in CHECKBOXES


def test_primary_action_uses_json_button_role():
    start = THEME.index('with dpg.theme(tag="main_primary_button_theme")')
    end = THEME.index('with dpg.theme(tag="main_secondary_button_theme")', start)
    primary = THEME[start:end]
    assert "dpg.add_theme_color(dpg.mvThemeCol_Button, ACCENT)" in primary
    assert "dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, ACCENT_HOVER)" in primary
    assert "dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, ACCENT_ACTIVE)" in primary


def test_release_console_uses_real_alignment_tables():
    for tag in ("header_layout", "dashboard_metric_table", "dashboard_flow_table", "dashboard_guard_table"):
        assert f'tag="{tag}"' in MAIN
    for tag in ("header_engine_column", "metric_restore_column", "metric_collision_column"):
        assert f'tag="{tag}"' in MAIN


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


def test_alignment_labels_do_not_depend_on_space_padding():
    for label in ("Shared files", "Restore point", "Selected graph", "AUTOMATIC", "ENFORCED", "CONFINED"):
        assert label in MAIN
    assert "Shared-file collision scan" not in MAIN
    assert "ROLLBACK        AUTOMATIC" not in MAIN


def test_responsive_shell_collapses_before_clipping():
    assert "wide_workspace = workspace_width >= 1080 and shared.window_height >= 720" in WINDOW
    assert "side_width = min(360, max(320, int(workspace_width * 0.25))) if wide_workspace else 0" in WINDOW
    assert "metric_visible = inner_height >= 350 and main_width >= 560" in WINDOW
    assert 'dpg.configure_item("header_engine_column", show=shared.window_width >= 760)' in WINDOW
    assert 'dpg.configure_item("metric_restore_column", show=main_width >= 650)' in WINDOW
    assert 'dpg.configure_item("metric_collision_column", show=main_width >= 830)' in WINDOW
    assert 'dpg.configure_item("dashboard_hero_card", height=hero_height)' in WINDOW
    assert 'dpg.configure_item("dashboard_safety_text", wrap=max(180, side_width - 30))' in WINDOW


def test_release_console_keeps_actionable_navigation():
    for label in ("PATCH CORE", "MOD LIBRARY", "D2PFX NETWORK", "CONTROL PANEL", "RESTORE POINTS"):
        assert f'label="{label}"' in MAIN


def test_d2pfx_uses_json_link_and_highlight_roles():
    assert "(70, 51, 90, 210)" in D2PFX
    assert "(133, 56, 148, 230)" in D2PFX
    assert "(122, 193, 67, 255)" in D2PFX
    assert "color=(255, 255, 0)" in D2PFX
    assert "color=(0, 255, 255)" not in D2PFX
