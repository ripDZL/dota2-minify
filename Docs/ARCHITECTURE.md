# Architecture
- Current product lineage: rc7-derived hardening; exact upstream baseline `d4b4520c945a9e1f8f5facc52a76ac5903babe90`.
- Branch flow exactly hardening -> beta -> main; no persistent integration/reference branches.
- Current committed foliage engine uses hardened same-length RERL rewriting; private `_09` alias remains smoke-only. `core/foliage_smoke.py` generates the ignored local smoke mod from the installed Dota VPK; no Valve stock binary is committed.
- Never freeze/version-pin Dota stock binary bytes in repo; any successful alias implementation must derive from current stock Dota with strict bounds.
- Security boundary: local bundled/mod Python trusted; archive/VPK/profile/backup/download/D2PFX data untrusted; destinations confined.
- Current fork hardening primitives: `core/security.py`, `core/backup_manager.py`, `core/mod_compat.py`, `core/mod_library.py`.
- Current DearPyGui minimum viewport is 960x680. At that size every visible label/control must remain legible and inside its container.
- UI identity is split intentionally: `base.VERSION = "1.14rc7"` is upstream/manifest compatibility; `base.DISPLAY_VERSION = base.FORK_BUILD = "v21.4-hardening"` is user-facing. Keep viewport/title text ASCII-safe on Windows.
- Unified startup modals use explicit `modal_active` queue state rather than rendered-visibility probes; multiple same-frame startup notices must serialize, never share one popup tree.
- Minimum-size strategy: use measured responsive widths/heights, text wrap, flexible tables/groups, and breakpoint-driven collapse of **optional** telemetry. Essential navigation/actions must not disappear or clip. Do not treat a larger minimum as the primary fix.
- The fit invariant applies to dashboard/header/activity/footer plus Mod Library, Settings, D2PFX browser, dialogs, and plugin/browser surfaces.
- Implemented compact behavior: Home final compact pass runs after generic resize geometry; optional activity/social telemetry collapses; D2PFX switches to a 148px sidebar + one-column cards and hides optional catalogue telemetry; shared modals clamp to client bounds with scrollable copy.
- Upstream v2rc4 target architecture: PyWebView host + Svelte frontend + Python services + plugin SDK + CSS themes.
- v2rc4 tag `e444454684c2d7f809e7eef20a1b72d4422c50d7`; histories diverged, so migrate semantically rather than merge.
- Preferred mapping: Black-Plum -> CSS theme; nested Collections/profiles/favorites -> ModService + Svelte; backup/collision -> PatchService + backend modules; D2PFX hardening -> plugin data/API/build hook.
- Port fork security into v2 before accepting any v2 test build: bounded/atomic downloads, safe archives, URL/redirect/SSRF validation, bounded decompression, staged installs, symlink-safe cursor operations. Exact caller map and acceptance gates live in `Docs/V2_PORT_PLAN.md`.
- Stage 1 implementation is isolated under `V2_STAGING/` until the complete v2rc4 architecture surrounds it. This prevents an incomplete PyWebView/Svelte tree from replacing the validated rc7-derived product.
- Staged app updates require GitHub asset SHA-256 propagation from Svelte to Python; Workshop Tools require a GitHub asset digest and use staged directory publication with rollback. D2PFX installs use confined staging + atomic publication; cursor copies accept only bounded regular files; remap output/build paths are confined.
- Preserve collision-aware resource ownership. Upstream blanket category conflicts are not equivalent to fork Dark Terrain behavior.
- Preserve no-auto-prelaunch policy even though upstream v2 exposes `patch_on_launch`.
- Upstream v2 Remove Foliage remap is eligible for isolated validation; never reintroduce a full-map Remove Foliage layer.
- Main Menu Background must retain both collapse rules.
- Rebuild the minimum-fit invariant in responsive Svelte/CSS/container rules during v2 migration.

- `V2_STAGING/` now contains the full exact v2rc4 architecture, not a partial source slice. Fork security and logical mod-library semantics override selected upstream files.
- v2 display identity mirrors the fork split: internal `VERSION = "2rc4"`; user-facing `DISPLAY_VERSION = FORK_BUILD = "v21.4-hardening"`.
- v2 automatic Steam prelaunch injection is disabled by compatibility shim and removed from settings/pipeline; explicit CLI `prelaunch` remains.
- v2 Mod Library services use stable logical IDs for nested/Collection/D2PFX mods; profiles are complete snapshots and favorites use stable keys.
- Windows CI packaging uses `V2_STAGING/scripts/pyinstaller_guard.py`: on GitHub Windows runners only, skip PyInstaller's package-import DLL-path heuristic that can hang unattended; retain normal PE/DLL dependency analysis. Local/non-GitHub packaging keeps default PyInstaller behavior.

- v2 untrusted local-file reads use bounded regular-file opens with pre-open `stat`, no-follow where available, post-open `fstat`, and device/inode identity comparison; applied to profiles, D2PFX cache, JSON/JSONC mod config, remap rules, and mod metadata.
- v2 portable path validation rejects traversal plus Windows ADS/device-name/control/trailing-dot-space aliases before normalization; remap glob characters remain supported.
- D2PFX cursor publication revalidates source identity after open; recursive nested-mod discovery does not follow symlink directories.

- v2 D2PFX preview contract: catalogue `.webp` names are served from the D2PFX data-branch JPG mirror after `.webp -> .jpg` normalization; do not point normalized JPG names at main-branch `assets/previews` WebP files. Keep category URL first plus data-root fallback.
- v2 D2PFX UI parity: desktop catalogue is capped at 4 columns with 3/2/1 responsive breakpoints; 960px stays one-column compact. Cards surface fork Updated-date metadata and visible preview-failure state. Async search is request-ordered, and install state is not persisted before publication succeeds.

- v2 Mod Library has two presentation modes over the same filtered/sorted model: default compact `list` and existing `cards`. The selection is UI-only state persisted as `minify.mod-library.view-mode` in local storage; it does not alter mod configuration/state semantics.
- List mode mirrors legacy ergonomics: collapsible source-type groups (Standard, Collections, D2PFX, VPK), compact rows, selected counts, optional 64x36 previews only when available, and the same favorite/details/toggle actions as Cards mode.
