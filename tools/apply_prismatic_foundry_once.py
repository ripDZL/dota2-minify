from pathlib import Path

root = Path(".")
main_path = root / "Minify" / "__main__.py"
theme_path = root / "Minify" / "ui" / "theme.py"
window_path = root / "Minify" / "ui" / "window.py"
checks_path = root / "Minify" / "ui" / "checkboxes.py"
d2pfx_path = root / "Minify" / "browsers" / "d2pfx" / "ui.py"
test_path = root / "tests" / "test_modern_ui.py"

main = main_path.read_text(encoding="utf-8")
start_marker = "        # v21.1 layout-fit shell."
end_marker = "        dpg.add_spacer(height=4)"
start = main.index(start_marker)
end = main.index(end_marker, start)
layout = r'''        # v21.4 Prismatic Foundry command console. The shell is intentionally
        # layered: brand rail -> command rail -> navigation/workspace -> live activity.
        dpg.add_child_window(
            tag="app_shell_header",
            height=72,
            autosize_x=True,
            border=True,
            no_scrollbar=True,
            no_scroll_with_mouse=True,
        )
        with dpg.group(parent="app_shell_header", horizontal=True, horizontal_spacing=10):
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

        dpg.add_child_window(
            tag="header_accent_rail",
            height=5,
            autosize_x=True,
            border=False,
            no_scrollbar=True,
            no_scroll_with_mouse=True,
        )
        dpg.add_spacer(height=7)

        dpg.add_group(tag="app_shell_body", horizontal=True, horizontal_spacing=9)
        dpg.add_child_window(
            parent="app_shell_body",
            tag="app_nav_rail",
            width=188,
            height=350,
            border=True,
            no_scrollbar=True,
            no_scroll_with_mouse=True,
        )
        dpg.add_text("COMMAND DECK", parent="app_nav_rail", tag="nav_workspace_label")
        dpg.add_child_window(
            parent="app_nav_rail",
            tag="nav_status_card",
            width=-1,
            height=54,
            border=True,
            no_scrollbar=True,
            no_scroll_with_mouse=True,
        )
        dpg.add_text("SYSTEM", parent="nav_status_card", tag="nav_status_title")
        dpg.add_text("● PROTECTED", parent="nav_status_card", tag="nav_status_value")

        dpg.add_spacer(parent="app_nav_rail", height=7)
        dpg.add_button(
            parent="app_nav_rail",
            tag="nav_patch_button",
            label="PATCH CORE",
            callback=lambda: None,
            width=-1,
            height=36,
        )
        dpg.add_button(
            parent="app_nav_rail",
            tag="button_select_mods",
            label="MOD LIBRARY",
            callback=lambda: window.show_overlay("mod_menu"),
            width=-1,
            height=36,
        )
        dpg.add_button(
            parent="app_nav_rail",
            tag="nav_d2pfx_button",
            label="D2PFX NETWORK",
            callback=d2pfx_ui.toggle,
            width=-1,
            height=36,
        )
        dpg.add_button(
            parent="app_nav_rail",
            tag="nav_settings_button",
            label="CONTROL PANEL",
            callback=lambda: window.show_overlay("settings_menu"),
            width=-1,
            height=36,
        )
        dpg.add_spacer(parent="app_nav_rail", height=8)
        dpg.add_separator(parent="app_nav_rail")
        dpg.add_text("RECOVERY", parent="app_nav_rail", tag="nav_secondary_label")
        dpg.add_button(
            parent="app_nav_rail",
            tag="nav_restore_button",
            label="RESTORE POINTS",
            callback=checkboxes.show_backups,
            width=-1,
            height=32,
        )
        dpg.add_button(
            parent="app_nav_rail",
            tag="button_uninstall",
            label="REMOVE MINIFY",
            callback=modals.Uninstall.show,
            width=-1,
            height=32,
        )

        dpg.add_child_window(
            parent="app_shell_body",
            tag="app_workspace",
            width=-1,
            height=350,
            border=True,
            no_scrollbar=True,
            no_scroll_with_mouse=True,
        )
        with dpg.group(parent="app_workspace", tag="workspace_columns", horizontal=True, horizontal_spacing=10):
            dpg.add_child_window(
                parent="workspace_columns",
                tag="app_workspace_main",
                width=-1,
                height=-1,
                border=False,
                no_scrollbar=True,
                no_scroll_with_mouse=True,
            )
            dpg.add_child_window(
                parent="app_workspace_main",
                tag="dashboard_hero_card",
                height=142,
                width=-1,
                border=True,
                no_scrollbar=True,
                no_scroll_with_mouse=True,
            )
            dpg.add_text("PATCH MATRIX  /  RELEASE CONSOLE", parent="dashboard_hero_card", tag="workspace_eyebrow")
            dpg.add_text("Orchestrate your Dota build", parent="dashboard_hero_card", tag="dashboard_focus_title")
            dpg.bind_item_font("dashboard_focus_title", "large_font")
            dpg.add_text(
                "Select, inspect and deploy mods through a guarded patch transaction with collision review and rollback.",
                parent="dashboard_hero_card",
                tag="dashboard_focus_hint",
                wrap=460,
            )
            dpg.add_spacer(parent="dashboard_hero_card", height=5)
            dpg.add_child_window(
                parent="dashboard_hero_card",
                tag="dashboard_metric_strip",
                height=39,
                width=-1,
                border=True,
                no_scrollbar=True,
                no_scroll_with_mouse=True,
            )
            with dpg.group(parent="dashboard_metric_strip", horizontal=True, horizontal_spacing=11):
                dpg.add_text("0 selected • 0 installed", tag="dashboard_metric")
                dpg.add_text("RESTORE // ARMED", tag="metric_restore_state")
                dpg.add_text("COLLISION // INDEXED", tag="metric_collision_state")

            dpg.add_spacer(parent="app_workspace_main", height=6)
            dpg.add_child_window(
                parent="app_workspace_main",
                tag="dashboard_status_panel",
                height=58,
                width=-1,
                border=True,
                no_scrollbar=True,
                no_scroll_with_mouse=True,
            )
            with dpg.group(parent="dashboard_status_panel", horizontal=True):
                dpg.add_text("● READY", tag="dashboard_status_label")
                dpg.add_text("Getting your mod library ready...", tag="dashboard_status_message", wrap=420)

            dpg.add_spacer(parent="app_workspace_main", height=6)
            dpg.add_child_window(
                parent="app_workspace_main",
                tag="dashboard_action_bar",
                height=66,
                width=-1,
                border=True,
                no_scrollbar=True,
                no_scroll_with_mouse=True,
            )
            dpg.add_text("DEPLOYMENT COMMANDS", parent="dashboard_action_bar", tag="dashboard_action_label")
            with dpg.group(parent="dashboard_action_bar", horizontal=True):
                dpg.add_button(
                    tag="button_patch",
                    label="REVIEW + DEPLOY",
                    callback=checkboxes.show_patch_preview,
                    enabled=False,
                    width=210,
                    height=34,
                )
                dpg.add_button(
                    tag="button_refresh_main",
                    label="RESCAN LIBRARY",
                    callback=checkboxes.refresh,
                    width=146,
                    height=34,
                )

            dpg.add_child_window(
                parent="workspace_columns",
                tag="app_workspace_side",
                width=286,
                height=-1,
                border=True,
                no_scrollbar=True,
                no_scroll_with_mouse=True,
            )
            dpg.add_child_window(
                parent="app_workspace_side",
                tag="dashboard_flow_card",
                height=132,
                width=-1,
                border=True,
                no_scrollbar=True,
                no_scroll_with_mouse=True,
            )
            dpg.add_text("DEPLOYMENT SEQUENCE", parent="dashboard_flow_card", tag="dashboard_side_title")
            dpg.add_text("01  ANALYZE      Shared-file collision scan", parent="dashboard_flow_card", tag="dashboard_step_1")
            dpg.add_text("02  SNAPSHOT     Managed-output restore point", parent="dashboard_flow_card", tag="dashboard_step_2")
            dpg.add_text("03  COMPOSE      Apply selected mod graph", parent="dashboard_flow_card", tag="dashboard_step_3")

            dpg.add_spacer(parent="app_workspace_side", height=6)
            dpg.add_child_window(
                parent="app_workspace_side",
                tag="dashboard_signal_card",
                height=100,
                width=-1,
                border=True,
                no_scrollbar=True,
                no_scroll_with_mouse=True,
            )
            dpg.add_text("GUARD MATRIX", parent="dashboard_signal_card", tag="dashboard_signal_title")
            dpg.add_text("ROLLBACK        AUTOMATIC", parent="dashboard_signal_card", tag="signal_rollback")
            dpg.add_text("VALIDATION      ENFORCED", parent="dashboard_signal_card", tag="signal_validation")
            dpg.add_text("PATH SAFETY     CONFINED", parent="dashboard_signal_card", tag="signal_paths")

            dpg.add_spacer(parent="app_workspace_side", height=6)
            dpg.add_child_window(
                parent="app_workspace_side",
                tag="dashboard_safety_card",
                height=-1,
                width=-1,
                border=True,
                no_scrollbar=True,
                no_scroll_with_mouse=True,
            )
            dpg.add_text("FAIL-SAFE", parent="dashboard_safety_card", tag="dashboard_safety_title")
            dpg.add_text(
                "If deployment validation fails, Minify rolls back the managed output to the previous restore point.",
                parent="dashboard_safety_card",
                tag="dashboard_safety_text",
                wrap=240,
            )

        dpg.add_spacer(height=8)
        dpg.add_child_window(
            tag="activity_header",
            height=44,
            autosize_x=True,
            border=True,
            no_scrollbar=True,
            no_scroll_with_mouse=True,
        )
        with dpg.group(parent="activity_header", horizontal=True):
            dpg.add_text("LIVE ACTIVITY", tag="activity_label")
            dpg.add_text("SETUP  /  DOWNLOAD  /  PATCH  /  VALIDATION", tag="activity_caption")
            dpg.add_text("● STREAM ONLINE", tag="activity_stream_state")

'''
main = main[:start] + layout + main[end:]
main_path.write_text(main, encoding="utf-8")

theme = theme_path.read_text(encoding="utf-8")
palette_start = theme.index("# v21.4: Crimson Slate release visual system.")
palette_end = theme.index("settings_theme = 0", palette_start)
palette = '''# v21.4: Prismatic Foundry release visual system.
# Deep navy-black substrate, violet orchestration state, cyan telemetry,
# magenta energy rails, ember deployment actions, and gold metadata.
BACKGROUND = (6, 8, 16, 255)
BACKGROUND_DEEP = (2, 4, 10, 255)
SURFACE = (12, 16, 29, 255)
SURFACE_ALT = (18, 23, 40, 255)
SURFACE_RAISED = (25, 32, 54, 255)
SURFACE_RECESSED = (8, 11, 21, 255)
SURFACE_HOVER = (34, 43, 70, 255)
SURFACE_ACTIVE = (28, 36, 62, 255)
SURFACE_WARM = (35, 20, 32, 255)
BORDER = (64, 74, 115, 255)
BORDER_SOFT = (36, 43, 70, 255)
BEVEL_LIGHT = (105, 121, 177, 255)
BEVEL_DARK = (0, 1, 5, 230)
BEVEL_EMBER = (255, 142, 92, 255)
TEXT = (241, 245, 255, 255)
MUTED = (154, 165, 194, 255)
MUTED_DARK = (86, 96, 125, 255)
ACCENT = (121, 92, 255, 255)
ACCENT_HOVER = (158, 134, 255, 255)
ACCENT_ACTIVE = (94, 68, 228, 255)
ACCENT_MUTED = (55, 43, 124, 255)
CYAN = (48, 218, 255, 255)
CYAN_MUTED = (24, 89, 112, 255)
MAGENTA = (239, 68, 168, 255)
MAGENTA_MUTED = (105, 33, 78, 255)
EMBER = (255, 112, 70, 255)
EMBER_HOVER = (255, 145, 96, 255)
EMBER_ACTIVE = (220, 83, 48, 255)
EMBER_MUTED = (112, 48, 36, 255)
HIGHLIGHT = (255, 203, 94, 255)
D2PFX = (59, 222, 205, 255)
VPK = (131, 216, 151, 255)
DANGER = (238, 72, 105, 255)
DANGER_HOVER = (255, 100, 130, 255)
WARNING = (255, 190, 80, 255)
SUCCESS = (84, 225, 166, 255)

'''
theme = theme[:palette_start] + palette + theme[palette_end:]
theme = theme.replace("dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 2)", "dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)")
theme = theme.replace("dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 3)", "dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 7)")
theme = theme.replace("dpg.add_theme_style(dpg.mvStyleVar_ScrollbarRounding, 2)", "dpg.add_theme_style(dpg.mvStyleVar_ScrollbarRounding, 7)")
theme = theme.replace("dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 2)", "dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 6)")
theme = theme.replace("(126, 37, 64, 255)", "(75, 58, 160, 255)")
theme = theme.replace("(92, 31, 52, 255)", "(76, 59, 163, 255)")
theme = theme.replace("(13, 25, 25, 255)", "(10, 25, 31, 255)")
theme = theme.replace("(42, 91, 82, 255)", "(31, 114, 126, 255)")
theme = theme.replace("(31, 25, 31, 255)", "(16, 25, 42, 255)")
theme = theme.replace("(104, 35, 58, 255)", "(56, 77, 154, 255)")
theme = theme.replace("(207, 145, 150, 255)", "(211, 155, 170, 255)")
theme = theme.replace("(85, 42, 49, 255)", "(88, 37, 55, 255)")
theme = theme.replace("(142, 70, 80, 255)", "(151, 62, 87, 255)")
theme = theme.replace("(56, 55, 67, 255)", "(47, 55, 83, 255)")
theme = theme.replace("(76, 74, 89, 255)", "(68, 79, 118, 255)")

inject_before = '    with dpg.theme(tag="settings_scroll_theme"):\n'
extra_themes = '''    with dpg.theme(tag="header_engine_chip_theme"):
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (14, 18, 34, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Border, CYAN_MUTED)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, (17, 74, 96, 190))
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 8)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=10, y=6)

    with dpg.theme(tag="header_accent_rail_theme"):
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, MAGENTA)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 0)

    with dpg.theme(tag="nav_status_card_theme"):
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (15, 20, 37, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Border, ACCENT_MUTED)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, (40, 31, 93, 180))
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 7)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=9, y=6)

    with dpg.theme(tag="dashboard_metric_strip_theme"):
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, BACKGROUND_DEEP)
            dpg.add_theme_color(dpg.mvThemeCol_Border, (63, 50, 137, 255))
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, (30, 22, 74, 200))
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 6)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=9, y=7)

    with dpg.theme(tag="dashboard_signal_card_theme"):
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (11, 23, 34, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Border, CYAN_MUTED)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, (11, 64, 82, 190))
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 7)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=10, y=7)

    with dpg.theme(tag="prismatic_cyan_text_theme"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, CYAN)

    with dpg.theme(tag="prismatic_magenta_text_theme"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, MAGENTA)

    with dpg.theme(tag="prismatic_gold_text_theme"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, HIGHLIGHT)

    with dpg.theme(tag="prismatic_success_text_theme"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, SUCCESS)

'''
if inject_before not in theme:
    raise SystemExit("theme injection marker missing")
theme = theme.replace(inject_before, extra_themes + inject_before, 1)

old_bind = '''        ("dashboard_safety_card", "dashboard_safety_card_theme"),
        ("dashboard_status_panel", "dashboard_status_panel_theme"),
        ("activity_header", "activity_header_theme"),
'''
new_bind = '''        ("dashboard_safety_card", "dashboard_safety_card_theme"),
        ("dashboard_status_panel", "dashboard_status_panel_theme"),
        ("header_engine_chip", "header_engine_chip_theme"),
        ("header_accent_rail", "header_accent_rail_theme"),
        ("nav_status_card", "nav_status_card_theme"),
        ("dashboard_metric_strip", "dashboard_metric_strip_theme"),
        ("dashboard_signal_card", "dashboard_signal_card_theme"),
        ("activity_header", "activity_header_theme"),
'''
if old_bind not in theme:
    raise SystemExit("theme binding tuple mismatch")
theme = theme.replace(old_bind, new_bind, 1)

old_muted = '''        "dashboard_step_1",
        "dashboard_step_2",
        "dashboard_step_3",
    ):
'''
new_muted = '''        "dashboard_step_1",
        "dashboard_step_2",
        "dashboard_step_3",
        "dashboard_action_label",
        "nav_status_title",
        "header_engine_label",
    ):
'''
if old_muted not in theme:
    raise SystemExit("muted binding tuple mismatch")
theme = theme.replace(old_muted, new_muted, 1)

bind_anchor = '''    if dpg.does_item_exist("dashboard_status_label"):
        dpg.bind_item_theme("dashboard_status_label", "dashboard_status_ready_theme")
'''
bindings = '''    if dpg.does_item_exist("dashboard_status_label"):
        dpg.bind_item_theme("dashboard_status_label", "dashboard_status_ready_theme")
    for tag in ("header_engine_state", "activity_stream_state", "signal_validation", "signal_paths"):
        if dpg.does_item_exist(tag):
            dpg.bind_item_theme(tag, "prismatic_cyan_text_theme")
    for tag in ("metric_restore_state", "nav_status_value", "signal_rollback"):
        if dpg.does_item_exist(tag):
            dpg.bind_item_theme(tag, "prismatic_success_text_theme")
    if dpg.does_item_exist("metric_collision_state"):
        dpg.bind_item_theme("metric_collision_state", "prismatic_gold_text_theme")
    if dpg.does_item_exist("dashboard_signal_title"):
        dpg.bind_item_theme("dashboard_signal_title", "prismatic_magenta_text_theme")
'''
if bind_anchor not in theme:
    raise SystemExit("status binding anchor mismatch")
theme = theme.replace(bind_anchor, bindings, 1)
theme_path.write_text(theme, encoding="utf-8")

checks = checks_path.read_text(encoding="utf-8")
old_palette = '''UI_ACCENT = (190, 39, 77, 255)
UI_ACCENT_HOVER = (224, 54, 94, 255)
UI_EMBER = (207, 43, 79, 255)
UI_EMBER_HOVER = (238, 60, 99, 255)
UI_TEXT = (239, 239, 244, 255)
UI_MUTED = (157, 157, 171, 255)
UI_PANEL = (28, 28, 37, 255)
UI_PANEL_ALT = (34, 34, 45, 255)
UI_RAISED = (42, 42, 54, 255)
UI_RECESSED = (22, 22, 30, 255)
UI_PANEL_HOVER = (51, 50, 63, 255)
UI_BORDER = (69, 68, 82, 255)
UI_BEVEL_LIGHT = (91, 89, 104, 255)
UI_BEVEL_DARK = (2, 2, 5, 170)
UI_D2PFX = (82, 195, 184, 255)
UI_COLLECTION = (231, 109, 137, 255)
UI_VPK = (132, 188, 139, 255)
UI_WARNING = (224, 175, 82, 255)
UI_ERROR = (211, 62, 80, 255)
UI_SUCCESS = (92, 188, 130, 255)
'''
new_palette = '''UI_ACCENT = (121, 92, 255, 255)
UI_ACCENT_HOVER = (158, 134, 255, 255)
UI_EMBER = (255, 112, 70, 255)
UI_EMBER_HOVER = (255, 145, 96, 255)
UI_TEXT = (241, 245, 255, 255)
UI_MUTED = (154, 165, 194, 255)
UI_PANEL = (12, 16, 29, 255)
UI_PANEL_ALT = (18, 23, 40, 255)
UI_RAISED = (25, 32, 54, 255)
UI_RECESSED = (8, 11, 21, 255)
UI_PANEL_HOVER = (34, 43, 70, 255)
UI_BORDER = (64, 74, 115, 255)
UI_BEVEL_LIGHT = (105, 121, 177, 255)
UI_BEVEL_DARK = (0, 1, 5, 230)
UI_D2PFX = (59, 222, 205, 255)
UI_COLLECTION = (255, 203, 94, 255)
UI_VPK = (131, 216, 151, 255)
UI_WARNING = (255, 190, 80, 255)
UI_ERROR = (238, 72, 105, 255)
UI_SUCCESS = (84, 225, 166, 255)
'''
if old_palette not in checks:
    raise SystemExit("checkbox palette mismatch")
checks = checks.replace(old_palette, new_palette, 1)
checks = checks.replace("dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 2)", "dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)")
checks = checks.replace("dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 3)", "dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 7)")
checks_path.write_text(checks, encoding="utf-8")

d2pfx = d2pfx_path.read_text(encoding="utf-8")
for old, new in (
    ("(91, 30, 50, 210)", "(28, 80, 106, 210)"),
    ("(133, 35, 64, 230)", "(35, 122, 151, 230)"),
    ("(184, 43, 79, 255)", "(48, 178, 211, 255)"),
    ("color=(224, 54, 94)", "color=(48, 218, 255)"),
):
    d2pfx = d2pfx.replace(old, new)
d2pfx_path.write_text(d2pfx, encoding="utf-8")

window = window_path.read_text(encoding="utf-8")
window = window.replace(
    "shell_body_height = max(292, min(388, int(shared.window_height * 0.36)))",
    "shell_body_height = max(340, min(454, int(shared.window_height * 0.43)))",
    1,
)
window = window.replace("side_width = 260 if wide_workspace else 0", "side_width = 286 if wide_workspace else 0", 1)
window = window.replace(
    'dpg.configure_item("app_shell_header", width=shared.window_width, height=60)',
    'dpg.configure_item("app_shell_header", width=shared.window_width, height=72)',
    1,
)
window = window.replace(
    'dpg.configure_item("activity_header", width=shared.window_width, height=40)',
    'dpg.configure_item("activity_header", width=shared.window_width, height=44)',
    1,
)
window_path.write_text(window, encoding="utf-8")

tests = '''from pathlib import Path


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


def test_prismatic_foundry_palette_is_materialized():
    assert "# v21.4: Prismatic Foundry release visual system." in THEME
    assert "BACKGROUND = (6, 8, 16, 255)" in THEME
    assert "ACCENT = (121, 92, 255, 255)" in THEME
    assert "CYAN = (48, 218, 255, 255)" in THEME
    assert "MAGENTA = (239, 68, 168, 255)" in THEME
    assert "EMBER = (255, 112, 70, 255)" in THEME
    assert "UI_ACCENT = (121, 92, 255, 255)" in CHECKBOXES


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


def test_release_console_has_multichannel_status_language():
    for label in (
        "PATCH MATRIX  /  RELEASE CONSOLE",
        "RESTORE // ARMED",
        "COLLISION // INDEXED",
        "DEPLOYMENT SEQUENCE",
        "GUARD MATRIX",
        "LIVE ACTIVITY",
        "STREAM ONLINE",
    ):
        assert label in MAIN


def test_prismatic_theme_binds_new_surfaces():
    for pair in (
        '("header_engine_chip", "header_engine_chip_theme")',
        '("header_accent_rail", "header_accent_rail_theme")',
        '("nav_status_card", "nav_status_card_theme")',
        '("dashboard_metric_strip", "dashboard_metric_strip_theme")',
        '("dashboard_signal_card", "dashboard_signal_card_theme")',
    ):
        assert pair in THEME


def test_prismatic_ui_uses_modern_depth_geometry():
    assert "dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)" in THEME
    assert "dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 7)" in THEME
    assert "dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)" in CHECKBOXES
    assert "shell_body_height = max(340, min(454, int(shared.window_height * 0.43)))" in WINDOW


def test_d2pfx_uses_prismatic_network_cyan():
    assert "(48, 178, 211, 255)" in D2PFX
    assert "color=(48, 218, 255)" in D2PFX
    assert "color=(0, 255, 255)" not in D2PFX
'''
test_path.write_text(tests, encoding="utf-8")
