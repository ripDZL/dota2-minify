"Dev tools pane that contains things for easy navigation, workarounds and debugging"

import os
import shutil
import threading
import webbrowser

import dearpygui.dearpygui as dpg
import helper
from core import base, config, constants, fs, log, output, steam

from ui import checkboxes

# Developer tools are embedded in Control Panel now. Keep the legacy state
# variables because resize code and third-party integrations may still import them.
dev_mode_state = 0
prev_width = None
prev_height = None

TOOL_BUTTON_MIN_WIDTH = 150
TOOL_BUTTON_MAX_WIDTH = 360
SECTION_HEADER_MIN_WIDTH = 150
SECTION_HEADER_MAX_WIDTH = 360
GENERAL_BUTTON_MIN_WIDTH = 84
COMBO_MIN_WIDTH = 220
COMBO_MAX_WIDTH = 520
TEXT_WIDTH_FALLBACK = 8
TOOL_BUTTON_PADDING = 38
SECTION_HEADER_PADDING = 48
COMBO_PADDING = 58


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


def _fit_control_width(label, min_width, max_width, padding):
    return max(min_width, min(max_width, _text_width(label) + padding))


def _tool_button(parent, label, callback):
    width = _fit_control_width(label, TOOL_BUTTON_MIN_WIDTH, TOOL_BUTTON_MAX_WIDTH, TOOL_BUTTON_PADDING)
    return dpg.add_button(parent=parent, label=label, callback=callback, width=width)


def _section_header(parent, label, default_open=False):
    width = _fit_control_width(label, SECTION_HEADER_MIN_WIDTH, SECTION_HEADER_MAX_WIDTH, SECTION_HEADER_PADDING)
    return dpg.add_collapsing_header(parent=parent, label=label, default_open=default_open, width=width)


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


def _fit_general_control_panel_controls():
    """Keep Settings section headers, combos and action buttons content-sized."""
    if not dpg.does_item_exist("settings_content_group"):
        return

    for item in _walk_descendants("settings_content_group"):
        try:
            item_type = str(dpg.get_item_type(item))
            cfg = dpg.get_item_configuration(item)
        except Exception:
            continue

        label = str(cfg.get("label") or "")
        if "mvCollapsingHeader" in item_type and label:
            dpg.configure_item(
                item,
                width=_fit_control_width(
                    label,
                    SECTION_HEADER_MIN_WIDTH,
                    SECTION_HEADER_MAX_WIDTH,
                    SECTION_HEADER_PADDING,
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
