# Progress
- [x] Three-branch model retained; validated UI product tip `5d097d3f7246f47e4f89008781d0e45d6137c13f`.
- [x] Beta previously promoted; current beta `442d36dcc902f6436c6404f2947091663c254cc5`; main remains `a26bc88a0d412e357965f29488b83a7f9093e11f`.
- [x] Dark Terrain independent.
- [x] RERL hardening code `3dbf6cb6d9dbc691bc8bab00b3739c889dd2a326`; CI `34528212083`: **286/286 PASS**; Windows build PASS.
- [x] Simple upstream-style tree redirect smoke failed; some trees invisible.
- [x] ID-update semantics rejected; blank `_05.vmat_c` confirmed to remove target foliage.
- [x] Private `_09` smoke generator integrated into Developer Tools; derives current stock `_05` locally as ignored `_09` alias; human smoke pending.
- [x] CI #171 / `35394422779`: **294/294 PASS**, Windows portable PASS.
- [x] Startup modal race fixed with explicit queue active state; Tutorial and Language Setup no longer construct into the same popup frame.
- [x] User-facing version/title now shows `v21.4-hardening`; upstream compatibility remains `VERSION = "1.14rc7"`. CI #173 / `35403299757`: **295/295 PASS**, Windows portable PASS; portable SHA-256 `6b9788d3ac1e60dba636d5a5b0b17b5dea4d52285a1660e2111ebbc9fc1ff8b1`.
- [x] Upstream reviewed through `Minify-v2rc4` / `e444454684c2d7f809e7eef20a1b72d4422c50d7`.
- [x] v2 advantages identified: PyWebView/Svelte, CSS themes, services, plugin SDK, D2PFX plugin, migrations, remap processor.
- [x] v2 incompatibilities identified: no nested Collections/profiles/restore points/collision index; weaker network/archive/D2PFX/cursor hardening; auto-prelaunch option.
- [x] Upstream latest Remove Foliage uses blacklist + `remap.json`, not a full-map VPK layer.
- [x] 960x680 UI gate implemented and validated; CI #168 / `35392039137`: **289/289 PASS**, Windows portable PASS.
- [x] Responsive pass covers Home/activity/footer, Mod Library/Settings sizing, compact D2PFX, and shared modal clamping/scrolling.
- [x] Explicit v2 compatibility matrix and staged security/product caller map completed.
- [x] v2 Stage 1 security source port staged under `V2_STAGING/`: core security/fs, updater + Workshop Tools, D2PFX data/API/cursors, remap confinement, Svelte digest handoff.
- [x] CI #176 / `35405707258`: **309/309 PASS**, Ruff/compile PASS, Windows portable PASS; artifact digest `sha256:d8e5e9da96eacc949f46af14944246ce4b124c33b7918e40833852ec9f857771`.
- [x] Production rc7-derived app remains unchanged by `V2_STAGING`; validated product tip remains `8f29962bb056a9f95ab224f135bf795ecbda2b93`.
- [ ] Next: human foliage alias smoke remains an independent manual gate. For v2, integrate the staged Stage 1 substrate into the full v2rc4 tree, then begin Stage 2 recursive mod model/services; no raw merge/rebase.
- [ ] Human foliage alias smoke + general Windows/Dota smoke remain.

- [x] Full exact v2rc4 architecture tree materialized under `V2_STAGING/`; fork Stage 1 security and Stage 2 logical mod-library semantics integrated.
- [x] v2 Mod Library now exposes type/category filters, favorites, and profile save/apply/copy/delete controls; nested/D2PFX paths use logical IDs.
- [x] v2 identity/manual-prelaunch/Main Menu fork behaviors preserved.
- [x] CI #191 / `35438400128`: **327/327 PASS**; root + v2 Ruff/compile PASS; Svelte/plugin build PASS; rc7 + v2rc4 Windows portable builds PASS.
- [ ] Next v2 work: transactional restore/rollback + collision index/report + Dark Terrain resource-yield semantics, then Black-Plum CSS/min-fit polish and Dota smoke.

- [x] v2 runtime startup fix `0cf84afbcc67a2097753ef8648a84bc2f6533512`: real newlines restored in staged `core/base.py`; runtime import regression test added.
- [x] CI #192 / `35443577402`: **327/327 PASS**; both validation jobs and both Windows portable jobs PASS. Fixed v2 portable SHA-256 `77ac3af45ecd9e8eb1baff6bef4e1b6c8402b4374c1c766dda83c96af972ba00`.
- [x] v2 Windows PyInstaller stall isolated to the package-import DLL-path heuristic after `Looking for dynamic libraries`; real PE dependency analysis had not begun.
- [x] CI-only guard fix `472bfe794d4e0deecfc1e5deb352943737e181e6` preserves normal binary dependency scanning and leaves local/non-GitHub builds unchanged.
- [x] CI #214 / `35459474245`: **364/364 PASS**; both validation jobs, root Windows portable, and v2 Windows portable PASS.
- [x] Current parity-complete v2 portable SHA-256: `86018d93c44fc2a93e270dfdb91dd9e3d6790149e20f0081f86eb2b796405803`.
- [ ] Next: user Windows/Dota smoke; private foliage alias smoke remains a separate human gate.

- [x] Residual v2 hostile-input/path-race review closed: Windows path aliases/ADS/device names, bounded identity-checked profile/D2PFX/config/remap/mod-metadata reads, and cursor source identity.
- [x] Final security stack validated at `541d8b4f20e48a1f62dc4052f6347fd450a5ba55`; CI #218 / `35464400624`: **369/369 PASS**, both validation jobs and both Windows portable builds PASS.
- [x] Current parity-complete v2 portable SHA-256: `2acb39b7099b125a8583e727774cd112873c234ca9c22c36344671c3a25f5007`.
- [ ] Next: full Windows/Dota smoke; private foliage alias smoke remains a separate human gate.

- [x] D2PFX screenshot regression fixed at `fced5d8c412b493bd1a7ca2dd19f82e02d182f91`: preview URLs now use D2PFX data-branch JPG mirror/root fallback; fork Updated-date labels restored; desktop grid capped at 4 columns; visible action feedback + stale-search protection + post-success install state added.
- [x] Installed D2PFX preview extension/MIME parity fixed at `f6c7b63c0f42152f8ce20d891371434e0e5998ce`.
- [x] CI #220 / `35466711651`: **374/374 PASS**, Ruff clean, both validation jobs and both Windows portable builds PASS.
- [x] Current v2 portable SHA-256: `2f976b02ef49310f7f2c67a1f643e9bccbf47d98f1a6f3a6f184b563c7d3aee3`.
- [ ] Next: user re-smoke corrected D2PFX Browser, then continue full Windows/Dota smoke; private foliage alias remains separate.

- [x] Toggleable legacy-style v2 Mod Library list view added at `1354b8549f0e546faed062794ba7669d0f0a5ba0`: List is default, Cards retained, selection persists, grouped collapsible Standard/Collections/D2PFX/VPK sections, compact optional 64x36 thumbnails, row metadata/favorite/details/state controls.
- [x] CI #221 / `35467625867`: **375/375 PASS**, Ruff clean, v2 validation/Svelte/plugin builds PASS, root + v2 Windows portable PASS.
- [x] Current v2 portable SHA-256: `87a59e0959cd6f7a96971055b619c254aff1d1876ddbe68eae0dc27d811b261e`.
- [ ] Next: user smoke of Mod Library List/Cards + D2PFX, then continue full Windows/Dota smoke; foliage alias remains separate.

- [x] Legacy-list smoke follow-up fixed at `1c17df75253aa9b5c3924497e78587ad51ff9e81`: collection sections preserve actual parent labels (for example Hero Mods), current `browser: "d2pfx"` manifests classify as D2PFX, and Select all/Clear/Invert/Expand all/Collapse all are restored.
- [x] CI #222 / `35468658278`: **377/377 PASS**, Ruff clean, v2 validation/Svelte/plugin builds PASS, root + v2 Windows portable PASS.
- [x] Current v2 portable SHA-256: `3312efd9cbdfc84ffb87805504205fafc1af376d7e5b2b72007fdf835a7a90de`.
- [ ] Next: user smoke of section placement/bulk controls + D2PFX, then continue full Windows/Dota smoke; private foliage alias remains separate.

- [x] Windows smoke exposed patch preflight aborting on `PermissionError: [WinError 5]` while replacing derived `config/mod-content-index.json`.
- [x] Fixed at `c8dd5d6167279ea98bfcddadbeea7e4910084831`: absolute cache path, bounded retry for Windows permission/sharing failures, writable-bit repair, process-local in-memory fallback, and non-fatal disk-cache disable after persistent failure.
- [x] CI #223 / `35469297934`: **379/379 PASS**, Ruff clean, v2 validation/Svelte/plugin builds PASS, root + v2 Windows portable PASS.
- [x] Current v2 portable SHA-256: `4413087967b6170c70a9fa9c568002b0d8806b73498d20973c916337b5845516`.
- [ ] Next: user PATCH/preflight retry on Windows; then continue UI/D2PFX/full Dota smoke. Foliage alias remains separate.

- [x] rc7 conflict-semantics parity: category/plugin overlaps no longer synthesize hard conflicts; explicit manifest conflicts still block.
- [x] CI #224 / `35470208025`: **380/380 PASS**, Ruff clean, both validation jobs and both Windows portable builds PASS.
- [x] Current v2 portable SHA-256: `f6ee41ed9f11c11ea24b3fdbf01a2b33c88118a6fa270b235ba6105a8af60190`.

- [x] Patch activity visibility: global live PATCH/PREFLIGHT status + immediate PatchService start log + Home recent-terminal panel; `c7b319e46d06991d2d2bb69a3e31631caa869509`.
- [x] CI #225 / `35470787033`: **381/381 PASS**, Ruff clean, both validation jobs and both Windows portable builds PASS.
- [x] Current v2 portable SHA-256: `d6b45e3f7e77c68ff8919fae6d51761524c3d8d2f16c26f1467d342c038066af`.

- [x] Per-section Mod Library All/None parity restored at `ca24d6a7a16add68333dced211fc6a1248fe3d7c`.
- [x] Full-section selection semantics verified by regression test; always/untickable states preserved.
- [x] CI #226 / `35471631659`: **382/382 PASS**, Ruff clean, v2 validation/Svelte/plugin PASS, root + v2 Windows portable PASS.
- [x] Current v2 portable SHA-256: `a6e3ba78514c992c32ae0b8b223aafc75c749c77054a6db75851af685b87cceb`.

- [x] D2PFX-aware Hero defaults added at `811e971b7a3c2a12e0c396843adc19d26b5f6c1f`; validated/formatted head `3d4c355aed635661cf3a0fd3b89b7e9f48360de5`.
- [x] Hero Mods `Defaults except D2PFX` uses actual virtual-resource overlap against enabled D2PFX mods; no filename/hero-name guesswork.
- [x] CI #229 / `35473330452`: **384/384 PASS**, Ruff clean, v2 validation/Svelte/plugin PASS, root + v2 Windows portable PASS.
- [x] Current v2 portable SHA-256: `8bec9db28cc641cfbc7a64aab32c3b37bf7835185e2983d32ad5ab87a70b6550`.

- [x] D2PFX list organization: `257010615572a61e54ef4473f853d9636da2789b` creates one list section per stored D2PFX category with humanized labels and existing section controls.
- [x] CI #230 / `35474054089`: **385/385 PASS**, Ruff clean, v2 validation/Svelte/plugin PASS, root + v2 Windows portable PASS.
- [x] Current v2 portable SHA-256: `aa7fd595767ff61af453f75ad6212c5c354617425ecc55850cdadd59c91fda53`.

- [x] `0db87a1bbe4b8e79bd3f49f4afa924fa6aea3e86`: D2PFX Mod Library now uses one collapsible `D2PFX Mods` parent and category-organized internal sections with counts/All/None.
- [x] CI #231 / `35474663691`: **385/385 PASS**, Ruff clean, both validation jobs and both Windows portable builds PASS.
- [x] Current v2 portable SHA-256: `95653076e5874def8cc2e4507e5917cf1e51f3e52d54c47f5da0bb233b3a2108`.


- [x] Custom Transparent HUD v1.4 compatibility: rc7 DearPyGui/`ui.details` initial UI hook is bypassed on v2 when manifest settings exist; other lifecycle scripts remain active.
- [x] Legacy DearPyGui runtime is packaged for dynamic scripts; startup initial-script failure cannot crash Minify.
- [x] CI #234 / `35480754644`: **388/388 PASS**, Ruff clean, both validation jobs and both Windows portable builds PASS.
- [x] Current v2 portable SHA-256: `3ba0ba120550c343660051427fbc916e0658d27496ef1a0f3e6fa69ada8760fe`.

- [x] Simple Dark Terrain river compatibility added at `7d165b52bbfbf5cedaaf51475f1ffcad022559e5`: indexed overlap identifies shared river/water resources and excludes only those paths from Simple Dark Terrain.
- [x] CI #237 / `35485223052`: **392/392 PASS**, Ruff clean, both validation jobs and both Windows portable builds PASS.
- [x] Current v2 portable SHA-256: `6add0bfc7ac16309bee064ecb6831c891da6fe091e96f0aa0896a3d0a752fdbc`.

- Showcase View river follow-up: `7c25fe7dccc71247ea746e14476718d7e24df752`.
  - First river compatibility pass could hand a river competitor the main deferred material while companion deferred resources stayed with Simple Dark Terrain.
  - Revised rule: Simple Dark Terrain yields only overlapping river/water resources; any overlapping `materials/dev/deferred_post_process*` resources are excluded from the river competitor so the deferred chain remains coherent.
  - Added copy/exclusion + Showcase regression coverage.
- CI #238 / `35608475147`: **SUCCESS**, **394/394 tests passed**, Ruff clean, v2 validation/Svelte/plugin PASS, both Windows portable builds PASS.
- v2 inner ZIP SHA-256: `d1b9bab0b8c37e02538ae0fec745c5fc6fbb0c59e256ccdce2216e368b6052ec`.

- Remove Weather Effects black-panel fix validated at `3a8823b1de0294715609c015ba1a95b00c46fbbb`.
  - Root cause: blacklist VMAT entries copied generic `blank.vmat_c` over Dota skybox render materials.
  - Fix removes `materials/skybox/sky_dota_*` from both rc7-derived and v2 staged Remove Weather blacklists; rain particles + thunder sounds remain suppressed.
  - CI #241 / `35735125205`: **396/396 PASS**, Ruff clean, v2 Svelte/plugin PASS, root + v2 Windows portable PASS.
  - v2 portable SHA-256: `d8567683f9bc401e229a180d64e68cb0db55631a4c61b78434e2e5e51ef548cc`.
- Next gate: human Dota smoke of Remove Weather Effects, especially Showcase View / `I`; confirm no black panel and acceptable weather removal.

- README fork comparison milestone:
  - Added top-of-README current-upstream comparison against Egezenn `main` `bd86c7cb619896e7200b7269c1b23245d3037120`; upstream code remains v2rc4 baseline plus docs-only symbol update.
  - Added `docs/assets/fork-vs-upstream.svg` visual summary.
  - Difference table covers intentional product/behavior deltas and marks automated, human-smoke-pending, and experimental items separately.
  - Added explicit permission for Egezenn to reuse/port fork ideas, fixes, UI concepts, tests, compatibility rules, and code subject to GPL-3.0.

- D2PFX freshness fix validated at `715cad3a3c7c01230d1bab08d36904d198c2bff1`.
  - Live source was current; browser freshness was the problem.
  - Added publisher `recentlyAddedMods` as first **Recently Added** view; entries retain real source category for install/uninstall/state/preview routing.
  - Normal categories default newest-first; automatic catalogue refresh reduced from 24h to 5m.
  - Manual Refresh Data no longer deletes the last-good cache before network success and now reports refresh failure.
  - CI #253 / `35766619028`: **399/399 PASS**, Ruff clean, v2 Svelte/D2PFX build PASS, root + v2 Windows portable PASS.
  - v2 test ZIP SHA-256: `bc626ab6994e9a7cb8ec79badc5086704e5ca597f71a3bd568f76b8e2a92c3db`; artifact digest `sha256:b2a8f35181052a549b6c1cd0f64a49a4fee80b660d43b86a181173e8f05adae9`.
- Next gate: user D2PFX Browser smoke of Recently Added / Refresh Data / install-from-recent category routing.
