"Dev tools pane that contains things for easy navigation, workarounds and debugging"

import os
import shutil
import threading
import webbrowser

import dearpygui.dearpygui as dpg
import helper
from core import base, config, constants, fs, log, output, steam

from ui import checkboxes, theme

# Developer tools are embedded in Control Panel now. Keep the legacy state
# variables because resize code and third-party integrations may still import them.
dev_mode_state = 0
prev_width = None
prev_height = None

TOOL_BUTTON_MIN_WIDTH = 150
TOOL_BUTTON_MAX_WIDTH = 360
GENERAL_BUTTON_MIN_WIDTH = 84
COMBO_MIN_WIDTH = 220
COMBO_MAX_WIDTH = 520
INPUT_TEXT_MIN_WIDTH = 280
INPUT_TEXT_MAX_WIDTH = 720
TEXT_WIDTH_FALLBACK = 8
TOOL_BUTTON_PADDING = 38
COMBO_PADDING = 58
INPUT_TEXT_PADDING = 44
RESTORE_BUTTON_WIDTH = 180
RESTORE_BUTTON_HEIGHT = 30
HOME_COMPACT_MIN_SHELL_HEIGHT = 250
HOME_COMPACT_INNER_INSET = 34
HOME_COMPACT_VERTICAL_GAP = 22
HOME_STATUS_HEIGHT = 68
HOME_ACTION_NORMAL_HEIGHT = 96
HOME_CENTER_SIDE_PADDING = 20
HOME_STATUS_TEXT_GAP = 8
HOME_SURFACE_TAGS = (
    "app_workspace_main",
    "dashboard_hero_card",
    "dashboard_metric_strip",
    "dashboard_status_panel",
    "dashboard_action_bar",
)
HOME_SEPARATOR_PLACEMENTS = (
    ("home_separator_after_intro", "dashboard_hero_card", "dashboard_metric_strip"),
    ("home_separator_before_status", "app_workspace_main", "dashboard_status_panel"),
    ("home_separator_before_actions", "app_workspace_main", "dashboard_action_bar"),
)


def extract_workshop_tools():
    "Extracts the bare minimum requirements for resourcecompiler.exe"
    output.clean()
    fs.remove_path(base.rescomp_override_dir)
    fails = 0

    for i, path in enumerate(constants.dota_tools_paths):
        if os.path.exists(path):
            if os.path.isdir(path):
                shutil.copytree(path, constants.dota_tools_extraction_paths[i])
            else:
                shutil.copy(path, constants.dota_tools_extraction_paths[i])
        else:
            output.add_text("&extraction_of_failed", path)
            fails += 1

    if not fails:
        constants.recalc_rescomp_dirs()
        if os.path.exists(constants.dota_resource_compiler_path):
            output.add_text("&extracted")
        else:
            output.add_text("&extraction_of_failed", path)


def tick_batch(state: bool):
    for box in checkboxes.checkboxes:
        box_cfg = dpg.get_item_configuration(box)
        if box_cfg["enabled"]:
            dpg.set_value(box, state)
    checkboxes.setup_state()


def _text_width(label):
    label = str(label or "")
    try:
        measured = dpg.get_text_size(label)
        width = int(measured[0]) if measured else 0
        if width > 0:
            return width
    except Exception:
        pass
    return max(1, len(label)) * TEXT_WIDTH_FALLBACK


def _item_width(tag, fallback):
    try:
        width = int(dpg.get_item_rect_size(tag)[0])
        return width if width > 0 else fallback
    except Exception:
        return fallback


def _fit_control_width(label, min_width, max_width, padding):
    return max(min_width, min(max_width, _text_width(label) + padding))


def _tool_button(parent, label, callback):
    width = _fit_control_width(label, TOOL_BUTTON_MIN_WIDTH, TOOL_BUTTON_MAX_WIDTH, TOOL_BUTTON_PADDING)
    return dpg.add_button(parent=parent, label=label, callback=callback, width=width)


def _section_header(parent, label, default_open=False):
    # Dear PyGui collapsing headers do not expose a width configuration field.
    # Keep headers full-row and content-fit the actionable controls inside them.
    return dpg.add_collapsing_header(parent=parent, label=label, default_open=default_open)


def _walk_descendants(parent):
    for slot in range(4):
        try:
            children = dpg.get_item_children(parent, slot) or []
        except Exception:
            children = []
        for child in children:
            yield child
            yield from _walk_descendants(child)


def _combo_display_text(item):
    try:
        cfg = dpg.get_item_configuration(item)
    except Exception:
        cfg = {}
    candidates = [str(value) for value in (cfg.get("items") or []) if value not in (None, "")]
    try:
        current = dpg.get_value(item)
    except Exception:
        current = ""
    if current not in (None, ""):
        candidates.append(str(current))
    return max(candidates, key=len) if candidates else "Select"


def _input_display_text(item):
    try:
        current = dpg.get_value(item)
    except Exception:
        current = ""
    return str(current or "")


def _fit_general_control_panel_controls():
    """Keep supported Settings fields, combos and action buttons content-sized."""
    if not dpg.does_item_exist("settings_content_group"):
        return

    for item in _walk_descendants("settings_content_group"):
        try:
            item_type = str(dpg.get_item_type(item))
            cfg = dpg.get_item_configuration(item)
            alias = str(dpg.get_item_alias(item) or "")
        except Exception:
            continue

        label = str(cfg.get("label") or "")
        if "mvInputText" in item_type and alias.startswith("opt_"):
            dpg.configure_item(
                item,
                width=_fit_control_width(
                    _input_display_text(item),
                    INPUT_TEXT_MIN_WIDTH,
                    INPUT_TEXT_MAX_WIDTH,
                    INPUT_TEXT_PADDING,
                ),
            )
        elif "mvCombo" in item_type:
            dpg.configure_item(
                item,
                width=_fit_control_width(_combo_display_text(item), COMBO_MIN_WIDTH, COMBO_MAX_WIDTH, COMBO_PADDING),
            )
        elif "mvButton" in item_type and label:
            dpg.configure_item(
                item,
                width=_fit_control_width(label, GENERAL_BUTTON_MIN_WIDTH, TOOL_BUTTON_MAX_WIDTH, TOOL_BUTTON_PADDING),
            )


def _item_value(tag):
    try:
        return str(dpg.get_value(tag) or "")
    except Exception:
        return ""


def _ensure_compact_home_center_groups():
    """Place the surviving Home copy in tagged rows that can be centered safely."""
    if dpg.does_item_exist("dashboard_status_panel"):
        if not dpg.does_item_exist("home_status_line") and dpg.does_item_exist("dashboard_metric"):
            dpg.add_group(
                parent="dashboard_status_panel",
                tag="home_status_line",
                horizontal=True,
                horizontal_spacing=HOME_STATUS_TEXT_GAP,
                before="dashboard_metric",
            )
            dpg.add_spacer(parent="home_status_line", tag="home_status_line_spacer", width=0)
            for tag in ("dashboard_status_label", "dashboard_status_message"):
                if dpg.does_item_exist(tag):
                    dpg.move_item(tag, parent="home_status_line")

        if not dpg.does_item_exist("home_metric_line") and dpg.does_item_exist("dashboard_metric"):
            dpg.add_group(
                parent="dashboard_status_panel",
                tag="home_metric_line",
                horizontal=True,
                before="dashboard_metric",
            )
            dpg.add_spacer(parent="home_metric_line", tag="home_metric_line_spacer", width=0)
            dpg.move_item("dashboard_metric", parent="home_metric_line")

    if (
        dpg.does_item_exist("dashboard_action_bar")
        and dpg.does_item_exist("dashboard_action_label")
        and not dpg.does_item_exist("home_action_label_line")
    ):
        dpg.add_group(
            parent="dashboard_action_bar",
            tag="home_action_label_line",
            horizontal=True,
            before="dashboard_action_label",
        )
        dpg.add_spacer(parent="home_action_label_line", tag="home_action_label_spacer", width=0)
        dpg.move_item("dashboard_action_label", parent="home_action_label_line")

    if (
        dpg.does_item_exist("dashboard_action_bar")
        and dpg.does_item_exist("dashboard_action_buttons")
        and not dpg.does_item_exist("home_action_buttons_row")
    ):
        dpg.add_group(
            parent="dashboard_action_bar",
            tag="home_action_buttons_row",
            horizontal=True,
            horizontal_spacing=0,
        )
        dpg.add_spacer(parent="home_action_buttons_row", tag="home_action_buttons_spacer", width=0)
        dpg.move_item("dashboard_action_buttons", parent="home_action_buttons_row")


def _center_home_line(parent, spacer, text_tags, spacing=0):
    if not dpg.does_item_exist(parent) or not dpg.does_item_exist(spacer):
        return

    parent_width = _item_width(parent, 0)
    if parent_width <= 0:
        return

    visible_tags = [tag for tag in text_tags if dpg.does_item_exist(tag)]
    text_width = sum(_text_width(_item_value(tag)) for tag in visible_tags)
    if len(visible_tags) > 1:
        text_width += spacing * (len(visible_tags) - 1)

    available_width = max(0, parent_width - HOME_CENTER_SIDE_PADDING)
    spacer_width = max(0, (available_width - text_width) // 2)
    dpg.configure_item(spacer, width=spacer_width)


def _configured_width(tag, fallback):
    try:
        width = int(dpg.get_item_configuration(tag).get("width", fallback))
        return width if width > 0 else fallback
    except Exception:
        return fallback


def _center_home_action_buttons():
    """Center the responsive Patch/Rescan cluster inside the deployment surface."""
    required = (
        "dashboard_action_bar",
        "dashboard_action_buttons",
        "home_action_buttons_spacer",
        "button_patch",
        "button_refresh_main",
    )
    if any(not dpg.does_item_exist(tag) for tag in required):
        return

    parent_width = _item_width("dashboard_action_bar", 0)
    if parent_width <= 0:
        return

    try:
        group_cfg = dpg.get_item_configuration("dashboard_action_buttons")
    except Exception:
        group_cfg = {}
    horizontal = bool(group_cfg.get("horizontal", True))
    spacing = int(group_cfg.get("horizontal_spacing", 8) or 0)

    patch_width = _item_width("button_patch", _configured_width("button_patch", 210))
    refresh_width = _item_width("button_refresh_main", _configured_width("button_refresh_main", 146))
    cluster_width = (
        patch_width + refresh_width + spacing if horizontal else max(patch_width, refresh_width)
    )
    available_width = max(0, parent_width - HOME_CENTER_SIDE_PADDING)
    spacer_width = max(0, (available_width - cluster_width) // 2)
    dpg.configure_item("home_action_buttons_spacer", width=spacer_width)


def _center_compact_home_text():
    """Center Home status/count/section copy and the deployment button cluster."""
    _ensure_compact_home_center_groups()
    _center_home_line(
        "dashboard_status_panel",
        "home_status_line_spacer",
        ("dashboard_status_label", "dashboard_status_message"),
        spacing=HOME_STATUS_TEXT_GAP,
    )
    _center_home_line(
        "dashboard_status_panel",
        "home_metric_line_spacer",
        ("dashboard_metric",),
    )
    _center_home_line(
        "dashboard_action_bar",
        "home_action_label_spacer",
        ("dashboard_action_label",),
    )
    _center_home_action_buttons()


def _ensure_home_uniform_surface():
    """Render Home as one slate surface with light section separators."""
    if not dpg.does_item_exist("home_uniform_surface_theme"):
        with dpg.theme(tag="home_uniform_surface_theme"):
            with dpg.theme_component(dpg.mvChildWindow):
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, theme.SURFACE)
                dpg.add_theme_color(dpg.mvThemeCol_Border, theme.SURFACE)
                dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, theme.SURFACE)
                dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 0)
                dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 0)
                dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=10, y=8)

    if not dpg.does_item_exist("home_uniform_table_theme"):
        with dpg.theme(tag="home_uniform_table_theme"):
            with dpg.theme_component(dpg.mvTable):
                dpg.add_theme_color(dpg.mvThemeCol_TableRowBg, theme.SURFACE)
                dpg.add_theme_color(dpg.mvThemeCol_TableRowBgAlt, theme.SURFACE)
                dpg.add_theme_color(dpg.mvThemeCol_TableBorderStrong, theme.SURFACE)
                dpg.add_theme_color(dpg.mvThemeCol_TableBorderLight, theme.SURFACE)

    if not dpg.does_item_exist("home_subtle_separator_theme"):
        with dpg.theme(tag="home_subtle_separator_theme"):
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Separator, theme.BORDER_SOFT)
                dpg.add_theme_color(dpg.mvThemeCol_SeparatorHovered, theme.BORDER_SOFT)
                dpg.add_theme_color(dpg.mvThemeCol_SeparatorActive, theme.BORDER_SOFT)

    for tag in HOME_SURFACE_TAGS:
        if dpg.does_item_exist(tag):
            dpg.bind_item_theme(tag, "home_uniform_surface_theme")
            if tag != "app_workspace_main":
                dpg.configure_item(tag, border=False)

    if dpg.does_item_exist("dashboard_metric_table"):
        dpg.bind_item_theme("dashboard_metric_table", "home_uniform_table_theme")

    for separator_tag, parent, before in HOME_SEPARATOR_PLACEMENTS:
        if not dpg.does_item_exist(separator_tag) and dpg.does_item_exist(parent) and dpg.does_item_exist(before):
            dpg.add_separator(parent=parent, tag=separator_tag)
            dpg.bind_item_theme(separator_tag, "home_subtle_separator_theme")
            try:
                dpg.move_item(separator_tag, parent=parent, before=before)
            except Exception:
                pass

    # Hide the explanatory hero/sequence immediately. A one-frame delayed
    # layout pass runs after window.on_resize finishes so the Home shell itself
    # also collapses to the live status + deployment controls.
    _apply_compact_home_layout()
    _schedule_compact_home_layout()


def _configured_height(tag, fallback):
    try:
        height = int(dpg.get_item_configuration(tag).get("height", fallback))
        return height if height > 0 else fallback
    except Exception:
        return fallback


def _apply_compact_home_layout():
    """Keep Home focused on live status and deployment controls only."""
    for tag in ("dashboard_hero_card", "dashboard_metric_strip"):
        if dpg.does_item_exist(tag):
            dpg.configure_item(tag, show=False)

    for tag in ("home_separator_after_intro", "home_separator_before_status"):
        if dpg.does_item_exist(tag):
            dpg.configure_item(tag, show=False)
    if dpg.does_item_exist("home_separator_before_actions"):
        dpg.configure_item("home_separator_before_actions", show=True)

    action_height = max(
        HOME_ACTION_NORMAL_HEIGHT, _configured_height("dashboard_action_bar", HOME_ACTION_NORMAL_HEIGHT)
    )
    inner_height = HOME_STATUS_HEIGHT + action_height + HOME_COMPACT_VERTICAL_GAP
    shell_height = max(HOME_COMPACT_MIN_SHELL_HEIGHT, inner_height + HOME_COMPACT_INNER_INSET)

    if dpg.does_item_exist("app_nav_rail"):
        dpg.configure_item("app_nav_rail", height=shell_height)
    if dpg.does_item_exist("app_workspace"):
        dpg.configure_item("app_workspace", height=shell_height)
    if dpg.does_item_exist("app_workspace_main"):
        dpg.configure_item(
            "app_workspace_main",
            height=inner_height,
            no_scrollbar=True,
            no_scroll_with_mouse=True,
        )
    if dpg.does_item_exist("dashboard_status_panel"):
        dpg.configure_item("dashboard_status_panel", height=HOME_STATUS_HEIGHT)
    if dpg.does_item_exist("dashboard_action_bar"):
        dpg.configure_item("dashboard_action_bar", height=action_height)

    _center_compact_home_text()


def _schedule_compact_home_layout():
    """Reapply compact Home dimensions after the parent resize pass completes."""
    set_frame_callback = getattr(dpg, "set_frame_callback", None)
    get_frame_count = getattr(dpg, "get_frame_count", None)
    if callable(set_frame_callback) and callable(get_frame_count):
        try:
            set_frame_callback(
                get_frame_count() + 1,
                lambda sender=None, app_data=None: _apply_compact_home_layout(),
            )
            return
        except Exception:
            pass
    _apply_compact_home_layout()


def _ensure_restore_dialog_fit():
    """Keep the restore action label inside its button on Windows font metrics."""
    if dpg.does_item_exist("backup_restore_button"):
        dpg.configure_item(
            "backup_restore_button",
            width=RESTORE_BUTTON_WIDTH,
            height=RESTORE_BUTTON_HEIGHT,
        )


def _wipe_language_paths():
    import patch

    threading.Thread(target=patch.unins.wipe, daemon=True).start()


def render_panel(parent):
    """Render advanced tools inside the Control Panel Developer tab."""
    if dpg.does_item_exist("developer_tools_content"):
        return

    with dpg.group(parent=parent, tag="developer_tools_content"):
        dpg.add_text("DEVELOPER TOOLS", tag="developer_tools_title")
        dpg.add_text(
            "Advanced diagnostics and maintenance. Use these only when you know what the action changes.",
            tag="developer_tools_warning",
            wrap=700,
        )
        dpg.add_separator()

        paths = _section_header("developer_tools_content", "Paths & files", default_open=True)
        _tool_button(paths, "Open compile output path", lambda: fs.open_thing(os.path.join(helper.output_path)))
        _tool_button(
            paths,
            "Open compiled pak66 VPK",
            lambda: fs.open_thing(os.path.join(helper.output_path, "pak66_dir.vpk")),
        )
        _tool_button(paths, "Open Minify root", lambda: fs.open_thing(os.getcwd()))
        _tool_button(paths, "Open logs", lambda: fs.open_thing(base.logs_dir))
        _tool_button(paths, "Open config", lambda: fs.open_thing(base.config_dir))
        _tool_button(paths, "Open mods", lambda: fs.open_thing(base.mods_dir))
        _tool_button(
            paths,
            "Open Dota 2 folder",
            lambda: fs.open_thing(os.path.join(config.get("steam_library"), "steamapps", "common", "dota 2 beta")),
        )
        _tool_button(paths, "Open Dota 2 pak01 VPK", lambda: fs.open_thing(constants.dota_game_pak_path))
        _tool_button(paths, "Open Dota 2 core pak01 VPK", lambda: fs.open_thing(constants.dota_core_pak_path))
        _tool_button(
            paths,
            "Launch Dota 2 Tools",
            lambda: fs.open_thing(
                constants.dota2_tools_executable,
                f"-addon a -language {config.get('output_locale')} -novid -console",
            ),
        )
        dpg.add_text("Requires Steam to be running.", parent=paths)
        _tool_button(
            paths,
            "Launch Dota 2",
            lambda: fs.open_thing(
                constants.dota2_executable,
                f"-language {config.get('output_locale')} -novid -console",
            ),
        )
        _tool_button(paths, "Create debug zip", log.create_debug_zip)

        mod_tools = _section_header("developer_tools_content", "Mod tools", default_open=False)
        _tool_button(mod_tools, "Select path to compile", helper.select_compile_dir)
        _tool_button(
            mod_tools,
            "Compile items from selected path",
            lambda: helper.compile_assets(
                input_path=os.path.join(base.config_dir, "custom"),
                output_path=os.path.join(base.config_dir, "compiled"),
            ),
        )
        _tool_button(mod_tools, "Untick all mods", lambda: tick_batch(False))
        _tool_button(mod_tools, "Tick all mods", lambda: tick_batch(True))

        maintenance = _section_header("developer_tools_content", "Maintenance", default_open=False)
        dpg.add_text("These actions can change local Steam/Dota state.", parent=maintenance, wrap=700)
        _tool_button(
            maintenance,
            "Wipe language paths",
            _wipe_language_paths,
        )
        _tool_button(maintenance, "Extract workshop tools", extract_workshop_tools)
        _tool_button(maintenance, "Launch Steam", lambda: fs.open_thing(steam.steam_executable_path, "-silent"))
        _tool_button(maintenance, "Kill Steam", lambda: fs.open_thing(steam.steam_executable_path, "-exitsteam"))
        _tool_button(maintenance, "Validate Dota 2", lambda: webbrowser.open(f"steam://validate/{base.STEAM_DOTA_ID}"))

        debug_env = config.get("debug_env", False) if not base.FROZEN else False
        if not base.FROZEN and debug_env:
            debug_tools = _section_header("developer_tools_content", "Dear PyGui diagnostics", default_open=False)
            _tool_button(debug_tools, "Debug", dpg.show_debug)
            _tool_button(debug_tools, "Item registry", dpg.show_item_registry)
            _tool_button(debug_tools, "Metrics", dpg.show_metrics)
            _tool_button(debug_tools, "Style editor", dpg.show_style_editor)
            _tool_button(debug_tools, "Font manager", dpg.show_font_manager)


def install_control_panel_tab():
    """Install Preferences/Developer tabs into the existing Control Panel."""
    if not dpg.does_item_exist("settings_scroll") or not dpg.does_item_exist("settings_content_group"):
        return

    if not dpg.does_item_exist("settings_tabs"):
        with dpg.tab_bar(parent="settings_scroll", tag="settings_tabs"):
            dpg.add_tab(label="GENERAL", tag="settings_general_tab")
            dpg.add_tab(label="DEVELOPER", tag="settings_developer_tab")

        dpg.move_item("settings_content_group", parent="settings_general_tab")

    if dpg.does_item_exist("settings_developer_tab"):
        render_panel("settings_developer_tab")

    # Settings can rebuild their children after Reload/Reset. Re-apply content
    # fitting whenever the Control Panel is opened/resized so rebuilt controls
    # do not return to full-row width.
    _fit_general_control_panel_controls()

    # Home is also revisited on resize. Keep its implementation visually merged
    # into one continuous surface, then add restrained divider lines between the
    # major user-facing stages so the page scans cleanly without nested cards.
    _ensure_home_uniform_surface()
    _ensure_restore_dialog_fit()

    # Remove any old floating developer panes if this build is reached from a
    # live/reloaded context rather than a clean process start.
    for tag in ("opener", "mod_tools", "maintenance_tools", "debug_tools"):
        if dpg.does_item_exist(tag):
            dpg.delete_item(tag)


def toggle():
    """Open the Control Panel directly on its Developer tab."""
    global dev_mode_state
    dev_mode_state = 0
    install_control_panel_tab()

    if dpg.does_item_exist("settings_menu"):
        from ui import window

        window.show_overlay("settings_menu")
        if dpg.does_item_exist("settings_tabs") and dpg.does_item_exist("settings_developer_tab"):
            dpg.set_value("settings_tabs", "settings_developer_tab")
