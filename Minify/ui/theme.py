"DPG theming and platform specific theme hacks"

import ctypes

import dearpygui.dearpygui as dpg
from core import base, utils

# v21.4: Prismatic Foundry release visual system.
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

settings_theme = 0


def apply():
    global settings_theme

    with dpg.theme() as global_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=10, y=9)
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, x=9, y=7)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, x=9, y=5)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_ScrollbarRounding, 7)
            dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 6)
            dpg.add_theme_color(dpg.mvThemeCol_Text, TEXT)
            dpg.add_theme_color(dpg.mvThemeCol_TextDisabled, MUTED_DARK)
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, BACKGROUND)
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, BACKGROUND)
            dpg.add_theme_color(dpg.mvThemeCol_PopupBg, SURFACE)
            dpg.add_theme_color(dpg.mvThemeCol_Border, BORDER)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_color(dpg.mvThemeCol_TitleBg, BACKGROUND_DEEP)
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, BACKGROUND_DEEP)
            dpg.add_theme_color(dpg.mvThemeCol_Header, SURFACE_RAISED)
            dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, SURFACE_HOVER)
            dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, SURFACE_ACTIVE)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, SURFACE_RECESSED)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, SURFACE_HOVER)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, SURFACE_ACTIVE)
            dpg.add_theme_color(dpg.mvThemeCol_Button, SURFACE_RAISED)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, SURFACE_HOVER)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, SURFACE_ACTIVE)
            dpg.add_theme_color(dpg.mvThemeCol_CheckMark, ACCENT)
            dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, ACCENT)
            dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, ACCENT_HOVER)
            dpg.add_theme_color(dpg.mvThemeCol_Separator, BORDER_SOFT)
            dpg.add_theme_color(dpg.mvThemeCol_SeparatorHovered, ACCENT_MUTED)
            dpg.add_theme_color(dpg.mvThemeCol_SeparatorActive, ACCENT)
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg, BACKGROUND_DEEP)
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab, (47, 55, 83, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabHovered, (68, 79, 118, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabActive, ACCENT_MUTED)
            dpg.add_theme_color(dpg.mvThemeCol_TableBorderStrong, BORDER)
            dpg.add_theme_color(dpg.mvThemeCol_TableBorderLight, BORDER_SOFT)
            dpg.add_theme_color(dpg.mvThemeCol_TableRowBg, SURFACE_RECESSED)
            dpg.add_theme_color(dpg.mvThemeCol_TableRowBgAlt, SURFACE)
    dpg.bind_theme(global_theme)

    # Application shell: compact flat-dark chrome with crimson focus and inset controls.
    with dpg.theme(tag="app_shell_header_theme"):
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, BACKGROUND_DEEP)
            dpg.add_theme_color(dpg.mvThemeCol_Border, BORDER_SOFT)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=13, y=8)

    with dpg.theme(tag="app_nav_rail_theme"):
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, SURFACE_RECESSED)
            dpg.add_theme_color(dpg.mvThemeCol_Border, BORDER_SOFT)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 7)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=9, y=10)

    with dpg.theme(tag="app_workspace_theme"):
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, SURFACE)
            dpg.add_theme_color(dpg.mvThemeCol_Border, BORDER)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 7)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=16, y=14)

    with dpg.theme(tag="app_workspace_main_theme"):
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, SURFACE)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 0)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=3, y=2)

    with dpg.theme(tag="dashboard_hero_card_theme"):
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, SURFACE_ALT)
            dpg.add_theme_color(dpg.mvThemeCol_Border, ACCENT_MUTED)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 7)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=14, y=11)

    with dpg.theme(tag="dashboard_action_bar_theme"):
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, SURFACE_RECESSED)
            dpg.add_theme_color(dpg.mvThemeCol_Border, BORDER_SOFT)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 7)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=9, y=8)

    with dpg.theme(tag="dashboard_flow_card_theme"):
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, SURFACE_ALT)
            dpg.add_theme_color(dpg.mvThemeCol_Border, (76, 59, 163, 255))
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 7)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=11, y=10)

    with dpg.theme(tag="dashboard_safety_card_theme"):
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (10, 25, 31, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Border, (31, 114, 126, 255))
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 7)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=11, y=10)

    with dpg.theme(tag="dashboard_safety_title_theme"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, D2PFX)

    with dpg.theme(tag="app_workspace_side_theme"):
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, SURFACE_RECESSED)
            dpg.add_theme_color(dpg.mvThemeCol_Border, BORDER_SOFT)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 7)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=12, y=11)

    with dpg.theme(tag="dashboard_status_panel_theme"):
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (16, 25, 42, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Border, (56, 77, 154, 255))
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 7)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=10, y=8)

    with dpg.theme(tag="activity_header_theme"):
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, BACKGROUND_DEEP)
            dpg.add_theme_color(dpg.mvThemeCol_Border, BORDER_SOFT)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 7)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=10, y=6)

    with dpg.theme(tag="header_engine_chip_theme"):
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

    with dpg.theme(tag="settings_scroll_theme"):
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, BACKGROUND)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 0)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=12, y=10)

    with dpg.theme(tag="settings_actions_bar_theme"):
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, BACKGROUND_DEEP)
            dpg.add_theme_color(dpg.mvThemeCol_Border, BORDER_SOFT)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 7)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=10, y=7)

    with dpg.theme(tag="app_nav_button_theme"):
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Text, MUTED)
            dpg.add_theme_color(dpg.mvThemeCol_Button, SURFACE_RAISED)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, SURFACE_HOVER)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, SURFACE_ACTIVE)
            dpg.add_theme_color(dpg.mvThemeCol_Border, BORDER)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, x=9, y=6)

    with dpg.theme(tag="app_nav_primary_theme"):
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Text, TEXT)
            dpg.add_theme_color(dpg.mvThemeCol_Button, ACCENT_MUTED)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (75, 58, 160, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, ACCENT_MUTED)
            dpg.add_theme_color(dpg.mvThemeCol_Border, BEVEL_EMBER)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)

    with dpg.theme(tag="dashboard_title_theme"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, EMBER_HOVER)

    with dpg.theme(tag="dashboard_product_theme"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, TEXT)

    with dpg.theme(tag="dashboard_highlight_theme"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, HIGHLIGHT)

    with dpg.theme(tag="dashboard_muted_theme"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, MUTED)

    with dpg.theme(tag="dashboard_focus_title_theme"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, TEXT)

    with dpg.theme(tag="dashboard_status_ready_theme"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, D2PFX)

    with dpg.theme(tag="dashboard_status_working_theme"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, ACCENT_HOVER)

    with dpg.theme(tag="dashboard_status_warning_theme"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, WARNING)

    with dpg.theme(tag="dashboard_status_error_theme"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, DANGER_HOVER)

    with dpg.theme(tag="dashboard_status_success_theme"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, SUCCESS)

    with dpg.theme(tag="main_primary_button_theme"):
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Text, (25, 13, 10, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Button, EMBER)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, EMBER_HOVER)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, EMBER_ACTIVE)
            dpg.add_theme_color(dpg.mvThemeCol_Border, BEVEL_EMBER)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, x=14, y=8)
        with dpg.theme_component(dpg.mvButton, enabled_state=False):
            dpg.add_theme_color(dpg.mvThemeCol_Text, MUTED_DARK)
            dpg.add_theme_color(dpg.mvThemeCol_Button, SURFACE_ALT)

    with dpg.theme(tag="main_secondary_button_theme"):
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Text, TEXT)
            dpg.add_theme_color(dpg.mvThemeCol_Button, SURFACE_RAISED)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, SURFACE_HOVER)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, SURFACE_ACTIVE)
            dpg.add_theme_color(dpg.mvThemeCol_Border, BORDER)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, x=12, y=7)

    # Destructive maintenance remains visually quiet until the user engages it.
    with dpg.theme(tag="danger_button_theme"):
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Text, (211, 155, 170, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Button, SURFACE)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (88, 37, 55, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, DANGER)
            dpg.add_theme_color(dpg.mvThemeCol_Border, (151, 62, 87, 255))
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)

    with dpg.theme() as mod_menu_theme:
        with dpg.theme_component():
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=8, y=8)
            dpg.add_theme_color(dpg.mvThemeCol_Text, TEXT)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, SURFACE_RECESSED)
            dpg.add_theme_color(dpg.mvThemeCol_Border, BORDER)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1)
            dpg.add_theme_color(dpg.mvThemeCol_CheckMark, ACCENT)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, SURFACE_HOVER)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, SURFACE_ACTIVE)
        with dpg.theme_component(dpg.mvCheckbox, enabled_state=False):
            dpg.add_theme_color(dpg.mvThemeCol_Text, MUTED_DARK)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, SURFACE)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, SURFACE)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, SURFACE)
            dpg.add_theme_color(dpg.mvThemeCol_CheckMark, MUTED_DARK)

    with dpg.theme() as footer_theme:
        with dpg.theme_component():
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=4, y=2)
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, x=5, y=3)
            dpg.add_theme_color(dpg.mvThemeCol_Text, MUTED)
            dpg.add_theme_color(dpg.mvThemeCol_Button, SURFACE_RAISED)
            dpg.add_theme_color(dpg.mvThemeCol_Border, BORDER)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, SURFACE_HOVER)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, SURFACE_ALT)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, SURFACE_RECESSED)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, SURFACE_HOVER)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, SURFACE_ACTIVE)
        with dpg.theme_component(enabled_state=False):
            dpg.add_theme_color(dpg.mvThemeCol_Text, MUTED_DARK)
            dpg.add_theme_color(dpg.mvThemeCol_Button, BACKGROUND)

    with dpg.theme() as terminal_theme:
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, BACKGROUND_DEEP)
            dpg.add_theme_color(dpg.mvThemeCol_Border, BORDER)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=10, y=9)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 7)

    with dpg.theme() as popup_theme:
        with dpg.theme_component():
            dpg.add_theme_color(dpg.mvThemeCol_Text, TEXT)
            dpg.add_theme_color(dpg.mvThemeCol_Button, SURFACE_RAISED)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, SURFACE_HOVER)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, SURFACE_ACTIVE)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, SURFACE_RECESSED)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, SURFACE_HOVER)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, SURFACE_ACTIVE)
            dpg.add_theme_color(dpg.mvThemeCol_Border, BEVEL_EMBER)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1)
            dpg.add_theme_color(dpg.mvThemeCol_ModalWindowDimBg, (2, 3, 5, 215))
            dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=18, y=16)
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, x=9, y=8)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)

    with dpg.theme(tag="settings_theme") as settings_theme:
        with dpg.theme_component():
            dpg.add_theme_color(dpg.mvThemeCol_Text, TEXT)
            dpg.add_theme_color(dpg.mvThemeCol_TextDisabled, MUTED_DARK)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, SURFACE_RECESSED)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, SURFACE_HOVER)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, SURFACE_ACTIVE)
            dpg.add_theme_color(dpg.mvThemeCol_CheckMark, ACCENT)
            dpg.add_theme_color(dpg.mvThemeCol_Border, BORDER)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=12, y=10)
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, x=8, y=8)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)

    # Library workspace rail and command strip.
    with dpg.theme(tag="mod_manager_source_rail_theme"):
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, SURFACE_RECESSED)
            dpg.add_theme_color(dpg.mvThemeCol_Border, BORDER)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 7)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=7, y=8)

    with dpg.theme(tag="mod_manager_nav_theme"):
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Text, MUTED)
            dpg.add_theme_color(dpg.mvThemeCol_Button, SURFACE_RAISED)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, SURFACE_HOVER)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, SURFACE_ACTIVE)
            dpg.add_theme_color(dpg.mvThemeCol_Border, BORDER)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)

    with dpg.theme(tag="mod_manager_nav_active_theme"):
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Text, TEXT)
            dpg.add_theme_color(dpg.mvThemeCol_Button, ACCENT_MUTED)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (75, 58, 160, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, ACCENT_MUTED)
            dpg.add_theme_color(dpg.mvThemeCol_Border, BEVEL_EMBER)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)

    with dpg.theme(tag="mod_manager_statusbar_theme"):
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, SURFACE_RECESSED)
            dpg.add_theme_color(dpg.mvThemeCol_Border, BORDER)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=8, y=8)

    # Library chrome gets the same restrained depth treatment: raised command strips,
    # recessed list surfaces, and crisp 1 px bevel edges.
    with dpg.theme(tag="mod_manager_toolbar_card_theme"):
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, SURFACE_ALT)
            dpg.add_theme_color(dpg.mvThemeCol_Border, BORDER)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 7)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=10, y=7)

    with dpg.theme(tag="mod_manager_status_badge_theme"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, ACCENT_HOVER)

    # Bind the rebuilt application shell.
    for tag, theme_tag in (
        ("app_shell_header", "app_shell_header_theme"),
        ("app_nav_rail", "app_nav_rail_theme"),
        ("app_workspace", "app_workspace_theme"),
        ("app_workspace_main", "app_workspace_main_theme"),
        ("app_workspace_side", "app_workspace_side_theme"),
        ("dashboard_hero_card", "dashboard_hero_card_theme"),
        ("dashboard_action_bar", "dashboard_action_bar_theme"),
        ("dashboard_flow_card", "dashboard_flow_card_theme"),
        ("dashboard_safety_card", "dashboard_safety_card_theme"),
        ("dashboard_status_panel", "dashboard_status_panel_theme"),
        ("header_engine_chip", "header_engine_chip_theme"),
        ("header_accent_rail", "header_accent_rail_theme"),
        ("nav_status_card", "nav_status_card_theme"),
        ("dashboard_metric_strip", "dashboard_metric_strip_theme"),
        ("dashboard_signal_card", "dashboard_signal_card_theme"),
        ("activity_header", "activity_header_theme"),
        ("settings_scroll", "settings_scroll_theme"),
        ("settings_actions_bar", "settings_actions_bar_theme"),
    ):
        if dpg.does_item_exist(tag):
            dpg.bind_item_theme(tag, theme_tag)
    if dpg.does_item_exist("app_title"):
        dpg.bind_item_theme("app_title", "dashboard_title_theme")
    if dpg.does_item_exist("app_product_name"):
        dpg.bind_item_theme("app_product_name", "dashboard_product_theme")
    for tag in (
        "app_version",
        "workspace_eyebrow",
        "dashboard_focus_hint",
        "dashboard_status_message",
        "nav_workspace_label",
        "nav_secondary_label",
        "activity_caption",
        "dashboard_step_1",
        "dashboard_step_2",
        "dashboard_step_3",
        "dashboard_action_label",
        "nav_status_title",
        "header_engine_label",
    ):
        if dpg.does_item_exist(tag):
            dpg.bind_item_theme(tag, "dashboard_muted_theme")
    if dpg.does_item_exist("dashboard_focus_title"):
        dpg.bind_item_theme("dashboard_focus_title", "dashboard_focus_title_theme")
    for tag in ("dashboard_metric", "dashboard_side_title", "activity_label"):
        if dpg.does_item_exist(tag):
            dpg.bind_item_theme(tag, "dashboard_highlight_theme")
    if dpg.does_item_exist("dashboard_status_label"):
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

    if dpg.does_item_exist("dashboard_safety_title"):
        dpg.bind_item_theme("dashboard_safety_title", "dashboard_safety_title_theme")
    if dpg.does_item_exist("dashboard_safety_text"):
        dpg.bind_item_theme("dashboard_safety_text", "dashboard_muted_theme")

    if dpg.does_item_exist("button_patch"):
        dpg.bind_item_theme("button_patch", "main_primary_button_theme")
    if dpg.does_item_exist("button_refresh_main"):
        dpg.bind_item_theme("button_refresh_main", "main_secondary_button_theme")
    if dpg.does_item_exist("nav_patch_button"):
        dpg.bind_item_theme("nav_patch_button", "app_nav_primary_theme")
    for tag in ("button_select_mods", "nav_d2pfx_button", "nav_settings_button"):
        if dpg.does_item_exist(tag):
            dpg.bind_item_theme(tag, "app_nav_button_theme")
    for tag in ("nav_restore_button",):
        if dpg.does_item_exist(tag):
            dpg.bind_item_theme(tag, "app_nav_button_theme")
    if dpg.does_item_exist("button_uninstall"):
        dpg.bind_item_theme("button_uninstall", "danger_button_theme")

    for tag, theme_tag in (
        ("d2pfx_browser_eyebrow", "dashboard_title_theme"),
        ("d2pfx_browser_heading", "dashboard_product_theme"),
        ("d2pfx_browser_subtitle", "dashboard_muted_theme"),
    ):
        if dpg.does_item_exist(tag):
            dpg.bind_item_theme(tag, theme_tag)

    if dpg.does_item_exist("settings_eyebrow"):
        dpg.bind_item_theme("settings_eyebrow", "dashboard_title_theme")
    for tag in ("settings_intro",):
        if dpg.does_item_exist(tag):
            dpg.bind_item_theme(tag, "dashboard_muted_theme")
    if dpg.does_item_exist("settings_save_button"):
        dpg.bind_item_theme("settings_save_button", "main_primary_button_theme")
    for tag in ("settings_refresh_button", "settings_reset_button"):
        if dpg.does_item_exist(tag):
            dpg.bind_item_theme(tag, "main_secondary_button_theme")

    dpg.bind_item_theme("mod_menu", mod_menu_theme)
    dpg.bind_item_theme("footer", footer_theme)
    dpg.bind_item_theme("settings_menu", settings_theme)
    dpg.bind_item_theme("modal_popup", popup_theme)
    dpg.bind_item_theme("terminal_window", terminal_theme)


def enable_dark_titlebar():
    if base.is_win:
        with utils.try_pass():
            hwnd = ctypes.windll.user32.FindWindowW(None, base.TITLE)
            if hwnd != 0:
                value = ctypes.c_int(1)
                ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(value), ctypes.sizeof(value))
