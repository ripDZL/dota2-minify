from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEVTOOLS = (ROOT / "Minify" / "ui" / "dev_tools.py").read_text(encoding="utf-8")
WINDOW = (ROOT / "Minify" / "ui" / "window.py").read_text(encoding="utf-8")


def test_general_path_fields_are_content_fit_without_touching_mod_inputs():
    assert "INPUT_TEXT_MIN_WIDTH = 280" in DEVTOOLS
    assert "INPUT_TEXT_MAX_WIDTH = 720" in DEVTOOLS
    assert "INPUT_TEXT_PADDING = 44" in DEVTOOLS
    assert "def _input_display_text(item):" in DEVTOOLS
    assert '"mvInputText" in item_type and alias.startswith("opt_")' in DEVTOOLS
    assert "_input_display_text(item)" in DEVTOOLS


def test_activity_log_buttons_have_safe_height_and_vertical_centering():
    assert "ACTIVITY_BUTTON_HEIGHT = 30" in WINDOW
    assert WINDOW.count("height=ACTIVITY_BUTTON_HEIGHT") == 2
    assert "button_y = max(0, (36 - ACTIVITY_BUTTON_HEIGHT) // 2)" in WINDOW
    assert 'dpg.set_item_pos("activity_copy_button", (copy_x, button_y))' in WINDOW
    assert 'dpg.set_item_pos("activity_select_button", (select_x, button_y))' in WINDOW
