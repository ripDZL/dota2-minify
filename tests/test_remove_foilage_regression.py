import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REMOVE_FOILAGE = ROOT / "Minify" / "mods" / "Remove Foilage"
DARK_TERRAIN = ROOT / "Minify" / "mods" / "Dark Terrain"


def test_remove_foilage_preserves_referenced_oak_tree_assets():
    entries = set((REMOVE_FOILAGE / "blacklist.txt").read_text(encoding="utf-8").splitlines())

    assert "materials/models/props_tree/tree_oak_leaves_05.vmat_c" not in entries
    assert "models/props_tree/tree_oak_leaves_05.vmdl_c" not in entries
    assert "materials/models/props_tree/tree_oak_leaves_08.vmat_c" in entries
    assert "models/props_tree/tree_oak_leaves_08.vmdl_c" in entries


def test_dark_terrain_keeps_remove_foilage_dependency():
    manifest = json.loads((DARK_TERRAIN / "manifest.json").read_text(encoding="utf-8"))

    assert manifest.get("dependencies") == ["Remove Foilage"]
