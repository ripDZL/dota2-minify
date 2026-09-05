from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise SystemExit(f"expected exactly one match in {path}: {old[:80]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


main = ROOT / "Minify" / "__main__.py"
text = main.read_text(encoding="utf-8")
start_marker = '        with dpg.table(parent="app_shell_header", tag="header_layout", header_row=False, width=-1):\n'
end_marker = '\n\n        dpg.add_child_window(\n            tag="header_accent_rail",'
start = text.index(start_marker)
end = text.index(end_marker, start)
new_header = '''        with dpg.table(
            parent="app_shell_header",
            tag="header_layout",
            header_row=False,
            width=-1,
            policy=dpg.mvTable_SizingStretchProp,
        ):
            dpg.add_table_column(tag="header_left_gutter", width_stretch=True, init_width_or_weight=1.0)
            dpg.add_table_column(tag="header_brand_column", width_fixed=True, init_width_or_weight=340)
            dpg.add_table_column(tag="header_right_gutter", width_stretch=True, init_width_or_weight=1.0)
            with dpg.table_row():
                dpg.add_spacer(width=1)
                with dpg.group(tag="header_brand_group", horizontal=True, horizontal_spacing=10):
                    dpg.add_text("MINIFY", tag="app_title")
                    dpg.bind_item_font("app_title", "large_font")
                    with dpg.group():
                        dpg.add_text("DOTA 2 MOD ORCHESTRATION", tag="app_product_name")
                        dpg.add_text(f"RELEASE ENGINE  //  v{base.VERSION}", tag="app_version")
                dpg.add_spacer(width=1)'''
text = text[:start] + new_header + text[end:]
main.write_text(text, encoding="utf-8")

replace_once(
    main,
    'viewport_width = max(760, base.main_window_width, config.get("window_width", base.main_window_width))\nviewport_height = max(580, base.main_window_height, config.get("window_height", base.main_window_height))',
    'MIN_VIEWPORT_WIDTH = 960\nMIN_VIEWPORT_HEIGHT = 680\n\nviewport_width = max(MIN_VIEWPORT_WIDTH, base.main_window_width, config.get("window_width", base.main_window_width))\nviewport_height = max(MIN_VIEWPORT_HEIGHT, base.main_window_height, config.get("window_height", base.main_window_height))',
)
replace_once(main, '    min_width=max(760, base.main_window_width),', '    min_width=MIN_VIEWPORT_WIDTH,')
replace_once(main, '    min_height=max(580, base.main_window_height),', '    min_height=MIN_VIEWPORT_HEIGHT,')

window = ROOT / "Minify" / "ui" / "window.py"
replace_once(
    window,
    '    shell_body_height = max(350, min(500, int(shared.window_height * 0.47)))',
    '    # Reserve enough vertical space for the activity stream, terminal, and footer.\n    # The viewport minimum guarantees this body never has to clip navigation controls.\n    shell_body_height = max(350, min(500, shared.window_height - 330))',
)
replace_once(
    window,
    '    if dpg.does_item_exist("header_engine_column"):\n        dpg.configure_item("header_engine_column", show=shared.window_width >= 760)\n',
    '',
)

theme = ROOT / "Minify" / "ui" / "theme.py"
theme_text = theme.read_text(encoding="utf-8")
block_start = theme_text.index('    with dpg.theme(tag="header_engine_chip_theme"):\n')
block_end = theme_text.index('    with dpg.theme(tag="header_accent_rail_theme"):\n', block_start)
theme_text = theme_text[:block_start] + theme_text[block_end:]
theme_text = theme_text.replace('        ("header_engine_chip", "header_engine_chip_theme"),\n', '')
theme_text = theme_text.replace('        "header_engine_label",\n', '')
theme_text = theme_text.replace(
    '    for tag in ("header_engine_state", "activity_stream_state", "signal_validation", "signal_paths"):\n',
    '    for tag in ("activity_stream_state", "signal_validation", "signal_paths"):\n',
)
theme.write_text(theme_text, encoding="utf-8")

tests = ROOT / "tests" / "test_modern_ui.py"
test_text = tests.read_text(encoding="utf-8")
test_text = test_text.replace(
    '    for tag in ("header_engine_column", "metric_restore_column", "metric_collision_column"):\n        assert f\'tag="{tag}"\' in MAIN\n',
    '    for tag in ("header_left_gutter", "header_brand_column", "header_right_gutter"):\n        assert f\'tag="{tag}"\' in MAIN\n    for tag in ("metric_restore_column", "metric_collision_column"):\n        assert f\'tag="{tag}"\' in MAIN\n',
)
test_text = test_text.replace(
    '        "header_engine_chip",\n',
    '        "header_brand_group",\n',
)
test_text = test_text.replace(
    '    assert \'dpg.configure_item("header_engine_column", show=shared.window_width >= 760)\' in WINDOW\n',
    '',
)
append = '''\n\ndef test_header_brand_is_centered_and_engine_chip_removed():\n    assert 'tag="header_brand_group"' in MAIN\n    assert 'tag="header_left_gutter"' in MAIN\n    assert 'tag="header_right_gutter"' in MAIN\n    assert MAIN.count("width_stretch=True, init_width_or_weight=1.0") >= 2\n    assert 'tag="header_engine_chip"' not in MAIN\n    assert 'tag="header_engine_column"' not in MAIN\n    assert 'dpg.add_text("PATCH ENGINE"' not in MAIN\n\n\ndef test_viewport_has_safe_minimum_layout_budget():\n    assert "MIN_VIEWPORT_WIDTH = 960" in MAIN\n    assert "MIN_VIEWPORT_HEIGHT = 680" in MAIN\n    assert "min_width=MIN_VIEWPORT_WIDTH" in MAIN\n    assert "min_height=MIN_VIEWPORT_HEIGHT" in MAIN\n    assert "shell_body_height = max(350, min(500, shared.window_height - 330))" in WINDOW\n'''
if 'def test_header_brand_is_centered_and_engine_chip_removed()' not in test_text:
    test_text = test_text.rstrip() + append + "\n"
tests.write_text(test_text, encoding="utf-8")
