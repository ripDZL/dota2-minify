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
        # v21.4 responsive command console. Keep the home surface focused on
        # actions, live state, and the patch sequence rather than static help.
        dpg.add_child_window(
            tag="app_shell_header",
            height=76,
            autosize_x=True,
            border=True,
            no_scrollbar=True,
            no_scroll_with_mouse=True,
        )
        with dpg.table(
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
                dpg.add_spacer(width=1)

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
            height=380,
            border=True,
            no_scrollbar=True,
            no_scroll_with_mouse=True,
        )
        dpg.add_text("COMMAND DECK", parent="app_nav_rail", tag="nav_workspace_label")
        dpg.add_child_window(
            parent="app_nav_rail",
            tag="nav_status_card",
            width=-1,
            height=66,
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
            height=380,
            border=True,
            no_scrollbar=True,
            no_scroll_with_mouse=True,
        )
        with dpg.group(parent="app_workspace", tag="workspace_columns"):
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
                height=168,
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
            dpg.add_spacer(parent="dashboard_hero_card", height=3)
            dpg.add_child_window(
                parent="dashboard_hero_card",
                tag="dashboard_metric_strip",
                height=66,
                width=-1,
                border=True,
                no_scrollbar=True,
                no_scroll_with_mouse=True,
            )
            with dpg.table(parent="dashboard_metric_strip", tag="dashboard_metric_table", header_row=False, width=-1):
                dpg.add_table_column(width_fixed=True, init_width_or_weight=28)
                dpg.add_table_column(width_fixed=True, init_width_or_weight=92)
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
                    dpg.add_text("Selected mods", tag="dashboard_step_3_detail")

            dpg.add_child_window(
                parent="app_workspace_main",
                tag="dashboard_status_panel",
                height=60,
                width=-1,
                border=True,
                no_scrollbar=True,
                no_scroll_with_mouse=True,
            )
            with dpg.group(parent="dashboard_status_panel", horizontal=True):
                dpg.add_text("● READY", tag="dashboard_status_label")
                dpg.add_text("Getting your mod library ready...", tag="dashboard_status_message", wrap=420)
            dpg.add_text("0 selected • 0 installed", parent="dashboard_status_panel", tag="dashboard_metric")

            dpg.add_child_window(
                parent="app_workspace_main",
                tag="dashboard_action_bar",
                height=76,
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

        dpg.add_spacer(height=8)
        dpg.add_child_window(
            tag="activity_header",
            height=36,
            autosize_x=True,
            border=True,
            no_scrollbar=True,
            no_scroll_with_mouse=True,
        )
        dpg.add_text("ACTIVITY LOG", parent="activity_header", tag="activity_label")

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

MIN_VIEWPORT_WIDTH = 960
MIN_VIEWPORT_HEIGHT = 680

viewport_width = max(MIN_VIEWPORT_WIDTH, base.main_window_width, config.get("window_width", base.main_window_width))
viewport_height = max(
    MIN_VIEWPORT_HEIGHT, base.main_window_height, config.get("window_height", base.main_window_height)
)

shared.viewport_width = viewport_width
shared.viewport_height = viewport_height

dpg.create_viewport(
    title=base.TITLE,
    width=viewport_width,
    height=viewport_height,
    min_width=MIN_VIEWPORT_WIDTH,
    min_height=MIN_VIEWPORT_HEIGHT,
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
