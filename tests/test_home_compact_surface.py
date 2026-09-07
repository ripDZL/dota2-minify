from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEVTOOLS = (ROOT / "Minify" / "ui" / "dev_tools.py").read_text(encoding="utf-8")


def test_home_hides_explanatory_hero_and_sequence():
    for tag in ("dashboard_hero_card", "dashboard_metric_strip"):
        assert f'dpg.configure_item(tag, show=False)' in DEVTOOLS
    assert 'for tag in ("dashboard_hero_card", "dashboard_metric_strip"):' in DEVTOOLS


def test_home_keeps_only_status_action_separator_visible():
    assert 'for tag in ("home_separator_after_intro", "home_separator_before_status"):' in DEVTOOLS
    assert 'dpg.configure_item(tag, show=False)' in DEVTOOLS
    assert 'dpg.configure_item("home_separator_before_actions", show=True)' in DEVTOOLS


def test_home_compacts_shell_after_resize_pass():
    for token in (
        "HOME_COMPACT_MIN_SHELL_HEIGHT = 250",
        "HOME_COMPACT_INNER_INSET = 34",
        "HOME_COMPACT_VERTICAL_GAP = 22",
        "HOME_STATUS_HEIGHT = 68",
        "HOME_ACTION_NORMAL_HEIGHT = 96",
        "inner_height = HOME_STATUS_HEIGHT + action_height + HOME_COMPACT_VERTICAL_GAP",
        "shell_height = max(HOME_COMPACT_MIN_SHELL_HEIGHT, inner_height + HOME_COMPACT_INNER_INSET)",
        'dpg.configure_item("app_nav_rail", height=shell_height)',
        'dpg.configure_item("app_workspace", height=shell_height)',
        'height=inner_height,\n            no_scrollbar=True',
        'getattr(dpg, "set_frame_callback", None)',
        'getattr(dpg, "get_frame_count", None)',
    ):
        assert token in DEVTOOLS
