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


class RecursiveDirectoryModTests(unittest.TestCase):
    FUNCTION_NAMES = (
        "_is_hidden_or_reserved_dir",
        "_looks_like_directory_mod",
        "_visible_child_directories",
        "_has_explicit_collection_marker",
        "_looks_like_directory_collection",
        "_discover_collection_child_roots",
        "_nested_directory_mod_id",
        "_nested_directory_group",
        "_discover_nested_directory_roots",
        "_discover_directory_mod_entries",
        "get_mod_id_for_path",
        "resolve_mod_reference",
    )

    def _env(self, root):
        return load_mod_shared_functions(
            *self.FUNCTION_NAMES,
            namespace={
                "os": os,
                "base": types.SimpleNamespace(mods_dir=str(root)),
                "mod_paths": {},
                "mod_labels": {},
            },
        )

    def test_collection_children_become_individual_nested_mods(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Mega Pack" / "Mod A").mkdir(parents=True)
            (root / "Mega Pack" / "Mod A" / "manifest.json").write_text("{}", encoding="utf-8")
            (root / "Mega Pack" / "Mod B" / "files").mkdir(parents=True)
            entries = self._env(root)["_discover_directory_mod_entries"]()
            self.assertEqual(
                [item[0] for item in entries],
                ["nested-mod::Mega Pack/Mod A", "nested-mod::Mega Pack/Mod B"],
            )

    def test_large_markerless_collection_promotes_immediate_children(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            collection = root / "Default Skins Mod"
            for name in ("Abaddon", "Alchemist", "Axe", "Bane", "Chen", "Doom", "Invoker", "Pudge"):
                (collection / name / "game" / "models").mkdir(parents=True)
            ids = [item[0] for item in self._env(root)["_discover_directory_mod_entries"]()]
            self.assertEqual(len(ids), 8)
            self.assertIn("nested-mod::Default Skins Mod/Abaddon", ids)
            self.assertIn("nested-mod::Default Skins Mod/Pudge", ids)
            self.assertNotIn("Default Skins Mod", ids)

    def test_collection_child_is_not_split_into_internal_asset_dirs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            collection = root / "Hero Pack"
            for index in range(8):
                hero = collection / f"Hero {index}"
                for internal in ("game", "content", "materials", "models", "scripts", "panorama", "sounds", "particles"):
                    (hero / internal).mkdir(parents=True)
            ids = [item[0] for item in self._env(root)["_discover_directory_mod_entries"]()]
            self.assertEqual(len(ids), 8)
            self.assertTrue(all(mod_id.count("/") == 1 for mod_id in ids))

    def test_explicit_collection_marker_supports_small_collection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            collection = root / "Small Pack"
            collection.mkdir()
            (collection / ".minify-collection").write_text("", encoding="utf-8")
            for name in ("Mod One", "Mod Two"):
                (collection / name / "whatever").mkdir(parents=True)
            ids = [item[0] for item in self._env(root)["_discover_directory_mod_entries"]()]
            self.assertEqual(ids, ["nested-mod::Small Pack/Mod One", "nested-mod::Small Pack/Mod Two"])

    def test_markerless_parent_with_payload_file_stays_legacy_mod(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            legacy = root / "Legacy Multi Dir Mod"
            for index in range(8):
                (legacy / f"asset{index}").mkdir(parents=True)
            (legacy / "custom.cfg").write_text("payload", encoding="utf-8")
            entries = self._env(root)["_discover_directory_mod_entries"]()
            self.assertEqual(entries, [("Legacy Multi Dir Mod", str(legacy))])

    def test_deep_collections_keep_relative_group_and_stable_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mod = root / "Mega Pack" / "Heroes" / "Invoker" / "files"
            mod.mkdir(parents=True)
            env = self._env(root)
            entries = env["_discover_directory_mod_entries"]()
            self.assertEqual(entries[0][0], "nested-mod::Mega Pack/Heroes/Invoker")
            self.assertEqual(env["_nested_directory_group"](mod.parent), "Mega Pack/Heroes")

    def test_existing_top_level_mod_ids_are_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Direct Mod" / "files").mkdir(parents=True)
            self.assertEqual(self._env(root)["_discover_directory_mod_entries"]()[0][0], "Direct Mod")

    def test_markerless_top_level_folder_keeps_legacy_compatibility(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Legacy Mod" / "misc").mkdir(parents=True)
            self.assertEqual(self._env(root)["_discover_directory_mod_entries"]()[0][0], "Legacy Mod")

    def test_reserved_and_hidden_collection_folders_are_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for parent in ("_Private", ".cache"):
                (root / parent / "Hidden Mod" / "files").mkdir(parents=True)
            (root / "Visible" / "Real Mod" / "files").mkdir(parents=True)
            ids = [item[0] for item in self._env(root)["_discover_directory_mod_entries"]()]
            self.assertEqual(ids, ["nested-mod::Visible/Real Mod"])

    def test_scanner_stops_descending_after_finding_a_mod_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outer = root / "Pack" / "Outer Mod"
            (outer / "files" / "Internal Folder").mkdir(parents=True)
            (outer / "files" / "Internal Folder" / "manifest.json").write_text("{}", encoding="utf-8")
            ids = [item[0] for item in self._env(root)["_discover_directory_mod_entries"]()]
            self.assertEqual(ids, ["nested-mod::Pack/Outer Mod"])

    def test_duplicate_folder_names_do_not_collide(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for collection in ("Pack A", "Pack B"):
                (root / collection / "Same Name" / "files").mkdir(parents=True)
            ids = [item[0] for item in self._env(root)["_discover_directory_mod_entries"]()]
            self.assertEqual(ids, ["nested-mod::Pack A/Same Name", "nested-mod::Pack B/Same Name"])

    def test_symlinked_collection_children_are_not_followed(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside_tmp:
            root = Path(tmp)
            outside = Path(outside_tmp) / "Outside Mod"
            (outside / "files").mkdir(parents=True)
            collection = root / "Collection"
            collection.mkdir()
            link = collection / "Linked Mod"
            try:
                link.symlink_to(outside, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("Directory symlinks are unavailable in this environment")
            self.assertEqual(self._env(root)["_discover_directory_mod_entries"](), [("Collection", str(collection))])

    def test_sibling_dependency_names_resolve_to_nested_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ("Core", "Addon"):
                (root / "Pack" / name / "files").mkdir(parents=True)
            env = self._env(root)
            entries = env["_discover_directory_mod_entries"]()
            env["mod_paths"].update(dict(entries))
            env["mod_labels"].update({mod_id: Path(path).name for mod_id, path in entries})
            owner = "nested-mod::Pack/Addon"
            self.assertEqual(env["resolve_mod_reference"]("Core", relative_to=owner), "nested-mod::Pack/Core")
            self.assertEqual(env["get_mod_id_for_path"](root / "Pack" / "Core"), "nested-mod::Pack/Core")
