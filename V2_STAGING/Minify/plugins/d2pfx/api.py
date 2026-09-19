import datetime as dt
import os
import re
import tempfile
from typing import Any, Dict, List

from core import base, config, fs, mods_shared, output, security, utils
from core.plugin_sdk import PluginRouter

from . import __main__ as plugin_main
from .data import DataManager

router = PluginRouter()


def _d2pfx_date_value(mod: Dict[str, Any]) -> dt.datetime | None:
    if not isinstance(mod, dict):
        return None
    meta = mod.get("meta", {})
    if not isinstance(meta, dict):
        return None
    raw = meta.get("date")
    if raw is None or raw == "" or raw is False:
        return None

    try:
        numeric = float(raw)
    except (TypeError, ValueError):
        numeric = None

    if numeric is not None:
        if numeric == 0:
            return None
        if abs(numeric) >= 100_000_000_000:
            numeric /= 1000.0
        try:
            return dt.datetime.fromtimestamp(numeric, tz=dt.timezone.utc)
        except (OverflowError, OSError, ValueError):
            return None

    text = str(raw).strip()
    if not text:
        return None
    try:
        parsed = dt.datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        try:
            parsed_date = dt.date.fromisoformat(text)
        except ValueError:
            return None
        parsed = dt.datetime.combine(parsed_date, dt.time.min, tzinfo=dt.timezone.utc)

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed


def _format_d2pfx_updated_date(mod: Dict[str, Any]) -> str | None:
    parsed = _d2pfx_date_value(mod)
    if parsed is not None:
        value = parsed.astimezone(dt.timezone.utc).date()
        return f"Updated {value.strftime('%b')} {value.day}, {value.year}"

    meta = mod.get("meta", {}) if isinstance(mod, dict) else {}
    raw = meta.get("date") if isinstance(meta, dict) else None
    if isinstance(raw, str):
        text = raw.strip()
        if text and len(text) <= 32:
            return f"Updated {text}"
    return None


def _d2pfx_date_sort_key(mod: Dict[str, Any]) -> float:
    parsed = _d2pfx_date_value(mod)
    return parsed.timestamp() if parsed is not None else 0.0


@router.route
def get_categories(params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    dm = DataManager()
    if dm.load():
        categories = dm.get_categories()
        res = []
        for cat_id in categories:
            res.append(
                {
                    "id": cat_id,
                    "name": dm.get_category_name(cat_id),
                    "description": dm.get_category_description(cat_id),
                }
            )
        return res
    return []


@router.route
def get_mods(params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    params = params or {}
    cat_id = params.get("cat_id", "")
    search = params.get("search", "")
    sort_mode = params.get("sort_mode", "")

    dm = DataManager()
    if not dm.load():
        return []

    raw_mods = dm.get_mods(cat_id)

    expanded_mods = []
    for m in raw_mods:
        if "styles" in m and isinstance(m["styles"], list):
            for style in m["styles"]:
                m_style = dict(m)
                m_style.update(style)
                expanded_mods.append(m_style)
        else:
            expanded_mods.append(dict(m))

    filter_nsfw = bool(config.get("d2pfx_filter_nsfw", True))
    filter_anime = bool(config.get("d2pfx_filter_anime", False))

    filtered = []
    for m in expanded_mods:
        tags = m.get("tags", {})
        if filter_nsfw:
            is_adult = False
            if isinstance(tags, dict):
                is_adult = any(k.lower() == "adult" and v for k, v in tags.items())
            elif isinstance(tags, list):
                is_adult = any(str(t).lower() == "adult" for t in tags)
            if is_adult:
                continue

        if filter_anime:
            is_anime = False
            if isinstance(tags, dict):
                is_anime = any(k.lower() == "anime" and v for k, v in tags.items())
            elif isinstance(tags, list):
                is_anime = any(str(t).lower() == "anime" for t in tags)
            if is_anime:
                continue

        filtered.append(m)

    if search:
        tokens = re.findall(r"(?:by:|tag:|sort:)?\S+", search.lower())
        for token in tokens:
            if token.startswith("by:"):
                val = token[3:]
                if val:

                    def _has_author(m):
                        a = m.get("author")
                        if not a:
                            return False
                        if isinstance(a, list):
                            return any(val in str(x).lower() for x in a)
                        return val in str(a).lower()

                    filtered = [m for m in filtered if _has_author(m)]
            elif token.startswith("tag:"):
                val = token[4:]
                if val:
                    filtered = [m for m in filtered if any(val in str(t).lower() for t in (m.get("tags") or []))]
            elif token.startswith("sort:"):
                sort_mode = token[5:]
            else:
                filtered = [
                    m for m in filtered if token in m.get("name", "").lower() or token in m.get("label", "").lower()
                ]

    if sort_mode:
        if sort_mode == "a-z":
            filtered.sort(key=lambda m: m.get("name", "").lower())
        elif sort_mode == "z-a":
            filtered.sort(key=lambda m: m.get("name", "").lower(), reverse=True)
        elif sort_mode == "new":
            filtered.sort(key=_d2pfx_date_sort_key, reverse=True)
        elif sort_mode == "old":
            filtered.sort(key=_d2pfx_date_sort_key)

    for m in filtered:
        m["updated_label"] = _format_d2pfx_updated_date(m)
        prev = m.get("preview")
        if isinstance(prev, str) and prev:
            if prev.casefold().startswith(("http://", "https://")):
                m["preview_url"] = prev
                m["preview_fallback_url"] = None
            else:
                m["preview_url"] = dm.get_preview_url(cat_id, prev)
                m["preview_fallback_url"] = dm.get_preview_fallback_url(prev)
        else:
            m["preview_url"] = None
            m["preview_fallback_url"] = None

    return filtered


def _resolve_mod_folder(name: str, cat_id: str, label: str = None) -> str:
    from patch import manifest_utils

    mods_shared.scan_mods()
    for mod_id in mods_shared.mods_alphabetical:
        mod_path = mods_shared.get_mod_path(mod_id)
        if not os.path.isdir(mod_path):
            continue
        cfg = manifest_utils.get_mod(mod_path)
        if (
            cfg.get("browser") == "d2pfx"
            and cfg.get("name") == name
            and cfg.get("category") == cat_id
            and cfg.get("label") == label
        ):
            return mod_id

    mod_dir_name = f"D2PFX {cat_id.upper()} - {name}"
    if label:
        mod_dir_name = f"{mod_dir_name} {label}"
    return utils.sanitize_win_path(mod_dir_name)


@router.route
def get_installed_mods(params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    from patch import manifest_utils

    mods_shared.scan_mods()
    installed = []
    for mod_id in mods_shared.mods_alphabetical:
        mod_path = mods_shared.get_mod_path(mod_id)
        if not os.path.isdir(mod_path):
            continue
        cfg = manifest_utils.get_mod(mod_path)
        if cfg.get("browser") == "d2pfx":
            installed.append(
                {
                    "name": cfg.get("name"),
                    "category": cfg.get("category"),
                    "label": cfg.get("label"),
                    "folder": mod_id,
                    "enabled": mods_shared.get_state(mod_id),
                }
            )
    return installed


@router.route
def set_mod_state(params: Dict[str, Any] = None) -> Dict[str, Any]:
    params = params or {}
    mod_name = params.get("mod_name") or params.get("name", "")
    cat_id = params.get("cat_id", "")
    label = params.get("label")
    enabled = bool(params.get("enabled", True))

    folder = _resolve_mod_folder(mod_name, cat_id, label)
    mods_shared.set_state(folder, enabled)
    return {"success": True, "folder": folder, "enabled": enabled}


@router.route
def install_mod(params: Dict[str, Any] = None) -> Dict[str, Any]:
    params = params or {}
    mod = params.get("mod", {})
    cat_id = params.get("cat_id", "")
    if not isinstance(mod, dict):
        return {"success": False, "error": "Invalid D2PFX mod payload."}

    dm = DataManager()
    name = str(mod.get("name") or "Unknown")[:4096]
    label = mod.get("label")
    author = mod.get("author")
    sender = mod.get("sender")
    tags = mod.get("tags", [])
    links = mod.get("links", [])
    if not isinstance(links, list):
        links = []

    vpk_link = next(
        (link for link in links if isinstance(link, dict) and str(link.get("url", "")).casefold().endswith(".vpk")),
        None,
    )
    zip_link = next(
        (link for link in links if isinstance(link, dict) and str(link.get("url", "")).casefold().endswith(".zip")),
        None,
    )
    mod_url = None
    is_zip = False

    file_value = mod.get("file")
    if isinstance(file_value, str):
        if file_value.casefold().endswith(".vpk"):
            mod_url = file_value
        elif file_value.casefold().endswith(".zip"):
            mod_url = file_value
            is_zip = True

    if not mod_url:
        if vpk_link:
            mod_url = vpk_link.get("url")
        elif zip_link:
            mod_url = zip_link.get("url")
            is_zip = True

    if not isinstance(mod_url, str) or not mod_url:
        return {"success": False, "error": f"No compatible mod file (.vpk/.zip) found for '{name}'."}

    if not mod_url.casefold().startswith(("http://", "https://")):
        mod_url = dm.get_file_url(cat_id, mod_url)

    mod_dir_name = f"D2PFX {str(cat_id).upper()} - {name}"
    if label:
        mod_dir_name = f"{mod_dir_name} {label}"
    target_folder = utils.sanitize_win_path(mod_dir_name)
    try:
        security.safe_relative_path(target_folder)
        _, target_dir = security.confined_destination(base.mods_dir, target_folder)
    except ValueError as exc:
        return {"success": False, "error": f"Unsafe D2PFX install destination: {exc}"}

    staging_root = None
    try:
        fs.create_dirs(base.mods_dir)
        if os.path.islink(base.mods_dir):
            raise ValueError("Mods directory cannot be a symlink during D2PFX installation.")
        if os.path.lexists(target_dir):
            raise ValueError("A D2PFX mod directory with this name already exists.")

        staging_root = tempfile.mkdtemp(prefix=".d2pfx-install-", dir=base.mods_dir)
        install_dir = os.path.join(staging_root, "payload")
        fs.create_dirs(install_dir)

        mod_filename = security.safe_download_filename(mod_url, allowed_extensions={".vpk", ".zip"})
        mod_dest = os.path.join(install_dir, mod_filename)
        if not dm.download_file(
            mod_url,
            mod_dest,
            name=f"{name} ({str(cat_id).upper()})",
            emit_progress=True,
        ):
            raise ValueError("Failed to download mod file.")

        if is_zip:
            if not fs.extract_archive(mod_dest, install_dir):
                raise ValueError("Failed to extract mod archive.")
            fs.remove_path(mod_dest)

        preview_file = mod.get("preview")
        if isinstance(preview_file, str) and preview_file:
            preview_url = (
                preview_file
                if preview_file.casefold().startswith(("http://", "https://"))
                else dm.get_preview_url(cat_id, preview_file)
            )
            preview_dest = os.path.join(install_dir, "preview.webp")
            dm.download_file(
                preview_url,
                preview_dest,
                emit_progress=False,
                max_bytes=32 * 1024 * 1024,
            )

        if isinstance(tags, dict):
            active_tags = [str(k) for k, v in tags.items() if v][:256]
        elif isinstance(tags, list):
            active_tags = [str(item) for item in tags[:256]]
        elif tags is None:
            active_tags = []
        else:
            active_tags = [str(tags)]

        modcfg = {
            "browser": "d2pfx",
            "name": name,
            "category": cat_id,
            "author": author,
            "sender": sender,
            "links": links[:64],
            "tags": active_tags,
            "version": plugin_main.VERSION,
            "label": label,
        }
        if cat_id in plugin_main.RENAME_CATEGORIES:
            modcfg["order"] = 2

        config.write_json_file(os.path.join(install_dir, "manifest.json"), modcfg)

        notes_content = f"Installed via D2PFX Browser {modcfg.get('version') or plugin_main.VERSION}\n\n"
        if cat_id and str(cat_id).casefold() != "unknown":
            notes_content += f"Category: {cat_id}\n"
        type_labels = {"author": "Author", "source": "Source", "modded": "Modded", "sender": "Sender"}
        for t_key in ("author", "source", "modded", "sender"):
            values = []
            for link in links[:64]:
                if not isinstance(link, dict) or link.get("type") != t_key:
                    continue
                value = link.get("name") or link.get("url")
                if value:
                    values.append(str(value)[:4096])
            if values:
                notes_content += f"{type_labels[t_key]}: {', '.join(values)}\n"
        if active_tags:
            notes_content += f"Tags: {', '.join(active_tags)}\n"

        with open(os.path.join(install_dir, "notes.md"), "w", encoding="utf-8") as file:
            file.write(notes_content)

        if os.path.lexists(target_dir):
            raise ValueError("The D2PFX destination appeared during installation; refusing to overwrite it.")
        _, target_dir = security.confined_destination(base.mods_dir, target_folder)
        os.replace(install_dir, target_dir)
        fs.remove_path(staging_root)
        staging_root = None

        mods_shared.scan_mods()
        output.add_text(f"D2PFX mod '{name}' installed successfully.", msg_type="success")
        return {"success": True, "folder": target_folder}
    except Exception as exc:
        if staging_root:
            fs.remove_path(staging_root)
        return {"success": False, "error": str(exc)}


@router.route
def uninstall_mod(params: Dict[str, Any] = None) -> Dict[str, Any]:
    params = params or {}
    mod_name = params.get("mod_name")
    cat_id = params.get("cat_id")
    label = params.get("label")

    from patch import manifest_utils

    mods_shared.scan_mods()
    target_dir = None
    target_id = None
    for mod_id in mods_shared.mods_alphabetical:
        mod_path = mods_shared.get_mod_path(mod_id)
        if not os.path.isdir(mod_path):
            continue
        cfg = manifest_utils.get_mod(mod_path)
        if (
            cfg.get("browser") == "d2pfx"
            and cfg.get("name") == mod_name
            and cfg.get("category") == cat_id
            and cfg.get("label") == label
        ):
            target_dir = mod_path
            target_id = mod_id
            break

    if not target_dir:
        fallback_id = _resolve_mod_folder(str(mod_name or ""), str(cat_id or ""), label)
        possible_dir = mods_shared.get_mod_path(fallback_id)
        if os.path.isdir(possible_dir):
            target_dir = possible_dir
            target_id = fallback_id

    if not target_dir:
        return {"success": False, "error": "Mod directory not found."}

    try:
        relative = os.path.relpath(os.path.abspath(target_dir), os.path.abspath(base.mods_dir)).replace(os.sep, "/")
        security.safe_relative_path(relative)
        _, confined = security.confined_destination(base.mods_dir, relative)
        if os.path.normcase(os.path.abspath(confined)) != os.path.normcase(os.path.abspath(target_dir)):
            raise ValueError("D2PFX uninstall target escaped the mods directory.")
        fs.remove_path(confined)

        if target_id:
            states = config.read_json_file(base.mods_config_dir)
            if isinstance(states, dict) and target_id in states:
                del states[target_id]
                config.write_json_file(base.mods_config_dir, dict(sorted(states.items())))

        mods_shared.scan_mods()
        output.add_text(f"D2PFX mod '{mod_name}' removed.", msg_type="info")
        return {"success": True}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


@router.route
def prune_metadata_cache(params: Dict[str, Any] = None) -> Dict[str, Any]:
    dm = DataManager()
    metadata_file = os.path.join(dm.cache_dir, "mods.json")
    constants_file = os.path.join(dm.cache_dir, "constants.json")
    fs.remove_path(metadata_file, constants_file)
    dm.metadata = {}
    dm.constants = {}
    success = dm.refresh()
    return {"success": success}


def handle_api(action: str, params: Dict[str, Any] = None) -> Any:
    return router.dispatch(action, params)
