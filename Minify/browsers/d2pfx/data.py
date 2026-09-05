import json
import os
import stat
import tempfile
import time
import urllib.parse

import requests
from core import base, config, fs, security

# D2PFX Browser Constants
BASE_URL = "https://raw.githubusercontent.com/h6rd/Dota2PornFxWeb/data/"
ASSETS_URL = "https://raw.githubusercontent.com/h6rd/Dota2PornFxWeb/main/assets/files/"
CACHE_DIR = os.path.join(base.cache_dir, "browsers", "d2pfx")
PREVIEWS_CACHE_DIR = os.path.join(CACHE_DIR, "previews")
BLACKLIST = [
    "guides",
    "item-sounds",
    "news",
    "tools",
    "sites",
    "packs",
    "huds",  # https://github.com/Egezenn/dota2-minify/issues/143
    "fonts",
]
CATALOGUE_FILES = {"mods.json.gz", "constants.json.gz"}
MAX_CATEGORIES = 256
MAX_CATEGORY_ID_CHARS = 128
MAX_CATEGORY_TEXT_CHARS = 4096
MAX_FLATTEN_DEPTH = 16
MAX_FLATTEN_NODES = 20_000
MAX_MODS_PER_CATEGORY = 5_000
MAX_LINKS_PER_MOD = 64
MAX_ASSET_PATH_CHARS = 2048


def _safe_category_id(value) -> str:
    category = urllib.parse.unquote(str(value or "")).strip()
    if not category or len(category) > MAX_CATEGORY_ID_CHARS:
        raise ValueError("D2PFX category ID is invalid.")
    normalized = security.safe_relative_path(category)
    if "/" in normalized or normalized != category:
        raise ValueError("D2PFX category ID must be one safe path segment.")
    return normalized


def _safe_asset_path(value) -> str:
    decoded = urllib.parse.unquote(str(value or "")).strip()
    if not decoded or len(decoded) > MAX_ASSET_PATH_CHARS:
        raise ValueError("D2PFX asset path is invalid.")
    return security.safe_relative_path(decoded)


def _quoted_asset_url(base_url: str, category, filename) -> str:
    safe_category = _safe_category_id(category)
    safe_filename = _safe_asset_path(filename)
    encoded_category = urllib.parse.quote(safe_category, safe="")
    encoded_filename = "/".join(urllib.parse.quote(part, safe="") for part in safe_filename.split("/"))
    return f"{base_url}{encoded_category}/{encoded_filename}"


class DataManager:
    def __init__(self):
        self.cache_dir = CACHE_DIR
        self.previews_dir = PREVIEWS_CACHE_DIR
        fs.create_dirs(self.cache_dir, self.previews_dir)
        self.metadata = {}
        self.constants = {}

    def download_file(self, url, dest, progress_tag=None, max_bytes=security.ARCHIVE_MAX_FILE_BYTES):
        return fs.download_file(url, dest, progress_tag=progress_tag, max_bytes=max_bytes)

    def _catalogue_cache_path(self, filename):
        if filename not in CATALOGUE_FILES:
            raise ValueError(f"Unsupported D2PFX catalogue file: {filename!r}")
        if os.path.lexists(self.cache_dir) and os.path.islink(self.cache_dir):
            raise ValueError("D2PFX cache directory cannot be a symlink.")
        local_name = filename.removesuffix(".gz")
        _, path = security.confined_destination(self.cache_dir, local_name)
        return path

    @staticmethod
    def _validate_catalogue_shape(filename, data):
        if not isinstance(data, dict):
            raise ValueError("D2PFX catalogue must be a JSON object.")
        if filename == "mods.json.gz":
            mods_data = data.get("modsData")
            if not isinstance(mods_data, dict):
                raise ValueError("D2PFX mods catalogue is missing a valid modsData object.")
            if len(mods_data) > MAX_CATEGORIES:
                raise ValueError("D2PFX mods catalogue contains too many categories.")
        return data

    def _read_cached_catalogue(self, filename, local_path):
        info = os.stat(local_path, follow_symlinks=False)
        if not stat.S_ISREG(info.st_mode):
            raise ValueError("Cached D2PFX catalogue must be a regular file.")
        if info.st_size > security.D2PFX_MAX_MANIFEST_BYTES:
            raise ValueError("Cached D2PFX catalogue exceeds the safety limit.")

        flags = os.O_RDONLY
        if hasattr(os, "O_BINARY"):
            flags |= os.O_BINARY
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        fd = os.open(local_path, flags)
        with os.fdopen(fd, "r", encoding="utf-8") as file:
            opened = os.fstat(file.fileno())
            if not stat.S_ISREG(opened.st_mode) or opened.st_size > security.D2PFX_MAX_MANIFEST_BYTES:
                raise ValueError("Cached D2PFX catalogue changed during validation.")
            return self._validate_catalogue_shape(filename, json.load(file))

    def fetch_gz_json(self, filename, force_refresh=False):
        try:
            local_path = self._catalogue_cache_path(filename)
        except ValueError as exc:
            print(f"Error fetching {filename}: {exc}")
            return None
        gz_url = f"{BASE_URL}data/{filename}"

        if not force_refresh and os.path.lexists(local_path):
            try:
                return self._read_cached_catalogue(filename, local_path)
            except Exception:
                pass

        response = None
        try:
            response = requests.get(gz_url, stream=True, timeout=(10, 30))
            if response.status_code == 200:
                compressed = bytearray()
                for chunk in response.iter_content(chunk_size=64 * 1024):
                    if not chunk:
                        continue
                    compressed.extend(chunk)
                    if len(compressed) > security.D2PFX_MAX_MANIFEST_BYTES:
                        raise ValueError("Compressed D2PFX catalogue exceeds the safety limit.")

                decoded = security.bounded_zlib_decompress(
                    bytes(compressed),
                    max_output=security.D2PFX_MAX_MANIFEST_BYTES,
                )
                data = self._validate_catalogue_shape(filename, json.loads(decoded.decode("utf-8")))

                fd, temporary = tempfile.mkstemp(prefix=".d2pfx-catalogue-", suffix=".json", dir=self.cache_dir)
                try:
                    with os.fdopen(fd, "w", encoding="utf-8") as out:
                        json.dump(data, out, indent=2)
                    # Revalidate the cache destination after the temp file is complete.
                    local_path = self._catalogue_cache_path(filename)
                    os.replace(temporary, local_path)
                except Exception:
                    try:
                        os.remove(temporary)
                    except FileNotFoundError:
                        pass
                    raise
                return data
        except Exception as e:
            print(f"Error fetching {filename}: {e}")
        finally:
            if response is not None:
                try:
                    response.close()
                except Exception:
                    pass

        return None

    def refresh(self):
        self.metadata = self.fetch_gz_json("mods.json.gz", force_refresh=True)
        self.constants = self.fetch_gz_json("constants.json.gz", force_refresh=True)
        if self.metadata is not None:
            config.set("d2pfx_last_refresh", int(time.time()))
        return self.metadata is not None

    def _needs_refresh(self):
        if not config.get("d2pfx_auto_refresh_catalogue", True):
            return False
        last_refresh = config.get("d2pfx_last_refresh", 0)
        return (time.time() - last_refresh) > 86400

    def load(self):
        if self._needs_refresh():
            self.refresh()

        self.metadata = self.fetch_gz_json("mods.json.gz")
        self.constants = self.fetch_gz_json("constants.json.gz")
        return self.metadata is not None

    def get_categories(self):
        if not isinstance(self.metadata, dict):
            return []
        mods_data = self.metadata.get("modsData", {})
        if not isinstance(mods_data, dict):
            return []

        categories = []
        for category in mods_data:
            try:
                safe_category = _safe_category_id(category)
            except ValueError:
                continue
            if safe_category.casefold() in BLACKLIST:
                continue
            categories.append(safe_category)
            if len(categories) >= MAX_CATEGORIES:
                break
        return sorted(categories, key=str.casefold)

    def get_category_name(self, cat_id):
        try:
            safe_category = _safe_category_id(cat_id)
        except ValueError:
            return ""
        fallback = safe_category.capitalize()
        if not isinstance(self.constants, dict):
            return fallback
        value = self.constants.get(safe_category, fallback)
        return str(value)[:MAX_CATEGORY_TEXT_CHARS] if isinstance(value, (str, int, float)) else fallback

    def get_category_description(self, cat_id):
        try:
            safe_category = _safe_category_id(cat_id)
        except ValueError:
            return ""
        if not isinstance(self.constants, dict):
            return ""
        value = self.constants.get(f"{safe_category}-desc", "")
        return str(value)[:MAX_CATEGORY_TEXT_CHARS] if isinstance(value, (str, int, float)) else ""

    def get_mods(self, cat_id):
        if not isinstance(self.metadata, dict):
            return []
        try:
            cat_id = _safe_category_id(cat_id)
        except ValueError:
            return []
        mods_data = self.metadata.get("modsData", {})
        if not isinstance(mods_data, dict):
            return []
        data = mods_data.get(cat_id, [])

        flattened = []
        stack = [(data, 0)]
        visited = 0

        while stack and len(flattened) < MAX_MODS_PER_CATEGORY:
            item, depth = stack.pop()
            visited += 1
            if visited > MAX_FLATTEN_NODES:
                break
            if depth > MAX_FLATTEN_DEPTH:
                continue

            if isinstance(item, list):
                remaining = max(0, MAX_FLATTEN_NODES - visited)
                for sub in reversed(item[:remaining]):
                    stack.append((sub, depth + 1))
                continue
            if not isinstance(item, dict):
                continue

            if "groups" in item:
                stack.append((item["groups"], depth + 1))
                continue
            if "mods" in item:
                stack.append((item["mods"], depth + 1))
                continue
            if "name" in item:
                name = item.get("name")
                if not isinstance(name, str) or not name.strip() or len(name) > MAX_CATEGORY_TEXT_CHARS:
                    continue

                normalized = dict(item)
                links = item.get("links", [])
                safe_links = links[:MAX_LINKS_PER_MOD] if isinstance(links, list) else []
                for key, types in [("author", ("author", "modded")), ("sender", ("sender",))]:
                    vals = []
                    for link in safe_links:
                        if not isinstance(link, dict) or link.get("type") not in types:
                            continue
                        candidate = link.get("name") or link.get("url")
                        if isinstance(candidate, (str, int, float)):
                            vals.append(str(candidate)[:MAX_CATEGORY_TEXT_CHARS])
                    normalized[key] = vals[0] if len(vals) == 1 else (vals or None)
                flattened.append(normalized)
                continue

            for value in list(item.values())[:MAX_LINKS_PER_MOD]:
                if isinstance(value, (dict, list)):
                    stack.append((value, depth + 1))

        return flattened

    def get_preview_url(self, cat_id, filename):
        filename = urllib.parse.unquote(str(filename or ""))
        if filename.casefold().endswith(".webp"):
            filename = filename[:-5] + ".jpg"
        return _quoted_asset_url(f"{BASE_URL}previews/", cat_id, filename)

    def get_file_url(self, cat_id, filename):
        return _quoted_asset_url(ASSETS_URL, cat_id, filename)
