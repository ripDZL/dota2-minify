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
