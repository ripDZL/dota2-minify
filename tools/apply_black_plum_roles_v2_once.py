from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "Minify" / "ui" / "theme.py"
CHECKS = ROOT / "Minify" / "ui" / "checkboxes.py"
D2PFX = ROOT / "Minify" / "browsers" / "d2pfx" / "ui.py"
TESTS = ROOT / "tests" / "test_modern_ui.py"


def once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"missing transform anchor: {label}")
    return text.replace(old, new, 1)


theme = THEME.read_text(encoding="utf-8")
start = theme.index("# v21.4: Plumfire Reactor release visual system.")
end = theme.index("\nsettings_theme = 0", start)
new_tokens = '''# v21.4: Black-Plum Reactor release visual system.
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
'''
theme = theme[:start] + new_tokens + theme[end:]

# Use the source program's broad field roles instead of near-black nested cards.
theme = once(
    theme,
    'with dpg.theme(tag="app_nav_rail_theme"):\n        with dpg.theme_component(dpg.mvChildWindow):\n            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, SURFACE_RECESSED)',
    'with dpg.theme(tag="app_nav_rail_theme"):\n        with dpg.theme_component(dpg.mvChildWindow):\n            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, SURFACE)',
    "nav slate",
)
theme = once(
    theme,
    'with dpg.theme(tag="app_workspace_theme"):\n        with dpg.theme_component(dpg.mvChildWindow):\n            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, SURFACE)',
    'with dpg.theme(tag="app_workspace_theme"):\n        with dpg.theme_component(dpg.mvChildWindow):\n            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, BACKGROUND)',
    "workspace plum chrome",
)
theme = once(
    theme,
    'with dpg.theme(tag="app_workspace_side_theme"):\n        with dpg.theme_component(dpg.mvChildWindow):\n            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, SURFACE_RECESSED)',
    'with dpg.theme(tag="app_workspace_side_theme"):\n        with dpg.theme_component(dpg.mvChildWindow):\n            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, BACKGROUND)',
    "side plum",
)

# Global unthemed controls become purple; green is reserved for selected/safe state.
theme = theme.replace(
    "dpg.add_theme_color(dpg.mvThemeCol_Button, SURFACE_RAISED)",
    "dpg.add_theme_color(dpg.mvThemeCol_Button, ACCENT)",
)
theme = theme.replace(
    "dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, SURFACE_HOVER)",
    "dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, ACCENT_HOVER)",
)
theme = theme.replace(
    "dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, SURFACE_ACTIVE)",
    "dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, ACCENT_ACTIVE)",
)
theme = theme.replace(
    "dpg.add_theme_color(dpg.mvThemeCol_CheckMark, ACCENT)",
    "dpg.add_theme_color(dpg.mvThemeCol_CheckMark, SUCCESS)",
)
theme = once(theme, "dpg.add_theme_color(dpg.mvThemeCol_Separator, BORDER_SOFT)", "dpg.add_theme_color(dpg.mvThemeCol_Separator, MAGENTA_MUTED)", "red divider")
theme = once(theme, "dpg.add_theme_color(dpg.mvThemeCol_SeparatorHovered, ACCENT_MUTED)", "dpg.add_theme_color(dpg.mvThemeCol_SeparatorHovered, EMBER)", "red divider hover")
theme = once(theme, "dpg.add_theme_color(dpg.mvThemeCol_SeparatorActive, ACCENT)", "dpg.add_theme_color(dpg.mvThemeCol_SeparatorActive, EMBER_HOVER)", "red divider active")

old_nav = '''    with dpg.theme(tag="app_nav_primary_theme"):
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Text, TEXT)
            dpg.add_theme_color(dpg.mvThemeCol_Button, ACCENT_MUTED)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (75, 58, 160, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, ACCENT_MUTED)
            dpg.add_theme_color(dpg.mvThemeCol_Border, BEVEL_EMBER)
'''
new_nav = '''    with dpg.theme(tag="app_nav_primary_theme"):
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Text, JSON_BASE_ALT)
            dpg.add_theme_color(dpg.mvThemeCol_Button, SUCCESS)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (146, 211, 91, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (104, 169, 53, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Border, BACKGROUND_DEEP)
'''
theme = once(theme, old_nav, new_nav, "lime active nav")

theme = theme.replace("dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (16, 25, 42, 255))", "dpg.add_theme_color(dpg.mvThemeCol_ChildBg, SURFACE_ALT)")
theme = theme.replace("dpg.add_theme_color(dpg.mvThemeCol_Border, (56, 77, 154, 255))", "dpg.add_theme_color(dpg.mvThemeCol_Border, SUCCESS)")
theme = theme.replace("dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (15, 20, 37, 255))", "dpg.add_theme_color(dpg.mvThemeCol_ChildBg, SURFACE_ALT)")
THEME.write_text(theme, encoding="utf-8")

checks = CHECKS.read_text(encoding="utf-8")n