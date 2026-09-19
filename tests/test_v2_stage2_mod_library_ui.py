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


def test_v2_mod_library_restores_persistent_legacy_list_view_with_card_toggle():
    grid = (WEB / "lib" / "components" / "ModGrid.svelte").read_text(encoding="utf-8")
    row = (WEB / "lib" / "components" / "ModListRow.svelte").read_text(encoding="utf-8")

    for token in (
        'type ViewMode = "list" | "cards";',
        'let viewMode: ViewMode = "list";',
        'MOD_VIEW_KEY = "minify.mod-library.view-mode"',
        'window.localStorage.getItem(MOD_VIEW_KEY)',
        'window.localStorage.setItem(MOD_VIEW_KEY, mode)',
        'on:click={() => setViewMode("list")}',
        'on:click={() => setViewMode("cards")}',
        'listGroupLabel(groupKey)',
        'aria-expanded={!collapsedGroups[groupKey]}',
        "<ModListRow",
    ):
        assert token in grid

    for label in ("Standard Mods", "Collections", "D2PFX · ", "VPK Mods"):
        assert label in grid

    assert "class:has-preview={Boolean(preview)}" in row
    assert "width: 64px;" in row
    assert "height: 36px;" in row
    assert "{#if preview}" in row
    assert "metadata.join" in row
    assert 'class="favorite-btn"' in row
    assert 'class="details-btn"' in row


def test_v2_mod_library_list_uses_legacy_collection_sections_and_bulk_controls():
    grid = (WEB / "lib" / "components" / "ModGrid.svelte").read_text(encoding="utf-8")

    for token in (
        'return `collection::${group}`',
        'key.startsWith("collection::")',
        'return key.slice("collection::".length) || "Collections"',
        ">Select all</button>",
        ">Clear</button>",
        "on:click={invertSelectable}>Invert</button>",
        "on:click={expandAllGroups}>Expand all</button>",
        "on:click={collapseAllGroups}>Collapse all</button>",
        "mod.always || mod.untickable ? mod",
    ):
        assert token in grid

    assert 'if (key.startsWith("d2pfx::")) {' in grid
    assert 'return `D2PFX · ${d2pfxCategoryLabel(category)}`;' in grid
    assert 'if (key === "vpk") return "VPK Mods";' in grid


def test_v2_mod_library_list_has_rc7_all_none_controls_per_section():
    grid = (WEB / "lib" / "components" / "ModGrid.svelte").read_text(encoding="utf-8")

    for token in (
        "function allModsInListGroup(key: string)",
        "function totalInListGroup(key: string): number",
        "async function setListGroupSelectable(groupKey: string, value: boolean)",
        'listGroupKey(mod) === groupKey && !mod.always && !mod.untickable',
        'class="list-group-actions"',
        "Select in this section",
        'on:click={() => setListGroupSelectable(groupKey, true)}>All</button>',
        'on:click={() => setListGroupSelectable(groupKey, false)}>None</button>',
        "{selectedInListGroup(groupKey)}/{totalInListGroup(groupKey)} selected",
    ):
        assert token in grid

    helper = grid[grid.index("async function setListGroupSelectable"):grid.index("function expandAllGroups")]
    assert "filteredMods" not in helper


def test_v2_hero_section_exposes_d2pfx_aware_default_selector():
    grid = (WEB / "lib" / "components" / "ModGrid.svelte").read_text(encoding="utf-8")
    global_types = (WEB / "global.d.ts").read_text(encoding="utf-8")

    for token in (
        "async function applyHeroDefaultsWithoutD2pfx()",
        "api?.apply_hero_defaults_without_d2pfx?.()",
        'listGroupLabel(groupKey) === "Hero Mods"',
        "Defaults except D2PFX",
        "Enable Hero Mods defaults except heroes actually overridden by enabled D2PFX mods",
        "heroDefaultsStatus",
    ):
        assert token in grid

    assert "apply_hero_defaults_without_d2pfx?:" in global_types


def test_v2_d2pfx_installs_are_grouped_by_category_in_legacy_list_view():
    grid = (WEB / "lib" / "components" / "ModGrid.svelte").read_text(encoding="utf-8")

    for token in (
        'if (type === "d2pfx") {',
        'const category = String(mod?.category || "other").trim().toLowerCase() || "other";',
        'return `d2pfx::${category}`;',
        'function d2pfxCategoryLabel(value: string): string',
        'key.startsWith("d2pfx::")',
        'return `D2PFX · ${d2pfxCategoryLabel(category)}`;',
        'if (key.startsWith("d2pfx::")) return 2;',
    ):
        assert token in grid

    assert "D2PFX Mods" not in grid
