from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "V2_STAGING" / "Minify"
PROFILES = STAGE / "core" / "profiles.py"


def _profile_env():
    source = PROFILES.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(PROFILES))
    constants = {
        "PROFILE_EXPORT_FORMAT",
        "PROFILE_EXPORT_VERSION",
        "PROFILE_MAX_FILE_BYTES",
        "PROFILE_MAX_COUNT",
        "PROFILE_MAX_STATES_PER_PROFILE",
        "PROFILE_MAX_TOTAL_STATES",
        "PROFILE_MAX_NAME_CHARS",
        "PROFILE_MAX_MOD_ID_CHARS",
        "PROFILE_MAX_HINT_CHARS",
    }
    functions = {
        "_normalize_profiles_mapping",
        "_normalize_hints",
        "normalize_import_bundle",
        "complete_snapshot",
    }
    nodes = []
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id in constants for target in node.targets
        ):
            nodes.append(node)
        elif isinstance(node, ast.FunctionDef) and node.name in functions:
            nodes.append(node)
    env = {}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(PROFILES), "exec"), env)
    return env


def test_v2_profiles_require_strict_json_booleans():
    env = _profile_env()
    profiles, hints = env["normalize_import_bundle"](
        {"profiles": {"Unsafe": {"mods": {"mod-a": "false"}}}}
    )
    assert profiles == {}
    assert hints == {}


def test_v2_profiles_accept_legacy_shape_and_are_complete_snapshots():
    env = _profile_env()
    profiles, hints = env["normalize_import_bundle"](
        {"Legacy": {"mods": {"mod-a": True, "mod-b": False}}}
    )
    assert profiles == {"Legacy": {"mod-a": True, "mod-b": False}}
    assert hints == {}
    assert env["complete_snapshot"](
        profiles["Legacy"], ["mod-a", "mod-b", "mod-c"]
    ) == {"mod-a": True, "mod-b": False, "mod-c": False}


def test_v2_profiles_reject_wrong_export_version():
    env = _profile_env()
    profiles, _ = env["normalize_import_bundle"](
        {
            "format": env["PROFILE_EXPORT_FORMAT"],
            "version": env["PROFILE_EXPORT_VERSION"] + 1,
            "profiles": {"P": {"mods": {"m": True}}},
        }
    )
    assert profiles == {}


def test_v2_profile_hints_only_keep_referenced_mods():
    env = _profile_env()
    payload = {
        "format": env["PROFILE_EXPORT_FORMAT"],
        "version": env["PROFILE_EXPORT_VERSION"],
        "profiles": {"P": {"mods": {"a": True}}},
        "mod_hints": {
            "a": {"display_name": "A", "source": "Local", "stable_key": "mod:a"},
            "unused": {"display_name": "Unused", "source": "", "stable_key": ""},
        },
    }
    profiles, hints = env["normalize_import_bundle"](payload)
    assert profiles == {"P": {"a": True}}
    assert hints == {"a": {"display_name": "A", "source": "Local", "stable_key": "mod:a"}}


def test_v2_mod_library_favorites_use_stable_keys_and_atomic_storage():
    source = (STAGE / "core" / "mod_library.py").read_text(encoding="utf-8")
    for token in (
        'LIBRARY_DB_FILE = "mod-library.json"',
        "mods_shared.get_mod_fingerprint(mod)",
        'keys.append(f"sha256:{fingerprint}")',
        'return [f"mod:{str(mod).casefold()}"]',
        "tempfile.mkstemp",
        "os.replace(temporary, _db_path())",
        "def set_favorite(",
        "def metadata(",
    ):
        assert token in source


def test_v2_mod_service_exposes_favorites_and_profiles_without_ui_state_dependency():
    service = (STAGE / "ui" / "services" / "mod_service.py").read_text(encoding="utf-8")
    app = (STAGE / "ui" / "app.py").read_text(encoding="utf-8")
    global_types = (STAGE / "ui" / "web" / "src" / "global.d.ts").read_text(encoding="utf-8")

    for token in (
        "mod_library.is_favorite(mod_name)",
        "def set_favorite(",
        "def get_profiles(",
        "def save_profile(",
        "def apply_profile(",
        "profiles.complete_snapshot(states, available)",
        "mods_shared.get_mod_path(mod)",
    ):
        assert token in service

    for token in (
        "def set_mod_favorite(",
        "def get_profiles(",
        "def save_profile(",
        "def apply_profile(",
        "def duplicate_profile(",
        "def delete_profile(",
    ):
        assert token in app

    assert "set_mod_favorite?:" in global_types
    assert "get_profiles?:" in global_types
    assert "apply_profile?:" in global_types


def test_v2_mod_service_recognizes_string_schema_d2pfx_installs():
    library = (STAGE / "core" / "mod_library.py").read_text(encoding="utf-8")
    service = (STAGE / "ui" / "services" / "mod_service.py").read_text(encoding="utf-8")

    assert "def is_d2pfx(mod: str) -> bool:" in library
    assert "return bool(_d2pfx_metadata(_manifest_metadata(mod)))" in library
    assert 'if browser == "d2pfx":' in library
    assert "if mod_library.is_d2pfx(mod_name):" in service


def test_v2_hero_default_selector_uses_real_resource_overlap_with_enabled_d2pfx():
    service = (STAGE / "ui" / "services" / "mod_service.py").read_text(encoding="utf-8")
    app = (STAGE / "ui" / "app.py").read_text(encoding="utf-8")

    for token in (
        "def apply_hero_defaults_without_d2pfx(self)",
        'casefold() == "hero mods"',
        "mod_library.is_d2pfx(mod)",
        "bool(mods_shared.get_state(mod))",
        "set(mod_library.index_contents(mod))",
        "not hero_entries.isdisjoint(entries)",
        "desired[hero_mod] = not blockers",
        "self.set_mods(desired)",
    ):
        assert token in service

    assert "def apply_hero_defaults_without_d2pfx(self)" in app
    assert "return self.mod_service.apply_hero_defaults_without_d2pfx()" in app
