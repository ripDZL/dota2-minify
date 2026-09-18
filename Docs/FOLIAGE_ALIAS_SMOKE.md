# Foliage Alias Smoke

- Scope: human-only validation of the private `_09` stock-material alias; not production behavior.
- Production `Remove Foilage` remains unchanged until smoke passes.
- Generator: `scripts/foliage_alias_smoke.py`.
- Generator extracts current `materials/models/props_tree/tree_oak_leaves_05.vmat_c` from local Dota `pak01_dir.vpk`.
- Generated smoke mod keeps committed blank `_05.vmat_c`, writes current stock bytes as private `_09.vmat_c`, and redirects affected tree model RERL names `_05 -> _09`.
- Redirect is same UTF-8 byte length; IDs remain unchanged.
- Generated mod/ZIP contains a Valve stock binary and must stay local; never commit or redistribute it.
- Default output: `Minify/mods/Remove Foilage - Private Alias Smoke`; this folder is already ignored by the repo's mod ignore policy.
- Run: `uv run python scripts/foliage_alias_smoke.py`.
- If Dota is outside a common Steam path: `uv run python scripts/foliage_alias_smoke.py --dota-pak "X:\\...\\dota 2 beta\\game\\dota\\pak01_dir.vpk"`.
- During smoke: production `Remove Foilage` unchecked; private alias smoke checked.
- PASS requires all three: stock trees visible; target foliage gone; tree/pathing collision normal.
- FAIL on any item: do not port alias to production; record screenshot/map location and exact failure.
