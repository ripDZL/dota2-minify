# v2rc4 Semantic Port Plan

- Target: upstream `Minify-v2rc4` / `e444454684c2d7f809e7eef20a1b72d4422c50d7`; semantic port only, no raw merge/rebase.

## Stage 1 — Security substrate
- Carry fork `core/security.py` semantics first: `safe_relative_path`, `confined_destination`, bounded zlib, safe ZIP/TAR extraction, hash verification.
- Replace v2 `core/fs.py::download_file`: HTTPS policy where required, redirect/host validation, connect/read timeouts, content-length/stream caps, temp file + atomic replace, cleanup on failure.
- Replace v2 `core/fs.py::extract_archive`: no raw ZIP `extract`/`extractall`; reject traversal, absolute/drive paths, symlinks/reparse-like entries; enforce member/count/size/decompression limits.
- Harden v2 `ui/app.py::download_workshop_tools`: validate API/download targets, bounded download, safe extraction, staged `rescomproot` replacement.
- Harden v2 `plugins/d2pfx/data.py`: public-HTTPS/SSRF checks, safe asset/category names, bounded metadata/image/payload downloads, bounded gzip JSON, atomic cache writes.
- Harden v2 `plugins/d2pfx/api.py`: confined install destinations, sanitized filenames, staged ZIP/VPK installs, safe archive members.
- Harden v2 `plugins/d2pfx/build_hook.py`: port regular-file/symlink-safe cursor collection/copy/restore.
- Harden v2 `patch/remap_processor.py`: confine target/build/output paths and validate remap rule shape before decompile/write.
- Gate: port hostile path/archive/download/cursor regressions before any v2 user build.

## Stage 2 — Mod model
- Replace top-level-only loop in v2 `core/mods_shared.py::scan_mods` with recursive logical discovery.
- Preserve nested mods, Collections/custom categories, custom VPK categories, stable logical IDs, profiles, favorites.
- Update v2 `ui/services/mod_service.py` to expose collection/category/profile/favorite metadata.
- Gate: nested discovery/category/profile regressions match current hardening semantics.

## Stage 3 — Patch transaction and collisions
- Port `core/backup_manager.py` restore-point lifecycle into the v2 PatchService boundary.
- Build file ownership/collision index before writes and expose preflight to Svelte.
- Preserve Dark Terrain resource-level yielding; do not substitute v2 blanket `terrains` category conflicts.
- Flow: preflight -> restore point -> staged build -> atomic deploy -> mark success; rollback on failure.
- Gate: collision/rollback tests plus forced mid-patch failure tests.

## Stage 4 — D2PFX plugin
- Keep v2 plugin/Svelte architecture.
- Replace network/install/archive/cursor internals with Stage 1 hardened implementations.
- Preserve per-component removal and installed-state tracking.
- Gate: current fork D2PFX security suites mapped to plugin APIs.

## Stage 5 — UI/UX
- Port Black-Plum tokens to CSS variables.
- Preserve the 960x680-equivalent fit invariant: responsive wrapping, scroll ownership, breakpoint collapse of optional telemetry only.
- Port Mod Library search/filter/category/profile/favorite/collision review plus terminal/activity/restore surfaces.
- Gate: browser-size regressions + Windows manual minimum-size smoke.

## Stage 6 — Fork behavior
- Preserve second Remove Main Menu Background `#FrontpageContents` collapse rule.
- Preserve manual `prelaunch`; disable v2 automatic `steam.add_prelaunch_to_launch_options` mutation.
- Preserve locale/English-fix semantics.
- Evaluate v2 Remove Foliage `remap.json` only against human `_09` findings; current `_05 -> _00` behavior is not accepted as fixed.

## Stage 7 — Migration/validation
- Add config/state migration for profiles, favorites, Collections, backup metadata, and fork settings.
- Port semantic regressions before deleting the DearPyGui implementation.
- Run full CI + Windows portable build, then full Windows/Dota smoke.
- Promote hardening -> beta only after explicit approval; beta -> main only after separate explicit approval.
