# Build sources (not part of the published pages)

- `budget/` — budget-airline dashboard (/budget/): route matrix (make_routes.py → routes.json/md), sweep URLs (make_urls.py + tfs_lcc.js → urls-sweep1.txt), sweep results (raw/sweep1-google.md → parse_sweep.py), page build (build_budget.py + budget_template.html).
- `gba/` — Zone GBA dashboard (planned /gba/, not built yet): route matrix (parse_2lnr.py, probe_gba.py → make_routes.py → routes.json/md), sweep URLs (make_urls.py + tfs_gba.js → urls-sweep1.txt, plan in urls-sweep1-plan.md).

Raw HTML caches (2LNR pages) are not committed; they can be re-fetched. Public flight data only — no personal data.
