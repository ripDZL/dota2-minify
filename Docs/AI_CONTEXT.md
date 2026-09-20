# AI Context
- Current upstream-integrated baseline: `Egezenn/dota2-minify` `Minify-v1.14rc7` / `d4b4520c945a9e1f8f5facc52a76ac5903babe90`.
- Repo `ripDZL/dota2-minify`; branches exactly `v21.4-hardening` -> `beta` -> `main`.
- Validated product tip: `8f29962bb056a9f95ab224f135bf795ecbda2b93`; beta `442d36dcc902f6436c6404f2947091663c254cc5`; main `a26bc88a0d412e357965f29488b83a7f9093e11f`.
- UI CI #168 / `35392039137`: **289/289 PASS**, Ruff/compile PASS, Windows portable PASS.
- Current committed foliage/RERL production behavior remains `3dbf6cb6d9dbc691bc8bab00b3739c889dd2a326`; no `_09` alias is enabled in production.
- Local `_09` human-smoke tooling is integrated at `f885e761faab103c1727f738335c3d28bb0045e6`; CI #171 / `35394422779`: **294/294 PASS**, Ruff/compile PASS, Windows portable PASS.
- UI/modal identity fix validated at `8f29962bb056a9f95ab224f135bf795ecbda2b93`; CI #173 / `35403299757`: **295/295 PASS**, Ruff/compile PASS, Windows portable PASS.
- Startup modals now use explicit active-state queueing, preventing Tutorial/Language Setup same-frame overlap. User-facing release/title is `v21.4-hardening`; internal `VERSION = "1.14rc7"` remains for manifest compatibility; ASCII title removes Windows mojibake.
- Current portable SHA-256: `6b9788d3ac1e60dba636d5a5b0b17b5dea4d52285a1660e2111ebbc9fc1ff8b1`.
- Smoke-enabled portable SHA-256: `c1291295d849f14a403bb045e75e8095ec8228b2a39b6176b9a792106a55cae0`.
- Dark Terrain remains independent.
- Human smoke of simple upstream-style `_05 -> _00` RERL redirect still loses some tree visibility; do not use target-name RERL ID updates.
- Confirmed: blanking stock `tree_oak_leaves_05.vmat_c` removes target foliage.
- Current smoke-only candidate: preserve stock tree material through unused private `_09` alias; production behavior not committed until human smoke passes.
- Private-alias portable SHA-256 `7e8feede3c2f648155a03a619760a996ea99c17a445f31335e4182191f8b5457`; mod-only SHA-256 `3d7d9b169e0fbbd808236e65e8d57affc85055d187301327ecd89cd2eb68e86b`.
- Upstream audit 2026-09-18: latest release `Minify-v2rc4` / `e444454684c2d7f809e7eef20a1b72d4422c50d7`; upstream main `bd86c7cb619896e7200b7269c1b23245d3037120` is a docs-index commit after the release.
- rc7 and v2rc4 diverged from merge base `c25db2cc0310e443eadacde9d9c3f6c84334ccd9`; v2rc4 is 50 commits ahead and rc7 3 commits ahead. Never raw-merge/rebase.
- v2 architecture: PyWebView + Svelte frontend, CSS themes, Python service layer, plugin SDK, D2PFX plugin, migrations, remap processor.
- Fork-only behavior to preserve: recursive/nested mods + Collections/custom categories, profiles/favorites, collision index/report, transactional restore points/rollback, Dark Terrain collision-aware yielding, Main Menu two-rule fix, hardened network/archive/D2PFX/cursor/backup handling, manual prelaunch/no-auto-injection.
- Upstream v2 gaps found: top-level-only mod scan; no profiles/favorites/restore points/collision report; weaker download/archive/D2PFX/cursor confinement/limits; optional automatic Steam prelaunch injection remains.
- Upstream Main Menu Background currently has only the dashboard-background collapse rule; retain fork `#FrontpageContents` rule.
- 960x680 DearPyGui fit pass complete: final resize owns compact Home geometry; activity/footer optional telemetry collapses at the breakpoint; D2PFX uses compact sidebar + one-column grid; shared modals clamp/scroll; Mod Library/Settings remain scroll-safe.
- Explicit v2 compatibility matrix: `Docs/V2_COMPATIBILITY_MATRIX.md`; exact staged security/product caller map: `Docs/V2_PORT_PLAN.md`.
- Preferred integration: treat v2rc4 as a new architecture target and port fork behavior explicitly; keep current hardening history as rollback provenance.
- v2 Stage 1 source staging tip: `5589355f7b2b4af00a7facb4b1de5458f1b93749` under `V2_STAGING/`; production product tip remains `8f29962bb056a9f95ab224f135bf795ecbda2b93`.
- Staged Stage 1: shared path/archive/decompression/hash/public-HTTPS primitives; bounded atomic v2 downloads/extraction; digest-verified app updates; digest-verified transactional Workshop Tools install/rollback; hardened D2PFX catalogue/install/cursor flows; confined remap processing; updater digest propagation.
- CI #176 / `35405707258`: **309/309 PASS**, Ruff/compile PASS, Windows portable PASS. Artifact digest `sha256:d8e5e9da96eacc949f46af14944246ce4b124c33b7918e40833852ec9f857771`.
- `V2_STAGING` is intentionally non-production and is not packaged as the v2 app yet; next migration stage is the v2 mod model/services around the security substrate.

- Validated v2 architecture tip: `59746db919e567245371609257cb7ab13a7e518b`; exact v2rc4 tree now materialized under `V2_STAGING/` with fork security/mod-library semantics layered on top.
- v2 Stage 2 ports: recursive/nested mods, Collections/custom VPK metadata, logical mod IDs, favorites, profiles, D2PFX logical-ID handling, Svelte Mod Library filters/profile controls.
- v2 fork behaviors preserved in staging: user-facing `v21.4-hardening` identity with internal `VERSION = "2rc4"`, manual prelaunch/no Steam auto-injection, Main Menu second `#FrontpageContents` rule.
- CI #191 / `35438400128`: **327/327 PASS**, root Ruff/compile PASS, v2 Ruff/compile PASS, Svelte + D2PFX plugin builds PASS, rc7 Windows portable PASS, v2rc4 Windows portable PASS.
- v2 artifact digest: `sha256:41e328b86a6f7448508c0dc040a94e562dfe97776f819d1ac7683b9a126da884`; rc7 artifact digest: `sha256:7f6b73eb1b4413916a30a7f99a3af302f0442c5ae8fd446cddea24b452270a5c`.

- v2 launch regression fixed at `0cf84afbcc67a2097753ef8648a84bc2f6533512`: staged `core/base.py` had literal `\\n` escapes after a comment, so `VERSION/FORK_BUILD/DISPLAY_VERSION/TITLE` were commented out at runtime despite source/compile checks. Identity test now imports the staged module and asserts runtime attributes.
- CI #192 / `35443577402`: **327/327 PASS**, root + v2 Ruff/compile PASS, Svelte/plugin builds PASS, rc7 + v2 Windows portable PASS.
- Fixed v2 portable SHA-256: `77ac3af45ecd9e8eb1baff6bef4e1b6c8402b4374c1c766dda83c96af972ba00`.
- v2 Windows PyInstaller stall diagnosed: the hosted-Windows package-import DLL-path heuristic blocked after `Looking for dynamic libraries`, before PE dependency scanning.
- Fix `472bfe794d4e0deecfc1e5deb352943737e181e6`: GitHub-Windows-only PyInstaller guard skips that heuristic while preserving binary dependency analysis; local/non-GitHub builds are unchanged.
- CI #214 / `35459474245`: **364/364 PASS**, v2 compile/Ruff/Svelte/plugin PASS, root Windows portable PASS, v2 Windows portable PASS.
- Current parity-complete v2 portable SHA-256: `86018d93c44fc2a93e270dfdb91dd9e3d6790149e20f0081f86eb2b796405803`.

- Residual v2 hostile-input/path-race review completed through `541d8b4f20e48a1f62dc4052f6347fd450a5ba55`: Windows alias/ADS/device/trailing-dot-space path rejection; bounded identity-checked local reads; profile import/load; D2PFX catalogue; cursor sources; generic JSON/JSONC; remap.json; Mods.txt/d2pfx manifest/VPK sidecar metadata.
- Recursive nested-mod discovery already skips symlink directories; no scanner traversal change was needed.
- CI #218 / `35464400624`: **369/369 PASS**, Ruff clean, v2 validation PASS, root Windows portable PASS, v2 Windows portable PASS.
- Current parity-complete v2 portable SHA-256: `2acb39b7099b125a8583e727774cd112873c234ca9c22c36344671c3a25f5007`.

- User D2PFX screenshot smoke found blank previews, over-dense desktop cards, and missing fork Updated-date labels in the v2 plugin.
- Root cause: v2 changed catalogue `.webp` names to `.jpg` but used the main-branch `assets/previews` WebP tree. Fix `fced5d8c412b493bd1a7ca2dd19f82e02d182f91` restores the data-branch JPG preview tree + root fallback, Updated-date formatting, max-4 desktop layout, visible status, stale-search protection, and post-success install state.
- Follow-up `f6c7b63c0f42152f8ce20d891371434e0e5998ce` keeps installed D2PFX preview filenames/MIME aligned with downloaded image type.
- CI #220 / `35466711651`: **374/374 PASS**, Ruff clean, v2 validation/Svelte/plugin builds PASS, root + v2 Windows portable PASS.
- Current D2PFX-corrected v2 portable SHA-256: `2f976b02ef49310f7f2c67a1f643e9bccbf47d98f1a6f3a6f184b563c7d3aee3`.

- User requested the old Mod Library list presentation back while keeping the v2 cards. Implemented at `1354b8549f0e546faed062794ba7669d0f0a5ba0`.
- Mod Library now defaults to a compact legacy-style grouped List view with collapsible Standard/Collections/D2PFX/VPK sections, selected/total counts, checkbox/favorite/details controls, source/category metadata, and a 64x36 thumbnail only when a preview exists. Cards remains toggleable; choice persists in local storage.
- CI #221 / `35467625867`: **375/375 PASS**, Ruff clean, v2 Svelte/plugin validation PASS, root + v2 Windows portable PASS.
- Current list-view test ZIP SHA-256: `87a59e0959cd6f7a96971055b619c254aff1d1876ddbe68eae0dc27d811b261e`; GitHub v2 artifact digest `sha256:54acf4d448a0db4744fc10c3bde20f83c419bca538085c30f8c101bd0dbadb4e`.

- User smoke of the first legacy-list build found two classification regressions: D2PFX installs appeared in Standard because v2 writes `"browser": "d2pfx"` while ModService only recognized dictionary browser metadata; nested Single Hero mods were collapsed into a generic Collections section instead of their legacy `Hero Mods` section.
- Fix `1c17df75253aa9b5c3924497e78587ad51ff9e81`: public v2 `mod_library.is_d2pfx` recognizes both manifest schemas; ModService uses it; list collection keys preserve the real parent group name; Select all/Clear/Invert/Expand all/Collapse all restored. Bulk selection leaves always/untickable states unchanged.
- CI #222 / `35468658278`: **377/377 PASS**, Ruff clean, v2 validation/Svelte/plugin builds PASS, root + v2 Windows portable PASS.
- Current legacy-section-corrected v2 portable SHA-256: `3312efd9cbdfc84ffb87805504205fafc1af376d7e5b2b72007fdf835a7a90de`.

- Windows runtime smoke found PATCH/preflight blocked by `PermissionError [WinError 5]` when `mod_library._save_content_index` replaced `config/mod-content-index.json`.
- Fix `c8dd5d6167279ea98bfcddadbeea7e4910084831`: content-index persistence is explicitly best-effort because it is derived; absolute destination, four Windows permission/sharing retries, writable-bit repair, in-memory cache retention, and process-level disk-write disable after persistent failure. Patch preflight no longer propagates cache publication failure.
- CI #223 / `35469297934`: **379/379 PASS**, Ruff clean, both validation jobs and both Windows portable builds PASS. Current v2 ZIP SHA-256 `4413087967b6170c70a9fa9c568002b0d8806b73498d20973c916337b5845516`.

- PATCH smoke after the cache fix exposed a parity regression: upstream-v2 plugin/category `category_conflicts` were being expanded into synthetic hard conflicts, blocking D2PFX combinations rc7 permits.
- Fix `99bf24ea8702a50b456d472189db5d7eb49fc967`: category/plugin overlaps remain visible in collision preflight/reporting but no longer populate hard `mod_conflicts_list`; explicit per-mod manifest `conflicts` still hard-stop like rc7. Dark Terrain resource yielding remains separate.
- CI #224 / `35470208025`: **380/380 PASS**, Ruff clean, v2 Svelte/plugin validation PASS, root + v2 Windows portable PASS.
- Current v2 ZIP SHA-256: `f6ee41ed9f11c11ea24b3fdbf01a2b33c88118a6fa270b235ba6105a8af60190`.

- User requested visible patch progress and a terminal on Home. Implemented at `c7b319e46d06991d2d2bb69a3e31631caa869509`: global PATCH/PREFLIGHT live status, immediate patch-start log, Home recent-terminal panel (120 lines), full-terminal shortcut, and patch no longer auto-switches to Terminal.
- CI #225 / `35470787033`: **381/381 PASS**, Ruff clean, v2 validation/Svelte/plugin builds PASS, root + v2 Windows portable PASS.
- Current status/Home-terminal v2 ZIP SHA-256: `d6b45e3f7e77c68ff8919fae6d51761524c3d8d2f16c26f1467d342c038066af`.

- Legacy Mod Library per-section bulk controls restored at `ca24d6a7a16add68333dced211fc6a1248fe3d7c`: every expanded section has All/None, operating on the complete section regardless of active filters; always/untickable mods are preserved.
- CI #226 / `35471631659`: **382/382 PASS**, Ruff clean, v2 validation/Svelte/plugin PASS, both Windows portable builds PASS.
- Current v2 portable SHA-256: `a6e3ba78514c992c32ae0b8b223aafc75c749c77054a6db75851af685b87cceb`.

- Hero Mods now has a D2PFX-aware bulk selector: `Defaults except D2PFX`.
- Implementation `811e971b7a3c2a12e0c396843adc19d26b5f6c1f` / formatted head `3d4c355aed635661cf3a0fd3b89b7e9f48360de5`: enable all Hero defaults except those sharing actual indexed virtual resources with currently enabled D2PFX mods. Disabled D2PFX installs do not suppress defaults.
- CI #229 / `35473330452`: **384/384 PASS**, Ruff clean, v2 validation/Svelte/plugin PASS, both Windows portable builds PASS.
- Current v2 portable SHA-256: `8bec9db28cc641cfbc7a64aab32c3b37bf7835185e2983d32ad5ab87a70b6550`.

- D2PFX Mod Library category organization fixed at `257010615572a61e54ef4473f853d9636da2789b`: list mode now groups installed D2PFX mods by their stored category ID, with humanized per-category section labels and inherited All/None + selected/total controls.
- CI #230 / `35474054089`: **385/385 PASS**, Ruff clean, v2 validation/Svelte/plugin PASS, both Windows portable builds PASS.
- Current v2 portable SHA-256: `aa7fd595767ff61af453f75ad6212c5c354617425ecc55850cdadd59c91fda53`.

- D2PFX Mod Library grouping corrected at `0db87a1bbe4b8e79bd3f49f4afa924fa6aea3e86`: one top-level collapsible `D2PFX Mods` section with non-collapsible category subheaders inside; per-category counts and All/None retained.
- CI #231 / `35474663691`: **385/385 PASS**, Ruff clean, v2 validation/Svelte/plugin PASS, root + v2 Windows portable PASS.
- Current v2 portable SHA-256: `95653076e5874def8cc2e4507e5917cf1e51f3e52d54c47f5da0bb233b3a2108`.


- Custom Transparent HUD v1.4 smoke exposed an rc7-only startup hook: `script_initial.py` imports DearPyGui and `ui.details`, which the v2 PyWebView/Svelte shell does not provide.
- Compatibility fix stack: `eef4124a9ea01c736d4462a7a5742092ee02b55c` bundles DearPyGui for legacy dynamic scripts and makes initial-script crashes non-fatal; `c4c3e44c5adb59ca9819d5f36dcec4f1a5cf68cc` detects manifest-backed rc7 DearPyGui Details hooks and skips that obsolete UI hook while preserving all other lifecycle scripts.
- The uploaded mod already declares 17 manifest controls; v2 Settings uses those values, so no archive rewrite is required.
- CI #234 / `35480754644`: **388/388 PASS**, Ruff clean, v2 Svelte/plugin validation PASS, both Windows portable builds PASS.
- Current v2 portable SHA-256: `3ba0ba120550c343660051427fbc916e0658d27496ef1a0f3e6fa69ada8760fe`; artifact digest `sha256:1f28594f6bc2a87a477c48fed3ddfed74238078b7848f62a960658a5a3d2549c`.


- Simple Dark Terrain/river compatibility contract: detect real indexed virtual-resource overlap, not mod names. Simple Dark Terrain yields only overlapping river/water paths to selected competitors; unrelated terrain stays intact. If the same proven river competitor also owns the shared deferred post-process material, it may own that overlap too.
- Validated at `7d165b52bbfbf5cedaaf51475f1ffcad022559e5`; CI #237 / `35485223052`: **392/392 PASS**, both Windows portable builds PASS. v2 ZIP SHA-256 `6add0bfc7ac16309bee064ecb6831c891da6fe091e96f0aa0896a3d0a752fdbc`.
