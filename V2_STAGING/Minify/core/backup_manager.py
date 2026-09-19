"""Transactional backup/restore for files managed by Minify."""

from __future__ import annotations

import datetime as dt
import json
import os
import shutil
import stat
import tempfile

from core import base, constants, security

BACKUP_DIR_NAME = "backups"
MAX_BACKUPS = 10
MAX_MANIFEST_BYTES = 256 * 1024
MANAGED_OUTPUTS = (
    "pak65_dir.vpk",
    "pak66_dir.vpk",
    "pak67_dir.vpk",
    os.path.join("maps", "dota.vpk"),
)
_MANAGED_CANONICAL = {path.replace(os.sep, "/") for path in MANAGED_OUTPUTS}


def _root() -> str:
    return os.path.abspath(os.path.join(base.config_dir, BACKUP_DIR_NAME))


def _manifest_path(snapshot: str) -> str:
    return os.path.join(snapshot, "manifest.json")


def _atomic_json_write(path: str, payload: dict) -> None:
    directory = os.path.dirname(os.path.abspath(path))
    os.makedirs(directory, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".minify-manifest-", suffix=".tmp", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as file:
            json.dump(payload, file, indent=2, ensure_ascii=False)
        os.replace(temporary, path)
    except Exception:
        try:
            os.remove(temporary)
        except FileNotFoundError:
            pass
        raise


def _write_manifest(snapshot: str, manifest: dict) -> None:
    snapshot = _validated_snapshot(snapshot, require_exists=False)
    os.makedirs(snapshot, exist_ok=True)
    _atomic_json_write(_manifest_path(snapshot), manifest)


def _read_manifest(snapshot: str) -> dict:
    fd = None
    try:
        path = _manifest_path(snapshot)
        before = os.stat(path, follow_symlinks=False)
        if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_MANIFEST_BYTES:
            return {}

        flags = os.O_RDONLY
        if hasattr(os, "O_BINARY"):
            flags |= os.O_BINARY
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        fd = os.open(path, flags)
        opened = os.fstat(fd)
        if not stat.S_ISREG(opened.st_mode) or opened.st_size > MAX_MANIFEST_BYTES:
            return {}
        if (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino):
            return {}

        with os.fdopen(fd, "r", encoding="utf-8-sig") as file:
            fd = None
            data = json.load(file)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}
    finally:
        if fd is not None:
            try:
                os.close(fd)
            except OSError:
                pass


def _copy_if_exists(source: str, destination: str) -> bool:
    if not os.path.isfile(source) or os.path.islink(source):
        return False
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    shutil.copy2(source, destination)
    return True


def _validated_snapshot(snapshot: str, *, require_exists: bool = True) -> str:
    original = os.path.abspath(snapshot)
    if os.path.lexists(original) and os.path.islink(original):
        raise ValueError("Backup snapshot cannot be a symlink.")
    root = os.path.realpath(_root())
    candidate = os.path.realpath(original)
    try:
        common = os.path.commonpath((root, candidate))
    except ValueError as exc:
        raise ValueError("Backup snapshot is outside Minify's backup root.") from exc
    if common != root or candidate == root:
        raise ValueError("Backup snapshot is outside Minify's backup root.")
    if require_exists and not os.path.isdir(candidate):
        raise FileNotFoundError("Backup snapshot does not exist.")
    if os.path.dirname(candidate) != root:
        raise ValueError("Backup snapshot has an invalid location.")
    return candidate


def _validated_output_path(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Backup does not contain a valid output path.")
    candidate_real = os.path.realpath(os.path.abspath(value))
    candidate = os.path.normcase(candidate_real)
    try:
        allowed = {}
        for path in constants.minify_dota_possible_language_output_paths:
            resolved = os.path.realpath(os.path.abspath(path))
            allowed[os.path.normcase(resolved)] = resolved
    except Exception as exc:
        raise RuntimeError("Could not resolve Minify's allowed output locations.") from exc
    if candidate not in allowed:
        raise ValueError("Backup output path is not a Minify-managed Dota language output directory.")
    return allowed[candidate]


def _managed_output_path(output_path: str, relative: str) -> str:
    canonical = str(relative).replace("\\", "/").strip("/")
    if canonical not in _MANAGED_CANONICAL:
        raise ValueError(f"Unmanaged output path: {relative!r}")
    _, destination = security.confined_destination(output_path, canonical)
    return destination


def _validated_manifest_outputs(value) -> list[str]:
    if not isinstance(value, list):
        raise ValueError("Backup managed-output list is invalid.")
    if len(value) > len(MANAGED_OUTPUTS):
        raise ValueError("Backup contains too many managed outputs.")
    result: list[str] = []
    seen = set()
    for item in value:
        if not isinstance(item, str):
            raise ValueError("Backup managed-output entry is invalid.")
        canonical = item.replace("\\", "/").strip("/")
        if canonical not in _MANAGED_CANONICAL:
            raise ValueError(f"Backup references an unmanaged output: {item!r}")
        if canonical not in seen:
            result.append(canonical)
            seen.add(canonical)
    return result


def _validated_selection_path() -> str:
    destination = os.path.abspath(getattr(base, "mods_config_dir", os.path.join(base.config_dir, "mods.json")))
    config_root = os.path.realpath(os.path.abspath(base.config_dir))
    parent_real = os.path.realpath(os.path.dirname(destination))
    try:
        common = os.path.commonpath((config_root, parent_real))
    except ValueError as exc:
        raise ValueError("Mod-selection restore path is outside Minify's config directory.") from exc
    if common != config_root:
        raise ValueError("Mod-selection restore path is outside Minify's config directory.")
    return destination


def create_restore_point(output_path: str, selected_mods=None, reason="pre-patch") -> str:
    output_path = _validated_output_path(output_path)
    live_paths = {
        relative.replace(os.sep, "/"): _managed_output_path(output_path, relative) for relative in MANAGED_OUTPUTS
    }
    os.makedirs(_root(), exist_ok=True)
    now = dt.datetime.now().astimezone()
    stamp = now.strftime("%Y%m%d-%H%M%S-%f")
    snapshot = os.path.join(_root(), stamp)
    os.makedirs(snapshot, exist_ok=False)

    existing = []
    for relative in MANAGED_OUTPUTS:
        source = live_paths[relative.replace(os.sep, "/")]
        destination = os.path.join(snapshot, "output", relative)
        if _copy_if_exists(source, destination):
            existing.append(relative.replace(os.sep, "/"))

    mods_config = _validated_selection_path()
    _copy_if_exists(mods_config, os.path.join(snapshot, "config", "mods.json"))

    manifest = {
        "schema_version": 1,
        "created": now.isoformat(timespec="seconds"),
        "reason": str(reason)[:128],
        "status": "created",
        "output_path": os.path.abspath(output_path),
        "existing_managed_outputs": existing,
        "selected_mods": [str(item)[:512] for item in list(selected_mods or [])[:5000]],
    }
    _write_manifest(snapshot, manifest)
    prune_backups()
    return snapshot


def mark_success(snapshot: str) -> None:
    snapshot = _validated_snapshot(snapshot)
    manifest = _read_manifest(snapshot)
    if not manifest:
        return
    manifest["status"] = "successful patch"
    manifest["completed"] = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    _write_manifest(snapshot, manifest)


def mark_rolled_back(snapshot: str, error="") -> None:
    snapshot = _validated_snapshot(snapshot)
    manifest = _read_manifest(snapshot)
    if not manifest:
        return
    manifest["status"] = "rolled back"
    manifest["rollback_time"] = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    if error:
        manifest["error"] = str(error)[:4096]
    _write_manifest(snapshot, manifest)


def _atomic_copy(source: str, destination: str) -> None:
    directory = os.path.dirname(os.path.abspath(destination))
    os.makedirs(directory, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".minify-restore-", suffix=".tmp", dir=directory)
    os.close(fd)
    try:
        shutil.copy2(source, temporary)
        os.replace(temporary, destination)
    except Exception:
        try:
            os.remove(temporary)
        except FileNotFoundError:
            pass
        raise


def restore_restore_point(snapshot: str, restore_selection=True) -> dict:
    snapshot = _validated_snapshot(snapshot)
    manifest = _read_manifest(snapshot)
    if not manifest:
        raise FileNotFoundError("Backup manifest is missing or unreadable.")
    if manifest.get("schema_version") != 1:
        raise ValueError("Backup schema version is unsupported.")

    output_path = _validated_output_path(manifest.get("output_path"))
    existing = _validated_manifest_outputs(manifest.get("existing_managed_outputs", []))
    live_paths = {
        relative.replace(os.sep, "/"): _managed_output_path(output_path, relative) for relative in MANAGED_OUTPUTS
    }

    sources: dict[str, str] = {}
    for canonical in existing:
        _, source = security.confined_destination(snapshot, f"output/{canonical}")
        if not os.path.isfile(source) or os.path.islink(source):
            raise FileNotFoundError(f"Backup payload is missing: {canonical}")
        sources[canonical] = source

    selection_source = None
    selection_destination = None
    if restore_selection:
        _, candidate = security.confined_destination(snapshot, "config/mods.json")
        if os.path.lexists(candidate) and os.path.islink(candidate):
            raise ValueError("Backup selection payload cannot be a symlink.")
        if os.path.isfile(candidate):
            selection_source = candidate
            selection_destination = _validated_selection_path()

    os.makedirs(output_path, exist_ok=True)
    transaction = tempfile.mkdtemp(prefix=".minify-restore-", dir=output_path)
    staged_new = os.path.join(transaction, "new")
    staged_old = os.path.join(transaction, "old")
    os.makedirs(staged_new)
    os.makedirs(staged_old)

    selection_transaction = None
    selection_new = None
    selection_old = None
    selection_existed = False
    if selection_source and selection_destination:
        selection_parent = os.path.dirname(selection_destination)
        os.makedirs(selection_parent, exist_ok=True)
        selection_transaction = tempfile.mkdtemp(prefix=".minify-selection-restore-", dir=selection_parent)
        selection_new = os.path.join(selection_transaction, "new.json")
        selection_old = os.path.join(selection_transaction, "old.json")

    try:
        for canonical, source in sources.items():
            relative = canonical.replace("/", os.sep)
            destination = os.path.join(staged_new, relative)
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            shutil.copy2(source, destination)
        for relative in MANAGED_OUTPUTS:
            current = live_paths[relative.replace(os.sep, "/")]
            if os.path.isfile(current) and not os.path.islink(current):
                old = os.path.join(staged_old, relative)
                os.makedirs(os.path.dirname(old), exist_ok=True)
                shutil.copy2(current, old)

        if selection_source and selection_new and selection_destination:
            shutil.copy2(selection_source, selection_new)
            if os.path.isfile(selection_destination) and not os.path.islink(selection_destination):
                shutil.copy2(selection_destination, selection_old)
                selection_existed = True
            elif os.path.lexists(selection_destination) and os.path.islink(selection_destination):
                raise ValueError("Live mod-selection file cannot be a symlink during restore.")

        restored: list[str] = []
        selection_restored = False
        selection_touched = False
        try:
            for relative in MANAGED_OUTPUTS:
                current = live_paths[relative.replace(os.sep, "/")]
                if os.path.isfile(current) or os.path.islink(current):
                    os.remove(current)
            for canonical in existing:
                relative = canonical.replace("/", os.sep)
                source = os.path.join(staged_new, relative)
                destination = live_paths[canonical]
                os.makedirs(os.path.dirname(destination), exist_ok=True)
                os.replace(source, destination)
                restored.append(canonical)

            if selection_source and selection_new and selection_destination:
                selection_touched = True
                os.replace(selection_new, selection_destination)
                selection_restored = True
        except Exception:
            for relative in MANAGED_OUTPUTS:
                current = live_paths[relative.replace(os.sep, "/")]
                if os.path.isfile(current) or os.path.islink(current):
                    os.remove(current)
                old = os.path.join(staged_old, relative)
                if os.path.isfile(old):
                    os.makedirs(os.path.dirname(current), exist_ok=True)
                    os.replace(old, current)
            if selection_touched and selection_destination:
                if os.path.isfile(selection_destination) or os.path.islink(selection_destination):
                    os.remove(selection_destination)
                if selection_existed and selection_old and os.path.isfile(selection_old):
                    os.replace(selection_old, selection_destination)
            raise

        manifest["last_restored"] = dt.datetime.now().astimezone().isoformat(timespec="seconds")
        _write_manifest(snapshot, manifest)
        return {"restored": restored, "selection_restored": selection_restored, "output_path": output_path}
    finally:
        shutil.rmtree(transaction, ignore_errors=True)
        if selection_transaction:
            shutil.rmtree(selection_transaction, ignore_errors=True)


def list_restore_points() -> list[dict]:
    root = _root()
    if not os.path.isdir(root):
        return []
    results = []
    for name in sorted(os.listdir(root), reverse=True):
        path = os.path.join(root, name)
        if not os.path.isdir(path) or os.path.islink(path):
            continue
        try:
            path = _validated_snapshot(path)
        except (ValueError, FileNotFoundError):
            continue
        manifest = _read_manifest(path)
        if not manifest:
            continue
        item = dict(manifest)
        item["path"] = path
        item["id"] = name
        results.append(item)
    return results


def prune_backups(max_backups=MAX_BACKUPS) -> None:
    try:
        limit = max(0, min(int(max_backups), 100))
    except (TypeError, ValueError):
        limit = MAX_BACKUPS
    points = list_restore_points()
    for item in points[limit:]:
        path = item.get("path")
        try:
            path = _validated_snapshot(path)
        except (ValueError, FileNotFoundError, TypeError):
            continue
        shutil.rmtree(path, ignore_errors=True)
