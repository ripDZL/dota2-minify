"Settings menu"

import os

import dearpygui.dearpygui as dpg
import helper
from core import base, config, constants, mods_shared, registry, steam, utils
from patch import manifest_utils

SETTINGS = [
    {
        "key": "steam_root",
        "text": "Steam Root",
        "default": "",
        "type": "inputbox",
    },
    {
        "key": "steam_library",
        "text": "Steam Library",
        "default": "",
        "type": "inputbox",
    },
    {
        "key": "output_path",
        "text": "Output Path",
        "default": "",
        "type": "inputbox",
    },
    {
        "key": "steam_id",
        "text": "Steam ID",
        "default": "",
        "type": "combo",
        "items_getter": steam.get_steam_accounts,
    },
    {
        "key": "opt_into_rcs",
        "text": "Opt into RCs",
        "default": False,
        "type": "checkbox",
    },
    {
        "key": "fix_options",
        "text": "Handle language option (current ID)",
        "default": True,
        "type": "checkbox",
    },
    {
        "key": "apply_for_all",
        "text": "Apply everything for all users",
        "default": True,
        "type": "checkbox",
    },
    {
        "key": "launch_dota_after_patch",
        "text": "Launch Dota2 after patching",
        "default": False,
        "type": "checkbox",
    },
    {
        "key": "kill_self_after_patch",
        "text": "Close Minify after patching",
        "default": False,
        "type": "checkbox",
    },
    {
        "key": "opt_out_vpk_metadata",
        "text": "Opt-out of VPK metadata",
        "default": False,
        "type": "checkbox",
    },
]
MOD_SETTINGS_WIDGETS = []


def save(sender=None, app_data=None, user_data=None):
    for opt in SETTINGS:
        val = dpg.get_value(f"opt_{opt['key']}")
        if opt["key"] == "steam_id" and val:
            val = val.split(" - ")[0]
        config.set(opt["key"], val)

    for b_conf in registry.get_browser_configs():
        for opt in getattr(b_conf, "SETTINGS", []):
            tag = f"opt_{opt['key']}"
            if dpg.does_item_exist(tag):
                config.set(opt["key"], dpg.get_value(tag))

    for widget in MOD_SETTINGS_WIDGETS:
        if widget.get("type") == "button":
            continue
        tag = widget["tag"]
        mod_name = widget["mod_name"]
        setting_key = widget["key"]
        widget_type = widget["type"]

        if widget_type == "list":
            val = dpg.get_item_configuration(tag)["items"]
        elif widget_type == "color":
            val = dpg.get_value(tag)
        else:
            val = dpg.get_value(tag)

        mod_data = config.get_mod(mod_name)
        mod_data[setting_key] = val
        config.set_mod(mod_name, mod_data)


def apply_preset(sender, app_data, user_data):
    mod_name = user_data["mod_name"]
    presets = user_data["presets"]
    combo_tag = user_data["combo_tag"]

    selected_preset_name = dpg.get_value(combo_tag)
    if not selected_preset_name:
        return

    preset = next((p for p in presets if p["name"] == selected_preset_name), None)
    if not preset:
        return

    mod_data = config.get_mod(mod_name)
    for k, v in preset.get("values", {}).items():
        mod_data[k] = v

    config.set_mod(mod_name, mod_data)
    refresh()


def handle_button_click(sender, app_data, user_data):
    mod_name = user_data["mod_name"]
    function_name = user_data["key"]
    script_path = os.path.join(mods_shared.get_mod_path(mod_name), "script_utility.py")
    helper.exec_script_function(script_path, mod_name, function_name)


def refresh(sender=None, app_data=None, user_data=None):
    render_menu()


def reset(sender=None, app_data=None, user_data=None):
    config.set("modconf", {})
    render_menu()


def render_menu(parent="settings_menu"):
    global MOD_SETTINGS_WIDGETS
    MOD_SETTINGS_WIDGETS.clear()

    if dpg.does_item_exist("settings_content_group"):
        dpg.delete_item("settings_content_group", children_only=True)
    else:
        dpg.add_group(parent=parent, tag="settings_content_group")

    dpg.add_text("SETTINGS", parent="settings_content_group", tag="settings_eyebrow")
    dpg.add_text("Minify preferences", parent="settings_content_group", tag="settings_title")
    dpg.bind_item_font("settings_title", "large_font")
    dpg.add_text(
        "Everyday options are grouped by what they affect. Advanced mod settings stay below.",
        parent="settings_content_group",
        tag="settings_intro",
        wrap=620,
    )

    groups = (
        ("Paths & Steam", {"steam_root", "steam_library", "output_path", "steam_id"}),
        ("Patch behavior", {"fix_options", "apply_for_all", "launch_dota_after_patch", "kill_self_after_patch"}),
        ("Updates & privacy", {"opt_into_rcs", "opt_out_vpk_metadata"}),
    )

    def add_option(opt, parent):
        _tag = f"opt_{opt['key']}"
        _text = opt.get("text") if opt["type"] == "checkbox" else f"{opt.get('text')}:"
        _default_value = config.get(opt["key"], opt["default"])
        if opt["type"] == "checkbox":
            dpg.add_checkbox(parent=parent, tag=_tag, label=_text, default_value=_default_value)
        elif opt["type"] == "combo":
            dpg.add_text(_text, parent=parent)
            raw_items = opt["items_getter"]() if "items_getter" in opt else opt.get("items", [])
            if raw_items and isinstance(raw_items[0], dict):
                items = [f"{item['id']} - {item['name']}" for item in raw_items]
            else:
                items = raw_items
            if opt["key"] == "steam_id" and _default_value:
                for item in items:
                    if item.startswith(f"{_default_value} - "):
                        _default_value = item
                        break
            dpg.add_combo(parent=parent, tag=_tag, items=items, default_value=_default_value, width=-1)
        else:
            dpg.add_text(_text, parent=parent)
            dpg.add_input_text(parent=parent, tag=_tag, default_value=_default_value, width=-1)

    for title, keys in groups:
        header = dpg.add_collapsing_header(parent="settings_content_group", label=title, default_open=True)
        for opt in SETTINGS:
            if opt["key"] in keys:
                add_option(opt, header)

    browser_settings = [
        opt
        for b_conf in registry.get_browser_configs()
        for opt in getattr(b_conf, "SETTINGS", [])
    ]
    if browser_settings:
        browser_header = dpg.add_collapsing_header(parent="settings_content_group", label="Browser integrations", default_open=False)
        for opt in browser_settings:
            add_option(opt, browser_header)

    mod_settings_found = False
    for mod in constants.mods_alphabetical:
        mod_path = mods_shared.get_mod_path(mod)
        if mod.endswith(".vpk"):
            continue
        mod_config = manifest_utils.get_mod(mod_path)
        always = mod_config.get("always", False)
        mod_enabled = dpg.does_item_exist(mod) and dpg.get_value(mod)
        settings_to_render = [
            opt for opt in mod_config.get("settings", [])
            if always or mod_enabled or opt.get("force", False)
        ]
        if not settings_to_render:
            continue
        if not mod_settings_found:
            dpg.add_separator(parent="settings_content_group")
            dpg.add_text("MOD OPTIONS", parent="settings_content_group")
            mod_settings_found = True
        mod_header = dpg.add_collapsing_header(parent="settings_content_group", label=mods_shared.get_mod_label(mod), default_open=False)
        saved_mod_data = config.get_mod(mod)
        presets = mod_config.get("presets", [])
        if presets:
            preset_names = [preset["name"] for preset in presets]
            current_preset = ""
            for preset in presets:
                if all(saved_mod_data.get(k) == v for k, v in preset.get("values", {}).items()):
                    current_preset = preset["name"]
                    break
            combo_tag = f"preset_combo_{mod}"
            with dpg.group(parent=mod_header, horizontal=True):
                dpg.add_combo(tag=combo_tag, items=preset_names, default_value=current_preset, width=180)
                dpg.add_button(label="Apply preset", callback=apply_preset, user_data={"mod_name": mod, "presets": presets, "combo_tag": combo_tag})

        for opt in settings_to_render:
            _tag = f"mod_opt_{mod}_{opt['key']}"
            _text = opt.get("text") if opt["type"] == "checkbox" else f"{opt.get('text')}:"
            _default_value = saved_mod_data.get(opt["key"], opt.get("default", ""))
            if opt["type"] == "checkbox":
                dpg.add_checkbox(parent=mod_header, tag=_tag, label=_text, default_value=_default_value)
            elif opt["type"] == "combo":
                dpg.add_text(_text, parent=mod_header)
                dpg.add_combo(parent=mod_header, tag=_tag, items=opt.get("items", []), default_value=_default_value, width=-1)
            elif opt["type"] == "number":
                dpg.add_text(_text, parent=mod_header)
                if opt.get("var_type", "int") == "float":
                    dpg.add_input_float(parent=mod_header, tag=_tag, default_value=float(_default_value) if _default_value else 0.0, step=opt.get("step", 0.1), width=-1)
                else:
                    dpg.add_input_int(parent=mod_header, tag=_tag, default_value=int(_default_value) if _default_value else 0, step=opt.get("step", 1), width=-1)
            elif opt["type"] == "slider":
                dpg.add_text(_text, parent=mod_header)
                _callback = snap_slider if opt.get("step") else None
                _user_data = {"step": opt.get("step")} if opt.get("step") else None
                if opt.get("var_type", "int") == "float":
                    dpg.add_slider_float(parent=mod_header, tag=_tag, default_value=float(_default_value) if _default_value else 0.0, min_value=float(opt.get("min", 0)), max_value=float(opt.get("max", 100)), width=-1, callback=_callback, user_data=_user_data)
                else:
                    dpg.add_slider_int(parent=mod_header, tag=_tag, default_value=int(_default_value) if _default_value else 0, min_value=int(opt.get("min", 0)), max_value=int(opt.get("max", 100)), width=-1, callback=_callback, user_data=_user_data)
            elif opt["type"] == "color":
                dpg.add_text(_text, parent=mod_header)
                with dpg.group(parent=mod_header, horizontal=True):
                    dpg.add_input_text(tag=_tag, default_value=_default_value if isinstance(_default_value, str) else utils.rgba_to_hex(_default_value), width=-120, callback=lambda s, a, u: dpg.set_value(u, utils.hex_to_rgba(a)), user_data=f"{_tag}_preview")
                    dpg.add_color_button(tag=f"{_tag}_preview", default_value=utils.parse_color(_default_value))
            elif opt["type"] == "list":
                dpg.add_text(_text, parent=mod_header)
                dpg.add_listbox(parent=mod_header, tag=_tag, items=_default_value if isinstance(_default_value, list) else [], width=-1, num_items=5)
                input_tag = f"{_tag}_input"
                with dpg.group(parent=mod_header, horizontal=True):
                    dpg.add_input_text(tag=input_tag, width=-130)
                    dpg.add_button(label="Add", width=60, callback=add_to_list, user_data={"listbox_tag": _tag, "input_tag": input_tag})
                    dpg.add_button(label="Remove", width=60, callback=remove_from_list, user_data={"listbox_tag": _tag})
            elif opt["type"] == "button":
                dpg.add_button(parent=mod_header, tag=_tag, label=opt.get("text", opt["key"]), callback=handle_button_click, user_data={"mod_name": mod, "key": opt["key"]}, width=-1)
            else:
                dpg.add_text(_text, parent=mod_header)
                dpg.add_input_text(parent=mod_header, tag=_tag, default_value=_default_value, width=-1)
            MOD_SETTINGS_WIDGETS.append({"tag": _tag, "mod_name": mod, "key": opt["key"], "type": opt["type"]})


def add_to_list(sender, app_data, user_data):
    listbox_tag = user_data["listbox_tag"]
    input_tag = user_data["input_tag"]
    new_item = dpg.get_value(input_tag)
    if new_item:
        items = dpg.get_item_configuration(listbox_tag)["items"]
        if new_item not in items:
            items.append(new_item)
            dpg.configure_item(listbox_tag, items=items)
            dpg.set_value(input_tag, "")


def remove_from_list(sender, app_data, user_data):
    listbox_tag = user_data["listbox_tag"]
    selected_item = dpg.get_value(listbox_tag)
    if selected_item:
        items = dpg.get_item_configuration(listbox_tag)["items"]
        if selected_item in items:
            items.remove(selected_item)
            dpg.configure_item(listbox_tag, items=items)


def snap_slider(sender, app_data, user_data):
    step = user_data.get("step")
    if step:
        step = float(step)
        snapped_val = round(app_data / step) * step
        dpg.set_value(sender, snapped_val)
