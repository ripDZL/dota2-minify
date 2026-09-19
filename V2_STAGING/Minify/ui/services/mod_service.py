import base64
import datetime as dt
import os
from typing import Any, Dict, List

from core import base, config, mod_library, mods_shared, output, profiles, utils


class ModService:
    @staticmethod
    def _library_metadata(mod_name: str, mod_path: str, cfg: Dict[str, Any] | None = None) -> Dict[str, Any]:
        cfg = cfg if isinstance(cfg, dict) else {}
        shared = mods_shared.get_mod_metadata(mod_name)
        group = str(mods_shared.get_mod_group(mod_name) or "").strip()
        browser = cfg.get("browser")
        browser = browser if isinstance(browser, dict) else {}
        manifest_category = str(cfg.get("category") or browser.get("category") or "").strip()
        category = manifest_category or str(shared.get("category") or group or "").strip()

        if mod_library.is_d2pfx(mod_name):
            source = "D2PFX"
            mod_type = "d2pfx"
        elif mod_name.casefold().endswith(".vpk"):
            source = str(shared.get("source") or "Local VPK")
            mod_type = "vpk"
        elif group:
            source = str(shared.get("source") or "Local folder")
            mod_type = "collection"
        else:
            source = str(shared.get("source") or "Minify")
            mod_type = "standard"

        return {
            "group": group,
            "category": mod_library.category(mod_name) or category,
            "source": mod_library.source(mod_name) or source,
            "type": mod_type,
            "nested": bool(shared.get("nested") or group),
            "path": os.path.abspath(mod_path),
            "favorite": mod_library.is_favorite(mod_name),
        }

    @staticmethod
    def get_mod_preview(mod_path: str) -> str | None:
        if not os.path.isdir(mod_path):
            return None
        for filename in os.listdir(mod_path):
            if filename.lower() in (
                "preview.jpg",
                "preview.jpeg",
                "preview.png",
                "preview.webp",
                "preview.gif",
            ):
                p_path = os.path.join(mod_path, filename)
                try:
                    ext = filename.lower().rsplit(".", 1)[-1]
                    mime_type = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"
                    with open(p_path, "rb") as img_file:
                        encoded = base64.b64encode(img_file.read()).decode("utf-8")
                        return f"data:{mime_type};base64,{encoded}"
                except Exception as e:
                    output.add_text(
                        f"Error loading preview image for {os.path.basename(mod_path)}: {e}", msg_type="warning"
                    )
        return None

    def get_mods(self) -> List[Dict[str, Any]]:
        try:
            mods_shared.scan_mods()
            import conditions
            from patch import manifest_utils

            if not conditions.workshop_installed:
                conditions.disable_workshop_mods()

            mod_list = mods_shared.visually_available_mods
            mods_data = []
            for mod in mod_list:
                mod_path = mods_shared.get_mod_path(mod)
                always = False
                untickable = False
                display_name = mod_library.display_name(mod)
                if os.path.isdir(mod_path):
                    cfg = manifest_utils.get_mod(mod_path)
                    always = bool(cfg.get("always", False))
                    if isinstance(cfg, dict) and cfg.get("name"):
                        display_name = str(cfg["name"])
                    if not conditions.workshop_installed and conditions.is_workshop_required_mod(mod_path, cfg):
                        untickable = True
                preview = self.get_mod_preview(mod_path)
                metadata = self._library_metadata(mod, mod_path, cfg if os.path.isdir(mod_path) else {})
                mods_data.append(
                    {
                        "name": mod,
                        "display_name": display_name,
                        "enabled": not untickable and (always or mods_shared.get_state(mod)),
                        "always": always,
                        "untickable": untickable,
                        "preview": preview,
                        **metadata,
                    }
                )
            return mods_data
        except Exception as e:
            output.add_text(f"get_mods error: {e}", msg_type="error")
            return []

    def apply_hero_defaults_without_d2pfx(self) -> Dict[str, Any]:
        """Enable Hero Mods defaults except those actually overridden by enabled D2PFX mods."""
        try:
            mods_shared.scan_mods()
            visible = list(mods_shared.visually_available_mods)
            hero_mods = [
                mod
                for mod in visible
                if str(mods_shared.get_mod_group(mod) or "").strip().casefold() == "hero mods"
                and not mod_library.is_d2pfx(mod)
            ]
            selected_d2pfx = [
                mod
                for mod in visible
                if mod_library.is_d2pfx(mod) and bool(mods_shared.get_state(mod))
            ]

            d2pfx_entries = {
                mod: set(mod_library.index_contents(mod))
                for mod in selected_d2pfx
            }

            desired: Dict[str, bool] = {}
            protected: Dict[str, List[str]] = {}
            for hero_mod in hero_mods:
                hero_entries = set(mod_library.index_contents(hero_mod))
                blockers = [
                    mod
                    for mod, entries in d2pfx_entries.items()
                    if hero_entries and entries and not hero_entries.isdisjoint(entries)
                ]
                desired[hero_mod] = not blockers
                if blockers:
                    protected[hero_mod] = blockers

            if not self.set_mods(desired):
                return {"success": False, "error": "Could not update Hero Mods selection."}

            enabled = sum(1 for value in desired.values() if value)
            disabled = len(desired) - enabled
            protected_rows = [
                {
                    "hero": mod_library.display_name(hero_mod),
                    "d2pfx": [mod_library.display_name(mod) for mod in blockers],
                }
                for hero_mod, blockers in sorted(
                    protected.items(),
                    key=lambda item: mod_library.display_name(item[0]).casefold(),
                )
            ]
            output.add_text(
                f"Hero defaults updated: {enabled} enabled, {disabled} left disabled for enabled D2PFX overrides.",
                msg_type="success",
            )
            return {
                "success": True,
                "enabled": enabled,
                "disabled": disabled,
                "hero_count": len(hero_mods),
                "selected_d2pfx": len(selected_d2pfx),
                "protected": protected_rows,
            }
        except Exception as exc:
            output.add_text(f"Hero default selection error: {exc}", msg_type="error")
            return {"success": False, "error": str(exc)}

    def set_favorite(self, mod_name: str, value: bool) -> Dict[str, Any]:
        try:
            mods_shared.scan_mods()
            if mod_name not in mods_shared.mod_paths:
                return {"success": False, "error": "Mod not found."}
            favorite = mod_library.set_favorite(mod_name, bool(value))
            return {"success": True, "favorite": favorite}
        except Exception as exc:
            output.add_text(f"set_favorite error: {exc}", msg_type="error")
            return {"success": False, "error": str(exc)}

    def get_profiles(self) -> List[Dict[str, Any]]:
        return profiles.list_profiles()

    def save_profile(self, name: str) -> Dict[str, Any]:
        try:
            mods_shared.scan_mods()
            states = {mod: bool(mods_shared.get_state(mod)) for mod in mods_shared.visually_available_mods}
            saved = profiles.save_profile(name, states)
            return {"success": True, "name": str(name).strip(), "state_count": len(saved)}
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    def apply_profile(self, name: str) -> Dict[str, Any]:
        try:
            import conditions
            from patch import manifest_utils

            mods_shared.scan_mods()
            states = profiles.get_profile(name)
            if states is None:
                return {"success": False, "error": "Profile not found."}

            available = list(mods_shared.visually_available_mods)
            snapshot = profiles.complete_snapshot(states, available)
            applied = 0
            locked = 0
            missing = len(set(states) - set(available))

            for mod in available:
                mod_path = mods_shared.get_mod_path(mod)
                cfg = manifest_utils.get_mod(mod_path) if os.path.isdir(mod_path) else {}
                always = bool(cfg.get("always", False)) if isinstance(cfg, dict) else False
                workshop_locked = (
                    os.path.isdir(mod_path)
                    and not conditions.workshop_installed
                    and conditions.is_workshop_required_mod(mod_path, cfg)
                )
                if always or workshop_locked:
                    locked += 1
                    continue
                mods_shared.set_state(mod, snapshot[mod])
                applied += 1

            return {
                "success": True,
                "name": str(name).strip(),
                "applied": applied,
                "locked": locked,
                "missing": missing,
            }
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    def duplicate_profile(self, name: str) -> Dict[str, Any]:
        try:
            new_name = profiles.duplicate_profile(name)
            if not new_name:
                return {"success": False, "error": "Profile not found."}
            return {"success": True, "name": new_name}
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    def delete_profile(self, name: str) -> Dict[str, Any]:
        try:
            return {"success": profiles.delete_profile(name)}
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    def update_profile(self, name: str) -> Dict[str, Any]:
        clean_name = str(name or "").strip()
        if not profiles.get_profile(clean_name):
            return {"success": False, "error": "Profile not found."}
        return self.save_profile(clean_name)

    def export_profile_bundle(self) -> Dict[str, Any]:
        mods_shared.scan_mods()
        saved = profiles.load_profiles()
        referenced = {mod for states in saved.values() for mod in states}
        available = set(mods_shared.visually_available_mods)
        hints: Dict[str, Dict[str, str]] = {}

        for mod in sorted(referenced, key=str.casefold):
            hint = {"display_name": mod, "source": "", "stable_key": ""}
            if mod in available:
                try:
                    hint["display_name"] = mod_library.display_name(mod)
                    hint["source"] = mod_library.source(mod)
                    hint["stable_key"] = mod_library.stable_key(mod, calculate_hash=False)
                except Exception:
                    pass
            hints[mod] = hint

        return {
            "format": profiles.PROFILE_EXPORT_FORMAT,
            "version": profiles.PROFILE_EXPORT_VERSION,
            "exported_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
            "profiles": {
                name: {"mods": dict(states)}
                for name, states in sorted(saved.items(), key=lambda item: item[0].casefold())
            },
            "mod_hints": hints,
        }

    @staticmethod
    def _profile_identity_indexes(mods: List[str]) -> tuple[Dict[str, List[str]], Dict[tuple[str, str], List[str]]]:
        stable_index: Dict[str, List[str]] = {}
        friendly_index: Dict[tuple[str, str], List[str]] = {}
        for mod in mods:
            try:
                stable = str(mod_library.stable_key(mod, calculate_hash=False) or "")
                if stable:
                    stable_index.setdefault(stable, []).append(mod)
                friendly = (
                    str(mod_library.display_name(mod) or mod).strip().casefold(),
                    str(mod_library.source(mod) or "").strip().casefold(),
                )
                friendly_index.setdefault(friendly, []).append(mod)
            except Exception:
                continue
        return stable_index, friendly_index

    @classmethod
    def _remap_imported_states(
        cls, states: Dict[str, bool], hints: Dict[str, Dict[str, str]], available: List[str]
    ) -> tuple[Dict[str, bool], int]:
        current = set(available)
        stable_index, friendly_index = cls._profile_identity_indexes(available)
        remapped: Dict[str, bool] = {}
        remap_count = 0

        for imported_mod, enabled in states.items():
            target = imported_mod
            if imported_mod not in current:
                hint = hints.get(imported_mod, {}) if isinstance(hints, dict) else {}
                stable = str(hint.get("stable_key", "") or "") if isinstance(hint, dict) else ""
                stable_matches = stable_index.get(stable, []) if stable else []
                if len(stable_matches) == 1:
                    target = stable_matches[0]
                else:
                    friendly = (
                        str(hint.get("display_name", imported_mod) or imported_mod).strip().casefold(),
                        str(hint.get("source", "") or "").strip().casefold(),
                    )
                    friendly_matches = friendly_index.get(friendly, [])
                    if len(friendly_matches) == 1:
                        target = friendly_matches[0]
            if target != imported_mod:
                remap_count += 1
            remapped[target] = bool(enabled)

        return remapped, remap_count

    def import_profile_bundle(self, data: Any) -> Dict[str, Any]:
        imported, hints = profiles.normalize_import_bundle(data)
        if not imported:
            return {"success": False, "error": "No valid Minify profiles were found."}

        mods_shared.scan_mods()
        available = list(mods_shared.visually_available_mods)
        existing = profiles.load_profiles()
        added = 0
        duplicates = 0
        renamed = 0
        remapped = 0
        targets: List[str] = []

        for name, states in imported.items():
            mapped, mapped_count = self._remap_imported_states(states, hints, available)
            remapped += mapped_count

            if name in existing and existing[name] == mapped:
                duplicates += 1
                targets.append(name)
                continue

            target_name = name
            if target_name in existing:
                base_name = f"{name} (Imported)"
                target_name = base_name
                counter = 2
                while target_name in existing:
                    target_name = f"{base_name} {counter}"
                    counter += 1
                renamed += 1

            profiles.save_profile(target_name, mapped)
            existing[target_name] = mapped
            targets.append(target_name)
            added += 1

        applied_name = targets[0] if targets else ""
        apply_result = self.apply_profile(applied_name) if applied_name else {"success": True}
        if applied_name and not apply_result.get("success"):
            return {"success": False, "error": apply_result.get("error", "Imported profile could not be applied.")}

        return {
            "success": True,
            "added": added,
            "duplicates": duplicates,
            "renamed": renamed,
            "remapped": remapped,
            "applied_name": applied_name,
        }

    @staticmethod
    def _build_directory_tree(dir_path: str) -> Dict[str, Any]:
        dir_name = os.path.basename(dir_path)

        def _scan(current_path: str, rel_path: str) -> Dict[str, Any]:
            children = []
            try:
                entries = sorted(
                    os.listdir(current_path),
                    key=lambda x: (not os.path.isdir(os.path.join(current_path, x)), x.lower()),
                )
                for entry in entries:
                    if entry.startswith((".", "_")) or entry == "__pycache__":
                        continue
                    full_entry_path = os.path.join(current_path, entry)
                    entry_rel = os.path.join(rel_path, entry).replace("\\", "/") if rel_path else entry
                    if os.path.isdir(full_entry_path):
                        children.append(_scan(full_entry_path, entry_rel))
                    else:
                        size = 0
                        try:
                            size = os.path.getsize(full_entry_path)
                        except OSError:
                            pass
                        children.append(
                            {
                                "name": entry,
                                "type": "file",
                                "path": entry_rel,
                                "size": size,
                            }
                        )
            except Exception as e:
                output.add_text(f"Error scanning directory {current_path}: {e}", msg_type="warning")
            return {
                "name": os.path.basename(current_path) if rel_path else dir_name,
                "type": "directory",
                "path": rel_path,
                "children": children,
            }

        return _scan(dir_path, "")

    @staticmethod
    def _count_tree_files(node: Dict[str, Any]) -> int:
        if node.get("type") == "file":
            return 1
        return sum(ModService._count_tree_files(child) for child in node.get("children", []))

    @staticmethod
    def _build_vpk_tree(mod_name: str, vpk_path: str) -> Dict[str, Any]:
        import vpk

        root: Dict[str, Any] = {
            "name": mod_name,
            "type": "directory",
            "path": "",
            "children": [],
        }
        try:
            pak = vpk.open(vpk_path)
            for path_str in sorted(pak):
                parts = path_str.replace("\\", "/").strip("/").split("/")
                curr = root
                curr_path = ""
                for i, part in enumerate(parts):
                    curr_path = f"{curr_path}/{part}" if curr_path else part
                    is_file = i == len(parts) - 1
                    found = None
                    for child in curr["children"]:
                        if child["name"] == part and child["type"] == ("file" if is_file else "directory"):
                            found = child
                            break
                    if not found:
                        found = {
                            "name": part,
                            "type": "file" if is_file else "directory",
                            "path": curr_path,
                        }
                        if not is_file:
                            found["children"] = []
                        curr["children"].append(found)
                    curr = found
        except Exception as e:
            output.add_text(f"Error reading VPK {mod_name}: {e}", msg_type="warning")

        def _sort(node: Dict[str, Any]) -> None:
            if "children" in node:
                node["children"].sort(key=lambda x: (0 if x["type"] == "directory" else 1, x["name"].lower()))
                for c in node["children"]:
                    _sort(c)

        _sort(root)
        return root

    @staticmethod
    def _format_json(raw_text: str) -> str:
        trimmed = raw_text.strip()
        if "\n" in trimmed:
            return trimmed
        try:
            import json

            return json.dumps(json.loads(trimmed), indent=2)
        except Exception:
            return trimmed

    def get_mod_methods(self, mod_name: str, mod_path: str) -> List[Dict[str, Any]]:
        methods: List[Dict[str, Any]] = []

        if mod_name.endswith(".vpk") and os.path.isfile(mod_path):
            vpk_tree = self._build_vpk_tree(mod_name, mod_path)
            count = self._count_tree_files(vpk_tree)
            methods.append(
                {
                    "name": mod_name,
                    "type": "tree",
                    "tree": vpk_tree,
                    "badge": f"{count} file" if count == 1 else f"{count} files",
                }
            )
            return methods

        if not os.path.isdir(mod_path):
            return methods

        # 1. files directory
        files_dir = os.path.join(mod_path, "files")
        if os.path.isdir(files_dir):
            tree = self._build_directory_tree(files_dir)
            count = self._count_tree_files(tree)
            methods.append(
                {
                    "name": "files",
                    "type": "tree",
                    "tree": tree,
                    "badge": f"{count} file" if count == 1 else f"{count} files",
                }
            )

        # 2. files_uncompiled directory
        files_uncompiled_dir = os.path.join(mod_path, "files_uncompiled")
        if os.path.isdir(files_uncompiled_dir):
            tree = self._build_directory_tree(files_uncompiled_dir)
            count = self._count_tree_files(tree)
            methods.append(
                {
                    "name": "files_uncompiled",
                    "type": "tree",
                    "tree": tree,
                    "badge": f"{count} file" if count == 1 else f"{count} files",
                }
            )

        # 3. blacklist.txt
        blacklist_path = os.path.join(mod_path, "blacklist.txt")
        if os.path.isfile(blacklist_path):
            try:
                with utils.open_utf8(blacklist_path) as f:
                    bl_content = f.read()
                lines = bl_content.splitlines()
                methods.append(
                    {
                        "name": "blacklist.txt",
                        "type": "blacklist",
                        "content": bl_content,
                        "badge": f"{len(lines)} line" if len(lines) == 1 else f"{len(lines)} lines",
                    }
                )
            except Exception as e:
                output.add_text(f"Error reading blacklist.txt for {mod_name}: {e}", msg_type="warning")

        # 4. xml.json
        xml_path = os.path.join(mod_path, "xml.json")
        if os.path.isfile(xml_path):
            try:
                with utils.open_utf8(xml_path) as f:
                    raw_xml = f.read()
                fmt_xml = self._format_json(raw_xml)
                lines = fmt_xml.splitlines()
                methods.append(
                    {
                        "name": "xml.json",
                        "type": "json",
                        "content": fmt_xml,
                        "badge": f"{len(lines)} line" if len(lines) == 1 else f"{len(lines)} lines",
                    }
                )
            except Exception as e:
                output.add_text(f"Error reading xml.json for {mod_name}: {e}", msg_type="warning")

        # 5. replacer.json
        replacer_path = os.path.join(mod_path, "replacer.json")
        if os.path.isfile(replacer_path):
            try:
                with utils.open_utf8(replacer_path) as f:
                    raw_replacer = f.read()
                fmt_replacer = self._format_json(raw_replacer)
                lines = fmt_replacer.splitlines()
                methods.append(
                    {
                        "name": "replacer.json",
                        "type": "json",
                        "content": fmt_replacer,
                        "badge": f"{len(lines)} line" if len(lines) == 1 else f"{len(lines)} lines",
                    }
                )
            except Exception as e:
                output.add_text(f"Error reading replacer.json for {mod_name}: {e}", msg_type="warning")

        # 6. styling.css
        styling_path = os.path.join(mod_path, "styling.css")
        if os.path.isfile(styling_path):
            try:
                with utils.open_utf8(styling_path) as f:
                    css_content = f.read()
                lines = css_content.splitlines()
                methods.append(
                    {
                        "name": "styling.css",
                        "type": "css",
                        "content": css_content,
                        "badge": f"{len(lines)} line" if len(lines) == 1 else f"{len(lines)} lines",
                    }
                )
            except Exception as e:
                output.add_text(f"Error reading styling.css for {mod_name}: {e}", msg_type="warning")

        # 7. Python scripts
        script_priority = [
            "script_initial.py",
            "script.py",
            "script_after_decompile.py",
            "script_after_recompile.py",
            "script_after_patch.py",
            "script_prelaunch.py",
            "script_uninstall.py",
            "script_utility.py",
        ]
        script_files = [
            f
            for f in os.listdir(mod_path)
            if f.startswith("script") and f.endswith(".py") and os.path.isfile(os.path.join(mod_path, f))
        ]
        script_files.sort(key=lambda x: (script_priority.index(x) if x in script_priority else 999, x.lower()))
        for s_file in script_files:
            s_path = os.path.join(mod_path, s_file)
            try:
                with utils.open_utf8(s_path) as f:
                    py_content = f.read()
                lines = py_content.splitlines()
                methods.append(
                    {
                        "name": s_file,
                        "type": "python",
                        "content": py_content,
                        "badge": f"{len(lines)} line" if len(lines) == 1 else f"{len(lines)} lines",
                    }
                )
            except Exception as e:
                output.add_text(f"Error reading {s_file} for {mod_name}: {e}", msg_type="warning")

        # 8. manifest.json
        manifest_path = os.path.join(mod_path, "manifest.json")
        if os.path.isfile(manifest_path):
            try:
                with utils.open_utf8(manifest_path) as f:
                    raw_manifest = f.read()
                fmt_manifest = self._format_json(raw_manifest)
                lines = fmt_manifest.splitlines()
                methods.append(
                    {
                        "name": "manifest.json",
                        "type": "json",
                        "content": fmt_manifest,
                        "badge": f"{len(lines)} line" if len(lines) == 1 else f"{len(lines)} lines",
                    }
                )
            except Exception as e:
                output.add_text(f"Error reading manifest.json for {mod_name}: {e}", msg_type="warning")

        # 9. Other custom files
        known_files = {
            "notes.md",
            "preview.jpg",
            "preview.jpeg",
            "preview.png",
            "preview.webp",
            "preview.gif",
            "blacklist.txt",
            "xml.json",
            "replacer.json",
            "styling.css",
            "manifest.json",
            "files",
            "files_uncompiled",
            "__pycache__",
        }
        for item in sorted(os.listdir(mod_path), key=str.lower):
            if item.lower() in known_files or item.startswith(("script", ".", "_")):
                continue
            item_path = os.path.join(mod_path, item)
            if os.path.isfile(item_path):
                ext = item.lower().rsplit(".", 1)[-1] if "." in item else ""
                type_str = "text"
                if ext == "json":
                    type_str = "json"
                elif ext in ("xml", "vxml"):
                    type_str = "xml"
                elif ext == "css":
                    type_str = "css"
                elif ext == "py":
                    type_str = "python"
                try:
                    with utils.open_utf8(item_path) as f:
                        other_content = f.read()
                    lines = other_content.splitlines()
                    methods.append(
                        {
                            "name": item,
                            "type": type_str,
                            "content": other_content,
                            "badge": f"{len(lines)} line" if len(lines) == 1 else f"{len(lines)} lines",
                        }
                    )
                except Exception:
                    pass

        return methods

    def get_mod_details(self, mod_name: str, lang: str | None = None) -> Dict[str, Any]:
        try:
            if not lang:
                lang = config.get("locale") or "EN"
            mod_path = mods_shared.get_mod_path(mod_name)
            methods = self.get_mod_methods(mod_name, mod_path)

            display_name = mods_shared.get_mod_label(mod_name)
            if os.path.isdir(mod_path):
                from patch import manifest_utils

                cfg = manifest_utils.get_mod(mod_path)
                if isinstance(cfg, dict) and cfg.get("name"):
                    display_name = str(cfg["name"])

            if not os.path.isdir(mod_path):
                return {
                    "name": mod_name,
                    "display_name": display_name,
                    "notes": None,
                    "preview": None,
                    "has_notes": False,
                    "has_preview": False,
                    "methods": methods,
                }

            notes_path = os.path.join(mod_path, "notes.md")
            notes_content = None
            if os.path.exists(notes_path):
                try:
                    with utils.open_utf8(notes_path) as f:
                        raw_notes = f.read()
                    notes_content = self.parse_notes_for_locale(raw_notes, lang)
                except Exception as e:
                    output.add_text(f"Error reading notes for {mod_name}: {e}", msg_type="warning")

            preview_data_url = self.get_mod_preview(mod_path)

            return {
                "name": mod_name,
                "display_name": display_name,
                "notes": notes_content,
                "preview": preview_data_url,
                "has_notes": bool(notes_content),
                "has_preview": bool(preview_data_url),
                "methods": methods,
            }
        except Exception as e:
            output.add_text(f"get_mod_details error: {e}", msg_type="error")
            return {
                "name": mod_name,
                "notes": None,
                "preview": None,
                "has_notes": False,
                "has_preview": False,
                "methods": [],
            }

    @staticmethod
    def parse_notes_for_locale(notes_text: str, lang: str) -> str:
        if not notes_text or "<!-- lang:" not in notes_text.lower():
            return notes_text.strip()

        sections: Dict[str, str] = {}
        current_lang: str | None = None
        lines: List[str] = []

        for line in notes_text.splitlines():
            trimmed = line.strip()
            if trimmed.lower().startswith("<!-- lang:") and trimmed.endswith("-->"):
                if current_lang:
                    sections[current_lang] = "\n".join(lines).strip()
                current_lang = trimmed[10:-3].strip().lower()
                lines = []
            else:
                lines.append(line)
        if current_lang:
            sections[current_lang] = "\n".join(lines).strip()

        target_lang = (lang or "en").lower()
        if target_lang in sections:
            return sections[target_lang]
        elif "en" in sections:
            return sections["en"]
        elif sections:
            return next(iter(sections.values()))

        return notes_text.strip()

    def set_mods(self, data: Dict[str, bool]) -> bool:
        try:
            import conditions
            from patch import manifest_utils

            for mod_name, enabled in data.items():
                mod_path = mods_shared.get_mod_path(mod_name)
                if os.path.isdir(mod_path):
                    cfg = manifest_utils.get_mod(mod_path)
                    if cfg.get("always", False):
                        continue
                    if not conditions.workshop_installed and conditions.is_workshop_required_mod(mod_path, cfg):
                        continue
                mods_shared.set_state(mod_name, bool(enabled))
            return True
        except Exception:
            return False
