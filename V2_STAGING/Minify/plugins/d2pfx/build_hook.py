import os
import stat
import tempfile

import helper
import vpk
from core import base, constants, fs, log, mods_shared, output, security, utils
from patch import manifest_utils, vpk_utils

from . import __main__ as plugin_main

CURSOR_EXTENSIONS = {".ani", ".bmp", ".cur", ".res", ".png", ".jpg", ".jpeg"}
CURSOR_MAX_FILES = 512
CURSOR_MAX_FILE_BYTES = 64 * 1024 * 1024
CURSOR_MAX_TOTAL_BYTES = 256 * 1024 * 1024


def _relative_under(root: str, path: str) -> str:
    root_abs = os.path.abspath(root)
    path_abs = os.path.abspath(path)
    relative = os.path.relpath(path_abs, root_abs).replace(os.sep, "/")
    return security.safe_relative_path(relative)


def _regular_file_stat(root: str, path: str):
    relative = _relative_under(root, path)
    _, confined = security.confined_destination(root, relative)
    info = os.stat(confined, follow_symlinks=False)
    if not stat.S_ISREG(info.st_mode):
        raise ValueError(f"Path is not a regular file: {confined}")
    return confined, info


def _atomic_copy_regular_file(
    source: str,
    destination: str,
    *,
    source_root: str,
    destination_root: str,
    max_bytes: int = CURSOR_MAX_FILE_BYTES,
) -> None:
    source, source_info = _regular_file_stat(source_root, source)
    if source_info.st_size > max_bytes:
        raise ValueError(f"Cursor file exceeds the {max_bytes}-byte safety limit: {source}")

    destination_relative = _relative_under(destination_root, destination)
    _, destination = security.confined_destination(destination_root, destination_relative)
    parent = os.path.dirname(destination)
    os.makedirs(parent, exist_ok=True)
    _, destination = security.confined_destination(destination_root, destination_relative)

    if os.path.lexists(destination):
        destination_info = os.stat(destination, follow_symlinks=False)
        if not stat.S_ISREG(destination_info.st_mode):
            raise ValueError(f"Cursor destination is not a regular file: {destination}")

    flags = os.O_RDONLY
    if hasattr(os, "O_BINARY"):
        flags |= os.O_BINARY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW

    source_fd = os.open(source, flags)
    temporary = None
    try:
        opened = os.fstat(source_fd)
        if not stat.S_ISREG(opened.st_mode) or opened.st_size > max_bytes:
            raise ValueError(f"Cursor source changed during validation: {source}")

        temporary_fd, temporary = tempfile.mkstemp(prefix=".minify-cursor-", dir=parent)
        written = 0
        with os.fdopen(source_fd, "rb") as input_file, os.fdopen(temporary_fd, "wb") as output_file:
            source_fd = -1
            while True:
                chunk = input_file.read(1024 * 1024)
                if not chunk:
                    break
                written += len(chunk)
                if written > max_bytes:
                    raise ValueError(f"Cursor file exceeds the {max_bytes}-byte safety limit: {source}")
                output_file.write(chunk)

        _, destination = security.confined_destination(destination_root, destination_relative)
        if os.path.lexists(destination):
            destination_info = os.stat(destination, follow_symlinks=False)
            if not stat.S_ISREG(destination_info.st_mode):
                raise ValueError(f"Cursor destination changed to a non-regular file: {destination}")
        os.replace(temporary, destination)
        temporary = None
    finally:
        if source_fd >= 0:
            os.close(source_fd)
        if temporary:
            try:
                os.remove(temporary)
            except FileNotFoundError:
                pass


def _cursor_source_dir(mod_path: str) -> str:
    mod_root = os.path.abspath(mod_path)
    for root, dirs, _ in os.walk(mod_root, followlinks=False):
        safe_dirs = []
        for directory in dirs:
            candidate = os.path.join(root, directory)
            if os.path.islink(candidate):
                continue
            try:
                _relative_under(mod_root, candidate)
            except ValueError:
                continue
            safe_dirs.append(directory)
            if directory.casefold() == "cursor":
                return candidate
        dirs[:] = safe_dirs
    return mod_root


def _collect_cursor_files(cursor_mod_paths: list[str]) -> list[tuple[str, str, str]]:
    collected = []
    total_bytes = 0
    for mod_path in cursor_mod_paths:
        source_dir = _cursor_source_dir(mod_path)
        for root, dirs, files in os.walk(source_dir, followlinks=False):
            dirs[:] = [directory for directory in dirs if not os.path.islink(os.path.join(root, directory))]
            for filename in files:
                if os.path.splitext(filename)[1].casefold() not in CURSOR_EXTENSIONS:
                    continue
                source = os.path.join(root, filename)
                source, info = _regular_file_stat(source_dir, source)
                if info.st_size > CURSOR_MAX_FILE_BYTES:
                    raise ValueError(f"Cursor file exceeds the per-file safety limit: {source}")
                collected.append((source_dir, source, filename))
                total_bytes += info.st_size
                if len(collected) > CURSOR_MAX_FILES:
                    raise ValueError(f"Cursor selection exceeds the {CURSOR_MAX_FILES}-file safety limit.")
                if total_bytes > CURSOR_MAX_TOTAL_BYTES:
                    raise ValueError("Cursor selection exceeds the total-size safety limit.")
    return collected


def scan_d2pfx_mods(mod_list):
    pfx_high_priority = {}  # mod_name: [vpk_paths]
    pfx_normal = {}  # mod_name: [vpk_paths]
    map_vpk_paths = []
    cursor_mod_paths = []

    for mod_name in mod_list:
        if not mods_shared.get_state(mod_name):
            continue

        mod_path = mods_shared.get_mod_path(mod_name)
        if not os.path.isdir(mod_path):
            continue

        cfg = manifest_utils.get_mod(mod_path)
        if not cfg or cfg.get("browser") != "d2pfx":
            continue

        cat = cfg.get("category")
        if cat == "cursors":
            cursor_mod_paths.append(mod_path)
            continue

        vpk_files = []
        for root, dirs, files in os.walk(mod_path, followlinks=False):
            dirs[:] = [directory for directory in dirs if not os.path.islink(os.path.join(root, directory))]
            for filename in files:
                if not filename.casefold().endswith(".vpk"):
                    continue
                candidate = os.path.join(root, filename)
                try:
                    candidate, _ = _regular_file_stat(mod_path, candidate)
                except (OSError, ValueError):
                    continue
                vpk_files.append(candidate)

        if not vpk_files:
            continue

        if cat == "terrains":
            if os.path.isdir(os.path.join(mod_path, "maps")):
                map_vpk_paths.extend(vpk_files)
            else:
                pfx_normal[mod_name] = vpk_files
        elif cat in plugin_main.RENAME_CATEGORIES:
            pfx_high_priority[mod_name] = vpk_files
        else:
            pfx_normal[mod_name] = vpk_files

    return pfx_normal, pfx_high_priority, map_vpk_paths, cursor_mod_paths


def run_pre_build(mod_list):
    pfx_normal, _, map_vpk_paths, cursor_mod_paths = scan_d2pfx_mods(mod_list)

    # 1. Maps (dota.vpk)
    if map_vpk_paths:
        output.add_text("&merging_vpks")
        maps_output_dir = os.path.join(helper.output_path, "maps")
        fs.create_dirs(maps_output_dir)
        fs.remove_path(base.merge_dir)
        fs.create_dirs(base.merge_dir)

        try:
            vpk_utils.dump(vpk.open(map_vpk_paths[-1]), base.merge_dir)
        except Exception:
            log.write_warning("&failed_merge_mod", os.path.basename(map_vpk_paths[-1]))

        vpk_utils.dump_metadata(base.merge_dir)
        vpk.new(base.merge_dir).save(os.path.join(maps_output_dir, "dota.vpk"))
        fs.remove_path(base.merge_dir)
    else:
        dota_vpk_path = os.path.join(helper.output_path, "maps", "dota.vpk")
        if os.path.exists(dota_vpk_path):
            if vpk_utils.is_minify_pak(dota_vpk_path):
                fs.remove_path(dota_vpk_path)
                maps_output_dir = os.path.join(helper.output_path, "maps")
                if os.path.isdir(maps_output_dir) and not os.listdir(maps_output_dir):
                    fs.remove_path(maps_output_dir)

    # 2. Cursors
    if cursor_mod_paths:
        game_root = os.path.dirname(os.path.dirname(constants.dota_game_pak_path))
        minify_root = os.path.dirname(os.path.abspath(base.mods_dir))
        cursor_bkup_dir = os.path.join(minify_root, "backup", "d2pfx_cursors")
        cursor_backup_payload = os.path.join(cursor_bkup_dir, "dota", "resource", "cursor")
        dota_cursor_dir = os.path.join(game_root, "dota", "resource", "cursor")

        output.add_text("&installing_terminal", "D2PFX Cursors")
        cursor_files = _collect_cursor_files(cursor_mod_paths)

        for _, _, filename in cursor_files:
            destination = os.path.join(dota_cursor_dir, filename)
            backup = os.path.join(cursor_backup_payload, filename)
            for root, path in ((game_root, destination), (minify_root, backup)):
                relative = _relative_under(root, path)
                _, confined = security.confined_destination(root, relative)
                if os.path.lexists(confined):
                    info = os.stat(confined, follow_symlinks=False)
                    if not stat.S_ISREG(info.st_mode):
                        raise ValueError(f"Unsafe cursor destination path: {confined}")

        for source_root, source, filename in cursor_files:
            destination = os.path.join(dota_cursor_dir, filename)
            backup = os.path.join(cursor_backup_payload, filename)
            if os.path.isfile(destination) and not os.path.exists(backup):
                _atomic_copy_regular_file(
                    destination,
                    backup,
                    source_root=game_root,
                    destination_root=minify_root,
                )
            _atomic_copy_regular_file(
                source,
                destination,
                source_root=source_root,
                destination_root=game_root,
            )
    else:
        restore_d2pfx_cursors()

    # 3. Normal Priority VPKs (Base Layer)
    if pfx_normal:
        output.add_text("&merging_vpks")
        for mod_name, vpk_paths in pfx_normal.items():
            for path in vpk_paths:
                try:
                    vpk_utils.dump(
                        vpk.open(path),
                        constants.minify_dota_compile_output_path,
                        check_exists=True,
                    )
                    output.add_text("&merged_mod", mod_name, indent=True)
                except Exception:
                    log.write_warning("&failed_merge_mod", mod_name)


def run_post_build(mod_list):
    _, pfx_high_priority, _, _ = scan_d2pfx_mods(mod_list)

    # High Priority VPKs (Override Layer)
    if pfx_high_priority:
        output.add_text("&merging_vpks")
        for mod_name, vpk_paths in pfx_high_priority.items():
            for path in vpk_paths:
                try:
                    vpk_utils.dump(
                        vpk.open(path),
                        constants.minify_dota_compile_output_path,
                        check_exists=False,
                    )
                    output.add_text("&merged_mod", mod_name, indent=True)
                except Exception:
                    log.write_warning("&failed_merge_mod", mod_name)


def restore_d2pfx_cursors():
    minify_root = os.path.dirname(os.path.abspath(base.mods_dir))
    cursor_bkup_dir = os.path.join(minify_root, "backup", "d2pfx_cursors")
    cursor_backup_payload = os.path.join(cursor_bkup_dir, "dota", "resource", "cursor")
    if not os.path.isdir(cursor_bkup_dir):
        return

    game_root = os.path.dirname(os.path.dirname(constants.dota_game_pak_path))
    dota_cursor_dir = os.path.join(game_root, "dota", "resource", "cursor")

    try:
        relative = _relative_under(minify_root, cursor_backup_payload)
        _, confined_payload = security.confined_destination(minify_root, relative)
    except ValueError:
        log.write_warning("Refusing to restore D2PFX cursor backup outside Minify's backup root.")
        return

    if not os.path.isdir(confined_payload) or os.path.islink(confined_payload):
        log.write_warning("Refusing to restore an invalid D2PFX cursor backup payload.")
        return

    restored = 0
    unsafe = False
    for entry in os.scandir(confined_payload):
        if os.path.splitext(entry.name)[1].casefold() not in CURSOR_EXTENSIONS:
            continue
        if entry.is_symlink() or not entry.is_file(follow_symlinks=False):
            unsafe = True
            log.write_warning(f"Skipping unsafe D2PFX cursor backup entry: {entry.name}")
            continue
        destination = os.path.join(dota_cursor_dir, entry.name)
        try:
            _atomic_copy_regular_file(
                entry.path,
                destination,
                source_root=minify_root,
                destination_root=game_root,
            )
        except (OSError, ValueError):
            unsafe = True
            log.write_warning(f"Could not safely restore D2PFX cursor backup entry: {entry.name}")
            continue
        restored += 1

    if not unsafe:
        fs.remove_path(cursor_bkup_dir)
    if restored > 0:
        output.add_text(f"Restored {restored} original cursor files.", msg_type="success", indent=True)

