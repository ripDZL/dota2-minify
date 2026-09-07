from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEVTOOLS = (ROOT / "Minify" / "ui" / "dev_tools.py").read_text(encoding="utf-8")


def test_compact_home_surviving_copy_is_centered():
    for token in (
        "HOME_CENTER_SIDE_PADDING = 20",
        "HOME_STATUS_TEXT_GAP = 8",
        'tag="home_status_line"',
        'tag="home_status_line_spacer"',
        'tag="home_metric_line"',
        'tag="home_metric_line_spacer"',
        'tag="home_action_label_line"',
        'tag="home_action_label_spacer"',
        'dpg.move_item(tag, parent="home_status_line")',
        'dpg.move_item("dashboard_metric", parent="home_metric_line")',
        'dpg.move_item("dashboard_action_label", parent="home_action_label_line")',
        "def _center_compact_home_text():",
        '"dashboard_status_panel",\n        "home_status_line_spacer"',
        '"dashboard_status_panel",\n        "home_metric_line_spacer"',
        '"dashboard_action_bar",\n        "home_action_label_spacer"',
        "_center_compact_home_text()",
    ):
        assert token in DEVTOOLS


def test_home_centering_uses_live_text_widths_and_parent_width():
    for token in (
        "parent_width = _item_width(parent, 0)",
        "text_width = sum(_text_width(_item_value(tag)) for tag in visible_tags)",
        "available_width = max(0, parent_width - HOME_CENTER_SIDE_PADDING)",
        "spacer_width = max(0, (available_width - text_width) // 2)",
        "dpg.configure_item(spacer, width=spacer_width)",
    ):
        assert token in DEVTOOLS


def test_home_deployment_buttons_are_centered_as_cluster():
    # The action pair stays centered as one responsive cluster, including narrow stacked layouts.
    for token in (
        'tag="home_action_buttons_row"',
        'tag="home_action_buttons_spacer"',
        'dpg.move_item("dashboard_action_buttons", parent="home_action_buttons_row")',
        "def _center_home_action_buttons():",
        'parent_width = _item_width("dashboard_action_bar", 0)',
        'patch_width = _item_width("button_patch", _configured_width("button_patch", 210))',
        'refresh_width = _item_width("button_refresh_main", _configured_width("button_refresh_main", 146))',
        "cluster_width = (",
        'dpg.configure_item("home_action_buttons_spacer", width=spacer_width)',
        "_center_home_action_buttons()",
    ):
        assert token in DEVTOOLS
