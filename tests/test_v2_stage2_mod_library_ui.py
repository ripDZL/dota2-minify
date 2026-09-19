from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "V2_STAGING" / "Minify" / "ui" / "web" / "src"


def test_v2_mod_cards_expose_favorite_control():
    source = (WEB / "lib" / "components" / "ModCard.svelte").read_text(encoding="utf-8")
    assert "export let favorite: boolean = false;" in source
    assert "export let onFavorite:" in source
    assert "Add to favorites" in source
    assert "Remove from favorites" in source


def test_v2_mod_library_ui_exposes_source_category_and_profile_controls():
    source = (WEB / "lib" / "components" / "ModGrid.svelte").read_text(encoding="utf-8")
    for token in (
        'value="collection">Collections',
        'value="d2pfx">D2PFX',
        'value="favorites">Favorites',
        "All categories",
        "api?.get_profiles",
        "api?.save_profile",
        "api?.apply_profile",
        "api?.duplicate_profile",
        "api?.delete_profile",
        "api?.set_mod_favorite",
        "onFavorite={toggleFavorite}",
    ):
        assert token in source


def test_v2_mod_library_ui_retains_compact_960px_breakpoint():
    source = (WEB / "lib" / "components" / "ModGrid.svelte").read_text(encoding="utf-8")
    assert "@media (max-width: 960px)" in source
    assert "flex-basis: 100%;" in source
    assert "min-height: 0;" in source
    assert "overflow-y: auto;" in source
