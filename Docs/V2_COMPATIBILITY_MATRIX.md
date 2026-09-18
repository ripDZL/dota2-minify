# v2rc4 Compatibility Matrix

Baseline: upstream `Minify-v2rc4` / `e444454684c2d7f809e7eef20a1b72d4422c50d7`. Migration is semantic only; no raw merge/rebase.

| Capability | Current hardening fork | Upstream v2rc4 | Required action |
| --- | --- | --- | --- |
| UI architecture | DearPyGui Black-Plum; validated 960x680 fit | PyWebView + Svelte + CSS themes | Adopt v2 shell; rebuild Black-Plum as CSS; preserve minimum-fit invariant |
| Mod discovery | Recursive/nested mods, Collections, custom categories | `core/mods_shared.py` scans only direct `mods/` children | Port recursive discovery + stable logical IDs before UI migration |
| Profiles | Saved/apply/update/duplicate/import/export | No profile subsystem found | Port as service + persisted schema + migration |
| Favorites | Persisted favorites/filter | No favorite subsystem found | Port metadata + service/UI state |
| Custom VPK categories | Supported | Top-level VPKs only; manifest categories target directory mods | Port VPK identity/category metadata |
| Collision index/report | File-level ownership, overlap review | Manifest/category conflict rejection only | Port collision index + preflight API/UI |
| Dark Terrain | Independent; collision-aware resource yielding | `category: terrains` blanket category conflict | Reject as-is; port resource-level yield semantics |
| Restore points/rollback | Transactional pre-patch backup manager | No equivalent restore-point manager found | Port before patch pipeline cutover |
| Patch review | Review/overlap/restore safety before apply | Main UI starts patch directly after workshop check | Add preflight/review service endpoint and Svelte surface |
| Path/archive/network security | Central `core/security.py`; bounded downloads/extraction; confinement | No equivalent centralized security module | Port security substrate before D2PFX/update/install adoption |
| D2PFX | Hardened browser/install/download/cursor handling | Cleaner plugin architecture + Svelte browser | Adopt plugin architecture; replace data/API/build-hook internals with hardened semantics |
| Remove Foliage | Blank `_05` + hardened same-length RERL; current `_05 -> _00` smoke loses trees | `remap.json` also maps `_05 -> _00` via decompile/recompile | Do not adopt as validated fix; compare only after private `_09` human smoke |
| Main Menu background | Two collapse rules, including `#FrontpageContents` fix | Only dashboard background manager rule | Port second rule explicitly |
| Prelaunch policy | Manual command; no automatic Steam injection | `core/steam.py::add_prelaunch_to_launch_options` writes launch options when `patch_on_launch` | Disable automatic injection; retain explicit/manual prelaunch |
| Settings | Fork settings + hardening controls | Service-driven schema + Svelte settings | Adopt service pattern; map fork keys and defaults explicitly |
| Theme system | Python/DPG theme tokens | CSS theme files + runtime theme injection | Port Black-Plum tokens to CSS variables |
| Plugin surfaces | Native browser surfaces | Iframe/plugin service architecture | Adopt with origin/message/API review and same fit/security requirements |
| Test baseline | Hardening CI #168: 289/289 + Windows portable PASS | Different architecture/test surface | Port semantic regressions, not test implementation details |

## Staged semantic port order

1. **Security substrate:** port destination confinement, URL/redirect validation, bounded download/decompression, archive traversal/symlink rejection, atomic/staged writes, cursor confinement, backup validation.
2. **Mod model:** recursive discovery, nested Collections, custom VPK categories, stable identifiers, profiles/favorites.
3. **Patch transaction:** collision index, patch preflight, restore points/rollback, Dark Terrain resource-level yielding.
4. **D2PFX plugin:** keep v2 plugin/Svelte structure; replace download/install/archive/cursor paths with hardened fork behavior.
5. **UI migration:** Black-Plum CSS, responsive minimum-fit rules, Mod Library/Settings/terminal/dialog parity.
6. **Behavioral fixes:** Main Menu second rule, manual-prelaunch policy, locale behavior.
7. **Foliage:** evaluate v2 remap only against human-smoked alias findings; no target-name RERL ID updates; no stock binaries in repo.
8. **Validation:** migrated semantic regression suite, Windows portable build, then full Dota smoke before beta promotion.

## Security mapping

- `core/security.py` path confinement -> v2 ModService, PatchService, plugin install/update destinations.
- Bounded HTTP + redirect/host validation -> updater, D2PFX metadata/previews/payloads, workshop/bootstrap downloads.
- Safe archive extraction -> D2PFX packs and any plugin/update ZIP handling.
- Atomic/staged writes -> downloaded payloads, profile/config migrations, patch outputs, backups.
- Symlink/reparse-point rejection -> cursor operations, archive extraction, backup/restore.
- Size/count/decompression limits -> D2PFX archives, profiles, remote metadata, images.
- Transactional backup validation -> PatchService preflight/apply/rollback boundary.
