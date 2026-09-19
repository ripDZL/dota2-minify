# Handoff Prompt

- Repo: `ripDZL/dota2-minify`.
- Branches must remain exactly: `v21.4-hardening`, `beta`, `main`.
- Work only on `v21.4-hardening` unless the user explicitly approves promotion.
- Re-fetch all 3 branch heads before edits.
- Latest validated code head before handoff docs: `99bf24ea8702a50b456d472189db5d7eb49fc967`.
- Known untouched promotion heads at handoff:
  - `beta`: `442d36dcc902f6436c6404f2947091663c254cc5`
  - `main`: `a26bc88a0d412e357965f29488b83a7f9093e11f`
- Re-fetch the live `v21.4-hardening` head because this handoff document itself is committed after the code head.
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
  - D2PFX browser parity: max-4 desktop grid / compact 960px layout, working data-branch JPG previews + fallback, fork Updated-date labels, visible action status, stale-search protection, post-success install state, correct installed-preview MIME/extension.
  - Hardened Remove Foliage RERL behavior.
  - Local-only `_09` foliage alias smoke generator in Developer Tools.
  - Migration/workspace parity, state filters, sorting, selected counts.
  - Mod Library persistent List/Cards toggle; default legacy-style grouped list with actual legacy section names (Standard, each Collection such as Hero Mods, D2PFX, VPK), optional 64x36 previews, and Select all/Clear/Invert/Expand all/Collapse all controls.
  - Mod setting presets.
  - Verified dependency downloads / unsupported-architecture PATH-only behavior.
  - Nested-mod lifecycle script handling.
  - Stale Minify prelaunch cleanup without automatic Steam prelaunch injection.
  - Fork updater channel / `DISPLAY_VERSION`.
  - Custom output-path persistence and restore safety.
  - Workshop-independent RERL processing.
  - v2 Developer Tools parity actions.
  - v2 Home / Control Panel surface.
  - Residual hostile-input/path-race hardening: Windows alias/ADS/device-path rejection, identity-checked bounded local reads, profile/D2PFX/remap/config/mod-metadata/cursor race guards.
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
  - `fced5d8c412b493bd1a7ca2dd19f82e02d182f91` D2PFX preview/date/layout/state parity.
  - `f6c7b63c0f42152f8ce20d891371434e0e5998ce` preserve installed D2PFX preview image type.
  - `1354b8549f0e546faed062794ba7669d0f0a5ba0` restore persistent toggleable legacy-style Mod Library list view.
  - `1c17df75253aa9b5c3924497e78587ad51ff9e81` restore legacy collection section labels + bulk controls and fix string-schema D2PFX classification.
  - `c8dd5d6167279ea98bfcddadbeea7e4910084831` make derived content-index cache publication best-effort so Windows cache locks cannot abort patch preflight.

## Current CI / Windows build
- PyInstaller hosted-Windows DLL import-probe stall remains fixed by `472bfe794d4e0deecfc1e5deb352943737e181e6`.
- Residual security hardening stack:
  - `3a37edb7f0f814e6276f5fff3d03ffbca1dd5b1d`: Windows path aliases/ADS/device names + bounded identity-checked profile reads.
  - `eecd7ef43156506ff5797030d34e5a1e10b50f8b`: D2PFX catalogue identity-checked reads.
  - `94a166544ce8455441abc9457f6e04a8e1ea4644`: cursor source identity check.
  - `734f083d53b4cd15df37956b1bc6cd70a801440a`: bounded generic JSON/JSONC + remap reads.
  - `541d8b4f20e48a1f62dc4052f6347fd450a5ba55`: bounded D2PFX/sidecar mod metadata reads.
- CI #223 / run `35469297934`: **SUCCESS**.
  - root `validate`: SUCCESS, **379 tests passed**, Ruff clean.
  - `validate-v2-staging`: SUCCESS, including Svelte + D2PFX plugin builds.
  - root `build-windows-portable`: SUCCESS.
  - `build-v2-windows-portable`: SUCCESS.
- Runtime smoke found patch preflight blocked by Windows `WinError 5` while atomically replacing `config/mod-content-index.json`.
- `mod-content-index.json` is derived/disposable. v2 now uses an absolute cache destination, retries Windows permission/sharing failures, repairs a read-only destination when possible, keeps the live index in memory, and disables disk cache persistence for the process if publication still fails. Patch preflight continues.
- Mod Library legacy-section and D2PFX fixes from #222 remain included.
- Current v2 inner portable ZIP SHA-256: `4413087967b6170c70a9fa9c568002b0d8806b73498d20973c916337b5845516`.
- GitHub v2 artifact digest: `sha256:f5ce5d38a127577d73b1ace29575cd17f65a6f1eab583dbae91d566837cc1c74`.

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
- Current parity-complete v2 Windows test ZIP is built from `c8dd5d6167279ea98bfcddadbeea7e4910084831`; CI #223 / `35469297934`.
- Next immediate gate: user retry of patch preflight/PATCH on Windows, then continue Mod Library/D2PFX/full Windows/Dota smoke.
- Private foliage alias human smoke remains independent and must not be claimed PASS without actual Dota testing.
- Fix smoke findings only on `v21.4-hardening`.
- Keep `beta` and `main` untouched unless the user explicitly approves promotion.

- Conflict-semantics smoke fix: `99bf24ea8702a50b456d472189db5d7eb49fc967`.
  - Same-category/plugin overlaps stay advisory in preflight/reporting.
  - Only explicit per-mod manifest `conflicts` retain the rc7 hard stop.
  - Dark Terrain resource-yield compatibility remains independent.
- CI #224 / `35470208025`: **SUCCESS**, **380 tests passed**, Ruff clean, v2 validation/Svelte/plugin PASS, both Windows portable builds PASS.
- Current v2 portable SHA-256: `f6ee41ed9f11c11ea24b3fdbf01a2b33c88118a6fa270b235ba6105a8af60190`.
- Current GitHub v2 artifact digest: `sha256:9ee5af9352cc5a5831641f58f1bddf171d647cbe9d5cdc641f9f3ac7e4793328`.
- Next immediate gate: retry PATCH with the same D2PFX overlap set; expected result is warning/report + continued patch unless an explicit manifest conflict exists.
