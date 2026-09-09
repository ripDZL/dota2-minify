import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REMOVE_FOILAGE = ROOT / "Minify" / "mods" / "Remove Foilage"
DARK_TERRAIN = ROOT / "Minify" / "mods" / "Dark Terrain"
# Keep only the targeted leaf resources; stock tree/static/destruction models stay untouched.
EXPECTED_TREE_FOLIAGE = {
    "materials/models/props_tree/tree_oak_leaves_08.vmat_c",
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
    assert "materials/models/props_tree/tree_oak_leaves_05.vmat_c" not in entries
    assert "models/props_tree/tree_oak_leaves_05.vmdl_c" not in entries
    assert "materials/models/props_nature/fern001.vmat_c" in entries


def test_dark_terrain_keeps_remove_foilage_dependency():
    manifest = json.loads((DARK_TERRAIN / "manifest.json").read_text(encoding="utf-8"))

    assert manifest.get("dependencies") == ["Remove Foilage"]
