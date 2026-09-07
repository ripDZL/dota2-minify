from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEVTOOLS = (ROOT / "Minify" / "ui" / "dev_tools.py").read_text(encoding="utf-8")


def test_control_panel_actions_use_content_fit_widths():
    assert "TOOL_BUTTON_MIN_WIDTH = 150" in DEVTOOLS
    assert "TOOL_BUTTON_MAX_WIDTH = 360" in DEVTOOLS
    assert "SECTION_HEADER_MIN_WIDTH = 150" in DEVTOOLS
    assert "SECTION_HEADER_MAX_WIDTH = 360" in DEVTOOLS
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


def test_general_settings_headers_combos_and_buttons_reapply_fit_after_rebuild():
    assert "def _fit_general_control_panel_controls():" in DEVTOOLS
    assert '"mvCollapsingHeader" in item_type' in DEVTOOLS
    assert '"mvCombo" in item_type' in DEVTOOLS
    assert '"mvButton" in item_type' in DEVTOOLS
    assert "_combo_display_text(item)" in DEVTOOLS

    install_start = DEVTOOLS.index("def install_control_panel_tab")
    install_end = DEVTOOLS.index("def toggle", install_start)
    install = DEVTOOLS[install_start:install_end]
    assert 'if not dpg.does_item_exist("settings_tabs"):' in install
    assert "_fit_general_control_panel_controls()" in install
