import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "V2_STAGING" / "Minify"
MOD = STAGE / "mods" / "Remove Foliage"


def test_v2_remove_foliage_uses_rc7_blank_and_same_length_rerl():
    blank_payload = STAGE / "bin" / "blank-files" / "blank.vmat_c"
    override = MOD / "files" / "materials" / "models" / "props_tree" / "tree_oak_leaves_05.vmat_c"
    rules = json.loads((MOD / "rerl.json").read_text(encoding="utf-8"))

    assert override.read_bytes() == blank_payload.read_bytes()
    source = "materials/models/props_tree/tree_oak_leaves_05.vmat"
    target = "materials/models/props_tree/tree_oak_leaves_00.vmat"
    assert rules == {
        "models/props_tree/tree_oak*.vmdl_c": {source: target},
        "models/props_tree/dire_tree00*.vmdl_c": {source: target},
    }
    assert len(source.encode("utf-8")) == len(target.encode("utf-8"))

    blacklist = {
        line.strip()
        for line in (MOD / "blacklist.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    }
    assert "materials/models/props_tree/tree_oak_leaves_08.vmat_c" in blacklist
    assert "materials/models/props_tree/tree_oak_leaves_blank.vmat_c" not in blacklist


def test_v2_rerl_engine_preserves_compiled_resource_ids_and_layout_contract():
    engine = (STAGE / "core" / "rerl.py").read_text(encoding="utf-8")
    processor = (STAGE / "patch" / "rerl_processor.py").read_text(encoding="utf-8")
    patch = (STAGE / "patch" / "__init__.py").read_text(encoding="utf-8")

    assert "Only same-byte-length UTF-8 replacements are accepted" in engine
    assert "patched[entry.string_offset : entry.string_offset + entry.string_length]" in engine
    assert "rerl.patch_resource_rerl(data, redirect_map)" in processor
    assert 'rerl_file = os.path.join(mod_path, "rerl.json")' in patch
    assert "rerl_processor.process(rerl_file, folder, dota_pak_contents)" in patch
    assert "elif conditions.workshop_installed and os.path.exists(remap_file)" in patch


def test_v2_foliage_private_alias_smoke_remains_local_only_and_unvalidated():
    source = (STAGE / "core" / "foliage_smoke.py").read_text(encoding="utf-8")
    app = (STAGE / "ui" / "app.py").read_text(encoding="utf-8")
    settings = (
        STAGE / "ui" / "web" / "src" / "lib" / "components" / "Settings.svelte"
    ).read_text(encoding="utf-8")

    for token in (
        'SOURCE_MOD_NAME = "Remove Foliage"',
        'SMOKE_MOD_NAME = "Remove Foliage - Private Alias Smoke"',
        'ALIAS_RESOURCE = "materials/models/props_tree/tree_oak_leaves_09.vmat_c"',
        '"contains_local_dota_stock_asset": True',
        '"redistribute": False',
        "validate_compiled_resource",
    ):
        assert token in source

    assert "def generate_foliage_alias_smoke(" in app
    assert "foliage_smoke.build_from_vpk(Path(constants.dota_game_pak_path))" in app
    assert "Generate _09 foliage smoke mod" in settings
    assert "No Valve stock asset is bundled or uploaded." in settings
