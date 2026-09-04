"Shared mod scanning logic"

import hashlib
import json
import os
import tempfile
import re
import sys

import jsonc

from core import base, constants, utils

VPK_COLLECTION_DIR = "_VPK Mods"
NESTED_VPK_PREFIX = "nested-vpk::"
NESTED_DIR_PREFIX = "nested-mod::"
D2PFX_MANIFEST_FILE = "d2pfx-manifest.json"
D2PFX_MODS_LIST_FILE = "Mods.txt"
VPK_IDENTITY_DB_FILE = "vpk-identities.json"
VPK_HASH_CACHE_FILE = "vpk-hash-cache.json"

mods_alphabetical = []
mods_with_order = []
visually_unavailable_mods = []
visually_available_mods = []
mod_dependencies_list = []
mod_conflicts_list = []
mod_paths = {}
mod_labels = {}
mod_groups = {}
mod_metadata = {}

_get_state_callback = None
_set_state_callback = None


def register_state_callbacks(get_cb, set_cb):
    global _get_state_callback, _set_state_callback
    _get_state_callback = get_cb
    _set_state_callback = set_cb


def get_mod_path(mod):
    """Return the real path for a discovered mod."""
    return mod_paths.get(mod, os.path.join(base.mods_dir, mod))


def get_mod_label(mod):
    """Return the human-readable label shown for a mod."""
    if mod in mod_labels:
        return mod_labels[mod]
    return mod[:-4] if mod.lower().endswith(".vpk") else mod


def get_mod_group(mod):
    """Return the organizational group/category for a nested VPK mod."""
    return mod_groups.get(mod, "")


def get_mod_filename(mod):
    """Return only the physical filename for a discovered mod."""
    return os.path.basename(get_mod_path(mod))


def get_mod_metadata(mod):
    """Return a copy of metadata associated with a discovered mod."""
    return dict(mod_metadata.get(mod, {}))


# A nested directory is considered a real Minify mod only when its root contains
# one of Minify's own control/payload markers. This prevents recursive scanning
# from turning internal asset folders into separate selectable mods.
DIRECTORY_MOD_MARKER_FILES = {
    "manifest.json",
    "blacklist.txt",
    "styling.css",
    "xml.json",
    "replacer.json",
    "menu.xml",
    "d2pfx-manifest.json",
}
DIRECTORY_MOD_MARKER_DIRS = {"files", "files_uncompiled"}
COLLECTION_MARKER_FILE = ".minify-collection"
AUTO_COLLECTION_MIN_CHILDREN = 8
COLLECTION_NON_PAYLOAD_FILES = {
    COLLECTION_MARKER_FILE,
    "readme",
    "readme.txt",
    "readme.md",
    "license",
    "license.txt",
    "desktop.ini",
    "thumbs.db",
}
MAX_NESTED_MOD_SCAN_DEPTH = 12
MAX_NESTED_MOD_SCAN_DIRS = 4096


def _is_hidden_or_reserved_dir(name):
    name = str(name or "")
    return not name or name.startswith(".") or name.startswith("_")


def _looks_like_directory_mod(path):
    """Return True when *path* looks like a Minify mod root, not a container."""
    if not os.path.isdir(path):
        return False
    try:
        entries = os.listdir(path)
    except OSError:
        return False

    names = {entry.casefold() for entry in entries}
    if names.intersection(DIRECTORY_MOD_MARKER_FILES):
        return True
    if names.intersection(DIRECTORY_MOD_MARKER_DIRS):
        return True
    return any(name.startswith("script_") and name.endswith(".py") for name in names) or "script.py" in names


def _visible_child_directories(path):
    """Return safe immediate child directories in deterministic order."""
    children = []
    try:
        entries = sorted(os.listdir(path), key=str.casefold)
    except OSError:
        return children
    for name in entries:
        if _is_hidden_or_reserved_dir(name):
            continue
        child_path = os.path.join(path, name)
        if os.path.islink(child_path) or not os.path.isdir(child_path):
            continue
        children.append(child_path)
    return children


def _has_explicit_collection_marker(path):
    return os.path.isfile(os.path.join(path, COLLECTION_MARKER_FILE))


def _looks_like_directory_collection(path):
    """Return True when *path* is an organizational collection, not a mod.

    Small/ambiguous collections can opt in with ``.minify-collection``. Large
    markerless folders are auto-detected only when they contain many immediate
    child directories and no parent-level payload files. This keeps ordinary
    rc6-style markerless mods from being split into their internal asset dirs.
    """
    if not os.path.isdir(path) or _looks_like_directory_mod(path):
        return False

    children = _visible_child_directories(path)
    if not children:
        return False
    if _has_explicit_collection_marker(path):
        return True
    if len(children) < AUTO_COLLECTION_MIN_CHILDREN:
        return False

    try:
        entries = os.listdir(path)
    except OSError:
        return False
    for name in entries:
        child_path = os.path.join(path, name)
        if os.path.isdir(child_path):
            continue
        if name.casefold() in COLLECTION_NON_PAYLOAD_FILES:
            continue
        # Any other parent-level file makes this ambiguous, so preserve rc6's
        # legacy behavior and keep the parent as one mod.
        return False
    return True


def _discover_collection_child_roots(container_path):
    """Return selectable immediate children of a collection folder.

    Immediate children are intentionally treated as legacy mod roots even when
    markerless. We do not recursively split their internal asset directories.
    An explicitly marked child collection may contain another organizational
    layer and is expanded recursively.
    """
    discovered = []
    for child_path in _visible_child_directories(container_path):
        if _has_explicit_collection_marker(child_path):
            discovered.extend(_discover_collection_child_roots(child_path))
        else:
            discovered.append(child_path)
    return discovered


def _nested_directory_mod_id(path):
    relative = os.path.relpath(path, base.mods_dir).replace(os.sep, "/")
    if "/" not in relative:
        return os.path.basename(path)
    return f"{NESTED_DIR_PREFIX}{relative}"


def _nested_directory_group(path):
    relative = os.path.relpath(path, base.mods_dir).replace(os.sep, "/")
    parent = relative.rsplit("/", 1)[0] if "/" in relative else ""
    return parent


def _discover_nested_directory_roots(container_path):
    """Find mod roots below an organizational folder, stopping at each mod root."""
    discovered = []
    seen = set()
    visited = 0

    def walk(current, depth=0):
        nonlocal visited
        if depth > MAX_NESTED_MOD_SCAN_DEPTH or visited >= MAX_NESTED_MOD_SCAN_DIRS:
            return
        try:
            real_current = os.path.normcase(os.path.realpath(current))
        except (OSError, ValueError):
            return
        if real_current in seen:
            return
        seen.add(real_current)
        visited += 1

        try:
            children = sorted(os.listdir(current), key=str.casefold)
        except OSError:
            return
        for child in children:
            if _is_hidden_or_reserved_dir(child):
                continue
            child_path = os.path.join(current, child)
            if os.path.islink(child_path) or not os.path.isdir(child_path):
                continue
            if _looks_like_directory_mod(child_path):
                discovered.append(child_path)
                continue
            walk(child_path, depth + 1)

    walk(container_path)
    return discovered


def _discover_directory_mod_entries():
    """Return ``(mod_id, path)`` pairs for top-level and nested directory mods.

    Existing top-level behavior is preserved. A top-level directory becomes an
    organizational collection when explicitly marked, when it is a large
    markerless sibling collection, or when recognized nested mod roots exist.
    """
    entries = []
    try:
        top_level = sorted(os.listdir(base.mods_dir), key=str.casefold)
    except OSError:
        return entries

    for name in top_level:
        if _is_hidden_or_reserved_dir(name):
            continue
        path = os.path.join(base.mods_dir, name)
        if os.path.islink(path) or not os.path.isdir(path):
            continue

        if _looks_like_directory_mod(path):
            entries.append((name, path))
            continue

        if _looks_like_directory_collection(path):
            children = _discover_collection_child_roots(path)
            entries.extend((_nested_directory_mod_id(mod_path), mod_path) for mod_path in children)
            continue

        nested = _discover_nested_directory_roots(path)
        if nested:
            entries.extend((_nested_directory_mod_id(mod_path), mod_path) for mod_path in nested)
        else:
            # Backward compatibility: rc6 treated every ordinary top-level
            # directory as a mod, even if it had no recognizable marker files.
            entries.append((name, path))

    return entries


def get_mod_id_for_path(path):
    """Return the discovered stable ID for a physical mod directory/file path."""
    try:
        target = os.path.normcase(os.path.abspath(path))
    except (TypeError, ValueError):
        return None
    for mod_id, mod_path in mod_paths.items():
        try:
            if os.path.normcase(os.path.abspath(mod_path)) == target:
                return mod_id
        except (TypeError, ValueError):
            continue
    return None


def resolve_mod_reference(reference, relative_to=None):
    """Resolve a manifest dependency/conflict name to a discovered mod ID.

    Exact IDs win. For nested mods, a sibling folder name is preferred, then a
    unique display/physical basename match. Ambiguous names are left unchanged.
    """
    reference = str(reference or "").strip()
    if not reference or reference in mod_paths:
        return reference

    if relative_to in mod_paths:
        owner_dir = os.path.dirname(mod_paths[relative_to])
        candidate = os.path.abspath(os.path.join(owner_dir, reference))
        try:
            root = os.path.abspath(base.mods_dir)
            if os.path.commonpath([root, candidate]) == root:
                matched = get_mod_id_for_path(candidate)
                if matched:
                    return matched
        except (ValueError, OSError):
            pass

    folded = reference.casefold()
    matches = []
    for mod_id, mod_path in mod_paths.items():
        label = str(mod_labels.get(mod_id, "")).casefold()
        basename = os.path.basename(mod_path).casefold()
        if folded in {label, basename, mod_id.casefold()}:
            matches.append(mod_id)
    return matches[0] if len(matches) == 1 else reference


def get_mod_source(mod):
    return str(mod_metadata.get(mod, {}).get("source", "")).strip()


def is_mod_identified(mod):
    if not mod.lower().endswith(".vpk"):
        return True
    return bool(mod_metadata.get(mod, {}).get("identified", False))


def _normalize_metadata(value, fallback_name=""):
    if isinstance(value, str):
        metadata = {"display_name": value}
    elif isinstance(value, dict):
        metadata = dict(value)
    else:
        return {}

    if not metadata.get("display_name"):
        metadata["display_name"] = metadata.get("name") or fallback_name

    display_name = str(metadata.get("display_name", "")).strip()
    if display_name:
        metadata["display_name"] = display_name
    else:
        metadata.pop("display_name", None)

    category = str(metadata.get("category", "")).strip()
    if category:
        metadata["category"] = category
    else:
        metadata.pop("category", None)

    source = str(metadata.get("source", "")).strip()
    if source:
        metadata["source"] = source
    else:
        metadata.pop("source", None)

    return metadata


def _parse_mods_txt(path):
    """Parse Dota2PornFxWeb's human-readable Mods.txt mapping."""
    mappings = {}
    current_category = ""
    mapping_pattern = re.compile(r"^\s*[•*\-]\s*(.+?)\s*(?:➜|->|=>)\s*(.+?)\s*$")

    try:
        with open(path, encoding="utf-8-sig", errors="replace") as file:
            for raw_line in file:
                line = raw_line.strip()
                if not line:
                    continue

                category_match = re.match(r"^(.+?):$", line)
                if category_match:
                    candidate = category_match.group(1).strip()
                    if candidate.casefold() not in {"total mods", "generated"}:
                        current_category = candidate
                    continue

                match = mapping_pattern.match(raw_line)
                if not match:
                    continue

                display_name = match.group(1).strip()
                file_names = [
                    os.path.basename(item.strip())
                    for item in match.group(2).split(",")
                    if item.strip().lower().endswith(".vpk")
                ]
                part_count = len(file_names)

                for part_index, file_name in enumerate(file_names, start=1):
                    metadata = {
                        "display_name": display_name,
                        "source": "Dota2PornFxWeb Mods.txt",
                        "part_index": part_index,
                        "part_count": part_count,
                        "identified": True,
                    }
                    if current_category:
                        metadata["category"] = current_category
                    mappings[file_name.casefold()] = metadata
    except Exception:
        return {}

    return mappings


def _add_manifest_file_mapping(mappings, file_name, value, defaults=None):
    if not isinstance(file_name, str) or not file_name.lower().endswith(".vpk"):
        return

    metadata = _normalize_metadata(value)
    if defaults:
        merged = dict(defaults)
        merged.update(metadata)
        metadata = _normalize_metadata(merged)

    if metadata:
        metadata["identified"] = True
        mappings[os.path.basename(file_name).casefold()] = metadata


def _parse_d2pfx_manifest(path):
    """Read a flexible d2pfx-manifest.json file."""
    try:
        with open(path, encoding="utf-8-sig") as file:
            data = json.load(file)
    except Exception:
        return {}

    if not isinstance(data, dict):
        return {}

    mappings = {}

    files = data.get("files")
    if isinstance(files, dict):
        for file_name, value in files.items():
            _add_manifest_file_mapping(mappings, file_name, value)

    mods = data.get("mods")
    if isinstance(mods, list):
        for mod in mods:
            if not isinstance(mod, dict):
                continue

            display_name = mod.get("display_name") or mod.get("name") or ""
            defaults = {
                "display_name": display_name,
                "category": mod.get("category", ""),
                "source": mod.get("source", "Dota2PornFxWeb manifest"),
            }
            mod_files = mod.get("files")
            if isinstance(mod_files, str):
                mod_files = [mod_files]
            if not isinstance(mod_files, list):
                single_file = mod.get("file")
                mod_files = [single_file] if isinstance(single_file, str) else []

            part_count = len(mod_files)
            for part_index, file_name in enumerate(mod_files, start=1):
                part_defaults = dict(defaults)
                part_defaults["part_index"] = part_index
                part_defaults["part_count"] = part_count
                _add_manifest_file_mapping(mappings, file_name, {}, part_defaults)

    for file_name, value in data.items():
        if isinstance(file_name, str) and file_name.lower().endswith(".vpk"):
            _add_manifest_file_mapping(mappings, file_name, value)

    return mappings


def _discover_pack_metadata_maps(collection_path):
    """Collect Mods.txt/manifest mappings once per scan."""
    pack_maps = []
    if not os.path.isdir(collection_path):
        return pack_maps

    for current_root, directories, files in os.walk(collection_path):
        directories[:] = sorted(
            (directory for directory in directories if not directory.startswith(".")),
            key=str.casefold,
        )

        file_lookup = {file_name.casefold(): file_name for file_name in files}
        mappings = {}

        mods_txt_name = file_lookup.get(D2PFX_MODS_LIST_FILE.casefold())
        if mods_txt_name:
            mappings.update(_parse_mods_txt(os.path.join(current_root, mods_txt_name)))

        manifest_name = file_lookup.get(D2PFX_MANIFEST_FILE.casefold())
        if manifest_name:
            mappings.update(_parse_d2pfx_manifest(os.path.join(current_root, manifest_name)))

        if mappings:
            pack_maps.append((os.path.normcase(os.path.abspath(current_root)), mappings))

    pack_maps.sort(key=lambda item: len(item[0]), reverse=True)
    return pack_maps


def _path_is_within(path, parent):
    try:
        return os.path.commonpath((path, parent)) == parent
    except (ValueError, OSError):
        return False


def _find_pack_metadata(vpk_path, pack_maps):
    normalized_path = os.path.normcase(os.path.abspath(vpk_path))
    file_key = os.path.basename(vpk_path).casefold()

    for pack_root, mappings in pack_maps:
        if _path_is_within(normalized_path, pack_root):
            metadata = mappings.get(file_key)
            if metadata:
                return dict(metadata)

    return {}


def _identity_db_path():
    return os.path.join(base.config_dir, VPK_IDENTITY_DB_FILE)


def _load_identity_db():
    path = _identity_db_path()
    try:
        with open(path, encoding="utf-8-sig") as file:
            data = json.load(file)
    except Exception:
        return {}

    if not isinstance(data, dict):
        return {}

    identities = data.get("identities", data)
    if not isinstance(identities, dict):
        return {}

    normalized = {}
    for fingerprint, value in identities.items():
        if not isinstance(fingerprint, str):
            continue
        metadata = _normalize_metadata(value)
        if metadata:
            metadata["identified"] = True
            normalized[fingerprint.casefold()] = metadata
    return normalized


def _hash_cache_path():
    return os.path.join(base.config_dir, VPK_HASH_CACHE_FILE)


def _load_hash_cache():
    try:
        with open(_hash_cache_path(), encoding="utf-8-sig") as file:
            data = json.load(file)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save_hash_cache(cache):
    os.makedirs(base.config_dir, exist_ok=True)
    path = _hash_cache_path()
    fd, temporary = tempfile.mkstemp(prefix=".minify-hash-cache-", suffix=".tmp", dir=base.config_dir)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as file:
            json.dump(cache, file, indent=2, ensure_ascii=False, sort_keys=True)
        os.replace(temporary, path)
    except Exception:
        try:
            os.remove(temporary)
        except FileNotFoundError:
            pass
        raise


def _sha256_file(path):
    """SHA-256 with a size/mtime cache so Refresh Mods does not rehash large VPKs."""
    try:
        stat = os.stat(path)
        size = int(stat.st_size)
        mtime_ns = int(getattr(stat, "st_mtime_ns", int(stat.st_mtime * 1_000_000_000)))
        cache_key = os.path.normcase(os.path.abspath(path))
        cache = _load_hash_cache()
        cached = cache.get(cache_key, {})
        if (
            isinstance(cached, dict)
            and cached.get("size") == size
            and cached.get("mtime_ns") == mtime_ns
            and cached.get("sha256")
        ):
            return str(cached["sha256"]).casefold()
    except Exception:
        return ""

    digest = hashlib.sha256()
    try:
        with open(path, "rb") as file:
            while True:
                chunk = file.read(4 * 1024 * 1024)
                if not chunk:
                    break
                digest.update(chunk)
    except Exception:
        return ""

    fingerprint = digest.hexdigest().casefold()
    try:
        cache[cache_key] = {"size": size, "mtime_ns": mtime_ns, "sha256": fingerprint}
        _save_hash_cache(cache)
    except Exception:
        pass
    return fingerprint


def get_mod_fingerprint(mod):
    """Return a stable SHA-256 for a VPK mod, cached by file size + mtime."""
    if not str(mod).lower().endswith(".vpk"):
        return ""
    return _sha256_file(get_mod_path(mod))


def _save_identity_db(identities):
    os.makedirs(base.config_dir, exist_ok=True)
    payload = {"schema_version": 1, "identities": identities}
    path = _identity_db_path()
    fd, temporary = tempfile.mkstemp(prefix=".minify-identities-", suffix=".tmp", dir=base.config_dir)
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


def register_identity_for_path(vpk_path, metadata):
    """Persist human-readable VPK metadata by content hash and sidecar."""
    if not os.path.isfile(vpk_path):
        return ""
    fingerprint = _sha256_file(vpk_path)
    if not fingerprint:
        return ""

    normalized = _normalize_metadata(metadata)
    if not normalized.get("display_name"):
        return ""
    normalized["identified"] = True
    normalized["fingerprint"] = fingerprint

    identities = _load_identity_db()
    identities[fingerprint] = normalized
    _save_identity_db(identities)

    sidecar_path = f"{vpk_path}.minify.json"
    try:
        with open(sidecar_path, "w", encoding="utf-8", newline="\n") as file:
            json.dump(normalized, file, indent=2, ensure_ascii=False)
    except Exception:
        pass
    return fingerprint


def update_vpk_identity(mod, display_name, category="", source="Manual", pack_name=""):
    """Update identity metadata for a discovered VPK and refresh in-memory labels."""
    path = get_mod_path(mod)
    metadata = {
        "display_name": str(display_name).strip(),
        "category": str(category).strip(),
        "source": str(source).strip() or "Manual",
        "identified": True,
    }
    if pack_name:
        metadata["pack_name"] = str(pack_name).strip()
    fingerprint = register_identity_for_path(path, metadata)
    if not fingerprint:
        return False

    normalized = _finalize_vpk_metadata(path, metadata, str(category).strip())
    mod_metadata[mod] = normalized
    mod_labels[mod] = _vpk_label(path, normalized)
    mod_groups[mod] = str(normalized.get("category", "")).strip()
    return True


def parse_mods_txt(path):
    """Public wrapper for the Dota2PornFxWeb Mods.txt parser."""
    return _parse_mods_txt(path)


def _lookup_identity_metadata(vpk_path, identity_db):
    if not identity_db:
        return {}

    fingerprint = _sha256_file(vpk_path)
    if not fingerprint:
        return {}

    metadata = identity_db.get(fingerprint)
    if not metadata:
        return {}

    result = dict(metadata)
    result["identified"] = True
    result["fingerprint"] = fingerprint
    result.setdefault("source", "Minify VPK identity database")
    return result


def _load_vpk_metadata(vpk_path, pack_maps, identity_db):
    """Resolve metadata from pack files, sidecar, then persistent SHA-256 identity DB."""
    metadata = _find_pack_metadata(vpk_path, pack_maps)
    sidecar_path = f"{vpk_path}.minify.json"

    try:
        with open(sidecar_path, encoding="utf-8-sig") as file:
            sidecar = json.load(file)
            if isinstance(sidecar, dict):
                metadata.update(sidecar)
                metadata["identified"] = True
    except Exception:
        pass

    metadata = _normalize_metadata(metadata)
    if metadata.get("display_name"):
        metadata["identified"] = True
        return metadata

    identity_metadata = _lookup_identity_metadata(vpk_path, identity_db)
    if identity_metadata:
        metadata.update(identity_metadata)
        metadata = _normalize_metadata(metadata)
        metadata["identified"] = True

    return metadata


def _is_generic_pak_name(path):
    stem = os.path.splitext(os.path.basename(path))[0]
    return re.fullmatch(r"!?pak\d+_dir", stem, flags=re.IGNORECASE) is not None


def _vpk_label(vpk_path, metadata):
    display_name = str(metadata.get("display_name", "")).strip()
    if not display_name:
        display_name = os.path.splitext(os.path.basename(vpk_path))[0]

    part_count = metadata.get("part_count")
    part_index = metadata.get("part_index")
    if isinstance(part_count, int) and part_count > 1 and isinstance(part_index, int):
        display_name = f"{display_name} [{part_index}/{part_count}]"

    return display_name


def _finalize_vpk_metadata(vpk_path, metadata, relative_group=""):
    result = dict(metadata)
    identified = bool(result.get("identified") or result.get("display_name"))
    if not identified and not _is_generic_pak_name(vpk_path):
        identified = True
        result.setdefault("source", "VPK filename")

    result["identified"] = identified
    if relative_group and not result.get("category"):
        result["category"] = relative_group
    return result


def get_state(mod):
    if _get_state_callback:
        return _get_state_callback(mod)

    try:
        with utils.open_utf8(base.mods_config_dir) as file:
            states = jsonc.load(file)
            return states.get(mod, False)
    except Exception:
        return False


def set_state(mod, value):
    if _set_state_callback:
        return _set_state_callback(mod, value)

    try:
        states = {}
        if os.path.exists(base.mods_config_dir):
            with utils.open_utf8(base.mods_config_dir) as file:
                states = jsonc.load(file)

        states[mod] = value
        with utils.open_utf8(base.mods_config_dir, "w") as file:
            jsonc.dump(dict(sorted(states.items())), file, indent=2)
    except Exception:
        pass


def enforce_locale_mod_states():
    from core import config

    locale = config.get("output_locale", "english")
    for required_mod in constants.LOCALE_MOD_REQUIREMENTS.get(locale, []):
        set_state(required_mod, True)


def scan_mods():
    from patch import manifest_utils

    global \
        mods_alphabetical, \
        mods_with_order, \
        visually_unavailable_mods, \
        visually_available_mods, \
        mod_dependencies_list, \
        mod_conflicts_list, \
        mod_paths, \
        mod_labels, \
        mod_groups, \
        mod_metadata

    if not os.path.exists(base.mods_dir):
        sys.exit()

    _alphabetical = []
    _with_order = []
    _unavailable = []
    _available = []
    _dependencies = []
    _conflicts = []
    _paths = {}
    _labels = {}
    _groups = {}
    _metadata = {}

    identity_db = _load_identity_db()

    # Directory-backed mods may be organized inside arbitrary collection folders.
    # Top-level mod IDs remain unchanged; nested IDs include their relative path.
    for mod, mod_path in _discover_directory_mod_entries():
        _alphabetical.append(mod)
        _paths[mod] = mod_path

        relative_path = os.path.relpath(mod_path, base.mods_dir).replace(os.sep, "/")
        if mod.startswith(NESTED_DIR_PREFIX):
            group = _nested_directory_group(mod_path)
            label = os.path.basename(mod_path)
            _labels[mod] = label
            _groups[mod] = group
            _metadata[mod] = {
                "display_name": label,
                "category": group,
                "source": "Local folder",
                "relative_path": relative_path,
                "nested": True,
            }

        blacklist_exist = os.path.exists(os.path.join(mod_path, "blacklist.txt"))
        cfg = manifest_utils.get_mod(mod_path)
        order = cfg.get("order", 1)
        dependencies = cfg.get("dependencies", None)
        conflicts = cfg.get("conflicts", None)
        visual = cfg.get("visual", True)
        _available.append(mod) if visual else _unavailable.append(mod)
        if dependencies is not None:
            _dependencies.append({mod: dependencies})
        if conflicts is not None:
            _conflicts.append({mod: conflicts})

        if blacklist_exist and not cfg:
            _with_order.append({mod: 2})
        else:
            _with_order.append({mod: order})

    # Preserve rc6 support for loose VPKs directly inside the mods root.
    for mod in sorted(os.listdir(base.mods_dir), key=str.casefold):
        mod_path = os.path.join(base.mods_dir, mod)
        if mod.startswith("_") or not os.path.isfile(mod_path) or not mod.lower().endswith(".vpk"):
            continue
        metadata = _finalize_vpk_metadata(
            mod_path,
            _load_vpk_metadata(mod_path, [], identity_db),
        )
        _alphabetical.append(mod)
        _available.append(mod)
        _with_order.append({mod: 1})
        _paths[mod] = mod_path
        _labels[mod] = _vpk_label(mod_path, metadata)
        _groups[mod] = str(metadata.get("category", "")).strip()
        _metadata[mod] = metadata

    vpk_collection_path = os.path.join(base.mods_dir, VPK_COLLECTION_DIR)
    pack_maps = _discover_pack_metadata_maps(vpk_collection_path)

    if os.path.isdir(vpk_collection_path):
        for current_root, directories, files in os.walk(vpk_collection_path):
            directories[:] = sorted(
                (directory for directory in directories if not directory.startswith(".")),
                key=str.casefold,
            )

            for file_name in sorted(files, key=str.casefold):
                if not file_name.lower().endswith(".vpk"):
                    continue

                mod_path = os.path.join(current_root, file_name)
                relative_path = os.path.relpath(mod_path, vpk_collection_path).replace(os.sep, "/")
                mod_id = f"{NESTED_VPK_PREFIX}{relative_path}"
                relative_parent = os.path.dirname(relative_path).replace("\\", "/")
                metadata = _finalize_vpk_metadata(
                    mod_path,
                    _load_vpk_metadata(mod_path, pack_maps, identity_db),
                    relative_parent,
                )

                _alphabetical.append(mod_id)
                _available.append(mod_id)
                _with_order.append({mod_id: 1})
                _paths[mod_id] = mod_path
                _labels[mod_id] = _vpk_label(mod_path, metadata)
                _groups[mod_id] = str(metadata.get("category") or relative_parent).strip()
                _metadata[mod_id] = metadata

    def mod_order_key(item):
        mod_id = list(item.keys())[0]
        order = list(item.values())[0]

        if mod_id.lower().endswith(".vpk"):
            file_name = os.path.basename(_paths.get(mod_id, mod_id)).casefold()
            match = re.match(r"!?pak(\d+)_dir\.vpk$", file_name)
            pak_number = int(match.group(1)) if match else 1000
            bang_priority = 0 if file_name.startswith("!") else 1
            return order, 0, pak_number, bang_priority, _labels.get(mod_id, file_name).casefold()

        return order, 1, _labels.get(mod_id, mod_id).casefold()

    temp_sorted = sorted(_with_order, key=mod_order_key)
    _with_order = [list(item.keys())[0] for item in temp_sorted]

    mods_alphabetical[:] = sorted(
        _alphabetical,
        key=lambda mod: _labels.get(mod, mod).casefold(),
    )
    mods_with_order[:] = _with_order
    visually_unavailable_mods[:] = _unavailable
    visually_available_mods[:] = _available
    mod_dependencies_list[:] = _dependencies
    mod_conflicts_list[:] = _conflicts
    mod_paths.clear()
    mod_paths.update(_paths)
    mod_labels.clear()
    mod_labels.update(_labels)
    mod_groups.clear()
    mod_groups.update(_groups)
    mod_metadata.clear()
    mod_metadata.update(_metadata)
