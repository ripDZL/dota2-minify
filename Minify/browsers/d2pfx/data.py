import json
import os
import tempfile
import time

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


class DataManager:
    def __init__(self):
        self.cache_dir = CACHE_DIR
        self.previews_dir = PREVIEWS_CACHE_DIR
        fs.create_dirs(self.cache_dir, self.previews_dir)
        self.metadata = {}
        self.constants = {}

    def download_file(self, url, dest, progress_tag=None):
        return fs.download_file(url, dest, progress_tag=progress_tag)

    def fetch_gz_json(self, filename, force_refresh=False):
        local_path = os.path.join(self.cache_dir, filename.replace(".gz", ""))
        gz_url = f"{BASE_URL}data/{filename}"

        if not force_refresh and os.path.exists(local_path):
            try:
                if os.path.getsize(local_path) > security.D2PFX_MAX_MANIFEST_BYTES:
                    raise ValueError("Cached D2PFX catalogue exceeds the safety limit.")
                with open(local_path, "r", encoding="utf-8") as f:
                    cached = json.load(f)
                if not isinstance(cached, dict):
                    raise ValueError("Cached D2PFX catalogue must be a JSON object.")
                return cached
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
                data = json.loads(decoded.decode("utf-8"))
                if not isinstance(data, dict):
                    raise ValueError("D2PFX catalogue must be a JSON object.")

                fd, temporary = tempfile.mkstemp(prefix=".d2pfx-catalogue-", suffix=".json", dir=self.cache_dir)
                try:
                    with os.fdopen(fd, "w", encoding="utf-8") as out:
                        json.dump(data, out, indent=2)
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
        if not self.metadata:
            return []
        mods_data = self.metadata.get("modsData", {})
        return sorted([c for c in mods_data.keys() if c.lower() not in BLACKLIST])

    def get_category_name(self, cat_id):
        if not self.constants:
            return cat_id.capitalize()
        return self.constants.get(cat_id, cat_id.capitalize())

    def get_category_description(self, cat_id):
        if not self.constants:
            return ""
        return self.constants.get(f"{cat_id}-desc", "")

    def get_mods(self, cat_id):
        if not self.metadata:
            return []
        data = self.metadata.get("modsData", {}).get(cat_id, [])

        flattened = []

        def _flatten(item):
            if isinstance(item, list):
                for sub in item:
                    _flatten(sub)
            elif isinstance(item, dict):
                if "groups" in item:
                    _flatten(item["groups"])
                elif "mods" in item:
                    _flatten(item["mods"])
                elif "name" in item:  # It's a mod
                    # Extract authors and senders from links
                    links = item.get("links", [])
                    for key, types in [("author", ("author", "modded")), ("sender", ("sender",))]:
                        vals = [l.get("name") or l.get("url") for l in links if l.get("type") in types]
                        vals = [x for x in vals if x]
                        item[key] = vals[0] if len(vals) == 1 else (vals or None)

                    flattened.append(item)
                else:
                    # Check if it's a dict that might contain groups/mods
                    for val in item.values():
                        if isinstance(val, (dict, list)):
                            _flatten(val)

        _flatten(data)
        return flattened

    def get_preview_url(self, cat_id, filename):
        if filename and filename.endswith(".webp"):
            filename = filename.replace(".webp", ".jpg")
        return f"{BASE_URL}previews/{cat_id}/{filename}"

    def get_file_url(self, cat_id, filename):
        return f"{ASSETS_URL}{cat_id}/{filename}"
