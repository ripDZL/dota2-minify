from pathlib import Path


def replace_once(path, old, new):
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one match, found {count}: {old[:80]!r}")
    p.write_text(text.replace(old, new, 1), encoding="utf-8")


# Landing workspace: add real layered composition rather than a flat panel.
main_path = Path("Minify/__main__.py")
main = main_path.read_text(encoding="utf-8")
old_main = '''            dpg.add_text("PATCH WORKSPACE", parent="app_workspace_main", tag="workspace_eyebrow")
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
'''
new_main = '''            dpg.add_child_window(
                parent="app_workspace_main",
                tag="dashboard_hero_card",
                height=118,
                width=-1,
                border=True,
                no_scrollbar=True,
                no_scroll_with_mouse=True,
            )
            dpg.add_text("PATCH WORKSPACE", parent="dashboard_hero_card", tag="workspace_eyebrow")
            dpg.add_text("Build a clean patch", parent="dashboard_hero_card", tag="dashboard_focus_title")
            dpg.bind_item_font("dashboard_focus_title", "large_font")
            dpg.add_text("0 selected • 0 installed", parent="dashboard_hero_card", tag="dashboard_metric")
            dpg.add_text(
                "Choose your mods, review shared files, then let Minify create a restore point before changing Dota.",
                parent="dashboard_hero_card",
                tag="dashboard_focus_hint",
                wrap=420,
            )
            dpg.add_spacer(parent="app_workspace_main", height=6)
            dpg.add_child_window(
                parent="app_workspace_main",
                tag="dashboard_status_panel",
                height=54,
                width=-1,
                border=True,
                no_scrollbar=True,
                no_scroll_with_mouse=True,
            )
            with dpg.group(parent="dashboard_status_panel", horizontal=True):
                dpg.add_text("● READY", tag="dashboard_status_label")
                dpg.add_text("Getting your mod library ready...", tag="dashboard_status_message", wrap=420)
            dpg.add_spacer(parent="app_workspace_main", height=6)
            dpg.add_child_window(
                parent="app_workspace_main",
                tag="dashboard_action_bar",
                height=58,
                width=-1,
                border=True,
                no_scrollbar=True,
                no_scroll_with_mouse=True,
            )
            with dpg.group(parent="dashboard_action_bar", horizontal=True):
                dpg.add_button(
                    tag="button_patch",
                    label="Review & Patch",
                    callback=checkboxes.show_patch_preview,
                    enabled=False,
                    width=196,
                    height=38,
                )
                dpg.add_button(
                    tag="button_refresh_main", label="Refresh", callback=checkboxes.refresh, width=132, height=38
                )
'''
if main.count(old_main) != 1:
    raise SystemExit("landing workspace block mismatch")
main = main.replace(old_main, new_main, 1)

old_side = '''            dpg.add_text("PATCH FLOW", parent="app_workspace_side", tag="dashboard_side_title")
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
'''
new_side = '''            dpg.add_child_window(
                parent="app_workspace_side",
                tag="dashboard_flow_card",
                height=126,
                width=-1,
                border=True,
                no_scrollbar=True,
                no_scroll_with_mouse=True,
            )
            dpg.add_text("PATCH FLOW", parent="dashboard_flow_card", tag="dashboard_side_title")
            dpg.add_text("01  Review shared files", parent="dashboard_flow_card", tag="dashboard_step_1")
            dpg.add_text("02  Create restore point", parent="dashboard_flow_card", tag="dashboard_step_2")
            dpg.add_text("03  Apply selected mods", parent="dashboard_flow_card", tag="dashboard_step_3")
            dpg.add_spacer(parent="app_workspace_side", height=6)
            dpg.add_child_window(
                parent="app_workspace_side",
                tag="dashboard_safety_card",
                height=-1,
                width=-1,
                border=True,
                no_scrollbar=True,
                no_scroll_with_mouse=True,
            )
            dpg.add_text("SAFETY / ROLLBACK", parent="dashboard_safety_card", tag="dashboard_safety_title")
            dpg.add_text(
                "Automatic rollback protects the previous Minify output if a patch fails.",
                parent="dashboard_safety_card",
                tag="dashboard_safety_text",
                wrap=220,
            )
'''
if main.count(old_side) != 1:
    raise SystemExit("side workspace block mismatch")
main = main.replace(old_side, new_side, 1)
main_path.write_text(main, encoding="utf-8")

# Global release visual system: richer layered depth + dual arc/ember accents.
theme_path = Path("Minify/ui/theme.py")
theme = theme_path.read_text(encoding="utf-8")
old_palette = '''# v21.4: modern graphite visual system.\n# Flat layered surfaces, cool blue focus, subtle borders and larger radii.\n# BEVEL_* names remain compatibility aliases, but the shadow is transparent so\n# controls render as clean flat cards instead of faux-raised chrome.\nBACKGROUND = (10, 13, 18, 255)\nBACKGROUND_DEEP = (7, 9, 13, 255)\nSURFACE = (17, 22, 29, 255)\nSURFACE_ALT = (22, 28, 37, 255)\nSURFACE_RAISED = (27, 34, 44, 255)\nSURFACE_RECESSED = (12, 16, 22, 255)\nSURFACE_HOVER = (35, 44, 57, 255)\nSURFACE_ACTIVE = (24, 31, 41, 255)\nSURFACE_WARM = (27, 31, 41, 255)\nBORDER = (54, 65, 82, 255)\nBORDER_SOFT = (35, 43, 55, 255)\nBEVEL_LIGHT = BORDER\nBEVEL_DARK = (0, 0, 0, 0)\nBEVEL_EMBER = (112, 170, 255, 255)\nTEXT = (236, 241, 248, 255)\nMUTED = (150, 161, 178, 255)\nMUTED_DARK = (92, 102, 118, 255)\nACCENT = (80, 145, 255, 255)\nACCENT_HOVER = (111, 168, 255, 255)\nACCENT_ACTIVE = (61, 122, 232, 255)\nACCENT_MUTED = (38, 70, 120, 255)\nHIGHLIGHT = (142, 183, 255, 255)\nD2PFX = (76, 201, 190, 255)\nVPK = (126, 196, 141, 255)\nDANGER = (223, 86, 105, 255)\nDANGER_HOVER = (239, 108, 125, 255)\nWARNING = (236, 186, 83, 255)\nSUCCESS = (93, 200, 139, 255)\n'''
new_palette = '''# v21.4: Obsidian Arc release visual system.\n# Deep layered graphite, luminous arc-blue state, ember-orange identity/actions,\n# and subtle physical edge lighting. Dense enough to feel authored, restrained\n# enough to keep long mod lists readable.\nBACKGROUND = (7, 9, 14, 255)\nBACKGROUND_DEEP = (3, 5, 9, 255)\nSURFACE = (14, 19, 27, 255)\nSURFACE_ALT = (21, 28, 39, 255)\nSURFACE_RAISED = (30, 39, 53, 255)\nSURFACE_RECESSED = (9, 13, 19, 255)\nSURFACE_HOVER = (43, 55, 73, 255)\nSURFACE_ACTIVE = (25, 33, 46, 255)\nSURFACE_WARM = (34, 24, 25, 255)\nBORDER = (65, 80, 103, 255)\nBORDER_SOFT = (32, 42, 57, 255)\nBEVEL_LIGHT = (100, 118, 145, 255)\nBEVEL_DARK = (1, 2, 5, 220)\nBEVEL_EMBER = (255, 132, 92, 255)\nTEXT = (241, 245, 250, 255)\nMUTED = (158, 171, 190, 255)\nMUTED_DARK = (88, 100, 119, 255)\nACCENT = (84, 151, 255, 255)\nACCENT_HOVER = (116, 176, 255, 255)\nACCENT_ACTIVE = (62, 125, 232, 255)\nACCENT_MUTED = (36, 69, 119, 255)\nEMBER = (240, 103, 70, 255)\nEMBER_HOVER = (255, 133, 91, 255)\nEMBER_ACTIVE = (204, 80, 55, 255)\nEMBER_MUTED = (103, 48, 40, 255)\nHIGHLIGHT = (239, 191, 105, 255)\nD2PFX = (78, 208, 196, 255)\nVPK = (132, 201, 145, 255)\nDANGER = (222, 82, 101, 255)\nDANGER_HOVER = (241, 104, 121, 255)\nWARNING = (239, 184, 78, 255)\nSUCCESS = (91, 204, 139, 255)\n'''
if theme.count(old_palette) != 1:
    raise SystemExit("theme palette mismatch")
theme = theme.replace(old_palette, new_palette, 1)

insert_after = '''    with dpg.theme(tag="app_workspace_main_theme"):\n        with dpg.theme_component(dpg.mvChildWindow):\n            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, SURFACE)\n            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 0)\n            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=3, y=2)\n\n'''
extra_themes = '''    with dpg.theme(tag="dashboard_hero_card_theme"):\n        with dpg.theme_component(dpg.mvChildWindow):\n            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, SURFACE_ALT)\n            dpg.add_theme_color(dpg.mvThemeCol_Border, ACCENT_MUTED)\n            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)\n            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)\n            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 8)\n            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=14, y=11)\n\n    with dpg.theme(tag="dashboard_action_bar_theme"):\n        with dpg.theme_component(dpg.mvChildWindow):\n            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, SURFACE_RECESSED)\n            dpg.add_theme_color(dpg.mvThemeCol_Border, BORDER_SOFT)\n            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)\n            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)\n            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 8)\n            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=9, y=8)\n\n    with dpg.theme(tag="dashboard_flow_card_theme"):\n        with dpg.theme_component(dpg.mvChildWindow):\n            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, SURFACE_ALT)\n            dpg.add_theme_color(dpg.mvThemeCol_Border, (57, 79, 116, 255))\n            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)\n            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)\n            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 8)\n            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=11, y=10)\n\n    with dpg.theme(tag="dashboard_safety_card_theme"):\n        with dpg.theme_component(dpg.mvChildWindow):\n            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (13, 25, 25, 255))\n            dpg.add_theme_color(dpg.mvThemeCol_Border, (42, 91, 82, 255))\n            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, BEVEL_DARK)\n            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)\n            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 8)\n            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=11, y=10)\n\n    with dpg.theme(tag="dashboard_safety_title_theme"):\n        with dpg.theme_component(dpg.mvAll):\n            dpg.add_theme_color(dpg.mvThemeCol_Text, D2PFX)\n\n'''
if theme.count(insert_after) != 1:
    raise SystemExit("workspace main theme insertion point mismatch")
theme = theme.replace(insert_after, insert_after + extra_themes, 1)

# Ember owns brand and irreversible patch action; blue owns navigation/state.
theme = theme.replace(
    '            dpg.add_theme_color(dpg.mvThemeCol_Text, ACCENT_HOVER)\n\n    with dpg.theme(tag="dashboard_product_theme"):',
    '            dpg.add_theme_color(dpg.mvThemeCol_Text, EMBER_HOVER)\n\n    with dpg.theme(tag="dashboard_product_theme"):',
    1,
)
old_primary = '''            dpg.add_theme_color(dpg.mvThemeCol_Text, TEXT)\n            dpg.add_theme_color(dpg.mvThemeCol_Button, ACCENT)\n            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, ACCENT_HOVER)\n            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, ACCENT_ACTIVE)\n            dpg.add_theme_color(dpg.mvThemeCol_Border, BEVEL_EMBER)\n'''
new_primary = '''            dpg.add_theme_color(dpg.mvThemeCol_Text, (25, 13, 10, 255))\n            dpg.add_theme_color(dpg.mvThemeCol_Button, EMBER)\n            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, EMBER_HOVER)\n            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, EMBER_ACTIVE)\n            dpg.add_theme_color(dpg.mvThemeCol_Border, BEVEL_EMBER)\n'''
if theme.count(old_primary) != 1:
    raise SystemExit("primary button theme mismatch")
theme = theme.replace(old_primary, new_primary, 1)

old_bind = '''        ("app_workspace_main", "app_workspace_main_theme"),\n        ("app_workspace_side", "app_workspace_side_theme"),\n        ("dashboard_status_panel", "dashboard_status_panel_theme"),\n'''
new_bind = '''        ("app_workspace_main", "app_workspace_main_theme"),\n        ("app_workspace_side", "app_workspace_side_theme"),\n        ("dashboard_hero_card", "dashboard_hero_card_theme"),\n        ("dashboard_action_bar", "dashboard_action_bar_theme"),\n        ("dashboard_flow_card", "dashboard_flow_card_theme"),\n        ("dashboard_safety_card", "dashboard_safety_card_theme"),\n        ("dashboard_status_panel", "dashboard_status_panel_theme"),\n'''
if theme.count(old_bind) != 1:
    raise SystemExit("theme binding tuple mismatch")
theme = theme.replace(old_bind, new_bind, 1)
needle = '''    if dpg.does_item_exist("dashboard_status_label"):\n        dpg.bind_item_theme("dashboard_status_label", "dashboard_status_ready_theme")\n\n'''
replacement = needle + '''    if dpg.does_item_exist("dashboard_safety_title"):\n        dpg.bind_item_theme("dashboard_safety_title", "dashboard_safety_title_theme")\n    if dpg.does_item_exist("dashboard_safety_text"):\n        dpg.bind_item_theme("dashboard_safety_text", "dashboard_muted_theme")\n\n'''
if theme.count(needle) != 1:
    raise SystemExit("status binding insertion mismatch")
theme = theme.replace(needle, replacement, 1)
theme_path.write_text(theme, encoding="utf-8")

# Mod Library has its own theme system; align it with the release identity.
checks_path = Path("Minify/ui/checkboxes.py")
checks = checks_path.read_text(encoding="utf-8")
old_consts = '''UI_ACCENT = (236, 103, 72, 255)\nUI_ACCENT_HOVER = (255, 132, 92, 255)\nUI_TEXT = (247, 243, 234, 255)\nUI_MUTED = (159, 170, 184, 255)\nUI_PANEL = (18, 24, 33, 255)\nUI_PANEL_ALT = (25, 33, 44, 255)\nUI_RAISED = (33, 42, 54, 255)\nUI_RECESSED = (12, 16, 22, 255)\nUI_PANEL_HOVER = (44, 56, 72, 255)\nUI_BORDER = (58, 73, 92, 255)\nUI_BEVEL_LIGHT = (80, 95, 116, 255)\nUI_BEVEL_DARK = (2, 4, 7, 255)\nUI_D2PFX = (100, 199, 188, 255)\nUI_COLLECTION = (218, 181, 112, 255)\nUI_VPK = (145, 191, 126, 255)\nUI_WARNING = (226, 176, 72, 255)\nUI_ERROR = (229, 91, 103, 255)\nUI_SUCCESS = (103, 193, 130, 255)\n'''
new_consts = '''UI_ACCENT = (84, 151, 255, 255)\nUI_ACCENT_HOVER = (116, 176, 255, 255)\nUI_EMBER = (240, 103, 70, 255)\nUI_EMBER_HOVER = (255, 133, 91, 255)\nUI_TEXT = (241, 245, 250, 255)\nUI_MUTED = (158, 171, 190, 255)\nUI_PANEL = (14, 19, 27, 255)\nUI_PANEL_ALT = (21, 28, 39, 255)\nUI_RAISED = (30, 39, 53, 255)\nUI_RECESSED = (9, 13, 19, 255)\nUI_PANEL_HOVER = (43, 55, 73, 255)\nUI_BORDER = (65, 80, 103, 255)\nUI_BEVEL_LIGHT = (100, 118, 145, 255)\nUI_BEVEL_DARK = (1, 2, 5, 220)\nUI_D2PFX = (78, 208, 196, 255)\nUI_COLLECTION = (239, 191, 105, 255)\nUI_VPK = (132, 201, 145, 255)\nUI_WARNING = (239, 184, 78, 255)\nUI_ERROR = (222, 82, 101, 255)\nUI_SUCCESS = (91, 204, 139, 255)\n'''
if checks.count(old_consts) != 1:
    raise SystemExit("checkbox palette mismatch")
checks = checks.replace(old_consts, new_consts, 1)
old_mod_primary = '''            dpg.add_theme_color(dpg.mvThemeCol_Text, (31, 18, 14, 255))\n            dpg.add_theme_color(dpg.mvThemeCol_Button, UI_ACCENT)\n            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, UI_ACCENT_HOVER)\n            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (193, 82, 52, 255))\n            dpg.add_theme_color(dpg.mvThemeCol_Border, UI_ACCENT_HOVER)\n'''
new_mod_primary = '''            dpg.add_theme_color(dpg.mvThemeCol_Text, (25, 13, 10, 255))\n            dpg.add_theme_color(dpg.mvThemeCol_Button, UI_EMBER)\n            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, UI_EMBER_HOVER)\n            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (204, 80, 55, 255))\n            dpg.add_theme_color(dpg.mvThemeCol_Border, UI_EMBER_HOVER)\n'''
if checks.count(old_mod_primary) != 1:
    raise SystemExit("mod primary theme mismatch")
checks = checks.replace(old_mod_primary, new_mod_primary, 1)
checks = checks.replace("dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 3)", "dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)")
checks = checks.replace("dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 2)", "dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5)")
checks = checks.replace("dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 2)", "dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 7)")
checks_path.write_text(checks, encoding="utf-8")

# D2PFX keeps its teal identity, but remove the legacy bright-cyan/flat selection.
d2pfx_path = Path("Minify/browsers/d2pfx/ui.py")
d2pfx = d2pfx_path.read_text(encoding="utf-8")nd2pfx = d2pfx.replace('dpg.add_theme_color(dpg.mvThemeCol_Header, (0, 119, 119, 150))', 'dpg.add_theme_color(dpg.mvThemeCol_Header, (20, 78, 76, 190))', 1)
d2pfx = d2pfx.replace('dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (0, 119, 119, 200))', 'dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (30, 108, 104, 220))', 1)
d2pfx = d2pfx.replace('dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (0, 119, 119, 255))', 'dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (42, 137, 130, 255))', 1)
d2pfx = d2pfx.replace('dpg.add_text("Select a category", tag="d2pfx_cat_title", color=(0, 255, 255))', 'dpg.add_text("Select a category", tag="d2pfx_cat_title", color=(78, 208, 196))', 1)
d2pfx_path.write_text(d2pfx, encoding="utf-8")

# Update visual-regression assertions to the release system.
test_path = Path("tests/test_modern_ui.py")
test_path.write_text('''from pathlib import Path\n\n\nROOT = Path(__file__).resolve().parents[1]\nMAIN = (ROOT / "Minify" / "__main__.py").read_text(encoding="utf-8")\nTHEME = (ROOT / "Minify" / "ui" / "theme.py").read_text(encoding="utf-8")\nCHECKBOXES = (ROOT / "Minify" / "ui" / "checkboxes.py").read_text(encoding="utf-8")\nD2PFX = (ROOT / "Minify" / "browsers" / "d2pfx" / "ui.py").read_text(encoding="utf-8")\n\n\ndef test_stale_workspace_badge_removed():\n    assert "LOCAL MOD WORKSPACE" not in MAIN\n    assert 'tag="header_context"' not in MAIN\n    assert 'tag="header_badge"' not in MAIN\n\n\ndef test_obsidian_arc_release_palette_is_materialized():\n    assert "# v21.4: Obsidian Arc release visual system." in THEME\n    assert "ACCENT = (84, 151, 255, 255)" in THEME\n    assert "EMBER = (240, 103, 70, 255)" in THEME\n    assert "BEVEL_DARK = (1, 2, 5, 220)" in THEME\n    assert "UI_EMBER = (240, 103, 70, 255)" in CHECKBOXES\n\n\ndef test_release_dashboard_uses_layered_cards():\n    for tag in (\n        "dashboard_hero_card",\n        "dashboard_action_bar",\n        "dashboard_flow_card",\n        "dashboard_safety_card",\n    ):\n        assert f'tag="{tag}"' in MAIN\n        assert f'("{tag}",' in THEME\n\n\ndef test_d2pfx_uses_release_teal_instead_of_legacy_cyan():\n    assert "color=(78, 208, 196)" in D2PFX\n    assert "color=(0, 255, 255)" not in D2PFX\n''', encoding="utf-8")
