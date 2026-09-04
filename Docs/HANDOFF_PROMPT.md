# New Chat Handoff Prompt
- Work only in `ripDZL/dota2-minify` branch `v21.4-hardening` unless the user explicitly changes the plan.
- First read `Docs/AI_CONTEXT.md`, `Docs/TODO.md`, `Docs/PROGRESS.md`, `Docs/ARCHITECTURE.md`, `Docs/SESSION_SUMMARY.md`, and this file.
- Keep `main` upstream-tracking and untouched; keep `beta` frozen until remaining hardening/runtime gates pass. Beta ref remains `af83bbb051edced195d5f55ba49ff060a8c76f3c`.
- Exact upstream baseline: `Minify-v1.14rc7` commit `d4b4520c945a9e1f8f5facc52a76ac5903babe90`.
- Current tested code commit: `1c49475c59750d3669256885399c47efe06459db`; later branch commits may be Docs-only.
- Hardening CI run `33928368807` on `1c49475c`: compileall PASS; Ruff format gate PASS; Ruff lint PASS; pytest 131/131 PASS; Windows PyInstaller/runtime copy/portable ZIP/upload PASS.
- Current test ZIP: `Minify-v21.4-hardening-1c49475c59750d3669256885399c47efe06459db-windows.zip`; SHA-256 `3b86f34536ed1e0e0d3644bca64cdca51db33c03fb15311b69fb3fc744ce5aa3`; 53600449 bytes.
- Canonical user feature-reference is now uploaded `Minify-v1.14rc7-ModManager-v21.3.1-Safe-Foliage-Fix (1).zip`; SHA-256 `37755c4ee92e1847eef1a5a9c89aef6ba488f33accd0cb102c62a7db8780b5f8`.
- The uploaded v21.3.1 archive contains source overlays, exact-rc7 build/patch script, and bundled fork regression tests; 116/116 pass locally. Use this archive to recover the complete fork feature/fix set.
- Previous v21.2 beveled-UI ZIP is superseded as the target reference. Its seven UI/shell files already restored to hardening remain useful provenance but are not the complete feature baseline.
- v21.3.1 reference covers beveled Obsidian + Ember UI, Mod Library workspace, recursive/nested mods, markerless/collapsible Collections, profiles/import flow, D2PFX browser/imports, backups/conflict review, no-auto-prelaunch cleanup, Dark Terrain collision behavior, Safe Foliage, and Remove Main Menu Background CSS behavior.
- Do not wholesale copy v21.3.1 core overlay files onto hardening. Reconcile feature-by-feature so newer security/backend changes survive.
- v21.3.1 overlay `core/mod_library.py` is 68521 bytes / Git blob `56df3e70990003cfd76f04cbacf7878bba6e65ec`; it does not match the current hardening blob or the previously validated v21.4 source and is therefore a feature reference only.
- Prior v21.4 `core/mod_library.py` reconciliation remains blocked: current blob `a5204ea1d5e0309d3c6a764ad9b974e7bdeb8268`; expected validated blob `e95b2f6f59b3b96f7c19ed70ee514df02e500926`, SHA-256 `552dbb7f98d5e0db2ad32c1b2888d8ad4ae8945fdf49ebc2853765e59c6c9e7a`, 69949 bytes.
- Missing bootstrap chunk `005` contains the final 2089 compressed bytes of that exact prior v21.4 ZIP entry. Never fabricate missing bytes; never create `.materialize/READY` while payload is incomplete.
- Remove Foilage must remain blacklist-only. Never ship `Minify/mods/Remove Foilage/manifest.json` or `Minify/mods/Remove Foilage/maps/dota.vpk`; retain exact oak-leaf material/model blacklist entries.
- Steam policy: manual rc7 `prelaunch` remains; automatic Minify prelaunch injection disabled; stale generated wrappers cleaned narrowly.
- Hardening format gate excludes `Minify/core/mod_compat.py`, `Minify/core/mod_library.py`, `Minify/core/security.py`, `Minify/ui/settings.py`; compileall and full Ruff lint remain mandatory.
- Historical local hardening kit: 133/133 tests + 9 subtests; current GitHub suite: 131/131; uploaded v21.3.1 archive suite: 116/116. Keep these scopes distinct.
- Next work: diff/materialize complete v21.3.1 patch output and adapt its regression tests into canonical repo paths, rerun full CI/Windows build, then user/Dota smoke tests.
- Do not fast-forward `beta`, merge, tag, release, or open publication PR before remaining gates pass.
- At every major milestone update relevant `Docs/*.md` files; keep them terse bullets only.

## Resume instruction
- Read Docs, fetch current `v21.4-hardening`/`beta`/`main` refs, preserve tested-code/artifact identity above, use the v21.3.1 uploaded archive as canonical feature reference, and continue from `Docs/TODO.md`.