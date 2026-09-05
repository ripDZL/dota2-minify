import datetime as dt
import os
import re
import threading
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

import dearpygui.dearpygui as dpg
from core import config, fs, utils
from ui import modal_shared, window
from ui import shared as shared

from browsers.d2pfx import config as browser_config
from browsers.d2pfx.data import DataManager


def _format_d2pfx_updated_date(mod):
    # Return a compact Updated label only when D2PFX supplies date metadata.
    if not isinstance(mod, dict):
        return None
    meta = mod.get("meta", {})
    if not isinstance(meta, dict):
        return None
    raw = meta.get("date")
    if raw is None or raw == "" or raw is False:
        return None

    parsed_date = None
    try:
        numeric = float(raw)
    except (TypeError, ValueError):
        numeric = None

    if numeric is not None:
        if numeric == 0:
            return None
        # Accept Unix seconds or milliseconds; D2PFX can change catalogue producers.
        if abs(numeric) >= 100_000_000_000:
            numeric /= 1000.0
        try:
            parsed_date = dt.datetime.fromtimestamp(numeric, tz=dt.timezone.utc).date()
        except (OverflowError, OSError, ValueError):
            parsed_date = None
    else:
        text = str(raw).strip()
        if not text:
            return None
        try:
            parsed_date = dt.datetime.fromisoformat(text.replace("Z", "+00:00")).date()
        except ValueError:
            try:
                parsed_date = dt.date.fromisoformat(text)
            except ValueError:
                # Keep a short source-provided date rather than inventing one.
                return f"Updated {text}" if len(text) <= 32 else None

    return f"Updated {parsed_date.strftime('%b')} {parsed_date.day}, {parsed_date.year}" if parsed_date else None


class BrowserUI:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.data_manager = DataManager()
        self.textures_registry = "d2pfx_textures"
        self.selected_category = None
        self.loading_lock = threading.Lock()
        self.loading_previews = set()
        self.is_loading_data = False
        self.current_rendering_cat = None
        self.download_executor = ThreadPoolExecutor(max_workers=5)
        self.current_cols = 2
        self.installed_mods = {}  # mod_name -> mod_dir
        self.category_filter = ""
        self.mod_filter = ""

        # Register windows for resize
        for tag in ["d2pfx_browser_window", "d2pfx_details_modal"]:
            if tag not in shared.extra_windows_to_resize:
                shared.extra_windows_to_resize.append(tag)

        self._setup_textures()

    def _setup_textures(self):
        if not dpg.does_item_exist(self.textures_registry):
            with dpg.texture_registry(tag=self.textures_registry):
                pass

        if not dpg.does_item_exist("selected_cat_theme"):
            with dpg.theme(tag="selected_cat_theme"):
                with dpg.theme_component(dpg.mvSelectable):
                    dpg.add_theme_color(dpg.mvThemeCol_Header, (20, 78, 76, 190))
                    dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (30, 108, 104, 220))
                    dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (42, 137, 130, 255))
                    dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255))

    def render(self):
        if not dpg.does_item_exist("d2pfx_browser_window"):
            with dpg.window(
                tag="d2pfx_browser_window",
                label="D2PFX Browser",
                width=shared.window_width,
                height=shared.window_height,
                no_move=True,
                no_resize=True,
                no_collapse=True,
                show=False,
            ):
                from ui import gui

                gui.register_persistent_window("d2pfx_browser_window")
                with dpg.group(horizontal=True):
                    # Sidebar
                    with dpg.child_window(width=180, tag="d2pfx_sidebar"):
                        dpg.add_input_text(
                            hint="Search categories...",
                            width=-1,
                            callback=lambda s, a: self.render_categories(a),
                            indent=1,
                            tag="d2pfx_search_categories",
                        )
                        with dpg.group(tag="d2pfx_category_list"):
                            pass

                    # Main Content
                    with dpg.group():
                        with dpg.table(header_row=False, width=-1):
                            dpg.add_table_column()
                            dpg.add_table_column(width_fixed=True, init_width_or_weight=350)
                            with dpg.table_row():
                                with dpg.group():
                                    dpg.add_text("Select a category", tag="d2pfx_cat_title", color=(78, 208, 196))
                                    desc_text = dpg.add_text("", tag="d2pfx_cat_desc", wrap=0)
                                    if dpg.does_item_exist("small_font"):
                                        dpg.bind_item_font(desc_text, "small_font")

                                with dpg.group():
                                    dpg.add_text("D2PFX LIBRARY", tag="d2pfx_browser_eyebrow")
                                    dpg.add_text("Browse community mods", tag="d2pfx_browser_heading")
                                    dpg.add_text(
                                        "Installable packs, resources, and community tools",
                                        tag="d2pfx_browser_subtitle",
                                    )
                                    if dpg.does_item_exist("large_font"):
                                        dpg.bind_item_font("d2pfx_browser_heading", "large_font")
                                    for item_tag, theme_tag in (
                                        ("d2pfx_browser_eyebrow", "dashboard_title_theme"),
                                        ("d2pfx_browser_heading", "dashboard_product_theme"),
                                        ("d2pfx_browser_subtitle", "dashboard_muted_theme"),
                                    ):
                                        if dpg.does_item_exist(theme_tag):
                                            dpg.bind_item_theme(item_tag, theme_tag)
                                    dpg.add_input_text(
                                        hint="Search D2PFX...",
                                        width=-1,
                                        callback=lambda s, a: self.render_mods(self.selected_category, a),
                                        tag="d2pfx_search_mods",
                                    )
                                    import_btn = dpg.add_button(
                                        label="Import pack",
                                        tag="d2pfx_import_pack_button",
                                        width=-1,
                                        height=30,
                                        callback=lambda s, a: self.open_pack_importer(),
                                    )
                                    if dpg.does_item_exist("main_primary_button_theme"):
                                        dpg.bind_item_theme(import_btn, "main_primary_button_theme")
                                    with dpg.tooltip(import_btn):
                                        dpg.add_text(
                                            "Import a D2PFX share link or downloaded pack ZIP. You can remove imported components individually later."
                                        )
                                    meta_btn = dpg.add_button(
                                        label="Refresh list",
                                        width=-1,
                                        height=28,
                                        callback=lambda s, a: self.prune_metadata_cache(),
                                    )
                                    with dpg.tooltip(meta_btn):
                                        dpg.add_text("Reload the D2PFX categories and mod list from fresh metadata.")
                                    imgs_btn = dpg.add_button(
                                        label="Reload images",
                                        width=-1,
                                        height=28,
                                        callback=lambda s, a: self.prune_image_cache(),
                                    )
                                    with dpg.tooltip(imgs_btn):
                                        dpg.add_text("Clear cached previews so D2PFX images are downloaded again.")

                        dpg.add_spacer(height=5)

                        with dpg.child_window(tag="d2pfx_mods_view", border=False):
                            pass

        if not dpg.does_item_exist("d2pfx_handlers"):
            with dpg.handler_registry(tag="d2pfx_handlers"):
                dpg.add_key_press_handler(key=dpg.mvKey_Escape, callback=self.on_escape)

        dpg.configure_item("d2pfx_browser_window", show=True)
        window.on_resize()
        self.sync_installed_mods_from_disk()
        self.load_data()

    def get_optimization_installable_names(self):
        """Use D2PFX's own allow-list when present, with a safe rc6-era fallback."""
        fallback = {"Default Wards", "Tinker Lite Machines"}
        try:
            constants = self.data_manager.constants if isinstance(self.data_manager.constants, dict) else {}
            rules = constants.get("addToCartRules", {})
            allowed = rules.get("allowedMods", {}).get("optimization", []) if isinstance(rules, dict) else []
            if isinstance(allowed, list) and allowed:
                return {str(name) for name in allowed}
        except Exception:
            pass
        return fallback

    def is_installable_mod(self, mod, cat_id=None):
        """Return True only when a catalogue card can be safely managed as a Minify mod."""
        cat_id = cat_id or self.selected_category
        name = str(mod.get("name", ""))

        # D2PFX intentionally treats most Optimization cards as tools/resources.
        # Respect its pack allow-list instead of presenting a broken Install button.
        if cat_id == "optimization" and name not in self.get_optimization_installable_names():
            return False

        candidates = []
        file_value = mod.get("file")
        if isinstance(file_value, str):
            candidates.append(file_value)
        for link in mod.get("links", []) or []:
            if isinstance(link, dict) and isinstance(link.get("url"), str):
                candidates.append(link["url"])

        return any(str(value).lower().split("?", 1)[0].endswith((".vpk", ".zip")) for value in candidates)

    def get_browse_url(self, mod):
        """Find the best non-install resource URL for a catalogue-only card."""
        links = mod.get("links", []) or []
        preferred_types = ("source", "guide", "author", "modded", "sender")
        for wanted in preferred_types:
            for link in links:
                if not isinstance(link, dict) or link.get("type") != wanted:
                    continue
                url = str(link.get("url", "")).strip()
                if url.startswith(("https://", "http://")) and not url.lower().split("?", 1)[0].endswith(
                    (".vpk", ".zip")
                ):
                    return url
        for link in links:
            if not isinstance(link, dict):
                continue
            url = str(link.get("url", "")).strip()
            if url.startswith(("https://", "http://")) and not url.lower().split("?", 1)[0].endswith((".vpk", ".zip")):
                return url
        return None

    def open_catalogue_resource(self, mod):
        url = self.get_browse_url(mod)
        if not url:
            modal_shared.show(
                "Not installable in Minify",
                [
                    f"'{mod.get('name', 'This item')}' is listed by D2PFX, but it is not a VPK/ZIP mod that Minify can install safely."
                ],
                [{"label": "OK"}],
            )
            return
        fs.open_thing(url)

    def sync_installed_mods_from_disk(self):
        """Synchronize Browser card state from top-level D2PFX manifests."""
        from core import base
        from patch import manifest_utils

        self.clear_installed_mods()
        try:
            mod_dirs = sorted(os.listdir(base.mods_dir), key=str.casefold)
        except Exception:
            return

        for mod_dir in mod_dirs:
            if mod_dir.startswith("_"):
                continue
            mod_path = os.path.join(base.mods_dir, mod_dir)
            if not os.path.isdir(mod_path):
                continue
            try:
                cfg = manifest_utils.get_mod(mod_path)
                browser_info = cfg.get("browser", {}) if isinstance(cfg, dict) else {}
                if isinstance(browser_info, dict) and browser_info.get("browser") == "d2pfx":
                    self.register_installed_mod(mod_dir, browser_info)
            except Exception:
                continue

    def open_pack_importer(self):
        from ui import checkboxes

        checkboxes.show_import_dialog()

    def on_escape(self):
        # Close modal first if it exists
        if dpg.does_item_exist("d2pfx_details_modal"):
            dpg.delete_item("d2pfx_details_modal")
            return

        # Close browser if no modal is active
        if dpg.does_item_exist("d2pfx_browser_window") and dpg.is_item_shown("d2pfx_browser_window"):
            dpg.configure_item("d2pfx_browser_window", show=False)

    def prune_metadata_cache(self):
        # Reset search filters
        self.category_filter = ""
        self.mod_filter = ""
        if dpg.does_item_exist("d2pfx_search_categories"):
            dpg.set_value("d2pfx_search_categories", "")
        if dpg.does_item_exist("d2pfx_search_mods"):
            dpg.set_value("d2pfx_search_mods", "")

        # Reset selected category to reload fresh
        self.selected_category = None

        # Show loading progress
        modal_shared.show_progress(["Pruning metadata cache...", "Fetching fresh D2PFX database..."])

        # Delete local files
        metadata_file = os.path.join(self.data_manager.cache_dir, "mods.json")
        constants_file = os.path.join(self.data_manager.cache_dir, "constants.json")
        fs.remove_path(metadata_file, constants_file)

        # Reset internal states
        self.data_manager.metadata = {}
        self.data_manager.constants = {}

        def _task():
            try:
                success = self.data_manager.load()
                if success:
                    self.render_categories()
                    cats = self.data_manager.get_categories()
                    if cats:
                        self.select_category(cats[0])
                    modal_shared.show(
                        "Pruning Complete",
                        ["D2PFX metadata cache has been cleared and refreshed successfully."],
                        [{"label": "OK"}],
                    )
                else:
                    modal_shared.show(
                        "Error",
                        ["Failed to reload D2PFX metadata.", "Please check your internet connection."],
                        [{"label": "OK"}],
                    )
                    if dpg.does_item_exist("d2pfx_category_list"):
                        dpg.delete_item("d2pfx_category_list", children_only=True)
                        dpg.add_text("Failed to load data.", parent="d2pfx_category_list", color=(255, 0, 0))
            except Exception as e:
                modal_shared.show("Error", [f"An unexpected error occurred: {str(e)}"], [{"label": "OK"}])

        threading.Thread(target=_task, daemon=True).start()

    def prune_image_cache(self):
        # Clear UI components first to release texture usage
        if dpg.does_item_exist("d2pfx_mods_view"):
            dpg.delete_item("d2pfx_mods_view", children_only=True)

        # Show progress modal
        modal_shared.show_progress(["Pruning image cache...", "Removing local preview images..."])

        # Delete local previews files
        fs.remove_path(self.data_manager.previews_dir)
        fs.create_dirs(self.data_manager.previews_dir)

        # Clear in-memory DPG textures
        if dpg.does_item_exist(self.textures_registry):
            dpg.delete_item(self.textures_registry)
        self._setup_textures()

        # Reset search filters
        self.category_filter = ""
        self.mod_filter = ""
        if dpg.does_item_exist("d2pfx_search_categories"):
            dpg.set_value("d2pfx_search_categories", "")
        if dpg.does_item_exist("d2pfx_search_mods"):
            dpg.set_value("d2pfx_search_mods", "")

        # Reset selected category and reload
        self.selected_category = None

        def _task():
            try:
                success = self.data_manager.load()
                if success:
                    self.render_categories()
                    cats = self.data_manager.get_categories()
                    if cats:
                        self.select_category(cats[0])
                    modal_shared.show(
                        "Pruning Complete",
                        ["D2PFX preview images cache has been cleared successfully."],
                        [{"label": "OK"}],
                    )
                else:
                    modal_shared.show("Error", ["Failed to reload D2PFX data."], [{"label": "OK"}])
            except Exception as e:
                modal_shared.show("Error", [f"An unexpected error occurred: {str(e)}"], [{"label": "OK"}])

        threading.Thread(target=_task, daemon=True).start()

    def update_layout(self):
        if not dpg.does_item_exist("d2pfx_browser_window") or not dpg.is_item_shown("d2pfx_browser_window"):
            return

        content_width = shared.window_width - 150  # sidebar
        new_cols = max(2, int(content_width / 200))  # Adjust divisor for card width

        if self.current_cols != new_cols:
            self.current_cols = new_cols
            if self.selected_category:
                self.render_mods(self.selected_category)

    def load_data(self):
        if self.is_loading_data:
            return
        self.is_loading_data = True

        def _task():
            try:
                if self.data_manager.load():
                    self.render_categories()
                    # Auto-select first category if none selected
                    if not self.selected_category:
                        cats = self.data_manager.get_categories()
                        if cats:
                            self.select_category(cats[0])
                else:
                    if dpg.does_item_exist("d2pfx_category_list"):
                        dpg.add_text("Failed to load data.", parent="d2pfx_category_list", color=(255, 0, 0))
            finally:
                self.is_loading_data = False

        threading.Thread(target=_task, daemon=True).start()

    def render_categories(self, filter_text=None):
        if filter_text is not None:
            self.category_filter = filter_text

        filter_text = self.category_filter

        if not dpg.does_item_exist("d2pfx_category_list"):
            return

        dpg.delete_item("d2pfx_category_list", children_only=True)
        categories = self.data_manager.get_categories()

        for cat_id in categories:
            name = self.data_manager.get_category_name(cat_id)
            if filter_text.lower() in name.lower():
                item = dpg.add_selectable(
                    label=name,
                    parent="d2pfx_category_list",
                    callback=lambda s, a, u: self.select_category(u),
                    user_data=cat_id,
                    indent=8,
                )
                if self.selected_category == cat_id:
                    dpg.set_value(item, True)
                    dpg.bind_item_theme(item, "selected_cat_theme")

    def select_category(self, cat_id):
        self.selected_category = cat_id
        name = self.data_manager.get_category_name(cat_id)
        desc = self.data_manager.get_category_description(cat_id)

        dpg.set_value("d2pfx_cat_title", name)
        dpg.set_value("d2pfx_cat_desc", desc)

        # Update sidebar highlighting
        if dpg.does_item_exist("d2pfx_category_list"):
            for child in dpg.get_item_children("d2pfx_category_list", 1):
                if dpg.get_item_user_data(child) == cat_id:
                    dpg.set_value(child, True)
                    dpg.bind_item_theme(child, "selected_cat_theme")
                else:
                    dpg.set_value(child, False)
                    dpg.bind_item_theme(child, 0)

        self.render_mods(cat_id)

    def render_mods(self, cat_id, filter_text=None):
        if filter_text is not None:
            self.mod_filter = filter_text

        filter_text = self.mod_filter
        self.current_rendering_cat = cat_id
        if dpg.does_item_exist("d2pfx_mods_view"):
            dpg.delete_item("d2pfx_mods_view", children_only=True)

        mods = self.data_manager.get_mods(cat_id)

        # Expand styles into individual mod entries
        expanded_mods = []
        for m in mods:
            if "styles" in m and isinstance(m["styles"], list):
                for style in m["styles"]:
                    m_style = m.copy()
                    m_style.update(style)
                    expanded_mods.append(m_style)
            else:
                expanded_mods.append(m)
        mods = expanded_mods

        filter_nsfw = config.get("d2pfx_filter_nsfw", True)
        filter_anime = config.get("d2pfx_filter_anime", False)

        filtered_mods = []
        for m in mods:
            tags = m.get("tags", {})

            if filter_nsfw:
                is_adult = False
                if isinstance(tags, dict):
                    is_adult = any(k.lower() == "adult" and v for k, v in tags.items())
                elif isinstance(tags, list):
                    is_adult = any(t.lower() == "adult" for t in tags)
                if is_adult:
                    continue

            if filter_anime:
                is_anime = False
                if isinstance(tags, dict):
                    is_anime = any(k.lower() == "anime" and v for k, v in tags.items())
                elif isinstance(tags, list):
                    is_anime = any(t.lower() == "anime" for t in tags)
                if is_anime:
                    continue

            filtered_mods.append(m)
        mods = filtered_mods

        sort_mode = None
        if filter_text:
            filter_text = filter_text.lower()
            tokens = re.findall(r"(?:by:|tag:|sort:)?\S+", filter_text)

            filtered = mods
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
                        filtered = [m for m in filtered if any(val in t.lower() for t in m.get("tags", []))]
                elif token.startswith("sort:"):
                    sort_mode = token[5:]
                else:
                    filtered = [
                        m for m in filtered if token in m.get("name", "").lower() or token in m.get("label", "").lower()
                    ]
            mods = filtered

        if sort_mode:
            if sort_mode == "a-z":
                mods.sort(key=lambda m: m.get("name", "").lower())
            elif sort_mode == "z-a":
                mods.sort(key=lambda m: m.get("name", "").lower(), reverse=True)
            elif sort_mode == "new":
                mods.sort(key=lambda m: m.get("meta", {}).get("date", 0), reverse=True)
            elif sort_mode == "old":
                mods.sort(key=lambda m: m.get("meta", {}).get("date", 0))

        def _task():
            if not dpg.does_item_exist("d2pfx_mods_view") or self.current_rendering_cat != cat_id:
                return

            try:
                # Grid layout
                if not dpg.does_item_exist("d2pfx_mods_view"):
                    return
                grid = dpg.add_table(
                    parent="d2pfx_mods_view",
                    header_row=False,
                    policy=dpg.mvTable_SizingStretchProp,
                    borders_innerH=True,
                    borders_outerH=True,
                    borders_innerV=True,
                    borders_outerV=True,
                    width=-1,
                )
                cols = min(len(mods), self.current_cols) if mods else 1
                for _ in range(cols):
                    if not dpg.does_item_exist(grid):
                        return
                    dpg.add_table_column(parent=grid)

                current_row = None
                for i, mod in enumerate(mods):
                    # Check for disruption
                    if self.current_rendering_cat != cat_id:
                        return

                    if not isinstance(mod, dict):
                        continue

                    if i % cols == 0:
                        if not dpg.does_item_exist(grid):
                            return
                        current_row = dpg.add_table_row(parent=grid)

                    if not dpg.does_item_exist(current_row):
                        continue

                    try:
                        with dpg.group(parent=current_row, width=150):
                            # 1. Preview/Image (Top) - Use child_window to reserve space
                            preview_tag = f"d2pfx_grid_prev_{i}"
                            with dpg.child_window(
                                tag=preview_tag,
                                width=150,
                                height=100,
                                border=False,
                                no_scrollbar=True,
                                no_scroll_with_mouse=True,
                            ):
                                pass
                            self.load_preview(cat_id, mod.get("preview"), preview_tag, width=150, height=100)

                            dpg.add_spacer(height=2)

                            # 2. Title
                            name = mod.get("name", "Unknown")
                            label = mod.get("label")
                            display_name = f"{name} ({label})" if label else name
                            dpg.add_text(display_name, color=(255, 255, 255), wrap=150)

                            # 3. Author / Sender
                            author = mod.get("author")
                            sender = mod.get("sender")

                            author_strs = []
                            if author:
                                if isinstance(author, list):
                                    author_strs.append(f"By: {', '.join(str(x) for x in author)}")
                                else:
                                    author_strs.append(f"By: {author}")

                            if sender:
                                if isinstance(sender, list):
                                    author_strs.append(f"Sender: {', '.join(str(x) for x in sender)}")
                                else:
                                    author_strs.append(f"Sender: {sender}")

                            if author_strs:
                                for author_str in author_strs:
                                    author_item = dpg.add_text(author_str, color=(150, 150, 150), wrap=150)
                                    if dpg.does_item_exist("small_font"):
                                        dpg.bind_item_font(author_item, "small_font")

                            # 4. Updated date (only when D2PFX supplies one)
                            updated_label = _format_d2pfx_updated_date(mod)
                            if updated_label:
                                updated_item = dpg.add_text(updated_label, color=(198, 151, 92), wrap=150)
                                if dpg.does_item_exist("small_font"):
                                    dpg.bind_item_font(updated_item, "small_font")

                            # 5. Tags
                            tags = mod.get("tags", [])
                            if tags:
                                tags_item = dpg.add_text(f"{', '.join(tags)}", color=(100, 100, 255), wrap=150)
                                if dpg.does_item_exist("small_font"):
                                    dpg.bind_item_font(tags_item, "small_font")

                            dpg.add_spacer(height=5)

                            # 5. Action Button (Install/Remove)
                            mod_name = mod.get("name", "Unknown")
                            label = mod.get("label")
                            is_installed = (mod_name, cat_id, label) in self.installed_mods

                            if is_installed:
                                installed_text = dpg.add_text("● Installed", color=(105, 205, 135))
                                if dpg.does_item_exist("small_font"):
                                    dpg.bind_item_font(installed_text, "small_font")
                                remove_btn = dpg.add_button(
                                    label="Remove",
                                    width=-1,
                                    callback=lambda s, a, u: self.uninstall_mod(u),
                                    user_data=mod,
                                )
                                dpg.bind_item_theme(remove_btn, "danger_button_theme")
                                with dpg.tooltip(remove_btn):
                                    dpg.add_text(
                                        "Remove only this D2PFX component. Other imported pack components are left installed."
                                    )
                            else:
                                is_installable = self.is_installable_mod(mod, cat_id)
                                if is_installable:
                                    dpg.add_button(
                                        label="Install",
                                        width=-1,
                                        callback=lambda s, a, u: self.install_mod(u),
                                        user_data=mod,
                                    )
                                else:
                                    browse_url = self.get_browse_url(mod)
                                    action_label = "Open" if browse_url else "Info Only"
                                    action_btn = dpg.add_button(
                                        label=action_label,
                                        width=-1,
                                        callback=lambda s, a, u: self.open_catalogue_resource(u),
                                        user_data=mod,
                                    )
                                    with dpg.tooltip(action_btn):
                                        if browse_url:
                                            dpg.add_text(
                                                "D2PFX lists this as a resource/tool rather than an installable Minify mod. Open its linked page instead."
                                            )
                                        else:
                                            dpg.add_text(
                                                "This D2PFX catalogue item has no VPK/ZIP payload that Minify can safely install."
                                            )
                            dpg.add_spacer(height=10)
                    except (SystemError, Exception):
                        continue
            except (SystemError, Exception):
                return

        threading.Thread(target=_task, daemon=True).start()

    def clear_installed_mods(self):
        self.installed_mods.clear()

    def register_installed_mod(self, mod_dir, browser_info):
        mod_name = browser_info.get("name")
        cat_id = browser_info.get("category")
        label = browser_info.get("label")
        if mod_name and cat_id:
            self.installed_mods[(mod_name, cat_id, label)] = mod_dir

    def apply_fallback_icon(self, parent, width, height):
        if dpg.does_item_exist(parent):
            dpg.delete_item(parent, children_only=True)
            if dpg.does_item_exist("d2pfx_texture_tag"):
                dpg.add_image("d2pfx_texture_tag", parent=parent, width=width, height=height)
            dpg.configure_item(parent, show=True)

    def load_preview(self, cat_id, filename, parent, width=120, height=90):
        if not filename or filename.endswith(".mp4"):
            self.apply_fallback_icon(parent, width, height)
            return

        # Handle full URLs if present
        if filename.startswith("http"):
            url = filename
            clean_filename = os.path.basename(filename)
        else:
            if filename.endswith(".webp"):
                filename = filename.replace(".webp", ".jpg")

            # Encode URL parts (especially spaces in filename)
            encoded_cat = urllib.parse.quote(cat_id)
            encoded_file = urllib.parse.quote(filename)

            url = self.data_manager.get_preview_url(encoded_cat, encoded_file)
            clean_filename = filename

        cat_preview_dir = os.path.join(self.data_manager.previews_dir, utils.sanitize_win_path(cat_id))
        if not os.path.exists(cat_preview_dir):
            os.makedirs(cat_preview_dir, exist_ok=True)

        local_path = os.path.join(cat_preview_dir, utils.sanitize_win_path(clean_filename))

        # Sanitize texture tag (remove spaces)
        texture_tag = f"d2pfx_tex_{cat_id}_{clean_filename}".replace(" ", "_")

        def _add_to_ui():
            if dpg.does_item_exist(parent):
                if not dpg.does_item_exist(texture_tag):
                    return

                dpg.delete_item(parent, children_only=True)
                dpg.add_image(texture_tag, parent=parent, width=width, height=height)
                dpg.configure_item(parent, show=True)

        # Sync check if already in DPG texture registry
        if dpg.does_item_exist(texture_tag):
            _add_to_ui()
            return

        def _load():
            # If not locally present, download it (if not already downloading)
            if not os.path.exists(local_path):
                with self.loading_lock:
                    load_key = f"{cat_id}_{clean_filename}"
                    if load_key in self.loading_previews:
                        return
                    self.loading_previews.add(load_key)

                try:
                    if not fs.download_file(url, local_path):
                        # Fallback: Try root previews folder if category-specific fails
                        root_url = url.replace(f"previews/{cat_id}/", "previews/")
                        if root_url != url:
                            if not fs.download_file(root_url, local_path):
                                return
                        else:
                            return
                finally:
                    with self.loading_lock:
                        load_key = f"{cat_id}_{clean_filename}"
                        if load_key in self.loading_previews:
                            self.loading_previews.remove(load_key)

                if not os.path.exists(local_path):
                    self.apply_fallback_icon(parent, width, height)
                    return

            if not dpg.does_item_exist(parent):
                return

            try:
                # Native DPG image loading (JPG/PNG supported)
                if not os.path.exists(local_path) or os.path.getsize(local_path) == 0:
                    return

                res = dpg.load_image(local_path)
                if not res:
                    self.apply_fallback_icon(parent, width, height)
                    return
                w, h, channels, data = res
                # Sanitize texture tag (remove spaces)
                texture_tag = f"d2pfx_tex_{cat_id}_{clean_filename}".replace(" ", "_")

                if not dpg.does_item_exist(texture_tag):
                    dpg.add_static_texture(
                        width=w,
                        height=h,
                        default_value=data,
                        tag=texture_tag,
                        parent=self.textures_registry,
                    )

                if dpg.does_item_exist(parent):
                    dpg.add_image(texture_tag, parent=parent, width=width, height=height)
                    # Force a redraw of the parent
                    dpg.configure_item(parent, show=True)
                else:
                    pass
            except Exception:
                pass

        self.download_executor.submit(_load)

    def install_mod(self, mod):
        from core import base, config

        name = mod.get("name", "Unknown")
        label = mod.get("label")
        cat_id = self.selected_category
        if not self.is_installable_mod(mod, cat_id):
            modal_shared.show(
                "Not Installable",
                [f"'{name}' is a D2PFX resource/tool and does not expose a Minify-compatible VPK/ZIP payload."],
                [{"label": "OK"}],
            )
            return
        author = mod.get("author")
        sender = mod.get("sender")
        tags = mod.get("tags", [])
        links = mod.get("links", [])

        vpk_link = next((link for link in links if link.get("url", "").endswith(".vpk")), None)
        zip_link = next((link for link in links if link.get("url", "").endswith(".zip")), None)
        mod_url = None
        is_zip = False

        if mod.get("file"):
            f = mod.get("file")
            if f.endswith(".vpk"):
                mod_url = f
            elif f.endswith(".zip"):
                mod_url = f
                is_zip = True

        if not mod_url:
            if vpk_link:
                mod_url = vpk_link["url"]
            elif zip_link:
                mod_url = zip_link["url"]
                is_zip = True

        if not mod_url:
            modal_shared.show("Error", [f"No compatible mod file (.vpk/.zip) found for '{name}'."], [{"label": "OK"}])
            return

        if not mod_url.startswith("http"):
            mod_url = self.data_manager.get_file_url(cat_id, mod_url)

        mod_dir_name = f"D2PFX {cat_id.upper()} - {name}"
        if label:
            mod_dir_name = f"{mod_dir_name} {label}"
        target_dir = os.path.join(base.mods_dir, utils.sanitize_win_path(mod_dir_name))

        def _task():
            try:
                modal_shared.show_progress([f"Installing {name}...", "Downloading mod files..."])
                fs.create_dirs(target_dir)

                # 1. Download Mod File
                mod_dest = os.path.join(target_dir, os.path.basename(mod_url))
                if not self.data_manager.download_file(mod_url, mod_dest, progress_tag="modal_progress_status"):
                    raise Exception("Failed to download mod file.")

                # Handle extraction if zip
                if is_zip:
                    modal_shared.set_progress(0.9, "Extracting mod files...")
                    if not fs.extract_archive(mod_dest, target_dir):
                        raise Exception("Failed to extract mod archive.")
                    fs.remove_path(mod_dest)  # Clean up zip

                # 2. Download Preview for Minify local display
                preview_file = mod.get("preview")
                if preview_file:
                    preview_url = preview_file
                    if not preview_url.startswith("http"):
                        preview_url = self.data_manager.get_preview_url(cat_id, preview_file)

                    preview_dest = os.path.join(target_dir, "preview.jpg")
                    self.data_manager.download_file(preview_url, preview_dest)

                # 3. Create manifest.json
                modcfg = {
                    "browser": {
                        "browser": "d2pfx",
                        "name": name,
                        "category": cat_id,
                        "author": author,
                        "sender": sender,
                        "links": links,
                        "tags": tags,
                        "version": browser_config.VERSION,
                        "label": label,
                    },
                }

                if cat_id in browser_config.RENAME_CATEGORIES:
                    modcfg["order"] = 2

                config.write_json_file(os.path.join(target_dir, "manifest.json"), modcfg)

                # 4. Create notes.md
                version = modcfg["browser"]["version"]
                notes_content = f"Installed via D2PFX Browser {version}\n\n"
                if cat_id and cat_id.lower() != "unknown":
                    notes_content += f"Category: {cat_id}\n"

                # Process the four link types in order
                type_labels = {
                    "author": "Author",
                    "source": "Source",
                    "modded": "Modded",
                    "sender": "Sender",
                }

                for t_key in ["author", "source", "modded", "sender"]:
                    t_links = [l for l in links if l.get("type") == t_key]
                    t_vals = [l.get("name") or l.get("url") for l in t_links]
                    t_vals = [x for x in t_vals if x]
                    if t_vals:
                        notes_content += f"{type_labels[t_key]}: {', '.join(t_vals)}\n"

                # Tags
                tags_val = modcfg["browser"].get("tags")
                if tags_val:
                    if isinstance(tags_val, dict):
                        active_tags = [k for k, v in tags_val.items() if v]
                    elif isinstance(tags_val, list):
                        active_tags = tags_val
                    else:
                        active_tags = [str(tags_val)]

                    if active_tags:
                        notes_content += f"Tags: {', '.join(active_tags)}\n"

                with open(os.path.join(target_dir, "notes.md"), "w", encoding="utf-8") as f:
                    f.write(notes_content)

                modal_shared.show(
                    "Installation Complete",
                    [f"Mod '{name}' has been successfully installed!", "You can now see it in your mods list."],
                    [{"label": "Great!"}],
                )

                # Refresh main UI mods list if possible
                from ui import checkboxes

                checkboxes.refresh()

                # Refresh browser view
                self.render_mods(self.selected_category)

            except Exception as e:
                modal_shared.show("Installation Failed", [str(e)], [{"label": "OK"}])

        threading.Thread(target=_task, daemon=True).start()

    def uninstall_mod(self, mod):
        from core import base

        name = mod.get("name", "Unknown")
        cat_id = self.selected_category
        label = mod.get("label")
        if (name, cat_id, label) in self.installed_mods:
            mod_dir = self.installed_mods[(name, cat_id, label)]
            target_dir = os.path.join(base.mods_dir, mod_dir)

            try:
                fs.remove_path(target_dir)
                modal_shared.show(
                    "Uninstallation Complete",
                    [f"Mod '{name}' has been successfully removed."],
                    [{"label": "OK"}],
                )

                # Refresh main UI and scan
                from ui import checkboxes

                checkboxes.refresh()

                # Refresh browser view
                self.render_mods(self.selected_category)
            except Exception as e:
                modal_shared.show("Uninstallation Failed", [str(e)], [{"label": "OK"}])


def toggle():
    ui = BrowserUI.get_instance()
    if dpg.does_item_exist("d2pfx_browser_window"):
        if dpg.is_item_shown("d2pfx_browser_window"):
            dpg.configure_item("d2pfx_browser_window", show=False)
        else:
            ui.render()
    else:
        ui.render()
