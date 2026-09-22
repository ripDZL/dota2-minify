from __future__ import annotations

import ast
import datetime as dt
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "V2_STAGING" / "Minify"
DATA = STAGE / "plugins" / "d2pfx" / "data.py"
API = STAGE / "plugins" / "d2pfx" / "api.py"


def _date_env():
    source = API.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(API))
    wanted = {"_d2pfx_date_value", "_format_d2pfx_updated_date", "_d2pfx_date_sort_key"}
    nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in wanted]
    env = {"dt": dt, "Dict": dict, "Any": object}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(API), "exec"), env)
    return env



def _recent_env():
    source = DATA.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(DATA))
    manager = next(
        node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "DataManager"
    )
    method = next(
        node for node in manager.body if isinstance(node, ast.FunctionDef) and node.name == "get_recent_mods"
    )
    env = {
        "MAX_RECENT_MODS": 256,
        "BLACKLIST": ["fonts", "huds"],
        "_safe_category_id": lambda value: str(value),
    }
    exec(compile(ast.Module(body=[method], type_ignores=[]), str(DATA), "exec"), env)
    return env

def test_v2_d2pfx_preview_uses_data_branch_jpg_mirror():
    source = DATA.read_text(encoding="utf-8")
    assert 'PREVIEWS_URL = f"{BASE_URL}previews/"' in source
    assert 'filename = filename[:-5] + ".jpg"' in source
    assert "main/assets/previews/" not in source
    assert "def get_preview_fallback_url(self, filename):" in source


def test_v2_d2pfx_updated_date_matches_fork_behavior():
    env = _date_env()
    format_date = env["_format_d2pfx_updated_date"]

    assert format_date({"meta": {"date": 0}}) is None
    assert format_date({"meta": {"date": "2026-09-19"}}) == "Updated Sep 19, 2026"
    assert format_date({"meta": {"date": "2026-09-19T12:34:56Z"}}) == "Updated Sep 19, 2026"
    assert format_date({"meta": {"date": 1789821296000}}) == "Updated Sep 19, 2026"
    assert format_date({"meta": {"date": "legacy-date"}}) == "Updated legacy-date"


def test_v2_d2pfx_date_sort_accepts_mixed_catalogue_date_types():
    env = _date_env()
    sort_key = env["_d2pfx_date_sort_key"]
    mods = [
        {"name": "missing"},
        {"name": "iso", "meta": {"date": "2026-09-19"}},
        {"name": "seconds", "meta": {"date": 1789821296}},
        {"name": "milliseconds", "meta": {"date": 1789821296000}},
    ]
    ordered = sorted(mods, key=sort_key, reverse=True)
    assert ordered[-1]["name"] == "missing"
    assert {item["name"] for item in ordered[:3]} == {"iso", "seconds", "milliseconds"}


def test_v2_d2pfx_install_state_is_set_only_after_successful_install():
    browser = (STAGE / "plugins" / "d2pfx" / "src" / "D2pfxBrowser.svelte").read_text(encoding="utf-8")
    install_start = browser.index("  async function handleInstall")
    toggle_start = browser.index("  async function handleToggleEnabled", install_start)
    block = browser[install_start:toggle_start]

    call_index = block.index('callApi("install_mod"')
    state_index = block.index("await setModState", call_index)
    assert state_index > call_index
    assert "modRequestId" in browser


def test_v2_d2pfx_installed_preview_keeps_downloaded_image_type():
    source = API.read_text(encoding="utf-8")
    assert 'allowed_extensions={".jpg", ".jpeg", ".png", ".webp", ".gif"}' in source
    assert 'preview_dest = os.path.join(install_dir, f"preview{preview_extension}")' in source
    assert 'preview_dest = os.path.join(install_dir, "preview.webp")' not in source

def test_v2_d2pfx_recent_feed_resolves_live_entries_in_publisher_order():
    get_recent_mods = _recent_env()["get_recent_mods"]

    class Dummy:
        metadata = {
            "recentlyAddedMods": [
                {"name": "Newest Hero", "category": "heroes"},
                {"name": "Newest Courier", "category": "couriers"},
                {"name": "Older Hero", "category": "heroes"},
            ]
        }

        def __init__(self):
            self.calls = []

        def get_mods(self, category):
            self.calls.append(category)
            return {
                "heroes": [{"name": "Newest Hero"}, {"name": "Older Hero"}],
                "couriers": [{"name": "Newest Courier"}],
            }.get(category, [])

    manager = Dummy()
    result = get_recent_mods(manager)

    assert [item["name"] for item in result] == ["Newest Hero", "Newest Courier", "Older Hero"]
    assert [item["category_id"] for item in result] == ["heroes", "couriers", "heroes"]
    assert manager.calls == ["heroes", "couriers"]


def test_v2_d2pfx_recent_feed_and_freshness_are_exposed_to_browser():
    data_source = DATA.read_text(encoding="utf-8")
    api_source = API.read_text(encoding="utf-8")
    browser = (STAGE / "plugins" / "d2pfx" / "src" / "D2pfxBrowser.svelte").read_text(encoding="utf-8")

    assert 'RECENT_CATEGORY_ID = "__recent__"' in data_source
    assert "AUTO_REFRESH_SECONDS = 5 * 60" in data_source
    assert 'self.metadata.get("recentlyAddedMods", [])' in data_source
    assert '"name": "Recently Added"' in api_source
    assert 'if not sort_mode and not is_recent:' in api_source
    assert 'sort_mode = "new"' in api_source
    assert 'actual_category = str(m.get("category_id") or cat_id)' in api_source

    assert "function categoryForMod(m: D2Mod): string" in browser
    assert "return m.category_id || selectedCategory;" in browser
    assert 'cat_id: category' in browser
    assert "isInstalled(m, category, installedMods)" in browser

