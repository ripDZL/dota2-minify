from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEVTOOLS = (ROOT / "Minify" / "ui" / "dev_tools.py").read_text(encoding="utf-8")


def test_control_panel_actions_use_content_fit_widths():
    assert "TOOL_BUTTON_MIN_WIDTH = 150" in DEVTOOLS
    assert "TOOL_BUTTON_MAX_WIDTH = 360" in DEVTOOLS
    assert "COMBO_MIN_WIDTH = 220" in DEVTOOLS
    assert "COMBO_MAX_WIDTH = 520" in DEVTOOLS
    assert "def _text_width(label):" in DEVTOOLS
    assert "dpg.get_text_size(label)" in DEVTOOLS
    assert "def _fit_control_width(label, min_width, max_width, padding):" in DEVTOOLS
    assert "def _section_header(parent, label, default_open=False):" in DEVTOOLS

    tool_button_start = DEVTOOLS.index("def _tool_button")
    tool_button_end = DEVTOOLS.index("def _section_header", tool_button_start)
    tool_button = DEVTOOLS[tool_button_start:tool_button_end]
    assert "width=-1" not in tool_button
    assert "width = _fit_control_width(" in tool_button

    section_start = DEVTOOLS.index("def _section_header")
    section_end = DEVTOOLS.index("def _walk_descendants", section_start)
    section = DEVTOOLS[section_start:section_end]
    assert "width=" not in section


def test_general_settings_combos_and_buttons_reapply_fit_after_rebuild():
    assert "def _fit_general_control_panel_controls():" in DEVTOOLS
    fit_start = DEVTOOLS.index("def _fit_general_control_panel_controls")
    fit_end = DEVTOOLS.index("def _ensure_home_uniform_surface", fit_start)
    fit = DEVTOOLS[fit_start:fit_end]
    assert '"mvCollapsingHeader"' not in fit
    assert '"mvCombo" in item_type' in fit
    assert '"mvButton" in item_type' in fit
    assert "_combo_display_text(item)" in fit

    install_start = DEVTOOLS.index("def install_control_panel_tab")
    install_end = DEVTOOLS.index("def toggle", install_start)
    install = DEVTOOLS[install_start:install_end]
    assert 'if not dpg.does_item_exist("settings_tabs"):' in install
    assert "_fit_general_control_panel_controls()" in install


def test_home_dashboard_uses_one_uniform_surface():
    for tag in (
        '"app_workspace_main"',
        '"dashboard_hero_card"',
        '"dashboard_metric_strip"',
        '"dashboard_status_panel"',
        '"dashboard_action_bar"',
    ):
        assert tag in DEVTOOLS
    assert "def _ensure_home_uniform_surface():" in DEVTOOLS
    assert 'tag="home_uniform_surface_theme"' in DEVTOOLS
    assert 'dpg.add_theme_color(dpg.mvThemeCol_ChildBg, theme.SURFACE)' in DEVTOOLS
    assert 'dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 0)' in DEVTOOLS
    assert 'dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 0)' in DEVTOOLS
    assert 'tag="home_uniform_table_theme"' in DEVTOOLS
    assert 'dpg.add_theme_color(dpg.mvThemeCol_TableRowBg, theme.SURFACE)' in DEVTOOLS
    assert 'dpg.add_theme_color(dpg.mvThemeCol_TableRowBgAlt, theme.SURFACE)' in DEVTOOLS
    assert 'dpg.configure_item(tag, border=False)' in DEVTOOLS
    assert 'dpg.bind_item_theme("dashboard_metric_table", "home_uniform_table_theme")' in DEVTOOLS
    assert "_ensure_home_uniform_surface()" in DEVTOOLS
