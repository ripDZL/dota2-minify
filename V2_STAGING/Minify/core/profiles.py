"""Headless persistent mod profiles for the v2 service layer."""

from __future__ import annotations

import json
import os
import tempfile

from core import base

PROFILE_FILE_NAME = "mod-profiles.json"
PROFILE_EXPORT_FORMAT = "minify-mod-profiles"
PROFILE_EXPORT_VERSION = 1
PROFILE_MAX_FILE_BYTES = 8 * 1024 * 1024
PROFILE_MAX_COUNT = 256
PROFILE_MAX_STATES_PER_PROFILE = 5000
PROFILE_MAX_TOTAL_STATES = 20000
PROFILE_MAX_NAME_CHARS = 128
PROFILE_MAX_MOD_ID_CHARS = 512
PROFILE_MAX_HINT_CHARS = 512


def _path() -> str:
    return os.path.join(base.config_dir, PROFILE_FILE_NAME)


def _normalize_profiles_mapping(profiles) -> dict[str, dict[str, bool]]:
    if profiles in (None, {}):
        return {}
    if not isinstance(profiles, dict) or len(profiles) > PROFILE_MAX_COUNT:
        raise ValueError("Profile collection is invalid or excessive.")

    normalized = {}
    total_states = 0
    for name, value in profiles.items():
        if not isinstance(name, str) or not name.strip() or len(name) > PROFILE_MAX_NAME_CHARS:
            raise ValueError("Profile contains an invalid name.")

        states = value.get("mods") if isinstance(value, dict) and "mods" in value else value
        if not isinstance(states, dict) or len(states) > PROFILE_MAX_STATES_PER_PROFILE:
            raise ValueError("Profile contains an invalid or excessive mod state map.")

        clean_states = {}
        for mod, enabled in states.items():
            if not isinstance(mod, str) or not mod or len(mod) > PROFILE_MAX_MOD_ID_CHARS:
                raise ValueError("Profile contains an invalid mod identifier.")
            if type(enabled) is not bool:
                raise ValueError("Profile mod states must be JSON booleans.")
            clean_states[mod] = enabled

        total_states += len(clean_states)
        if total_states > PROFILE_MAX_TOTAL_STATES:
            raise ValueError("Profile bundle contains too many total mod states.")
        normalized[name.strip()] = clean_states
    return normalized


def _normalize_hints(hints, referenced: set[str]) -> dict:
    if hints in (None, {}):
        return {}
    if not isinstance(hints, dict) or len(hints) > PROFILE_MAX_TOTAL_STATES:
        raise ValueError("Profile mod hints are invalid or excessive.")

    normalized = {}
    for mod, hint in hints.items():
        if mod not in referenced:
            continue
        if not isinstance(mod, str) or len(mod) > PROFILE_MAX_MOD_ID_CHARS or not isinstance(hint, dict):
            raise ValueError("Profile contains an invalid mod hint.")
        clean = {}
        for key in ("display_name", "source", "stable_key"):
            value = hint.get(key, "")
            if value is None:
                value = ""
            if not isinstance(value, str) or len(value) > PROFILE_MAX_HINT_CHARS:
                raise ValueError("Profile contains an invalid mod hint value.")
            clean[key] = value
        normalized[mod] = clean
    return normalized


def load_profiles() -> dict[str, dict[str, bool]]:
    path = _path()
    try:
        if os.path.islink(path) or not os.path.isfile(path):
            return {}
        if os.path.getsize(path) > PROFILE_MAX_FILE_BYTES:
            return {}
        with open(path, encoding="utf-8-sig") as file:
            data = json.load(file)
        profiles = data.get("profiles", data) if isinstance(data, dict) else {}
        return _normalize_profiles_mapping(profiles)
    except Exception:
        return {}


def _write_profiles(profiles: dict[str, dict[str, bool]]) -> None:
    normalized = _normalize_profiles_mapping(profiles)
    os.makedirs(base.config_dir, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".minify-profiles-", suffix=".json", dir=base.config_dir)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as file:
            json.dump(
                {
                    "version": 2,
                    "profiles": {
                        name: {"mods": states}
                        for name, states in sorted(normalized.items(), key=lambda item: item[0].casefold())
                    },
                },
                file,
                indent=2,
                ensure_ascii=False,
            )
        os.replace(temporary, _path())
    except Exception:
        try:
            os.remove(temporary)
        except FileNotFoundError:
            pass
        raise


def list_profiles() -> list[dict]:
    return [
        {"name": name, "state_count": len(states)}
        for name, states in sorted(load_profiles().items(), key=lambda item: item[0].casefold())
    ]


def get_profile(name: str) -> dict[str, bool] | None:
    states = load_profiles().get(str(name or "").strip())
    return dict(states) if isinstance(states, dict) else None


def save_profile(name: str, states: dict[str, bool]) -> dict[str, bool]:
    clean_name = str(name or "").strip()
    normalized = _normalize_profiles_mapping({clean_name: states})
    profiles = load_profiles()
    profiles[clean_name] = normalized[clean_name]
    _write_profiles(profiles)
    return dict(profiles[clean_name])


def delete_profile(name: str) -> bool:
    clean_name = str(name or "").strip()
    profiles = load_profiles()
    if clean_name not in profiles:
        return False
    del profiles[clean_name]
    _write_profiles(profiles)
    return True


def duplicate_profile(name: str) -> str | None:
    clean_name = str(name or "").strip()
    profiles = load_profiles()
    states = profiles.get(clean_name)
    if states is None:
        return None

    base_name = f"{clean_name} Copy"
    new_name = base_name
    counter = 2
    while new_name in profiles:
        new_name = f"{base_name} {counter}"
        counter += 1
    profiles[new_name] = dict(states)
    _write_profiles(profiles)
    return new_name


def normalize_import_bundle(data) -> tuple[dict[str, dict[str, bool]], dict]:
    if not isinstance(data, dict):
        return {}, {}
    try:
        if "format" in data and (
            data.get("format") != PROFILE_EXPORT_FORMAT or data.get("version") != PROFILE_EXPORT_VERSION
        ):
            raise ValueError("Unsupported profile bundle format.")
        normalized = _normalize_profiles_mapping(data.get("profiles", data))
        referenced = {mod for states in normalized.values() for mod in states}
        hints = _normalize_hints(data.get("mod_hints", {}), referenced)
        return normalized, hints
    except ValueError:
        return {}, {}


def complete_snapshot(states: dict[str, bool], available_mods: list[str]) -> dict[str, bool]:
    """Profiles are complete snapshots: omitted available mods become disabled."""
    clean = _normalize_profiles_mapping({"snapshot": states})["snapshot"]
    return {mod: bool(clean.get(mod, False)) for mod in available_mods}
