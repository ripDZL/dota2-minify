# v2rc4 Staging

- Upstream target: `Egezenn/dota2-minify` `Minify-v2rc4` / `e444454684c2d7f809e7eef20a1b72d4422c50d7`.
- Purpose: semantic-port staging only; not a user build and not a raw merge/rebase.
- Current slice: Stage 1 security substrate and exact high-risk caller ports.
- Stage 2A: recursive/nested mod discovery, Collections, stable logical IDs, nested/custom VPK category metadata, and logical-ID-aware service/patch/settings/D2PFX callers.
- `Minify/core/security.py`: fork path/archive/decompression/hash protections plus shared public-HTTPS and safe-download-name helpers.
- `Minify/core/fs.py`: v2rc4 filesystem module with bounded/atomic downloads, optional per-hop URL validation, timeout/redirect limits, and safe archive extraction.
- Staged callers: `ui/app.py`, D2PFX `data.py`/`api.py`/`build_hook.py`, `patch/remap_processor.py`, plus updater digest propagation in Svelte/TypeScript.
- Staging remains isolated under `V2_STAGING`; it is source/test staging, not a production v2 build. The full exact v2rc4 tree still must be integrated around these semantic ports before packaging.
