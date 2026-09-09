import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REMOVE_FOILAGE = ROOT / "Minify" / "mods" / "Remove Foilage"
DARK_TERRAIN = ROOT / "Minify" / "mods" / "Dark Terrain"
# Current Dota tree-safe split: only the unreferenced _08 leaf material stays blanked.
EXPECTED_TREE_FOLIAGE = {
    "materials/models/props_tree/tree_oak_leaves_08.vmat_c",
}
PRESERVED_TREE_RESOURCES = {
    "materials/models/props_tree/tree_oak_leaves_05.vmat_c",
    "models/props_tree/tree_oak_leaves_05.vmdl_c",
    "materials/models/props_tree/tree_oak_leaves_blank.vmat_c",
    "models/props_tree/tree_oak_leaves_08.vmdl_c",
}


def test_remove_foilage_keeps_only_targeted_tree_leaf_resources():
    entries = (REMOVE_FOILAGE / "blacklist.txt").read_text(encoding="utf-8").splitlines()
    tree_entries = {
        entry
        for entry in entries
        if entry.startswith("materials/models/props_tree/")
        or entry.startswith("models/props_tree/")
    }

    assert tree_entries == EXPECTED_TREE_FOLIAGE
    for resource in PRESERVED_TREE_RESOURCES:
        assert resource not in entries
    assert "materials/models/props_nature/fern001.vmat_c" in entries


def test_dark_terrain_does_not_force_remove_foilage():
    manifest = json.loads((DARK_TERRAIN / "manifest.json").read_text(encoding="utf-8"))

    assert manifest.get("dependencies") == []
