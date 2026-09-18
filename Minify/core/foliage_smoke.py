"""Local-only tooling for the private Remove Foilage _09 human smoke."""

from __future__ import annotations

import hashlib
import json
import shutil
import struct
from datetime import datetime, timezone
from pathlib import Path

import vpk
from core import base

SOURCE_MOD_NAME = "Remove Foilage"
SMOKE_MOD_NAME = "Remove Foilage - Private Alias Smoke"
STOCK_RESOURCE = "materials/models/props_tree/tree_oak_leaves_05.vmat_c"
ALIAS_RESOURCE = "materials/models/props_tree/tree_oak_leaves_09.vmat_c"
RERL_SOURCE = "materials/models/props_tree/tree_oak_leaves_05.vmat"
RERL_TARGET = "materials/models/props_tree/tree_oak_leaves_09.vmat"
SMOKE_MARKER = "_MINIFY_FOLIAGE_ALIAS_SMOKE.json"
MAX_STOCK_RESOURCE_BYTES = 8 * 1024 * 1024
KNOWN_SOURCE2_HEADER_VERSION = 12

RERL_RULES = {
    "models/props_tree/tree_oak*.vmdl_c": {RERL_SOURCE: RERL_TARGET},
    "models/props_tree/dire_tree00*.vmdl_c": {RERL_SOURCE: RERL_TARGET},
}

SMOKE_README = """LOCAL SMOKE ONLY — DO NOT COMMIT OR REDISTRIBUTE THIS GENERATED MOD

This folder contains a stock Dota material extracted from your local installation.

Test setup:
1. Keep the production "Remove Foilage" mod UNCHECKED.
2. Select only "Remove Foilage - Private Alias Smoke" for this foliage test.
3. Patch normally.
4. In Dota, verify:
   - normal stock trees remain visible;
   - the target foliage removed by tree_oak_leaves_05 stays gone;
   - tree/pathing collision still behaves normally.
5. Report PASS/FAIL for each item before any production alias change is made.

The generator keeps tree_oak_leaves_05 blank and copies your current stock
tree_oak_leaves_05 material to the private same-length tree_oak_leaves_09 alias.
Affected tree model RERL names are redirected from _05 to _09 without changing IDs.
"""


def default_source_mod() -> Path:
    return Path(base.mods_dir) / SOURCE_MOD_NAME


def default_output_dir() -> Path:
    return Path(base.mods_dir) / SMOKE_MOD_NAME


def validate_compiled_resource(data: bytes, label: str) -> None:
    if len(data) < 16:
        raise ValueError(f"{label} is shorter than a Source 2 resource header.")
    file_size, header_version, _version, block_offset, block_count = struct.unpack_from("<IHHII", data, 0)
    if header_version != KNOWN_SOURCE2_HEADER_VERSION:
        raise ValueError(f"{label} has unsupported Source 2 header version {header_version}.")
    if file_size != len(data):
        raise ValueError(f"{label} size mismatch: header={file_size}, actual={len(data)}.")
    table_start = 8 + block_offset
    table_end = table_start + block_count * 12
    if table_start < 16 or table_end > len(data):
        raise ValueError(f"{label} has an invalid Source 2 block table.")


def read_stock_material(dota_pak_path: Path) -> bytes:
    dota_pak_path = Path(dota_pak_path)
    if not dota_pak_path.is_file():
        raise FileNotFoundError(f"Dota VPK not found: {dota_pak_path}")

    pak = vpk.open(str(dota_pak_path))
    pak_file = pak.get_file(STOCK_RESOURCE)
    if pak_file is None:
        raise FileNotFoundError(f"{STOCK_RESOURCE} is missing from {dota_pak_path}.")

    data = pak_file.read()
    if not data:
        raise ValueError(f"{STOCK_RESOURCE} is empty in the Dota VPK.")
    if len(data) > MAX_STOCK_RESOURCE_BYTES:
        raise ValueError(f"{STOCK_RESOURCE} is unexpectedly large ({len(data)} bytes); refusing smoke generation.")
    validate_compiled_resource(data, "stock tree_oak_leaves_05.vmat_c")
    return data


def _prepare_output(source_mod: Path, output_dir: Path) -> None:
    source_real = source_mod.resolve()
    output_real = output_dir.resolve()
    if source_real == output_real or source_real in output_real.parents:
        raise ValueError("Smoke output must not replace or live inside the production Remove Foilage mod.")

    if output_dir.exists():
        marker = output_dir / SMOKE_MARKER
        if not output_dir.is_dir() or not marker.is_file():
            raise RuntimeError(
                f"Refusing to replace existing non-smoke output: {output_dir}. "
                "Delete it manually or choose another output directory."
            )
        shutil.rmtree(output_dir)

    for item in source_mod.rglob("*"):
        if item.is_symlink():
            raise RuntimeError(f"Refusing to copy symlink from production mod: {item}")

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_mod, output_dir)


def build_smoke_mod(source_mod: Path, stock_bytes: bytes, output_dir: Path) -> dict[str, object]:
    source_mod = Path(source_mod)
    output_dir = Path(output_dir)
    if not source_mod.is_dir():
        raise FileNotFoundError(f"Production Remove Foilage mod not found: {source_mod}")

    if len(RERL_SOURCE.encode("utf-8")) != len(RERL_TARGET.encode("utf-8")):
        raise RuntimeError("Private alias redirect is no longer same-length; smoke generation is unsafe.")

    validate_compiled_resource(stock_bytes, "stock tree_oak_leaves_05.vmat_c")

    blank_path = source_mod / "files" / STOCK_RESOURCE
    if not blank_path.is_file():
        raise FileNotFoundError(f"Production blank override missing: {blank_path}")
    blank_bytes = blank_path.read_bytes()
    validate_compiled_resource(blank_bytes, "production blank tree_oak_leaves_05.vmat_c")
    if stock_bytes == blank_bytes:
        raise ValueError("Extracted stock material matches the blank override; refusing invalid smoke package.")

    _prepare_output(source_mod, output_dir)

    alias_path = output_dir / "files" / ALIAS_RESOURCE
    alias_path.parent.mkdir(parents=True, exist_ok=True)
    alias_path.write_bytes(stock_bytes)

    (output_dir / "rerl.json").write_text(json.dumps(RERL_RULES, indent=2) + "\n", encoding="utf-8")
    (output_dir / "SMOKE_README.txt").write_text(SMOKE_README, encoding="utf-8")

    metadata: dict[str, object] = {
        "purpose": "Remove Foilage private _09 alias human smoke",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "stock_resource": STOCK_RESOURCE,
        "alias_resource": ALIAS_RESOURCE,
        "stock_sha256": hashlib.sha256(stock_bytes).hexdigest(),
        "stock_size": len(stock_bytes),
        "contains_local_dota_stock_asset": True,
        "redistribute": False,
    }
    (output_dir / SMOKE_MARKER).write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return metadata


def build_from_vpk(
    dota_pak_path: Path,
    source_mod: Path | None = None,
    output_dir: Path | None = None,
) -> dict[str, object]:
    source_mod = Path(source_mod) if source_mod is not None else default_source_mod()
    output_dir = Path(output_dir) if output_dir is not None else default_output_dir()
    stock_bytes = read_stock_material(Path(dota_pak_path))
    metadata = build_smoke_mod(source_mod, stock_bytes, output_dir)
    metadata["output_dir"] = str(output_dir)
    return metadata
