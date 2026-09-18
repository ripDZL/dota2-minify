import importlib.util
import json
import struct
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "foliage_alias_smoke.py"
SPEC = importlib.util.spec_from_file_location("foliage_alias_smoke", SCRIPT)
assert SPEC and SPEC.loader
SMOKE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SMOKE)


def _resource(version):
    return struct.pack("<IHHII", 16, 12, version, 8, 0)


def _source_mod(tmp_path):
    source = tmp_path / "Remove Foilage"
    blank = source / "files" / SMOKE.STOCK_RESOURCE
    blank.parent.mkdir(parents=True)
    blank.write_bytes(_resource(1))
    (source / "blacklist.txt").write_text("materials/models/props_tree/tree_oak_leaves_08.vmat_c\n", encoding="utf-8")
    (source / "rerl.json").write_text("{}\n", encoding="utf-8")
    (source / "notes.md").write_text("test\n", encoding="utf-8")
    return source


def test_build_smoke_mod_preserves_blank_and_adds_private_stock_alias(tmp_path):
    source = _source_mod(tmp_path)
    output = tmp_path / "Remove Foilage - Private Alias Smoke"
    stock = _resource(2)

    metadata = SMOKE.build_smoke_mod(source, stock, output)

    assert (source / "files" / SMOKE.STOCK_RESOURCE).read_bytes() == _resource(1)
    assert (output / "files" / SMOKE.STOCK_RESOURCE).read_bytes() == _resource(1)
    assert (output / "files" / SMOKE.ALIAS_RESOURCE).read_bytes() == stock
    assert json.loads((output / "rerl.json").read_text(encoding="utf-8")) == SMOKE.RERL_RULES
    assert metadata["contains_local_dota_stock_asset"] is True
    assert metadata["redistribute"] is False
    assert (output / SMOKE.SMOKE_MARKER).is_file()
    assert "production \"Remove Foilage\" mod UNCHECKED" in (output / "SMOKE_README.txt").read_text(
        encoding="utf-8"
    )


def test_private_alias_redirect_stays_same_length():
    assert len(SMOKE.RERL_SOURCE.encode("utf-8")) == len(SMOKE.RERL_TARGET.encode("utf-8"))
    assert SMOKE.RERL_SOURCE.endswith("_05.vmat")
    assert SMOKE.RERL_TARGET.endswith("_09.vmat")


def test_build_smoke_mod_refuses_to_overwrite_unmarked_directory(tmp_path):
    source = _source_mod(tmp_path)
    output = tmp_path / "existing"
    output.mkdir()
    (output / "keep.txt").write_text("do not delete", encoding="utf-8")

    with pytest.raises(RuntimeError, match="Refusing to replace existing non-smoke output"):
        SMOKE.build_smoke_mod(source, _resource(2), output)

    assert (output / "keep.txt").read_text(encoding="utf-8") == "do not delete"


def test_write_smoke_zip_requires_generated_marker(tmp_path):
    output = tmp_path / "not-smoke"
    output.mkdir()

    with pytest.raises(RuntimeError, match="Not a generated foliage smoke directory"):
        SMOKE.write_smoke_zip(output, tmp_path / "bad.zip")
