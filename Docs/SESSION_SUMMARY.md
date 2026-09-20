# Session Summary
- Repo `ripDZL/dota2-minify`; current branch model exactly `v21.4-hardening` -> `beta` -> `main`.
- Validated product tip `8f29962bb056a9f95ab224f135bf795ecbda2b93`; beta `442d36dcc902f6436c6404f2947091663c254cc5`; main `a26bc88a0d412e357965f29488b83a7f9093e11f`.
- Current committed RERL product code `3dbf6cb6d9dbc691bc8bab00b3739c889dd2a326`; CI #166 / `34528212083`: **286/286 PASS**, Windows portable PASS.
- Foliage: simple `_05 -> _00` RERL smoke breaks some tree visibility; target-name RERL ID update also failed.
- Blanking original `_05.vmat_c` removes target foliage. Local `_09` smoke generation is integrated in Developer Tools; it derives stock `_05` from the installed Dota VPK and writes it as ignored `_09`. Human smoke pending.
- CI #171 / `35394422779`: **294/294 PASS**, Windows portable PASS; portable SHA-256 `c1291295d849f14a403bb045e75e8095ec8228b2a39b6176b9a792106a55cae0`.
- Screenshot regression fixed: startup Tutorial and Language Setup modals now serialize through explicit active-state queueing; user-facing title/release shows `v21.4-hardening` while internal rc7 compatibility version remains unchanged.
- CI #173 / `35403299757`: **295/295 PASS**, Ruff/compile PASS, Windows portable PASS; portable SHA-256 `6b9788d3ac1e60dba636d5a5b0b17b5dea4d52285a1660e2111ebbc9fc1ff8b1`.
- Latest upstream release audited: `Minify-v2rc4`, commit `e444454684c2d7f809e7eef20a1b72d4422c50d7`; raw merge/rebase rejected because histories/architecture diverged.
- v2 replaces DearPyGui with PyWebView/Svelte and adds CSS themes, services, plugin SDK, D2PFX plugin, migrations, remap processor.
- Fork-only behavior/security to preserve: nested mods/Collections/custom categories, profiles/favorites, restore points/rollback, collision report, Dark Terrain collision-aware handling, hardened downloads/archives/D2PFX/cursors, Main Menu second rule, manual prelaunch/no-auto-injection.
- 960x680 UI fit pass complete: responsive Home/activity/footer, scroll-safe Mod Library/Settings, compact one-column D2PFX, client-clamped shared modals.
- CI #168 / `35392039137`: **289/289 PASS**, compile/Ruff PASS, Windows portable PASS; artifact digest `43c0fcbea15a42afe6ae0100ed83d1ff01be070bfb14c27c855b4da60b6780a7`.
- v2 compatibility matrix and exact staged port map are complete (`Docs/V2_COMPATIBILITY_MATRIX.md`, `Docs/V2_PORT_PLAN.md`).
- v2 Stage 1 security source port is staged under `V2_STAGING/` at `5589355f7b2b4af00a7facb4b1de5458f1b93749`; it does not replace/package the current product.
- Staged coverage: core security/fs, updater digest verification, transactional Workshop Tools, D2PFX network/install/cursor hardening, remap confinement, updater digest propagation.
- CI #176 / `35405707258`: **309/309 PASS**, Ruff/compile PASS, Windows portable PASS; artifact digest `sha256:d8e5e9da96eacc949f46af14944246ce4b124c33b7918e40833852ec9f857771`.
- Pending: private foliage alias human smoke; integrate Stage 1 into the complete v2rc4 tree; then Stage 2 mod model/services and residual security/Dota smoke.
- Do not promote beta -> main without validation and explicit approval.

- Current hardening head validated: `59746db919e567245371609257cb7ab13a7e518b`.
- Exact v2rc4 tree is now fully present under `V2_STAGING/`; Stage 1 security + Stage 2 recursive mod model, favorites/profiles, D2PFX logical IDs, and Mod Library UI are integrated.
- CI #191 / `35438400128`: **327/327 PASS**, both validation jobs PASS, Svelte + plugin builds PASS, both Windows portable jobs PASS.
- v2 portable artifact digest: `sha256:41e328b86a6f7448508c0dc040a94e562dfe97776f819d1ac7683b9a126da884`.
- Branches remain exactly three; beta/main unchanged.

- User runtime smoke found `AttributeError: module 'core.base' has no attribute 'TITLE'` in the first v2 test ZIP. Root cause: escaped `\\n` text was embedded on the identity comment line, commenting out the constants at runtime.
- Fixed at `0cf84afbcc67a2097753ef8648a84bc2f6533512`; identity test now imports staged `core/base.py` and checks real runtime values.
- CI #192 / `35443577402`: **327/327 PASS**, v2 frontend/plugin and both Windows portable builds PASS. Replacement v2 portable SHA-256 `77ac3af45ecd9e8eb1baff6bef4e1b6c8402b4374c1c766dda83c96af972ba00`.
- v2 Windows build stall diagnosed from CI #213: PyInstaller blocked in its Windows package-import DLL-path heuristic immediately after `Looking for dynamic libraries`.
- Fixed at `472bfe794d4e0deecfc1e5deb352943737e181e6` with a GitHub-Windows-only guard; actual binary dependency analysis remains enabled and local/non-GitHub builds are unchanged.
- CI #214 / `35459474245`: **364/364 PASS**; both validation jobs and both Windows portable jobs PASS.
- Current parity-complete v2 portable SHA-256: `86018d93c44fc2a93e270dfdb91dd9e3d6790149e20f0081f86eb2b796405803`.
- Next gate: user Windows/Dota smoke. Beta/main remain untouched.

- Residual hostile-input/path-race review completed through `541d8b4f20e48a1f62dc4052f6347fd450a5ba55`.
- Hardened Windows alias/ADS/device paths; identity-checked bounded profile, D2PFX cache, generic JSON/JSONC, remap, Mods.txt, D2PFX manifest, VPK sidecar, and cursor-source reads.
- CI #218 / `35464400624`: **369/369 PASS**, Ruff clean, both validation jobs PASS, root + v2 Windows portable builds PASS.
- Current v2 portable SHA-256: `2acb39b7099b125a8583e727774cd112873c234ca9c22c36344671c3a25f5007`.
- Remaining gates: full Windows/Dota smoke and private _09 foliage alias human smoke. Beta/main remain untouched.

- User screenshot smoke exposed v2 D2PFX blank previews, over-dense grid, and missing Updated-date labels.
- Fixed at `fced5d8c412b493bd1a7ca2dd19f82e02d182f91`: correct data-branch JPG preview source + root fallback, fork date labels/mixed-date sorting, 4/3/2/1 responsive grid, visible action status, request-ordered search, and post-success install state.
- Installed preview extension/MIME fix `f6c7b63c0f42152f8ce20d891371434e0e5998ce` avoids saving downloaded JPG bytes as `preview.webp`.
- CI #220 / `35466711651`: **374/374 PASS**, Ruff clean, v2 validation/Svelte/plugin builds PASS, root + v2 Windows portable PASS.
- Current v2 portable SHA-256: `2f976b02ef49310f7f2c67a1f643e9bccbf47d98f1a6f3a6f184b563c7d3aee3`; GitHub v2 artifact digest `sha256:281b088b67efed0502cc4b6ec859e0363c75a470b37aa788e919c72810d0135c`.
- Next: D2PFX re-smoke, then full Windows/Dota smoke. Private foliage alias human smoke remains independent. Beta/main untouched.

- User preferred the old list-style Mod Library and requested it as a toggleable alternative to cards.
- Implemented at `1354b8549f0e546faed062794ba7669d0f0a5ba0`: List is the default; Cards remains available; preference persists across launches. List uses collapsible Standard/Collections/D2PFX/VPK sections, selected counts, compact metadata rows, and 64x36 thumbnails only for mods with previews.
- CI #221 / `35467625867`: **375/375 PASS**, Ruff clean, v2 Svelte/plugin validation PASS, root + v2 Windows portable PASS.
- Current v2 portable SHA-256: `87a59e0959cd6f7a96971055b619c254aff1d1876ddbe68eae0dc27d811b261e`; artifact digest `sha256:54acf4d448a0db4744fc10c3bde20f83c419bca538085c30f8c101bd0dbadb4e`.
- Next: Mod Library/D2PFX smoke, then full Windows/Dota smoke. Beta/main untouched.

- User smoke of #221 found D2PFX mods incorrectly under Standard and Single Hero nested mods under one generic Collections section; requested legacy selection buttons back.
- Root causes: ModService discarded string-form `browser: "d2pfx"`; initial v2 list grouped every nested mod under literal `collection` rather than the actual parent-group label.
- Fixed at `1c17df75253aa9b5c3924497e78587ad51ff9e81`: D2PFX schema normalization, real collection section labels such as Hero Mods, and Select all/Clear/Invert/Expand all/Collapse all. Bulk state changes preserve always/untickable mods.
- CI #222 / `35468658278`: **377/377 PASS**, Ruff clean, v2 Svelte/plugin validation PASS, root + v2 Windows portable PASS.
- Current v2 portable SHA-256: `3312efd9cbdfc84ffb87805504205fafc1af376d7e5b2b72007fdf835a7a90de`; artifact digest `sha256:7acb394329eaf3ae6ccdde6c7e14ff2f9370de37225078428e0cbf2452dd87b8`.
- Next: section/bulk-control/D2PFX smoke, then full Windows/Dota smoke. Beta/main untouched.

- User PATCH smoke on #222 failed in preflight with Windows `WinError 5` replacing `config/mod-content-index.json`.
- Root issue was treating a disposable collision-index cache write as mandatory. Fix `c8dd5d6167279ea98bfcddadbeea7e4910084831` makes cache persistence resilient/non-fatal while retaining the computed index in memory.
- CI #223 / `35469297934`: **379/379 PASS**, Ruff clean, v2 validation/Svelte/plugin builds PASS, root + v2 Windows portable PASS.
- Current v2 portable SHA-256: `4413087967b6170c70a9fa9c568002b0d8806b73498d20973c916337b5845516`; artifact digest `sha256:f5ce5d38a127577d73b1ace29575cd17f65a6f1eab583dbae91d566837cc1c74`.
- Next: user retry PATCH/preflight. Beta/main untouched.

- PATCH smoke on #223 showed D2PFX CREEP-DENY variants blocked although rc7 permits the same selection.
- Root cause: v2 plugin/category `category_conflicts` were converted into synthetic hard conflicts.
- Fixed at `99bf24ea8702a50b456d472189db5d7eb49fc967`: category/plugin overlaps are report-only; explicit manifest conflicts remain blocking; Dark Terrain compatibility remains independent.
- CI #224 / `35470208025`: **380/380 PASS**, Ruff clean, v2 Svelte/plugin validation PASS, both Windows portable builds PASS.
- Current ZIP SHA-256 `f6ee41ed9f11c11ea24b3fdbf01a2b33c88118a6fa270b235ba6105a8af60190`; v2 artifact digest `sha256:9ee5af9352cc5a5831641f58f1bddf171d647cbe9d5cdc641f9f3ac7e4793328`.

- User requested visible PATCH progress and terminal output on Home.
- Implemented `c7b319e46d06991d2d2bb69a3e31631caa869509`: immediate preflight/patch status bar, PatchService start log, Home live recent-terminal panel with full-terminal shortcut, and no automatic tab switch on patch start.
- CI #225 / `35470787033`: **381/381 PASS**, Ruff clean, v2 validation/Svelte/plugin builds PASS, both Windows portable builds PASS.
- Current v2 ZIP SHA-256 `d6b45e3f7e77c68ff8919fae6d51761524c3d8d2f16c26f1467d342c038066af`; v2 artifact digest `sha256:1b72b6265599eaed4e3bbd4686d3e164297a974f2bf9a86b525c8c63d2e06cda`.

- User requested rc7-style All/None controls per Mod Library section.
- Implemented `ca24d6a7a16add68333dced211fc6a1248fe3d7c`: expanded sections show `Select in this section — All / None`; actions cover hidden/filtered members too and preserve always/untickable mods; section counts use complete membership.
- CI #226 / `35471631659`: **382/382 PASS**, Ruff clean, v2 validation/Svelte/plugin PASS, both Windows portable builds PASS.
- Current v2 ZIP SHA-256 `a6e3ba78514c992c32ae0b8b223aafc75c749c77054a6db75851af685b87cceb`; artifact digest `sha256:4cfb684d75e229b2c0e32a94956eec651d1f8d0c4a4ab7ae2f297fa0b56018b2`.

- User requested a Hero Mods bulk action that keeps default heroes enabled unless an active D2PFX mod replaces them.
- Added `Defaults except D2PFX` at `811e971b7a3c2a12e0c396843adc19d26b5f6c1f`; formatted/validated head `3d4c355aed635661cf3a0fd3b89b7e9f48360de5`.
- Matching uses real content-index overlap between Hero defaults and enabled D2PFX mods; it does not guess from names and ignores disabled D2PFX mods.
- CI #229 / `35473330452`: **384/384 PASS**, Ruff clean, v2 validation/Svelte/plugin PASS, both Windows portable builds PASS.
- Current v2 portable SHA-256 `8bec9db28cc641cfbc7a64aab32c3b37bf7835185e2983d32ad5ab87a70b6550`; v2 artifact digest `sha256:9742a971fc1ed0994d65f5fcd15bda3c04d333084f59821651c10de13feb041b`.

- User noticed installed D2PFX mods were shown in one name-sorted section rather than organized by category.
- Fixed at `257010615572a61e54ef4473f853d9636da2789b`: D2PFX list grouping now uses stored category metadata and produces separate humanized D2PFX category sections, retaining per-section counts and All/None.
- CI #230 / `35474054089`: **385/385 PASS**, Ruff clean, v2 validation/Svelte/plugin PASS, both Windows portable builds PASS.
- Current v2 portable SHA-256 `aa7fd595767ff61af453f75ad6212c5c354617425ecc55850cdadd59c91fda53`; v2 artifact digest `sha256:d8f75b4431e00dc2f75dda1139fd694ed194c27d7e742ec15e1b12c183057823`.
- Next: user smoke of D2PFX category sections; continue PATCH/full Dota smoke. Beta/main untouched.

- User clarified D2PFX layout should be one collapsible parent, not one top-level section per category.
- `0db87a1bbe4b8e79bd3f49f4afa924fa6aea3e86` restores that hierarchy: one `D2PFX Mods` collapsible, category subheaders inside, per-category counts and All/None retained.
- CI #231 / `35474663691`: **385/385 PASS**, Ruff clean, v2 validation/Svelte/plugin PASS, root + v2 Windows portable PASS.
- Current v2 portable SHA-256: `95653076e5874def8cc2e4507e5917cf1e51f3e52d54c47f5da0bb233b3a2108`; artifact digest `sha256:a418597a9181c826595fdcb48e34d5e3a59bcf8b7599415395b08f23472770ff`.
- Beta/main untouched. Next: user D2PFX nesting smoke, then PATCH/full Dota smoke.


- User supplied custom Transparent HUD v1.4 after restart crash: `ModuleNotFoundError: dearpygui` from its rc7-only `script_initial.py`.
- Archive inspection: 17 manifest settings; initial hook patches DearPyGui `ui.details`; remaining `script.py`, after-decompile, and after-patch logic uses v2-compatible core APIs.
- Fix: DearPyGui legacy runtime bundled; manifest-backed rc7 DearPyGui Details hooks skipped on v2; initial lifecycle exceptions no longer crash startup. Exact user archive needs no rewrite.
- Validated code head `c4c3e44c5adb59ca9819d5f36dcec4f1a5cf68cc`; CI #234 / `35480754644`: **388/388 PASS**, both Windows builds PASS.
- Current v2 portable SHA-256 `3ba0ba120550c343660051427fbc916e0658d27496ef1a0f3e6fa69ada8760fe`; artifact digest `sha256:1f28594f6bc2a87a477c48fed3ddfed74238078b7848f62a960658a5a3d2549c`.
- Next: restart/Settings/PATCH/Dota smoke with exact custom Transparent HUD. Beta/main untouched.
