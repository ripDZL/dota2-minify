import importlib.util
import json
import struct
from pathlib import Path

import pytest

from core import foliage_smoke as SMOKE


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "foliage_alias_smoke.py"
DEVTOOLS = (ROOT / "Minify" / "ui" / "dev_tools.py").read_text(encoding="utf-8")


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
    output = tmp_path / SMOKE.SMOKE_MOD_NAME
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


def test_cli_loads_without_generating_stock_content():
    spec = importlib.util.spec_from_file_location("foliage_alias_smoke_cli", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert callable(module.discover_dota_pak)
    assert callable(module.main)


def test_portable_developer_tools_exposes_opt_in_smoke_generator():
    assert "def _generate_foliage_alias_smoke():" in DEVTOOLS
    assert 'foliage_smoke.build_from_vpk(constants.dota_game_pak_path)' in DEVTOOLS
    assert '"Generate _09 foliage smoke mod"' in DEVTOOLS
    assert "checkboxes.refresh()" in DEVTOOLS
