"""Shared airline exclusion list (permanent user rule, 11 Oct 2026): never search, show or recommend these carriers.
Used by gba/make_routes.py, gba/build_gba.py, budget/make_routes.py, budget/make_urls.py, budget/build_budget.py.
Google Flights tfs has no 'exclude airline' field (leg field 6 is include-only), so exclusion is applied at parse/build time."""
EXCLUDED_AIRLINES = {
    "9C": "Spring Airlines",
    "IJ": "Spring Japan",
    "AQ": "9 Air",
}
EXCLUDED_NAMES = ("Spring Airlines", "Spring Japan", "Spring", "9 Air")   # Google Flights display names
def is_excluded(code=None, name=None):
    if code and code.upper() in EXCLUDED_AIRLINES: return True
    if name:
        n = name.strip()
        return any(n == x or n.startswith(x + " ") or n.startswith(x) and n[len(x):len(x)+1] in ("", ",") for x in EXCLUDED_NAMES)
    return False
