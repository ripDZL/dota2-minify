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
