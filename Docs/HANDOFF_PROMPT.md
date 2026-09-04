# New Chat Handoff Prompt
- Work only in `ripDZL/dota2-minify` branch `v21.4-hardening` unless the user explicitly changes the plan.
- First read `Docs/AI_CONTEXT.md`, `Docs/TODO.md`, `Docs/PROGRESS.md`, `Docs/ARCHITECTURE.md`, `Docs/SESSION_SUMMARY.md`, and this file.
- Keep `main` upstream-tracking and untouched.
- Keep `beta` frozen until the hardening/materialization/runtime gates pass; beta currently points to `af83bbb051edced195d5f55ba49ff060a8c76f3c`.
- Exact upstream baseline is `Minify-v1.14rc7` commit `d4b4520c945a9e1f8f5facc52a76ac5903babe90`.
- Pre-handoff hardening head snapshot was `ac7562f852d5c1f8ca14630a92f26018c328642a`, 31 commits ahead of exact rc7. Re-fetch branch refs before editing because the branch may advance after this handoff commit.
- Local validated hardening-kit checkpoint: 133/133 regression tests + 9 subtests; Python compileall passed. Do not claim the fully materialized GitHub tree has passed that suite yet.
- Materialized source already present includes security/archive/VPK hardening, transactional backups, collision-driven Dark Terrain compatibility, no-auto-prelaunch Steam policy, dependency hash verification/architecture gating, recursive/nested mod scanning, Collections backend, nested lifecycle scripts, D2PFX nested build-hook handling, Optimization exposure, Remove Main Menu Background CSS fix, and `core/mod_library.py`.
- Rare dependency architecture issue is resolved: unsupported/nonexistent release assets are PATH-only; do not download a wrong architecture or unverified artifact.
- Remove Foilage must remain blacklist-only. Never ship `Minify/mods/Remove Foilage/manifest.json` or `Minify/mods/Remove Foilage/maps/dota.vpk`.
- Dark Terrain must yield `materials/dev/deferred_post_process.vmat_c` only when another selected mod actually owns that virtual path; Dark Terrain alone keeps its own post-process.
- `core/mod_library.py` requires reconciliation before acceptance: remote blob is `a5204ea1d5e0309d3c6a764ad9b974e7bdeb8268`; validated local hardening source had Git blob `e95b2f6f59b3b96f7c19ed70ee514df02e500926`, SHA-256 `552dbb7f98d5e0db2ad32c1b2888d8ad4ae8945fdf49ebc2853765e59c6c9e7a`, 69949 bytes, and compiled successfully. Determine the drift; do not blindly overwrite either copy.
- Forensic follow-up September 4, 2026: the validated archive entry starts at ZIP offset 22023, is 17398 bytes deflated / 69949 uncompressed, and ends at offset 39589 exclusive. Missing chunk `005` spans offsets 37500-44999 and contains the final 2089 compressed bytes, so the exact source cannot be reconstructed from committed chunks. Obtain exact validated source/blob or exact missing archive bytes before reconciliation.
- Temporary bootstrap files exist under `.materialize/` plus `.github/workflows/materialize-v21.4.yml`. They are migration tooling only, not canonical architecture.
- The one-time workflow expects handoff ZIP SHA-256 `97b2810c1e0ed2a51a407dd895d93e0f53e95bb82e65824cd41536da799fdece` and triggers only on `.materialize/READY`.
- DO NOT create `.materialize/READY` yet. At handoff snapshot only chunks `000`-`004` and `006`-`010` exist. The validated archive Base64 requires 23 chunks numbered `000`-`022`; `005` and `011`-`022` are missing. Never fabricate missing bytes. Obtain the exact validated archive before completing or remove this bootstrap once direct materialization is complete.
- Remaining materialization includes UI/check boxes, beveled Obsidian + Ember theme, Settings, patch integration/glue, window/gui/__main__ integration, D2PFX browser UI, profile/import UI, Remove Foilage blacklist correction, fork regression tests, and fork beta version identification.
- After full materialization: run upstream + fork tests, compileall/Ruff/static checks, hostile-input/security sweep, diff against exact rc7, cleanup of staging/cache artifacts, then Windows PowerShell/PyInstaller build and Dota smoke tests.
- Required Dota smoke tests: startup, lobby, demo/match load, patch/rollback, profiles, D2PFX, Dark Terrain + shader, and Remove Foilage.
- Do not fast-forward `beta`, merge, tag, release, or open a publication PR before the validation gates above pass.
- At every major milestone update the relevant `Docs/*.md` files in the same branch commit. Keep them terse bullets only.

## Resume instruction
- Read the Docs files, fetch current `v21.4-hardening`/`beta`/`main` refs, compare `v21.4-hardening` against exact rc7, inspect changes since the snapshot above, then continue from `Docs/TODO.md` without relying on prior chat memory.