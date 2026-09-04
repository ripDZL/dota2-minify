# New Chat Handoff Prompt
- Work only in `ripDZL/dota2-minify` branch `v21.4-hardening` unless the user explicitly changes the plan.
- First read `Docs/AI_CONTEXT.md`, `Docs/TODO.md`, `Docs/PROGRESS.md`, `Docs/ARCHITECTURE.md`, `Docs/SESSION_SUMMARY.md`, and this file.
- Keep `main` upstream-tracking and untouched; keep `beta` frozen until remaining hardening/runtime gates pass. Beta currently points to `af83bbb051edced195d5f55ba49ff060a8c76f3c`.
- Exact upstream baseline: `Minify-v1.14rc7` commit `d4b4520c945a9e1f8f5facc52a76ac5903babe90`.
- Current tested code commit: `1c49475c59750d3669256885399c47efe06459db`. Re-fetch branch refs because a later docs-only milestone commit may be branch head while executable bytes still correspond to this tested code commit.
- Hardening CI run `33928368807` on `1c49475c`: compileall PASS; Ruff format gate PASS; Ruff lint PASS; pytest 131/131 PASS; Windows PyInstaller/runtime copy/portable ZIP/upload PASS.
- Corrected UI test ZIP: `Minify-v21.4-hardening-1c49475c59750d3669256885399c47efe06459db-windows.zip`; SHA-256 `3b86f34536ed1e0e0d3644bca64cdca51db33c03fb15311b69fb3fc744ce5aa3`; 53600449 bytes.
- Previous `2b861d37...` test artifact was technically green but rejected by the user because it lacked their UI implementation; do not use it as the current UI baseline.
- User-supplied UI source of truth: `Minify-v1.14rc7-ModManager-v21.2-Beveled-UI.zip`; SHA-256 `92b75cd95434bbad0ef9eef0ddf2a67e0c6dc8b2730d08ff1bfeb3f7eed57b92`.
- Exact v21.2 UI reference was materialized from exact rc7 by its original patcher at `1d138d418fd823693260c4a9fddf039436daaca5`; supplied ZIP hash gate + compileall passed.
- UI restore commit `ae0c9e574b2afc05e78e7710e66f3d898b10c44f` transplanted only seven UI/shell files from that reference: `Minify/__main__.py`, `Minify/browsers/d2pfx/ui.py`, `Minify/ui/checkboxes.py`, `Minify/ui/gui.py`, `Minify/ui/settings.py`, `Minify/ui/theme.py`, `Minify/ui/window.py`. Newer hardening core/backend files were preserved.
- Restored UI includes Obsidian + Ember/beveled shell, Mod Library workspace, Collections/profiles, redesigned Settings, D2PFX browser/import UI, nested mod-path handling.
- Hardening format gate excludes `Minify/core/mod_compat.py`, `Minify/core/mod_library.py`, `Minify/core/security.py`, `Minify/ui/settings.py`; compileall and full Ruff lint remain mandatory.
- Preserve recursive/nested mods, markerless/collapsible Collections, profiles, D2PFX browser/imports, backups/conflict review, no-auto-prelaunch policy, Remove Main Menu Background CSS fix, and collision-driven Dark Terrain behavior.
- Remove Foilage must remain blacklist-only. Never ship `Minify/mods/Remove Foilage/manifest.json` or `Minify/mods/Remove Foilage/maps/dota.vpk`; retain exact `tree_oak_leaves_05.vmat_c` and `tree_oak_leaves_05.vmdl_c` blacklist entries.
- Steam policy: manual rc7 `prelaunch` remains; automatic Minify prelaunch injection disabled; stale generated wrappers cleaned narrowly.
- `core/mod_library.py` still requires reconciliation before acceptance: remote blob `a5204ea1d5e0309d3c6a764ad9b974e7bdeb8268`; validated local hardening source had Git blob `e95b2f6f59b3b96f7c19ed70ee514df02e500926`, SHA-256 `552dbb7f98d5e0db2ad32c1b2888d8ad4ae8945fdf49ebc2853765e59c6c9e7a`, 69949 bytes. Do not blindly overwrite either copy.
- Missing bootstrap chunk `005` contains the final 2089 compressed bytes of that exact ZIP entry; exact source cannot be reconstructed from committed chunks. Never fabricate missing bytes.
- Temporary bootstrap under `.materialize/` is migration tooling only. DO NOT create `.materialize/READY` while archive payload is incomplete; eventually complete with exact bytes or remove bootstrap after direct materialization.
- Historical local validated kit: 133/133 regression tests + 9 subtests; current GitHub suite is 131/131. Remaining fork regression tests are not yet fully materialized; do not claim otherwise.
- Remaining gates: user corrected-UI smoke test, Dota startup/lobby/demo-or-match/patch-rollback/profiles/D2PFX/Dark-Terrain/Remove-Foilage smoke tests, remaining fork regression-test materialization, patch/glue review, hostile-input/security sweep, complete rc7 diff review, `mod_library.py` reconciliation, staging/bootstrap cleanup.
- Do not fast-forward `beta`, merge, tag, release, or open publication PR before remaining gates pass.
- At every major milestone update the relevant `Docs/*.md` files in the same branch commit; keep them terse bullets only.

## Resume instruction
- Read Docs, fetch current `v21.4-hardening`/`beta`/`main` refs, preserve tested-code/artifact identity above, inspect changes since `1c49475c...`, then continue from `Docs/TODO.md`.