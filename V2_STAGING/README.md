# v2rc4 Staging

- Upstream target: `Egezenn/dota2-minify` `Minify-v2rc4` / `e444454684c2d7f809e7eef20a1b72d4422c50d7`.
- Purpose: semantic-port staging only; not a user build and not a raw merge/rebase.
- Current slice: Stage 1 core security substrate.
- `Minify/core/security.py`: fork path/archive/decompression/hash protections plus shared public-HTTPS and safe-download-name helpers.
- `Minify/core/fs.py`: v2rc4 filesystem module with bounded/atomic downloads, optional per-hop URL validation, timeout/redirect limits, and safe archive extraction.
- Remaining Stage 1 callers: `ui/app.py`, D2PFX `data.py`/`api.py`/`build_hook.py`, and `patch/remap_processor.py`.
- Do not package `V2_STAGING` as the production app until the Stage 1 gate passes.
