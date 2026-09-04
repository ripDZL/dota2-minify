"""Persistent mod-library metadata, indexing, conflict analysis, and D2PFX import.

This module intentionally has no Dear PyGui dependency so it can be used by
headless/CLI code and by the patcher preflight path.
"""

from __future__ import annotations

import base64
import datetime as _dt
import hashlib
import http.client
import ipaddress
import json
import os
import re
import shutil
import socket
import ssl
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
import zlib
from collections import defaultdict
from pathlib import Path

from core import base, mod_compat, mods_shared, security

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

# Dota2PornFxWeb share-link support. User-supplied URLs are intentionally
# restricted to the official short-link/front-end hosts. Catalogue, mod-file,
# and preview URLs are also restricted to official D2PFX frontends or the
# canonical h6rd/Dota2PornFxWeb raw GitHub repository.
D2PFX_SHARE_HOST = "share.d2pfx.workers.dev"
D2PFX_FRONTEND_HOSTS = {
    "d2pfx.netlify.app",
    "d2pfx.vercel.app",
    "d2pfx.onrender.com",
    "h6rd.github.io",
    "hrdq.codeberg.page",
}
D2PFX_CATALOG_URLS = (
    "https://raw.githubusercontent.com/h6rd/Dota2PornFxWeb/main/assets/data/mods.json",
    "https://d2pfx.netlify.app/assets/data/mods.json",
    "https://d2pfx.vercel.app/assets/data/mods.json",
)
D2PFX_FILES_BASE_URL = "https://raw.githubusercontent.com/h6rd/Dota2PornFxWeb/main/assets/files"
D2PFX_RAW_REPO_PATH_PREFIX = "/h6rd/Dota2PornFxWeb/"
D2PFX_CATALOG_CACHE_FILE = "d2pfx-mods-catalog.json"
D2PFX_CATALOG_CACHE_SECONDS = 6 * 60 * 60
D2PFX_MAX_PAYLOAD_CHARS = 2_000_000
D2PFX_MAX_PACK_ITEMS = 150
D2PFX_MAX_EXTRACTED_BYTES_PER_ITEM = 4 * 1024 * 1024 * 1024
D2PFX_MAX_CATALOG_BYTES = 64 * 1024 * 1024
D2PFX_MAX_MOD_BYTES = 2 * 1024 * 1024 * 1024
D2PFX_NON_VPK_ONLY_CATEGORIES = {"fonts", "cursors"}
D2PFX_BROWSER_VERSION = "0.4"
D2PFX_PREVIEWS_BASE_URL = "https://raw.githubusercontent.com/h6rd/Dota2PornFxWeb/main/assets/previews"
D2PFX_RENAME_CATEGORIES = {
    "trees",
    "river",
    "shaders",
    "herofx",
    "ranged-attack",
    "hero-items",
    "optimization",
}



def _utc_now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def _json_load(path: str, default):
    try:
        with open(path, encoding="utf-8-sig") as file:
            value = json.load(file)
        return value
    except Exception:
        return default


def _json_write_atomic(path: str, payload) -> None:
    directory = os.path.dirname(os.path.abspath(path)) or "."
    os.makedirs(directory, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".minify-json-", suffix=".tmp", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as file:
            json.dump(payload, file, indent=2, ensure_ascii=False, sort_keys=True)
        os.replace(temporary, path)
    except Exception:
        try:
            os.remove(temporary)
        except FileNotFoundError:
            pass
        raise


def _library_db_path() -> str:
    return os.path.join(base.config_dir, LIBRARY_DB_FILE)


def _content_index_path() -> str:
    return os.path.join(base.config_dir, CONTENT_INDEX_FILE)


def _load_library_db() -> dict:
    data = _json_load(_library_db_path(), {})
    if not isinstance(data, dict):
        data = {}
    data.setdefault("schema_version", SCHEMA_VERSION)
    data.setdefault("favorites", {})
    data.setdefault("overrides", {})
    if not isinstance(data["favorites"], dict):
        data["favorites"] = {}
    if not isinstance(data["overrides"], dict):
        data["overrides"] = {}
    return data


def _save_library_db(data: dict) -> None:
    data["schema_version"] = SCHEMA_VERSION
    _json_write_atomic(_library_db_path(), data)


def _load_content_index() -> dict:
    data = _json_load(_content_index_path(), {})
    if not isinstance(data, dict):
        data = {}
    records = data.get("records")
    if not isinstance(records, dict):
        records = {}
    return {"schema_version": SCHEMA_VERSION, "records": records}


def _save_content_index(data: dict) -> None:
    data["schema_version"] = SCHEMA_VERSION
    _json_write_atomic(_content_index_path(), data)


def _norm_path(path: str) -> str:
    return os.path.normcase(os.path.abspath(path))


def _stat_signature(path: str) -> tuple[int, int]:
    stat = os.stat(path)
    return int(stat.st_size), int(getattr(stat, "st_mtime_ns", int(stat.st_mtime * 1_000_000_000)))


def _record_key_for_path(path: str) -> str:
    return _norm_path(path)


def refresh_index(mods=None) -> dict:
    """Refresh cheap file metadata while preserving expensive hashes/content lists.

    No VPK contents are opened here. Expensive work is lazy and cached by size +
    mtime_ns, so ordinary Refresh Mods stays fast even with a large library.
    """
    data = _load_content_index()
    old_records = data["records"]
    new_records = {}
    now = _utc_now_iso()

    if mods is None:
        mods = list(mods_shared.visually_available_mods)

    for mod in mods:
        path = mods_shared.get_mod_path(mod)
        if not os.path.exists(path):
            continue

        try:
            size, mtime_ns = _stat_signature(path) if os.path.isfile(path) else (0, int(os.stat(path).st_mtime_ns))
        except OSError:
            continue

        key = _record_key_for_path(path)
        old = old_records.get(key, {}) if isinstance(old_records.get(key), dict) else {}
        unchanged = old.get("size") == size and old.get("mtime_ns") == mtime_ns

        record = {
            "path": os.path.abspath(path),
            "mod_id": mod,
            "size": size,
            "mtime_ns": mtime_ns,
            "first_seen": old.get("first_seen") or now,
            "last_seen": now,
            "type": "vpk" if mod.lower().endswith(".vpk") else "standard",
            "display_name": mods_shared.get_mod_label(mod),
            "category": mods_shared.get_mod_group(mod),
            "source": mods_shared.get_mod_source(mod),
        }

        if unchanged:
            for expensive in ("sha256", "entries", "entries_indexed_at", "entry_count"):
                if expensive in old:
                    record[expensive] = old[expensive]

        new_records[key] = record

    data["records"] = new_records
    _save_content_index(data)
    return data


def _record_for_mod(mod: str, create=True) -> tuple[dict, dict, str]:
    data = _load_content_index()
    path = mods_shared.get_mod_path(mod)
    key = _record_key_for_path(path)
    record = data["records"].get(key)
    if not isinstance(record, dict) and create:
        refresh_index()
        data = _load_content_index()
        record = data["records"].get(key)
    if not isinstance(record, dict):
        record = {}
    return data, record, key


def get_first_seen(mod: str) -> str:
    _, record, _ = _record_for_mod(mod)
    return str(record.get("first_seen", ""))


def get_sha256(mod: str) -> str:
    if not mod.lower().endswith(".vpk"):
        return ""

    data, record, key = _record_for_mod(mod)
    path = mods_shared.get_mod_path(mod)
    if not os.path.isfile(path):
        return ""

    try:
        size, mtime_ns = _stat_signature(path)
    except OSError:
        return ""

    if record.get("size") == size and record.get("mtime_ns") == mtime_ns and record.get("sha256"):
        return str(record["sha256"])

    fingerprint = mods_shared.get_mod_fingerprint(mod)
    if not fingerprint:
        return ""

    record.update({"size": size, "mtime_ns": mtime_ns, "sha256": fingerprint})
    data["records"][key] = record
    _save_content_index(data)
    return fingerprint


def _stable_keys(mod: str, calculate_hash=False) -> list[str]:
    if not mod.lower().endswith(".vpk"):
        return [f"mod:{mod.casefold()}"]

    keys = []
    _, record, _ = _record_for_mod(mod)
    metadata_fingerprint = str(mods_shared.get_mod_metadata(mod).get("fingerprint", "")).strip().casefold()
    fingerprint = metadata_fingerprint or str(record.get("sha256", "")).strip().casefold()
    if not fingerprint and calculate_hash:
        fingerprint = get_sha256(mod)
    if fingerprint:
        keys.append(f"sha256:{fingerprint}")
    keys.append(f"path:{_record_key_for_path(mods_shared.get_mod_path(mod))}")
    return keys


def stable_key(mod: str, calculate_hash=False) -> str:
    return _stable_keys(mod, calculate_hash=calculate_hash)[0]


def is_favorite(mod: str) -> bool:
    data = _load_library_db()
    return any(bool(data["favorites"].get(key, False)) for key in _stable_keys(mod, calculate_hash=False))


def set_favorite(mod: str, value: bool) -> None:
    data = _load_library_db()
    existing_keys = _stable_keys(mod, calculate_hash=False)
    if value:
        key = stable_key(mod, calculate_hash=True)
        data["favorites"][key] = True
        # Remove stale path aliases once a stable fingerprint exists.
        if key.startswith("sha256:"):
            for old_key in existing_keys:
                if old_key.startswith("path:"):
                    data["favorites"].pop(old_key, None)
    else:
        for key in _stable_keys(mod, calculate_hash=True):
            data["favorites"].pop(key, None)
    _save_library_db(data)


def toggle_favorite(mod: str) -> bool:
    new_value = not is_favorite(mod)
    set_favorite(mod, new_value)
    return new_value


def get_override(mod: str) -> dict:
    data = _load_library_db()
    for key in _stable_keys(mod, calculate_hash=False):
        value = data["overrides"].get(key, {})
        if isinstance(value, dict) and value:
            return dict(value)
    return {}


def set_override(mod: str, display_name="", category="", source="") -> None:
    data = _load_library_db()
    key = stable_key(mod, calculate_hash=mod.lower().endswith(".vpk"))
    value = {}
    if str(display_name).strip():
        value["display_name"] = str(display_name).strip()
    if str(category).strip():
        value["category"] = str(category).strip()
    if str(source).strip():
        value["source"] = str(source).strip()
    if value:
        data["overrides"][key] = value
    else:
        for old_key in _stable_keys(mod, calculate_hash=False):
            data["overrides"].pop(old_key, None)
    _save_library_db(data)


def _browser_manifest_info(mod: str) -> dict:
    """Return normalized browser metadata for a directory-backed Minify mod."""
    if mod.lower().endswith(".vpk"):
        return {}
    try:
        from patch import manifest_utils

        cfg = manifest_utils.get_mod(mods_shared.get_mod_path(mod))
        if not isinstance(cfg, dict):
            return {}
        browser = cfg.get("browser", {})
        return dict(browser) if isinstance(browser, dict) else {}
    except Exception:
        return {}


def is_d2pfx(mod: str) -> bool:
    """True for native D2PFX Browser components installed as Minify mod directories."""
    browser = _browser_manifest_info(mod)
    return browser.get("browser") == "d2pfx" or str(browser.get("name", "")).casefold().startswith("d2pfx")


def display_name(mod: str) -> str:
    override = get_override(mod).get("display_name")
    if override:
        return str(override)
    browser = _browser_manifest_info(mod)
    if browser.get("browser") == "d2pfx":
        name = str(browser.get("name") or mods_shared.get_mod_label(mod))
        label = str(browser.get("label") or "").strip()
        return f"{name} ({label})" if label else name
    return str(mods_shared.get_mod_label(mod))


def category(mod: str) -> str:
    override = get_override(mod).get("category")
    if override:
        return str(override)
    browser = _browser_manifest_info(mod)
    if browser.get("browser") == "d2pfx" and browser.get("category"):
        return str(browser["category"])
    value = mods_shared.get_mod_group(mod)
    if value:
        return str(value)
    return "VPK" if mod.lower().endswith(".vpk") else "Standard"


def source(mod: str) -> str:
    override = get_override(mod).get("source")
    if override:
        return str(override)
    browser = _browser_manifest_info(mod)
    if browser.get("browser") == "d2pfx":
        return "D2PFX"
    value = mods_shared.get_mod_source(mod)
    if value:
        return str(value)
    return "Minify" if not mod.lower().endswith(".vpk") else "Local VPK"


def _iter_embedded_vpks(root: str):
    for current_root, dirs, files in os.walk(root):
        dirs[:] = [name for name in dirs if not os.path.islink(os.path.join(current_root, name))]
        for name in files:
            if name.casefold().endswith(".vpk"):
                yield os.path.join(current_root, name)


def _standard_entries(mod: str) -> list[str]:
    """Index loose ``files`` payloads plus VPKs inside directory-backed mods."""
    import vpk

    root = mods_shared.get_mod_path(mod)
    results = set()
    folder = os.path.join(root, "files")
    if os.path.isdir(folder):
        for current_root, _, files in os.walk(folder):
            for name in files:
                full = os.path.join(current_root, name)
                rel = os.path.relpath(full, folder).replace(os.sep, "/").casefold()
                if rel:
                    results.add(rel)

    # D2PFX and other directory-backed mods may carry one or more VPKs rather
    # than a loose ``files`` tree. Index their virtual paths too so conflict
    # coverage matches what the build hook actually merges.
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
    """Return hash/size metadata for one virtual path owned by a mod."""
    normalized = str(virtual_path or "").replace("\\", "/").lstrip("/").casefold()
    root = mods_shared.get_mod_path(mod)
    try:
        if os.path.isfile(root) and root.casefold().endswith(".vpk"):
            return _fingerprint_vpk_entry(root, normalized) or {}

        direct = os.path.join(root, "files", *normalized.split("/"))
        if os.path.isfile(direct):
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


def index_contents(mod: str, force=False) -> list[str]:
    data, record, key = _record_for_mod(mod)
    path = mods_shared.get_mod_path(mod)
    if not os.path.exists(path):
        return []

    # File-backed VPKs can safely reuse cached directory tables when size +
    # mtime_ns still match. Directory-backed mods are rescanned because changing
    # a nested payload does not reliably change the root directory mtime.
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
    record["entries"] = entries
    record["entry_count"] = len(entries)
    record["indexer_version"] = 2
    record["entries_indexed_at"] = _utc_now_iso()
    data["records"][key] = record
    _save_content_index(data)
    return entries


def estimate_entry_count(mods) -> int:
    total = 0
    for mod in mods:
        _, record, _ = _record_for_mod(mod)
        count = record.get("entry_count")
        if isinstance(count, int):
            total += count
        else:
            total += len(index_contents(mod))
    return total


def _base_display_name(mod: str) -> str:
    name = display_name(mod)
    return re.sub(r"\s*\[\d+/\d+\]\s*$", "", name).strip().casefold()


def _conflict_severity(a: str, b: str, paths: list[str]) -> str:
    if _base_display_name(a) == _base_display_name(b):
        return "expected"
    if any(os.path.splitext(path)[1].casefold() in CRITICAL_EXTENSIONS for path in paths):
        return "critical"
    return "possible"


def analyze_conflicts(mods, max_examples=8) -> list[dict]:
    """Find exact output-path collisions between selected mods.

    VPKs are indexed from their directory tables; standard mods index their
    direct ``files`` tree. Results are grouped by mod pair to avoid dumping
    thousands of individual paths into the UI.
    """
    mods = [mod for mod in mods if os.path.exists(mods_shared.get_mod_path(mod))]
    entry_owners = defaultdict(list)

    for mod in mods:
        for entry in index_contents(mod):
            base_name = os.path.basename(entry)
            if base_name.startswith("minify_"):
                continue
            entry_owners[entry].append(mod)

    pair_paths = defaultdict(list)
    for entry, owners in entry_owners.items():
        unique = list(dict.fromkeys(owners))
        if len(unique) < 2:
            continue
        for i in range(len(unique)):
            for j in range(i + 1, len(unique)):
                pair = tuple(sorted((unique[i], unique[j]), key=str.casefold))
                pair_paths[pair].append(entry)

    conflicts = []
    for (a, b), paths in pair_paths.items():
        severity = _conflict_severity(a, b, paths)
        # Fingerprint every shared virtual path for the machine-readable
        # compatibility report. The UI still renders only a small preview,
        # so complete reporting does not turn Patch Preview into a wall of text.
        details = []
        for virtual_path in paths:
            fingerprints = {
                a: fingerprint_entry(a, virtual_path),
                b: fingerprint_entry(b, virtual_path),
            }
            classification = mod_compat.classify_collision(virtual_path, (a, b), fingerprints)
            details.append(
                {
                    "path": virtual_path,
                    "owners": fingerprints,
                    **classification,
                }
            )
        if any(item.get("classification") == "true conflict" for item in details):
            severity = "critical"
        group_classification = next(
            (name for name in ("true conflict", "unknown", "intentional override") if any(item.get("classification") == name for item in details)),
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
    """Build a machine-readable per-path compatibility report."""
    selected = list(dict.fromkeys(mods or []))
    if conflicts is None:
        conflicts = analyze_conflicts(selected)
    rows = []
    for conflict in conflicts:
        for detail in conflict.get("details", []):
            owners = detail.get("owners", {})
            a = conflict.get("a")
            b = conflict.get("b")
            winner = detail.get("winner", "undetermined")
            winner_name = display_name(winner) if winner in selected else str(winner)
            rows.append(
                {
                    "virtual_path": detail.get("path"),
                    "mod_a": {"id": a, "name": conflict.get("a_name"), **(owners.get(a) or {})},
                    "mod_b": {"id": b, "name": conflict.get("b_name"), **(owners.get(b) or {})},
                    "classification": detail.get("classification", "unknown"),
                    "winner": winner_name,
                    "load_priority": "forced compatibility owner" if detail.get("auto_fix") else "undetermined",
                    "recommended_action": detail.get("recommended_action", "Review manually."),
                    "auto_fix": bool(detail.get("auto_fix")),
                    "rule_id": detail.get("rule_id"),
                }
            )
    planned = []
    active_dark_rule = mod_compat.active_dark_terrain_rule(selected)
    for action in mod_compat.planned_resource_actions(selected):
        planned.append(
            {
                **action,
                "mod_name": display_name(action.get("mod")),
                "winner": str(active_dark_rule.get("winner", "other shader / base game")) if active_dark_rule else "undetermined",
            }
        )
    return {
        "generated_at": _utc_now_iso(),
        "selected_mods": [{"id": mod, "name": display_name(mod)} for mod in selected],
        "active_compatibility_rules": mod_compat.active_rules(selected),
        "collisions": rows,
        "planned_resource_actions": planned,
    }


def write_collision_report(mods, conflicts=None) -> str:
    report = build_collision_report(mods, conflicts=conflicts)
    path = os.path.join(base.logs_dir, COLLISION_REPORT_FILE)
    _json_write_atomic(path, report)
    return path


def _safe_folder_name(name: str) -> str:
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", str(name)).strip().rstrip(". ")
    name = name[:96].rstrip(". ") or "D2PFX Pack"
    reserved = {"con", "prn", "aux", "nul", *(f"com{i}" for i in range(1, 10)), *(f"lpt{i}" for i in range(1, 10))}
    if name.split(".", 1)[0].casefold() in reserved:
        name = "_" + name
    return name


def _unique_dir(parent: str, name: str) -> str:
    candidate = os.path.join(parent, name)
    if not os.path.exists(candidate):
        return candidate
    counter = 2
    while True:
        candidate = os.path.join(parent, f"{name} ({counter})")
        if not os.path.exists(candidate):
            return candidate
        counter += 1


def _safe_extract_zip(zip_path: str, target: str) -> None:
    security.safe_extract_zip(
        zip_path,
        target,
        max_entries=security.ARCHIVE_MAX_ENTRIES,
        max_file_bytes=D2PFX_MAX_MOD_BYTES,
        max_total_bytes=D2PFX_MAX_EXTRACTED_BYTES_PER_ITEM,
        max_ratio=security.ARCHIVE_MAX_COMPRESSION_RATIO,
    )



def _d2pfx_catalog_cache_path() -> str:
    return os.path.join(base.cache_dir, D2PFX_CATALOG_CACHE_FILE)


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Return redirect responses to the caller instead of following them.

    D2PFX short links only need the Location header. Not following the redirect
    also avoids a second DNS lookup for the front-end host just to recover the
    already-present ?pack= payload.
    """

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _is_dns_resolution_error(exc: BaseException) -> bool:
    reason = exc.reason if isinstance(exc, urllib.error.URLError) else exc
    if isinstance(reason, socket.gaierror):
        return True
    message = str(reason).casefold()
    return "getaddrinfo failed" in message or "name or service not known" in message or "nodename nor servname" in message


def _read_http_response_limited(response, max_bytes: int) -> bytes:
    content_length = response.headers.get("Content-Length")
    if content_length:
        try:
            size = int(content_length)
        except (TypeError, ValueError):
            size = 0
        if size > max_bytes:
            raise ValueError("Remote response is larger than the allowed safety limit.")
    data = response.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise ValueError("Remote response is larger than the allowed safety limit.")
    return data


def _doh_lookup_ipv4(host: str, *, timeout=6) -> list[str]:
    """Resolve one allow-listed host through Cloudflare DoH without system DNS.

    This is used only after the normal resolver has returned a host-not-found
    error. The TLS connection itself is still certificate-verified. No arbitrary
    user-supplied host is ever sent through this fallback.
    """
    host = str(host or "").strip().casefold()
    allowed = {D2PFX_SHARE_HOST, *D2PFX_FRONTEND_HOSTS, "raw.githubusercontent.com"}
    if host not in allowed:
        raise ValueError(f"Secure DNS fallback is not permitted for host: {host or 'unknown'}")

    errors = []
    resolvers = (
        ("1.1.1.1", "cloudflare-dns.com", "/dns-query?", "application/dns-json"),
        ("1.0.0.1", "cloudflare-dns.com", "/dns-query?", "application/dns-json"),
        ("8.8.8.8", "dns.google", "/resolve?", "application/json"),
    )
    for resolver_ip, resolver_host, resolver_path, accept in resolvers:
        query = resolver_path + urllib.parse.urlencode({"name": host, "type": "A"})
        raw_socket = None
        tls_socket = None
        try:
            raw_socket = socket.create_connection((resolver_ip, 443), timeout=timeout)
            context = ssl.create_default_context()
            tls_socket = context.wrap_socket(raw_socket, server_hostname=resolver_host)
            request = (
                f"GET {query} HTTP/1.1\r\n"
                f"Host: {resolver_host}\r\n"
                f"Accept: {accept}\r\n"
                f"User-Agent: Minify/{getattr(base, 'VERSION', 'unknown')} D2PFXImporter\r\n"
                "Connection: close\r\n\r\n"
            ).encode("ascii")
            tls_socket.sendall(request)
            response = http.client.HTTPResponse(tls_socket)
            response.begin()
            body = response.read(1024 * 1024)
            if response.status != 200:
                raise OSError(f"DoH resolver returned HTTP {response.status}")
            payload = json.loads(body.decode("utf-8"))
            addresses = []
            for answer in payload.get("Answer", []) if isinstance(payload, dict) else []:
                if not isinstance(answer, dict) or int(answer.get("type", 0) or 0) != 1:
                    continue
                candidate = str(answer.get("data", "")).strip()
                try:
                    addresses.append(str(ipaddress.IPv4Address(candidate)))
                except ipaddress.AddressValueError:
                    continue
            if addresses:
                return list(dict.fromkeys(addresses))
            raise OSError("DoH resolver returned no IPv4 address")
        except Exception as exc:
            errors.append(f"{resolver_ip}: {exc}")
        finally:
            try:
                if tls_socket is not None:
                    tls_socket.close()
                elif raw_socket is not None:
                    raw_socket.close()
            except Exception:
                pass
    raise OSError("Secure DNS fallback failed. " + " | ".join(errors[-3:]))


def _https_get_via_ip(url: str, ip: str, *, timeout=20, max_bytes=2 * 1024 * 1024):
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme.casefold() != "https":
        raise ValueError("Secure DNS fallback only supports HTTPS URLs.")
    host = (parsed.hostname or "").casefold()
    if not host:
        raise ValueError("HTTPS URL is missing a host.")
    target = urllib.parse.urlunsplit(("", "", parsed.path or "/", parsed.query, ""))
    if "\r" in target or "\n" in target:
        raise ValueError("Invalid characters in URL.")

    raw_socket = socket.create_connection((ip, parsed.port or 443), timeout=timeout)
    tls_socket = None
    try:
        context = ssl.create_default_context()
        # SNI and certificate validation continue to use the official hostname,
        # even though the TCP connection uses the DoH-resolved address.
        tls_socket = context.wrap_socket(raw_socket, server_hostname=host)
        request = (
            f"GET {target} HTTP/1.1\r\n"
            f"Host: {host}\r\n"
            "Accept: application/json,text/html,*/*\r\n"
            f"User-Agent: Minify/{getattr(base, 'VERSION', 'unknown')} D2PFXImporter\r\n"
            "Connection: close\r\n\r\n"
        ).encode("ascii")
        tls_socket.sendall(request)
        response = http.client.HTTPResponse(tls_socket)
        response.begin()
        data = _read_http_response_limited(response, max_bytes)
        headers = {str(k): str(v) for k, v in response.headers.items()}
        return int(response.status), headers, data
    finally:
        try:
            if tls_socket is not None:
                tls_socket.close()
            else:
                raw_socket.close()
        except Exception:
            pass


def _read_d2pfx_short_link(url: str, *, timeout=20, max_bytes=2 * 1024 * 1024):
    """Read a D2PFX short link once, preserving the redirect Location header."""
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": f"Minify/{getattr(base, 'VERSION', 'unknown')} D2PFXImporter",
            "Accept": "application/json,text/html,*/*",
        },
    )
    opener = urllib.request.build_opener(_NoRedirectHandler())
    try:
        try:
            response = opener.open(request, timeout=timeout)
        except urllib.error.HTTPError as exc:
            if exc.code in (301, 302, 303, 307, 308):
                data = exc.read(max_bytes + 1)
                if len(data) > max_bytes:
                    raise ValueError("Remote response is larger than the allowed safety limit.")
                return int(exc.code), {str(k): str(v) for k, v in exc.headers.items()}, data, False
            raise
        with response:
            data = _read_http_response_limited(response, max_bytes)
            return int(response.getcode() or 200), {str(k): str(v) for k, v in response.headers.items()}, data, False
    except urllib.error.URLError as exc:
        if not _is_dns_resolution_error(exc):
            raise
        parsed = urllib.parse.urlsplit(url)
        host = (parsed.hostname or "").casefold()
        last_error = exc
        for ip in _doh_lookup_ipv4(host, timeout=min(timeout, 6)):
            try:
                status, headers, data = _https_get_via_ip(url, ip, timeout=timeout, max_bytes=max_bytes)
                return status, headers, data, True
            except Exception as fallback_exc:
                last_error = fallback_exc
        raise urllib.error.URLError(
            f"System DNS could not resolve {host}, and the secure D2PFX DNS fallback also failed: {last_error}"
        ) from exc


def _validate_d2pfx_remote_url(url: str, *, allow_frontends: bool = True) -> str:
    """Constrain D2PFX network fetches to reviewed HTTPS provenance."""
    parsed = urllib.parse.urlparse(str(url or ""))
    if parsed.scheme.casefold() != "https":
        raise ValueError("D2PFX remote assets must use HTTPS.")
    host = (parsed.hostname or "").casefold()
    if host == "raw.githubusercontent.com":
        if not parsed.path.startswith(D2PFX_RAW_REPO_PATH_PREFIX):
            raise ValueError("D2PFX raw GitHub URL is outside the canonical Dota2PornFxWeb repository.")
        return url
    if allow_frontends and host in D2PFX_FRONTEND_HOSTS:
        return url
    raise ValueError(f"Unsupported D2PFX remote asset host: {host or 'unknown'}")


def _validate_d2pfx_catalog_url(url: str) -> str:
    return _validate_d2pfx_remote_url(url, allow_frontends=True)


def _validate_d2pfx_asset_url(url: str) -> str:
    return _validate_d2pfx_remote_url(url, allow_frontends=True)


def _read_url_bytes(url: str, *, timeout=30, max_bytes=16 * 1024 * 1024) -> tuple[str, bytes]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": f"Minify/{getattr(base, 'VERSION', 'unknown')} D2PFXImporter",
            "Accept": "application/json,text/html,*/*",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        final_url = response.geturl()
        content_length = response.headers.get("Content-Length")
        if content_length:
            try:
                if int(content_length) > max_bytes:
                    raise ValueError("Remote response is larger than the allowed safety limit.")
            except ValueError as exc:
                if "safety limit" in str(exc):
                    raise
        data = response.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise ValueError("Remote response is larger than the allowed safety limit.")
    return final_url, data


def _extract_pack_payload_from_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    values = urllib.parse.parse_qs(parsed.query, keep_blank_values=False).get("pack", [])
    return str(values[0]).strip() if values else ""


def _validate_d2pfx_frontend_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme.lower() != "https":
        raise ValueError("D2PFX links must use HTTPS.")
    host = (parsed.hostname or "").casefold()
    if host not in D2PFX_FRONTEND_HOSTS:
        raise ValueError(f"The resolved share link points to an unsupported host: {host or 'unknown'}")
    payload = _extract_pack_payload_from_url(url)
    if not payload:
        raise ValueError("The resolved D2PFX link does not contain a ?pack= payload.")
    return payload


def decode_d2pfx_pack_payload(payload: str) -> dict:
    """Decode Dota2PornFxWeb's Base64URL + raw-DEFLATE pack payload."""
    payload = urllib.parse.unquote(str(payload or "").strip())
    if payload.startswith("pack="):
        payload = payload[5:]
    if not payload or len(payload) > D2PFX_MAX_PAYLOAD_CHARS:
        raise ValueError("The D2PFX pack payload is empty or unreasonably large.")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", payload):
        raise ValueError("The D2PFX pack payload contains invalid characters.")

    padded = payload + "=" * ((4 - len(payload) % 4) % 4)
    try:
        compressed = base64.urlsafe_b64decode(padded.encode("ascii"))
    except Exception as exc:
        raise ValueError("The D2PFX pack payload is not valid Base64URL data.") from exc

    try:
        decoded = security.bounded_zlib_decompress(
            compressed,
            max_output=security.D2PFX_MAX_MANIFEST_BYTES,
        )
    except ValueError as exc:
        raise ValueError("The D2PFX pack payload could not be safely decompressed.") from exc

    try:
        raw = json.loads(decoded.decode("utf-8"))
    except Exception as exc:
        raise ValueError("The D2PFX pack payload does not contain valid JSON.") from exc
    if not isinstance(raw, dict):
        raise ValueError("The D2PFX pack manifest has an invalid root object.")

    raw_items = raw.get("items", [])
    if not isinstance(raw_items, list):
        raise ValueError("The D2PFX pack manifest does not contain an item list.")
    items = []
    seen_items = set()
    for value in raw_items:
        if not isinstance(value, dict):
            continue
        name = str(value.get("n", value.get("name", "")) or "").strip()
        category = str(value.get("c", value.get("categoryId", value.get("category", ""))) or "").strip()
        group = value.get("g", value.get("groupId"))
        group = str(group).strip() if group is not None else None
        if name and category:
            key = (category.casefold(), (group or "").casefold(), name.casefold())
            if key in seen_items:
                continue
            seen_items.add(key)
            items.append({"name": name, "categoryId": category, "groupId": group or None})
    if not items:
        raise ValueError("The D2PFX pack contains no usable mod selections.")
    if len(items) > D2PFX_MAX_PACK_ITEMS:
        raise ValueError(f"The D2PFX pack contains more than {D2PFX_MAX_PACK_ITEMS} selections.")

    return {
        "name": str(raw.get("name") or "D2PFX Shared Pack").strip() or "D2PFX Shared Pack",
        "items": items,
    }


def resolve_d2pfx_share(value: str) -> dict:
    """Resolve a D2PFX short URL, expanded URL, or raw pack payload."""
    original = str(value or "").strip()
    if not original:
        raise ValueError("Paste a Dota2PornFx share link or pack payload first.")

    if "://" not in original:
        result = decode_d2pfx_pack_payload(original)
        result.update({"input": original, "source_url": "raw payload", "resolved_url": "raw payload"})
        return result

    parsed = urllib.parse.urlparse(original)
    if parsed.scheme.lower() != "https":
        raise ValueError("Only HTTPS Dota2PornFx links are accepted.")
    host = (parsed.hostname or "").casefold()

    used_dns_fallback = False
    if host == D2PFX_SHARE_HOST:
        status, headers, body, used_dns_fallback = _read_d2pfx_short_link(
            original, timeout=20, max_bytes=2 * 1024 * 1024
        )
        if status >= 400:
            raise ValueError(f"The D2PFX share service returned HTTP {status}.")

        candidate = ""
        payload = ""
        location = headers.get("Location") or headers.get("location") or ""
        if location:
            candidate = urllib.parse.urljoin(original, location)
            try:
                payload = _validate_d2pfx_frontend_url(candidate)
            except ValueError:
                candidate = ""

        if not payload:
            candidate_from_body = ""
            try:
                data = json.loads(body.decode("utf-8"))
                if isinstance(data, dict):
                    for key in ("url", "longUrl", "long_url", "target", "destination"):
                        if isinstance(data.get(key), str):
                            candidate_from_body = data[key]
                            break
            except Exception:
                pass
            if not candidate_from_body:
                body_text = body.decode("utf-8", errors="ignore")
                match = re.search(r'https://[^\s"\'<>]+[?&]pack=[A-Za-z0-9_%=-]+', body_text)
                if match:
                    candidate_from_body = match.group(0).replace("&amp;", "&")
            if not candidate_from_body:
                raise ValueError("The D2PFX short link did not resolve to a supported pack URL.")
            candidate = candidate_from_body
            payload = _validate_d2pfx_frontend_url(candidate)
    elif host in D2PFX_FRONTEND_HOSTS:
        candidate = original
        payload = _validate_d2pfx_frontend_url(candidate)
    else:
        raise ValueError(
            "Unsupported D2PFX link host. Use an official share.d2pfx.workers.dev link "
            "or a Dota2PornFx ?pack= URL."
        )

    result = decode_d2pfx_pack_payload(payload)
    result.update({
        "input": original,
        "source_url": original,
        "resolved_url": candidate,
        "dns_fallback_used": used_dns_fallback,
    })
    return result


def _load_d2pfx_catalog(force_refresh=False) -> tuple[dict, str, bool]:
    """Return current D2PFX catalogue, source label, and stale-cache flag."""
    cache_path = _d2pfx_catalog_cache_path()
    cached = _json_load(cache_path, {})
    if not isinstance(cached, dict):
        cached = {}
    cached_data = cached.get("data") if isinstance(cached.get("data"), dict) else None
    fetched_at = float(cached.get("fetched_at", 0) or 0)
    if cached_data and not force_refresh and time.time() - fetched_at < D2PFX_CATALOG_CACHE_SECONDS:
        return cached_data, str(cached.get("source", "cache")), False

    errors = []
    for url in D2PFX_CATALOG_URLS:
        try:
            _validate_d2pfx_catalog_url(url)
            final_url, body = _read_url_bytes(url, timeout=30, max_bytes=D2PFX_MAX_CATALOG_BYTES)
            _validate_d2pfx_catalog_url(final_url)
            data = json.loads(body.decode("utf-8"))
            if not isinstance(data, dict) or not isinstance(data.get("modsData"), dict):
                raise ValueError("catalogue is missing modsData")
            _json_write_atomic(
                cache_path,
                {"fetched_at": time.time(), "source": url, "data": data},
            )
            return data, url, False
        except Exception as exc:
            errors.append(f"{url}: {exc}")

    if cached_data:
        return cached_data, str(cached.get("source", "cache")), True
    raise RuntimeError("Could not download the Dota2PornFx catalogue. " + " | ".join(errors[-3:]))


def _find_d2pfx_mod(item: dict, mods_data: dict) -> dict | None:
    """Resolve a shared-pack selection to the current D2PFX catalogue.

    The returned record intentionally carries the same browser identity fields
    used by BrowserUI (base name + category + style label).  This lets a pack
    import be indistinguishable from clicking Install on each individual card.
    """
    category_id = item["categoryId"]
    item_name = item["name"]
    group_id = item.get("groupId")
    category_data = mods_data.get(category_id)

    candidate_groups = []
    if isinstance(category_data, dict) and isinstance(category_data.get("groups"), list):
        groups = category_data["groups"]
        if group_id:
            candidate_groups.extend(group for group in groups if str(group.get("id", "")) == group_id)
        candidate_groups.extend(group for group in groups if group not in candidate_groups)
        candidates = []
        for group in candidate_groups:
            for mod in group.get("mods", []) if isinstance(group, dict) else []:
                if isinstance(mod, dict):
                    candidates.append((mod, str(group.get("id", "")) or None))
    elif isinstance(category_data, list):
        candidates = [(mod, None) for mod in category_data if isinstance(mod, dict)]
    else:
        candidates = []

    def _base_record(mod, resolved_group):
        return {
            **item,
            "groupId": resolved_group if resolved_group is not None else group_id,
            "base_name": str(mod.get("name", "")),
            "author": mod.get("author"),
            "sender": mod.get("sender"),
            "tags": mod.get("tags", []),
            "links": mod.get("links", []),
            "meta": mod.get("meta", {}),
        }

    for mod, resolved_group in candidates:
        base_name = str(mod.get("name", ""))
        if base_name == item_name:
            file_name = str(mod.get("file", "") or "").strip()
            if file_name:
                return {
                    **_base_record(mod, resolved_group),
                    "file": file_name,
                    "preview": str(mod.get("preview", "") or ""),
                    "label": None,
                }
        styles = mod.get("styles")
        if isinstance(styles, list):
            for style in styles:
                if not isinstance(style, dict):
                    continue
                label = str(style.get("label", ""))
                styled_name = f"{base_name} {label.replace('Style ', '')}".strip()
                if styled_name == item_name:
                    file_name = str(style.get("file", "") or "").strip()
                    if file_name:
                        merged_tags = style.get("tags", mod.get("tags", []))
                        return {
                            **_base_record(mod, resolved_group),
                            "tags": merged_tags,
                            "label": label or None,
                            "style": label,
                            "file": file_name,
                            "preview": str(style.get("preview", "") or ""),
                        }
    return None


def preview_d2pfx_share(value: str, force_catalog_refresh=False) -> dict:
    pack = resolve_d2pfx_share(value)
    catalog, catalog_source, stale_catalog = _load_d2pfx_catalog(force_refresh=force_catalog_refresh)
    mods_data = catalog.get("modsData", {})
    resolved = []
    unresolved = []
    category_counts = defaultdict(int)
    for item in pack["items"]:
        match = _find_d2pfx_mod(item, mods_data)
        if match:
            resolved.append(match)
            category_counts[match["categoryId"]] += 1
        else:
            unresolved.append(dict(item))

    non_vpk_only = [item for item in resolved if item["categoryId"] in D2PFX_NON_VPK_ONLY_CATEGORIES]
    vpk_candidates = [item for item in resolved if item["categoryId"] not in D2PFX_NON_VPK_ONLY_CATEGORIES]
    return {
        **pack,
        "resolved": resolved,
        "vpk_candidates": vpk_candidates,
        "non_vpk_only": non_vpk_only,
        "unresolved": unresolved,
        "total": len(pack["items"]),
        "resolved_count": len(resolved),
        "vpk_candidate_count": len(vpk_candidates),
        "non_vpk_only_count": len(non_vpk_only),
        "unavailable_count": len(unresolved),
        "category_counts": dict(sorted(category_counts.items())),
        "catalog_source": catalog_source,
        "stale_catalog": stale_catalog,
    }


def _d2pfx_category_label(category_id: str) -> str:
    special = {
        "herofx": "Hero Spells",
        "hero-items": "Hero Items",
        "hero-sounds": "Hero Sounds",
        "ti-bp-effects": "Effect Packs",
        "ranged-attack": "Ranged Attack",
        "mega-kill": "Mega-Kill",
        "item-effects": "Item Effects",
        "item-icons": "Item Icons",
        "item-sounds": "Item Sounds",
    }
    return special.get(category_id, category_id.replace("-", " ").title())


def _d2pfx_file_url(category_id: str, file_name: str) -> str:
    if file_name.lower().startswith(("http://", "https://")):
        return _validate_d2pfx_asset_url(file_name)
    category = urllib.parse.quote(category_id, safe="")
    filename = urllib.parse.quote(file_name, safe="/")
    return _validate_d2pfx_asset_url(f"{D2PFX_FILES_BASE_URL}/{category}/{filename}")


def _download_d2pfx_file(url: str, destination: str, progress=None) -> None:
    _validate_d2pfx_asset_url(url)
    request = urllib.request.Request(
        url,
        headers={"User-Agent": f"Minify/{getattr(base, 'VERSION', 'unknown')} D2PFXImporter"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        _validate_d2pfx_asset_url(response.geturl())
        length = response.headers.get("Content-Length")
        total = int(length) if length and length.isdigit() else 0
        if total > D2PFX_MAX_MOD_BYTES:
            raise ValueError("A D2PFX mod download exceeds the 2 GiB safety limit.")
        downloaded = 0
        with open(destination, "wb") as file:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                downloaded += len(chunk)
                if downloaded > D2PFX_MAX_MOD_BYTES:
                    raise ValueError("A D2PFX mod download exceeds the 2 GiB safety limit.")
                file.write(chunk)
                if progress:
                    progress(downloaded, total)


def _unique_file_name(file_name: str, existing_names: set[str]) -> str:
    candidate = os.path.basename(file_name)
    key = candidate.casefold()
    if key not in existing_names:
        existing_names.add(key)
        return candidate
    stem, extension = os.path.splitext(candidate)
    counter = 1
    while True:
        candidate = f"{stem}_{counter}{extension}"
        key = candidate.casefold()
        if key not in existing_names:
            existing_names.add(key)
            return candidate
        counter += 1


def _create_d2pfx_name_allocator(existing_names: set[str]):
    priority_counter = 2
    normal_counter = 10

    def allocate(original_name: str, category_id: str) -> str:
        nonlocal priority_counter, normal_counter
        original_name = os.path.basename(original_name)
        priority = category_id in D2PFX_RENAME_CATEGORIES
        if original_name.casefold().endswith("_dir.vpk"):
            if priority and priority_counter <= 9:
                candidate = f"!pak{priority_counter:02d}_dir.vpk"
                priority_counter += 1
                existing_names.add(candidate.casefold())
                return candidate
            if not priority and normal_counter <= 99:
                candidate = f"pak{normal_counter:02d}_dir.vpk"
                normal_counter += 1
                existing_names.add(candidate.casefold())
                return candidate
            if not priority:
                return _unique_file_name("pak99_dir.vpk", existing_names)
        if priority and not original_name.startswith("!"):
            original_name = "!" + original_name
        return _unique_file_name(original_name, existing_names)

    return allocate


def _d2pfx_browser_key(item: dict) -> tuple[str, str, str | None]:
    return (
        str(item.get("base_name") or item.get("name") or "Unknown"),
        str(item.get("categoryId") or "unknown"),
        str(item.get("label")) if item.get("label") not in (None, "") else None,
    )


def _scan_d2pfx_browser_installs() -> dict:
    """Return D2PFX Browser identities already installed as normal Minify mods."""
    installed = {}
    try:
        entries = os.listdir(base.mods_dir)
    except Exception:
        return installed
    for mod_dir in entries:
        if mod_dir.startswith("_"):
            continue
        path = os.path.join(base.mods_dir, mod_dir)
        if not os.path.isdir(path):
            continue
        manifest = _json_load(os.path.join(path, "manifest.json"), {})
        browser = manifest.get("browser") if isinstance(manifest, dict) else None
        if not isinstance(browser, dict):
            continue
        if browser.get("browser") != "d2pfx":
            continue
        name = str(browser.get("name") or "").strip()
        category = str(browser.get("category") or "").strip()
        label = browser.get("label")
        label = str(label) if label not in (None, "") else None
        if name and category:
            installed[(name, category, label)] = path
    return installed


def _archive_legacy_d2pfx_packs(pack_name: str, share_url: str = "") -> int:
    """Hide v16-era nested pack imports after a successful Browser migration.

    Old packs are moved below a dot-prefixed directory instead of deleted. The
    nested-VPK scanner deliberately skips dot directories, so this prevents
    duplicate application while keeping the old files available for recovery.
    """
    source_root = os.path.join(base.mods_dir, mods_shared.VPK_COLLECTION_DIR, "D2PFX Packs")
    archive_root = os.path.join(base.mods_dir, mods_shared.VPK_COLLECTION_DIR, ".Migrated D2PFX Packs")
    if not os.path.isdir(source_root):
        return 0
    moved = 0
    for entry in list(os.scandir(source_root)):
        if not entry.is_dir() or entry.name.startswith("."):
            continue
        manifest_path = os.path.join(entry.path, mods_shared.D2PFX_MANIFEST_FILE)
        manifest = _json_load(manifest_path, {})
        if not isinstance(manifest, dict):
            continue
        old_share = str(manifest.get("share_url") or "").strip()
        old_pack = str(manifest.get("pack_name") or "").strip()
        exact_share_match = bool(share_url and old_share and old_share == share_url)
        pack_match = bool(pack_name and old_pack and old_pack == pack_name)
        if not (exact_share_match or (not share_url and pack_match)):
            continue
        os.makedirs(archive_root, exist_ok=True)
        destination = _unique_dir(archive_root, entry.name)
        try:
            os.replace(entry.path, destination)
            moved += 1
        except Exception:
            pass
    return moved


def _d2pfx_component_dir_name(item: dict) -> str:
    name, category, label = _d2pfx_browser_key(item)
    raw = f"D2PFX {category.upper()} - {name}"
    if label:
        raw += f" {label}"
    return _safe_folder_name(raw)


def _d2pfx_browser_manifest(item: dict, pack_name: str, share_url: str = "") -> dict:
    name, category, label = _d2pfx_browser_key(item)
    browser = {
        "browser": "d2pfx",
        "name": name,
        "category": category,
        "author": item.get("author"),
        "sender": item.get("sender"),
        "links": item.get("links", []),
        "tags": item.get("tags", []),
        "version": D2PFX_BROWSER_VERSION,
        "label": label,
        "imported_from_pack": pack_name,
        "share_url": share_url,
    }
    manifest = {
        "browser": browser,
        "d2pfx_pack": {
            "name": pack_name,
            "share_url": share_url,
            "catalog_file": item.get("file", ""),
            "selected_name": item.get("name", name),
            "group_id": item.get("groupId"),
        },
    }
    if category in D2PFX_RENAME_CATEGORIES:
        manifest["order"] = 2
    return manifest


def _write_d2pfx_notes(target_dir: str, item: dict, pack_name: str, share_url: str = "") -> None:
    name, category, label = _d2pfx_browser_key(item)
    lines = [
        f"Installed via D2PFX Browser pack importer {D2PFX_BROWSER_VERSION}",
        "",
        f"Pack: {pack_name}",
        f"Category: {category}",
    ]
    if label:
        lines.append(f"Style: {label}")
    if share_url:
        lines.append(f"Share Link: {share_url}")
    author = item.get("author")
    sender = item.get("sender")
    if author:
        lines.append(f"Author: {', '.join(map(str, author)) if isinstance(author, list) else author}")
    if sender:
        lines.append(f"Sender: {', '.join(map(str, sender)) if isinstance(sender, list) else sender}")
    tags = item.get("tags")
    if isinstance(tags, dict):
        tags = [key for key, enabled in tags.items() if enabled]
    if tags:
        lines.append(f"Tags: {', '.join(map(str, tags)) if isinstance(tags, (list, tuple)) else tags}")
    with open(os.path.join(target_dir, "notes.md"), "w", encoding="utf-8", newline="\n") as file:
        file.write("\n".join(lines) + "\n")


def _extract_d2pfx_vpks(download_path: str, live_file: str, target_dir: str) -> int:
    """Copy only VPK payloads from a D2PFX file into a component directory."""
    if zipfile.is_zipfile(download_path):
        extracted = security.safe_extract_zip(
            download_path,
            target_dir,
            max_entries=security.ARCHIVE_MAX_ENTRIES,
            max_file_bytes=D2PFX_MAX_MOD_BYTES,
            max_total_bytes=D2PFX_MAX_EXTRACTED_BYTES_PER_ITEM,
            max_ratio=security.ARCHIVE_MAX_COMPRESSION_RATIO,
            predicate=lambda info: (
                not info.is_dir()
                and info.filename.replace("\\", "/").casefold().endswith(".vpk")
            ),
        )
        return len(extracted)
    if live_file.casefold().endswith(".vpk"):
        name = os.path.basename(urllib.parse.urlparse(live_file).path) or os.path.basename(live_file)
        _, destination = security.confined_destination(target_dir, name)
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        shutil.copy2(download_path, destination)
        return 1
    return 0


def _download_d2pfx_preview(item: dict, target_dir: str) -> None:
    preview_file = str(item.get("preview", "") or "").strip()
    if not preview_file or preview_file.casefold().endswith((".mp4", ".webm")):
        return
    try:
        if preview_file.lower().startswith(("http://", "https://")):
            preview_url = _validate_d2pfx_asset_url(preview_file)
        else:
            category = urllib.parse.quote(str(item.get("categoryId", "")), safe="")
            filename = urllib.parse.quote(preview_file, safe="/")
            preview_url = _validate_d2pfx_asset_url(f"{D2PFX_PREVIEWS_BASE_URL}/{category}/{filename}")
        request = urllib.request.Request(preview_url, headers={"User-Agent": f"Minify/{getattr(base, 'VERSION', 'unknown')} D2PFXImporter"})
        with urllib.request.urlopen(request, timeout=20) as response:
            _validate_d2pfx_asset_url(response.geturl())
            data = response.read(16 * 1024 * 1024 + 1)
        if len(data) <= 16 * 1024 * 1024:
            with open(os.path.join(target_dir, "preview.jpg"), "wb") as file:
                file.write(data)
    except Exception:
        pass


def _install_d2pfx_component(item: dict, pack_name: str, share_url: str, staging_root: str) -> tuple[str, int]:
    live_file = str(item.get("file", "") or "").strip()
    if not live_file:
        raise ValueError("The current D2PFX catalogue entry has no downloadable file.")
    source_url = _d2pfx_file_url(str(item.get("categoryId", "")), live_file)
    suffix = ".zip" if live_file.casefold().endswith(".zip") else os.path.splitext(urllib.parse.urlparse(live_file).path)[1]
    stage = tempfile.mkdtemp(prefix="component-", dir=staging_root)
    download_path = os.path.join(stage, "download" + (suffix or ".bin"))
    payload_dir = os.path.join(stage, "payload")
    os.makedirs(payload_dir, exist_ok=True)
    try:
        _download_d2pfx_file(source_url, download_path)
        vpk_count = _extract_d2pfx_vpks(download_path, live_file, payload_dir)
        if not vpk_count:
            raise ValueError("This selection did not contain a VPK payload Minify can patch.")
        _json_write_atomic(os.path.join(payload_dir, "manifest.json"), _d2pfx_browser_manifest(item, pack_name, share_url))
        _write_d2pfx_notes(payload_dir, item, pack_name, share_url)
        _download_d2pfx_preview(item, payload_dir)

        target_name = _d2pfx_component_dir_name(item)
        target_dir = os.path.join(base.mods_dir, target_name)
        if os.path.exists(target_dir):
            target_dir = _unique_dir(base.mods_dir, target_name)
        os.replace(payload_dir, target_dir)
        return target_dir, vpk_count
    finally:
        shutil.rmtree(stage, ignore_errors=True)


def import_d2pfx_share(value: str, preview=None, progress=None) -> dict:
    """Install a shared D2PFX pack as individual Browser-managed components.

    Each selection becomes the same kind of top-level Minify mod directory that
    the native D2PFX Browser creates.  Its manifest carries the browser identity,
    so after the normal mod rescan the matching D2PFX card changes from Install
    to Remove and can be uninstalled independently from every other pack item.
    """
    if not isinstance(preview, dict) or preview.get("input") != str(value or "").strip():
        preview = preview_d2pfx_share(value)

    resolved = [item for item in preview.get("resolved", []) if item.get("categoryId") not in D2PFX_NON_VPK_ONLY_CATEGORIES]
    skipped_non_vpk = [item.get("name", "Unknown") for item in preview.get("resolved", []) if item.get("categoryId") in D2PFX_NON_VPK_ONLY_CATEGORIES]
    if not resolved:
        raise ValueError("This D2PFX pack has no Browser-compatible VPK selections for Minify to import.")

    already_map = _scan_d2pfx_browser_installs()
    staging_root = os.path.join(base.mods_dir, "_D2PFX Import Staging")
    os.makedirs(staging_root, exist_ok=True)
    failures = []
    installed = []
    already_installed = []
    copied_vpks = 0
    total = len(resolved)

    try:
        for index, item in enumerate(resolved, start=1):
            key = _d2pfx_browser_key(item)
            if key in already_map:
                already_installed.append(item.get("name", key[0]))
                if progress:
                    progress(f"Already installed: {item.get('name', key[0])} ({index}/{total})", index, total)
                continue
            try:
                if progress:
                    progress(f"Installing {item.get('name', key[0])} ({index}/{total})", index - 1, total)
                target_dir, vpk_count = _install_d2pfx_component(
                    item,
                    str(preview.get("name") or "D2PFX Pack"),
                    str(preview.get("source_url") or ""),
                    staging_root,
                )
                copied_vpks += vpk_count
                installed.append({"name": item.get("name", key[0]), "path": target_dir, "key": key})
                already_map[key] = target_dir
                if progress:
                    progress(f"Installed {item.get('name', key[0])} ({index}/{total})", index, total)
            except Exception as exc:
                failures.append({"name": item.get("name", key[0]), "error": str(exc)})
    finally:
        shutil.rmtree(staging_root, ignore_errors=True)

    if not installed and not already_installed:
        raise RuntimeError("The pack was resolved, but none of its components could be installed.")

    legacy_archived = _archive_legacy_d2pfx_packs(
        str(preview.get("name") or "D2PFX Pack"),
        str(preview.get("source_url") or ""),
    )

    return {
        "pack_name": str(preview.get("name") or "D2PFX Pack"),
        "selected": int(preview.get("total", len(preview.get("items", []))) or 0),
        "resolved": int(preview.get("resolved_count", len(resolved)) or 0),
        "unavailable": int(preview.get("unavailable_count", 0) or 0),
        "installed_components": len(installed),
        "already_installed": len(already_installed),
        "copied": copied_vpks,
        "identified": copied_vpks,
        "unknown": 0,
        "skipped_non_vpk": len(skipped_non_vpk),
        "failures": failures,
        "components": installed,
        "legacy_archived": legacy_archived,
    }


def _catalog_category_id_from_label(label: str, mods_data: dict) -> str | None:
    wanted = str(label or "").strip().casefold()
    if not wanted:
        return None
    for category_id in mods_data:
        if _d2pfx_category_label(category_id).casefold() == wanted:
            return category_id
    slug = re.sub(r"[^a-z0-9]+", "-", wanted).strip("-")
    return slug if slug in mods_data else None


def _resolve_d2pfx_display_name(display_name: str, category_label: str, mods_data: dict) -> dict | None:
    preferred = _catalog_category_id_from_label(category_label, mods_data)
    category_ids = ([preferred] if preferred else []) + [cat for cat in mods_data if cat != preferred]
    for category_id in category_ids:
        match = _find_d2pfx_mod({"name": display_name, "categoryId": category_id, "groupId": None}, mods_data)
        if match:
            return match
    return None


def import_d2pfx_zip(zip_path: str) -> dict:
    """Import a downloaded D2PFX pack into individual Browser-managed mods."""
    zip_path = os.path.abspath(zip_path)
    if not os.path.isfile(zip_path) or not zip_path.lower().endswith(".zip"):
        raise ValueError("Choose a Dota2PornFxWeb .zip pack.")

    catalog, _, _ = _load_d2pfx_catalog(force_refresh=False)
    mods_data = catalog.get("modsData", {})
    already_map = _scan_d2pfx_browser_installs()
    failures = []
    installed = []
    already_installed = []
    copied_vpks = 0
    unresolved = []

    with tempfile.TemporaryDirectory(prefix="minify-d2pfx-zip-") as temp:
        _safe_extract_zip(zip_path, temp)
        mods_txt_candidates = list(Path(temp).rglob("Mods.txt"))
        if not mods_txt_candidates:
            raise FileNotFoundError("Mods.txt was not found in the selected pack.")
        mods_txt_candidates.sort(key=lambda p: len(p.parts))
        mods_txt = mods_txt_candidates[0]
        pack_root = mods_txt.parent
        source_mods = pack_root / "mods"
        if not source_mods.is_dir():
            raise FileNotFoundError("The pack does not contain a mods folder beside Mods.txt.")

        mappings = mods_shared.parse_mods_txt(str(mods_txt))
        if not mappings:
            raise ValueError("Mods.txt was found but no VPK mappings could be parsed.")

        grouped = defaultdict(list)
        for source_file in sorted(source_mods.rglob("*.vpk"), key=lambda path: str(path).casefold()):
            if source_file.is_symlink() or not source_file.is_file():
                continue
            metadata = mappings.get(source_file.name.casefold(), {})
            display_name = str(metadata.get("display_name") or "").strip()
            category_label = str(metadata.get("category") or "").strip()
            if display_name:
                grouped[(display_name, category_label)].append(source_file)

        if not grouped:
            raise ValueError("Mods.txt did not map any VPKs to D2PFX component names.")

        staging_root = os.path.join(base.mods_dir, "_D2PFX Import Staging")
        os.makedirs(staging_root, exist_ok=True)
        try:
            for (display_name, category_label), source_files in grouped.items():
                item = _resolve_d2pfx_display_name(display_name, category_label, mods_data)
                if not item:
                    unresolved.append(display_name)
                    continue
                key = _d2pfx_browser_key(item)
                if key in already_map:
                    already_installed.append(display_name)
                    continue
                stage = tempfile.mkdtemp(prefix="zip-component-", dir=staging_root)
                payload = os.path.join(stage, "payload")
                os.makedirs(payload, exist_ok=True)
                try:
                    for source_file in source_files:
                        destination = os.path.join(payload, source_file.name)
                        shutil.copy2(source_file, destination)
                        copied_vpks += 1
                    _json_write_atomic(os.path.join(payload, "manifest.json"), _d2pfx_browser_manifest(item, pack_root.name, ""))
                    _write_d2pfx_notes(payload, item, pack_root.name, "")
                    target_name = _d2pfx_component_dir_name(item)
                    target_dir = os.path.join(base.mods_dir, target_name)
                    if os.path.exists(target_dir):
                        target_dir = _unique_dir(base.mods_dir, target_name)
                    os.replace(payload, target_dir)
                    installed.append({"name": display_name, "path": target_dir, "key": key})
                    already_map[key] = target_dir
                except Exception as exc:
                    failures.append({"name": display_name, "error": str(exc)})
                finally:
                    shutil.rmtree(stage, ignore_errors=True)
        finally:
            shutil.rmtree(staging_root, ignore_errors=True)

    if not installed and not already_installed:
        raise RuntimeError("No current D2PFX Browser components could be recovered from this ZIP pack.")

    legacy_archived = _archive_legacy_d2pfx_packs(pack_root.name, "")

    return {
        "pack_name": pack_root.name,
        "installed_components": len(installed),
        "already_installed": len(already_installed),
        "copied": copied_vpks,
        "identified": copied_vpks,
        "unknown": len(unresolved),
        "unresolved": unresolved,
        "failures": failures,
        "components": installed,
        "legacy_archived": legacy_archived,
    }
