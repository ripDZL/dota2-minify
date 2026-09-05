import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../Minify")))

from ui import checkboxes


def test_profile_import_requires_strict_json_booleans():
    profiles, hints = checkboxes._normalized_import_profiles({"profiles": {"Unsafe": {"mods": {"mod-a": "false"}}}})
    assert profiles == {}
    assert hints == {}


def test_profile_import_accepts_boolean_states_and_legacy_shape():
    profiles, hints = checkboxes._normalized_import_profiles({"Legacy": {"mods": {"mod-a": True, "mod-b": False}}})
    assert profiles == {"Legacy": {"mod-a": True, "mod-b": False}}
    assert hints == {}


def test_profile_export_format_version_must_match():
    profiles, _ = checkboxes._normalized_import_profiles(
        {
            "format": checkboxes.PROFILE_EXPORT_FORMAT,
            "version": checkboxes.PROFILE_EXPORT_VERSION + 1,
            "profiles": {"P": {"mods": {"m": True}}},
        }
    )
    assert profiles == {}


def test_profile_bundle_rejects_excessive_profile_count(monkeypatch):
    monkeypatch.setattr(checkboxes, "PROFILE_MAX_COUNT", 2)
    payload = {"profiles": {f"P{i}": {"mods": {}} for i in range(3)}}
    profiles, _ = checkboxes._normalized_import_profiles(payload)
    assert profiles == {}


def test_profile_bundle_rejects_excessive_state_count(monkeypatch):
    monkeypatch.setattr(checkboxes, "PROFILE_MAX_STATES_PER_PROFILE", 2)
    payload = {"profiles": {"P": {"mods": {"a": True, "b": False, "c": True}}}}
    profiles, _ = checkboxes._normalized_import_profiles(payload)
    assert profiles == {}


def test_profile_bundle_rejects_oversized_mod_identifier(monkeypatch):
    monkeypatch.setattr(checkboxes, "PROFILE_MAX_MOD_ID_CHARS", 3)
    payload = {"profiles": {"P": {"mods": {"abcd": True}}}}
    profiles, _ = checkboxes._normalized_import_profiles(payload)
    assert profiles == {}


def test_load_profiles_rejects_oversized_file(monkeypatch, tmp_path):
    monkeypatch.setattr(checkboxes.base, "config_dir", str(tmp_path))
    monkeypatch.setattr(checkboxes, "PROFILE_MAX_FILE_BYTES", 32)
    path = tmp_path / checkboxes.PROFILE_FILE_NAME
    path.write_text(json.dumps({"profiles": {"P": {"mods": {"a": True}}}}) + " " * 64)

    assert checkboxes._load_profiles() == {}


def test_profile_hints_are_bounded_and_only_keep_referenced_mods():
    payload = {
        "format": checkboxes.PROFILE_EXPORT_FORMAT,
        "version": checkboxes.PROFILE_EXPORT_VERSION,
        "profiles": {"P": {"mods": {"a": True}}},
        "mod_hints": {
            "a": {"display_name": "A", "source": "Local", "stable_key": "mod:a"},
            "unused": {"display_name": "Unused", "source": "", "stable_key": ""},
        },
    }
    profiles, hints = checkboxes._normalized_import_profiles(payload)
    assert profiles == {"P": {"a": True}}
    assert hints == {"a": {"display_name": "A", "source": "Local", "stable_key": "mod:a"}}
