from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    target = Path(path)
    text = target.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected exactly one match, found {count}: {old!r}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


replace_once(
    "Minify/__main__.py",
    '            dpg.add_spacer(tag="header_spacer", width=10)\n'
    '            dpg.add_text("LOCAL MOD WORKSPACE", tag="header_context")\n'
    '            dpg.add_text("RC6", tag="header_badge")\n',
    "",
)
replace_once(
    "Minify/ui/window.py",
    '    if dpg.does_item_exist("header_spacer"):\n'
    '        dpg.configure_item("header_spacer", width=max(12, shared.window_width - 520))\n',
    "",
)

theme = Path("Minify/ui/theme.py")
text = theme.read_text(encoding="utf-8")

old_palette = """# v21.2: Obsidian Ember depth pass.
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
"""
new_palette = """# v21.4: modern graphite visual system.
# Flat layered surfaces, cool blue focus, subtle borders and larger radii.
# BEVEL_* names remain compatibility aliases, but the shadow is transparent so
# controls render as clean flat cards instead of faux-raised chrome.
BACKGROUND = (10, 13, 18, 255)
BACKGROUND_DEEP = (7, 9, 13, 255)
SURFACE = (17, 22, 29, 255)
SURFACE_ALT = (22, 28, 37, 255)
SURFACE_RAISED = (27, 34, 44, 255)
SURFACE_RECESSED = (12, 16, 22, 255)
SURFACE_HOVER = (35, 44, 57, 255)
SURFACE_ACTIVE = (24, 31, 41, 255)
SURFACE_WARM = (27, 31, 41, 255)
BORDER = (54, 65, 82, 255)
BORDER_SOFT = (35, 43, 55, 255)
BEVEL_LIGHT = BORDER
BEVEL_DARK = (0, 0, 0, 0)
BEVEL_EMBER = (112, 170, 255, 255)
TEXT = (236, 241, 248, 255)
MUTED = (150, 161, 178, 255)
MUTED_DARK = (92, 102, 118, 255)
ACCENT = (80, 145, 255, 255)
ACCENT_HOVER = (111, 168, 255, 255)
ACCENT_ACTIVE = (61, 122, 232, 255)
ACCENT_MUTED = (38, 70, 120, 255)
HIGHLIGHT = (142, 183, 255, 255)
D2PFX = (76, 201, 190, 255)
VPK = (126, 196, 141, 255)
DANGER = (223, 86, 105, 255)
DANGER_HOVER = (239, 108, 125, 255)
WARNING = (236, 186, 83, 255)
SUCCESS = (93, 200, 139, 255)
"""
if text.count(old_palette) != 1:
    raise SystemExit("theme palette block did not match exactly")
text = text.replace(old_palette, new_palette, 1)

replacements = {
    "dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=9, y=8)": "dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=10, y=9)",
    "dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, x=8, y=6)": "dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, x=9, y=7)",
    "dpg.add_theme_style(dpg.mvStyleVar_FramePadding, x=7, y=4)": "dpg.add_theme_style(dpg.mvStyleVar_FramePadding, x=9, y=5)",
    "dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 3)": "dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 7)",
    "dpg.add_theme_style(dpg.mvStyleVar_ScrollbarRounding, 4)": "dpg.add_theme_style(dpg.mvStyleVar_ScrollbarRounding, 8)",
    "dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 4)": "dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 6)",
    "dpg.add_theme_color(dpg.mvThemeCol_Border, BEVEL_LIGHT)": "dpg.add_theme_color(dpg.mvThemeCol_Border, BORDER)",
    "dpg.add_theme_color(dpg.mvThemeCol_TableBorderStrong, BEVEL_LIGHT)": "dpg.add_theme_color(dpg.mvThemeCol_TableBorderStrong, BORDER)",
    "dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab, (61, 69, 82, 255))": "dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab, (47, 56, 70, 255))",
    "dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabHovered, (80, 90, 105, 255))": "dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabHovered, (63, 75, 93, 255))",
    "dpg.add_theme_color(dpg.mvThemeCol_Border, ACCENT_MUTED)": "dpg.add_theme_color(dpg.mvThemeCol_Border, BORDER_SOFT)",
    "dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (11, 16, 23, 255))": "dpg.add_theme_color(dpg.mvThemeCol_ChildBg, SURFACE_RECESSED)",
    "dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 5)": "dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 9)",
    "dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 4)": "dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 8)",
    "dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 2)": "dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 8)",
    "dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (12, 28, 30, 255))": "dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (14, 24, 34, 255))",
    "dpg.add_theme_color(dpg.mvThemeCol_Border, (38, 79, 78, 255))": "dpg.add_theme_color(dpg.mvThemeCol_Border, (36, 74, 112, 255))",
    "dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (11, 15, 21, 255))": "dpg.add_theme_color(dpg.mvThemeCol_ChildBg, BACKGROUND_DEEP)",
    "dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 2)": "dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 7)",
    "dpg.add_theme_color(dpg.mvThemeCol_Button, (38, 31, 32, 255))": "dpg.add_theme_color(dpg.mvThemeCol_Button, ACCENT_MUTED)",
    "dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (66, 42, 40, 255))": "dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (47, 88, 148, 255))",
    "dpg.add_theme_color(dpg.mvThemeCol_Text, (31, 18, 14, 255))": "dpg.add_theme_color(dpg.mvThemeCol_Text, TEXT)",
    "dpg.add_theme_color(dpg.mvThemeCol_Text, (119, 102, 96, 255))": "dpg.add_theme_color(dpg.mvThemeCol_Text, MUTED_DARK)",
    "dpg.add_theme_color(dpg.mvThemeCol_Button, (47, 40, 40, 255))": "dpg.add_theme_color(dpg.mvThemeCol_Button, SURFACE_ALT)",
    "dpg.add_theme_color(dpg.mvThemeCol_CheckMark, (104, 76, 68, 255))": "dpg.add_theme_color(dpg.mvThemeCol_CheckMark, MUTED_DARK)",
    "dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (14, 19, 26, 255))": "dpg.add_theme_color(dpg.mvThemeCol_ChildBg, SURFACE_RECESSED)",
    "dpg.add_theme_color(dpg.mvThemeCol_Button, (53, 34, 34, 255))": "dpg.add_theme_color(dpg.mvThemeCol_Button, ACCENT_MUTED)",
    "dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (68, 42, 40, 255))": "dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (47, 88, 148, 255))",
}
for old, new in replacements.items():
    if old not in text:
        raise SystemExit(f"missing theme pattern: {old}")
    text = text.replace(old, new)

text = text.replace(
    "# Library chrome gets the same restrained depth treatment: raised command strips,\n"
    "# recessed list surfaces, and crisp 1 px bevel edges.\n",
    "# Library chrome follows the same flat card system with restrained contrast.\n",
)
text = text.replace('        "header_context",\n', "")
text = text.replace(
    '    for tag in ("header_badge", "dashboard_metric", "dashboard_side_title", "activity_label"):\n',
    '    for tag in ("dashboard_metric", "dashboard_side_title", "activity_label"):\n',
)
theme.write_text(text, encoding="utf-8")

Path("tests/test_modern_ui.py").write_text(
    '''from pathlib import Path\n\n\nROOT = Path(__file__).resolve().parents[1]\nMAIN = (ROOT / "Minify" / "__main__.py").read_text(encoding="utf-8")\nTHEME = (ROOT / "Minify" / "ui" / "theme.py").read_text(encoding="utf-8")\nWINDOW = (ROOT / "Minify" / "ui" / "window.py").read_text(encoding="utf-8")\n\n\ndef test_stale_workspace_badge_removed():\n    assert "LOCAL MOD WORKSPACE" not in MAIN\n    assert 'tag="header_context"' not in MAIN\n    assert 'tag="header_badge"' not in MAIN\n    assert '"header_spacer"' not in WINDOW\n\n\ndef test_modern_graphite_blue_palette_is_materialized():\n    assert "# v21.4: modern graphite visual system." in THEME\n    assert "ACCENT = (80, 145, 255, 255)" in THEME\n    assert "BEVEL_DARK = (0, 0, 0, 0)" in THEME\n    assert "mvStyleVar_FrameRounding, 7" in THEME\n    assert "mvStyleVar_ChildRounding, 9" in THEME\n''',
    encoding="utf-8",
)
