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
    assert "# v21.4: Black-Plum Reactor release visual system." in THEME
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
    assert "ACCENT_HOVER = (169, 98, 183, 255)" in THEME
    assert "UI_ACCENT = (133, 56, 148, 255)" in CHECKBOXES
    assert "UI_ACCENT_HOVER = (169, 98, 183, 255)" in CHECKBOXES
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
    for tag in ("header_left_gutter", "header_brand_column", "header_right_gutter"):
        assert f'tag="{tag}"' in MAIN
    for tag in ("metric_restore_column", "metric_collision_column"):
        assert f'tag="{tag}"' in MAIN


def test_release_console_has_dense_command_hierarchy():
    for tag in (
        "header_brand_group",
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
    assert 'dpg.configure_item("metric_restore_column", show=main_width >= 650)' in WINDOW
    assert 'dpg.configure_item("metric_collision_column", show=main_width >= 830)' in WINDOW
    assert 'dpg.configure_item("dashboard_hero_card", height=hero_height)' in WINDOW
    assert 'dpg.configure_item("dashboard_safety_text", wrap=max(180, side_width - 30))' in WINDOW


def test_release_console_keeps_actionable_navigation():
    for label in ("PATCH CORE", "MOD LIBRARY", "D2PFX NETWORK", "CONTROL PANEL", "RESTORE POINTS"):
        assert f'label="{label}"' in MAIN


def test_d2pfx_uses_json_link_and_highlight_roles():
    assert "(122, 193, 67, 255)" in D2PFX
    assert "color=(255, 255, 0)" in D2PFX
    assert "color=(0, 255, 255)" not in D2PFX


def test_source_screenshot_spatial_color_roles_are_materialized():
    assert "BACKGROUND = JSON_WINDOW_BG" in THEME
    assert "SURFACE = JSON_BASE_BG" in THEME
    assert "SURFACE_RAISED = JSON_BUTTON_BG" in THEME
    assert "dpg.add_theme_color(dpg.mvThemeCol_Button, SUCCESS)" in THEME
    assert "dpg.add_theme_color(dpg.mvThemeCol_Text, JSON_BASE_ALT)" in THEME
    assert "UI_PANEL = (88, 108, 114, 255)" in CHECKBOXES
    assert "UI_RAISED = (133, 56, 148, 255)" in CHECKBOXES
    assert "dpg.add_theme_color(dpg.mvThemeCol_Header, (122, 193, 67, 230))" in D2PFX
    assert "dpg.add_theme_color(dpg.mvThemeCol_Text, (0, 0, 0))" in D2PFX


def test_nav_status_card_has_safe_vertical_budget():
    start = MAIN.index('tag="nav_status_card"')
    card = MAIN[start : start + 320]
    assert "height=66" in card
    assert 'dpg.add_text("SYSTEM", parent="nav_status_card"' in card
    assert 'dpg.add_text("● PROTECTED", parent="nav_status_card"' in card
    assert "nav_status_height = 66 if shell_body_height >= 370 else 62" in WINDOW
    assert 'dpg.configure_item("nav_status_card", height=nav_status_height)' in WINDOW


def test_header_brand_is_centered_and_engine_chip_removed():
    assert 'tag="header_brand_group"' in MAIN
    assert 'tag="header_left_gutter"' in MAIN
    assert 'tag="header_right_gutter"' in MAIN
    assert MAIN.count("width_stretch=True, init_width_or_weight=1.0") >= 2
    assert 'tag="header_engine_chip"' not in MAIN
    assert 'tag="header_engine_column"' not in MAIN
    assert 'dpg.add_text("PATCH ENGINE"' not in MAIN


def test_viewport_has_safe_minimum_layout_budget():
    assert "MIN_VIEWPORT_WIDTH = 960" in MAIN
    assert "MIN_VIEWPORT_HEIGHT = 680" in MAIN
    assert "min_width=MIN_VIEWPORT_WIDTH" in MAIN
    assert "min_height=MIN_VIEWPORT_HEIGHT" in MAIN
    assert "shell_body_height = max(350, min(500, shared.window_height - 330))" in WINDOW
