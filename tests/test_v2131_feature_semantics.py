from __future__ import annotations

import ast
import datetime as dt
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKBOXES = ROOT / "Minify" / "ui" / "checkboxes.py"
D2PFX_UI = ROOT / "Minify" / "browsers" / "d2pfx" / "ui.py"
MOD_LIBRARY = ROOT / "Minify" / "core" / "mod_library.py"


def load_functions(path: Path, *names: str, namespace: dict | None = None) -> dict:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    wanted = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
    missing = set(names) - {node.name for node in wanted}
    if missing:
        raise AssertionError(f"Missing functions in {path.name}: {sorted(missing)}")
    env = {} if namespace is None else dict(namespace)
    exec(compile(ast.Module(body=wanted, type_ignores=[]), str(path), "exec"), env)
    return env


class FakeDPG:
    def __init__(self, values):
        self.values = dict(values)

    def does_item_exist(self, tag):
        return tag in self.values

    def get_value(self, tag):
        return self.values[tag]


class SearchStateTests(unittest.TestCase):
    def test_capture_search_accepts_empty_string(self):
        ui_state = {
            "search": "old",
            "state_filter": "All",
            "type_filter": "All Mods",
            "category_filter": "All Categories",
            "sort": "Name A-Z",
        }
        dpg = FakeDPG(
            {
                "mod_search": "",
                "mod_state_filter": "All",
                "mod_type_filter": "All Mods",
                "mod_category_filter": "All Categories",
                "mod_sort": "Name A-Z",
            }
        )
        env = load_functions(CHECKBOXES, "_capture_ui_state", namespace={"ui_state": ui_state, "dpg": dpg})
        env["_capture_ui_state"]()
        self.assertEqual(ui_state["search"], "")

    def test_search_callback_empty_value_is_authoritative(self):
        ui_state = {"search": "old"}
        calls = []
        env = load_functions(
            CHECKBOXES,
            "search_changed",
            namespace={
                "ui_state": ui_state,
                "apply_filters": lambda *args, **kwargs: calls.append((args, kwargs, ui_state["search"])),
            },
        )
        env["search_changed"](app_data="")
        self.assertEqual(ui_state["search"], "")
        self.assertEqual(calls, [((), {"capture_search": False}, "")])

    def test_search_input_uses_dedicated_callback(self):
        source = CHECKBOXES.read_text(encoding="utf-8")
        block = source[source.index('tag="mod_search"') :][:500]
        self.assertIn("callback=search_changed", block)


class D2PFXSortTests(unittest.TestCase):
    def test_category_name_filename_sort_is_stable(self):
        metadata = {
            "b-z": ("Beta", "Zulu", "z.vpk"),
            "a-z": ("Alpha", "Zulu", "z.vpk"),
            "a-a2": ("Alpha", "alpha", "b.vpk"),
            "a-a1": ("Alpha", "Alpha", "a.vpk"),
        }
        env = load_functions(
            CHECKBOXES,
            "_d2pfx_sort_key",
            "_sort_d2pfx_mods",
            namespace={
                "_category": lambda mod: metadata[mod][0],
                "_display_name": lambda mod: metadata[mod][1],
                "mods_shared": types.SimpleNamespace(get_mod_filename=lambda mod: metadata[mod][2]),
            },
        )
        self.assertEqual(env["_sort_d2pfx_mods"](["b-z", "a-z", "a-a2", "a-a1"]), ["a-a1", "a-a2", "a-z", "b-z"])

    def test_blank_category_uses_other_fallback(self):
        metadata = {"none": ("", "Bravo", "b.vpk"), "alpha": ("Alpha", "Zulu", "z.vpk")}
        env = load_functions(
            CHECKBOXES,
            "_d2pfx_sort_key",
            "_sort_d2pfx_mods",
            namespace={
                "_category": lambda mod: metadata[mod][0],
                "_display_name": lambda mod: metadata[mod][1],
                "mods_shared": types.SimpleNamespace(get_mod_filename=lambda mod: metadata[mod][2]),
            },
        )
        self.assertEqual(env["_sort_d2pfx_mods"](["none", "alpha"]), ["alpha", "none"])


class D2PFXUpdatedDateTests(unittest.TestCase):
    def _formatter(self):
        return load_functions(D2PFX_UI, "_format_d2pfx_updated_date", namespace={"dt": dt})[
            "_format_d2pfx_updated_date"
        ]

    def test_missing_or_blank_date_renders_no_label(self):
        fmt = self._formatter()
        self.assertIsNone(fmt({"name": "No Date"}))
        self.assertIsNone(fmt({"meta": {}}))
        self.assertIsNone(fmt({"meta": {"date": ""}}))
        self.assertIsNone(fmt({"meta": {"date": 0}}))

    def test_unix_seconds_and_milliseconds_are_normalized(self):
        fmt = self._formatter()
        seconds = 1787875200
        self.assertEqual(fmt({"meta": {"date": seconds}}), "Updated Aug 28, 2026")
        self.assertEqual(fmt({"meta": {"date": seconds * 1000}}), "Updated Aug 28, 2026")

    def test_iso_and_short_source_dates_are_supported(self):
        fmt = self._formatter()
        self.assertEqual(fmt({"meta": {"date": "2026-08-28T12:30:00Z"}}), "Updated Aug 28, 2026")
        self.assertEqual(fmt({"meta": {"date": "Summer 2026"}}), "Updated Summer 2026")


class CollisionReportRegressionTests(unittest.TestCase):
    def test_collision_report_fingerprints_every_shared_path(self):
        source = MOD_LIBRARY.read_text(encoding="utf-8")
        self.assertIn("for virtual_path in paths:", source)
        self.assertNotIn("for virtual_path in paths[:max_examples]:", source)
        self.assertIn('"examples": paths[:max_examples]', source)

    def test_report_contains_required_per_path_fields(self):
        source = MOD_LIBRARY.read_text(encoding="utf-8")
        for marker in (
            '"virtual_path"',
            '"classification"',
            '"winner"',
            '"recommended_action"',
            '"crc32"',
            '"sha256"',
            '"size"',
        ):
            self.assertIn(marker, source)
        self.assertIn("def fingerprint_entry", source)
        self.assertIn("def write_collision_report", source)
        self.assertIn('COLLISION_REPORT_FILE = "compatibility-report.json"', source)

    def test_directory_backed_vpks_are_included_in_collision_index(self):
        source = MOD_LIBRARY.read_text(encoding="utf-8")
        self.assertIn("def _iter_embedded_vpks", source)
        self.assertIn("for vpk_path in _iter_embedded_vpks(root)", source)
        self.assertIn("indexer_version", source)

    def test_patch_preview_keeps_hash_winner_and_action_context(self):
        source = CHECKBOXES.read_text(encoding="utf-8")
        self.assertIn("Automatic compatibility actions", source)
        self.assertIn("CRC32=", source)
        self.assertIn("SHA256=", source)
        self.assertIn("Winner:", source)
        self.assertIn("Action:", source)
