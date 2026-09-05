"""Mod Library workspace and state management.

v21.2 keeps the responsive source rail/search-first workspace and adds a restrained
beveled depth pass to controls, section headers, list surfaces, and command strips.
"""

from __future__ import annotations

import concurrent.futures
import datetime as dt
import json
import os
import shlex
import threading
import traceback

import conditions
import dearpygui.dearpygui as dpg
import helper
import jsonc
from core import (
    backup_manager,
    base,
    config,
    constants,
    fs,
    mod_compat,
    mod_library,
    mods_shared,
    output,
    registry,
    utils,
)
from patch import manifest_utils
from ui import details, localization, settings, shared, theme

checkboxes = []
checkboxes_state = {}
profile_cache = {}
mod_sections = {}
section_members = {"standard": [], "d2pfx": [], "vpk": [], "unknown": []}
collection_headers = {}
collection_members = {}
d2pfx_category_headers = {}
d2pfx_category_members = {}

SECTION_TAGS = {
    "standard": "standard_mods_header",
    "d2pfx": "d2pfx_mods_header",
    "vpk": "vpk_mods_header",
    "unknown": "unknown_vpk_mods_header",
}
SECTION_LABELS = {
    "standard": "Standard Mods",
    "d2pfx": "D2PFX Mods",
    "vpk": "VPK Mods",
    "unknown": "Unknown VPKs",
}

PROFILE_FILE_NAME = "mod-profiles.json"
PROFILE_EXPORT_FORMAT = "minify-mod-profiles"
PROFILE_EXPORT_VERSION = 1
PROFILE_MAX_FILE_BYTES = 8 * 1024 * 1024
PROFILE_MAX_COUNT = 256
PROFILE_MAX_STATES_PER_PROFILE = 5000
PROFILE_MAX_TOTAL_STATES = 20000
PROFILE_MAX_NAME_CHARS = 128
PROFILE_MAX_MOD_ID_CHARS = 512
PROFILE_MAX_HINT_CHARS = 512
STATE_FILTER_ITEMS = ["All", "Selected", "Unselected"]
TYPE_FILTER_ITEMS = ["All Mods", "Standard", "Collections", "D2PFX", "VPK", "Unknown", "Favorites"]
SORT_ITEMS = [
    "Name A-Z",
    "Name Z-A",
    "Category",
    "Enabled First",
    "Disabled First",
    "Source",
    "Recently Added",
    "File Priority",
]

TOOLBAR_HEIGHT = 152
STATUSBAR_HEIGHT = 108
SOURCE_RAIL_MIN_WIDTH = 144
SOURCE_RAIL_MAX_WIDTH = 196
MIN_SEARCH_WIDTH = 260
UI_ACCENT = (133, 56, 148, 255)
UI_ACCENT_HOVER = (169, 98, 183, 255)
UI_EMBER = (223, 80, 59, 255)
UI_EMBER_HOVER = (244, 102, 82, 255)
UI_TEXT = (247, 240, 231, 255)
UI_MUTED = (217, 199, 176, 255)
UI_PANEL = (88, 108, 114, 255)
UI_PANEL_ALT = (74, 92, 98, 255)
UI_RAISED = (133, 56, 148, 255)
UI_RECESSED = (72, 89, 94, 255)
UI_PANEL_HOVER = (101, 122, 128, 255)
UI_BORDER = (42, 38, 48, 255)
UI_BEVEL_LIGHT = (164, 143, 123, 255)
UI_BEVEL_DARK = (0, 0, 0, 210)
UI_D2PFX = (255, 255, 0, 255)
UI_COLLECTION = (255, 195, 15, 255)
UI_VPK = (122, 193, 67, 255)
UI_WARNING = (255, 195, 15, 255)
UI_ERROR = (223, 80, 59, 255)
UI_SUCCESS = (122, 193, 67, 255)

ui_state = {
    "search": "",
    "state_filter": "All",
    "type_filter": "All Mods",
    "category_filter": "All Categories",
    "sort": "Name A-Z",
}
last_error_text = ""
last_conflicts = []
active_action_mod = None
backup_display_map = {}
d2pfx_url_preview = None

AUXILIARY_WINDOWS = (
    "mod_actions_window",
    "patch_preview_window",
    "backup_manager_window",
    "error_details_window",
    "d2pfx_import_window",
    "d2pfx_import_dialog",
    "profile_export_dialog",
    "profile_import_dialog",
)


def _ensure_ui_themes():
    if dpg.does_item_exist("mod_manager_toolbar_theme"):
        return

    with dpg.theme(tag="mod_manager_toolbar_theme"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, UI_TEXT)
            dpg.add_theme_color(dpg.mvThemeCol_TextDisabled, UI_MUTED)
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, UI_PANEL)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, UI_RECESSED)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, UI_PANEL_HOVER)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (51, 60, 72, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Button, UI_RAISED)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, UI_PANEL_HOVER)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (51, 60, 72, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Border, UI_BEVEL_LIGHT)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, UI_BEVEL_DARK)
            dpg.add_theme_color(dpg.mvThemeCol_CheckMark, UI_ACCENT)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=8, y=6)
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, x=6, y=5)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, x=6, y=3)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 7)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)

    with dpg.theme(tag="mod_manager_list_theme"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, UI_TEXT)
            dpg.add_theme_color(dpg.mvThemeCol_TextDisabled, UI_MUTED)
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, UI_RECESSED)
            dpg.add_theme_color(dpg.mvThemeCol_Header, UI_PANEL_ALT)
            dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, UI_PANEL_HOVER)
            dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (51, 60, 72, 255))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (17, 22, 29, 255))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, UI_PANEL_HOVER)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (51, 60, 72, 255))
            dpg.add_theme_color(dpg.mvThemeCol_CheckMark, UI_ACCENT)
            dpg.add_theme_color(dpg.mvThemeCol_Button, UI_RAISED)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, UI_PANEL_HOVER)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (51, 60, 72, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Border, UI_BEVEL_LIGHT)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, UI_BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=8, y=7)
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, x=7, y=4)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, x=5, y=3)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 7)

    # Standard stays neutral; special source types get restrained identifiers.
    with dpg.theme(tag="mod_manager_section_theme"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, UI_TEXT)
            dpg.add_theme_color(dpg.mvThemeCol_Header, (28, 33, 41, 255))
            dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, UI_PANEL_HOVER)
            dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (17, 23, 31, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Border, UI_BEVEL_LIGHT)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, UI_BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, x=7, y=5)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)

    with dpg.theme(tag="mod_manager_collection_section_theme"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, UI_COLLECTION)
            dpg.add_theme_color(dpg.mvThemeCol_Header, (39, 34, 27, 255))
            dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (54, 45, 32, 255))
            dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (65, 52, 35, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Border, UI_BEVEL_LIGHT)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, UI_BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, x=7, y=5)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)

    with dpg.theme(tag="mod_manager_d2pfx_section_theme"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, UI_D2PFX)
            dpg.add_theme_color(dpg.mvThemeCol_Header, (24, 38, 40, 255))
            dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (31, 51, 53, 255))
            dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (37, 61, 62, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Border, UI_BEVEL_LIGHT)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, UI_BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, x=7, y=5)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)

    with dpg.theme(tag="mod_manager_vpk_section_theme"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, UI_VPK)
            dpg.add_theme_color(dpg.mvThemeCol_Header, (29, 38, 31, 255))
            dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (39, 50, 41, 255))
            dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (45, 59, 48, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Border, UI_BEVEL_LIGHT)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, UI_BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, x=7, y=5)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)

    with dpg.theme(tag="mod_manager_unknown_theme"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, UI_WARNING)
            dpg.add_theme_color(dpg.mvThemeCol_CheckMark, UI_WARNING)

    with dpg.theme(tag="mod_manager_unknown_section_theme"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, UI_WARNING)
            dpg.add_theme_color(dpg.mvThemeCol_Header, (43, 36, 25, 255))
            dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (57, 47, 30, 255))
            dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (66, 55, 34, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Border, UI_BEVEL_LIGHT)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, UI_BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, x=7, y=5)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)

    with dpg.theme(tag="mod_manager_d2pfx_category_theme"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, UI_D2PFX)

    with dpg.theme(tag="mod_manager_heading_theme"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, UI_ACCENT_HOVER)

    with dpg.theme(tag="mod_manager_muted_theme"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, UI_MUTED)

    with dpg.theme(tag="mod_manager_warning_theme"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, UI_WARNING)

    with dpg.theme(tag="mod_manager_error_theme"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, UI_ERROR)

    with dpg.theme(tag="mod_manager_success_theme"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, UI_SUCCESS)

    with dpg.theme(tag="mod_manager_primary_theme"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, (25, 13, 10, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Button, UI_EMBER)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, UI_EMBER_HOVER)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (204, 80, 55, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Border, UI_EMBER_HOVER)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, UI_BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)

    with dpg.theme(tag="mod_manager_card_theme"):
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, UI_PANEL)
            dpg.add_theme_color(dpg.mvThemeCol_Border, UI_BEVEL_LIGHT)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, UI_BEVEL_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 7)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=10, y=7)


def _add_tooltip(item, text):
    if dpg.does_item_exist(item):
        with dpg.tooltip(parent=item):
            dpg.add_text(text)


def _current_menu_width():
    width = getattr(shared, "window_width", 0) or base.main_window_width
    return max(base.main_window_width, int(width))


def _current_menu_height():
    height = getattr(shared, "window_height", 0) or base.main_window_height
    return max(base.main_window_height, int(height))


def _source_rail_width(width=None):
    width = int(width or _current_menu_width())
    return max(SOURCE_RAIL_MIN_WIDTH, min(SOURCE_RAIL_MAX_WIDTH, int(width * 0.165)))


def _search_width(width=None):
    width = int(width or _current_menu_width())
    return max(MIN_SEARCH_WIDTH, width - 40)


def _list_width(width=None):
    width = int(width or _current_menu_width())
    return max(260, width - _source_rail_width(width) - 28)


def _row_action_indent(width=None):
    return max(180, _list_width(width) - 116)


def _center_window(tag, width, height):
    vw = _current_menu_width()
    vh = _current_menu_height()
    dpg.configure_item(tag, width=min(width, vw - 30), height=min(height, vh - 30))
    dpg.set_item_pos(tag, (max(0, (vw - width) // 2), max(0, (vh - height) // 2)))


def on_resize(width=None, height=None):
    width = int(width or _current_menu_width())
    height = int(height or _current_menu_height())
    body_height = max(196, height - TOOLBAR_HEIGHT - STATUSBAR_HEIGHT - 36)
    list_width = _list_width(width)

    if dpg.does_item_exist("mod_manager_toolbar"):
        dpg.configure_item("mod_manager_toolbar", width=max(100, width - 16), height=TOOLBAR_HEIGHT)
    if dpg.does_item_exist("mod_source_rail"):
        dpg.configure_item("mod_source_rail", width=_source_rail_width(width), height=body_height)
    if dpg.does_item_exist("mod_manager_list"):
        dpg.configure_item("mod_manager_list", width=list_width, height=body_height)
    if dpg.does_item_exist("mod_manager_statusbar"):
        dpg.configure_item("mod_manager_statusbar", width=max(100, width - 16), height=STATUSBAR_HEIGHT)
    if dpg.does_item_exist("mod_search"):
        dpg.configure_item("mod_search", width=_search_width(width))
    for tag in ("profile_select", "profile_name"):
        if dpg.does_item_exist(tag):
            dpg.configure_item(tag, width=max(180, list_width - 24))
    if dpg.does_item_exist("mod_manager_status_text"):
        dpg.configure_item("mod_manager_status_text", wrap=max(220, width - 34))

    indent = _row_action_indent(width)
    meta_wrap = max(220, list_width - 64)
    for mod in checkboxes:
        tag = f"{mod}_favorite_button"
        if dpg.does_item_exist(tag):
            dpg.configure_item(tag, indent=indent)
        meta_tag = f"{mod}_meta"
        if dpg.does_item_exist(meta_tag):
            dpg.configure_item(meta_tag, wrap=meta_wrap)


def _capture_ui_state(*, capture_search=True):
    mapping = {
        "mod_search": "search",
        "mod_state_filter": "state_filter",
        "mod_type_filter": "type_filter",
        "mod_category_filter": "category_filter",
        "mod_sort": "sort",
    }
    for tag, key in mapping.items():
        if key == "search" and not capture_search:
            continue
        if not dpg.does_item_exist(tag):
            continue
        value = dpg.get_value(tag)
        # Empty text is a valid search value. Falling back with ``or`` here
        # retained the previous query when the user erased the search box.
        if key == "search":
            ui_state[key] = str(value or "")
        elif value not in (None, ""):
            ui_state[key] = str(value)


def _profile_path():
    return os.path.join(base.config_dir, PROFILE_FILE_NAME)


def _normalize_profile_states(states):
    if not isinstance(states, dict):
        raise ValueError("Profile mod states must be a JSON object.")
    if len(states) > PROFILE_MAX_STATES_PER_PROFILE:
        raise ValueError("Profile contains too many mod states.")

    normalized = {}
    for mod, enabled in states.items():
        if not isinstance(mod, str) or not mod or len(mod) > PROFILE_MAX_MOD_ID_CHARS:
            raise ValueError("Profile contains an invalid mod identifier.")
        if not isinstance(enabled, bool):
            raise ValueError("Profile mod states must use JSON booleans.")
        normalized[mod] = enabled
    return normalized


def _normalize_profiles_mapping(profiles):
    if not isinstance(profiles, dict):
        raise ValueError("Profiles must be a JSON object.")
    if len(profiles) > PROFILE_MAX_COUNT:
        raise ValueError("Profile bundle contains too many profiles.")

    normalized = {}
    total_states = 0
    for name, value in profiles.items():
        if not isinstance(name, str):
            raise ValueError("Profile names must be strings.")
        name = name.strip()
        if not name or len(name) > PROFILE_MAX_NAME_CHARS or not isinstance(value, dict):
            raise ValueError("Profile contains an invalid name or value.")
        states = value.get("mods", value)
        normalized_states = _normalize_profile_states(states)
        total_states += len(normalized_states)
        if total_states > PROFILE_MAX_TOTAL_STATES:
            raise ValueError("Profile bundle contains too many total mod states.")
        normalized[name] = normalized_states
    return normalized


def _normalize_profile_hints(hints, referenced):
    if hints in (None, {}):
        return {}
    if not isinstance(hints, dict) or len(hints) > PROFILE_MAX_TOTAL_STATES:
        raise ValueError("Profile mod hints are invalid or excessive.")

    normalized = {}
    for mod, hint in hints.items():
        if mod not in referenced:
            continue
        if not isinstance(mod, str) or len(mod) > PROFILE_MAX_MOD_ID_CHARS or not isinstance(hint, dict):
            raise ValueError("Profile contains an invalid mod hint.")
        clean = {}
        for key in ("display_name", "source", "stable_key"):
            value = hint.get(key, "")
            if value is None:
                value = ""
            if not isinstance(value, str) or len(value) > PROFILE_MAX_HINT_CHARS:
                raise ValueError("Profile contains an invalid mod hint value.")
            clean[key] = value
        normalized[mod] = clean
    return normalized


def _load_profiles():
    global profile_cache
    try:
        path = _profile_path()
        if os.path.islink(path) or not os.path.isfile(path):
            raise FileNotFoundError(path)
        if os.path.getsize(path) > PROFILE_MAX_FILE_BYTES:
            raise ValueError("Saved profile file exceeds the safety limit.")
        with open(path, encoding="utf-8-sig") as file:
            data = json.load(file)
        profiles = data.get("profiles", data) if isinstance(data, dict) else {}
        profile_cache = _normalize_profiles_mapping(profiles)
    except Exception:
        profile_cache = {}
    return profile_cache


def _write_profiles():
    os.makedirs(base.config_dir, exist_ok=True)
    temp = _profile_path() + ".tmp"
    payload = {
        "version": 2,
        "profiles": {
            name: {"mods": states}
            for name, states in sorted(profile_cache.items(), key=lambda item: item[0].casefold())
        },
    }
    with open(temp, "w", encoding="utf-8", newline="\n") as file:
        json.dump(payload, file, indent=2, ensure_ascii=False)
    os.replace(temp, _profile_path())


def _refresh_profile_combo(selected=None):
    if not dpg.does_item_exist("profile_select"):
        return
    names = sorted(profile_cache, key=str.casefold)
    dpg.configure_item("profile_select", items=names)
    if selected in profile_cache:
        dpg.set_value("profile_select", selected)
    elif names:
        current = str(dpg.get_value("profile_select") or "")
        dpg.set_value("profile_select", current if current in profile_cache else names[0])
    else:
        dpg.set_value("profile_select", "")


def _profile_export_payload():
    """Build a portable profile bundle with best-effort mod identity hints."""
    referenced = set()
    for states in profile_cache.values():
        if isinstance(states, dict):
            referenced.update(str(mod) for mod in states)

    hints = {}
    for mod in sorted(referenced, key=str.casefold):
        hint = {"display_name": mod, "source": "", "stable_key": ""}
        try:
            hint["display_name"] = str(mods_shared.get_mod_label(mod) or mod)
            hint["source"] = str(mods_shared.get_mod_source(mod) or "")
            if mod in checkboxes or dpg.does_item_exist(mod):
                hint["stable_key"] = str(mod_library.stable_key(mod, calculate_hash=False) or "")
        except Exception:
            pass
        hints[mod] = hint

    return {
        "format": PROFILE_EXPORT_FORMAT,
        "version": PROFILE_EXPORT_VERSION,
        "exported_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "profiles": {
            name: {"mods": dict(states)}
            for name, states in sorted(profile_cache.items(), key=lambda item: item[0].casefold())
        },
        "mod_hints": hints,
    }


def _unique_profile_export_path(directory):
    base_name = "Minify-Profiles.json"
    candidate = os.path.join(directory, base_name)
    if not os.path.exists(candidate):
        return candidate
    counter = 2
    while True:
        candidate = os.path.join(directory, f"Minify-Profiles-{counter}.json")
        if not os.path.exists(candidate):
            return candidate
        counter += 1


def _dialog_directory(app_data):
    if not isinstance(app_data, dict):
        return ""
    for key in ("file_path_name", "current_path"):
        value = app_data.get(key)
        if value:
            path = os.path.abspath(str(value))
            return os.path.dirname(path) if os.path.isfile(path) else path
    selections = app_data.get("selections")
    if isinstance(selections, dict) and selections:
        path = os.path.abspath(str(next(iter(selections.values()))))
        return os.path.dirname(path) if os.path.isfile(path) else path
    return ""


def choose_profile_export_directory(sender=None, app_data=None, user_data=None):
    if dpg.does_item_exist("profile_export_dialog"):
        dpg.configure_item("profile_export_dialog", show=True)


def export_profiles_callback(sender=None, app_data=None, user_data=None):
    directory = _dialog_directory(app_data)
    if not directory:
        set_status("Profile export cancelled.", "ready")
        return
    try:
        os.makedirs(directory, exist_ok=True)
        path = _unique_profile_export_path(directory)
        payload = _profile_export_payload()
        with open(path, "w", encoding="utf-8", newline="\n") as file:
            json.dump(payload, file, indent=2, ensure_ascii=False)
        output.add_text(f"Exported {len(profile_cache)} profile(s) to {path}", msg_type="success")
        set_status(f"Profiles exported: {os.path.basename(path)}", "success")
    except Exception:
        report_patch_error(traceback.format_exc())
        output.add_text("Profile export failed. Open Error Details for technical information.", msg_type="error")
        set_status("Profile export failed.", "error")


def choose_profile_import_file(sender=None, app_data=None, user_data=None):
    if dpg.does_item_exist("profile_import_dialog"):
        dpg.configure_item("profile_import_dialog", show=True)


def _normalized_import_profiles(data):
    try:
        if not isinstance(data, dict):
            raise ValueError("Profile bundle must be a JSON object.")
        if "format" in data:
            if data.get("format") != PROFILE_EXPORT_FORMAT or data.get("version") != PROFILE_EXPORT_VERSION:
                raise ValueError("Unsupported Minify profile export format/version.")
        profiles = data.get("profiles", data)
        normalized = _normalize_profiles_mapping(profiles)
        referenced = {mod for states in normalized.values() for mod in states}
        hints = _normalize_profile_hints(data.get("mod_hints", {}), referenced)
        return normalized, hints
    except ValueError:
        return {}, {}


def _current_profile_identity_indexes():
    stable_index = {}
    friendly_index = {}
    for mod in checkboxes:
        try:
            stable = str(mod_library.stable_key(mod, calculate_hash=False) or "")
            if stable:
                stable_index.setdefault(stable, []).append(mod)
            friendly = (
                str(mods_shared.get_mod_label(mod) or mod).strip().casefold(),
                str(mods_shared.get_mod_source(mod) or "").strip().casefold(),
            )
            friendly_index.setdefault(friendly, []).append(mod)
        except Exception:
            continue
    return stable_index, friendly_index


def _remap_imported_states(states, hints):
    current = set(checkboxes)
    stable_index, friendly_index = _current_profile_identity_indexes()
    remapped = {}
    remap_count = 0

    for imported_mod, enabled in states.items():
        target = imported_mod
        if imported_mod not in current:
            hint = hints.get(imported_mod, {}) if isinstance(hints, dict) else {}
            if isinstance(hint, dict):
                stable = str(hint.get("stable_key", "") or "")
                stable_matches = stable_index.get(stable, []) if stable else []
                if len(stable_matches) == 1:
                    target = stable_matches[0]
                else:
                    friendly = (
                        str(hint.get("display_name", imported_mod) or imported_mod).strip().casefold(),
                        str(hint.get("source", "") or "").strip().casefold(),
                    )
                    friendly_matches = friendly_index.get(friendly, [])
                    if len(friendly_matches) == 1:
                        target = friendly_matches[0]
        if target != imported_mod:
            remap_count += 1
        remapped[target] = bool(enabled)

    return remapped, remap_count


def _unique_imported_profile_name(name):
    if name not in profile_cache:
        return name
    base_name = f"{name} (Imported)"
    candidate = base_name
    counter = 2
    while candidate in profile_cache:
        candidate = f"{base_name} {counter}"
        counter += 1
    return candidate


def import_profiles_callback(sender=None, app_data=None, user_data=None):
    path = _file_dialog_path(app_data)
    if not path:
        set_status("Profile import cancelled.", "ready")
        return

    try:
        if not os.path.isfile(path):
            raise ValueError("Selected profile import is not a regular file.")
        if os.path.getsize(path) > PROFILE_MAX_FILE_BYTES:
            raise ValueError("Selected profile import exceeds the safety limit.")
        with open(path, encoding="utf-8-sig") as file:
            data = json.load(file)
        imported, hints = _normalized_import_profiles(data)
        if not imported:
            raise ValueError("No valid Minify profiles were found in the selected JSON file.")

        added = 0
        duplicates = 0
        renamed = 0
        remapped = 0
        imported_targets = []

        for name, states in imported.items():
            mapped_states, mapped_count = _remap_imported_states(states, hints)
            remapped += mapped_count

            if name in profile_cache and profile_cache[name] == mapped_states:
                duplicates += 1
                imported_targets.append(name)
                continue

            target_name = name
            if target_name in profile_cache:
                target_name = _unique_imported_profile_name(name)
                renamed += 1

            profile_cache[target_name] = mapped_states
            imported_targets.append(target_name)
            added += 1

        if added:
            _write_profiles()

        applied_name = imported_targets[0] if imported_targets else None
        _refresh_profile_combo(applied_name)
        if applied_name and applied_name in profile_cache:
            _apply_profile_states(applied_name, profile_cache[applied_name])

        details = [f"{added} imported"]
        if duplicates:
            details.append(f"{duplicates} duplicate(s) skipped")
        if renamed:
            details.append(f"{renamed} name collision(s) preserved")
        if remapped:
            details.append(f"{remapped} mod ID(s) remapped")
        summary = ", ".join(details)
        if applied_name:
            output.add_text(
                f"Profile bundle imported from {path}: {summary}. Applied '{applied_name}'.",
                msg_type="success",
            )
            if len(imported_targets) > 1:
                set_status(
                    f"Profiles imported: {summary}. Applied {applied_name}; choose another saved setup to switch.",
                    "success",
                )
            else:
                set_status(f"Profiles imported and applied: {applied_name}.", "success")
        else:
            output.add_text(f"Profile bundle imported from {path}: {summary}.", msg_type="success")
            set_status(f"Profiles imported: {summary}.", "success")
    except Exception:
        report_patch_error(traceback.format_exc())
        output.add_text("Profile import failed. Open Error Details for technical information.", msg_type="error")
        set_status("Profile import failed.", "error")


def open_profiles_folder(sender=None, app_data=None, user_data=None):
    os.makedirs(base.config_dir, exist_ok=True)
    fs.open_thing(base.config_dir)


def _current_states():
    states = {}
    for mod in checkboxes:
        if dpg.does_item_exist(mod):
            states[mod] = bool(dpg.get_value(mod))
    return states


def save_profile(sender=None, app_data=None, user_data=None):
    name = str(dpg.get_value("profile_name") or "").strip() if dpg.does_item_exist("profile_name") else ""
    if not name:
        output.add_text("Enter a profile name before saving.", msg_type="warning")
        return
    if len(name) > PROFILE_MAX_NAME_CHARS:
        output.add_text(f"Profile names are limited to {PROFILE_MAX_NAME_CHARS} characters.", msg_type="warning")
        return
    profile_cache[name] = _current_states()
    _write_profiles()
    _refresh_profile_combo(name)
    set_status(f"Profile saved: {name}", "success")


def update_profile(sender=None, app_data=None, user_data=None):
    name = str(dpg.get_value("profile_select") or "").strip() if dpg.does_item_exist("profile_select") else ""
    if not name or name not in profile_cache:
        output.add_text("Choose a saved profile first.", msg_type="warning")
        return
    profile_cache[name] = _current_states()
    _write_profiles()
    set_status(f"Profile updated: {name}", "success")


def _apply_profile_states(name, states):
    """Apply a complete saved setup to the live Mod Library checkboxes.

    Profiles are snapshots, so mods omitted from the profile are turned off.
    Checkboxes disabled by Minify/runtime requirements are left untouched.
    """
    if not isinstance(states, dict):
        return False

    applied = 0
    unavailable = 0
    current = set(checkboxes)
    missing = len(set(states) - current)

    for mod in checkboxes:
        if not dpg.does_item_exist(mod):
            continue
        if not _is_enabled_checkbox(mod):
            unavailable += 1
            continue
        dpg.set_value(mod, bool(states.get(mod, False)))
        applied += 1

    setup_state()
    details = [f"{applied} mod state(s) applied"]
    if unavailable:
        details.append(f"{unavailable} locked")
    if missing:
        details.append(f"{missing} unavailable in this build")
    set_status(f"Profile applied: {name} • {', '.join(details)}", "success")
    return True


def profile_selected(sender=None, app_data=None, user_data=None):
    """Apply a saved setup as soon as the user selects it in the profile combo."""
    name = str(app_data or "").strip()
    if not name and dpg.does_item_exist("profile_select"):
        name = str(dpg.get_value("profile_select") or "").strip()
    states = profile_cache.get(name)
    if states is None:
        return False
    return _apply_profile_states(name, states)


def load_profile(sender=None, app_data=None, user_data=None):
    name = str(dpg.get_value("profile_select") or "").strip() if dpg.does_item_exist("profile_select") else ""
    states = profile_cache.get(name)
    if states is None:
        output.add_text("Choose a saved profile first.", msg_type="warning")
        return False
    return _apply_profile_states(name, states)


def duplicate_profile(sender=None, app_data=None, user_data=None):
    name = str(dpg.get_value("profile_select") or "").strip() if dpg.does_item_exist("profile_select") else ""
    if not name or name not in profile_cache:
        output.add_text("Choose a saved profile first.", msg_type="warning")
        return
    base_name = f"{name} Copy"
    new_name = base_name
    counter = 2
    while new_name in profile_cache:
        new_name = f"{base_name} {counter}"
        counter += 1
    profile_cache[new_name] = dict(profile_cache[name])
    _write_profiles()
    _refresh_profile_combo(new_name)
    set_status(f"Profile duplicated: {new_name}", "success")


def delete_profile(sender=None, app_data=None, user_data=None):
    name = str(dpg.get_value("profile_select") or "").strip() if dpg.does_item_exist("profile_select") else ""
    if not name or name not in profile_cache:
        output.add_text("Choose a saved profile first.", msg_type="warning")
        return
    del profile_cache[name]
    _write_profiles()
    _refresh_profile_combo()
    set_status(f"Profile deleted: {name}", "ready")


def open_vpk_folder(sender=None, app_data=None, user_data=None):
    path = os.path.join(base.mods_dir, mods_shared.VPK_COLLECTION_DIR)
    os.makedirs(path, exist_ok=True)
    fs.open_thing(path)


def load():
    global checkboxes_state
    try:
        with utils.open_utf8(base.mods_config_dir) as file:
            checkboxes_state = jsonc.load(file)
    except Exception:
        checkboxes_state = {}
        with utils.open_utf8(base.mods_config_dir, "w") as file:
            jsonc.dump({}, file)
    if not isinstance(checkboxes_state, dict):
        checkboxes_state = {}
    for mod in constants.visually_unavailable_mods:
        checkboxes_state.setdefault(mod, False)


def save():
    for box in checkboxes:
        if dpg.does_item_exist(box):
            checkboxes_state[box] = bool(dpg.get_value(box))
    with utils.open_utf8(base.mods_config_dir, "w") as file:
        jsonc.dump(dict(sorted(checkboxes_state.items())), file, indent=2)


def setup_state():
    save()
    settings.refresh()
    apply_filters()


def _is_enabled_checkbox(mod):
    if not dpg.does_item_exist(mod):
        return False
    return dpg.get_item_configuration(mod).get("enabled", True)


def _set_mod_values(mods, value):
    changed = False
    for mod in mods:
        if _is_enabled_checkbox(mod):
            dpg.set_value(mod, value)
            changed = True
    if changed:
        setup_state()


def check_all_mods(sender=None, app_data=None, user_data=None):
    _set_mod_values(checkboxes, True)


def uncheck_all_mods(sender=None, app_data=None, user_data=None):
    _set_mod_values(checkboxes, False)


def invert_all_mods(sender=None, app_data=None, user_data=None):
    changed = False
    for mod in checkboxes:
        if _is_enabled_checkbox(mod):
            dpg.set_value(mod, not bool(dpg.get_value(mod)))
            changed = True
    if changed:
        setup_state()


def _set_all_sections(open_state):
    for header_tag in list(SECTION_TAGS.values()) + list(collection_headers.values()):
        if dpg.does_item_exist(header_tag) and dpg.is_item_shown(header_tag):
            with utils.try_pass():
                dpg.set_value(header_tag, bool(open_state))


def expand_all_sections(sender=None, app_data=None, user_data=None):
    _set_all_sections(True)


def collapse_all_sections(sender=None, app_data=None, user_data=None):
    _set_all_sections(False)


def clear_filters(sender=None, app_data=None, user_data=None):
    ui_state.update(
        {"search": "", "state_filter": "All", "type_filter": "All Mods", "category_filter": "All Categories"}
    )
    for tag, value in (
        ("mod_search", ""),
        ("mod_state_filter", "All"),
        ("mod_type_filter", "All Mods"),
        ("mod_category_filter", "All Categories"),
    ):
        if dpg.does_item_exist(tag):
            dpg.set_value(tag, value)
    apply_filters()


SOURCE_NAV = {
    "All Mods": "source_nav_all",
    "Standard": "source_nav_standard",
    "Collections": "source_nav_collections",
    "D2PFX": "source_nav_d2pfx",
    "VPK": "source_nav_vpk",
    "Unknown": "source_nav_unknown",
    "Favorites": "source_nav_favorites",
}


def _sync_source_nav():
    current = ui_state.get("type_filter", "All Mods")
    for value, tag in SOURCE_NAV.items():
        if dpg.does_item_exist(tag):
            dpg.bind_item_theme(
                tag,
                "mod_manager_nav_active_theme" if value == current else "mod_manager_nav_theme",
            )


def set_type_filter(sender=None, app_data=None, user_data=None):
    value = str(user_data or "All Mods")
    if value not in TYPE_FILTER_ITEMS:
        value = "All Mods"
    ui_state["type_filter"] = value
    if dpg.does_item_exist("mod_type_filter"):
        dpg.set_value("mod_type_filter", value)
    apply_filters(capture_search=False)


def set_section_mods(sender=None, app_data=None, user_data=None):
    if isinstance(user_data, (tuple, list)) and len(user_data) == 2:
        section, value = user_data
        if str(section).startswith("collection::"):
            group = str(section).split("::", 1)[1]
            _set_mod_values(collection_members.get(group, []), bool(value))
        else:
            _set_mod_values(section_members.get(section, []), bool(value))


def _display_name(mod):
    return mod_library.display_name(mod)


def _collection_group(mod):
    """Return the organizational parent for a nested local directory mod."""
    if not str(mod).startswith(mods_shared.NESTED_DIR_PREFIX):
        return ""
    if mod_library.is_d2pfx(mod):
        return ""
    return str(mods_shared.get_mod_group(mod) or "").strip()


def _collection_section_key(group):
    return f"collection::{group}"


def _category(mod):
    return mod_library.category(mod)


def _source(mod):
    return mod_library.source(mod)


def _is_unknown(mod):
    return mod.lower().endswith(".vpk") and not mods_shared.is_mod_identified(mod)


def _search_tokens(query):
    try:
        return shlex.split(query)
    except ValueError:
        return query.split()


def _bool_query(value):
    return str(value).casefold() in {"1", "true", "yes", "on", "enabled", "selected"}


def _mod_matches_search(mod, query, selected):
    if not query:
        return True

    label = _display_name(mod)
    filename = mods_shared.get_mod_filename(mod)
    category = _category(mod)
    source = _source(mod)
    is_vpk = mod.lower().endswith(".vpk")
    unknown = _is_unknown(mod)
    favorite = mod_library.is_favorite(mod)
    haystack = " ".join((label, filename, category, source)).casefold()

    for raw_token in _search_tokens(query):
        token = raw_token.casefold()
        if ":" not in token:
            if token not in haystack:
                return False
            continue

        field, value = token.split(":", 1)
        if field == "category" and value not in category.casefold():
            return False
        if field == "source" and value not in source.casefold():
            return False
        if field == "file" and value not in filename.casefold():
            return False
        if field == "type":
            wanted = value
            is_d2pfx = mod_library.is_d2pfx(mod)
            if wanted in {"standard", "mod"} and (is_vpk or is_d2pfx or _collection_group(mod)):
                return False
            if wanted in {"collection", "collections"} and not _collection_group(mod):
                return False
            if wanted == "d2pfx" and not is_d2pfx:
                return False
            if wanted == "vpk" and not is_vpk:
                return False
            if wanted == "unknown" and not unknown:
                return False
            if wanted == "identified" and (not is_vpk or unknown):
                return False
        if field in {"enabled", "selected"} and selected != _bool_query(value):
            return False
        if field == "favorite" and favorite != _bool_query(value):
            return False
        if field == "status":
            match = {
                "unknown": unknown,
                "identified": is_vpk and not unknown,
                "selected": selected,
                "unselected": not selected,
                "favorite": favorite,
            }.get(value, False)
            if not match:
                return False
    return True


def _type_matches(mod, type_filter):
    if type_filter == "All Mods":
        return True
    if type_filter == "Favorites":
        return mod_library.is_favorite(mod)
    if type_filter == "Standard":
        return not mod.lower().endswith(".vpk") and not mod_library.is_d2pfx(mod) and not _collection_group(mod)
    if type_filter == "Collections":
        return bool(_collection_group(mod))
    if type_filter == "D2PFX":
        return mod_library.is_d2pfx(mod)
    if type_filter == "VPK":
        return mod.lower().endswith(".vpk")
    if type_filter == "Unknown":
        return _is_unknown(mod)
    return True


def search_changed(sender=None, app_data=None, user_data=None):
    """Apply the input callback value directly, including the empty string.

    Dear PyGui provides the edited text in ``app_data``. Treating that callback
    value as authoritative prevents a stale widget read from resurrecting the
    previous query when the field is cleared during rapid filter changes.
    """
    ui_state["search"] = "" if app_data is None else str(app_data)
    apply_filters(capture_search=False)


def apply_filters(sender=None, app_data=None, user_data=None, *, capture_search=True):
    _capture_ui_state(capture_search=capture_search)
    query = ui_state["search"].strip().casefold()
    state_filter = ui_state["state_filter"]
    type_filter = ui_state["type_filter"]
    category_filter = ui_state["category_filter"]

    dynamic_members = dict(section_members)
    dynamic_members.update({_collection_section_key(group): members for group, members in collection_members.items()})
    visible_counts = {section: 0 for section in dynamic_members}
    selected_counts = {section: 0 for section in dynamic_members}
    visible_d2pfx_categories = {category: 0 for category in d2pfx_category_members}
    selected_total = 0
    visible_total = 0

    for mod in checkboxes:
        row_tag = f"{mod}_group_tag"
        if not dpg.does_item_exist(row_tag):
            continue
        selected = bool(dpg.get_value(mod)) if dpg.does_item_exist(mod) else False
        show = _mod_matches_search(mod, query, selected)
        show = show and _type_matches(mod, type_filter)
        if category_filter != "All Categories":
            show = show and _category(mod).casefold() == category_filter.casefold()
        if state_filter == "Selected":
            show = show and selected
        elif state_filter == "Unselected":
            show = show and not selected

        dpg.configure_item(row_tag, show=show)
        section = mod_sections.get(mod)
        if selected:
            selected_total += 1
            if section in selected_counts:
                selected_counts[section] += 1
        if show:
            visible_total += 1
            if section in visible_counts:
                visible_counts[section] += 1
            if section == "d2pfx":
                category = _category(mod) or "Other"
                visible_d2pfx_categories[category] = visible_d2pfx_categories.get(category, 0) + 1

    active_filter = bool(
        query or state_filter != "All" or type_filter != "All Mods" or category_filter != "All Categories"
    )
    for section, header_tag in SECTION_TAGS.items():
        if not dpg.does_item_exist(header_tag):
            continue
        total = len(section_members.get(section, []))
        visible = visible_counts.get(section, 0)
        selected = selected_counts.get(section, 0)
        label = f"{SECTION_LABELS[section]}  •  {selected}/{total} selected"
        if visible != total:
            label += f"  •  {visible} shown"
        dpg.configure_item(header_tag, show=visible > 0, label=label)
        if active_filter and visible > 0:
            with utils.try_pass():
                dpg.set_value(header_tag, True)

    # Nested directory collections are first-class collapsible sections, not
    # part of the Standard Mods header. Each parent keeps its own selected and
    # visible counts and can be expanded/collapsed independently. Selecting the
    # Collections source alone must not force every collection open.
    collection_auto_open = bool(query or state_filter != "All" or category_filter != "All Categories")
    for group, header_tag in collection_headers.items():
        section_key = _collection_section_key(group)
        total = len(collection_members.get(group, []))
        visible = visible_counts.get(section_key, 0)
        selected = selected_counts.get(section_key, 0)
        label = f"{group}  •  {selected}/{total} selected"
        if visible != total:
            label += f"  •  {visible} shown"
        if dpg.does_item_exist(header_tag):
            dpg.configure_item(header_tag, show=visible > 0, label=label)
            if collection_auto_open and visible > 0:
                with utils.try_pass():
                    dpg.set_value(header_tag, True)

    # D2PFX is category-first both logically and visually. Hide empty category
    # dividers during search/filtering so clearing a query restores a clean,
    # continuous category layout instead of leaving orphan headings behind.
    for category, header_info in d2pfx_category_headers.items():
        header_tag, count_tag = header_info
        visible = visible_d2pfx_categories.get(category, 0)
        total_in_category = len(d2pfx_category_members.get(category, []))
        if dpg.does_item_exist(header_tag):
            dpg.configure_item(header_tag, show=visible > 0)
        if dpg.does_item_exist(count_tag):
            count_text = (
                f"{visible}/{total_in_category} shown" if visible != total_in_category else f"{total_in_category} mods"
            )
            dpg.set_value(count_tag, count_text)

    total = len(checkboxes)
    status = f"{selected_total} selected • {total} installed"
    if visible_total != total:
        status += f" • {visible_total} shown"
    # Keep the Mod Library and home Patch Workspace on the same live summary.
    # The dashboard control is named dashboard_metric; an earlier UI pass
    # accidentally targeted a nonexistent dashboard tag, leaving
    # the home screen permanently at its hard-coded 0 selected / 0 installed.
    for tag in ("mod_selection_status", "dashboard_metric"):
        if dpg.does_item_exist(tag):
            dpg.set_value(tag, status)
    _sync_source_nav()
    if dpg.does_item_exist("mod_empty_state"):
        dpg.configure_item("mod_empty_state", show=visible_total == 0)


def _sort_key(mod):
    choice = ui_state.get("sort", "Name A-Z")
    name = _display_name(mod).casefold()
    category = _category(mod).casefold()
    source = _source(mod).casefold()
    selected = bool(checkboxes_state.get(mod, False))
    first_seen = mod_library.get_first_seen(mod)

    if choice == "Category":
        return (category, name)
    if choice == "Enabled First":
        return (0 if selected else 1, name)
    if choice == "Disabled First":
        return (0 if not selected else 1, name)
    if choice == "Source":
        return (source, name)
    if choice == "Recently Added":
        # ISO timestamps sort lexically; invert numeric-ish string by using a
        # tuple and reverse in _sort_mods.
        return (first_seen, name)
    if choice == "File Priority":
        try:
            priority = mods_shared.mods_with_order.index(mod)
        except ValueError:
            priority = 999999
        return (priority, name)
    return (name,)


def _sort_mods(mods):
    choice = ui_state.get("sort", "Name A-Z")
    reverse = choice in {"Name Z-A", "Recently Added"}
    return sorted(mods, key=_sort_key, reverse=reverse)


def _d2pfx_sort_key(mod):
    """Stable category -> display name -> filename key for D2PFX components."""
    return (
        (_category(mod) or "Other").strip().casefold(),
        _display_name(mod).strip().casefold(),
        mods_shared.get_mod_filename(mod).strip().casefold(),
    )


def _sort_d2pfx_mods(mods):
    """Keep D2PFX installs grouped predictably: category A-Z, then mod name A-Z."""
    return sorted(mods, key=_d2pfx_sort_key)


def _sort_changed(sender=None, app_data=None, user_data=None):
    _capture_ui_state()
    create()


def show_details(sender, app_data, user_data):
    mod = user_data.replace("_details_window_tag", "")
    details.render_details_window(mod)
    dpg.configure_item(user_data, show=True)
    dpg.focus_item(user_data)


def set_status(message, level="ready"):
    label = {
        "ready": "Ready",
        "working": "Working",
        "warning": "Needs attention",
        "error": "Problem",
        "success": "Done",
    }.get(level, str(level).title())
    text = f"{label}  •  {message}"

    if dpg.does_item_exist("mod_manager_status_text"):
        dpg.set_value("mod_manager_status_text", text)
        theme_tag = {
            "warning": "mod_manager_warning_theme",
            "error": "mod_manager_error_theme",
            "success": "mod_manager_success_theme",
        }.get(level, "mod_manager_muted_theme" if level == "ready" else "mod_manager_heading_theme")
        dpg.bind_item_theme("mod_manager_status_text", theme_tag)

    # The dashboard separates state from explanation so the eye can scan
    # Done / Working / Problem without parsing a full sentence.
    if dpg.does_item_exist("dashboard_status_label"):
        dpg.set_value("dashboard_status_label", f"● {label}")
        dashboard_theme = {
            "working": "dashboard_status_working_theme",
            "warning": "dashboard_status_warning_theme",
            "error": "dashboard_status_error_theme",
            "success": "dashboard_status_success_theme",
        }.get(level, "dashboard_status_ready_theme")
        dpg.bind_item_theme("dashboard_status_label", dashboard_theme)
    if dpg.does_item_exist("dashboard_status_message"):
        dpg.set_value("dashboard_status_message", str(message))

    if dpg.does_item_exist("status_error_details_button"):
        dpg.configure_item("status_error_details_button", show=bool(last_error_text))


def report_patch_error(error_text):
    global last_error_text
    last_error_text = str(error_text or "Unknown patch error")
    set_status("The patch did not finish. Technical details are available.", "error")


def show_error_details(sender=None, app_data=None, user_data=None):
    if not dpg.does_item_exist("error_details_window"):
        return
    dpg.set_value("error_details_text", last_error_text or "No error details are currently available.")
    _center_window("error_details_window", 700, 420)
    dpg.configure_item("error_details_window", show=True)
    dpg.focus_item("error_details_window")


def refresh(sender=None, app_data=None, user_data=None):
    set_status("Checking your mod folders for changes...", "working")
    mods_shared.scan_mods()
    mod_library.refresh_index()
    create()
    settings.refresh()
    output.add_text("&refreshed_mod_list")
    set_status("Mod library is up to date.", "success")


def toggle_favorite(sender=None, app_data=None, user_data=None):
    mod = str(user_data or "")
    if not mod:
        return
    value = mod_library.toggle_favorite(mod)
    tag = f"{mod}_favorite_button"
    if dpg.does_item_exist(tag):
        dpg.configure_item(tag, label="★" if value else "☆")
    apply_filters()


def _meta_text(mod):
    if mod.lower().endswith(".vpk"):
        parts = [_category(mod), _source(mod), mods_shared.get_mod_filename(mod)]
        if _is_unknown(mod):
            parts.insert(0, "Unknown")
    else:
        parts = [_category(mod), _source(mod)]
    return "  •  ".join(part for part in parts if part)


def _open_actions_window(mod):
    global active_action_mod
    active_action_mod = mod
    path = mods_shared.get_mod_path(mod)
    dpg.set_value("mod_action_title", _display_name(mod))
    dpg.set_value(
        "mod_action_file",
        f"File: {mods_shared.get_mod_filename(mod) if os.path.isfile(path) else os.path.basename(path)}",
    )
    dpg.set_value("mod_action_name", _display_name(mod))
    dpg.set_value("mod_action_category", _category(mod))
    dpg.set_value("mod_action_source", _source(mod))
    dpg.set_value("mod_action_favorite", mod_library.is_favorite(mod))
    dpg.set_value("mod_action_hash", "")
    is_vpk = mod.lower().endswith(".vpk")
    dpg.configure_item("mod_action_identify_hint", show=is_vpk)
    dpg.configure_item(
        "mod_action_details_button",
        show=not is_vpk and f"{mod}_details_window_tag" in shared.tag_data_for_details_windows,
    )
    _center_window("mod_actions_window", 560, 360)
    dpg.configure_item("mod_actions_window", show=True)
    dpg.focus_item("mod_actions_window")


def show_mod_actions(sender=None, app_data=None, user_data=None):
    if user_data:
        _open_actions_window(str(user_data))


def save_mod_actions(sender=None, app_data=None, user_data=None):
    mod = active_action_mod
    if not mod:
        return
    name = str(dpg.get_value("mod_action_name") or "").strip()
    category_value = str(dpg.get_value("mod_action_category") or "").strip()
    source_value = str(dpg.get_value("mod_action_source") or "").strip()
    favorite = bool(dpg.get_value("mod_action_favorite"))
    mod_library.set_favorite(mod, favorite)

    if mod.lower().endswith(".vpk"):
        if not name:
            output.add_text("A VPK display name cannot be empty.", msg_type="warning")
            return
        if not mods_shared.update_vpk_identity(mod, name, category_value, source_value or "Manual"):
            output.add_text("Could not save VPK identity metadata.", msg_type="error")
            return
        mod_library.set_override(mod, "", "", "")
    else:
        mod_library.set_override(mod, name, category_value, source_value)

    dpg.configure_item("mod_actions_window", show=False)
    set_status(f"Updated metadata: {name or mod}", "success")
    mods_shared.scan_mods()
    mod_library.refresh_index()
    create()


def hash_active_mod(sender=None, app_data=None, user_data=None):
    mod = active_action_mod
    if not mod or not mod.lower().endswith(".vpk"):
        dpg.set_value("mod_action_hash", "Hash is only used for VPK files.")
        return
    set_status("Calculating VPK SHA-256...", "working")
    fingerprint = mod_library.get_sha256(mod)
    dpg.set_value("mod_action_hash", f"SHA-256: {fingerprint}" if fingerprint else "SHA-256 could not be calculated.")
    set_status("VPK fingerprint calculated.", "success" if fingerprint else "warning")


def open_active_mod_location(sender=None, app_data=None, user_data=None):
    mod = active_action_mod
    if not mod:
        return
    path = mods_shared.get_mod_path(mod)
    fs.open_thing(os.path.dirname(path) if os.path.isfile(path) else path)


def show_active_standard_details(sender=None, app_data=None, user_data=None):
    mod = active_action_mod
    tag = f"{mod}_details_window_tag" if mod else ""
    if tag and dpg.does_item_exist(tag):
        dpg.configure_item("mod_actions_window", show=False)
        show_details(None, None, tag)


def _selected_mods():
    return [mod for mod in checkboxes if dpg.does_item_exist(mod) and bool(dpg.get_value(mod))]


def _format_conflict_summary(conflicts):
    counts = mod_library.conflict_counts(conflicts)
    return (
        f"{counts['pairs']} conflict pairs • "
        f"{counts.get('critical', 0)} critical • "
        f"{counts.get('possible', 0)} possible • "
        f"{counts.get('expected', 0)} expected"
    )


def show_patch_preview(sender=None, app_data=None, user_data=None):
    global last_conflicts
    selected = _selected_mods()
    set_status("Checking your selection before patching...", "working")
    try:
        last_conflicts = mod_library.analyze_conflicts(selected)
        estimated = mod_library.estimate_entry_count(selected)
    except Exception:
        last_conflicts = []
        estimated = 0
        report_patch_error(traceback.format_exc())

    standard = sum(1 for mod in selected if not mod.lower().endswith(".vpk"))
    vpks = sum(1 for mod in selected if mod.lower().endswith(".vpk"))
    unknown = sum(1 for mod in selected if _is_unknown(mod))
    compatibility_rules = mod_compat.active_rules(selected)
    summary = (
        f"Selected mods: {len(selected)}\n"
        f"Standard mods: {standard}\n"
        f"VPK mods: {vpks}\n"
        f"Unknown VPKs: {unknown}\n"
        f"Indexed asset paths: {estimated}\n"
        f"Output locale: {config.get('output_locale', 'english')}\n"
        f"Conflicts: {_format_conflict_summary(last_conflicts)}\n"
        f"Automatic compatibility fixes: {len(compatibility_rules)}"
    )
    dpg.set_value("patch_preview_summary", summary)
    has_conflicts = bool(last_conflicts)
    dpg.configure_item(
        "patch_preview_conflicts_button",
        enabled=True,
        label=f"Check overlaps ({len(last_conflicts)})",
    )
    dpg.configure_item("patch_preview_warning", show=has_conflicts or unknown > 0)
    warning_bits = []
    if has_conflicts:
        warning_bits.append("Review detected overlaps before patching.")
    if compatibility_rules:
        warning_bits.append(
            "Known compatibility rules will exclude only confirmed conflicting resources from generated output."
        )
    if unknown:
        warning_bits.append(f"{unknown} enabled VPK(s) are still unidentified.")
    dpg.set_value("patch_preview_warning", " ".join(warning_bits))
    if dpg.does_item_exist("patch_preview_conflict_view"):
        dpg.configure_item("patch_preview_conflict_view", show=False)
    if dpg.does_item_exist("patch_preview_main_view"):
        dpg.configure_item("patch_preview_main_view", show=True)
    _center_window("patch_preview_window", 580, 390)
    dpg.configure_item("patch_preview_window", show=True)
    dpg.focus_item("patch_preview_window")
    set_status("Review is ready.", "warning" if has_conflicts else "ready")


def close_conflicts(sender=None, app_data=None, user_data=None):
    """Return from the inline Conflict Report to the Patch Preview summary."""
    if dpg.does_item_exist("patch_preview_conflict_view"):
        dpg.configure_item("patch_preview_conflict_view", show=False)
    if dpg.does_item_exist("patch_preview_main_view"):
        dpg.configure_item("patch_preview_main_view", show=True)
    if dpg.does_item_exist("patch_preview_window"):
        _center_window("patch_preview_window", 580, 390)
        dpg.focus_item("patch_preview_window")


def show_conflicts(sender=None, app_data=None, user_data=None):
    """Render conflicts inside Patch Preview itself.

    Using one modal avoids Dear PyGui's modal-layer ordering problem entirely.
    The button remains useful even when zero conflicts are detected so it can
    never appear to be a dead control.
    """
    if not dpg.does_item_exist("conflict_list"):
        set_status("Conflict report UI is unavailable.", "error")
        return

    dpg.delete_item("conflict_list", children_only=True)
    if not last_conflicts:
        dpg.add_text("No indexed conflicts were detected.", parent="conflict_list")
        dpg.add_text(
            "This means the currently selected, indexed mods do not share any asset paths.",
            parent="conflict_list",
            wrap=710,
        )
    else:
        counts = mod_library.conflict_counts(last_conflicts)
        dpg.add_text(
            f"{counts['pairs']} conflict pair(s) • "
            f"{counts.get('critical', 0)} critical • "
            f"{counts.get('possible', 0)} possible • "
            f"{counts.get('expected', 0)} expected",
            parent="conflict_list",
            wrap=710,
        )
        dpg.add_spacer(parent="conflict_list", height=6)
        active_rules = mod_compat.active_rules(_selected_mods())
        if active_rules:
            dpg.add_text("Automatic compatibility actions", parent="conflict_list", wrap=710)
            for rule in active_rules:
                dpg.add_text(
                    f"  {rule['title']}: {rule['summary']}",
                    parent="conflict_list",
                    wrap=700,
                )
            for action in mod_compat.planned_resource_actions(_selected_mods()):
                dpg.add_text(
                    f"  [{action['classification'].upper()}] {action['path']} — {action['recommended_action']}",
                    parent="conflict_list",
                    wrap=700,
                )
            dpg.add_spacer(parent="conflict_list", height=8)

        for conflict in last_conflicts[:100]:
            heading = (
                f"[{conflict['severity'].upper()} / {conflict.get('classification', 'unknown').upper()}] "
                f"{conflict['a_name']}  ↔  {conflict['b_name']}  "
                f"({conflict['count']} shared paths)"
            )
            dpg.add_text(heading, parent="conflict_list", wrap=710)
            for detail in conflict.get("details", [])[:5]:
                dpg.add_text(f"    {detail['path']}", parent="conflict_list", wrap=700)
                for owner, fingerprint in detail.get("owners", {}).items():
                    owner_name = mod_library.display_name(owner)
                    if fingerprint.get("error"):
                        info = f"hash unavailable: {fingerprint['error']}"
                    else:
                        info = (
                            f"size={fingerprint.get('size', '?')}  "
                            f"CRC32={fingerprint.get('crc32', '?')}  "
                            f"SHA256={str(fingerprint.get('sha256', '?'))[:16]}…"
                        )
                    dpg.add_text(f"      {owner_name}: {info}", parent="conflict_list", wrap=690)
                winner = detail.get("winner", "undetermined")
                if winner in detail.get("owners", {}):
                    winner = mod_library.display_name(winner)
                dpg.add_text(
                    f"      Winner: {winner}  •  Action: {detail.get('recommended_action', 'Review manually')}",
                    parent="conflict_list",
                    wrap=690,
                )
            dpg.add_spacer(parent="conflict_list", height=6)

    if dpg.does_item_exist("patch_preview_main_view"):
        dpg.configure_item("patch_preview_main_view", show=False)
    if dpg.does_item_exist("patch_preview_conflict_view"):
        dpg.configure_item("patch_preview_conflict_view", show=True)

    _center_window("patch_preview_window", 780, 560)
    dpg.focus_item("patch_preview_window")
    set_status("Conflict report opened.", "warning" if last_conflicts else "ready")


def _start_patch(sender=None, app_data=None, user_data=None):
    dpg.configure_item("patch_preview_window", show=False)
    set_status("Patching... a restore point will be created first.", "working")
    import patch

    threading.Thread(target=patch.patcher, daemon=True).start()


def show_backups(sender=None, app_data=None, user_data=None):
    global backup_display_map
    points = backup_manager.list_restore_points()
    backup_display_map = {}
    items = []
    for point in points:
        created = str(point.get("created", point.get("id", "Unknown")))
        status = str(point.get("status", "created"))
        count = len(point.get("selected_mods", []))
        label = f"{created}  •  {count} mods  •  {status}"
        backup_display_map[label] = point.get("path")
        items.append(label)
    dpg.configure_item("backup_select", items=items)
    dpg.set_value("backup_select", items[0] if items else "")
    dpg.set_value(
        "backup_summary",
        f"{len(items)} restore point(s). Minify keeps the newest {backup_manager.MAX_BACKUPS}."
        if items
        else "No restore points have been created yet.",
    )
    dpg.configure_item("backup_restore_button", enabled=bool(items))
    _center_window("backup_manager_window", 700, 300)
    dpg.configure_item("backup_manager_window", show=True)
    dpg.focus_item("backup_manager_window")


def restore_backup(sender=None, app_data=None, user_data=None):
    label = str(dpg.get_value("backup_select") or "") if dpg.does_item_exist("backup_select") else ""
    path = backup_display_map.get(label)
    if not path:
        output.add_text("Choose a restore point first.", msg_type="warning")
        return
    try:
        set_status("Restoring Minify-managed Dota files...", "working")
        result = backup_manager.restore_restore_point(path, restore_selection=True)
        dpg.configure_item("backup_manager_window", show=False)
        load()
        refresh()
        output.add_text(f"Restored backup to {result['output_path']}", msg_type="success")
        set_status("Restore completed.", "success")
    except Exception:
        report_patch_error(traceback.format_exc())
        output.add_text("Restore failed. Open Error Details for technical information.", msg_type="error")


def _set_d2pfx_import_busy(busy, message=""):
    for tag in (
        "d2pfx_import_link_button",
        "d2pfx_import_available_button",
        "d2pfx_import_zip_button",
        "d2pfx_import_close_button",
        "d2pfx_import_url",
    ):
        if dpg.does_item_exist(tag):
            enabled = not busy
            if tag == "d2pfx_import_available_button" and not busy:
                enabled = bool(d2pfx_url_preview and d2pfx_url_preview.get("resolved_count", 0))
            dpg.configure_item(tag, enabled=enabled)
    if dpg.does_item_exist("d2pfx_import_progress"):
        dpg.configure_item("d2pfx_import_progress", show=bool(busy))
        if busy:
            dpg.set_value("d2pfx_import_progress", 0.02)
    if dpg.does_item_exist("d2pfx_import_progress_text"):
        dpg.set_value("d2pfx_import_progress_text", message or ("Working..." if busy else ""))


def _format_d2pfx_preview(preview):
    lines = [
        f"Pack: {preview.get('name', 'D2PFX Shared Pack')}",
        f"Selected: {preview.get('total', 0)}",
        f"Resolved in current catalog: {preview.get('resolved_count', 0)}",
        f"Browser-compatible components: {preview.get('vpk_candidate_count', preview.get('resolved_count', 0))}",
        f"Loose-file-only selections: {preview.get('non_vpk_only_count', 0)}",
        f"Unavailable / changed: {preview.get('unavailable_count', 0)}",
    ]
    category_counts = preview.get("category_counts", {})
    if category_counts:
        lines.append("")
        lines.append("Categories:")
        for category_id, count in sorted(category_counts.items(), key=lambda pair: pair[0].casefold()):
            label = category_id.replace("-", " ").title()
            lines.append(f"  • {label}: {count}")
    unresolved = preview.get("unresolved", [])
    if unresolved:
        lines.append("")
        lines.append("Unavailable selections:")
        for item in unresolved[:10]:
            lines.append(f"  • {item.get('name', 'Unknown')} [{item.get('categoryId', '?')}]")
        if len(unresolved) > 10:
            lines.append(f"  • ...and {len(unresolved) - 10} more")
    lines.append("")
    if preview.get("stale_catalog"):
        lines.append("WARNING: The current catalog could not be refreshed; a cached copy is being used.")
    lines.append(
        "Minify installs VPK-compatible components as native D2PFX Browser mods. Terrain VPKs are supported; fonts, cursors, and other loose-file-only extras are reported and skipped."
    )
    return "\n".join(lines)


def _clear_d2pfx_url_preview(sender=None, app_data=None, user_data=None):
    global d2pfx_url_preview
    d2pfx_url_preview = None
    if dpg.does_item_exist("d2pfx_import_available_button"):
        dpg.configure_item("d2pfx_import_available_button", enabled=False)
    if dpg.does_item_exist("d2pfx_import_preview"):
        dpg.set_value(
            "d2pfx_import_preview",
            "Paste a Dota2PornFx share link, expanded ?pack= URL, or raw pack payload, then click Fetch Link.",
        )


def show_import_dialog(sender=None, app_data=None, user_data=None):
    global d2pfx_url_preview
    d2pfx_url_preview = None
    if not dpg.does_item_exist("d2pfx_import_window"):
        _create_auxiliary_windows()
    if not dpg.does_item_exist("d2pfx_import_window"):
        return
    if dpg.does_item_exist("d2pfx_import_available_button"):
        dpg.configure_item("d2pfx_import_available_button", enabled=False)
    if dpg.does_item_exist("d2pfx_import_progress"):
        dpg.configure_item("d2pfx_import_progress", show=False)
    if dpg.does_item_exist("d2pfx_import_progress_text"):
        dpg.set_value("d2pfx_import_progress_text", "")
    if dpg.does_item_exist("d2pfx_import_preview"):
        dpg.set_value(
            "d2pfx_import_preview",
            "Paste a Dota2PornFx share link, expanded ?pack= URL, or raw pack payload, then click Fetch Link.\n\nImported components will appear as Remove in the D2PFX Browser and can be removed individually. Downloaded ZIP importing remains available below.",
        )
    _center_window("d2pfx_import_window", 720, 470)
    dpg.configure_item("d2pfx_import_window", show=True)
    dpg.focus_item("d2pfx_import_url")


def choose_d2pfx_zip(sender=None, app_data=None, user_data=None):
    if dpg.does_item_exist("d2pfx_import_window"):
        dpg.configure_item("d2pfx_import_window", show=False)
    if dpg.does_item_exist("d2pfx_import_dialog"):
        dpg.configure_item("d2pfx_import_dialog", show=True)


def fetch_d2pfx_url_preview(sender=None, app_data=None, user_data=None):
    value = str(dpg.get_value("d2pfx_import_url") or "").strip() if dpg.does_item_exist("d2pfx_import_url") else ""
    if not value:
        if dpg.does_item_exist("d2pfx_import_preview"):
            dpg.set_value("d2pfx_import_preview", "Paste a Dota2PornFx share link first.")
        return

    def worker():
        global d2pfx_url_preview
        try:
            _set_d2pfx_import_busy(True, "Resolving share link and refreshing the D2PFX catalog...")
            set_status("Resolving Dota2PornFx share link...", "working")
            preview = mod_library.preview_d2pfx_share(value)
            # Ignore a result if the user managed to change the field while the
            # request was running.
            current = (
                str(dpg.get_value("d2pfx_import_url") or "").strip() if dpg.does_item_exist("d2pfx_import_url") else ""
            )
            if current != value:
                d2pfx_url_preview = None
                return
            d2pfx_url_preview = preview
            if dpg.does_item_exist("d2pfx_import_preview"):
                dpg.set_value("d2pfx_import_preview", _format_d2pfx_preview(preview))
            if dpg.does_item_exist("d2pfx_import_available_button"):
                dpg.configure_item(
                    "d2pfx_import_available_button",
                    enabled=preview.get("vpk_candidate_count", preview.get("resolved_count", 0)) > 0,
                )
            unavailable = int(preview.get("unavailable_count", 0) or 0)
            used_dns_fallback = bool(preview.get("dns_fallback_used"))
            if unavailable:
                suffix = " Secure DNS fallback was used." if used_dns_fallback else ""
                set_status(f"D2PFX pack resolved with {unavailable} unavailable selection(s).{suffix}", "warning")
            elif used_dns_fallback:
                set_status("D2PFX share link resolved using the secure DNS fallback and is ready to import.", "success")
            else:
                set_status("D2PFX share link resolved and ready to import.", "success")
        except Exception:
            d2pfx_url_preview = None
            details_text = traceback.format_exc()
            report_patch_error(details_text)
            message = details_text.strip().splitlines()[-1] if details_text.strip() else "Unknown error"
            if dpg.does_item_exist("d2pfx_import_preview"):
                dpg.set_value("d2pfx_import_preview", f"Could not resolve this Dota2PornFx pack.\n\n{message}")
            set_status("D2PFX share-link lookup failed.", "error")
        finally:
            _set_d2pfx_import_busy(False)

    threading.Thread(target=worker, daemon=True).start()


def _refresh_d2pfx_browser_after_import():
    try:
        from browsers.d2pfx.ui import BrowserUI

        browser = BrowserUI.get_instance()
        if browser.selected_category and dpg.does_item_exist("d2pfx_browser_window"):
            browser.render_mods(browser.selected_category)
    except Exception:
        pass


def import_d2pfx_url_pack(sender=None, app_data=None, user_data=None):
    value = str(dpg.get_value("d2pfx_import_url") or "").strip() if dpg.does_item_exist("d2pfx_import_url") else ""
    preview = d2pfx_url_preview
    if not value or not isinstance(preview, dict) or preview.get("input") != value:
        fetch_d2pfx_url_preview()
        return

    def progress(message, completed, total):
        fraction = float(completed) / float(total) if total else 0.0
        if dpg.does_item_exist("d2pfx_import_progress"):
            dpg.set_value("d2pfx_import_progress", max(0.02, min(1.0, fraction)))
        if dpg.does_item_exist("d2pfx_import_progress_text"):
            dpg.set_value("d2pfx_import_progress_text", message)

    def worker():
        global d2pfx_url_preview
        try:
            _set_d2pfx_import_busy(True, "Preparing D2PFX URL import...")
            set_status("Downloading Dota2PornFx pack from share link...", "working")
            result = mod_library.import_d2pfx_share(value, preview=preview, progress=progress)
            if dpg.does_item_exist("d2pfx_import_progress"):
                dpg.set_value("d2pfx_import_progress", 1.0)
            if dpg.does_item_exist("d2pfx_import_progress_text"):
                dpg.set_value("d2pfx_import_progress_text", "Import complete. Refreshing Mod Library...")
            mods_shared.scan_mods()
            mod_library.refresh_index()
            if dpg.does_item_exist("d2pfx_import_window"):
                dpg.configure_item("d2pfx_import_window", show=False)
            d2pfx_url_preview = None
            create()
            _refresh_d2pfx_browser_after_import()
            notes = []
            if result.get("unavailable"):
                notes.append(f"{result['unavailable']} unavailable")
            if result.get("skipped_non_vpk"):
                notes.append(f"{result['skipped_non_vpk']} non-VPK skipped")
            if result.get("failures"):
                notes.append(f"{len(result['failures'])} download failure(s)")
            suffix = f" ({', '.join(notes)})" if notes else ""
            installed_count = int(result.get("installed_components", 0) or 0)
            already_count = int(result.get("already_installed", 0) or 0)
            if already_count:
                notes.append(f"{already_count} already installed")
            legacy_archived = int(result.get("legacy_archived", 0) or 0)
            if legacy_archived:
                notes.append(f"{legacy_archived} legacy pack archived")
            suffix = f" ({', '.join(notes)})" if notes else ""
            output.add_text(
                f"Installed {installed_count} D2PFX component(s) from pack {result['pack_name']}{suffix}. "
                "They are now managed individually by the D2PFX Browser.",
                msg_type="success" if not result.get("failures") else "warning",
            )
            set_status(
                f"D2PFX Browser imported: {result['pack_name']}{suffix}",
                "success" if not result.get("failures") else "warning",
            )
        except Exception:
            report_patch_error(traceback.format_exc())
            output.add_text("D2PFX URL import failed. Open Error Details for technical information.", msg_type="error")
            set_status("D2PFX URL import failed.", "error")
        finally:
            _set_d2pfx_import_busy(False)

    threading.Thread(target=worker, daemon=True).start()


def _file_dialog_path(app_data):
    if isinstance(app_data, dict):
        direct = app_data.get("file_path_name")
        if direct:
            return direct
        selections = app_data.get("selections")
        if isinstance(selections, dict) and selections:
            return next(iter(selections.values()))
    return ""


def import_d2pfx_callback(sender=None, app_data=None, user_data=None):
    path = _file_dialog_path(app_data)
    if not path:
        return
    try:
        set_status("Importing and identifying Dota2PornFx pack...", "working")
        result = mod_library.import_d2pfx_zip(path)
        mods_shared.scan_mods()
        mod_library.refresh_index()
        create()
        _refresh_d2pfx_browser_after_import()
        installed_count = int(result.get("installed_components", 0) or 0)
        already_count = int(result.get("already_installed", 0) or 0)
        unresolved = int(result.get("unknown", 0) or 0)
        details = []
        if already_count:
            details.append(f"{already_count} already installed")
        if unresolved:
            details.append(f"{unresolved} no longer in current catalog")
        legacy_archived = int(result.get("legacy_archived", 0) or 0)
        if legacy_archived:
            details.append(f"{legacy_archived} legacy pack archived")
        suffix = f" ({', '.join(details)})" if details else ""
        output.add_text(
            f"Installed {installed_count} D2PFX component(s) from {result['pack_name']}{suffix}. "
            "Each component can now be removed from the D2PFX Browser.",
            msg_type="success" if not result.get("failures") else "warning",
        )
        set_status(
            f"Imported {result['pack_name']} into D2PFX Browser{suffix}.",
            "success" if not result.get("failures") else "warning",
        )
    except Exception:
        report_patch_error(traceback.format_exc())
        output.add_text("D2PFX import failed. Open Error Details for technical information.", msg_type="error")


def _create_auxiliary_windows():
    # Auxiliary windows are top-level items, so rebuilding the Mod Library does
    # not remove them. Reuse the existing set instead of deleting a currently
    # active file dialog/modal from inside its own callback.
    if all(dpg.does_item_exist(tag) for tag in AUXILIARY_WINDOWS):
        return

    # Recover from a partial initialization by rebuilding the incomplete set.
    for tag in AUXILIARY_WINDOWS:
        if dpg.does_item_exist(tag):
            dpg.delete_item(tag)

    dpg.add_window(
        tag="mod_actions_window", label="Mod information", modal=True, show=False, no_resize=True, no_move=True
    )
    dpg.add_text("", parent="mod_actions_window", tag="mod_action_title")
    dpg.bind_item_font("mod_action_title", "large_font")
    dpg.add_text("", parent="mod_actions_window", tag="mod_action_file")
    dpg.bind_item_theme("mod_action_file", "mod_manager_muted_theme")
    dpg.add_text("Display name", parent="mod_actions_window")
    dpg.add_input_text(parent="mod_actions_window", tag="mod_action_name", width=-1)
    dpg.add_text("Category", parent="mod_actions_window")
    dpg.add_input_text(parent="mod_actions_window", tag="mod_action_category", width=-1)
    dpg.add_text("Source", parent="mod_actions_window")
    dpg.add_input_text(parent="mod_actions_window", tag="mod_action_source", width=-1)
    dpg.add_checkbox(parent="mod_actions_window", tag="mod_action_favorite", label="Keep in Favorites")
    dpg.add_text(
        "For VPK files, Minify remembers this identity by file fingerprint, so the name survives moves and generic pakXX filenames.",
        parent="mod_actions_window",
        tag="mod_action_identify_hint",
        wrap=520,
    )
    dpg.bind_item_theme("mod_action_identify_hint", "mod_manager_muted_theme")
    dpg.add_text("", parent="mod_actions_window", tag="mod_action_hash", wrap=520)
    with dpg.group(parent="mod_actions_window", horizontal=True):
        dpg.add_button(label="Save changes", callback=save_mod_actions, width=100)
        dpg.add_button(label="Open folder", callback=open_active_mod_location, width=92)
        dpg.add_button(label="Verify file", callback=hash_active_mod, width=84)
        dpg.add_button(
            tag="mod_action_details_button", label="Preview", callback=show_active_standard_details, width=72
        )
        dpg.add_button(label="Close", callback=lambda: dpg.configure_item("mod_actions_window", show=False), width=70)

    dpg.add_window(
        tag="patch_preview_window", label="Patch Preview", modal=True, show=False, no_resize=True, no_move=True
    )

    dpg.add_group(parent="patch_preview_window", tag="patch_preview_main_view", show=True)
    dpg.add_text("Review your patch", parent="patch_preview_main_view", tag="patch_preview_title")
    dpg.bind_item_font("patch_preview_title", "large_font")
    dpg.add_text("", parent="patch_preview_main_view", tag="patch_preview_summary")
    dpg.add_text("", parent="patch_preview_main_view", tag="patch_preview_warning", show=False, wrap=540)
    dpg.bind_item_theme("patch_preview_warning", "mod_manager_warning_theme")
    dpg.add_spacer(parent="patch_preview_main_view", height=8)
    with dpg.group(parent="patch_preview_main_view", horizontal=True):
        dpg.add_button(
            tag="patch_preview_conflicts_button", label="Check overlaps (0)", callback=show_conflicts, width=150
        )
        dpg.add_button(label="Apply patch", callback=_start_patch, width=110)
        dpg.add_button(
            label="Cancel", callback=lambda: dpg.configure_item("patch_preview_window", show=False), width=80
        )

    dpg.add_group(parent="patch_preview_window", tag="patch_preview_conflict_view", show=False)
    dpg.add_text("Shared files", parent="patch_preview_conflict_view", tag="conflict_report_title")
    dpg.bind_item_font("conflict_report_title", "large_font")
    dpg.add_text(
        "These mods change some of the same Dota files. Review the groups below before applying the patch; some overlaps are intentional, while others can make one mod override another.",
        parent="patch_preview_conflict_view",
        wrap=730,
    )
    dpg.add_child_window(parent="patch_preview_conflict_view", tag="conflict_list", width=-1, height=410, border=True)
    with dpg.group(parent="patch_preview_conflict_view", horizontal=True):
        dpg.add_button(label="Back to review", callback=close_conflicts, width=108)
        dpg.add_button(label="Apply anyway", callback=_start_patch, width=108)

    dpg.add_window(
        tag="backup_manager_window", label="Restore a backup", modal=True, show=False, no_resize=True, no_move=True
    )
    dpg.add_text("Restore a previous Minify state", parent="backup_manager_window", tag="backup_title")
    dpg.bind_item_font("backup_title", "large_font")
    dpg.add_text("", parent="backup_manager_window", tag="backup_summary", wrap=650)
    dpg.add_combo(parent="backup_manager_window", tag="backup_select", items=[], width=-1)
    with dpg.group(parent="backup_manager_window", horizontal=True):
        dpg.add_button(tag="backup_restore_button", label="Restore this backup", callback=restore_backup, width=120)
        dpg.add_button(
            label="Close", callback=lambda: dpg.configure_item("backup_manager_window", show=False), width=80
        )

    dpg.add_window(
        tag="error_details_window", label="Technical details", modal=True, show=False, no_resize=True, no_move=True
    )
    dpg.add_text(
        "These details are useful when reporting a problem or troubleshooting a failed patch.",
        parent="error_details_window",
    )
    dpg.add_input_text(
        parent="error_details_window", tag="error_details_text", multiline=True, readonly=True, width=-1, height=-45
    )
    dpg.add_button(
        parent="error_details_window",
        label="Close",
        callback=lambda: dpg.configure_item("error_details_window", show=False),
        width=80,
    )

    dpg.add_window(
        tag="d2pfx_import_window",
        label="Import a D2PFX pack",
        modal=True,
        show=False,
        no_resize=True,
        no_move=True,
        no_collapse=True,
    )
    dpg.add_text("Import a D2PFX pack", parent="d2pfx_import_window", tag="d2pfx_import_title")
    dpg.bind_item_font("d2pfx_import_title", "large_font")
    dpg.add_text(
        "Paste an official D2PFX share link to preview what is available. Minify installs each available item separately, so you can remove individual components later.",
        parent="d2pfx_import_window",
        wrap=660,
    )
    dpg.bind_item_theme(dpg.last_item(), "mod_manager_muted_theme")
    dpg.add_spacer(parent="d2pfx_import_window", height=5)
    dpg.add_input_text(
        parent="d2pfx_import_window",
        tag="d2pfx_import_url",
        hint="https://share.d2pfx.workers.dev/s/...",
        width=-1,
        callback=_clear_d2pfx_url_preview,
    )
    with dpg.group(parent="d2pfx_import_window", horizontal=True):
        dpg.add_button(
            tag="d2pfx_import_link_button", label="Preview link", callback=fetch_d2pfx_url_preview, width=100
        )
        dpg.add_button(
            tag="d2pfx_import_available_button",
            label="Install available",
            callback=import_d2pfx_url_pack,
            width=120,
            enabled=False,
        )
        dpg.bind_item_theme("d2pfx_import_available_button", "mod_manager_primary_theme")
        dpg.add_button(tag="d2pfx_import_zip_button", label="Import ZIP", callback=choose_d2pfx_zip, width=90)
        dpg.add_button(
            tag="d2pfx_import_close_button",
            label="Close",
            callback=lambda: dpg.configure_item("d2pfx_import_window", show=False),
            width=70,
        )
    dpg.add_input_text(
        parent="d2pfx_import_window",
        tag="d2pfx_import_preview",
        multiline=True,
        readonly=True,
        width=-1,
        height=230,
        default_value="Paste a D2PFX share link, expanded ?pack= URL, or raw pack payload, then choose Preview link.\n\nMinify will show what it can install before anything changes. You can also import a downloaded pack with Import ZIP.",
    )
    dpg.add_progress_bar(
        parent="d2pfx_import_window", tag="d2pfx_import_progress", width=-1, default_value=0.0, show=False
    )
    dpg.add_text("", parent="d2pfx_import_window", tag="d2pfx_import_progress_text", wrap=660)
    dpg.bind_item_theme("d2pfx_import_progress_text", "mod_manager_muted_theme")

    with dpg.file_dialog(
        directory_selector=False,
        show=False,
        callback=import_d2pfx_callback,
        tag="d2pfx_import_dialog",
        width=720,
        height=460,
    ):
        dpg.add_file_extension(".zip", color=(0, 210, 210, 255))
        dpg.add_file_extension(".*")

    with dpg.file_dialog(
        directory_selector=True,
        show=False,
        callback=export_profiles_callback,
        tag="profile_export_dialog",
        width=720,
        height=460,
    ):
        pass

    with dpg.file_dialog(
        directory_selector=False,
        show=False,
        callback=import_profiles_callback,
        tag="profile_import_dialog",
        width=720,
        height=460,
    ):
        dpg.add_file_extension(".json", color=UI_ACCENT)
        dpg.add_file_extension(".*")


def _create_section(section, mods, default_open):
    if not mods:
        return
    header_tag = SECTION_TAGS[section]
    dpg.add_collapsing_header(
        parent="mod_manager_list",
        tag=header_tag,
        label=f"{SECTION_LABELS[section]}  •  {len(mods)} {'mod' if len(mods) == 1 else 'mods'}",
        default_open=default_open,
    )
    section_theme = {
        "d2pfx": "mod_manager_d2pfx_section_theme",
        "vpk": "mod_manager_vpk_section_theme",
        "unknown": "mod_manager_unknown_section_theme",
    }.get(section, "mod_manager_section_theme")
    dpg.bind_item_theme(header_tag, section_theme)
    controls_tag = f"{section}_bulk_controls"
    dpg.add_group(parent=header_tag, tag=controls_tag, horizontal=True)
    dpg.add_text("Select in this section", parent=controls_tag)
    dpg.bind_item_theme(dpg.last_item(), "mod_manager_muted_theme")
    dpg.add_button(
        parent=controls_tag, label="All", small=True, width=42, callback=set_section_mods, user_data=(section, True)
    )
    dpg.add_button(
        parent=controls_tag, label="None", small=True, width=48, callback=set_section_mods, user_data=(section, False)
    )


def _create_collection_section(group, mods, default_open=False):
    if not mods:
        return None
    index = len(collection_headers)
    header_tag = f"collection_mods_header_{index}"
    dpg.add_collapsing_header(
        parent="mod_manager_list",
        tag=header_tag,
        label=f"{group}  •  0/{len(mods)} selected",
        default_open=default_open,
    )
    dpg.bind_item_theme(header_tag, "mod_manager_collection_section_theme")
    controls_tag = f"collection_bulk_controls_{index}"
    dpg.add_group(parent=header_tag, tag=controls_tag, horizontal=True)
    dpg.add_text("Select in this collection", parent=controls_tag)
    dpg.bind_item_theme(dpg.last_item(), "mod_manager_muted_theme")
    section_key = _collection_section_key(group)
    dpg.add_button(
        parent=controls_tag, label="All", small=True, width=42, callback=set_section_mods, user_data=(section_key, True)
    )
    dpg.add_button(
        parent=controls_tag,
        label="None",
        small=True,
        width=48,
        callback=set_section_mods,
        user_data=(section_key, False),
    )
    collection_headers[group] = header_tag
    return header_tag


def _create_d2pfx_category_header(category):
    members = d2pfx_category_members.get(category, [])
    index = len(d2pfx_category_headers)
    group_tag = f"d2pfx_category_header_{index}"
    count_tag = f"d2pfx_category_count_{index}"
    dpg.add_group(parent=SECTION_TAGS["d2pfx"], tag=group_tag, horizontal=True)
    dpg.add_text(category or "Other", parent=group_tag)
    dpg.bind_item_theme(dpg.last_item(), "mod_manager_d2pfx_category_theme")
    dpg.add_text(f"{len(members)} {'mod' if len(members) == 1 else 'mods'}", parent=group_tag, tag=count_tag)
    dpg.bind_item_theme(count_tag, "mod_manager_muted_theme")
    d2pfx_category_headers[category] = (group_tag, count_tag)


def _create_mod_row(mod, section, enable_ticking, value, has_details, parent_tag=None):
    row_tag = f"{mod}_group_tag"
    top_tag = f"{mod}_top_row"
    meta_tag = f"{mod}_meta"
    dpg.add_group(parent=parent_tag or SECTION_TAGS[section], tag=row_tag)
    dpg.add_group(parent=row_tag, tag=top_tag, horizontal=True)
    dpg.add_checkbox(
        parent=top_tag,
        label=_display_name(mod),
        tag=mod,
        callback=setup_state,
        default_value=value,
        enabled=enable_ticking,
    )
    if section == "unknown":
        dpg.bind_item_theme(mod, "mod_manager_unknown_theme")

    fav_tag = f"{mod}_favorite_button"
    dpg.add_button(
        parent=top_tag,
        tag=fav_tag,
        label="★" if mod_library.is_favorite(mod) else "☆",
        small=True,
        width=28,
        indent=_row_action_indent(),
        callback=toggle_favorite,
        user_data=mod,
    )
    dpg.add_button(
        parent=top_tag,
        tag=f"{mod}_manage_button",
        label="⋯",
        small=True,
        width=28,
        callback=show_mod_actions,
        user_data=mod,
    )
    _add_tooltip(fav_tag, "Add or remove this mod from Favorites")
    _add_tooltip(f"{mod}_manage_button", "Open information and actions for this mod")

    dpg.add_text(_meta_text(mod), parent=row_tag, tag=meta_tag, indent=28, wrap=max(220, _list_width() - 64))
    dpg.bind_item_theme(meta_tag, "mod_manager_muted_theme" if section != "unknown" else "mod_manager_warning_theme")

    if mod.lower().endswith(".vpk"):
        with dpg.tooltip(parent=mod):
            dpg.add_text(f"File: {mods_shared.get_mod_filename(mod)}")
            dpg.add_text(f"Category: {_category(mod)}")
            dpg.add_text(f"Source: {_source(mod)}")
            dpg.add_text("Needs identification" if _is_unknown(mod) else "Identified")
    elif section == "d2pfx":
        with dpg.tooltip(parent=mod):
            dpg.add_text(f"Category: {_category(mod)}")
            dpg.add_text("Source: D2PFX Browser")
            dpg.add_text("You can also manage this component from the D2PFX Browser.")
    elif has_details:
        _add_tooltip(mod, "Preview and notes are available from the … menu.")


def create():
    _capture_ui_state()
    if dpg.does_item_exist("mod_menu"):
        dpg.delete_item("mod_menu", children_only=True)

    for window_tag in list(shared.tag_data_for_details_windows):
        if dpg.does_item_exist(window_tag):
            dpg.delete_item(window_tag)
    shared.tag_data_for_details_windows.clear()

    for browser_config in registry.get_browser_configs():
        if hasattr(browser_config, "on_scan_start"):
            browser_config.on_scan_start()

    if dpg.does_item_exist("mod_images_registry"):
        dpg.delete_item("mod_images_registry", children_only=True)
    shared.mod_details_image_cache.clear()

    checkboxes.clear()
    mod_sections.clear()
    collection_headers.clear()
    collection_members.clear()
    d2pfx_category_headers.clear()
    d2pfx_category_members.clear()
    for members in section_members.values():
        members.clear()

    _load_profiles()
    _ensure_ui_themes()
    mod_library.refresh_index()
    _create_auxiliary_windows()

    # Workspace command bar: identity + search first, filters second. Source
    # selection lives in the persistent rail below instead of another dropdown.
    dpg.add_child_window(
        parent="mod_menu",
        tag="mod_manager_toolbar",
        height=TOOLBAR_HEIGHT,
        width=max(100, _current_menu_width() - 16),
        border=False,
        no_scrollbar=True,
        no_scroll_with_mouse=True,
    )
    dpg.bind_item_theme("mod_manager_toolbar", "mod_manager_toolbar_theme")

    dpg.add_text("MOD LIBRARY", parent="mod_manager_toolbar", tag="mod_library_eyebrow")
    dpg.bind_item_theme("mod_library_eyebrow", "mod_manager_heading_theme")
    dpg.add_text("Choose what Minify applies", parent="mod_manager_toolbar", tag="mod_library_title")
    dpg.bind_item_font("mod_library_title", "large_font")
    dpg.add_text("0 selected • 0 installed", parent="mod_manager_toolbar", tag="mod_selection_status")
    dpg.bind_item_theme("mod_selection_status", "mod_manager_status_badge_theme")

    dpg.add_input_text(
        parent="mod_manager_toolbar",
        tag="mod_search",
        hint="Search mods...  Ctrl+F",
        default_value=ui_state["search"],
        width=_search_width(),
        callback=search_changed,
    )

    with dpg.group(parent="mod_manager_toolbar", tag="library_filter_row", horizontal=True):
        dpg.add_combo(
            tag="mod_state_filter",
            items=STATE_FILTER_ITEMS,
            default_value=ui_state["state_filter"],
            width=92,
            callback=apply_filters,
        )
        dpg.add_combo(
            tag="mod_category_filter",
            items=["All Categories"],
            default_value=ui_state["category_filter"],
            width=142,
            callback=apply_filters,
        )
        dpg.add_combo(
            tag="mod_sort", items=SORT_ITEMS, default_value=ui_state["sort"], width=118, callback=_sort_changed
        )
        dpg.add_button(tag="clear_mod_filters_button", label="Reset", callback=clear_filters, small=True, width=52)
        # State storage for source navigation; the rail is the visible control.
        dpg.add_combo(
            tag="mod_type_filter",
            items=TYPE_FILTER_ITEMS,
            default_value=ui_state["type_filter"],
            callback=apply_filters,
            show=False,
        )

    _add_tooltip(
        "mod_search",
        "Filter by mod name. Advanced search supports category:, source:, file:, type:, status:, selected:, and favorite:.",
    )
    _add_tooltip("mod_state_filter", "Show all, selected, or unselected mods.")
    _add_tooltip("mod_category_filter", "Limit the workspace to one metadata category.")
    _add_tooltip("mod_sort", "Sort Standard/VPK/Unknown sections. D2PFX remains category-first, then name.")
    _add_tooltip("clear_mod_filters_button", "Clear search, source, category, state, and sort filters.")

    dpg.add_group(parent="mod_menu", tag="library_body", horizontal=True, horizontal_spacing=6)
    body_height = max(196, _current_menu_height() - TOOLBAR_HEIGHT - STATUSBAR_HEIGHT - 36)
    dpg.add_child_window(
        parent="library_body",
        tag="mod_source_rail",
        width=_source_rail_width(),
        height=body_height,
        border=False,
        no_scrollbar=True,
        no_scroll_with_mouse=True,
    )
    dpg.bind_item_theme("mod_source_rail", "mod_manager_source_rail_theme")
    dpg.add_text("BROWSE", parent="mod_source_rail", tag="source_rail_title")
    dpg.bind_item_theme("source_rail_title", "mod_manager_muted_theme")
    for label, value, tag in (
        ("All mods", "All Mods", "source_nav_all"),
        ("Standard", "Standard", "source_nav_standard"),
        ("Collections", "Collections", "source_nav_collections"),
        ("D2PFX", "D2PFX", "source_nav_d2pfx"),
        ("VPK files", "VPK", "source_nav_vpk"),
        ("Needs setup", "Unknown", "source_nav_unknown"),
        ("Favorites", "Favorites", "source_nav_favorites"),
    ):
        dpg.add_button(
            parent="mod_source_rail",
            tag=tag,
            label=label,
            width=-1,
            height=30,
            callback=set_type_filter,
            user_data=value,
        )
    dpg.add_spacer(parent="mod_source_rail", height=8)
    dpg.add_separator(parent="mod_source_rail")
    dpg.add_text("SELECTION", parent="mod_source_rail")
    dpg.bind_item_theme(dpg.last_item(), "mod_manager_muted_theme")
    dpg.add_button(
        parent="mod_source_rail",
        tag="check_all_mods_button",
        label="Select all",
        callback=check_all_mods,
        width=-1,
        height=28,
    )
    dpg.add_button(
        parent="mod_source_rail",
        tag="uncheck_all_mods_button",
        label="Clear",
        callback=uncheck_all_mods,
        width=-1,
        height=28,
    )
    dpg.add_button(
        parent="mod_source_rail",
        tag="invert_all_mods_button",
        label="Invert",
        callback=invert_all_mods,
        width=-1,
        height=28,
    )
    dpg.add_spacer(parent="mod_source_rail", height=8)
    dpg.add_separator(parent="mod_source_rail")
    dpg.add_button(
        parent="mod_source_rail",
        tag="expand_sections_button",
        label="Expand all",
        callback=expand_all_sections,
        width=-1,
        height=28,
    )
    dpg.add_button(
        parent="mod_source_rail",
        tag="collapse_sections_button",
        label="Collapse all",
        callback=collapse_all_sections,
        width=-1,
        height=28,
    )

    list_height = body_height
    dpg.add_child_window(
        parent="library_body",
        tag="mod_manager_list",
        width=_list_width(),
        height=list_height,
        border=False,
        no_scrollbar=False,
    )
    dpg.bind_item_theme("mod_manager_list", "mod_manager_list_theme")

    dpg.add_collapsing_header(
        parent="mod_manager_list", tag="profile_tools_header", label="Profiles & sharing", default_open=False
    )
    dpg.bind_item_theme("profile_tools_header", "mod_manager_section_theme")
    dpg.add_text("Saved setups", parent="profile_tools_header")
    dpg.bind_item_theme(dpg.last_item(), "mod_manager_muted_theme")
    dpg.add_combo(
        parent="profile_tools_header",
        tag="profile_select",
        items=sorted(profile_cache, key=str.casefold),
        width=-1,
        callback=profile_selected,
    )
    dpg.add_group(parent="profile_tools_header", tag="profile_select_row", horizontal=True)
    dpg.add_button(parent="profile_select_row", label="Use setup", callback=load_profile, small=True, width=78)
    dpg.add_button(parent="profile_select_row", label="Update", callback=update_profile, small=True, width=62)
    dpg.add_button(parent="profile_select_row", label="Make copy", callback=duplicate_profile, small=True, width=78)
    dpg.add_button(parent="profile_select_row", label="Delete", callback=delete_profile, small=True, width=54)
    dpg.add_input_text(parent="profile_tools_header", tag="profile_name", hint="Name this setup...", width=-1)
    dpg.add_button(parent="profile_tools_header", label="Save setup", callback=save_profile, small=True, width=92)

    dpg.add_group(parent="profile_tools_header", tag="profile_transfer_row", horizontal=True)
    dpg.add_text("Share or move", parent="profile_transfer_row")
    dpg.bind_item_theme(dpg.last_item(), "mod_manager_muted_theme")
    dpg.add_button(
        parent="profile_transfer_row",
        tag="profile_export_button",
        label="Export profiles",
        callback=choose_profile_export_directory,
        small=True,
        width=104,
    )
    dpg.add_button(
        parent="profile_transfer_row",
        tag="profile_import_button",
        label="Import & apply",
        callback=choose_profile_import_file,
        small=True,
        width=104,
    )
    dpg.add_button(
        parent="profile_transfer_row",
        tag="profile_folder_button",
        label="Open folder",
        callback=open_profiles_folder,
        small=True,
        width=86,
    )
    _add_tooltip(
        "profile_export_button", "Export every saved profile to a portable JSON bundle for another Minify build."
    )
    _add_tooltip(
        "profile_import_button",
        "Import a portable profile bundle and apply its first setup immediately. Selecting any saved setup applies it instantly.",
    )
    _add_tooltip("profile_folder_button", "Open Minify's persistent configuration folder.")
    _refresh_profile_combo()

    dpg.add_text(
        "No mods match this view. Clear a filter or choose Reset.",
        parent="mod_manager_list",
        tag="mod_empty_state",
        show=False,
    )
    dpg.bind_item_theme("mod_empty_state", "mod_manager_muted_theme")

    mod_details_cache = {}

    def scan_mod_details(mod_name):
        mod_p = mods_shared.get_mod_path(mod_name)
        img_p = os.path.join(mod_p, "preview.jpg")
        if not os.path.exists(img_p):
            img_p = os.path.join(mod_p, "preview.png")
        notes_p = os.path.join(mod_p, "notes.md")
        image_data = None
        has_notes = False
        if os.path.exists(img_p):
            try:
                image_data = dpg.load_image(img_p)
            except Exception as err:
                print(f"Failed to load image for {mod_name}: {err}")
        if os.path.exists(notes_p) and os.path.getsize(notes_p) > 0:
            has_notes = True
        return mod_name, image_data, has_notes

    directory_mods = [m for m in constants.visually_available_mods if not m.lower().endswith(".vpk")]
    d2pfx_mods = [m for m in directory_mods if mod_library.is_d2pfx(m)]
    normal_mods = [m for m in directory_mods if not mod_library.is_d2pfx(m)]
    identified_vpk_mods = [
        m for m in constants.visually_available_mods if m.lower().endswith(".vpk") and mods_shared.is_mod_identified(m)
    ]
    unknown_vpk_mods = [
        m
        for m in constants.visually_available_mods
        if m.lower().endswith(".vpk") and not mods_shared.is_mod_identified(m)
    ]

    normal_mods = _sort_mods(normal_mods)
    collection_mods = [mod for mod in normal_mods if _collection_group(mod)]
    standard_mods = [mod for mod in normal_mods if not _collection_group(mod)]
    grouped_collection_mods = {}
    for mod in collection_mods:
        grouped_collection_mods.setdefault(_collection_group(mod), []).append(mod)
    grouped_collection_mods = {
        group: _sort_mods(members)
        for group, members in sorted(grouped_collection_mods.items(), key=lambda item: item[0].casefold())
    }
    # D2PFX is intentionally category-first regardless of the general library
    # sort control; categories stay together and names are alphabetical inside
    # each category.
    d2pfx_mods = _sort_d2pfx_mods(d2pfx_mods)
    identified_vpk_mods = _sort_mods(identified_vpk_mods)
    unknown_vpk_mods = _sort_mods(unknown_vpk_mods)

    section_members["standard"].extend(standard_mods)
    collection_members.update({group: list(members) for group, members in grouped_collection_mods.items()})
    section_members["d2pfx"].extend(d2pfx_mods)
    section_members["vpk"].extend(identified_vpk_mods)
    section_members["unknown"].extend(unknown_vpk_mods)
    for mod in d2pfx_mods:
        category = _category(mod) or "Other"
        d2pfx_category_members.setdefault(category, []).append(mod)
    for mod in standard_mods:
        mod_sections[mod] = "standard"
    for group, members in grouped_collection_mods.items():
        for mod in members:
            mod_sections[mod] = _collection_section_key(group)
    for mod in d2pfx_mods:
        mod_sections[mod] = "d2pfx"
    for mod in identified_vpk_mods:
        mod_sections[mod] = "vpk"
    for mod in unknown_vpk_mods:
        mod_sections[mod] = "unknown"

    categories = sorted(
        {_category(mod) for mod in normal_mods + d2pfx_mods + identified_vpk_mods + unknown_vpk_mods if _category(mod)},
        key=str.casefold,
    )
    category_items = ["All Categories"] + categories
    dpg.configure_item("mod_category_filter", items=category_items)
    if ui_state["category_filter"] not in category_items:
        ui_state["category_filter"] = "All Categories"
    dpg.set_value("mod_category_filter", ui_state["category_filter"])

    with concurrent.futures.ThreadPoolExecutor() as executor:
        for m_name, img_data, notes_exist in executor.map(scan_mod_details, normal_mods + d2pfx_mods):
            mod_details_cache[m_name] = (img_data, notes_exist)

    _create_section("standard", standard_mods, True)
    for group, members in grouped_collection_mods.items():
        _create_collection_section(group, members, default_open=False)
    _create_section("d2pfx", d2pfx_mods, True)
    _create_section("vpk", identified_vpk_mods, True)
    _create_section("unknown", unknown_vpk_mods, False)

    ordered_mods = standard_mods + collection_mods + d2pfx_mods + identified_vpk_mods + unknown_vpk_mods
    last_d2pfx_category = None
    for mod in ordered_mods:
        section = mod_sections[mod]
        collection_group = _collection_group(mod)
        logical_section = "standard" if collection_group else section
        parent_tag = collection_headers.get(collection_group) if collection_group else None
        if section == "d2pfx":
            current_category = _category(mod) or "Other"
            if current_category != last_d2pfx_category:
                _create_d2pfx_category_header(current_category)
                last_d2pfx_category = current_category
        mod_path = mods_shared.get_mod_path(mod)
        unsupported_version = False
        has_details = False

        if is_vpk := mod.lower().endswith(".vpk"):
            always_val = False
        else:
            cfg = manifest_utils.get_mod(mod_path)
            always_val = cfg.get("always", False)
            if browser_info := cfg.get("browser"):
                for browser_config in registry.get_browser_configs():
                    if hasattr(browser_config, "on_scan"):
                        browser_config.on_scan(mod, browser_info)
            if version_req := cfg.get("version"):
                if not manifest_utils.is_version_at_least(base.VERSION, version_req):
                    unsupported_version = True
            img_data, has_notes = mod_details_cache.get(mod, (None, False))
            has_details = bool(img_data or has_notes)

        if unsupported_version:
            enable_ticking = False
            value = False
            if checkboxes_state.get(mod, False):
                checkboxes_state[mod] = False
                save()
            output.add_text(f"Disabled {mod} (Requires version {version_req})", msg_type="warning")
        elif always_val:
            enable_ticking = False
            value = True
        else:
            enable_ticking = True
            value = bool(checkboxes_state.get(mod, False))

        if not is_vpk and has_details:
            tag_data = f"{mod}_details_window_tag"
            shared.tag_data_for_details_windows.append(tag_data)
            dpg.add_window(
                tag=tag_data,
                modal=True,
                pos=(0, 0),
                show=False,
                label=mod,
                no_resize=True,
                no_move=True,
                no_close=False,
                no_collapse=True,
                no_saved_settings=True,
                width=_current_menu_width(),
                height=_current_menu_height(),
            )
            dpg.bind_item_theme(tag_data, theme.settings_theme)
            content_group = f"{mod}_details_content_group"
            with dpg.group(parent=tag_data, tag=content_group):
                pass
            img_data, _ = mod_details_cache.get(mod, (None, False))
            if img_data:
                try:
                    w, h, _, d = img_data
                    image_tag = f"{mod}_image_texture"
                    dpg.add_static_texture(
                        width=w, height=h, default_value=d, tag=image_tag, parent="mod_images_registry"
                    )
                    shared.mod_details_image_cache[mod] = (w, h, image_tag)
                except Exception as error:
                    print(f"Failed to display image for {mod}: {error}")
            details.render_details_window(mod)

        _create_mod_row(mod, logical_section, enable_ticking, value, has_details, parent_tag=parent_tag)
        checkboxes.append(mod)

    # Persistent command strip: the message gets its own line so long status text
    # can wrap without pushing the action buttons outside the viewport.
    dpg.add_child_window(
        parent="mod_menu",
        tag="mod_manager_statusbar",
        width=max(100, _current_menu_width() - 16),
        height=STATUSBAR_HEIGHT,
        border=False,
        no_scrollbar=True,
        no_scroll_with_mouse=True,
    )
    dpg.bind_item_theme("mod_manager_statusbar", "mod_manager_statusbar_theme")
    dpg.add_text(
        "Ready • Your mod library is loaded.",
        parent="mod_manager_statusbar",
        tag="mod_manager_status_text",
        wrap=max(220, _current_menu_width() - 34),
    )
    dpg.bind_item_theme("mod_manager_status_text", "mod_manager_muted_theme")
    with dpg.group(parent="mod_manager_statusbar", tag="mod_manager_status_actions", horizontal=True):
        dpg.add_button(
            tag="status_error_details_button",
            label="Error details",
            callback=show_error_details,
            width=108,
            height=32,
            show=bool(last_error_text),
        )
        dpg.add_button(
            tag="open_vpk_folder_button", label="Open VPK folder", callback=open_vpk_folder, width=126, height=32
        )
        dpg.add_button(tag="backups_button", label="Restore backups", callback=show_backups, width=132, height=32)
        dpg.add_button(
            tag="review_patch_button", label="Review & Patch", callback=show_patch_preview, width=158, height=36
        )
    dpg.bind_item_theme("review_patch_button", "mod_manager_primary_theme")
    _add_tooltip("open_vpk_folder_button", "Open the folder where Minify manages nested VPK files.")
    _add_tooltip("backups_button", "Restore Minify to an automatic backup from before a patch.")
    _add_tooltip(
        "review_patch_button", "Review selected mods, shared files, and safety information before applying the patch."
    )

    conditions.disable_workshop_mods()
    apply_filters()
    on_resize()
    if last_error_text:
        set_status("Previous operation failed. Error Details are available.", "error")
    else:
        set_status("Your mod library is ready.", "ready")


def get_value(mod):
    return dpg.get_value(mod)


def set_value(mod, value):
    if dpg.does_item_exist(mod):
        dpg.set_value(mod, value)


mods_shared.register_state_callbacks(get_value, set_value)
