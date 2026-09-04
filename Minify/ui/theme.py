"DPG theming and platform specific theme hacks"

import ctypes

import dearpygui.dearpygui as dpg
from core import base, utils

# v21.2: Obsidian Ember depth pass.
# Near-black structure and warm text remain, but raised controls now use a
# light upper edge plus a deep border shadow while text inputs stay recessed.
# The bevel is deliberately restrained: tight corners, 1 px edges, no gloss.
BACKGROUND = (9, 12, 18, 255)
BACKGROUND_DEEP = (5, 7, 11, 255)
SURFACE = (16, 22, 31, 255)
SURFACE_ALT = (24, 32, 43, 255)
SURFACE_RAISED = (31, 40, 52, 255)
SURFACE_RECESSED = (11, 15, 21, 255)
SURFACE_HOVER = (42, 54, 70, 255)
SURFACE_ACTIVE = (17, 23, 31, 255)
SURFACE_WARM = (38, 26, 28, 255)
BORDER = (57, 72, 91, 255)
BORDER_SOFT = (34, 44, 57, 255)
BEVEL_LIGHT = (78, 93, 114, 255)
BEVEL_DARK = (2, 4, 7, 255)
BEVEL_EMBER = (255, 144, 104, 255)
TEXT = (248, 244, 235, 255)
MUTED = (153, 166, 182, 255)
MUTED_DARK = (91, 101, 115, 255)
ACCENT = (236, 103, 72, 255)
ACCENT_HOVER = (255, 132, 92, 255)
ACCENT_ACTIVE = (204, 79, 54, 255)
ACCENT_MUTED = (111, 59, 50, 255)
HIGHLIGHT = (229, 183, 105, 255)
D2PFX = (90, 197, 188, 255)
VPK = (139, 190, 127, 255)
DANGER = (205, 73, 87, 255)
DANGER_HOVER = (233, 94, 107, 255)
WARNING = (230, 177, 73, 255)
SUCCESS = (101, 196, 133, 255)

settings_theme = 0


def apply():
    global settings_theme

    with dpg.theme() as global_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=9, y=8)
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, x=8, y=6)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, x=7, y=4)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 3)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_ScrollbarRounding, 4)
            dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 4)
            dpg.add_theme_color(dpg.mvThemeCol_Text, TEXT)
            dpg.add_theme_color(dpg.mvThemeCol_TextDisabled, MUTED_DARK)
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, BACKGROUND)
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, BACKGROUND)
            dpg.add_theme_color(dpg.mvThemeCol_PopupBg, SURFACE)
            dpg.add_theme_color(dpg.mvThemeCol_Border, BEVEL_LIGHT)
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
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab, (61, 69, 82, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabHovered, (80, 90, 105, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabActive, ACCENT_MUTED)
            dpg.add_theme_color(dpg.mvThemeCol_TableBorderStrong, BEVEL_LIGHT)
            dpg.add_theme_color(dpg.mvThemeCol_TableBorderLight, BORDER_SOFT)
            dpg.add_theme_color(dpg.mvThemeCol_TableRowBg, SURFACE_RECESSED)
            dpg.add_theme_color(dpg.mvThemeCol_TableRowBgAlt, SURFACE)
    dpg.bind_theme(global_theme)

    # Application shell: a slim identity bar, persistent navigation rail and
    # one focused workspace. Flair comes from controlled contrast, not chrome.
    with dpg.theme(tag="app_shell_header_theme"):
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, BACKGROUND_DEEP)
            dpg.add_theme_color(dpg.mvThemeCol_Border, ACCENT_MUTED)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=13, y=8)

    with dpg.theme(tag="app_nav_rail_theme"):
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (11, 16, 23, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Border, BORDER_SOFT)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 5)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=9, y=10)

    with dpg.theme(tag="app_workspace_theme"):
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, SURFACE)
            dpg.add_theme_color(dpg.mvThemeCol_Border, BEVEL_LIGHT)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 5)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=16, y=14)

    with dpg.theme(tag="app_workspace_main_theme"):
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, SURFACE)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 0)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=3, y=2)

    with dpg.theme(tag="app_workspace_side_theme"):
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (11, 16, 23, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Border, ACCENT_MUTED)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 5)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=12, y=11)

    with dpg.theme(tag="dashboard_status_panel_theme"):
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (12, 28, 30, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Border, (38, 79, 78, 255))
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 4)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=10, y=8)

    with dpg.theme(tag="activity_header_theme"):
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (11, 15, 21, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Border, BORDER_SOFT)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 4)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=10, y=6)

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
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 4)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=10, y=7)

    with dpg.theme(tag="app_nav_button_theme"):
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Text, MUTED)
            dpg.add_theme_color(dpg.mvThemeCol_Button, SURFACE_RAISED)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, SURFACE_HOVER)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, SURFACE_ACTIVE)
            dpg.add_theme_color(dpg.mvThemeCol_Border, BEVEL_LIGHT)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 2)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, x=9, y=6)

    with dpg.theme(tag="app_nav_primary_theme"):
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Text, TEXT)
            dpg.add_theme_color(dpg.mvThemeCol_Button, (38, 31, 32, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (66, 42, 40, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, ACCENT_MUTED)
            dpg.add_theme_color(dpg.mvThemeCol_Border, BEVEL_EMBER)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 2)

    with dpg.theme(tag="dashboard_title_theme"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, ACCENT_HOVER)

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
            dpg.add_theme_color(dpg.mvThemeCol_Text, (31, 18, 14, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Button, ACCENT)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, ACCENT_HOVER)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, ACCENT_ACTIVE)
            dpg.add_theme_color(dpg.mvThemeCol_Border, BEVEL_EMBER)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 3)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, x=14, y=8)
        with dpg.theme_component(dpg.mvButton, enabled_state=False):
            dpg.add_theme_color(dpg.mvThemeCol_Text, (119, 102, 96, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Button, (47, 40, 40, 255))

    with dpg.theme(tag="main_secondary_button_theme"):
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Text, TEXT)
            dpg.add_theme_color(dpg.mvThemeCol_Button, SURFACE_RAISED)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, SURFACE_HOVER)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, SURFACE_ACTIVE)
            dpg.add_theme_color(dpg.mvThemeCol_Border, BEVEL_LIGHT)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 3)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, x=12, y=7)

    # Destructive maintenance remains visually quiet until the user engages it.
    with dpg.theme(tag="danger_button_theme"):
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Text, (207, 145, 150, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Button, SURFACE)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (85, 42, 49, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, DANGER)
            dpg.add_theme_color(dpg.mvThemeCol_Border, (142, 70, 80, 255))
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 3)

    with dpg.theme() as mod_menu_theme:
        with dpg.theme_component():
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=8, y=8)
            dpg.add_theme_color(dpg.mvThemeCol_Text, TEXT)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, SURFACE_RECESSED)
            dpg.add_theme_color(dpg.mvThemeCol_Border, BEVEL_LIGHT)
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
            dpg.add_theme_color(dpg.mvThemeCol_CheckMark, (104, 76, 68, 255))

    with dpg.theme() as footer_theme:
        with dpg.theme_component():
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=4, y=2)
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, x=5, y=3)
            dpg.add_theme_color(dpg.mvThemeCol_Text, MUTED)
            dpg.add_theme_color(dpg.mvThemeCol_Button, SURFACE_RAISED)
            dpg.add_theme_color(dpg.mvThemeCol_Border, BEVEL_LIGHT)
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
            dpg.add_theme_color(dpg.mvThemeCol_Border, BEVEL_LIGHT)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=9, y=8)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 2)

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
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 3)

    with dpg.theme(tag="settings_theme") as settings_theme:
        with dpg.theme_component():
            dpg.add_theme_color(dpg.mvThemeCol_Text, TEXT)
            dpg.add_theme_color(dpg.mvThemeCol_TextDisabled, MUTED_DARK)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, SURFACE_RECESSED)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, SURFACE_HOVER)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, SURFACE_ACTIVE)
            dpg.add_theme_color(dpg.mvThemeCol_CheckMark, ACCENT)
            dpg.add_theme_color(dpg.mvThemeCol_Border, BEVEL_LIGHT)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=12, y=10)
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, x=8, y=8)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 3)

    # Library workspace rail and command strip.
    with dpg.theme(tag="mod_manager_source_rail_theme"):
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (14, 19, 26, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Border, BEVEL_LIGHT)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 2)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=7, y=8)

    with dpg.theme(tag="mod_manager_nav_theme"):
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Text, MUTED)
            dpg.add_theme_color(dpg.mvThemeCol_Button, SURFACE_RAISED)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, SURFACE_HOVER)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, SURFACE_ACTIVE)
            dpg.add_theme_color(dpg.mvThemeCol_Border, BEVEL_LIGHT)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 2)

    with dpg.theme(tag="mod_manager_nav_active_theme"):
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Text, TEXT)
            dpg.add_theme_color(dpg.mvThemeCol_Button, (53, 34, 34, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (68, 42, 40, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, ACCENT_MUTED)
            dpg.add_theme_color(dpg.mvThemeCol_Border, BEVEL_EMBER)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 2)

    with dpg.theme(tag="mod_manager_statusbar_theme"):
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, SURFACE_RECESSED)
            dpg.add_theme_color(dpg.mvThemeCol_Border, BEVEL_LIGHT)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=8, y=8)

    # Library chrome gets the same restrained depth treatment: raised command strips,
    # recessed list surfaces, and crisp 1 px bevel edges.
    with dpg.theme(tag="mod_manager_toolbar_card_theme"):
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, SURFACE_ALT)
            dpg.add_theme_color(dpg.mvThemeCol_Border, BEVEL_LIGHT)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 2)
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
        ("dashboard_status_panel", "dashboard_status_panel_theme"),
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
        "header_context",
        "workspace_eyebrow",
        "dashboard_focus_hint",
        "dashboard_status_message",
        "nav_workspace_label",
        "nav_secondary_label",
        "activity_caption",
        "dashboard_step_1",
        "dashboard_step_2",
        "dashboard_step_3",
    ):
        if dpg.does_item_exist(tag):
            dpg.bind_item_theme(tag, "dashboard_muted_theme")
    if dpg.does_item_exist("dashboard_focus_title"):
        dpg.bind_item_theme("dashboard_focus_title", "dashboard_focus_title_theme")
    for tag in ("header_badge", "dashboard_metric", "dashboard_side_title", "activity_label"):
        if dpg.does_item_exist(tag):
            dpg.bind_item_theme(tag, "dashboard_highlight_theme")
    if dpg.does_item_exist("dashboard_status_label"):
        dpg.bind_item_theme("dashboard_status_label", "dashboard_status_ready_theme")

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
