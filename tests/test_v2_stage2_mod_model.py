from __future__ import annotations

import ast
import os
import tempfile
import types
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "V2_STAGING" / "Minify"
MODS_SHARED = STAGE / "core" / "mods_shared.py"


def _load_mod_functions(*names: str, root: Path):
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

    env = {
        "os": os,
        "base": types.SimpleNamespace(mods_dir=str(root)),
        "mod_paths": {},
        "mod_labels": {},
    }
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(MODS_SHARED), "exec"), env)
    return env


_DISCOVERY = (
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
    "get_mod_id_for_path",
    "resolve_mod_reference",
)


def test_v2_stage2_nested_collection_ids_are_stable_and_distinct():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for pack in ("Pack A", "Pack B"):
            collection = root / pack
            collection.mkdir()
            (collection / ".minify-collection").write_text("", encoding="utf-8")
            (collection / "Same Mod" / "files").mkdir(parents=True)

        env = _load_mod_functions(*_DISCOVERY, root=root)
        entries = env["_discover_directory_mod_entries"]()
        assert [item[0] for item in entries] == [
            "nested-mod::Pack A/Same Mod",
            "nested-mod::Pack B/Same Mod",
        ]

        env["mod_paths"].update(dict(entries))
        env["mod_labels"].update({mod_id: Path(path).name for mod_id, path in entries})
        assert env["get_mod_id_for_path"](root / "Pack A" / "Same Mod") == "nested-mod::Pack A/Same Mod"


def test_v2_stage2_sibling_dependency_reference_resolves_inside_collection():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        collection = root / "Pack"
        collection.mkdir()
        (collection / ".minify-collection").write_text("", encoding="utf-8")
        for name in ("Core", "Addon"):
            (collection / name / "files").mkdir(parents=True)

        env = _load_mod_functions(*_DISCOVERY, root=root)
        entries = env["_discover_directory_mod_entries"]()
        env["mod_paths"].update(dict(entries))
        env["mod_labels"].update({mod_id: Path(path).name for mod_id, path in entries})
        assert env["resolve_mod_reference"](
            "Core", relative_to="nested-mod::Pack/Addon"
        ) == "nested-mod::Pack/Core"


def test_v2_stage2_collection_symlinks_are_not_followed():
    with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside_tmp:
        root = Path(tmp)
        outside = Path(outside_tmp) / "Outside"
        (outside / "files").mkdir(parents=True)
        collection = root / "Pack"
        collection.mkdir()
        (collection / ".minify-collection").write_text("", encoding="utf-8")
        try:
            (collection / "Linked").symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError):
            return

        env = _load_mod_functions(*_DISCOVERY, root=root)
        assert env["_discover_directory_mod_entries"]() == [("Pack", str(collection))]


def test_v2_stage2_mod_metadata_reads_are_bounded_and_identity_checked():
    source = MODS_SHARED.read_text(encoding="utf-8")
    for token in (
        "D2PFX_METADATA_MAX_FILE_BYTES",
        "security.read_bounded_regular_file(path, max_bytes=D2PFX_METADATA_MAX_FILE_BYTES)",
        "data = config.read_json_file(path)",
        "sidecar = config.read_json_file(sidecar_path)",
    ):
        assert token in source
    assert 'with open(path, encoding="utf-8-sig", errors="replace")' not in source


def test_v2_stage2_mod_model_keeps_custom_vpk_categories_without_blanket_hard_conflicts():
    source = MODS_SHARED.read_text(encoding="utf-8")
    for token in (
        'VPK_COLLECTION_DIR = "_VPK Mods"',
        'NESTED_VPK_PREFIX = "nested-vpk::"',
        "relative_parent = os.path.dirname(relative_path)",
        '_groups[mod_id] = str(metadata.get("category") or relative_parent).strip()',
        'categories.discard("terrains")',
        "get_conflicting_categories()",
        '_conflicts.append({mod: [conflicts] if isinstance(conflicts, str) else list(conflicts)})',
    ):
        assert token in source

    scan_body = source[source.index("def scan_mods():") :]
    assert "category_mods" not in scan_body
    assert "active_conflicting_cats" not in scan_body
    assert "mods_in_category" not in scan_body


def test_v2_stage2_service_and_patch_callers_use_logical_mod_paths():
    service = (STAGE / "ui" / "services" / "mod_service.py").read_text(encoding="utf-8")
    patch = (STAGE / "patch" / "__init__.py").read_text(encoding="utf-8")
    config_service = (STAGE / "ui" / "services" / "config_service.py").read_text(encoding="utf-8")
    conditions = (STAGE / "conditions.py").read_text(encoding="utf-8")
    d2pfx = (STAGE / "plugins" / "d2pfx" / "build_hook.py").read_text(encoding="utf-8")
    d2pfx_api = (STAGE / "plugins" / "d2pfx" / "api.py").read_text(encoding="utf-8")

    assert "mod_path = mods_shared.get_mod_path(mod)" in service
    assert "mod_path = mods_shared.get_mod_path(mod_name)" in service
    for field in (
        '"group": group',
        '"category": mod_library.category(mod_name) or category',
        '"source": mod_library.source(mod_name) or source',
        '"type": mod_type',
        '"favorite": mod_library.is_favorite(mod_name)',
    ):
        assert field in service

    assert "dependency_id = mods_shared.resolve_mod_reference" in patch
    assert "conflicting_id = mods_shared.resolve_mod_reference" in patch
    assert "mod_path = mods_shared.get_mod_path(mod_name)" in patch
    assert "mod_path = mods_shared.get_mod_path(folder)" in patch

    assert "for mod_id in mods_shared.mods_alphabetical:" in config_service
    assert "mod_path = mods_shared.get_mod_path(mod_id)" in config_service
    assert "mod_path = mods_shared.get_mod_path(mod_name)" in config_service
    assert "mod_path = mods_shared.get_mod_path(folder)" in conditions
    assert "mod_path = mods_shared.get_mod_path(mod_name)" in d2pfx
    assert "for mod_id in mods_shared.mods_alphabetical:" in d2pfx_api
    assert "mod_path = mods_shared.get_mod_path(mod_id)" in d2pfx_api
    assert "security.confined_destination(base.mods_dir, relative)" in d2pfx_api
