from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOD_COMPAT = ROOT / "V2_STAGING" / "Minify" / "core" / "mod_compat.py"

RIVER_WATER = "materials/water/water_generic_000.vmat_c"
RIVERBED = "materials/blends/mod_radiant_riverbed_path_000.vmat_c"
GROUND = "materials/blends/mod_radiant_000.vmat_c"
DEFERRED = "materials/dev/deferred_post_process.vmat_c"
DEFERRED_FOG = "materials/dev/deferred_post_process_vmat_g_tfog_9ea98ee9.vtex_c"


def load_compat(entries):
    fake_shared = types.SimpleNamespace(
        get_mod_label=lambda mod: mod,
        get_mod_filename=lambda mod: os.path.basename(str(mod)),
        get_mod_metadata=lambda mod: {},
        get_mod_path=lambda mod: str(mod),
    )

    fake_library = types.SimpleNamespace(
        index_contents=lambda mod: list(entries.get(mod, set())),
        fingerprint_entry=lambda mod, virtual_path: (
            {"sha256": f"{mod}-{virtual_path}", "size": 1, "origin": "test"}
            if virtual_path in entries.get(mod, set())
            else {}
        ),
    )
    fake_core = types.ModuleType("core")
    fake_core.mods_shared = fake_shared
    fake_core.mod_library = fake_library

    previous_core = sys.modules.get("core")
    previous_library = sys.modules.get("core.mod_library")
    try:
        sys.modules["core"] = fake_core
        sys.modules["core.mod_library"] = fake_library
        spec = importlib.util.spec_from_file_location("test_v2_simple_dark_river_compat", MOD_COMPAT)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)
        module._indexed_entries = lambda mod: {
            module.normalize_virtual_path(path) for path in entries.get(mod, set())
        }
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


def test_simple_dark_terrain_yields_only_real_overlapping_river_resources():
    simple = "Simple Dark Terrain"
    river = "Clean River Mod"
    compat = load_compat(
        {
            simple: {RIVER_WATER, RIVERBED, GROUND, DEFERRED, DEFERRED_FOG},
            river: {RIVER_WATER, RIVERBED, DEFERRED, DEFERRED_FOG},
        }
    )

    rule = compat.active_simple_dark_river_rule([simple, river])
    assert rule is not None
    assert rule["simple"] == simple
    assert rule["competitors"] == [river]
    assert set(rule["exclude_from_simple"]) == {RIVER_WATER, RIVERBED}
    assert set(rule["exclude_from_competitors"][river]) == {DEFERRED, DEFERRED_FOG}
    assert GROUND not in compat.exclusions_for_mod(simple, [simple, river])
    assert DEFERRED not in compat.exclusions_for_mod(simple, [simple, river])
    assert compat.exclusions_for_mod(river, [simple, river]) == {DEFERRED, DEFERRED_FOG}


def test_non_overlapping_river_mod_does_not_change_simple_dark_terrain():
    simple = "Simple Dark Terrain"
    river = "River Mod"
    compat = load_compat({simple: {GROUND}, river: {RIVER_WATER}})

    assert compat.active_simple_dark_river_rule([simple, river]) is None
    assert compat.exclusions_for_mod(simple, [simple, river]) == set()


def test_copy_filters_river_overlaps_but_keeps_rest_of_simple_dark_terrain():
    simple = "Simple Dark Terrain"
    river = "River Mod"
    compat = load_compat({simple: {RIVER_WATER, GROUND}, river: {RIVER_WATER}})

    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "src"
        dst = Path(tmp) / "dst"
        (src / Path(RIVER_WATER).parent).mkdir(parents=True)
        (src / Path(GROUND).parent).mkdir(parents=True, exist_ok=True)
        (src / RIVER_WATER).write_bytes(b"simple-water")
        (src / GROUND).write_bytes(b"simple-ground")

        excluded = compat.copy_standard_files(simple, str(src), str(dst), [simple, river])

        assert set(excluded) == {RIVER_WATER}
        assert not (dst / RIVER_WATER).exists()
        assert (dst / GROUND).read_bytes() == b"simple-ground"


def test_river_collision_is_reported_as_automatic_compatibility_fix():
    simple = "Simple Dark Terrain"
    river = "River Mod"
    compat = load_compat({simple: {RIVERBED}, river: {RIVERBED}})

    result = compat.classify_collision(
        RIVERBED,
        [simple, river],
        {simple: {"sha256": "a"}, river: {"sha256": "b"}},
    )

    assert result["auto_fix"] is True
    assert result["winner"] == river
    assert result["rule_id"] == "simple-dark-terrain-river-compat"


def test_river_mod_keeps_water_but_yields_shared_deferred_family():
    simple = "Simple Dark Terrain"
    river = "River Mod"
    compat = load_compat(
        {
            simple: {RIVER_WATER, DEFERRED, DEFERRED_FOG},
            river: {RIVER_WATER, DEFERRED, DEFERRED_FOG},
        }
    )

    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "river"
        dst = Path(tmp) / "dst"
        for virtual_path, payload in (
            (RIVER_WATER, b"river-water"),
            (DEFERRED, b"river-deferred"),
            (DEFERRED_FOG, b"river-fog"),
        ):
            target = src / virtual_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)

        excluded = compat.copy_standard_files(river, str(src), str(dst), [simple, river])

        assert set(excluded) == {DEFERRED, DEFERRED_FOG}
        assert (dst / RIVER_WATER).read_bytes() == b"river-water"
        assert not (dst / DEFERRED).exists()
        assert not (dst / DEFERRED_FOG).exists()


def test_showcase_regression_protects_simple_dark_deferred_resources():
    simple = "Simple Dark Terrain"
    river = "River Mod"
    compat = load_compat(
        {
            simple: {RIVERBED, DEFERRED, DEFERRED_FOG},
            river: {RIVERBED, DEFERRED, DEFERRED_FOG},
        }
    )

    rule = compat.active_simple_dark_river_rule([simple, river])
    assert rule is not None
    assert DEFERRED not in rule["exclude_from_simple"]
    assert DEFERRED_FOG not in rule["exclude_from_simple"]
    assert set(rule["exclude_from_competitors"][river]) == {DEFERRED, DEFERRED_FOG}
    assert "Showcase View render artifacts" in compat.exclusion_reason(river, DEFERRED, [simple, river])
