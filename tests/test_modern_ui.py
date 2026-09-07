from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN = (ROOT / "Minify" / "__main__.py").read_text(encoding="utf-8")
THEME = (ROOT / "Minify" / "ui" / "theme.py").read_text(encoding="utf-8")
CHECKBOXES = (ROOT / "Minify" / "ui" / "checkboxes.py").read_text(encoding="utf-8")
D2PFX = (ROOT / "Minify" / "browsers" / "d2pfx" / "ui.py").read_text(encoding="utf-8")
WINDOW = (ROOT / "Minify" / "ui" / "window.py").read_text(encoding="utf-8")
TERMINAL = (ROOT / "Minify" / "ui" / "terminal.py").read_text(encoding="utf-8")
DEVTOOLS = (ROOT / "Minify" / "ui" / "dev_tools.py").read_text(encoding="utf-8")


def test_stale_workspace_badge_removed():
    assert "LOCAL MOD WORKSPACE" not in MAIN
    assert 'tag="header_context"' not in MAIN
    assert 'tag="header_badge"' not in MAIN


def test_user_json_palette_is_materialized():
    assert "# v21.4: Black-Plum Reactor release visual system." in THEME
    for token in (
        "JSON_ACCENT_DIVIDER = (223, 80, 59, 255)",
        "JSON_ACCENT_HIGHLIGHT = (122, 193, 67, 255)",
        "JSON_ACCENT_LINK = (255, 255, 0, 255)",
        "JSON_BASE_BG = (88, 108, 114, 255)",
        "JSON_BUTTON_BG = (133, 56, 148, 255)",
        "JSON_TEXT_BRIGHT = (255, 195, 15, 255)",
        "JSON_TEXT_DISABLED = (164, 143, 123, 255)",
        "JSON_TEXT_PLACEHOLDER = (217, 199, 176, 255)",
        "JSON_TEXT_PRIMARY = (247, 240, 231, 255)",
        "JSON_WINDOW_BG = (70, 51, 90, 255)",
    ):
        assert token in THEME
    assert "ACCENT_HOVER = (169, 98, 183, 255)" in THEME
    assert "UI_ACCENT = (133, 56, 148, 255)" in CHECKBOXES
    assert "UI_ACCENT_HOVER = (169, 98, 183, 255)" in CHECKBOXES
    assert "UI_SUCCESS = (122, 193, 67, 255)" in CHECKBOXES


def test_primary_action_uses_json_button_role():
    start = THEME.index('with dpg.theme(tag="main_primary_button_theme")')
    end = THEME.index('with dpg.theme(tag="main_secondary_button_theme")', start)
    primary = THEME[start:end]
    assert "dpg.add_theme_color(dpg.mvThemeCol_Button, ACCENT)" in primary
    assert "dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, ACCENT_HOVER)" in primary
    assert "dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, ACCENT_ACTIVE)" in primary


def test_release_console_uses_real_alignment_tables():
    for tag in ("header_layout", "dashboard_metric_table"):
        assert f'tag="{tag}"' in MAIN
    for tag in ("header_left_gutter", "header_brand_column", "header_right_gutter"):
        assert f'tag="{tag}"' in MAIN
    assert 'tag="dashboard_flow_table"' not in MAIN
    assert 'tag="dashboard_guard_table"' not in MAIN


def test_release_console_has_dense_command_hierarchy():
    for tag in (
        "header_brand_group",
        "header_accent_rail",
        "dashboard_hero_card",
        "dashboard_metric_strip",
        "dashboard_status_panel",
        "dashboard_action_bar",
        "activity_header",
    ):
        assert f'tag="{tag}"' in MAIN


def test_home_explainer_panel_removed_and_patch_sequence_is_vertical():
    for tag in ("app_workspace_side", "dashboard_flow_card", "dashboard_signal_card", "dashboard_safety_card"):
        assert f'tag="{tag}"' not in MAIN
    sequence_start = MAIN.index('tag="dashboard_metric_table"')
    sequence_end = MAIN.index('tag="dashboard_status_panel"', sequence_start)
    sequence = MAIN[sequence_start:sequence_end]
    assert sequence.count("with dpg.table_row():") == 3
    for label in ("ANALYZE", "Shared files", "SNAPSHOT", "Restore point", "COMPOSE", "Selected mods"):
        assert label in sequence


def test_alignment_labels_do_not_depend_on_space_padding():
    for label in ("Shared files", "Restore point", "Selected mods"):
        assert label in MAIN
    for stale in ("Shared-file collision scan", "ROLLBACK        AUTOMATIC", "GUARD MATRIX", "FAIL-SAFE"):
        assert stale not in MAIN


def test_activity_header_uses_plain_language_and_copy_tools():
    assert 'dpg.add_text("ACTIVITY LOG", parent="activity_header", tag="activity_label")' in MAIN
    assert "LIVE ACTIVITY" not in MAIN
    assert "STREAM ONLINE" not in MAIN
    assert 'tag="activity_caption"' not in MAIN
    assert 'tag="activity_stream_state"' not in MAIN
    assert 'tag="activity_copy_button"' in WINDOW
    assert 'label="COPY LOG"' in WINDOW
    assert 'tag="activity_select_button"' in WINDOW
    assert 'label="SELECT TEXT"' in WINDOW
    assert "callback=terminal.copy_all" in WINDOW
    assert "callback=terminal.show_copy_view" in WINDOW
    assert "right_edge = max(270, content_width - 28)" in WINDOW


def test_activity_log_has_selectable_debug_view():
    assert "def get_text():" in TERMINAL
    assert "def copy_all(" in TERMINAL
    assert "dpg.set_clipboard_text(get_text())" in TERMINAL
    assert "def show_copy_view(" in TERMINAL
    assert 'tag="activity_log_copy_text"' in TERMINAL
    assert "multiline=True" in TERMINAL
    assert "readonly=True" in TERMINAL
    assert 'label="COPY ALL"' in TERMINAL


def test_responsive_home_uses_independent_rows_before_clipping():
    assert "main_width = max(360, workspace_width - 20)" in WINDOW
    assert "hero_height = 124 if compact_width else 116" in WINDOW
    assert "sequence_height = max(94, min(116, int(base_inner_height * 0.24)))" in WINDOW
    assert "status_height = 68" in WINDOW
    assert "action_height = 136 if stack_actions else 96" in WINDOW
    assert "required_inner_height = hero_height + sequence_height + status_height + action_height + 20" in WINDOW
    assert "shell_body_height = min(520, max(base_shell_height, required_inner_height + 34))" in WINDOW
    assert 'dpg.move_item(' in WINDOW
    assert 'parent="app_workspace_main"' in WINDOW
    assert 'before="dashboard_status_panel"' in WINDOW
    assert 'dpg.configure_item("dashboard_metric_strip", height=sequence_height)' in WINDOW
    assert '"app_workspace_main",\n            width=main_width,\n            height=inner_height,\n            no_scrollbar=False' in WINDOW
    assert "wide_workspace" not in WINDOW
    assert 'dpg.configure_item("app_workspace_side"' not in WINDOW
    assert 'dpg.configure_item("dashboard_hero_card", height=hero_height)' in WINDOW


def test_deployment_buttons_use_responsive_row_budget():
    assert 'tag="dashboard_action_buttons"' in WINDOW
    assert 'dpg.move_item("button_patch", parent="dashboard_action_buttons")' in WINDOW
    assert 'dpg.move_item("button_refresh_main", parent="dashboard_action_buttons")' in WINDOW
    assert "stack_actions = main_width < 560" in WINDOW
    assert "action_cluster_width = max(260, min(620, main_width - 28))" in WINDOW
    assert "patch_width = action_cluster_width" in WINDOW
    assert "refresh_width = action_cluster_width" in WINDOW
    assert "patch_width = max(180, int(action_cluster_width * 0.58))" in WINDOW
    assert "refresh_width = max(140, action_cluster_width - patch_width - 8)" in WINDOW
    assert 'horizontal=not stack_actions' in WINDOW
    assert 'dpg.configure_item("button_patch", width=patch_width)' in WINDOW
    assert 'dpg.configure_item("button_refresh_main", width=refresh_width)' in WINDOW


def test_deployment_action_bar_has_non_clipping_vertical_budget():
    assert "base_shell_height = max(360, min(520, shared.window_height - 300))" in WINDOW
    assert "base_inner_height = max(300, base_shell_height - 34)" in WINDOW
    assert "action_height = 136 if stack_actions else 96" in WINDOW
    assert "required_inner_height = hero_height + sequence_height + status_height + action_height + 20" in WINDOW
    assert 'dpg.configure_item("dashboard_action_bar", height=action_height)' in WINDOW


def test_release_console_keeps_actionable_navigation():
    for label in ("PATCH CORE", "MOD LIBRARY", "D2PFX NETWORK", "CONTROL PANEL", "RESTORE POINTS"):
        assert f'label="{label}"' in MAIN


def test_d2pfx_uses_json_link_and_highlight_roles():
    assert "(122, 193, 67, 255)" in D2PFX
    assert "color=(255, 255, 0)" in D2PFX
    assert "color=(0, 255, 255)" not in D2PFX


def test_source_screenshot_spatial_color_roles_are_materialized():
    assert "BACKGROUND = JSON_WINDOW_BG" in THEME
    assert "SURFACE = JSON_BASE_BG" in THEME
    assert "SURFACE_RAISED = JSON_BUTTON_BG" in THEME
    assert "dpg.add_theme_color(dpg.mvThemeCol_Button, SUCCESS)" in THEME
    assert "dpg.add_theme_color(dpg.mvThemeCol_Text, JSON_BASE_ALT)" in THEME
    assert "UI_PANEL = (88, 108, 114, 255)" in CHECKBOXES
    assert "UI_RAISED = (133, 56, 148, 255)" in CHECKBOXES
    assert "dpg.add_theme_color(dpg.mvThemeCol_Header, (122, 193, 67, 230))" in D2PFX
    assert "dpg.add_theme_color(dpg.mvThemeCol_Text, (0, 0, 0))" in D2PFX


def test_redundant_left_status_and_footer_dev_entry_are_hidden_at_runtime():
    assert 'dpg.configure_item("nav_workspace_label", show=False)' in WINDOW
    assert 'dpg.configure_item("nav_status_card", show=False)' in WINDOW
    assert 'dpg.configure_item("button_dev", show=False)' in WINDOW
    assert "nav_status_height" not in WINDOW
    assert 'dpg.configure_item("nav_status_card", height=' not in WINDOW


def test_developer_tools_live_in_control_panel_tab_not_floating_windows():
    assert "def install_control_panel_tab():" in DEVTOOLS
    assert 'tag="settings_tabs"' in DEVTOOLS
    assert 'tag="settings_general_tab"' in DEVTOOLS
    assert 'tag="settings_developer_tab"' in DEVTOOLS
    assert 'label="DEVELOPER"' in DEVTOOLS
    assert 'dpg.move_item("settings_content_group", parent="settings_general_tab")' in DEVTOOLS
    assert 'render_panel("settings_developer_tab")' in DEVTOOLS
    assert 'window.show_overlay("settings_menu")' in DEVTOOLS
    assert "with dpg.window(" not in DEVTOOLS
    assert "dpg.configure_viewport(" not in DEVTOOLS


def test_header_is_reduced_to_centered_minify_release_lines():
    assert 'dpg.configure_item("header_brand_group", horizontal=False)' in WINDOW
    assert 'dpg.set_value("app_product_name", f"RELEASE: {base.VERSION}")' in WINDOW
    assert 'dpg.configure_item("app_version", show=False)' in WINDOW
    assert "HEADER_BRAND_WIDTH = 340" in WINDOW
    assert 'dpg.configure_item("app_title", indent=max(0, (HEADER_BRAND_WIDTH - title_width) // 2))' in WINDOW
    assert 'dpg.configure_item("app_product_name", indent=max(0, (HEADER_BRAND_WIDTH - release_width) // 2))' in WINDOW


def test_viewport_has_safe_minimum_layout_budget():
    assert "MIN_VIEWPORT_WIDTH = 960" in MAIN
    assert "MIN_VIEWPORT_HEIGHT = 680" in MAIN
    assert "min_width=MIN_VIEWPORT_WIDTH" in MAIN
    assert "min_height=MIN_VIEWPORT_HEIGHT" in MAIN
    assert "base_shell_height = max(360, min(520, shared.window_height - 300))" in WINDOW
    assert "shell_body_height = min(520, max(base_shell_height, required_inner_height + 34))" in WINDOW


def test_minimum_width_fit_contract_covers_primary_library_and_d2pfx():
    assert "compact_width = shared.window_width <= 1000" in WINDOW
    assert "nav_min_width = 160 if compact_width else 176" in WINDOW
    assert "action_cluster_width = max(260, min(620, main_width - 28))" in WINDOW
    assert 'dpg.configure_item("activity_header", width=content_width, height=36)' in WINDOW
    assert "content_width = max(320, shared.window_width - CONTENT_INSET)" in WINDOW
    assert "settings_width = content_width" in WINDOW
    assert 'with dpg.child_window(width=168, tag="d2pfx_sidebar"):' in D2PFX
    assert "init_width_or_weight=320" in D2PFX
    assert 'tag="d2pfx_cat_desc", wrap=360' in D2PFX
    assert "new_cols = max(2, min(4, int(content_width / 240)))" in D2PFX
    assert "wrap=max(220, _list_width() - 64)" in CHECKBOXES


def test_minimum_height_contract_keeps_navigation_and_library_controls_accessible():
    assert '"app_nav_rail",\n            width=nav_width,\n            height=shell_body_height,\n            no_scrollbar=False' in WINDOW
    assert 'dpg.configure_item("mod_source_rail", no_scrollbar=False, no_scroll_with_mouse=False)' in WINDOW
    assert 'dpg.configure_item("terminal_window", width=content_width)' in WINDOW
    assert 'dpg.configure_item("footer", width=content_width)' in WINDOW


def test_minimum_height_contract_bounds_d2pfx_and_auxiliary_scroll_regions():
    assert "d2pfx_content_height = max(MIN_D2PFX_CONTENT_HEIGHT, shared.window_height - 64)" in WINDOW
    assert "d2pfx_mods_height = max(180, d2pfx_content_height - D2PFX_HEADER_BUDGET)" in WINDOW
    assert 'dpg.configure_item("d2pfx_mods_view", height=d2pfx_mods_height, no_scrollbar=False)' in WINDOW
    assert 'dpg.configure_item("conflict_list", height=max(220, min(410, shared.window_height - 320)))' in WINDOW
    assert 'dpg.configure_item("d2pfx_import_preview", height=max(150, min(230, shared.window_height - 350)))' in WINDOW


def test_registered_browser_windows_resize_before_browser_layout_hooks():
    resize_tag_index = WINDOW.index('for window_tag in getattr(browser_config, "RESIZE_TAGS", [])')
    hook_index = WINDOW.index('if hasattr(browser_config, "on_resize"):', resize_tag_index)
    assert resize_tag_index < hook_index
