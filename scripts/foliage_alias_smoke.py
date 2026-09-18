"""CLI for the local-only Remove Foilage _09 alias smoke generator."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Minify"))

from core import foliage_smoke  # noqa: E402


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
            Path.home()
            / ".local"
            / "share"
            / "Steam"
            / "steamapps"
            / "common"
            / "dota 2 beta"
            / "game"
            / "dota"
            / "pak01_dir.vpk",
            Path.home()
            / ".steam"
            / "steam"
            / "steamapps"
            / "common"
            / "dota 2 beta"
            / "game"
            / "dota"
            / "pak01_dir.vpk",
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


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a local-only Remove Foilage _09 alias smoke mod from current Dota stock files."
    )
    parser.add_argument(
        "--dota-pak",
        help="Full path to Dota game/dota/pak01_dir.vpk. Auto-detected for common Steam locations if omitted.",
    )
    parser.add_argument(
        "--source-mod",
        type=Path,
        default=ROOT / "Minify" / "mods" / foliage_smoke.SOURCE_MOD_NAME,
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "Minify" / "mods" / foliage_smoke.SMOKE_MOD_NAME,
    )
    args = parser.parse_args()

    dota_pak = discover_dota_pak(args.dota_pak)
    metadata = foliage_smoke.build_from_vpk(dota_pak, args.source_mod, args.output)

    print(f"Generated smoke mod: {metadata['output_dir']}")
    print(f"Stock source: {dota_pak}")
    print(f"Stock SHA-256: {metadata['stock_sha256']}")
    print("IMPORTANT: keep production 'Remove Foilage' unchecked during this smoke.")
    print("Do not commit or redistribute the generated smoke mod; it contains a stock Dota material.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
