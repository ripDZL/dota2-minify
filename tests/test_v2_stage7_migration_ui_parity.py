import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "V2_STAGING" / "Minify"


def test_v2_config_and_ui_state_writes_are_atomic():
    config_source = (STAGE / "core" / "config.py").read_text(encoding="utf-8")
    state_source = (STAGE / "core" / "utils.py").read_text(encoding="utf-8")

    for token in (
        'tempfile.mkstemp(prefix=".minify-config-"',
        "os.replace(temporary, absolute)",
        "os.path.lexists(absolute) and os.path.islink(absolute)",
    ):
        assert token in config_source

    for token in (
        'tempfile.mkstemp(prefix=".minify-states-"',
        "os.replace(temporary, target)",
        "os.path.lexists(target) and os.path.islink(target)",
    ):
        assert token in state_source


def test_v2_nested_collection_migrations_are_bounded_and_recursive():
    source = (STAGE / "core" / "migrations.py").read_text(encoding="utf-8")
    for token in (
        "MAX_MIGRATION_MOD_DIRS = 4096",
        "MAX_MIGRATION_DEPTH = 12",
        "def _iter_mod_directories():",
        "if os.path.islink(path) or not os.path.isdir(path):",
        "for mod_path in _iter_mod_directories() or ():",
        'os.path.relpath(mod_path, base.mods_dir)',
    ):
        assert token in source


def test_v2_settings_restore_rc7_path_controls():
    settings = json.loads((STAGE / "bin" / "settings.json").read_text(encoding="utf-8"))
    by_key = {item["key"]: item for item in settings}
    assert by_key["steam_root"]["type"] == "inputbox"
    assert by_key["steam_library"]["type"] == "inputbox"
    assert by_key["output_path"]["type"] == "inputbox"
    assert "restart required" in by_key["steam_root"]["text"].lower()
    assert "restart required" in by_key["steam_library"]["text"].lower()


def test_v2_mod_library_restores_state_filters_sorting_and_selection_count():
    source = (
        STAGE / "ui" / "web" / "src" / "lib" / "components" / "ModGrid.svelte"
    ).read_text(encoding="utf-8")
    for token in (
        'let stateFilter = "all";',
        'let sortMode = "name-asc";',
        "function stateMatches(",
        "function sortMods(",
        'value="selected">Selected',
        'value="unselected">Unselected',
        'value="enabled-first">Enabled first',
        'value="file-priority">File priority',
        "selectedCount} selected",
    ):
        assert token in source


def test_v2_activity_terminal_restores_copy_and_select_controls():
    source = (
        STAGE / "ui" / "web" / "src" / "lib" / "components" / "Terminal.svelte"
    ).read_text(encoding="utf-8")
    for token in (
        "function selectAllLogs()",
        "async function copyAllLogs()",
        "navigator.clipboard.writeText(text)",
        'on:click={copyAllLogs}>Copy</button>',
        'on:click={selectAllLogs}>Select all</button>',
    ):
        assert token in source
