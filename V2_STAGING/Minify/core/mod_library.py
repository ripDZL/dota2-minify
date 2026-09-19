"""Headless v2 mod-library metadata and favorites.

This is the Stage 2 subset. Collision/content indexing is added at the patch
transaction stage; favorites and user metadata remain independent of the UI.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import re
import tempfile
import zlib
from collections import defaultdict

from core import base, mods_shared

LIBRARY_DB_FILE = "mod-library.json"
CONTENT_INDEX_FILE = "mod-content-index.json"
COLLISION_REPORT_FILE = "compatibility-report.json"
SCHEMA_VERSION = 3

CRITICAL_EXTENSIONS = {
    ".vmdl_c",
    ".vmat_c",
    ".vtex_c",
    ".vpcf_c",
    ".vsnd_c",
    ".vxml_c",
    ".vcss_c",
}


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

def _utc_now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def _content_index_path() -> str:
    return os.path.join(base.config_dir, CONTENT_INDEX_FILE)


def _load_content_index() -> dict:
    try:
        with open(_content_index_path(), encoding="utf-8-sig") as file:
            data = json.load(file)
    except Exception:
        data = {}
    if not isinstance(data, dict):
        data = {}
    records = data.get("records")
    if not isinstance(records, dict):
        records = {}
    return {"schema_version": SCHEMA_VERSION, "records": records}


def _save_content_index(data: dict) -> None:
    os.makedirs(base.config_dir, exist_ok=True)
    data["schema_version"] = SCHEMA_VERSION
    fd, temporary = tempfile.mkstemp(prefix=".minify-content-index-", suffix=".json", dir=base.config_dir)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as file:
            json.dump(data, file, indent=2, ensure_ascii=False, sort_keys=True)
        os.replace(temporary, _content_index_path())
    except Exception:
        try:
            os.remove(temporary)
        except FileNotFoundError:
            pass
        raise


def _record_key_for_path(path: str) -> str:
    return os.path.normcase(os.path.abspath(path))


def _stat_signature(path: str) -> tuple[int, int]:
    info = os.stat(path)
    return int(info.st_size), int(getattr(info, "st_mtime_ns", int(info.st_mtime * 1_000_000_000)))


def _record_for_mod(mod: str, create: bool = True) -> tuple[dict, dict, str]:
    data = _load_content_index()
    path = mods_shared.get_mod_path(mod)
    key = _record_key_for_path(path)
    record = data["records"].get(key)
    if not isinstance(record, dict):
        record = {}
        if create:
            data["records"][key] = record
    return data, record, key


def _iter_embedded_vpks(root: str):
    for current_root, dirs, files in os.walk(root):
        dirs[:] = [name for name in dirs if not os.path.islink(os.path.join(current_root, name))]
        for name in files:
            if name.casefold().endswith(".vpk"):
                yield os.path.join(current_root, name)


def _standard_entries(mod: str) -> list[str]:
    import vpk

    root = mods_shared.get_mod_path(mod)
    results = set()
    folder = os.path.join(root, "files")
    if os.path.isdir(folder):
        for current_root, dirs, files in os.walk(folder):
            dirs[:] = [name for name in dirs if not os.path.islink(os.path.join(current_root, name))]
            for name in files:
                full = os.path.join(current_root, name)
                if os.path.islink(full) or not os.path.isfile(full):
                    continue
                rel = os.path.relpath(full, folder).replace(os.sep, "/").casefold()
                if rel:
                    results.add(rel)

    for vpk_path in _iter_embedded_vpks(root):
        try:
            archive = vpk.open(vpk_path)
            results.update(str(entry).replace("\\", "/").casefold() for entry in archive)
        except Exception:
            continue
    return sorted(results)


def _vpk_entries(mod: str) -> list[str]:
    import vpk

    path = mods_shared.get_mod_path(mod)
    archive = vpk.open(path)
    return sorted({str(entry).replace("\\", "/").casefold() for entry in archive})


def _hash_stream(stream) -> tuple[int, str, int]:
    checksum = 0
    digest = hashlib.sha256()
    size = 0
    while True:
        chunk = stream.read(1024 * 1024)
        if not chunk:
            break
        size += len(chunk)
        checksum = zlib.crc32(chunk, checksum)
        digest.update(chunk)
    return checksum & 0xFFFFFFFF, digest.hexdigest(), size


def _fingerprint_vpk_entry(vpk_path: str, virtual_path: str) -> dict | None:
    import vpk

    archive = vpk.open(vpk_path)
    wanted = virtual_path.casefold()
    actual = next((str(entry) for entry in archive if str(entry).replace("\\", "/").casefold() == wanted), None)
    if actual is None:
        return None
    with archive.get_file(actual) as pak_file:
        crc_hint = getattr(pak_file, "crc32", None)
        size_hint = getattr(pak_file, "length", None)
        crc, sha256, measured_size = _hash_stream(pak_file)
    return {
        "crc32": f"{int(crc_hint if crc_hint is not None else crc) & 0xFFFFFFFF:08x}",
        "sha256": sha256,
        "size": int(size_hint if size_hint is not None else measured_size),
        "origin": os.path.basename(vpk_path),
    }


def fingerprint_entry(mod: str, virtual_path: str) -> dict:
    normalized = str(virtual_path or "").replace("\\", "/").lstrip("/").casefold()
    root = mods_shared.get_mod_path(mod)
    try:
        if os.path.isfile(root) and root.casefold().endswith(".vpk"):
            return _fingerprint_vpk_entry(root, normalized) or {}

        direct = os.path.join(root, "files", *normalized.split("/"))
        if os.path.isfile(direct) and not os.path.islink(direct):
            with open(direct, "rb") as stream:
                crc, sha256, size = _hash_stream(stream)
            return {"crc32": f"{crc:08x}", "sha256": sha256, "size": size, "origin": "files"}

        if os.path.isdir(root):
            for vpk_path in _iter_embedded_vpks(root):
                result = _fingerprint_vpk_entry(vpk_path, normalized)
                if result:
                    return result
    except Exception as error:
        return {"error": str(error)}
    return {}


def index_contents(mod: str, force: bool = False) -> list[str]:
    data, record, key = _record_for_mod(mod)
    path = mods_shared.get_mod_path(mod)
    if not os.path.exists(path):
        return []

    if not force and os.path.isfile(path) and record.get("indexer_version") == 2 and isinstance(record.get("entries"), list):
        try:
            size, mtime_ns = _stat_signature(path)
        except OSError:
            size = mtime_ns = None
        if record.get("size") == size and record.get("mtime_ns") == mtime_ns:
            return list(record["entries"])

    try:
        entries = _vpk_entries(mod) if os.path.isfile(path) and path.casefold().endswith(".vpk") else _standard_entries(mod)
        record.pop("index_error", None)
    except Exception as error:
        record["index_error"] = str(error)
        entries = []

    if os.path.isfile(path):
        try:
            size, mtime_ns = _stat_signature(path)
            record.update({"size": size, "mtime_ns": mtime_ns})
        except OSError:
            pass
    record.update(
        {
            "path": os.path.abspath(path),
            "mod_id": mod,
            "entries": entries,
            "entry_count": len(entries),
            "indexer_version": 2,
            "entries_indexed_at": _utc_now_iso(),
        }
    )
    data["records"][key] = record
    _save_content_index(data)
    return entries


def estimate_entry_count(mods) -> int:
    total = 0
    for mod in mods:
        _, record, _ = _record_for_mod(mod)
        count = record.get("entry_count")
        total += count if isinstance(count, int) else len(index_contents(mod))
    return total


def _base_display_name(mod: str) -> str:
    return re.sub(r"\s*\[\d+/\d+\]\s*$", "", display_name(mod)).strip().casefold()


def _conflict_severity(a: str, b: str, paths: list[str]) -> str:
    if _base_display_name(a) == _base_display_name(b):
        return "expected"
    if any(os.path.splitext(path)[1].casefold() in CRITICAL_EXTENSIONS for path in paths):
        return "critical"
    return "possible"


def analyze_conflicts(mods, max_examples: int = 8) -> list[dict]:
    from core import mod_compat

    mods = [mod for mod in mods if os.path.exists(mods_shared.get_mod_path(mod))]
    entry_owners = defaultdict(list)
    for mod in mods:
        for entry in index_contents(mod):
            if os.path.basename(entry).startswith("minify_"):
                continue
            entry_owners[entry].append(mod)

    pair_paths = defaultdict(list)
    for entry, owners in entry_owners.items():
        unique = list(dict.fromkeys(owners))
        for i in range(len(unique)):
            for j in range(i + 1, len(unique)):
                pair = tuple(sorted((unique[i], unique[j]), key=str.casefold))
                pair_paths[pair].append(entry)

    conflicts = []
    for (a, b), paths in pair_paths.items():
        details = []
        for virtual_path in paths:
            fingerprints = {a: fingerprint_entry(a, virtual_path), b: fingerprint_entry(b, virtual_path)}
            details.append(
                {
                    "path": virtual_path,
                    "owners": fingerprints,
                    **mod_compat.classify_collision(virtual_path, (a, b), fingerprints),
                }
            )
        severity = _conflict_severity(a, b, paths)
        if any(item.get("classification") == "true conflict" for item in details):
            severity = "critical"
        group_classification = next(
            (
                name
                for name in ("true conflict", "unknown", "intentional override")
                if any(item.get("classification") == name for item in details)
            ),
            "unknown",
        )
        conflicts.append(
            {
                "a": a,
                "b": b,
                "a_name": display_name(a),
                "b_name": display_name(b),
                "severity": severity,
                "classification": group_classification,
                "auto_fix": any(item.get("auto_fix") for item in details),
                "count": len(paths),
                "examples": paths[:max_examples],
                "details": details,
            }
        )

    severity_order = {"critical": 0, "possible": 1, "expected": 2}
    conflicts.sort(
        key=lambda item: (
            severity_order.get(item["severity"], 9),
            -item["count"],
            item["a_name"].casefold(),
            item["b_name"].casefold(),
        )
    )
    return conflicts


def conflict_counts(conflicts: list[dict]) -> dict:
    result = {"critical": 0, "possible": 0, "expected": 0, "pairs": len(conflicts)}
    for item in conflicts:
        severity = item.get("severity", "possible")
        result[severity] = result.get(severity, 0) + 1
    return result


def build_collision_report(mods, conflicts=None) -> dict:
    from core import mod_compat

    selected = list(dict.fromkeys(mods or []))
    conflicts = analyze_conflicts(selected) if conflicts is None else conflicts
    rows = []
    for conflict in conflicts:
        for detail in conflict.get("details", []):
            owners = detail.get("owners", {})
            a = conflict.get("a")
            b = conflict.get("b")
            winner = detail.get("winner", "undetermined")
            rows.append(
                {
                    "virtual_path": detail.get("path"),
                    "mod_a": {"id": a, "name": conflict.get("a_name"), **(owners.get(a) or {})},
                    "mod_b": {"id": b, "name": conflict.get("b_name"), **(owners.get(b) or {})},
                    "classification": detail.get("classification", "unknown"),
                    "winner": display_name(winner) if winner in selected else str(winner),
                    "load_priority": "forced compatibility owner" if detail.get("auto_fix") else "undetermined",
                    "recommended_action": detail.get("recommended_action", "Review manually."),
                    "auto_fix": bool(detail.get("auto_fix")),
                    "rule_id": detail.get("rule_id"),
                }
            )

    active_dark_rule = mod_compat.active_dark_terrain_rule(selected)
    planned = [
        {
            **action,
            "mod_name": display_name(action.get("mod")),
            "winner": str(active_dark_rule.get("winner", "other shader / base game")) if active_dark_rule else "undetermined",
        }
        for action in mod_compat.planned_resource_actions(selected)
    ]
    return {
        "generated_at": _utc_now_iso(),
        "selected_mods": [{"id": mod, "name": display_name(mod)} for mod in selected],
        "active_compatibility_rules": mod_compat.active_rules(selected),
        "collisions": rows,
        "planned_resource_actions": planned,
    }


def write_collision_report(mods, conflicts=None) -> str:
    report = build_collision_report(mods, conflicts=conflicts)
    os.makedirs(base.logs_dir, exist_ok=True)
    path = os.path.join(base.logs_dir, COLLISION_REPORT_FILE)
    fd, temporary = tempfile.mkstemp(prefix=".minify-compat-", suffix=".json", dir=base.logs_dir)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as file:
            json.dump(report, file, indent=2, ensure_ascii=False, sort_keys=True)
        os.replace(temporary, path)
    except Exception:
        try:
            os.remove(temporary)
        except FileNotFoundError:
            pass
        raise
    return path

