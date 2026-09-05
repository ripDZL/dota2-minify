from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN_PATH = ROOT / "Minify" / "__main__.py"
THEME_PATH = ROOT / "Minify" / "ui" / "theme.py"
WINDOW_PATH = ROOT / "Minify" / "ui" / "window.py"
CHECKS_PATH = ROOT / "Minify" / "ui" / "checkboxes.py"
D2PFX_PATH = ROOT / "Minify" / "browsers" / "d2pfx" / "ui.py"
TEST_PATH = ROOT / "tests" / "test_modern_ui.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"{label} anchor mismatch")
    return text.replace(old, new, 1)


main = MAIN_PATH.read_text(encoding="utf-8")
main = main.replace(
    "# v21.4 Prismatic Foundry command console. The shell is intentionally\n"
    "        # layered: brand rail -> command rail -> navigation/workspace -> live activity.",
    "# v21.4 responsive command console. Layout uses real columns and adaptive\n"
    "        # visibility so Windows font metrics cannot break alignment.",
    1,
)
main = main.replace('height=72,\n            autosize_x=True,', 'height=76,\n            autosize_x=True,', 1)

old_header = '''        with dpg.group(parent="app_shell_header", horizontal=True, horizontal_spacing=10):
            dpg.add_text("MINIFY", tag="app_title")
            dpg.bind_item_font("app_title", "large_font")
            with dpg.group():
                dpg.add_text("DOTA 2 MOD ORCHESTRATION", tag="app_product_name")
                dpg.add_text(f"RELEASE ENGINE  //  v{base.VERSION}", tag="app_version")
            dpg.add_spacer(width=16)
            dpg.add_child_window(
                tag="header_engine_chip",
                width=152,
                height=42,
                border=True,
                no_scrollbar=True,
                no_scroll_with_mouse=True,
            )
            dpg.add_text("PATCH ENGINE", parent="header_engine_chip", tag="header_engine_label")
            dpg.add_text("READY / GUARDED", parent="header_engine_chip", tag="header_engine_state")
'''
new_header = '''        with dpg.table(parent="app_shell_header", tag="header_layout", header_row=False, width=-1):
            dpg.add_table_column(tag="header_brand_column")
            dpg.add_table_column(tag="header_engine_column", width_fixed=True, init_width_or_weight=174)
            with dpg.table_row():
                with dpg.group(horizontal=True, horizontal_spacing=10):
                    dpg.add_text("MINIFY", tag="app_title")
                    dpg.bind_item_font("app_title", "large_font")
                    with dpg.group():
                        dpg.add_text("DOTA 2 MOD ORCHESTRATION", tag="app_product_name")
                        dpg.add_text(f"RELEASE ENGINE  //  v{base.VERSION}", tag="app_version")
                with dpg.child_window(
                    tag="header_engine_chip",
                    width=-1,
                    height=44,
                    border=True,
                    no_scrollbar=True,
                    no_scroll_with_mouse=True,
                ):
                    dpg.add_text("PATCH ENGINE", tag="header_engine_label")
                    dpg.add_text("READY / GUARDED", tag="header_engine_state")
'''
main = replace_once(main, old_header, new_header, "header layout")

main = main.replace('tag="app_nav_rail",\n            width=188,\n            height=350,', 'tag="app_nav_rail",\n            width=188,\n            height=380,', 1)
main = main.replace('tag="app_workspace",\n            width=-1,\n            height=350,', 'tag="app_workspace",\n            width=-1,\n            height=380,', 1)
main = main.replace('tag="dashboard_hero_card",\n                height=142,', 'tag="dashboard_hero_card",\n                height=168,', 1)

old_metrics = '''            with dpg.group(parent="dashboard_metric_strip", horizontal=True, horizontal_spacing=11):
                dpg.add_text("0 selected • 0 installed", tag="dashboard_metric")
                dpg.add_text("RESTORE // ARMED", tag="metric_restore_state")
                dpg.add_text("COLLISION // INDEXED", tag="metric_collision_state")
'''
new_metrics = '''            with dpg.table(parent="dashboard_metric_strip", tag="dashboard_metric_table", header_row=False, width=-1):
                dpg.add_table_column(tag="metric_primary_column")
                dpg.add_table_column(tag="metric_restore_column")
                dpg.add_table_column(tag="metric_collision_column")
                with dpg.table_row():
                    dpg.add_text("0 selected • 0 installed", tag="dashboard_metric")
                    dpg.add_text("RESTORE // ARMED", tag="metric_restore_state")
                    dpg.add_text("COLLISION // INDEXED", tag="metric_collision_state")
'''
main = replace_once(main, old_metrics, new_metrics, "metric table")
main = main.replace('tag="dashboard_metric_strip",\n                height=39,', 'tag="dashboard_metric_strip",\n                height=42,', 1)
main = main.replace('tag="dashboard_status_panel",\n                height=58,', 'tag="dashboard_status_panel",\n                height=60,', 1)
main = main.replace('tag="dashboard_action_bar",\n                height=66,', 'tag="dashboard_action_bar",\n                height=76,', 1)
main = main.replace('tag="app_workspace_side",\n                width=286,', 'tag="app_workspace_side",\n                width=320,', 1)
main = main.replace('tag="dashboard_flow_card",\n                height=132,', 'tag="dashboard_flow_card",\n                height=136,', 1)

old_flow = '''            dpg.add_text("DEPLOYMENT SEQUENCE", parent="dashboard_flow_card", tag="dashboard_side_title")
            dpg.add_text(
                "01  ANALYZE      Shared-file collision scan", parent="dashboard_flow_card", tag="dashboard_step_1"
            )
            dpg.add_text(
                "02  SNAPSHOT     Managed-output restore point", parent="dashboard_flow_card", tag="dashboard_step_2"
            )
            dpg.add_text(
                "03  COMPOSE      Apply selected mod graph", parent="dashboard_flow_card", tag="dashboard_step_3"
            )
'''
new_flow = '''            dpg.add_text("DEPLOYMENT SEQUENCE", parent="dashboard_flow_card", tag="dashboard_side_title")
            with dpg.table(parent="dashboard_flow_card", tag="dashboard_flow_table", header_row=False, width=-1):
                dpg.add_table_column(width_fixed=True, init_width_or_weight=28)
                dpg.add_table_column(width_fixed=True, init_width_or_weight=72)
                dpg.add_table_column()
                with dpg.table_row():
                    dpg.add_text("01", tag="dashboard_step_1_index")
                    dpg.add_text("ANALYZE", tag="dashboard_step_1")
                    dpg.add_text("Shared files", tag="dashboard_step_1_detail")
                with dpg.table_row():
                    dpg.add_text("02", tag="dashboard_step_2_index")
                    dpg.add_text("SNAPSHOT", tag="dashboard_step_2")
                    dpg.add_text("Restore point", tag="dashboard_step_2_detail")
                with dpg.table_row():
                    dpg.add_text("03", tag="dashboard_step_3_index")
                    dpg.add_text("COMPOSE", tag="dashboard_step_3")
                    dpg.add_text("Selected graph", tag="dashboard_step_3_detail")
'''
main = replace_once(main, old_flow, new_flow, "deployment table")
main = main.replace('tag="dashboard_signal_card",\n                height=100,', 'tag="dashboard_signal_card",\n                height=110,', 1)

old_guard = '''            dpg.add_text("GUARD MATRIX", parent="dashboard_signal_card", tag="dashboard_signal_title")
            dpg.add_text("ROLLBACK        AUTOMATIC", parent="dashboard_signal_card", tag="signal_rollback")
            dpg.add_text("VALIDATION      ENFORCED", parent="dashboard_signal_card", tag="signal_validation")
            dpg.add_text("PATH SAFETY     CONFINED", parent="dashboard_signal_card", tag="signal_paths")
'''
new_guard = '''            dpg.add_text("GUARD MATRIX", parent="dashboard_signal_card", tag="dashboard_signal_title")
            with dpg.table(parent="dashboard_signal_card", tag="dashboard_guard_table", header_row=False, width=-1):
                dpg.add_table_column()
                dpg.add_table_column()
                with dpg.table_row():
                    dpg.add_text("ROLLBACK", tag="signal_rollback_label")
                    dpg.add_text("AUTOMATIC", tag="signal_rollback")
                with dpg.table_row():
                    dpg.add_text("VALIDATION", tag="signal_validation_label")
                    dpg.add_text("ENFORCED", tag="signal_validation")
                with dpg.table_row():
                    dpg.add_text("PATH SAFETY", tag="signal_paths_label")
                    dpg.add_text("CONFINED", tag="signal_paths")
'''
main = replace_once(main, old_guard, new_guard, "guard table")
MAIN_PATH.write_text(main, encoding="utf-8")


theme = THEME_PATH.read_text(encoding="utf-8")
palette_start = theme.index("# v21.4: Prismatic Foundry release visual system.")
palette_end = theme.index("\n\nsettings_theme = 0", palette_start)
new_palette = '''# v21.4: Plumfire Reactor release visual system.
# Exact role anchors from the user-supplied theme JSON. Derived dark shades only
# extend those tokens for depth; primary interaction/state colors stay faithful.
JSON_ACCENT_DIVIDER = (223, 80, 59, 255)  # #df503b
JSON_ACCENT_HIGHLIGHT = (122, 193, 67, 255)  # #7ac143
JSON_ACCENT_LINK = (255, 255, 0, 255)  # #ffff00
JSON_BASE_ALT = (0, 0, 0, 255)  # #000000
JSON_BASE_BG = (88, 108, 114, 255)  # #586c72
JSON_BUTTON_BG = (133, 56, 148, 255)  # #853894
JSON_TEXT_BRIGHT = (255, 195, 15, 255)  # #ffc30f
JSON_TEXT_DISABLED = (164, 143, 123, 255)  # #a48f7b
JSON_TEXT_PLACEHOLDER = (217, 199, 176, 255)  # #d9c7b0
JSON_TEXT_PRIMARY = (247, 240, 231, 255)  # #f7f0e7
JSON_WINDOW_BG = (70, 51, 90, 255)  # #46335a

BACKGROUND = (12, 9, 17, 255)
BACKGROUND_DEEP = JSON_BASE_ALT
SURFACE = (25, 19, 33, 255)
SURFACE_ALT = (37, 27, 48, 255)
SURFACE_RAISED = (50, 37, 64, 255)
SURFACE_RECESSED = (17, 13, 23, 255)
SURFACE_HOVER = JSON_WINDOW_BG
SURFACE_ACTIVE = (58, 44, 70, 255)
SURFACE_WARM = (45, 27, 31, 255)
BORDER = JSON_BASE_BG
BORDER_SOFT = (53, 61, 68, 255)
BEVEL_LIGHT = JSON_TEXT_DISABLED
BEVEL_DARK = (0, 0, 0, 220)
BEVEL_EMBER = JSON_ACCENT_DIVIDER
TEXT = JSON_TEXT_PRIMARY
MUTED = JSON_TEXT_PLACEHOLDER
MUTED_DARK = JSON_TEXT_DISABLED
ACCENT = JSON_BUTTON_BG
ACCENT_HOVER = (169, 83, 184, 255)
ACCENT_ACTIVE = (104, 39, 118, 255)
ACCENT_MUTED = JSON_WINDOW_BG
# Compatibility aliases keep existing theme wiring stable while changing roles.
CYAN = JSON_ACCENT_HIGHLIGHT
CYAN_MUTED = (49, 79, 33, 255)
MAGENTA = JSON_ACCENT_DIVIDER
MAGENTA_MUTED = (96, 38, 31, 255)
EMBER = JSON_ACCENT_DIVIDER
EMBER_HOVER = (244, 102, 82, 255)
EMBER_ACTIVE = (180, 57, 43, 255)
EMBER_MUTED = (96, 38, 31, 255)
HIGHLIGHT = JSON_TEXT_BRIGHT
LINK = JSON_ACCENT_LINK
D2PFX = JSON_ACCENT_HIGHLIGHT
VPK = JSON_TEXT_BRIGHT
DANGER = JSON_ACCENT_DIVIDER
DANGER_HOVER = (244, 102, 82, 255)
WARNING = JSON_TEXT_BRIGHT
SUCCESS = JSON_ACCENT_HIGHLIGHT'''
theme = theme[:palette_start] + new_palette + theme[palette_end:]
theme = theme.replace(
    "# Application shell: compact flat-dark chrome with crimson focus and inset controls.",
    "# Application shell: plum-black depth with violet controls, ember dividers, lime state, and gold telemetry.",
    1,
)
for old, new in (
    ("dpg.add_theme_color(dpg.mvThemeCol_Border, (76, 59, 163, 255))", "dpg.add_theme_color(dpg.mvThemeCol_Border, ACCENT)"),
    ("dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (10, 25, 31, 255))", "dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (20, 28, 18, 255))"),
    ("dpg.add_theme_color(dpg.mvThemeCol_Border, (31, 114, 126, 255))", "dpg.add_theme_color(dpg.mvThemeCol_Border, CYAN_MUTED)"),
    ("dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (16, 25, 42, 255))", "dpg.add_theme_color(dpg.mvThemeCol_ChildBg, SURFACE_ALT)"),
    ("dpg.add_theme_color(dpg.mvThemeCol_Border, (56, 77, 154, 255))", "dpg.add_theme_color(dpg.mvThemeCol_Border, ACCENT)"),
    ("dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (14, 18, 34, 255))", "dpg.add_theme_color(dpg.mvThemeCol_ChildBg, SURFACE_ALT)"),
    ("dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, (17, 74, 96, 190))", "dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, ACCENT_MUTED)"),
    ("dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (15, 20, 37, 255))", "dpg.add_theme_color(dpg.mvThemeCol_ChildBg, SURFACE_ALT)"),
    ("dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, (40, 31, 93, 180))", "dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, ACCENT_MUTED)"),
    ("dpg.add_theme_color(dpg.mvThemeCol_Border, (63, 50, 137, 255))", "dpg.add_theme_color(dpg.mvThemeCol_Border, ACCENT)"),
    ("dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, (30, 22, 74, 200))", "dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, ACCENT_MUTED)"),
    ("dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (11, 23, 34, 255))", "dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (20, 28, 18, 255))"),
    ("dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, (11, 64, 82, 190))", "dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, CYAN_MUTED)"),
):
    theme = theme.replace(old, new)

theme = theme.replace(
    "dpg.add_theme_color(dpg.mvThemeCol_Text, EMBER_HOVER)",
    "dpg.add_theme_color(dpg.mvThemeCol_Text, HIGHLIGHT)",
    1,
)
old_primary = '''            dpg.add_theme_color(dpg.mvThemeCol_Text, (25, 13, 10, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Button, EMBER)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, EMBER_HOVER)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, EMBER_ACTIVE)
'''
new_primary = '''            dpg.add_theme_color(dpg.mvThemeCol_Text, TEXT)
            dpg.add_theme_color(dpg.mvThemeCol_Button, ACCENT)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, ACCENT_HOVER)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, ACCENT_ACTIVE)
'''
theme = replace_once(theme, old_primary, new_primary, "primary button palette")

old_muted_tail = '''        "dashboard_action_label",
        "nav_status_title",
        "header_engine_label",
    ):
'''
new_muted_tail = '''        "dashboard_action_label",
        "nav_status_title",
        "header_engine_label",
        "dashboard_step_1_detail",
        "dashboard_step_2_detail",
        "dashboard_step_3_detail",
        "signal_rollback_label",
        "signal_validation_label",
        "signal_paths_label",
    ):
'''
theme = replace_once(theme, old_muted_tail, new_muted_tail, "muted tag bindings")
old_highlights = '''    for tag in ("dashboard_metric", "dashboard_side_title", "activity_label"):
'''
new_highlights = '''    for tag in (
        "dashboard_metric",
        "dashboard_side_title",
        "activity_label",
        "dashboard_step_1_index",
        "dashboard_step_2_index",
        "dashboard_step_3_index",
    ):
'''
theme = replace_once(theme, old_highlights, new_highlights, "highlight tag bindings")
THEME_PATH.write_text(theme, encoding="utf-8")


checks = CHECKS_PATH.read_text(encoding="utf-8")
old_checks_start = checks.index("UI_ACCENT = (121, 92, 255, 255)")
old_checks_end = checks.index("\n\nui_state = {", old_checks_start)
new_checks = '''UI_ACCENT = (133, 56, 148, 255)
UI_ACCENT_HOVER = (169, 83, 184, 255)
UI_EMBER = (223, 80, 59, 255)
UI_EMBER_HOVER = (244, 102, 82, 255)
UI_TEXT = (247, 240, 231, 255)
UI_MUTED = (217, 199, 176, 255)
UI_PANEL = (25, 19, 33, 255)
UI_PANEL_ALT = (37, 27, 48, 255)
UI_RAISED = (50, 37, 64, 255)
UI_RECESSED = (17, 13, 23, 255)
UI_PANEL_HOVER = (70, 51, 90, 255)
UI_BORDER = (88, 108, 114, 255)
UI_BEVEL_LIGHT = (164, 143, 123, 255)
UI_BEVEL_DARK = (0, 0, 0, 220)
UI_D2PFX = (255, 255, 0, 255)
UI_COLLECTION = (255, 195, 15, 255)
UI_VPK = (122, 193, 67, 255)
UI_WARNING = (255, 195, 15, 255)
UI_ERROR = (223, 80, 59, 255)
UI_SUCCESS = (122, 193, 67, 255)'''
checks = checks[:old_checks_start] + new_checks + checks[old_checks_end:]
CHECKS_PATH.write_text(checks, encoding="utf-8")


d2pfx = D2PFX_PATH.read_text(encoding="utf-8")
old_selected = '''                    dpg.add_theme_color(dpg.mvThemeCol_Header, (99, 29, 52, 210))
                    dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (137, 36, 65, 230))
                    dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (48, 178, 211, 255))
                    dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255))
'''
new_selected = '''                    dpg.add_theme_color(dpg.mvThemeCol_Header, (70, 51, 90, 210))
                    dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (133, 56, 148, 230))
                    dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (122, 193, 67, 255))
                    dpg.add_theme_color(dpg.mvThemeCol_Text, (247, 240, 231, 255))
'''
d2pfx = replace_once(d2pfx, old_selected, new_selected, "D2PFX selected palette")
d2pfx = d2pfx.replace('color=(48, 218, 255)', 'color=(255, 255, 0)', 1)
D2PFX_PATH.write_text(d2pfx, encoding="utf-8")


window = WINDOW_PATH.read_text(encoding="utf-8")
old_layout = '''    # v21.1 responsive shell. Give the landing workspace more vertical room
    # and a wider navigation rail so text/buttons are not clipped on Windows.
    nav_width = max(164, min(212, int(shared.window_width * 0.135)))
    shell_body_height = max(340, min(454, int(shared.window_height * 0.43)))
    workspace_width = max(400, shared.window_width - nav_width - 32)
    wide_workspace = workspace_width >= 900
    side_width = 286 if wide_workspace else 0
    main_width = max(340, workspace_width - side_width - (18 if wide_workspace else 0) - 28)
    inner_height = max(248, shell_body_height - 36)

    if dpg.does_item_exist("app_shell_header"):
        dpg.configure_item("app_shell_header", width=shared.window_width, height=72)
    if dpg.does_item_exist("app_nav_rail"):
        dpg.configure_item("app_nav_rail", width=nav_width, height=shell_body_height)
    if dpg.does_item_exist("app_workspace"):
        dpg.configure_item("app_workspace", width=workspace_width, height=shell_body_height)
    if dpg.does_item_exist("app_workspace_main"):
        dpg.configure_item("app_workspace_main", width=main_width, height=inner_height)
    if dpg.does_item_exist("app_workspace_side"):
        dpg.configure_item("app_workspace_side", show=wide_workspace, width=max(1, side_width), height=inner_height)
    if dpg.does_item_exist("dashboard_focus_hint"):
        dpg.configure_item("dashboard_focus_hint", wrap=max(240, main_width - 24))
    if dpg.does_item_exist("dashboard_status_message"):
        dpg.configure_item("dashboard_status_message", wrap=max(190, main_width - 120))
    if dpg.does_item_exist("activity_header"):
        dpg.configure_item("activity_header", width=shared.window_width, height=44)
'''
new_layout = '''    # v21.4 adaptive shell. Width and height breakpoints intentionally remove
    # optional telemetry before any card or label can collide or clip.
    nav_width = max(176, min(220, int(shared.window_width * 0.13)))
    shell_body_height = max(350, min(500, int(shared.window_height * 0.47)))
    workspace_width = max(430, shared.window_width - nav_width - 34)
    wide_workspace = workspace_width >= 1080 and shared.window_height >= 720
    side_width = min(360, max(320, int(workspace_width * 0.25))) if wide_workspace else 0
    main_width = max(360, workspace_width - side_width - (18 if wide_workspace else 0) - 30)
    inner_height = max(300, shell_body_height - 34)
    metric_visible = inner_height >= 350 and main_width >= 560
    hero_height = 168 if metric_visible else 124
    status_height = 60 if inner_height >= 350 else 56
    action_height = 76 if inner_height >= 350 else 66
    flow_height = 136 if inner_height >= 390 else 128
    signal_height = 110 if inner_height >= 390 else 102

    if dpg.does_item_exist("app_shell_header"):
        dpg.configure_item("app_shell_header", width=shared.window_width, height=76)
    if dpg.does_item_exist("header_engine_column"):
        dpg.configure_item("header_engine_column", show=shared.window_width >= 760)
    if dpg.does_item_exist("app_nav_rail"):
        dpg.configure_item("app_nav_rail", width=nav_width, height=shell_body_height)
    if dpg.does_item_exist("app_workspace"):
        dpg.configure_item("app_workspace", width=workspace_width, height=shell_body_height)
    if dpg.does_item_exist("app_workspace_main"):
        dpg.configure_item("app_workspace_main", width=main_width, height=inner_height)
    if dpg.does_item_exist("app_workspace_side"):
        dpg.configure_item("app_workspace_side", show=wide_workspace, width=max(1, side_width), height=inner_height)
    if dpg.does_item_exist("dashboard_hero_card"):
        dpg.configure_item("dashboard_hero_card", height=hero_height)
    if dpg.does_item_exist("dashboard_metric_strip"):
        dpg.configure_item("dashboard_metric_strip", show=metric_visible, height=42)
    if dpg.does_item_exist("metric_restore_column"):
        dpg.configure_item("metric_restore_column", show=main_width >= 650)
    if dpg.does_item_exist("metric_collision_column"):
        dpg.configure_item("metric_collision_column", show=main_width >= 830)
    if dpg.does_item_exist("dashboard_status_panel"):
        dpg.configure_item("dashboard_status_panel", height=status_height)
    if dpg.does_item_exist("dashboard_action_bar"):
        dpg.configure_item("dashboard_action_bar", height=action_height)
    if dpg.does_item_exist("dashboard_flow_card"):
        dpg.configure_item("dashboard_flow_card", height=flow_height)
    if dpg.does_item_exist("dashboard_signal_card"):
        dpg.configure_item("dashboard_signal_card", height=signal_height)
    if dpg.does_item_exist("dashboard_focus_hint"):
        dpg.configure_item("dashboard_focus_hint", wrap=max(240, main_width - 28))
    if dpg.does_item_exist("dashboard_status_message"):
        dpg.configure_item("dashboard_status_message", wrap=max(190, main_width - 120))
    if dpg.does_item_exist("dashboard_safety_text") and wide_workspace:
        dpg.configure_item("dashboard_safety_text", wrap=max(180, side_width - 30))
    if dpg.does_item_exist("activity_header"):
        dpg.configure_item("activity_header", width=shared.window_width, height=44)
    if dpg.does_item_exist("activity_caption"):
        dpg.configure_item("activity_caption", show=shared.window_width >= 900)
    if dpg.does_item_exist("activity_stream_state"):
        dpg.configure_item("activity_stream_state", show=shared.window_width >= 620)
'''
window = replace_once(window, old_layout, new_layout, "responsive layout")
WINDOW_PATH.write_text(window, encoding="utf-8")


TEST_PATH.write_text(
    '''from pathlib import Path


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
''',
    encoding="utf-8",
)

print("JSON palette + responsive layout materialized")
