# AI Context
- Baseline: `Egezenn/dota2-minify` tag `Minify-v1.14rc7`, commit `d4b4520c945a9e1f8f5facc52a76ac5903babe90`.
- Fork: `ripDZL/dota2-minify`; branch flow `v21.4-hardening` -> `beta` -> `main`; exactly three branches.
- `beta`: `442d36dcc902f6436c6404f2947091663c254cc5`; `main`: `a26bc88a0d412e357965f29488b83a7f9093e11f`; both untouched by current foliage work.
- Current Remove Foilage split: blacklist only `tree_oak_leaves_08.vmat_c`, `tree_oak_leaves_blank.vmat_c`, and `tree_oak_leaves_08.vmdl_c` under tree namespaces; keep `_05` and stock tree/static/destruction models preserved.
- Dark Terrain is being decoupled from automatic `Remove Foilage` activation so terrain can run without inheriting foliage/tree side effects.
- Vanilla-tree compatibility mod goal: preserve every default tree resource at stock paths and apply only a microscopic saturation change; source payload must be extracted from the user's local Dota `pak01` archives.
- User supplied `pak01_dir.vpk`; full compiled tree payloads still require the referenced `pak01_###.vpk` data chunks or a local extraction step.
- Human Dota smoke remains required for Remove Foilage alone, Dark Terrain alone, and Dark Terrain + optional Remove Foilage/tree override.
- Do not promote `beta` until user approves gameplay behavior.
