from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "V2_STAGING" / "Minify"


def test_v2_home_control_panel_restores_rc7_dashboard_surface():
    home = (
        STAGE / "ui" / "web" / "src" / "lib" / "components" / "Home.svelte"
    ).read_text(encoding="utf-8")
    header = (
        STAGE / "ui" / "web" / "src" / "lib" / "components" / "Header.svelte"
    ).read_text(encoding="utf-8")
    app = (STAGE / "ui" / "web" / "src" / "App.svelte").read_text(encoding="utf-8")

    for token in (
        "CONTROL PANEL",
        "Selected mods",
        "Restore points",
        "Patch state",
        "transactional restore enabled",
        "Review & Patch",
        "Rescan mods",
        "@media (max-width: 960px)",
    ):
        assert token in home

    assert "activeTab === 'home'" in header
    assert 'onTabChange("home")' in header

    assert 'let activeTab: string = "home";' in app
    assert 'import Home from "./lib/components/Home.svelte";' in app
    assert "onPatch={handlePatch}" in app
    assert "onRestore={openRestoreManager}" in app
    assert "onRescan={handleRescanMods}" in app
