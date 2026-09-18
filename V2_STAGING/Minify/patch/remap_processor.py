import fnmatch
import json
import os
import subprocess

import conditions
from core import base, constants, fs, log, output, security, utils


REMAP_MAX_RULES = 1024
REMAP_MAX_REDIRECTS_PER_RULE = 256
REMAP_MAX_PATH_CHARS = 4096
REMAP_MAX_REFERENCE_CHARS = 4096
REMAP_MAX_RESOURCE_BYTES = 512 * 1024 * 1024
REMAP_MAX_SOURCE_CHARS = 64 * 1024 * 1024


def _validate_rules(raw):
    if not isinstance(raw, dict):
        raise ValueError("remap.json must contain an object.")
    if len(raw) > REMAP_MAX_RULES:
        raise ValueError("remap.json contains too many target rules.")

    validated = {}
    for target_pattern, redirect_map in raw.items():
        if not isinstance(target_pattern, str) or not target_pattern or len(target_pattern) > REMAP_MAX_PATH_CHARS:
            raise ValueError("remap.json contains an invalid target pattern.")
        safe_pattern = security.safe_relative_path(target_pattern)
        if not isinstance(redirect_map, dict) or not redirect_map:
            raise ValueError(f"remap.json target {target_pattern!r} must map references to replacements.")
        if len(redirect_map) > REMAP_MAX_REDIRECTS_PER_RULE:
            raise ValueError(f"remap.json target {target_pattern!r} contains too many redirects.")

        clean_redirects = {}
        for source_ref, destination_ref in redirect_map.items():
            if not isinstance(source_ref, str) or not isinstance(destination_ref, str):
                raise ValueError("remap.json redirects must use string keys and values.")
            if not source_ref or len(source_ref) > REMAP_MAX_REFERENCE_CHARS:
                raise ValueError("remap.json contains an invalid source reference.")
            if len(destination_ref) > REMAP_MAX_REFERENCE_CHARS:
                raise ValueError("remap.json contains an oversized destination reference.")
            clean_redirects[source_ref] = destination_ref
        validated[safe_pattern] = clean_redirects
    return validated


def _confined(root: str, relative: str) -> str:
    _, path = security.confined_destination(root, relative)
    return path


def process(remap_file: str, folder: str, dota_pak_contents) -> None:
    """Process validated remap rules without allowing build/output path escapes."""
    if not os.path.exists(remap_file):
        return

    try:
        with utils.open_utf8(remap_file) as file:
            rules = _validate_rules(json.load(file))
    except Exception as exc:
        log.write_warning(f"Failed to parse remap.json for {folder}: {exc}")
        return

    output_root = os.path.abspath(constants.minify_dota_compile_output_path)
    build_root = os.path.abspath(base.build_dir)
    fs.create_dirs(output_root, build_root)

    for target_pattern, redirect_map in rules.items():
        target_paths = []
        if any(char in target_pattern for char in ("*", "?", "[")):
            for filepath in dota_pak_contents:
                try:
                    safe_path = security.safe_relative_path(filepath)
                except ValueError:
                    continue
                if fnmatch.fnmatch(safe_path, target_pattern):
                    target_paths.append(safe_path)
        else:
            target_paths.append(target_pattern)

        if not target_paths:
            log.write_warning(f"No assets found matching '{target_pattern}' in remap.json for {folder}")
            continue

        for clean_path in target_paths:
            try:
                clean_path = security.safe_relative_path(clean_path)
                dest_file = _confined(output_root, clean_path)
                if os.path.lexists(dest_file):
                    info = os.stat(dest_file, follow_symlinks=False)
                    if not os.path.isfile(dest_file) or os.path.islink(dest_file):
                        raise ValueError(f"Unsafe remap destination: {clean_path}")
                    if info.st_size > REMAP_MAX_RESOURCE_BYTES:
                        raise ValueError(f"Remap target exceeds the safety limit: {clean_path}")
                    with open(dest_file, "rb") as file:
                        data = file.read(REMAP_MAX_RESOURCE_BYTES + 1)
                else:
                    pakfile = dota_pak_contents.get_file(clean_path)
                    if not pakfile:
                        log.write_warning(f"Target asset '{clean_path}' not found in game VPK for {folder}")
                        continue
                    data = pakfile.read()
                    if len(data) > REMAP_MAX_RESOURCE_BYTES:
                        raise ValueError(f"Remap target exceeds the safety limit: {clean_path}")

                if not any(source.encode("utf-8") in data for source in redirect_map):
                    continue

                if not (clean_path.endswith("_c") and conditions.workshop_installed):
                    continue

                source_rel = security.safe_relative_path(clean_path.removesuffix("_c"))
                out_source = _confined(build_root, source_rel)
                temp_c = _confined(build_root, clean_path)
                fs.create_dirs(os.path.dirname(out_source), os.path.dirname(temp_c))

                if os.path.lexists(out_source) and os.path.islink(out_source):
                    raise ValueError(f"Unsafe decompile output path: {source_rel}")
                if os.path.lexists(temp_c) and os.path.islink(temp_c):
                    raise ValueError(f"Unsafe temporary compiled path: {clean_path}")

                with open(temp_c, "wb") as file:
                    file.write(data)

                try:
                    result = subprocess.run(
                        [constants.s2v_exec_path, "-i", temp_c, "-d", "-o", out_source],
                        capture_output=True,
                        text=True,
                        creationflags=subprocess.CREATE_NO_WINDOW if base.is_win else 0,
                    )
                finally:
                    fs.remove_path(temp_c)

                if result.returncode != 0 or not os.path.exists(out_source):
                    log.write_warning(f"Failed to decompile '{clean_path}' for {folder}")
                    continue

                try:
                    if os.path.getsize(out_source) > REMAP_MAX_SOURCE_CHARS:
                        raise ValueError("Decompiled remap source exceeds the safety limit.")
                    with utils.open_utf8(out_source) as file:
                        source_content = file.read(REMAP_MAX_SOURCE_CHARS + 1)
                    if len(source_content) > REMAP_MAX_SOURCE_CHARS:
                        raise ValueError("Decompiled remap source exceeds the safety limit.")

                    for source_ref, destination_ref in redirect_map.items():
                        source_content = source_content.replace(source_ref, destination_ref)
                        if len(source_content) > REMAP_MAX_SOURCE_CHARS:
                            raise ValueError("Remapped source exceeds the safety limit.")

                    with utils.open_utf8(out_source, "w") as file:
                        file.write(source_content)
                    output.add_text(f"Remapped references in {clean_path}", indent=True)
                except Exception as exc:
                    log.write_warning(f"Failed to remap references in '{out_source}': {exc}")
            except Exception as exc:
                log.write_warning(f"Failed to process remap for '{clean_path}' in {folder}: {exc}")
