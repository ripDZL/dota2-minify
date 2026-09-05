from __future__ import annotations

import ast
import os
import tempfile
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODS_SHARED = ROOT / "Minify" / "core" / "mods_shared.py"


def load_mod_shared_functions(*names: str, namespace: dict | None = None) -> dict:
    source = MODS_SHARED.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(MODS_SHARED))
    constants = {
        "NESTED_DIR_PREFIX",
        "DIRECTORY_MOD_MARKER_FILES",
        "DIRECTORY_MOD_MARKER_DIRS",
        "MAX_NESTED_MOD_SCAN_DEPTH",
        "MAX_NESTED_MOD_SCAN_DIRS",
        "COLLECTION_MARKER_FILE",
        "AUTO_COLLECTION_MIN_CHILDREN",
        "COLLECTION_NON_PAYLOAD_FILES",
    }
    nodes = []
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id in constants for target in node.targets
        ):
            nodes.append(node)
        elif isinstance(node, ast.FunctionDef) and node.name in names:
            nodes.append(node)
    found = {node.name for node in nodes if isinstance(node, ast.FunctionDef)}
    missing = set(names) - found
    if missing:
        raise AssertionError(f"Missing functions in mods_shared.py: {sorted(missing)}")
    env = {} if namespace is None else dict(namespace)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(MODS_SHARED), "exec"), env)
    return env


class CustomVpkCategoryTests(unittest.TestCase):
    FUNCTION_NAMES = (
        "_is_hidden_or_reserved_dir",
        "_looks_like_directory_mod",
        "_visible_child_directories",
        "_has_explicit_collection_marker",
        "_looks_like_directory_collection",
        "_discover_collection_child_roots",
        "_directory_contains_vpk",
        "_discover_vpk_collection_child_roots",
        "_nested_directory_mod_id",
        "_nested_directory_group",
        "_discover_nested_directory_roots",
        "_discover_directory_mod_entries",
    )

    def _env(self, root: Path) -> dict:
        return load_mod_shared_functions(
            *self.FUNCTION_NAMES,
            namespace={
                "os": os,
                "base": types.SimpleNamespace(mods_dir=str(root)),
            },
        )

    def test_small_custom_folder_with_vpk_children_becomes_category(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "My Custom Pack" / "Hero A").mkdir(parents=True)
            (root / "My Custom Pack" / "Hero A" / "skin.vpk").write_bytes(b"a")
            (root / "My Custom Pack" / "Hero B" / "nested").mkdir(parents=True)
            (root / "My Custom Pack" / "Hero B" / "nested" / "effect.VPK").write_bytes(b"b")

            env = self._env(root)
            entries = env["_discover_directory_mod_entries"]()
            self.assertEqual(
                [mod_id for mod_id, _ in entries],
                ["nested-mod::My Custom Pack/Hero A", "nested-mod::My Custom Pack/Hero B"],
            )
            self.assertEqual(env["_nested_directory_group"](Path(entries[0][1])), "My Custom Pack")

    def test_non_vpk_sibling_is_not_promoted_as_a_mod(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = root / "My Custom Pack"
            (pack / "Hero A").mkdir(parents=True)
            (pack / "Hero A" / "skin.vpk").write_bytes(b"a")
            (pack / "Notes").mkdir(parents=True)
            (pack / "Notes" / "readme.txt").write_text("notes", encoding="utf-8")

            ids = [mod_id for mod_id, _ in self._env(root)["_discover_directory_mod_entries"]()]
            self.assertEqual(ids, ["nested-mod::My Custom Pack/Hero A"])

    def test_recognized_directory_mod_sibling_is_kept_with_vpk_children(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = root / "Mixed Pack"
            (pack / "VPK Mod").mkdir(parents=True)
            (pack / "VPK Mod" / "skin.vpk").write_bytes(b"vpk")
            (pack / "Folder Mod" / "files").mkdir(parents=True)

            ids = [mod_id for mod_id, _ in self._env(root)["_discover_directory_mod_entries"]()]
            self.assertEqual(ids, ["nested-mod::Mixed Pack/Folder Mod", "nested-mod::Mixed Pack/VPK Mod"])

    def test_top_level_directory_mod_with_embedded_vpk_keeps_legacy_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mod = root / "Direct Mod"
            (mod / "files").mkdir(parents=True)
            (mod / "files" / "payload.vpk").write_bytes(b"vpk")

            entries = self._env(root)["_discover_directory_mod_entries"]()
            self.assertEqual(entries, [("Direct Mod", str(mod))])

    def test_hidden_or_reserved_vpk_descendants_do_not_trigger_category(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = root / "Ordinary Folder"
            (pack / "Child" / ".cache").mkdir(parents=True)
            (pack / "Child" / ".cache" / "hidden.vpk").write_bytes(b"hidden")
            (pack / "Child" / "_staging").mkdir(parents=True)
            (pack / "Child" / "_staging" / "staged.vpk").write_bytes(b"staged")

            env = self._env(root)
            self.assertEqual(env["_discover_vpk_collection_child_roots"](str(pack)), [])
            self.assertEqual(env["_discover_directory_mod_entries"](), [("Ordinary Folder", str(pack))])


if __name__ == "__main__":
    unittest.main()
