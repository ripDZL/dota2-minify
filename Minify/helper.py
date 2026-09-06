"Dangling random functions"

import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog

import dearpygui.dearpygui as dpg
import vpk
from core import base, config, constants, fs, log, mods_shared, output, utils
from patch import manifest_utils

compiler_filepicker_path = ""
output_path = config.get("output_path", constants.minify_default_dota_pak_output_path)

_NATIVE_FILE_DIALOGS = {
    "d2pfx_import_dialog": ("open", (("ZIP archives", "*.zip"), ("All files", "*.*"))),
    "profile_import_dialog": ("open", (("JSON files", "*.json"), ("All files", "*.*"))),
    "profile_export_dialog": ("directory", ()),
}
_ORIGINAL_DPG_CONFIGURE_ITEM = dpg.configure_item


def _run_native_dialog(kind, filetypes=()):
    """Open a native Windows file/folder picker and return the selected path."""
    root = tk.Tk()
    root.withdraw()
    try:
        root.attributes("-topmost", True)
        if kind == "directory":
            return filedialog.askdirectory(parent=root)
        return filedialog.askopenfilename(parent=root, filetypes=filetypes)
    finally:
        root.destroy()


def _show_native_file_dialog(item):
    """Handle a known DPG file-dialog tag with the native system picker."""
    dialog = _NATIVE_FILE_DIALOGS.get(item)
    if not dialog:
        return False

    kind, filetypes = dialog
    try:
        path = _run_native_dialog(kind, filetypes)
    except Exception as exc:
        log.write_warning(f"Native file picker unavailable; falling back to Minify dialog: {exc}")
        return False

    # Cancellation is still a handled native-dialog request. Do not expose the
    # themed DPG browser after the user intentionally closed the system picker.
    if not path:
        return True

    callback = dpg.get_item_callback(item)
    if callable(callback):
        app_data = {
            "file_path_name": path,
            "current_path": path,
            "selections": {os.path.basename(path): path},
        }
        callback(item, app_data, None)
    return True


def _configure_item_with_native_file_dialog(item, **kwargs):
    if kwargs.get("show") is True and item in _NATIVE_FILE_DIALOGS:
        if _show_native_file_dialog(item):
            return None
    return _ORIGINAL_DPG_CONFIGURE_ITEM(item, **kwargs)


def _install_native_file_dialog_bridge():
    """Use system file dialogs for user browsing on Windows."""
    if not base.is_win or getattr(dpg.configure_item, "_minify_native_file_dialog_bridge", False):
        return
    _configure_item_with_native_file_dialog._minify_native_file_dialog_bridge = True
    dpg.configure_item = _configure_item_with_native_file_dialog


_install_native_file_dialog_bridge()


def get_blank_file_extensions():
    extensions = []
    for file in os.listdir(base.blank_files_dir):
        extensions.append(os.path.splitext(file)[1])
    return extensions


def change_output_path():
    global output_path
    selection = dpg.get_value("output_select")
    resolved = constants.resolve_locale(selection)
    output_path = [lang for lang in constants.minify_dota_possible_language_output_paths if resolved in lang][0]
    config.set("output_locale", selection)
    config.set("output_path", output_path)


def compile():
    """
    A wrapper for the Dota 2 Resource Compiler.
    """
    with open(base.log_rescomp, "wb") as file:
        command = [
            constants.dota_resource_compiler_path,
            "-i",
            constants.minify_dota_compile_input_path + "/*",
            "-r",
        ]

        if not base.is_win:
            command.insert(0, "wine")

        rescomp = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW if base.is_win else 0,
        )
        if rescomp.stdout != b"":
            file.write(rescomp.stdout)


def compile_assets(input_path=None, output_path=None, pak_path=None, sender=None, app_data=None, user_data=None):
    """
    resourcecompiler's friendly cousin
    Automagically handles image compilation
    """
    if compiler_filepicker_path:
        input_path = compiler_filepicker_path
        output_path = os.path.join(input_path, os.pardir, "#Minify_compiled")
        output.clean()
    if not output_path:
        output_path = os.path.join(input_path, os.pardir, "#Minify_compiled")

    img_list = [str(f.relative_to(input_path)) for f in Path(input_path).rglob("*.png") if f.is_file()]

    if os.path.exists(input_path):
        output.add_text("&compile_init", input_path)
        fs.remove_path(constants.minify_dota_compile_input_path, output_path)
        fs.create_dirs(constants.minify_dota_compile_input_path)

        with utils.open_utf8(os.path.join(input_path, "ref.xml"), "w") as file:
            file.write(create_img_ref_xml(img_list))

        items = os.listdir(input_path)

        for item in items:
            if os.path.isdir(os.path.join(input_path, item)):
                shutil.copytree(
                    os.path.join(input_path, item),
                    os.path.join(constants.minify_dota_compile_input_path, item),
                )
            else:
                shutil.copy(os.path.join(input_path, item), constants.minify_dota_compile_input_path)

        compile()

        fs.create_dirs(constants.minify_dota_compile_output_path)
        shutil.copytree(os.path.join(constants.minify_dota_compile_output_path), output_path)

        fs.remove_path(
            constants.minify_dota_compile_input_path,
            constants.minify_dota_compile_output_path,
            os.path.join(input_path, "ref.xml"),
            os.path.join(output_path, "ref.vxml_c"),
        )
        fs.create_dirs(constants.minify_dota_tools_required_path)

        output.add_text("&compile_successful", output_path)

        if pak_path:
            vpk_file = vpk.new(output_path)
            vpk_file.save(pak_path)
            output.add_text("&compile_created_pak", pak_path)
    else:
        output.add_text("&compile_no_path")


def create_img_ref_xml(img_path_list):
    "Helper function to create reference XMLs for images"
    xml_list = []
    for img_path in img_path_list:
        xml_list.append(f'\t\t\t<Image src="file://{img_path}" />')

    return rf"""<root>
    <Panel class="AddonLoadingRoot">
{"\n".join(xml_list)}
    </Panel>
</root>
"""


def select_compile_dir(sender=None, app_data=None):
    global compiler_filepicker_path
    root = tk.Tk()
    root.withdraw()
    path = filedialog.askdirectory(initialdir=os.getcwd())
    root.destroy()
    if path:
        compiler_filepicker_path = path


def exec_script(script_path, mod_name, order_name, _terminal_output=True):
    """
    Injects code
    Only called for `script.py`
    """
    if os.path.exists(script_path):
        mod_dir = os.path.dirname(script_path)
        cfg = manifest_utils.get_mod(mod_dir)
        if cfg.get("browser"):
            log.write_warning(f"Python script execution is disabled for browser mods: {mod_name}")
            return

        script_dir = os.path.dirname(script_path)
        if script_dir in sys.path:
            sys.path.remove(script_dir)
        sys.path.insert(0, script_dir)
        sys.modules.pop("script", None)

        safe_mod_name = re.sub(r"[^a-zA-Z0-9_]+", "_", str(mod_name)).strip("_").lower() or "mod"
        module_name = safe_mod_name + f"_{order_name}_script"
        spec = importlib.util.spec_from_file_location(module_name, script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        main_func = getattr(module, "main", None)
        if callable(main_func):
            if _terminal_output:
                output.add_text("&script_execution", mod_name, order_name)
            result = main_func()
            if _terminal_output:
                output.add_text("&script_success", mod_name, order_name, msg_type="success")
            return result
        else:
            log.write_warning("&script_no_main", mod_name, order_name)

    return None


def bulk_exec_script(order_name, terminal_output=True):
    """Run lifecycle scripts for discovered directory-backed mods.

    rc7 uses the boolean return value for ``script_prelaunch.py`` so the CLI can
    record whether a prelaunch action changed anything. Preserve that contract
    while resolving nested/collection mods through their stable discovered IDs.
    """
    bulk_name = f"script_{order_name}.py"
    any_ran = False
    for mod_name in list(mods_shared.mods_with_order):
        mod_path = mods_shared.get_mod_path(mod_name)
        if not os.path.isdir(mod_path):
            continue
        script_path = os.path.join(mod_path, bulk_name)
        if not os.path.isfile(script_path):
            continue
        cfg = manifest_utils.get_mod(mod_path)
        if "browser" in cfg:
            continue
        always = cfg.get("always", False)
        if always or order_name in ["initial", "uninstall"] or mods_shared.get_state(mod_name):
            result = exec_script(script_path, mod_name, order_name, _terminal_output=terminal_output)
            if result:
                any_ran = True
    return any_ran


def exec_script_function(script_path, mod_name, function_name="main"):
    """
    Executes a specific function from a Python script file
    """
    if os.path.exists(script_path):
        mod_dir = os.path.dirname(script_path)
        cfg = manifest_utils.get_mod(mod_dir)
        if cfg.get("browser"):
            log.write_warning(f"Python script execution is disabled for browser mods: {mod_name}")
            return

        script_dir = os.path.dirname(script_path)
        if script_dir in sys.path:
            sys.path.remove(script_dir)
        sys.path.insert(0, script_dir)
        sys.modules.pop("script", None)

        safe_mod_name = re.sub(r"[^a-zA-Z0-9_]+", "_", str(mod_name)).strip("_").lower() or "mod"
        module_name = safe_mod_name + "_utility"
        spec = importlib.util.spec_from_file_location(module_name, script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        func = getattr(module, function_name, None)
        if callable(func):
            func()
        else:
            log.write_warning(f"Function '{function_name}' not found in {script_path}")
    else:
        log.write_warning(f"Script file not found: {script_path}")
