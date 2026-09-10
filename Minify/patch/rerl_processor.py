"""Apply declarative RERL redirects from mod rerl.json files."""

from __future__ import annotations

import fnmatch
import json
import os

from core import constants, fs, log, output, rerl, security, utils


def _load_rules(rerl_file: str, folder: str) -> dict[str, dict[str, str]]:
    try:
        with utils.open_utf8(rerl_file) as file:
            rules = json.load(file)
    except Exception as exc:
        raise ValueError(f"Failed to parse rerl.json for {folder}: {exc}") from exc

    if not isinstance(rules, dict):
        raise ValueError(f"rerl.json for {folder} must contain an object.")

    validated: dict[str, dict[str, str]] = {}
    for target_pattern, redirect_map in rules.items():
        if not isinstance(target_pattern, str) or not target_pattern.strip():
            raise ValueError(f"rerl.json for {folder} contains an invalid target pattern.")
        if not isinstance(redirect_map, dict) or not redirect_map:
            raise ValueError(f"rerl.json rule {target_pattern!r} for {folder} must contain redirects.")

        clean_redirects: dict[str, str] = {}
        for source, target in redirect_map.items():
            if not isinstance(source, str) or not isinstance(target, str) or not source or not target:
                raise ValueError(f"rerl.json rule {target_pattern!r} for {folder} contains an invalid redirect.")
            if len(source.encode("utf-8")) != len(target.encode("utf-8")):
                raise ValueError(f"rerl.json redirect must preserve UTF-8 byte length: {source!r} -> {target!r}.")
            clean_redirects[source] = target

        validated[target_pattern.strip()] = clean_redirects

    return validated


def process(rerl_file: str, folder: str, dota_pak_contents) -> None:
    """Patch matching game resources into Minify's compile output."""
    if not os.path.exists(rerl_file):
        return

    try:
        rules = _load_rules(rerl_file, folder)
    except ValueError as exc:
        log.write_warning(str(exc))
        return

    pak_paths = list(dota_pak_contents)

    for target_pattern, redirect_map in rules.items():
        if any(token in target_pattern for token in ("*", "?", "[")):
            target_paths = [path for path in pak_paths if fnmatch.fnmatch(path, target_pattern)]
        else:
            target_paths = [target_pattern] if target_pattern in dota_pak_contents else []

        if not target_paths:
            log.write_warning(f"No assets found matching {target_pattern!r} in rerl.json for {folder}.")
            continue

        for path in target_paths:
            try:
                clean_path, dest_file = security.confined_destination(
                    constants.minify_dota_compile_output_path,
                    path,
                )

                if os.path.exists(dest_file):
                    with open(dest_file, "rb") as file:
                        data = file.read()
                else:
                    pakfile = dota_pak_contents.get_file(clean_path)
                    if not pakfile:
                        log.write_warning(f"Target asset {clean_path!r} not found in game VPK for {folder}.")
                        continue
                    data = pakfile.read()

                if not any(source.encode("utf-8") in data for source in redirect_map):
                    continue

                patched_data, count = rerl.patch_resource_rerl(data, redirect_map)
                if count == 0:
                    continue

                fs.create_dirs(os.path.dirname(dest_file))
                with open(dest_file, "wb") as file:
                    file.write(patched_data)
                output.add_text(f"Decoupled {count} RERL reference(s) in {clean_path}")

            except Exception as exc:
                log.write_warning(f"Failed to patch RERL for {path!r} in {folder}: {exc}")
