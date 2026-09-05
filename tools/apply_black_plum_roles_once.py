from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "Minify" / "ui" / "theme.py"
CHECKS = ROOT / "Minify" / "ui" / "checkboxes.py"
D2PFX = ROOT / "Minify" / "browsers" / "d2pfx" / "ui.py"
TESTS = ROOT / "tests" / "test_modern_ui.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"missing transform anchor: {label}")
    return text.replace(old, new, 1)


theme = THEME.read_text(encoding="utf-8")
old = '''# v21.4: Plumfire Reactor release visual system.\n# Exact role anchors from the user-supplied theme JSON. Derived dark shades only\n# extend those tokens for depth; primary interaction/state colors stay faithful.\nJSON_ACCENT_DIVIDER = (223, 80, 59, 255)  # #df503b\nJSON_ACCENT_HIGHLIGHT = (122, 193, 67, 255)  # #7ac143\nJSON_ACCENT_LINK = (255, 255, 0, 255)  # #ffff00\nJSON_BASE_ALT = (0, 0, 0, 255)  # #000000\nJSON_BASE_BG = (88, 108, 114, 255)  # #586c72\nJSON_BUTTON_BG = (133, 56, 148, 255)  # #853894\nJSON_TEXT_BRIGHT = (255, 195, 15, 255)  # #ffc30f\nJSON_TEXT_DISABLED = (164, 143, 123, 255)  # #a48f7b\nJSON_TEXT_PLACEHOLDER = (217, 199, 176, 255)  # #d9c7b0\nJSON_TEXT_PRIMARY = (247, 240, 231, 255)  # #f7f0e7\nJSON_WINDOW_BG = (70, 51, 90, 255)  # #46335a\n\nBACKGROUND = (12, 9, 17, 255)\nBACKGROUND_DEEP = JSON_BASE_ALT\nSURFACE = (25, 19, 33, 255)\nSURFACE_ALT = (37, 27, 48, 255)\nSURFACE_RAISED = (50, 37, 64, 255)\nSURFACE_RECESSED = (17, 13, 23, 255)\nSURFACE_HOVER = JSON_WINDOW_BG\nSURFACE_ACTIVE = (58, 44, 70, 255)\nSURFACE_WARM = (45, 27, 31, 255)\nBORDER = JSON_BASE_BG\nBORDER_SOFT = (53, 61, 68, 255)\nBEVEL_LIGHT = JSON_TEXT_DISABLED\nBEVEL_DARK = (0, 0, 0, 220)\nBEVEL_EMBER = JSON_ACCENT_DIVIDER\nTEXT = JSON_TEXT_PRIMARY\nMUTED = JSON_TEXT_PLACEHOLDER\nMUTED_DARK = JSON_TEXT_DISABLED\nACCENT = JSON_BUTTON_BG\nACCENT_HOVER = (169, 83, 184, 255)\nACCENT_ACTIVE = (104, 39, 118, 255)\nACCENT_MUTED = JSON_WINDOW_BG\n# Compatibility aliases keep existing theme wiring stable while changing roles.\nCYAN = JSON_ACCENT_HIGHLIGHT\nCYAN_MUTED = (49, 79, 33, 255)\nMAGENTA = JSON_ACCENT_DIVIDER\nMAGENTA_MUTED = (96, 38, 31, 255)\nEMBER = JSON_ACCENT_DIVIDER\nEMBER_HOVER = (244, 102, 82, 255)\nEMBER_ACTIVE = (180, 57, 43, 255)\nEMBER_MUTED = (96, 38, 31, 255)\nHIGHLIGHT = JSON_TEXT_BRIGHT\nLINK = JSON_ACCENT_LINK\nD2PFX = JSON_ACCENT_HIGHLIGHT\nVPK = JSON_TEXT_BRIGHT\nDANGER = JSON_ACCENT_DIVIDER\nDANGER_HOVER = (244, 102, 82, 255)\nWARNING = JSON_TEXT_BRIGHT\nSUCCESS = JSON_ACCENT_HIGHLIGHT\n'''
new = '''# v21.4: Black-Plum Reactor release visual system.\n# The user's source screenshot establishes spatial roles for the supplied JSON:\n# plum chrome, slate work areas, black strips, purple controls, lime selection,\n# red dividers, gold telemetry, yellow links, and warm-ivory body text.\nJSON_ACCENT_DIVIDER = (223, 80, 59, 255)  # #df503b\nJSON_ACCENT_HIGHLIGHT = (122, 193, 67, 255)  # #7ac143\nJSON_ACCENT_LINK = (255, 255, 0, 255)  # #ffff00\nJSON_BASE_ALT = (0, 0, 0, 255)  # #000000\nJSON_BASE_BG = (88, 108, 114, 255)  # #586c72\nJSON_BUTTON_BG = (133, 56, 148, 255)  # #853894\nJSON_TEXT_BRIGHT = (255, 195, 15, 255)  # #ffc30f\nJSON_TEXT_DISABLED = (164, 143, 123, 255)  # #a48f7b\nJSON_TEXT_PLACEHOLDER = (217, 199, 176, 255)  # #d9c7b0\nJSON_TEXT_PRIMARY = (247, 240, 231, 255)  # #f7f0e7\nJSON_WINDOW_BG = (70, 51, 90, 255)  # #46335a\n\nBACKGROUND = JSON_WINDOW_BG\nBACKGROUND_DEEP = JSON_BASE_ALT\nSURFACE = JSON_BASE_BG\nSURFACE_ALT = (74, 92, 98, 255)\nSURFACE_RAISED = JSON_BUTTON_BG\nSURFACE_RECESSED = (72, 89, 94, 255)\nSURFACE_HOVER = (101, 122, 128, 255)\nSURFACE_ACTIVE = (111, 77, 121, 255)\nSURFACE_WARM = JSON_WINDOW_BG\nBORDER = (42, 38, 48, 255)\nBORDER_SOFT = (58, 52, 68, 255)\nBEVEL_LIGHT = JSON_TEXT_DISABLED\nBEVEL_DARK = (0, 0, 0, 210)\nBEVEL_EMBER = JSON_ACCENT_DIVIDER\nTEXT = JSON_TEXT_PRIMARY\nMUTED = JSON_TEXT_PLACEHOLDER\nMUTED_DARK = JSON_TEXT_DISABLED\nACCENT = JSON_BUTTON_BG\nACCENT_HOVER = (169, 98, 183, 255)\nACCENT_ACTIVE = (105, 44, 119, 255)\nACCENT_MUTED = (104, 45, 117, 255)\n# Compatibility aliases keep existing theme wiring stable while changing roles.\nCYAN = JSON_ACCENT_HIGHLIGHT\nCYAN_MUTED = (71, 108, 47, 255)\nMAGENTA = JSON_ACCENT_DIVIDER\nMAGENTA_MUTED = (130, 52, 42, 255)\nEMBER = JSON_ACCENT_DIVIDER\nEMBER_HOVER = (244, 102, 82, 255)\nEMBER_ACTIVE = (180, 57, 43, 255)\nEMBER_MUTED = (130, 52, 42, 255)\nHIGHLIGHT = JSON_TEXT_BRIGHT\nLINK = JSON_ACCENT_LINK\nD2PFX = JSON_ACCENT_HIGHLIGHT\nVPK = JSON_TEXT_BRIGHT\nDANGER = JSON_ACCENT_DIVIDER\nDANGER_HOVER = (244, 102, 82, 255)\nWARNING = JSON_TEXT_BRIGHT\nSUCCESS = JSON_ACCENT_HIGHLIGHT\n'''
theme = replace_once(theme, old, new, "theme token block")

# Global widgets follow the source program: purple controls, slate fields, red dividers.
theme = theme.replace("dpg.add_theme_color(dpg.mvThemeCol_Button, SURFACE_RAISED)", "dpg.add_theme_color(dpg.mvThemeCol_Button, ACCENT)")
theme = theme.replace("dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, SURFACE_HOVER)", "dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, ACCENT_HOVER)")
theme = theme.replace("dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, SURFACE_ACTIVE)", "dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, ACCENT_ACTIVE)")
theme = theme.replace("dpg.add_theme_color(dpg.mvThemeCol_CheckMark, ACCENT)", "dpg.add_theme_color(dpg.mvThemeCol_CheckMark, SUCCESS)")
theme = theme.replace("dpg.add_theme_color(dpg.mvThemeCol_Separator, BORDER_SOFT)", "dpg.add_theme_color(dpg.mvThemeCol_Separator, MAGENTA_MUTED)", 1)
theme = theme.replace("dpg.add_theme_color(dpg.mvThemeCol_SeparatorHovered, ACCENT_MUTED)", "dpg.add_theme_color(dpg.mvThemeCol_SeparatorHovered, EMBER)", 1)
theme = theme.replace("dpg.add_theme_color(dpg.mvThemeCol_SeparatorActive, ACCENT)", "dpg.add_theme_color(dpg.mvThemeCol_SeparatorActive, EMBER_HOVER)", 1)

# Large spatial roles: slate left/work surfaces, plum side chrome, black hard strips.
theme = replace_once(theme, "dpg.add_theme_color(dpg.mvThemeCol_ChildBg, SURFACE_RECESSED)\n            dpg.add_theme_color(dpg.mvThemeCol_Border, BORDER_SOFT)", "dpg.add_theme_color(dpg.mvThemeCol_ChildBg, SURFACE)\n            dpg.add_theme_color(dpg.mvThemeCol_Border, BORDER_SOFT)", "nav rail surface")
theme = replace_once(theme, "with dpg.theme(tag=\"app_workspace_theme\"):\n        with dpg.theme_component(dpg.mvChildWindow):\n            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, SURFACE)", "with dpg.theme(tag=\"app_workspace_theme\"):\n        with dpg.theme_component(dpg.mvChildWindow):\n            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, BACKGROUND)", "workspace chrome")
theme = replace_once(theme, "with dpg.theme(tag=\"app_workspace_side_theme\"):\n        with dpg.theme_component(dpg.mvChildWindow):\n            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, SURFACE_RECESSED)", "with dpg.theme(tag=\"app_workspace_side_theme\"):\n        with dpg.theme_component(dpg.mvChildWindow):\n            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, BACKGROUND)", "workspace side plum")

# Active navigation is lime-on-black like the source application's selected rows.
old_nav = '''    with dpg.theme(tag="app_nav_primary_theme"):\n        with dpg.theme_component(dpg.mvButton):\n            dpg.add_theme_color(dpg.mvThemeCol_Text, TEXT)\n            dpg.add_theme_color(dpg.mvThemeCol_Button, ACCENT_MUTED)\n            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (75, 58, 160, 255))\n            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, ACCENT_MUTED)\n            dpg.add_theme_color(dpg.mvThemeCol_Border, BEVEL_EMBER)\n'''
new_nav = '''    with dpg.theme(tag="app_nav_primary_theme"):\n        with dpg.theme_component(dpg.mvButton):\n            dpg.add_theme_color(dpg.mvThemeCol_Text, JSON_BASE_ALT)\n            dpg.add_theme_color(dpg.mvThemeCol_Button, SUCCESS)\n            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (146, 211, 91, 255))\n            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (104, 169, 53, 255))\n            dpg.add_theme_color(dpg.mvThemeCol_Border, BACKGROUND_DEEP)\n'''
theme = replace_once(theme, old_nav, new_nav, "active navigation theme")

# Primary patch/save actions use the JSON purple button role; red stays destructive/divider.
old_primary = '''    with dpg.theme(tag="main_primary_button_theme"):\n        with dpg.theme_component(dpg.mvButton):\n            dpg.add_theme_color(dpg.mvThemeCol_Text, (25, 13, 10, 255))\n            dpg.add_theme_color(dpg.mvThemeCol_Button, EMBER)\n            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, EMBER_HOVER)\n            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, EMBER_ACTIVE)\n            dpg.add_theme_color(dpg.mvThemeCol_Border, BEVEL_EMBER)\n'''
new_primary = '''    with dpg.theme(tag="main_primary_button_theme"):\n        with dpg.theme_component(dpg.mvButton):\n            dpg.add_theme_color(dpg.mvThemeCol_Text, TEXT)\n            dpg.add_theme_color(dpg.mvThemeCol_Button, ACCENT)\n            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, ACCENT_HOVER)\n            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, ACCENT_ACTIVE)\n            dpg.add_theme_color(dpg.mvThemeCol_Border, JSON_TEXT_DISABLED)\n'''
theme = replace_once(theme, old_primary, new_primary, "primary button role")

# Status panels become slate fields rather than almost-black cards.
theme = theme.replace("dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (16, 25, 42, 255))", "dpg.add_theme_color(dpg.mvThemeCol_ChildBg, SURFACE_ALT)")
theme = theme.replace("dpg.add_theme_color(dpg.mvThemeCol_Border, (56, 77, 154, 255))", "dpg.add_theme_color(dpg.mvThemeCol_Border, SUCCESS)")
theme = theme.replace("dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (15, 20, 37, 255))", "dpg.add_theme_color(dpg.mvThemeCol_ChildBg, SURFACE_ALT)")

THEME.write_text(theme, encoding="utf-8")

checks = CHECKS.read_text(encoding="utf-8")
old_checks = '''UI_ACCENT = (133, 56, 148, 255)\nUI_ACCENT_HOVER = (169, 83, 184, 255)\nUI_EMBER = (223, 80, 59, 255)\nUI_EMBER_HOVER = (244, 102, 82, 255)\nUI_TEXT = (247, 240, 231, 255)\nUI_MUTED = (217, 199, 176, 255)\nUI_PANEL = (25, 19, 33, 255)\nUI_PANEL_ALT = (37, 27, 48, 255)\nUI_RAISED = (50, 37, 64, 255)\nUI_RECESSED = (17, 13, 23, 255)\nUI_PANEL_HOVER = (70, 51, 90, 255)\nUI_BORDER = (88, 108, 114, 255)\nUI_BEVEL_LIGHT = (164, 143, 123, 255)\nUI_BEVEL_DARK = (0, 0, 0, 220)\n'''
new_checks = '''UI_ACCENT = (133, 56, 148, 255)\nUI_ACCENT_HOVER = (169, 98, 183, 255)\nUI_EMBER = (223, 80, 59, 255)\nUI_EMBER_HOVER = (244, 102, 82, 255)\nUI_TEXT = (247, 240, 231, 255)\nUI_MUTED = (217, 199, 176, 255)\nUI_PANEL = (88, 108, 114, 255)\nUI_PANEL_ALT = (74, 92, 98, 255)\nUI_RAISED = (133, 56, 148, 255)\nUI_RECESSED = (72, 89, 94, 255)\nUI_PANEL_HOVER = (101, 122, 128, 255)\nUI_BORDER = (42, 38, 48, 255)\nUI_BEVEL_LIGHT = (164, 143, 123, 255)\nUI_BEVEL_DARK = (0, 0, 0, 210)\n'''
checks = replace_once(checks, old_checks, new_checks, "mod-library palette")
CHECKS.write_text(checks, encoding="utf-8")

d2pfx = D2PFX.read_text(encoding="utf-8")
d2pfx = replace_once(d2pfx, "dpg.add_theme_color(dpg.mvThemeCol_Header, (70, 51, 90, 210))", "dpg.add_theme_color(dpg.mvThemeCol_Header, (122, 193, 67, 230))", "d2pfx selected header")
d2pfx = replace_once(d2pfx, "dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (133, 56, 148, 230))", "dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (146, 211, 91, 240))", "d2pfx selected hover")
d2pfx = replace_once(d2pfx, "dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255))", "dpg.add_theme_color(dpg.mvThemeCol_Text, (0, 0, 0))", "d2pfx selected text")
D2PFX.write_text(d2pfx, encoding="utf-8")

tests = TESTS.read_text(encoding="utf-8")
tests = tests.replace("# v21.4: Plumfire Reactor release visual system.", "# v21.4: Black-Plum Reactor release visual system.")
tests += '''\n\ndef test_source_screenshot_spatial_color_roles_are_materialized():\n    assert "BACKGROUND = JSON_WINDOW_BG" in THEME\n    assert "SURFACE = JSON_BASE_BG" in THEME\n    assert "SURFACE_RAISED = JSON_BUTTON_BG" in THEME\n    assert "dpg.add_theme_color(dpg.mvThemeCol_Button, SUCCESS)" in THEME\n    assert "dpg.add_theme_color(dpg.mvThemeCol_Text, JSON_BASE_ALT)" in THEME\n    assert "UI_PANEL = (88, 108, 114, 255)" in CHECKBOXES\n    assert "UI_RAISED = (133, 56, 148, 255)" in CHECKBOXES\n    assert "dpg.add_theme_color(dpg.mvThemeCol_Header, (122, 193, 67, 230))" in D2PFX\n    assert "dpg.add_theme_color(dpg.mvThemeCol_Text, (0, 0, 0))" in D2PFX\n'''
TESTS.write_text(tests, encoding="utf-8")
