from pathlib import Path


WINDOW = Path("Minify/ui/window.py")
D2PFX = Path("Minify/browsers/d2pfx/ui.py")
CHECKBOXES = Path("Minify/ui/checkboxes.py")
TESTS = Path("tests/test_modern_ui.py")


def replace_once(text: str, old: str, new: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected exactly one replacement target, found {count}: {old[:120]!r}")
    return text.replace(old, new, 1)


window = WINDOW.read_text(encoding="utf-8")
window = replace_once(
    window,
    '''    nav_width = max(176, min(220, int(shared.window_width * 0.13)))
    # Reserve enough vertical space for the activity stream, terminal, and footer.
    # The viewport minimum guarantees this body never has to clip navigation controls.
    shell_body_height = max(350, min(500, shared.window_height - 330))
    nav_status_height = 66 if shell_body_height >= 370 else 62
    workspace_width = max(430, shared.window_width - nav_width - 34)
    wide_workspace = workspace_width >= 1080 and shared.window_height >= 720
    side_width = min(360, max(320, int(workspace_width * 0.25))) if wide_workspace else 0
    main_width = max(360, workspace_width - side_width - (18 if wide_workspace else 0) - 30)
    inner_height = max(300, shell_body_height - 34)
    metric_visible = inner_height >= 350 and main_width >= 560
''',
    '''    compact_width = shared.window_width <= 1000
    nav_min_width = 160 if compact_width else 176
    nav_width = max(nav_min_width, min(220, int(shared.window_width * 0.13)))
    # Reserve enough vertical space for the activity stream, terminal, and footer.
    # The viewport minimum guarantees this body never has to clip navigation controls.
    shell_body_height = max(350, min(500, shared.window_height - 330))
    nav_status_height = 66 if shell_body_height >= 370 else 62
    workspace_width = max(430, shared.window_width - nav_width - 34)
    wide_workspace = workspace_width >= 1080 and shared.window_height >= 720
    side_width = min(360, max(320, int(workspace_width * 0.25))) if wide_workspace else 0
    main_width = max(360, workspace_width - side_width - (18 if wide_workspace else 0) - 30)
    inner_height = max(300, shell_body_height - 34)
    metric_visible = inner_height >= 350 and main_width >= 520
    metric_restore_visible = metric_visible and main_width >= 760
    metric_collision_visible = metric_visible and main_width >= 940
''',
)
window = replace_once(
    window,
    '''    if dpg.does_item_exist("metric_restore_column"):
        dpg.configure_item("metric_restore_column", show=main_width >= 650)
    if dpg.does_item_exist("metric_collision_column"):
        dpg.configure_item("metric_collision_column", show=main_width >= 830)
''',
    '''    if dpg.does_item_exist("metric_restore_column"):
        dpg.configure_item("metric_restore_column", show=metric_restore_visible)
    if dpg.does_item_exist("metric_restore_state"):
        dpg.configure_item("metric_restore_state", show=metric_restore_visible)
    if dpg.does_item_exist("metric_collision_column"):
        dpg.configure_item("metric_collision_column", show=metric_collision_visible)
    if dpg.does_item_exist("metric_collision_state"):
        dpg.configure_item("metric_collision_state", show=metric_collision_visible)
''',
)
window = replace_once(
    window,
    '''    if dpg.does_item_exist("dashboard_action_bar"):
        dpg.configure_item("dashboard_action_bar", height=action_height)
''',
    '''    if dpg.does_item_exist("dashboard_action_bar"):
        dpg.configure_item("dashboard_action_bar", height=action_height)
    if dpg.does_item_exist("button_patch"):
        dpg.configure_item("button_patch", width=176 if compact_width else 210)
    if dpg.does_item_exist("button_refresh_main"):
        dpg.configure_item("button_refresh_main", width=128 if compact_width else 146)
''',
)
window = replace_once(
    window,
    '''    if dpg.does_item_exist("activity_caption"):
        dpg.configure_item("activity_caption", show=shared.window_width >= 900)
    if dpg.does_item_exist("activity_stream_state"):
        dpg.configure_item("activity_stream_state", show=shared.window_width >= 620)
    if dpg.does_item_exist("settings_scroll"):
        dpg.configure_item("settings_scroll", width=shared.window_width, height=max(220, shared.window_height - 78))
    if dpg.does_item_exist("settings_actions_bar"):
        dpg.configure_item("settings_actions_bar", width=shared.window_width, height=56)
''',
    '''    if dpg.does_item_exist("activity_caption"):
        dpg.configure_item("activity_caption", show=shared.window_width >= 1040)
    if dpg.does_item_exist("activity_stream_state"):
        dpg.configure_item("activity_stream_state", show=shared.window_width >= 700)
    settings_width = max(320, shared.window_width - 16)
    if dpg.does_item_exist("settings_scroll"):
        dpg.configure_item("settings_scroll", width=settings_width, height=max(220, shared.window_height - 78))
    if dpg.does_item_exist("settings_actions_bar"):
        dpg.configure_item("settings_actions_bar", width=settings_width, height=56)
    if dpg.does_item_exist("settings_intro"):
        dpg.configure_item("settings_intro", wrap=max(260, settings_width - 24))
''',
)
WINDOW.write_text(window, encoding="utf-8")


d2pfx = D2PFX.read_text(encoding="utf-8")
d2pfx = replace_once(d2pfx, 'with dpg.child_window(width=180, tag="d2pfx_sidebar"):', 'with dpg.child_window(width=168, tag="d2pfx_sidebar"):')
d2pfx = replace_once(
    d2pfx,
    'dpg.add_table_column(width_fixed=True, init_width_or_weight=350)',
    'dpg.add_table_column(width_fixed=True, init_width_or_weight=320)',
)
d2pfx = replace_once(d2pfx, 'desc_text = dpg.add_text("", tag="d2pfx_cat_desc", wrap=0)', 'desc_text = dpg.add_text("", tag="d2pfx_cat_desc", wrap=360)')
d2pfx = replace_once(
    d2pfx,
    '''                                    dpg.add_text(
                                        "Installable packs, resources, and community tools",
                                        tag="d2pfx_browser_subtitle",
                                    )
''',
    '''                                    dpg.add_text(
                                        "Installable packs, resources, and community tools",
                                        tag="d2pfx_browser_subtitle",
                                        wrap=300,
                                    )
''',
)
d2pfx = replace_once(
    d2pfx,
    '''        content_width = shared.window_width - 150  # sidebar
        new_cols = max(2, int(content_width / 200))  # Adjust divisor for card width

        if self.current_cols != new_cols:
''',
    '''        content_width = max(420, shared.window_width - 210)
        new_cols = max(2, min(4, int(content_width / 240)))
        category_wrap = max(220, shared.window_width - 168 - 320 - 80)

        if dpg.does_item_exist("d2pfx_cat_desc"):
            dpg.configure_item("d2pfx_cat_desc", wrap=category_wrap)
        if dpg.does_item_exist("d2pfx_browser_subtitle"):
            dpg.configure_item("d2pfx_browser_subtitle", wrap=300)

        if self.current_cols != new_cols:
''',
)
D2PFX.write_text(d2pfx, encoding="utf-8")


checkboxes = CHECKBOXES.read_text(encoding="utf-8")
checkboxes = replace_once(
    checkboxes,
    '    dpg.add_text(_meta_text(mod), parent=row_tag, tag=meta_tag, indent=28)\n',
    '    dpg.add_text(_meta_text(mod), parent=row_tag, tag=meta_tag, indent=28, wrap=max(220, _list_width() - 64))\n',
)
checkboxes = replace_once(
    checkboxes,
    '''    indent = _row_action_indent(width)
    for mod in checkboxes:
        tag = f"{mod}_favorite_button"
        if dpg.does_item_exist(tag):
            dpg.configure_item(tag, indent=indent)
''',
    '''    indent = _row_action_indent(width)
    meta_wrap = max(220, list_width - 64)
    for mod in checkboxes:
        tag = f"{mod}_favorite_button"
        if dpg.does_item_exist(tag):
            dpg.configure_item(tag, indent=indent)
        meta_tag = f"{mod}_meta"
        if dpg.does_item_exist(meta_tag):
            dpg.configure_item(meta_tag, wrap=meta_wrap)
''',
)
CHECKBOXES.write_text(checkboxes, encoding="utf-8")


tests = TESTS.read_text(encoding="utf-8")
tests = replace_once(
    tests,
    '''    assert "metric_visible = inner_height >= 350 and main_width >= 560" in WINDOW
    assert 'dpg.configure_item("metric_restore_column", show=main_width >= 650)' in WINDOW
    assert 'dpg.configure_item("metric_collision_column", show=main_width >= 830)' in WINDOW
''',
    '''    assert "metric_visible = inner_height >= 350 and main_width >= 520" in WINDOW
    assert "metric_restore_visible = metric_visible and main_width >= 760" in WINDOW
    assert "metric_collision_visible = metric_visible and main_width >= 940" in WINDOW
    assert 'dpg.configure_item("metric_restore_column", show=metric_restore_visible)' in WINDOW
    assert 'dpg.configure_item("metric_collision_column", show=metric_collision_visible)' in WINDOW
''',
)
if "def test_minimum_width_fit_contract_covers_primary_library_and_d2pfx" not in tests:
    tests += '''\n\ndef test_minimum_width_fit_contract_covers_primary_library_and_d2pfx():
    assert "compact_width = shared.window_width <= 1000" in WINDOW
    assert "nav_min_width = 160 if compact_width else 176" in WINDOW
    assert 'dpg.configure_item("button_patch", width=176 if compact_width else 210)' in WINDOW
    assert 'dpg.configure_item("button_refresh_main", width=128 if compact_width else 146)' in WINDOW
    assert 'dpg.configure_item("activity_caption", show=shared.window_width >= 1040)' in WINDOW
    assert "settings_width = max(320, shared.window_width - 16)" in WINDOW
    assert 'with dpg.child_window(width=168, tag="d2pfx_sidebar"):' in D2PFX
    assert "init_width_or_weight=320" in D2PFX
    assert 'tag="d2pfx_cat_desc", wrap=360' in D2PFX
    assert "new_cols = max(2, min(4, int(content_width / 240)))" in D2PFX
    assert "wrap=max(220, _list_width() - 64)" in CHECKBOXES
'''
TESTS.write_text(tests, encoding="utf-8")

print("Minimum-width fit patch applied")
