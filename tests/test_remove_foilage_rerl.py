import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / "Minify" / "mods" / "Remove Foilage"


def test_remove_foilage_blanks_05_with_existing_blank_payload_and_preserves_blank_material():
    blank_payload = ROOT / "Minify" / "bin" / "blank-files" / "blank.vmat_c"
    override = MOD / "files" / "materials" / "models" / "props_tree" / "tree_oak_leaves_05.vmat_c"
    blacklist_lines = {
        line.strip()
        for line in (MOD / "blacklist.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    }

    assert override.read_bytes() == blank_payload.read_bytes()
    assert "materials/models/props_tree/tree_oak_leaves_08.vmat_c" in blacklist_lines
    assert "materials/models/props_tree/tree_oak_leaves_blank.vmat_c" not in blacklist_lines


def test_remove_foilage_rerl_redirect_is_narrow_and_same_length():
    rules = json.loads((MOD / "rerl.json").read_text(encoding="utf-8"))
    expected_redirect = {
        "materials/models/props_tree/tree_oak_leaves_05.vmat":
            "materials/models/props_tree/tree_oak_leaves_00.vmat"
    }

    assert rules == {
        "models/props_tree/tree_oak*.vmdl_c": expected_redirect,
        "models/props_tree/dire_tree00*.vmdl_c": expected_redirect,
    }

    source, target = next(iter(expected_redirect.items()))
    assert len(source.encode("utf-8")) == len(target.encode("utf-8"))
