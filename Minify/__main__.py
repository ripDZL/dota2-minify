import os
import sys
import threading
import time
import webbrowser

from core import base

base.original_cwd = os.getcwd()

# Ensure root directories
if getattr(sys, "frozen", False):
    os.chdir(os.path.dirname(os.path.realpath(sys.executable)))
else:
    os.chdir(current_dir := os.path.dirname(os.path.abspath(__file__)))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

os.makedirs("cache", exist_ok=True)
os.makedirs("config", exist_ok=True)
os.makedirs("logs", exist_ok=True)

if len(sys.argv) > 1:
    import cli

    cli.run()
    sys.exit(0)

# isort: split

import browsers
import conditions
import dearpygui.dearpygui as dpg
import helper
import patch
from browsers.d2pfx import ui as d2pfx_ui
from core import base, config, constants, log
from ui import (
    checkboxes,
    dev_tools,
    fonts,
    gui,
    localization,
    modals,
    settings,
    shared,
    theme,
    window,
)

sys.excepthook = log.unhandled_handler()
browsers.initialize()

dpg.create_context()


def create_ui():
    button_size_x, button_size_y = gui.social_button_size
    with dpg.window(
        tag="primary_window",
        no_title_bar=True,
        no_move=True,
        no_resize=True,
        no_collapse=True,
        no_close=True,
        no_saved_settings=True,
        pos=(0, 0),
    ):
        # v21.1 layout-fit shell. Responsive child windows replace the
        # fixed-height v19.7 shell so Windows font metrics cannot clip actions.
        dpg.add_child_window(
            tag="app_shell_header",
            height=60,
            autosize_x=True,
            border=False,
            no_scrollbar=True,
            no_scroll_with_mouse=True,
        )
        with dpg.group(parent="app_shell_header", horizontal=True):
            dpg.add_text("MINIFY", tag="app_title")
            dpg.bind_item_font("app_title", "large_font")
            dpg.add_text("Dota 2 Mod Manager", tag="app_product_name")
            dpg.add_text(f"v{base.VERSION}", tag="app_version")
            dpg.add_spacer(tag="header_spacer", width=10)
            dpg.add_text("LOCAL MOD WORKSPACE", tag="header_context")
            dpg.add_text("RC6", tag="header_badge")

        dpg.add_spacer(height=8)
        dpg.add_group(tag="app_shell_body", horizontal=True, horizontal_spacing=8)
        dpg.add_child_window(
            parent="app_shell_body",
            tag="app_nav_rail",
            width=172,
            height=304,
            border=True,
            no_scrollbar=True,
            no_scroll_with_mouse=True,
        )
        dpg.add_text("NAVIGATION", parent="app_nav_rail", tag="nav_workspace_label")
        dpg.add_button(
            parent="app_nav_rail", tag="nav_patch_button", label="Patch", callback=lambda: None, width=-1, height=34
        )
        dpg.add_button(
            parent="app_nav_rail",
            tag="button_select_mods",
            label="Select Mods",
            callback=lambda: window.show_overlay("mod_menu"),
            width=-1,
            height=34,
        )
        dpg.add_button(
            parent="app_nav_rail",
            tag="nav_d2pfx_button",
            label="D2PFX Browser",
            callback=d2pfx_ui.toggle,
            width=-1,
            height=36,
        )
        dpg.add_button(
            parent="app_nav_rail",
            tag="nav_settings_button",
            label="Settings",
            callback=lambda: window.show_overlay("settings_menu"),
            width=-1,
            height=36,
        )
        dpg.add_spacer(parent="app_nav_rail", height=7)
        dpg.add_separator(parent="app_nav_rail")
        dpg.add_text("RECOVERY", parent="app_nav_rail", tag="nav_secondary_label")
        dpg.add_button(
            parent="app_nav_rail",
            tag="nav_restore_button",
            label="Restore backups",
            callback=checkboxes.show_backups,
            width=-1,
            height=32,
        )
        dpg.add_button(
            parent="app_nav_rail",
            tag="button_uninstall",
            label="Remove Minify",
            callback=modals.Uninstall.show,
            width=-1,
            height=32,
        )

        dpg.add_child_window(
            parent="app_shell_body",
            tag="app_workspace",
            width=-1,
            height=304,
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
            dpg.add_text("PATCH WORKSPACE", parent="app_workspace_main", tag="workspace_eyebrow")
            dpg.add_text("Build a clean patch", parent="app_workspace_main", tag="dashboard_focus_title")
            dpg.bind_item_font("dashboard_focus_title", "large_font")
            dpg.add_text("0 selected • 0 installed", parent="app_workspace_main", tag="dashboard_metric")
            dpg.add_text(
                "Choose your mods, review shared files, then let Minify create a restore point before changing Dota.",
                parent="app_workspace_main",
                tag="dashboard_focus_hint",
                wrap=420,
            )
            dpg.add_spacer(parent="app_workspace_main", height=5)
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
            with dpg.group(parent="app_workspace_main", horizontal=True):
                dpg.add_button(
                    tag="button_patch",
                    label="Review & Patch",
                    callback=checkboxes.show_patch_preview,
                    enabled=False,
                    width=196,
                    height=40,
                )
                dpg.add_button(
                    tag="button_refresh_main", label="Refresh", callback=checkboxes.refresh, width=132, height=40
                )

            dpg.add_child_window(
                parent="workspace_columns",
                tag="app_workspace_side",
                width=260,
                height=-1,
                border=True,
                no_scrollbar=True,
                no_scroll_with_mouse=True,
            )
            dpg.add_text("PATCH FLOW", parent="app_workspace_side", tag="dashboard_side_title")
            dpg.add_text("01  Review shared files", parent="app_workspace_side", tag="dashboard_step_1")
            dpg.add_text("02  Create restore point", parent="app_workspace_side", tag="dashboard_step_2")
            dpg.add_text("03  Apply selected mods", parent="app_workspace_side", tag="dashboard_step_3")
            dpg.add_spacer(parent="app_workspace_side", height=6)
            dpg.add_separator(parent="app_workspace_side")
            dpg.add_text("SAFETY", parent="app_workspace_side")
            dpg.add_text(
                "Automatic rollback protects the previous Minify output if a patch fails.",
                parent="app_workspace_side",
                wrap=220,
            )

        dpg.add_spacer(height=8)
        dpg.add_child_window(
            tag="activity_header", height=40, autosize_x=True, border=True, no_scrollbar=True, no_scroll_with_mouse=True
        )
        with dpg.group(parent="activity_header", horizontal=True):
            dpg.add_text("ACTIVITY", tag="activity_label")
            dpg.add_text("Live setup, download and patch output", tag="activity_caption")

        dpg.add_spacer(height=4)
        with dpg.group(tag="terminal_and_footer_group"):
            dpg.add_child_window(
                tag="terminal_window", no_scrollbar=False, show=True, autosize_x=True, height=-31, border=True
            )
            dpg.bind_item_font("terminal_window", "small_font")
            dpg.add_child_window(
                tag="footer", height=27, no_scrollbar=True, no_scroll_with_mouse=True, autosize_x=True, border=False
            )
        dpg.add_group(tag="footer_main_group", parent="footer", horizontal=True, horizontal_spacing=0)
        dpg.add_group(tag="footer_left_group", parent="footer_main_group", horizontal=True, horizontal_spacing=0)
        dpg.add_combo(
            parent="footer_left_group",
            tag="lang_select",
            items=(localization.localizations),
            default_value="EN",
            callback=localization.change,
            fit_width=True,
        )
        dpg.add_image_button(
            "discord_texture_tag",
            tag="button_discord",
            parent="footer_left_group",
            width=button_size_x,
            height=button_size_y,
            callback=lambda: webbrowser.open(base.discord),
        )
        dpg.add_image_button(
            "telegram_texture_tag",
            tag="button_telegram",
            parent="footer_left_group",
            width=button_size_x,
            height=button_size_y,
            callback=lambda: webbrowser.open(base.telegram),
        )
        dpg.add_image_button(
            "git_texture_tag",
            tag="button_git",
            parent="footer_left_group",
            width=button_size_x,
            height=button_size_y,
            callback=lambda: webbrowser.open(base.github_io),
        )
        dpg.add_image_button(
            "settings_texture_tag",
            tag="button_settings",
            parent="footer_left_group",
            show=False,
            width=button_size_x,
            height=button_size_y,
            callback=lambda: window.show_overlay("settings_menu"),
        )
        dpg.add_image_button(
            "dev_texture_tag",
            tag="button_dev",
            parent="footer_left_group",
            width=button_size_x,
            height=button_size_y,
            callback=dev_tools.toggle,
        )
        dpg.add_image_button(
            "refresh_texture_tag",
            tag="button_refresh",
            parent="footer_left_group",
            show=False,
            width=button_size_x,
            height=button_size_y,
            callback=checkboxes.refresh,
        )
        dpg.add_image_button(
            "d2pfx_texture_tag",
            tag="button_browser_d2pfx",
            parent="footer_left_group",
            show=False,
            width=button_size_x,
            height=button_size_y,
            callback=d2pfx_ui.toggle,
        )
        dpg.add_text(tag="language_select", parent="footer_left_group")
        dpg.add_combo(
            parent="footer_left_group",
            tag="output_select",
            items=(constants.minify_output_list),
            default_value=config.get("output_locale", "english"),
            callback=helper.change_output_path,
            fit_width=True,
        )

    # Register only after the complete primary window has been built.
    dpg.set_primary_window("primary_window", True)

    with dpg.tooltip(parent="nav_patch_button"):
        dpg.add_text("Current workspace: review and apply your selected mods")
    with dpg.tooltip(parent="button_patch"):
        dpg.add_text("Review selected mods, overlaps, and restore safety before patching")
    with dpg.tooltip(parent="button_select_mods"):
        dpg.add_text("Open the Mod Library workspace")
    with dpg.tooltip(parent="nav_d2pfx_button"):
        dpg.add_text("Open the D2PFX browser")
    with dpg.tooltip(parent="nav_settings_button"):
        dpg.add_text("Open Minify settings")
    with dpg.tooltip(parent="nav_restore_button"):
        dpg.add_text("Restore an automatic pre-patch backup")
    with dpg.tooltip(parent="button_refresh_main"):
        dpg.add_text("Rescan mod folders for additions or changes")
    with dpg.tooltip(parent="button_uninstall"):
        dpg.add_text("Remove Minify-managed changes from Dota 2")
    with dpg.tooltip(parent="button_git"):
        dpg.add_text("Minify website")
    with dpg.tooltip(parent="button_discord"):
        dpg.add_text("Discord")
    with dpg.tooltip(parent="button_telegram"):
        dpg.add_text("Telegram")
    with dpg.tooltip(parent="button_dev"):
        dpg.add_text("Developer tools")

    # Combined Modal Popup
    dpg.add_window(
        modal=True,
        no_move=True,
        tag="modal_popup",
        show=False,
        no_collapse=True,
        no_close=True,
        no_saved_settings=True,
        autosize=True,
        no_resize=True,
        no_title_bar=True,
        no_scrollbar=True,
    )
    dpg.add_group(tag="modal_text_wrapper", parent="modal_popup")
    dpg.add_group(tag="modal_progress_wrapper", parent="modal_popup", show=False)
    dpg.add_progress_bar(tag="modal_progress", parent="modal_progress_wrapper", width=-1)
    dpg.add_text("", tag="modal_progress_status", parent="modal_progress_wrapper")
    dpg.add_group(
        parent="modal_popup",
        tag="modal_button_wrapper",
        horizontal=True,
        horizontal_spacing=10,
    )

    dpg.add_window(
        tag="mod_menu",
        label=localization.mod_selection_window_var,
        pos=(0, 0),
        menubar=False,
        no_title_bar=False,
        no_move=True,
        no_collapse=True,
        no_close=False,
        no_open_over_existing_popup=True,
        show=False,
        no_resize=True,
        no_saved_settings=True,
        width=base.main_window_width,
        height=base.main_window_height,
        on_close=checkboxes.save,
    )

    dpg.add_window(
        modal=False,
        pos=(0, 0),
        tag="settings_menu",
        label="Settings",
        menubar=False,
        no_title_bar=False,
        no_move=True,
        no_collapse=True,
        no_close=False,
        no_open_over_existing_popup=True,
        height=base.main_window_height,
        width=base.main_window_width,
        show=False,
        no_resize=True,
        no_saved_settings=True,
    )

    dpg.add_child_window(
        parent="settings_menu", tag="settings_scroll", height=-64, width=-1, border=False, no_scrollbar=False
    )
    settings.render_menu(parent="settings_scroll")
    dpg.add_child_window(
        parent="settings_menu",
        tag="settings_actions_bar",
        height=60,
        width=-1,
        border=False,
        no_scrollbar=True,
        no_scroll_with_mouse=True,
    )
    with dpg.group(horizontal=True, parent="settings_actions_bar", tag="settings_buttons_group"):
        dpg.add_button(tag="settings_save_button", label="Save changes", callback=settings.save, width=132)
        dpg.add_button(tag="settings_refresh_button", label="Reload", callback=settings.refresh, width=96)
        dpg.add_button(tag="settings_reset_button", label="Reset options", callback=settings.reset, width=138)


def create_base_ui():
    localization.get_available()
    create_ui()
    with gui.interactive_lock():
        theme.enable_dark_titlebar()
        window.focus()
        theme.apply()
        localization.change(init=True)
        gui.start_text()
        modals.Update.check()
        modals.Announcements.check()
        gui.initiate_conditionals()
        conditions.disable_workshop_mods()
        if not conditions.workshop_installed and not config.get("workshop_modal_shown", False):
            modals.WorkshopTools.show()
        if not config.get("language_modal_shown", False):
            modals.LanguageSetup.show()
        time.sleep(0.05)
        helper.bulk_exec_script("initial", False)
        checkboxes.setup_state()
    with dpg.item_handler_registry(tag="widget_handler"):
        dpg.add_item_resize_handler(callback=window.on_resize)
    dpg.bind_item_handler_registry("primary_window", "widget_handler")
    window.on_resize()


fonts.register(config.get("locale", "EN"))


with dpg.handler_registry():
    dpg.add_mouse_drag_handler(tag="drag_handler", button=0, threshold=4, callback=window.drag)
    dpg.add_mouse_release_handler(button=0, callback=window.stop_drag)
    dpg.add_key_release_handler(dpg.mvKey_Escape, callback=gui.close_active_window)

    def focus_mod_search():
        if dpg.does_item_exist("mod_menu") and dpg.is_item_shown("mod_menu") and dpg.does_item_exist("mod_search"):
            dpg.focus_item("mod_search")

    def maybe_focus_mod_search(sender, app_data, user_data):
        if dpg.is_key_down(dpg.mvKey_Control):
            focus_mod_search()

    dpg.add_key_press_handler(dpg.mvKey_F, callback=maybe_focus_mod_search)

    def modal_accept():
        from ui import modal_shared

        if dpg.is_item_shown("modal_popup") and modal_shared.active_modal_callback:
            modal_shared.active_modal_callback()

    dpg.add_key_release_handler(dpg.mvKey_Return, callback=modal_accept)

with dpg.texture_registry(show=False):
    w, h, _, d = dpg.load_image(os.path.join(base.img_dir, "Discord.png"))
    dpg.add_static_texture(width=w, height=h, default_value=d, tag="discord_texture_tag")

    w, h, _, d = dpg.load_image(os.path.join(base.img_dir, "github.png"))
    dpg.add_static_texture(width=w, height=h, default_value=d, tag="git_texture_tag")

    w, h, _, d = dpg.load_image(os.path.join(base.img_dir, "cog-wheel.png"))
    dpg.add_static_texture(width=w, height=h, default_value=d, tag="settings_texture_tag")

    w, h, _, d = dpg.load_image(os.path.join(base.img_dir, "dev.png"))
    dpg.add_static_texture(width=w, height=h, default_value=d, tag="dev_texture_tag")

    w, h, _, d = dpg.load_image(os.path.join(base.img_dir, "telegram.png"))
    dpg.add_static_texture(width=w, height=h, default_value=d, tag="telegram_texture_tag")

    w, h, _, d = dpg.load_image(os.path.join(base.img_dir, "refresh.png"))
    dpg.add_static_texture(width=w, height=h, default_value=d, tag="refresh_texture_tag")

    w, h, _, d = dpg.load_image(os.path.join(base.img_dir, "d2pfx.png"))
    dpg.add_static_texture(width=w, height=h, default_value=d, tag="d2pfx_texture_tag")

# Creating_main_viewport

viewport_width = max(760, base.main_window_width, config.get("window_width", base.main_window_width))
viewport_height = max(580, base.main_window_height, config.get("window_height", base.main_window_height))

shared.viewport_width = viewport_width
shared.viewport_height = viewport_height

dpg.create_viewport(
    title=base.TITLE,
    width=viewport_width,
    height=viewport_height,
    min_width=max(760, base.main_window_width),
    min_height=max(580, base.main_window_height),
    x_pos=min(gui.widths) // 2 - viewport_width // 2,
    y_pos=max(0, min(gui.heights) // 2 - viewport_height // 2 - 120),
    resizable=True,
    decorated=True,
    vsync=True,
    clear_color=(0, 0, 0, 255),
)

dpg.set_frame_callback(1, callback=create_base_ui)  # On first frame execute app_start

dpg.set_viewport_small_icon("./bin/images/favicon.ico")
dpg.set_viewport_large_icon("./bin/images/favicon.ico")
dpg.setup_dearpygui()
dpg.show_viewport()
try:
    dpg.start_dearpygui()
except KeyboardInterrupt:
    pass

if shared.viewport_width > 0:
    config.set("window_width", shared.viewport_width)
if shared.viewport_height > 0:
    config.set("window_height", shared.viewport_height)

dpg.destroy_context()
