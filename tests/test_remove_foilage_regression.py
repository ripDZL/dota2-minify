import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REMOVE_FOILAGE = ROOT / "Minify" / "mods" / "Remove Foilage"
DARK_TERRAIN = ROOT / "Minify" / "mods" / "Dark Terrain"
TREE_PREFIXES = (
    "materials/models/props_tree/",
    "models/props_tree/",
)


def test_remove_foilage_preserves_stock_tree_namespaces():
    entries = (REMOVE_FOILAGE / "blacklist.txt").read_text(encoding="utf-8").splitlines()

    assert not any(entry.startswith(TREE_PREFIXES) for entry in entries)
    assert "materials/models/props_nature/fern001.vmat_c" in entries


def test_dark_terrain_keeps_remove_foilage_dependency():
    manifest = json.loads((DARK_TERRAIN / "manifest.json").read_text(encoding="utf-8"))

    assert manifest.get("dependencies") == ["Remove Foilage"]
