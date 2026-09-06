from __future__ import annotations

import ast
import os
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "Minify" / "helper.py"


def load_native_dialog_functions(*names: str, namespace: dict | None = None) -> dict:
    source = HELPER.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(HELPER))
    wanted_assignments = {"_NATIVE_FILE_DIALOGS"}
    nodes = []
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id in wanted_assignments for target in node.targets
        ):
            nodes.append(node)
        elif isinstance(node, ast.FunctionDef) and node.name in names:
            nodes.append(node)
    found = {node.name for node in nodes if isinstance(node, ast.FunctionDef)}
    missing = set(names) - found
    if missing:
        raise AssertionError(f"Missing native dialog functions: {sorted(missing)}")
    env = {} if namespace is None else dict(namespace)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(HELPER), "exec"), env)
    return env


class NativeFileDialogTests(unittest.TestCase):
    def test_known_library_file_dialogs_are_routed_to_system_picker(self):
        source = HELPER.read_text(encoding="utf-8")
        self.assertIn('"d2pfx_import_dialog": ("open"', source)
        self.assertIn('"profile_import_dialog": ("open"', source)
        self.assertIn('"profile_export_dialog": ("directory"', source)
        self.assertIn("filedialog.askopenfilename", source)
        self.assertIn("filedialog.askdirectory", source)
        self.assertIn("if not base.is_win", source)

    def test_native_selection_reuses_existing_dpg_callback_contract(self):
        calls = []
        callback = lambda sender, app_data, user_data: calls.append((sender, app_data, user_data))
        fake_dpg = types.SimpleNamespace(get_item_callback=lambda item: callback)
        env = load_native_dialog_functions(
            "_show_native_file_dialog",
            namespace={
                "dpg": fake_dpg,
                "os": os,
                "log": types.SimpleNamespace(write_warning=lambda *args: None),
                "_run_native_dialog": lambda kind, filetypes=(): r"C:\Users\Tester\Downloads\profiles.json",
            },
        )

        self.assertTrue(env["_show_native_file_dialog"]("profile_import_dialog"))
        self.assertEqual(len(calls), 1)
        sender, app_data, user_data = calls[0]
        self.assertEqual(sender, "profile_import_dialog")
        self.assertEqual(app_data["file_path_name"], r"C:\Users\Tester\Downloads\profiles.json")
        self.assertEqual(app_data["current_path"], app_data["file_path_name"])
        self.assertIsNone(user_data)

    def test_native_cancel_does_not_reopen_themed_dialog(self):
        fake_dpg = types.SimpleNamespace(get_item_callback=lambda item: None)
        env = load_native_dialog_functions(
            "_show_native_file_dialog",
            namespace={
                "dpg": fake_dpg,
                "os": os,
                "log": types.SimpleNamespace(write_warning=lambda *args: None),
                "_run_native_dialog": lambda kind, filetypes=(): "",
            },
        )
        self.assertTrue(env["_show_native_file_dialog"]("d2pfx_import_dialog"))

    def test_unrelated_configure_item_calls_still_use_dearpygui(self):
        original_calls = []
        env = load_native_dialog_functions(
            "_configure_item_with_native_file_dialog",
            namespace={
                "_NATIVE_FILE_DIALOGS": {
                    "profile_import_dialog": ("open", ()),
                },
                "_show_native_file_dialog": lambda item: True,
                "_ORIGINAL_DPG_CONFIGURE_ITEM": lambda item, **kwargs: original_calls.append((item, kwargs)),
            },
        )
        env["_configure_item_with_native_file_dialog"]("ordinary_widget", show=True, width=100)
        self.assertEqual(original_calls, [("ordinary_widget", {"show": True, "width": 100})])


if __name__ == "__main__":
    unittest.main()
