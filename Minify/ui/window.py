"Main window dragging, resizing and focus"

import ctypes
import subprocess

import dearpygui.dearpygui as dpg
from core import base, config, utils
from core.registry import get_browser_configs

from ui import details, dev_tools, modal_shared, shared, terminal

is_moving_viewport = False


def drag(sender, app_data, user_data):
    global is_moving_viewport

    if is_moving_viewport:
        drag_deltas = app_data
        viewport_current_pos = dpg.get_viewport_pos()
        new_x_position = viewport_current_pos[0] + drag_deltas[1]
        new_y_position = viewport_current_pos[1] + drag_deltas[2]
        new_y_position = max(new_y_position, 0)  # prevent the viewport to go off the top of the screen
        dpg.set_viewport_pos([new_x_position, new_y_position])
    elif dpg.get_item_alias(dpg.get_active_window()) is not None:
        is_hovered = (
            dpg.is_item_hovered("primary_window")
            or dpg.is_item_hovered("terminal_window")
            or dpg.is_item_hovered("footer")
            or dpg.is_item_hovered("mod_menu")
            or dpg.is_item_hovered("settings_menu")
            or dpg.get_item_alias(dpg.get_active_window()).endswith("details_window_tag")
        )

        if not is_hovered and dev_tools.dev_mode_state == 1:
            is_hovered = (
                dpg.is_item_hovered("opener")
                or dpg.is_item_hovered("mod_tools")
                or dpg.is_item_hovered("maintenance_tools")
            )

            debug_env = config.get("debug_env", False) if not base.FROZEN else False
            if not is_hovered and debug_env:
                is_hovered = dpg.is_item_hovered("debug_tools")

        if is_hovered:
            is_moving_viewport = True
            drag_deltas = app_data
            viewport_current_pos = dpg.get_viewport_pos()
            new_x_position = viewport_current_pos[0] + drag_deltas[1]
            new_y_position = viewport_current_pos[1] + drag_deltas[2]
            new_y_position = max(new_y_position, 0)  # prevent the viewport to go off the top of the screen
            dpg.set_viewport_pos([new_x_position, new_y_position])


def stop_drag():
    global is_moving_viewport
    is_moving_viewport = False


def show_overlay(tag):
    """Show an app overlay fitted to the viewport client area."""
    if not dpg.does_item_exist(tag):
        return
    on_resize()
    dpg.configure_item(tag, pos=(0, 0), show=True)
    dpg.focus_item(tag)


def focus():
    with utils.try_pass():
        if base.is_win:
            hwnd = ctypes.windll.user32.FindWindowW(None, "Minify")
            if hwnd != 0:
                ctypes.windll.user32.ShowWindow(hwnd, 9)
                ctypes.windll.user32.SetForegroundWindow(hwnd)

        else:
            subprocess.run(
                ["wmctrl", "-a", "Minify"],
                check=True,
            )


# TODO: wrap sizes should be generalized
def on_resize():
    if dev_tools.dev_mode_state != 1:
        dev_tools.prev_width = dpg.get_viewport_width()
        dev_tools.prev_height = dpg.get_viewport_height()
    shared.viewport_width = dpg.get_viewport_width()
    shared.viewport_height = dpg.get_viewport_height()
    # terminal wrap size
    client_width_fn = getattr(dpg, "get_viewport_client_width", None)
    client_height_fn = getattr(dpg, "get_viewport_client_height", None)
    shared.window_width = int(client_width_fn() if client_width_fn else dpg.get_viewport_width())
    shared.window_height = int(client_height_fn() if client_height_fn else dpg.get_viewport_height())

    if dpg.does_item_exist("primary_window"):
        dpg.configure_item(
            "primary_window",
            pos=(0, 0),
            width=shared.window_width,
            height=shared.window_height,
        )

    # v21.1 responsive shell. Give the landing workspace more vertical room
    # and a wider navigation rail so text/buttons are not clipped on Windows.
    nav_width = max(164, min(212, int(shared.window_width * 0.135)))
    shell_body_height = max(292, min(388, int(shared.window_height * 0.36)))
    workspace_width = max(400, shared.window_width - nav_width - 32)
    wide_workspace = workspace_width >= 900
    side_width = 260 if wide_workspace else 0
    main_width = max(340, workspace_width - side_width - (18 if wide_workspace else 0) - 28)
    inner_height = max(248, shell_body_height - 36)

    if dpg.does_item_exist("app_shell_header"):
        dpg.configure_item("app_shell_header", width=shared.window_width, height=60)
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
        dpg.configure_item("activity_header", width=shared.window_width, height=40)
    if dpg.does_item_exist("settings_scroll"):
        dpg.configure_item("settings_scroll", width=shared.window_width, height=max(220, shared.window_height - 78))
    if dpg.does_item_exist("settings_actions_bar"):
        dpg.configure_item("settings_actions_bar", width=shared.window_width, height=56)
    terminal.wrap_size = (
        base.main_window_width - 20 if dev_tools.dev_mode_state == 1 else min(max(360, shared.window_width - 30), 1180)
    )

    for item in shared.terminal_history:
        idx = item["id"]
        if dpg.does_item_exist(idx):
            dpg.configure_item(idx, wrap=terminal.wrap_size)

    # details windows resize
    for window_tag in shared.tag_data_for_details_windows:
        if dpg.does_item_exist(window_tag):
            dpg.configure_item(window_tag, width=shared.window_width, height=shared.window_height)
            if dpg.is_item_shown(window_tag):
                mod = window_tag.replace("_details_window_tag", "")
                details.render_details_window(mod)

    # menus resize
    if dpg.does_item_exist("mod_menu"):
        dpg.configure_item(
            "mod_menu",
            pos=(0, 0),
            width=shared.window_width,
            height=shared.window_height,
        )
        from ui import checkboxes

        checkboxes.on_resize(shared.window_width, shared.window_height)

    if dpg.does_item_exist("settings_menu"):
        dpg.configure_item(
            "settings_menu",
            pos=(0, 0),
            width=shared.window_width,
            height=shared.window_height,
        )

    # Browser discovery resizing
    for browser_config in get_browser_configs():
        if hasattr(browser_config, "on_resize"):
            browser_config.on_resize()

        for window_tag in getattr(browser_config, "RESIZE_TAGS", []):
            if dpg.does_item_exist(window_tag):
                dpg.configure_item(window_tag, width=shared.window_width, height=shared.window_height)

    if dpg.is_item_shown("modal_popup"):
        modal_shared.configure()
