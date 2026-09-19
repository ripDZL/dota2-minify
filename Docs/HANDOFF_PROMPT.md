# Handoff Prompt

- Repo: `ripDZL/dota2-minify`.
- Branches must remain exactly: `v21.4-hardening`, `beta`, `main`.
- Work only on `v21.4-hardening` unless the user explicitly approves promotion.
- Re-fetch all 3 branch heads before edits.
- Current heads:
  - `v21.4-hardening`: `c12197d660fdee3ddc4057ff30b5f8f2afe923cd`
  - `beta`: `442d36dcc902f6436c6404f2947091663c254cc5`
  - `main`: `a26bc88a0d412e357965f2947091663c254cc5`
- Correction: re-fetch `main` before doing anything; the line above is intentionally not authoritative if branch state changed.
- At session start read:
  - `Docs/AI_CONTEXT.md`
  - `Docs/TODO.md`
  - `Docs/PROGRESS.md`
  - `Docs/ARCHITECTURE.md`
  - `Docs/SESSION_SUMMARY.md`
  - `Docs/V2_COMPATIBILITY_MATRIX.md`
  - `Docs/V2_PORT_PLAN.md`
  - this file.
- User-visible project responses need America/Detroit date + timestamp.

## Baselines
- Current rc7-derived production app remains rooted at commit `8f29962bb056a9f95ab224f135bf795ecbda2b93`.
- Integrated upstream rc7 baseline: `Egezenn/dota2-minify` `Minify-v1.14rc7` / `d4b4520c945a9e1f8f5facc52a76ac5903babe90`.
- Exact v2 architecture target: upstream `Minify-v2rc4` / `e444454684c2d7f809e7eef20a1b72d4422c50d7`.
- Never raw merge/rebase v2. Continue semantic porting under `V2_STAGING/`.

## Current v2 parity state
- Full exact v2rc4 source tree is materialized under `V2_STAGING/`.
- v2 launch identity bug from the first test ZIP was fixed at `0cf84afbcc67a2097753ef8648a84bc2f6533512`; runtime tests now import staged `core/base.py` and verify `TITLE`.
- Feature parity work now includes:
  - Stage 1 security/download/archive/update hardening.
  - Recursive/nested mods, Collections, custom VPKs, stable logical IDs.
  - Favorites and profiles.
  - Profile save/apply/update/copy/delete/import/export with ID remapping.
  - Transactional restore points + automatic rollback.
  - Collision indexing/report and patch preflight UI.
  - Dark Terrain resource-level yielding.
  - Black-Plum v2 theme and 960x680 minimum-fit behavior.
  - Compact D2PFX 960px layout.
  - Hardened Remove Foliage RERL behavior.
  - Local-only `_09` foliage alias smoke generator in Developer Tools.
  - Migration/workspace parity, state filters, sorting, selected counts.
  - Mod setting presets.
  - Verified dependency downloads / unsupported-architecture PATH-only behavior.
  - Nested-mod lifecycle script handling.
  - Stale Minify prelaunch cleanup without automatic Steam prelaunch injection.
  - Fork updater channel / `DISPLAY_VERSION`.
  - Custom output-path persistence and restore safety.
  - Workshop-independent RERL processing.
  - v2 Developer Tools parity actions.
  - v2 Home / Control Panel surface.
- Key recent commits:
  - `a30675b24e14514a1ce7bd519ee173f452674553` restore/collision/Dark Terrain transaction.
  - `1f4362c1472c7dde715b66713dd62c10b0429307` Black-Plum + 960x680.
  - `e0a757c5997ac4a48faeaf7a5efca578092c8690` foliage RERL + local smoke tool.
  - `5c7f84cb42ea3b8547ff412dcc84ed061edf48e8` profile import/export/update.
  - `109ef952d86864055d64d4fc36d64a2d6a8b6661` compact D2PFX.
  - `84025bd80aef3c981faebdbf1e5ef9e91a618cf5` migration/workspace parity.
  - `8c9e25d29e4e00b761a13b3ac00ef89548d16ce3` settings preset workflow.
  - `0001c872b419ff4568dc9eb2604e8a44a8325968` verified dependency + nested script parity.
  - `c2413b7636eecf7c25a50a6f7c436a7058a9f060` stale prelaunch cleanup.
  - `dffd3b54df4df32191d52f77f65cf1b68a762363` fork updater channel.
  - `5dbe79c919cf787eaef258a051bd6bd216994d21` custom output path + workshopless RERL.
  - `7129a85c2a8e354b8bf5329e9368eecd22157fc0` Developer Tools parity.
  - `e999af8443a498a65f529df104b0cf12f0645cdf` Home Control Panel.
  - `ebbca811b41ad334a1e1ac01824939c7d77914ff` restore safety with custom output paths.

## Current CI / build blocker
- User manually stopped the older stuck jobs.
- Workflow now uses:
  - concurrency cancel-in-progress.
  - `windows-2022`.
  - root Windows build timeout: 30 minutes.
  - v2 Windows job timeout: 60 minutes.
  - v2 executable build-step timeout: 45 minutes.
- Commit `2a2385e5efad0919f7c7e250ce70591a051a748d` changed staged v2 PyInstaller launch from nested `uv run pyinstaller` to `sys.executable -m PyInstaller`.
- Commit `c12197d660fdee3ddc4057ff30b5f8f2afe923cd` extended Windows build timeouts.
- CI #213 / run `35456691291` at handoff:
  - root `validate`: SUCCESS.
  - `validate-v2-staging`: SUCCESS.
  - root `build-windows-portable`: SUCCESS.
  - `build-v2-windows-portable`: still stuck/in progress in **Build v2 executable and runtime package**.
- Validation currently reports **361 tests passed**; staged v2 compile/Ruff/Svelte/plugin build pass.
- The blocker is specifically the Windows v2 PyInstaller/runtime packaging step, not validation or the Svelte build.
- Do not wait indefinitely. Diagnose the PyInstaller stall itself. Prefer adding observable subprocess output/progress and isolating the exact PyInstaller stage rather than increasing timeouts again.

## Test ZIP rule
- User explicitly wants a v2 Windows ZIP **only when the parity work is done enough to test and the current build succeeds**.
- Do not send the old broken ZIP from `59746db...`.
- Do not present the older fixed-launch ZIP from `0cf84af...` as the current parity build.
- Once a current v2 Windows build succeeds:
  - download the `Minify-v21.4-hardening-v2rc4-windows` artifact.
  - extract the inner portable ZIP.
  - compute SHA-256 of the inner ZIP.
  - provide the sandbox download link + SHA-256.
  - state exact commit and CI run.

## Foliage
- Production/fork baseline uses blank `tree_oak_leaves_05.vmat_c`, blacklist `_08`, and same-length RERL `_05 -> _00`.
- v2 now ports this behavior.
- Private `_09` candidate remains **human-smoke only**:
  - keep original `_05` blank.
  - generate stock `_05` locally as unused `_09`.
  - redirect affected tree model RERL names `_05 -> _09` while preserving IDs/layout.
- Never commit or redistribute Valve stock binaries.
- Never claim foliage PASS without an actual Dota smoke test from the user.

## Next actions
- First: diagnose/fix the v2 Windows PyInstaller stall.
- Add runtime/packaging regression coverage where feasible; avoid grep-only tests when runtime semantics can be exercised.
- Re-run CI until the **current** v2 Windows portable artifact is produced.
- Then provide the user the ZIP for smoke testing.
- After user smoke feedback, fix only on `v21.4-hardening`.
- Keep `beta` and `main` untouched unless the user explicitly approves promotion.
