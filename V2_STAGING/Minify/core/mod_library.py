"""Headless v2 mod-library metadata and favorites.

This is the Stage 2 subset. Collision/content indexing is added at the patch
transaction stage; favorites and user metadata remain independent of the UI.
"""

from __future__ import annotations

import json
import os
import tempfile

from core import base, mods_shared

LIBRARY_DB_FILE = "mod-library.json"
SCHEMA_VERSION = 1


def _db_path() -> str:
    return os.path.join(base.config_dir, LIBRARY_DB_FILE)


def _load() -> dict:
    try:
        with open(_db_path(), encoding="utf-8-sig") as file:
            data = json.load(file)
    except Exception:
        data = {}
    if not isinstance(data, dict):
        data = {}
    favorites = data.get("favorites")
    overrides = data.get("overrides")
    return {
        "schema_version": SCHEMA_VERSION,
        "favorites": favorites if isinstance(favorites, dict) else {},
        "overrides": overrides if isinstance(overrides, dict) else {},
    }


def _save(data: dict) -> None:
    os.makedirs(base.config_dir, exist_ok=True)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "favorites": data.get("favorites", {}),
        "overrides": data.get("overrides", {}),
    }
    fd, temporary = tempfile.mkstemp(prefix=".minify-library-", suffix=".json", dir=base.config_dir)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as file:
            json.dump(payload, file, indent=2, ensure_ascii=False, sort_keys=True)
        os.replace(temporary, _db_path())
    except Exception:
        try:
            os.remove(temporary)
        except FileNotFoundError:
            pass
        raise


def _stable_keys(mod: str, *, calculate_hash: bool = False) -> list[str]:
    if not str(mod).casefold().endswith(".vpk"):
        return [f"mod:{str(mod).casefold()}"]

    keys = []
    metadata = mods_shared.get_mod_metadata(mod)
    fingerprint = str(metadata.get("fingerprint") or "").strip().casefold()
    if not fingerprint and calculate_hash:
        fingerprint = str(mods_shared.get_mod_fingerprint(mod) or "").strip().casefold()
    if fingerprint:
        keys.append(f"sha256:{fingerprint}")

    path = os.path.normcase(os.path.abspath(mods_shared.get_mod_path(mod)))
    keys.append(f"path:{path}")
    return keys


def stable_key(mod: str, *, calculate_hash: bool = False) -> str:
    return _stable_keys(mod, calculate_hash=calculate_hash)[0]


def is_favorite(mod: str) -> bool:
    data = _load()
    return any(bool(data["favorites"].get(key, False)) for key in _stable_keys(mod))


def set_favorite(mod: str, value: bool) -> bool:
    data = _load()
    if value:
        key = stable_key(mod, calculate_hash=True)
        data["favorites"][key] = True
        if key.startswith("sha256:"):
            for old_key in _stable_keys(mod):
                if old_key.startswith("path:"):
                    data["favorites"].pop(old_key, None)
    else:
        for key in _stable_keys(mod, calculate_hash=True):
            data["favorites"].pop(key, None)
    _save(data)
    return bool(value)


def get_override(mod: str) -> dict:
    data = _load()
    for key in _stable_keys(mod):
        value = data["overrides"].get(key)
        if isinstance(value, dict) and value:
            return dict(value)
    return {}


def set_override(mod: str, *, display_name: str = "", category: str = "", source: str = "") -> None:
    data = _load()
    key = stable_key(mod, calculate_hash=str(mod).casefold().endswith(".vpk"))
    value = {}
    for field, raw in (("display_name", display_name), ("category", category), ("source", source)):
        clean = str(raw or "").strip()
        if clean:
            value[field] = clean

    if value:
        data["overrides"][key] = value
    else:
        for old_key in _stable_keys(mod):
            data["overrides"].pop(old_key, None)
    _save(data)


def _manifest_metadata(mod: str) -> dict:
    if str(mod).casefold().endswith(".vpk"):
        return {}
    try:
        from patch import manifest_utils

        cfg = manifest_utils.get_mod(mods_shared.get_mod_path(mod))
    except Exception:
        return {}
    return cfg if isinstance(cfg, dict) else {}


def _d2pfx_metadata(cfg: dict) -> dict:
    browser = cfg.get("browser")
    if browser == "d2pfx":
        return {
            "name": cfg.get("name"),
            "category": cfg.get("category"),
            "label": cfg.get("label"),
        }
    if isinstance(browser, dict) and (
        browser.get("browser") == "d2pfx" or str(browser.get("name") or "").casefold().startswith("d2pfx")
    ):
        return {
            "name": browser.get("name"),
            "category": browser.get("category"),
            "label": browser.get("label"),
        }
    return {}


def display_name(mod: str) -> str:
    override = str(get_override(mod).get("display_name") or "").strip()
    if override:
        return override

    cfg = _manifest_metadata(mod)
    d2pfx = _d2pfx_metadata(cfg)
    if d2pfx:
        name = str(d2pfx.get("name") or mods_shared.get_mod_label(mod)).strip()
        label = str(d2pfx.get("label") or "").strip()
        return f"{name} ({label})" if label else name
    manifest_name = str(cfg.get("name") or "").strip()
    if manifest_name:
        return manifest_name
    return str(mods_shared.get_mod_label(mod) or mod)


def category(mod: str) -> str:
    override = str(get_override(mod).get("category") or "").strip()
    if override:
        return override

    cfg = _manifest_metadata(mod)
    d2pfx = _d2pfx_metadata(cfg)
    manifest_category = str(d2pfx.get("category") or cfg.get("category") or "").strip()
    if manifest_category:
        return manifest_category

    group = str(mods_shared.get_mod_group(mod) or "").strip()
    if group:
        return group
    return "VPK" if str(mod).casefold().endswith(".vpk") else "Standard"


def source(mod: str) -> str:
    override = str(get_override(mod).get("source") or "").strip()
    if override:
        return override

    if _d2pfx_metadata(_manifest_metadata(mod)):
        return "D2PFX"
    shared = str(mods_shared.get_mod_source(mod) or "").strip()
    if shared:
        return shared
    return "Local VPK" if str(mod).casefold().endswith(".vpk") else "Minify"


def metadata(mod: str) -> dict:
    group = str(mods_shared.get_mod_group(mod) or "").strip()
    return {
        "display_name": display_name(mod),
        "category": category(mod),
        "source": source(mod),
        "favorite": is_favorite(mod),
        "group": group,
        "nested": bool(mods_shared.get_mod_metadata(mod).get("nested") or group),
    }
