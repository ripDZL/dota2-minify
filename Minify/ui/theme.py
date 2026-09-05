"DPG theming and platform specific theme hacks"

import ctypes

import dearpygui.dearpygui as dpg
from core import base, utils

# v21.4: Black-Plum Reactor release visual system.
# Spatial roles follow the user's original app screenshot: plum chrome, slate work
# areas, black strips, purple controls, lime selection, red dividers, gold telemetry.
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

BACKGROUND = JSON_WINDOW_BG
BACKGROUND_DEEP = JSON_BASE_ALT
SURFACE = JSON_BASE_BG
SURFACE_ALT = (74, 92, 98, 255)
SURFACE_RAISED = JSON_BUTTON_BG
SURFACE_RECESSED = (72, 89, 94, 255)
SURFACE_HOVER = (101, 122, 128, 255)
SURFACE_ACTIVE = (111, 77, 121, 255)
SURFACE_WARM = JSON_WINDOW_BG
BORDER = (42, 38, 48, 255)
BORDER_SOFT = (58, 52, 68, 255)
BEVEL_LIGHT = JSON_TEXT_DISABLED
BEVEL_DARK = (0, 0, 0, 210)
BEVEL_EMBER = JSON_ACCENT_DIVIDER
TEXT = JSON_TEXT_PRIMARY
MUTED = JSON_TEXT_PLACEHOLDER
MUTED_DARK = JSON_TEXT_DISABLED
ACCENT = JSON_BUTTON_BG
ACCENT_HOVER = (169, 98, 183, 255)
ACCENT_ACTIVE = (105, 44, 119, 255)
ACCENT_MUTED = (104, 45, 117, 255)
CYAN = JSON_ACCENT_HIGHLIGHT
CYAN_MUTED = (71, 108, 47, 255)
MAGENTA = JSON_ACCENT_DIVIDER
MAGENTA_MUTED = (130, 52, 42, 255)
EMBER = JSON_ACCENT_DIVIDER
EMBER_HOVER = (244, 102, 82, 255)
EMBER_ACTIVE = (180, 57, 43, 255)
EMBER_MUTED = (130, 52, 42, 255)
HIGHLIGHT = JSON_TEXT_BRIGHT
LINK = JSON_ACCENT_LINK
D2PFX = JSON_ACCENT_HIGHLIGHT
VPK = JSON_TEXT_BRIGHT
DANGER = JSON_ACCENT_DIVIDER
DANGER_HOVER = (244, 102, 82, 255)
WARNING = JSON_TEXT_BRIGHT
SUCCESS = JSON_ACCENT_HIGHLIGHT

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
            dpg.add_theme_color(dpg.mvThemeCol_Button, ACCENT)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, ACCENT_HOVER)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, ACCENT_ACTIVE)
            dpg.add_theme_color(dpg.mvThemeCol_CheckMark, SUCCESS)
            dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, ACCENT)
            dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, ACCENT_HOVER)
            dpg.add_theme_color(dpg.mvThemeCol_Separator, MAGENTA_MUTED)
            dpg.add_theme_color(dpg.mvThemeCol_SeparatorHovered, EMBER)
            dpg.add_theme_color(dpg.mvThemeCol_SeparatorActive, EMBER_HOVER)
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg, BACKGROUND_DEEP)
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab, (47, 55, 83, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabHovered, (68, 79, 118, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabActive, ACCENT_MUTED)
            dpg.add_theme_color(dpg.mvThemeCol_TableBorderStrong, BORDER)
            dpg.add_theme_color(dpg.mvThemeCol_TableBorderLight, BORDER_SOFT)
            dpg.add_theme_color(dpg.mvThemeCol_TableRowBg, SURFACE_RECESSED)
            dpg.add_theme_color(dpg.mvThemeCol_TableRowBgAlt, SURFACE)
    dpg.bind_theme(global_theme)

    # Application shell: plum-black depth with violet controls, ember dividers, lime state, and gold telemetry.
    with dpg.theme(tag="app_shell_header_theme"):
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, BACKGROUND_DEEP)
            dpg.add_theme_color(dpg.mvThemeCol_Border, BORDER_SOFT)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=13, y=8)

    with dpg.theme(tag="app_nav_rail_theme"):
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, SURFACE)
            dpg.add_theme_color(dpg.mvThemeCol_Border, BORDER_SOFT)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 7)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=9, y=10)

    with dpg.theme(tag="app_workspace_theme"):
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, BACKGROUND)
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
            dpg.add_theme_color(dpg.mvThemeCol_Border, ACCENT)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 7)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=11, y=10)

    with dpg.theme(tag="dashboard_safety_card_theme"):
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (20, 28, 18, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Border, CYAN_MUTED)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 7)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=11, y=10)

    with dpg.theme(tag="dashboard_safety_title_theme"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, D2PFX)

    with dpg.theme(tag="app_workspace_side_theme"):
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, BACKGROUND)
            dpg.add_theme_color(dpg.mvThemeCol_Border, BORDER_SOFT)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 7)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=12, y=11)

    with dpg.theme(tag="dashboard_status_panel_theme"):
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, SURFACE_ALT)
            dpg.add_theme_color(dpg.mvThemeCol_Border, ACCENT)
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
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, SURFACE_ALT)
            dpg.add_theme_color(dpg.mvThemeCol_Border, CYAN_MUTED)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, ACCENT_MUTED)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 8)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=10, y=6)

    with dpg.theme(tag="header_accent_rail_theme"):
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, MAGENTA)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 0)

    with dpg.theme(tag="nav_status_card_theme"):
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, SURFACE_ALT)
            dpg.add_theme_color(dpg.mvThemeCol_Border, ACCENT_MUTED)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, ACCENT_MUTED)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 7)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=9, y=6)

    with dpg.theme(tag="dashboard_metric_strip_theme"):
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, BACKGROUND_DEEP)
            dpg.add_theme_color(dpg.mvThemeCol_Border, ACCENT)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, ACCENT_MUTED)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 6)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=9, y=7)

    with dpg.theme(tag="dashboard_signal_card_theme"):
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (20, 28, 18, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Border, CYAN_MUTED)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, CYAN_MUTED)
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
            dpg.add_theme_color(dpg.mvThemeCol_Button, ACCENT)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, ACCENT_HOVER)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, ACCENT_ACTIVE)
            dpg.add_theme_color(dpg.mvThemeCol_Border, BORDER)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, x=9, y=6)

    with dpg.theme(tag="app_nav_primary_theme"):
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Text, JSON_BASE_ALT)
            dpg.add_theme_color(dpg.mvThemeCol_Button, SUCCESS)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (146, 211, 91, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (104, 169, 53, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Border, BACKGROUND_DEEP)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)

    with dpg.theme(tag="dashboard_title_theme"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, HIGHLIGHT)

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
            dpg.add_theme_color(dpg.mvThemeCol_Text, TEXT)
            dpg.add_theme_color(dpg.mvThemeCol_Button, ACCENT)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, ACCENT_HOVER)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, ACCENT_ACTIVE)
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
            dpg.add_theme_color(dpg.mvThemeCol_Button, ACCENT)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, ACCENT_HOVER)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, ACCENT_ACTIVE)
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
            dpg.add_theme_color(dpg.mvThemeCol_CheckMark, SUCCESS)
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
            dpg.add_theme_color(dpg.mvThemeCol_Button, ACCENT)
            dpg.add_theme_color(dpg.mvThemeCol_Border, BORDER)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, ACCENT_HOVER)
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
            dpg.add_theme_color(dpg.mvThemeCol_Button, ACCENT)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, ACCENT_HOVER)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, ACCENT_ACTIVE)
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
            dpg.add_theme_color(dpg.mvThemeCol_CheckMark, SUCCESS)
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
            dpg.add_theme_color(dpg.mvThemeCol_Button, ACCENT)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, ACCENT_HOVER)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, ACCENT_ACTIVE)
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
        "dashboard_step_1_detail",
        "dashboard_step_2_detail",
        "dashboard_step_3_detail",
        "signal_rollback_label",
        "signal_validation_label",
        "signal_paths_label",
    ):
        if dpg.does_item_exist(tag):
            dpg.bind_item_theme(tag, "dashboard_muted_theme")
    if dpg.does_item_exist("dashboard_focus_title"):
        dpg.bind_item_theme("dashboard_focus_title", "dashboard_focus_title_theme")
    for tag in (
        "dashboard_metric",
        "dashboard_side_title",
        "activity_label",
        "dashboard_step_1_index",
        "dashboard_step_2_index",
        "dashboard_step_3_index",
    ):
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
