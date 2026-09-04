"""Compatibility rules for known cross-mod virtual-path collisions.

The compatibility layer never rewrites the user's source mod archives. Instead,
it filters specific virtual paths while Minify assembles generated output.

Dark Terrain yields its deferred-post-process material only when another selected
mod actually owns the same virtual resource. This preserves Dark Terrain's own
post-process when used alone while remaining compatible with Aqua, Green,
Cartoon, or future shader mods without hard-coding catalogue names.
"""

from __future__ import annotations

import hashlib
import os
import re
import shutil

from core import mods_shared

DARK_TERRAIN_DEFERRED = "materials/dev/deferred_post_process.vmat_c"
DARK_TERRAIN_FOG = "materials/dev/deferred_post_process_vmat_g_tfog_9ea98ee9.vtex_c"
DARK_TERRAIN_EXCLUSIONS = frozenset({DARK_TERRAIN_DEFERRED, DARK_TERRAIN_FOG})

INTENTIONAL_DARK_SIMPLE_BLEND_PREFIX = "materials/blends/"


def normalize_virtual_path(path: str) -> str:
    return str(path or "").replace("\\", "/").lstrip("/").casefold()


def _normalize_name(value: str) -> str:
    value = str(value or "").casefold().replace(".", " ").replace("_", " ").replace("-", " ")
    return " ".join(re.findall(r"[a-z0-9]+", value))


def _identity_strings(mod: str) -> set[str]:
    values = {str(mod or "")}
    try:
        values.add(mods_shared.get_mod_label(mod))
        values.add(mods_shared.get_mod_filename(mod))
        metadata = mods_shared.get_mod_metadata(mod)
        for key in ("display_name", "browser_name", "name", "label", "category"):
            if metadata.get(key):
                values.add(str(metadata[key]))
    except Exception:
        pass
    return {_normalize_name(value) for value in values if value}


def is_dark_terrain(mod: str) -> bool:
    names = _identity_strings(mod)
    return any(name in {"dark terrain", "dark terrain mod"} for name in names)


def is_simple_dark_terrain(mod: str) -> bool:
    names = _identity_strings(mod)
    return any(name in {"simple dark terrain", "simple dark terrain mod"} for name in names)


def _find_first(mods, predicate):
    for mod in mods:
        if predicate(mod):
            return mod
    return None


def _fingerprint_entry(mod: str, virtual_path: str) -> dict:
    try:
        from core import mod_library

        result = mod_library.fingerprint_entry(mod, virtual_path)
        return result if isinstance(result, dict) else {}
    except Exception:
        return {}


def _owns_deferred_resource(mod: str) -> bool:
    fingerprint = _fingerprint_entry(mod, DARK_TERRAIN_DEFERRED)
    return bool(
        fingerprint
        and not fingerprint.get("error")
        and any(key in fingerprint for key in ("sha256", "crc32", "size", "origin"))
    )


def _deferred_competitors(selected_mods, dark: str) -> list[str]:
    competitors = []
    for mod in selected_mods:
        if mod == dark:
            continue
        if _owns_deferred_resource(mod):
            competitors.append(mod)
    return competitors


def active_dark_terrain_rule(selected_mods) -> dict | None:
    selected = list(dict.fromkeys(selected_mods or []))
    dark = _find_first(selected, is_dark_terrain)
    if not dark:
        return None
    competitors = _deferred_competitors(selected, dark)
    if not competitors:
        return None
    simple = _find_first(selected, is_simple_dark_terrain)
    winner = competitors[-1]
    return {
        "id": "dark-terrain-deferred-post-process-compat",
        "title": "Dark Terrain shader compatibility",
        "dark": dark,
        "simple": simple,
        "competitors": competitors,
        "exclude_from_dark": sorted(DARK_TERRAIN_EXCLUSIONS),
        "winner": winner,
        "summary": (
            "Dark Terrain yields deferred_post_process because another selected mod "
            f"owns the same virtual resource: {', '.join(competitors)}."
        ),
    }


def active_rules(selected_mods) -> list[dict]:
    rule = active_dark_terrain_rule(selected_mods)
    return [rule] if rule else []


def exclusions_for_mod(mod: str, selected_mods) -> set[str]:
    rule = active_dark_terrain_rule(selected_mods)
    if rule and mod == rule["dark"]:
        return set(DARK_TERRAIN_EXCLUSIONS)
    return set()


def exclusion_reason(mod: str, virtual_path: str, selected_mods) -> str | None:
    path = normalize_virtual_path(virtual_path)
    rule = active_dark_terrain_rule(selected_mods)
    if not rule or mod != rule["dark"] or path not in DARK_TERRAIN_EXCLUSIONS:
        return None
    if path == DARK_TERRAIN_DEFERRED:
        competitors = ", ".join(rule.get("competitors", [])) or "another selected mod"
        return f"Dark Terrain yields the shared deferred post-process material to {competitors}."
    return "Dark Terrain fog texture is unused after its deferred material is excluded for a real shader collision."


def copy_standard_files(mod: str, source_dir: str, destination_dir: str, selected_mods) -> list[str]:
    excluded = {normalize_virtual_path(path) for path in exclusions_for_mod(mod, selected_mods)}
    if not excluded:
        shutil.copytree(source_dir, destination_dir, dirs_exist_ok=True)
        return []

    source_abs = os.path.abspath(source_dir)

    def ignore(directory, names):
        ignored = []
        for name in names:
            full = os.path.join(directory, name)
            rel = os.path.relpath(full, source_abs).replace(os.sep, "/")
            if normalize_virtual_path(rel) in excluded:
                ignored.append(name)
        return ignored

    shutil.copytree(source_dir, destination_dir, dirs_exist_ok=True, ignore=ignore)
    return sorted(excluded)


def classify_collision(path: str, owners, fingerprints=None) -> dict:
    owners = list(dict.fromkeys(owners or []))
    normalized = normalize_virtual_path(path)
    fingerprints = fingerprints or {}

    dark = _find_first(owners, is_dark_terrain)
    simple = _find_first(owners, is_simple_dark_terrain)
    other_owner = next((owner for owner in owners if owner != dark), None) if dark else None

    if normalized == DARK_TERRAIN_DEFERRED and dark and other_owner:
        return {
            "classification": "true conflict",
            "winner": other_owner,
            "recommended_action": "Exclude Dark Terrain's deferred material; let the other shader/resource owner win.",
            "auto_fix": True,
            "rule_id": "dark-terrain-deferred-post-process-compat",
        }

    if normalized.startswith(INTENTIONAL_DARK_SIMPLE_BLEND_PREFIX) and dark and simple:
        return {
            "classification": "intentional override",
            "winner": "load-order dependent",
            "recommended_action": "Keep both terrain blend resources; do not auto-remove them.",
            "auto_fix": False,
            "rule_id": None,
        }

    hashes = {
        str(info.get("sha256"))
        for info in fingerprints.values()
        if isinstance(info, dict) and info.get("sha256")
    }
    if len(hashes) == 1 and len(fingerprints) >= 2:
        return {
            "classification": "intentional override",
            "winner": "content identical",
            "recommended_action": "No compatibility change required; payloads are identical.",
            "auto_fix": False,
            "rule_id": None,
        }

    return {
        "classification": "unknown",
        "winner": "undetermined",
        "recommended_action": "Review the compiled resources before generating a compatibility patch.",
        "auto_fix": False,
        "rule_id": None,
    }


def planned_resource_actions(selected_mods) -> list[dict]:
    rule = active_dark_terrain_rule(selected_mods)
    if not rule:
        return []
    competitors = ", ".join(rule.get("competitors", [])) or "the competing shader"
    return [
        {
            "path": DARK_TERRAIN_DEFERRED,
            "mod": rule["dark"],
            "classification": "compatibility exclusion",
            "recommended_action": f"Exclude Dark Terrain's shared deferred material; let {competitors} own it.",
            "rule_id": rule["id"],
        },
        {
            "path": DARK_TERRAIN_FOG,
            "mod": rule["dark"],
            "classification": "safe-to-remove resource",
            "recommended_action": "Exclude because Dark Terrain's deferred material is being yielded for this collision.",
            "rule_id": rule["id"],
        },
    ]


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().casefold()


def _dark_deferred_source_hash(dark_mod: str) -> str:
    try:
        mod_path = mods_shared.get_mod_path(dark_mod)
    except Exception:
        return ""

    direct = os.path.join(mod_path, "files", *DARK_TERRAIN_DEFERRED.split("/"))
    if os.path.isfile(direct):
        try:
            with open(direct, "rb") as file:
                return _sha256_bytes(file.read())
        except OSError:
            return ""

    if os.path.isfile(mod_path) and mod_path.lower().endswith(".vpk"):
        try:
            import vpk

            archive = vpk.open(mod_path)
            entry = archive.get_file(DARK_TERRAIN_DEFERRED)
            if entry:
                return _sha256_bytes(entry.read())
        except Exception:
            return ""
    return ""


def validate_generated_output(output_dir: str, selected_mods) -> dict:
    rule = active_dark_terrain_rule(selected_mods)
    if not rule:
        return {"active": False, "valid": True, "target_archives": [], "fog_archives": []}

    import vpk

    dark_hash = _dark_deferred_source_hash(rule["dark"])
    target_archives = []
    fog_archives = []
    dark_payload_archives = []
    checked = []

    for filename in ("pak65_dir.vpk", "pak66_dir.vpk", "pak67_dir.vpk"):
        path = os.path.join(output_dir, filename)
        if not os.path.isfile(path):
            continue
        archive = vpk.open(path)
        entries = {normalize_virtual_path(entry): entry for entry in archive}
        checked.append(filename)

        target_key = normalize_virtual_path(DARK_TERRAIN_DEFERRED)
        fog_key = normalize_virtual_path(DARK_TERRAIN_FOG)
        if target_key in entries:
            target_archives.append(filename)
            if filename == "pak66_dir.vpk" and dark_hash:
                try:
                    payload = archive.get_file(entries[target_key]).read()
                    if _sha256_bytes(payload) == dark_hash:
                        dark_payload_archives.append(filename)
                except Exception:
                    pass
        if fog_key in entries:
            fog_archives.append(filename)

    errors = []
    if dark_payload_archives:
        errors.append("Dark Terrain's deferred material payload leaked into generated output")
    if fog_archives:
        errors.append("the excluded Dark Terrain fog texture is still present in generated output")

    if errors:
        raise RuntimeError("Dark Terrain shader compatibility validation failed: " + "; ".join(errors))

    return {
        "active": True,
        "valid": True,
        "checked_archives": checked,
        "target_archives": target_archives,
        "fog_archives": fog_archives,
        "dark_payload_archives": dark_payload_archives,
        "winner": rule.get("winner", "competing selected mod"),
    }
