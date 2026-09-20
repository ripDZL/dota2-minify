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
            simple: {RIVER_WATER, RIVERBED, GROUND, DEFERRED},
            river: {RIVER_WATER, RIVERBED, DEFERRED},
        }
    )

    rule = compat.active_simple_dark_river_rule([simple, river])
    assert rule is not None
    assert rule["simple"] == simple
    assert rule["competitors"] == [river]
    assert set(rule["exclude_from_simple"]) == {RIVER_WATER, RIVERBED, DEFERRED}
    assert GROUND not in compat.exclusions_for_mod(simple, [simple, river])


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
