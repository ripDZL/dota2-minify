"""Build a local-only Remove Foilage _09 alias smoke mod from current Dota files."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import struct
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import vpk

ROOT = Path(__file__).resolve().parents[1]
SOURCE_MOD = ROOT / "Minify" / "mods" / "Remove Foilage"
DEFAULT_OUTPUT = ROOT / "Minify" / "mods" / "Remove Foilage - Private Alias Smoke"

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


def _validate_compiled_resource(data: bytes, label: str) -> None:
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


def _candidate_from_library(library: Path) -> Path:
    return library / "steamapps" / "common" / "dota 2 beta" / "game" / "dota" / "pak01_dir.vpk"


def discover_dota_pak(explicit: str | None = None) -> Path:
    candidates: list[Path] = []
    if explicit:
        candidates.append(Path(explicit).expanduser())

    env_pak = os.environ.get("MINIFY_DOTA_PAK")
    if env_pak:
        candidates.append(Path(env_pak).expanduser())

    env_library = os.environ.get("STEAM_LIBRARY")
    if env_library:
        candidates.append(_candidate_from_library(Path(env_library).expanduser()))

    candidates.extend(
        [
            Path(r"C:\Program Files (x86)\Steam\steamapps\common\dota 2 beta\game\dota\pak01_dir.vpk"),
            Path(r"C:\Program Files\Steam\steamapps\common\dota 2 beta\game\dota\pak01_dir.vpk"),
            Path.home() / ".local" / "share" / "Steam" / "steamapps" / "common" / "dota 2 beta" / "game" / "dota" / "pak01_dir.vpk",
            Path.home() / ".steam" / "steam" / "steamapps" / "common" / "dota 2 beta" / "game" / "dota" / "pak01_dir.vpk",
        ]
    )

    seen: set[str] = set()
    for candidate in candidates:
        key = str(candidate)
        if key in seen:
            continue
        seen.add(key)
        if candidate.is_file():
            return candidate.resolve()

    raise FileNotFoundError(
        "Dota pak01_dir.vpk was not found. Pass --dota-pak with the full path to "
        "...\\dota 2 beta\\game\\dota\\pak01_dir.vpk."
    )


def read_stock_material(dota_pak_path: Path) -> bytes:
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
        raise ValueError(
            f"{STOCK_RESOURCE} is unexpectedly large ({len(data)} bytes); refusing smoke generation."
        )
    _validate_compiled_resource(data, "stock tree_oak_leaves_05.vmat_c")
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
                f"Delete it manually or choose another --output."
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

    _validate_compiled_resource(stock_bytes, "stock tree_oak_leaves_05.vmat_c")

    blank_path = source_mod / "files" / STOCK_RESOURCE
    if not blank_path.is_file():
        raise FileNotFoundError(f"Production blank override missing: {blank_path}")
    blank_bytes = blank_path.read_bytes()
    _validate_compiled_resource(blank_bytes, "production blank tree_oak_leaves_05.vmat_c")
    if stock_bytes == blank_bytes:
        raise ValueError("Extracted stock material matches the blank override; refusing invalid smoke package.")

    _prepare_output(source_mod, output_dir)

    alias_path = output_dir / "files" / ALIAS_RESOURCE
    alias_path.parent.mkdir(parents=True, exist_ok=True)
    alias_path.write_bytes(stock_bytes)

    (output_dir / "rerl.json").write_text(
        json.dumps(RERL_RULES, indent=2) + "\n",
        encoding="utf-8",
    )
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


def write_smoke_zip(output_dir: Path, zip_path: Path) -> None:
    output_dir = Path(output_dir)
    zip_path = Path(zip_path)
    if not (output_dir / SMOKE_MARKER).is_file():
        raise RuntimeError(f"Not a generated foliage smoke directory: {output_dir}")

    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(output_dir.rglob("*")):
            if path.is_symlink():
                raise RuntimeError(f"Refusing to archive symlink: {path}")
            if path.is_file():
                archive.write(path, Path(output_dir.name) / path.relative_to(output_dir))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a local-only Remove Foilage _09 alias smoke mod from current Dota stock files."
    )
    parser.add_argument(
        "--dota-pak",
        help="Full path to Dota game/dota/pak01_dir.vpk. Auto-detected for common Steam locations if omitted.",
    )
    parser.add_argument("--source-mod", type=Path, default=SOURCE_MOD)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--zip",
        action="store_true",
        help="Also create a private ZIP next to the output folder. The ZIP contains a Valve stock asset; do not redistribute it.",
    )
    args = parser.parse_args()

    dota_pak = discover_dota_pak(args.dota_pak)
    stock_bytes = read_stock_material(dota_pak)
    metadata = build_smoke_mod(args.source_mod, stock_bytes, args.output)

    print(f"Generated smoke mod: {args.output}")
    print(f"Stock source: {dota_pak}")
    print(f"Stock SHA-256: {metadata['stock_sha256']}")
    print("IMPORTANT: keep production 'Remove Foilage' unchecked during this smoke.")

    if args.zip:
        zip_path = args.output.with_suffix(".zip")
        write_smoke_zip(args.output, zip_path)
        print(f"Generated private smoke ZIP: {zip_path}")
        print("Do not commit or redistribute that ZIP; it contains a stock Dota material.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
