# TODO
- [x] Keep exactly `v21.4-hardening`, `beta`, `main`.
- [x] Keep Dark Terrain independent from Remove Foilage.
- [x] Port/harden RERL concept; CI #166 **286/286 PASS**; Windows portable PASS.
- [x] Confirm simple `_05 -> _00` smoke still breaks some trees.
- [x] Reject target-name RERL ID updates.
- [x] Confirm blanking original `_05.vmat_c` removes target foliage.
- [x] Build private `_09` stock-material alias smoke candidate.
- [x] Add reproducible local `_09` smoke generator + portable Developer Tools action; no stock binaries committed; CI #171 **294/294 PASS**, Windows portable PASS.
- [ ] Human smoke private alias: all stock trees visible, target foliage gone, collision correct.
- [ ] If alias succeeds, implement dynamic current-stock aliasing; never commit Dota stock binaries.
- [x] Audit upstream `Minify-v2rc4` / `e444454684c2d7f809e7eef20a1b72d4422c50d7`.
- [x] Confirm v2rc4 is a major architecture rewrite; raw merge/rebase is unsuitable.
- [x] 960x680 DearPyGui fit gate: responsive Home/activity/footer, scroll-safe Mod Library/Settings, compact one-column D2PFX, client-clamped shared modals; CI #168 **289/289 PASS**, Windows portable PASS.
- [x] Fix startup Tutorial/Language Setup modal overlap and show `v21.4-hardening` as the user-facing version; CI #173 **295/295 PASS**, Windows portable PASS.
- [x] Build explicit v2 compatibility matrix before replacing product architecture (`Docs/V2_COMPATIBILITY_MATRIX.md`).
- [x] Map staged v2 security/product ports to exact upstream caller files (`Docs/V2_PORT_PLAN.md`).
- [x] Stage v2 Stage 1 security substrate and high-risk callers under `V2_STAGING/`; CI #176 **309/309 PASS**, Windows portable PASS.
- [x] Port `core/security.py` protections into v2 downloads/extraction/update/D2PFX/cursor paths.
- [x] Integrate staged Stage 1 into the complete exact v2rc4 architecture under `V2_STAGING/`; CI #191 validated both v2 frontend and Windows portable.
- [x] Port recursive/nested discovery, Collections, custom VPK categories into v2 `mods_shared` + ModService/UI.
- [x] Port collision report into v2 services/UI; profiles/favorites/mod-library metadata are staged and validated.
- [x] Port transactional restore points/rollback + compatibility validation into v2 PatchService/pipeline.
- [x] Port Dark Terrain collision-aware yielding; do not replace it with blanket category conflict.
- [x] Preserve Main Menu second `#FrontpageContents` collapse rule.
- [ ] Evaluate upstream v2 Remove Foliage `remap.json` against private-alias findings in isolated Dota smoke.
- [x] Preserve manual `prelaunch`; disable automatic Steam launch-option injection.
- [x] Rebuild Black-Plum as CSS theme and retain the same minimum-window fit invariant in v2.
- [x] Residual hostile-input/path-race review; CI #218 **369/369 PASS**, both Windows portable builds PASS.
- [x] Fix v2 D2PFX screenshot regression: working JPG previews/fallback, Updated-date parity, max-4 desktop grid, action feedback/search race/install-state fixes; CI #220 **374/374 PASS**, both Windows portable builds PASS.
- [x] Restore toggleable legacy-style Mod Library list view with collapsible type groups, optional compact previews, and persistent List/Cards choice; CI #221 **375/375 PASS**, both Windows portable builds PASS.
- [x] Restore legacy section naming + bulk controls and fix D2PFX classification: actual collection labels such as Hero Mods, Select all/Clear/Invert/Expand all/Collapse all, current string-schema D2PFX manifests; CI #222 **377/377 PASS**, both Windows portable builds PASS.
- [x] Fix Windows patch-preflight `WinError 5` on `mod-content-index.json`: derived cache is best-effort/in-memory on publish failure; CI #223 **379/379 PASS**, both Windows portable builds PASS.
- [ ] Retry patch preflight/PATCH on Windows, then smoke Mod Library List/Cards + corrected D2PFX Browser and continue full Windows/Dota smoke.
- [ ] Beta -> main only after validation and explicit approval.

- [x] Fix v2 runtime startup `base.TITLE` regression caused by literal escaped newlines in staged base identity; CI #192 PASS and replacement v2 portable built.
- [x] Diagnose/fix the v2 Windows PyInstaller dynamic-library stall; CI #214 PASS on `472bfe794d4e0deecfc1e5deb352943737e181e6`.
- [x] Produce the current patch-preflight + legacy-section + D2PFX-corrected v2 Windows portable from `c8dd5d6167279ea98bfcddadbeea7e4910084831`; SHA-256 `4413087967b6170c70a9fa9c568002b0d8806b73498d20973c916337b5845516`.
- [ ] User PATCH/preflight retry + Mod Library/D2PFX re-smoke + Windows/Dota smoke of the current v2 ZIP.

- [x] Restore rc7 conflict semantics in v2: category/plugin overlaps are advisory/report-only; explicit manifest conflicts remain hard blockers. CI #224 **380/380 PASS**, both Windows builds PASS.
- [ ] Retry PATCH with the same D2PFX overlap set; then continue full Windows/Dota smoke.

- [x] Add immediate PATCH/preflight live status text and Home embedded terminal; code `c7b319e46d06991d2d2bb69a3e31631caa869509`.
- [x] CI #225 / `35470787033`: **381/381 PASS**, Ruff clean, v2 validation/Svelte/plugin builds PASS, both Windows portable builds PASS.
- [x] Current v2 portable SHA-256: `d6b45e3f7e77c68ff8919fae6d51761524c3d8d2f16c26f1467d342c038066af`.
- [ ] Smoke live PATCH status/Home terminal while completing a real patch; continue Dota smoke.

- [x] Restore rc7-style All/None controls inside each expanded Mod Library section.
- [x] Section All/None acts on complete category/collection membership, not filtered rows; preserve always/untickable states.
- [x] CI #226 / `35471631659`: **382/382 PASS**, both Windows portable builds PASS.
- [ ] User smoke of per-section selection controls and continued PATCH/Dota behavior.

- [x] Add Hero Mods `Defaults except D2PFX` bulk action using real indexed resource overlap with enabled D2PFX mods.
- [x] CI #229 / `35473330452`: **384/384 PASS**, both Windows portable builds PASS.
- [ ] User smoke of D2PFX-aware Hero default selection.
