from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "V2_STAGING"
MINIFY = STAGE / "Minify"


def test_v2_exact_architecture_tree_is_materialized():
    files = [path for path in MINIFY.rglob("*") if path.is_file()]
    assert len(files) >= 585

    for relative in (
        "__main__.py",
        "core/base.py",
        "core/plugin_sdk.py",
        "core/registry.py",
        "patch/__init__.py",
        "plugins/d2pfx/api.py",
        "themes/dark.css",
        "ui/app.py",
        "ui/services/mod_service.py",
        "ui/web/package-lock.json",
        "ui/web/src/App.svelte",
        "mods/Dark Terrain/manifest.json",
        "mods/Remove Foliage/remap.json",
    ):
        assert (MINIFY / relative).is_file(), relative

    for relative in (
        "pyproject.toml",
        "uv.lock",
        "scripts/Minify.spec",
        "scripts/build.py",
    ):
        assert (STAGE / relative).is_file(), relative


def test_v2_display_identity_keeps_internal_rc4_compatibility():
    source = (MINIFY / "core" / "base.py").read_text(encoding="utf-8")
    assert 'VERSION = "2rc4"' in source
    assert 'FORK_BUILD = "v21.4-hardening"' in source
    assert "DISPLAY_VERSION = FORK_BUILD" in source
    assert 'TITLE = f"Minify {DISPLAY_VERSION}"' in source


def test_v2_never_auto_injects_prelaunch_into_steam_options():
    steam = (MINIFY / "core" / "steam.py").read_text(encoding="utf-8")
    patch = (MINIFY / "patch" / "__init__.py").read_text(encoding="utf-8")
    settings = json.loads((MINIFY / "bin" / "settings.json").read_text(encoding="utf-8"))

    start = steam.index("def add_prelaunch_to_launch_options(")
    end = steam.index("\ndef fix_launch_options(", start)
    compatibility_shim = steam[start:end]
    assert "return False" in compatibility_shim
    assert '"UserLocalConfigStore"' not in compatibility_shim
    assert "vdf.dump" not in compatibility_shim
    assert "add_prelaunch_to_launch_options(" not in patch
    assert all(item.get("key") != "patch_on_launch" for item in settings)


def test_v2_main_menu_background_keeps_both_collapse_rules():
    css = (MINIFY / "mods" / "Remove Main Menu Background" / "styling.css").read_text(
        encoding="utf-8"
    )
    assert "DOTADashboardBackgroundManager:not(.Hidden)" in css
    assert "#FrontpageContents" in css
    assert css.count("visibility: collapse;") >= 2
