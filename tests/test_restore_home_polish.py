from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEVTOOLS = (ROOT / "Minify" / "ui" / "dev_tools.py").read_text(encoding="utf-8")


def test_restore_button_has_safe_windows_fit():
    assert "RESTORE_BUTTON_WIDTH = 180" in DEVTOOLS
    assert "RESTORE_BUTTON_HEIGHT = 30" in DEVTOOLS
    assert 'dpg.does_item_exist("backup_restore_button")' in DEVTOOLS
    assert '"backup_restore_button",\n            width=RESTORE_BUTTON_WIDTH,\n            height=RESTORE_BUTTON_HEIGHT' in DEVTOOLS


def test_home_uses_subtle_separators_without_nested_cards():
    for tag in (
        "home_separator_after_intro",
        "home_separator_before_status",
        "home_separator_before_actions",
    ):
        assert tag in DEVTOOLS
    assert 'tag="home_subtle_separator_theme"' in DEVTOOLS
    assert "dpg.mvThemeCol_Separator, theme.BORDER_SOFT" in DEVTOOLS
    assert "dpg.add_separator(parent=parent, tag=separator_tag)" in DEVTOOLS
    assert "dpg.move_item(separator_tag, parent=parent, before=before)" in DEVTOOLS
