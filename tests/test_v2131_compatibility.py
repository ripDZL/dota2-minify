from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOD_COMPAT = ROOT / "Minify" / "core" / "mod_compat.py"
FOILAGE = ROOT / "Minify" / "mods" / "Remove Foilage"
MENU_CSS = ROOT / "Minify" / "mods" / "Remove Main Menu Background" / "styling.css"
DEFERRED = "materials/dev/deferred_post_process.vmat_c"
FOG = "materials/dev/deferred_post_process_vmat_g_tfog_9ea98ee9.vtex_c"


def load_mod_compat(labels=None, filenames=None, metadata=None, paths=None, owners=None):
    labels = labels or {}
    filenames = filenames or {}
    metadata = metadata or {}
    paths = paths or {}
    owners = owners or {}

    fake_shared = types.SimpleNamespace(
        get_mod_label=lambda mod: labels.get(mod, mod),
        get_mod_filename=lambda mod: filenames.get(mod, os.path.basename(str(mod))),
        get_mod_metadata=lambda mod: metadata.get(mod, {}),
        get_mod_path=lambda mod: paths.get(mod, str(mod)),
    )

    def fingerprint_entry(mod, virtual_path):
        if virtual_path in owners.get(mod, set()):
            return {"sha256": f"owned-{mod}", "size": 1, "origin": "test"}
        return {}

    fake_core = types.ModuleType("core")
    fake_core.mods_shared = fake_shared
    fake_core.mod_library = types.SimpleNamespace(fingerprint_entry=fingerprint_entry)
    previous_core = sys.modules.get("core")
    previous_library = sys.modules.get("core.mod_library")
    try:
        sys.modules["core"] = fake_core
        sys.modules["core.mod_library"] = fake_core.mod_library
        spec = importlib.util.spec_from_file_location("test_v2131_mod_compat", MOD_COMPAT)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)
        module._fingerprint_entry = fingerprint_entry
        return module
    finally:
        if previous_core is None:
            sys.modules.pop("core", None)
        else:
            sys.modules["core"] = previous_core
        if previous_library is None:
            sys.modules.pop("core.mod_library", None)
        else:
            sys.modules["core.mod_library"] = previous_library


class DarkTerrainCompatibilityTests(unittest.TestCase):
    def setUp(self):
        self.dark = "Dark Terrain"
        self.simple = "Simple.Dark.Terrain"
        self.green = "D2PFX SHADERS - Wave Lite Green"
        self.aqua = "D2PFX SHADERS - Wave Lite Aqua"
        self.labels = {
            self.dark: "Dark Terrain",
            self.simple: "Simple.Dark.Terrain",
            self.green: "Wave Lite Green",
            self.aqua: "Wave Lite Aqua",
        }

    def _compat(self, owners=None, paths=None):
        return load_mod_compat(labels=self.labels, owners=owners, paths=paths)

    def test_dark_terrain_alone_keeps_its_deferred_resources(self):
        compat = self._compat()
        self.assertIsNone(compat.active_dark_terrain_rule([self.dark]))
        self.assertEqual(compat.exclusions_for_mod(self.dark, [self.dark]), set())
        self.assertEqual(compat.planned_resource_actions([self.dark]), [])

    def test_rule_activates_only_for_real_deferred_resource_owner(self):
        owners = {self.green: {DEFERRED}}
        compat = self._compat(owners=owners)
        rule = compat.active_dark_terrain_rule([self.dark, self.green])
        self.assertIsNotNone(rule)
        self.assertEqual(rule["dark"], self.dark)
        self.assertEqual(rule["competitors"], [self.green])
        self.assertEqual(rule["winner"], self.green)
        self.assertEqual(set(rule["exclude_from_dark"]), {DEFERRED, FOG})
        self.assertEqual(compat.exclusions_for_mod(self.dark, [self.dark, self.green]), {DEFERRED, FOG})

    def test_shader_name_without_resource_ownership_does_not_trigger_rule(self):
        compat = self._compat()
        self.assertIsNone(compat.active_dark_terrain_rule([self.dark, self.green, self.aqua]))
        self.assertEqual(compat.exclusions_for_mod(self.dark, [self.dark, self.green]), set())

    def test_simple_dark_terrain_blends_are_never_auto_removed(self):
        compat = self._compat(owners={self.green: {DEFERRED}})
        excluded = compat.exclusions_for_mod(self.dark, [self.dark, self.simple, self.green])
        self.assertFalse(any(path.startswith("materials/blends/") for path in excluded))
        result = compat.classify_collision("materials/blends/mod_dire_000.vmat_c", [self.dark, self.simple], {})
        self.assertEqual(result["classification"], "intentional override")
        self.assertFalse(result["auto_fix"])

    def test_copy_standard_files_keeps_dark_resources_without_collision(self):
        compat = self._compat()
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src"
            dst = Path(tmp) / "dst"
            (src / "materials/dev").mkdir(parents=True)
            (src / DEFERRED).write_bytes(b"dark-vmat")
            (src / FOG).write_bytes(b"dark-fog")
            excluded = compat.copy_standard_files(self.dark, str(src), str(dst), [self.dark])
            self.assertEqual(excluded, [])
            self.assertEqual((dst / DEFERRED).read_bytes(), b"dark-vmat")
            self.assertEqual((dst / FOG).read_bytes(), b"dark-fog")

    def test_copy_standard_files_filters_dark_resources_for_real_collision(self):
        compat = self._compat(owners={self.green: {DEFERRED}})
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src"
            dst = Path(tmp) / "dst"
            (src / "materials/dev").mkdir(parents=True)
            (src / "materials/blends").mkdir(parents=True)
            (src / DEFERRED).write_bytes(b"dark-vmat")
            (src / FOG).write_bytes(b"dark-fog")
            (src / "materials/blends/mod_dire_000.vmat_c").write_bytes(b"intentional")
            (src / "keep.bin").write_bytes(b"keep")
            excluded = compat.copy_standard_files(self.dark, str(src), str(dst), [self.dark, self.green])
            self.assertEqual(set(excluded), {DEFERRED, FOG})
            self.assertFalse((dst / DEFERRED).exists())
            self.assertFalse((dst / FOG).exists())
            self.assertEqual((dst / "materials/blends/mod_dire_000.vmat_c").read_bytes(), b"intentional")
            self.assertEqual((dst / "keep.bin").read_bytes(), b"keep")

    def test_non_dark_mod_is_never_filtered_by_dark_rule(self):
        compat = self._compat(owners={self.green: {DEFERRED}})
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src"
            dst = Path(tmp) / "dst"
            (src / "materials/dev").mkdir(parents=True)
            (src / DEFERRED).write_bytes(b"green-vmat")
            excluded = compat.copy_standard_files(self.green, str(src), str(dst), [self.dark, self.green])
            self.assertEqual(excluded, [])
            self.assertEqual((dst / DEFERRED).read_bytes(), b"green-vmat")

    def test_planned_actions_describe_collision_driven_exclusions(self):
        compat = self._compat(owners={self.green: {DEFERRED}})
        actions = compat.planned_resource_actions([self.dark, self.green])
        self.assertEqual({item["path"] for item in actions}, {DEFERRED, FOG})
        self.assertTrue(all(item["mod"] == self.dark for item in actions))

    def test_collision_classifier_keeps_other_owner_as_winner(self):
        compat = self._compat()
        result = compat.classify_collision(
            DEFERRED,
            [self.dark, self.green],
            {self.dark: {"sha256": "a"}, self.green: {"sha256": "b"}},
        )
        self.assertEqual(result["classification"], "true conflict")
        self.assertEqual(result["winner"], self.green)
        self.assertTrue(result["auto_fix"])

    def test_no_shader_name_allowlist_regression(self):
        source = MOD_COMPAT.read_text(encoding="utf-8")
        self.assertNotIn("active_dark_aqua_rule", source)
        self.assertNotIn("is_aqua_wave_lite", source)
        self.assertIn("_owns_deferred_resource", source)
        self.assertIn("_deferred_competitors", source)


class SafeFoliageAndMenuTests(unittest.TestCase):
    def test_remove_foilage_is_blacklist_only_and_has_oak_leaf_entries(self):
        self.assertFalse((FOILAGE / "manifest.json").exists())
        self.assertFalse((FOILAGE / "maps" / "dota.vpk").exists())
        blacklist = (FOILAGE / "blacklist.txt").read_text(encoding="utf-8-sig")
        for entry in (
            "materials/models/props_tree/tree_oak_leaves_05.vmat_c",
            "models/props_tree/tree_oak_leaves_05.vmdl_c",
        ):
            self.assertEqual(blacklist.count(entry), 1)

    def test_main_menu_background_keeps_both_collapse_rules(self):
        css = MENU_CSS.read_text(encoding="utf-8")
        self.assertIn("DOTADashboardBackgroundManager:not(.Hidden)", css)
        self.assertIn("#FrontpageContents", css)
        self.assertGreaterEqual(css.count("visibility: collapse"), 2)
