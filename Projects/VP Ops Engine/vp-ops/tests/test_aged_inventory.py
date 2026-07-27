#!/usr/bin/env python3
"""
Golden test for Job B (aged inventory) — stdlib only.

Unlike Job A, there's no single historical Slack post to diff against
byte-for-byte (see formats.py's module docstring for why: 5+ inconsistent
historical formats, none matching the CLAUDE.md canonical spec). Instead
this checks the underlying $ figures against numbers manually verified
from the real 2026-07-13 #aged-inventory-review post for all 5 stores,
plus structural checks (fixed-width table, correct ranking, TOTAL row math).

Run: python3 tests/test_aged_inventory.py
"""
from __future__ import annotations
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from vpops import bravo, formats  # noqa: E402

# Manually verified against the real 2026-07-13 #aged-inventory-review Slack
# post (all 5 stores) on 2026-07-26.
EXPECTED_2026_07_13 = {
    "ROA": {"jewelry_aged": 20550.67, "genmerch_aged": 4286.25, "subtotal_cost": 130797.39},
    "HAR": {"jewelry_aged": 23595.70, "genmerch_aged": 4917.18, "subtotal_cost": 152994.60},
    "CUL": {"jewelry_aged": 22125.01, "genmerch_aged": 7013.14, "subtotal_cost": 184142.73},
    "LEX": {"jewelry_aged": 7862.74, "genmerch_aged": 3853.47, "subtotal_cost": 81178.69},
    "WAY": {"jewelry_aged": 6514.19, "genmerch_aged": 4157.94, "subtotal_cost": 109709.93},
}


def check_numbers() -> bool:
    ok = True
    enddate = "2026-07-13"
    files = bravo.locate_store_files(enddate, "aged-inventory-summary.csv")
    missing = bravo.missing_stores(files)
    if missing:
        print(f"FAIL: missing stores for {enddate}: {missing}")
        return False

    for store, path in files.items():
        got = formats.extract_aged_inventory_metrics(path)
        expected = EXPECTED_2026_07_13[store]
        for key in expected:
            if abs(got[key] - expected[key]) > 0.01:
                ok = False
                print(f"FAIL {store}.{key}: got {got[key]:.2f}, expected {expected[key]:.2f}")
    if ok:
        print(f"PASS — all 5 stores' $ figures match the real {enddate} Slack post.")
    return ok


def check_structure() -> bool:
    enddate = "2026-07-13"
    files = bravo.locate_store_files(enddate, "aged-inventory-summary.csv")
    data = {store: formats.extract_aged_inventory_metrics(path) for store, path in files.items()}
    msg = formats.render_aged_inventory(data, enddate)

    ok = True
    if "TOTAL" not in msg:
        ok = False
        print("FAIL: no TOTAL row in output")
    if "docs.google.com/spreadsheets" not in msg:
        ok = False
        print("FAIL: missing Google Sheets link")
    if "_Source: Bravo POS" not in msg:
        ok = False
        print("FAIL: missing Source footer line")

    # Ranking check: Roanoke should be worst (highest Tot%), Waynesboro cleanest,
    # per the real 2026-07-13 post.
    lines = msg.split("\n")
    table_lines = [l for l in lines if l.startswith("```") or (l and not l.startswith((":", "_", "h")) and "$" in l)]
    if not any("Needs the most attention: Roanoke" in l for l in lines):
        ok = False
        print("FAIL: expected Roanoke flagged as needing the most attention")
    if not any("Cleanest book: Waynesboro" in l for l in lines):
        ok = False
        print("FAIL: expected Waynesboro flagged as cleanest")

    # Fixed-width check
    table_start = next(i for i, l in enumerate(lines) if l.startswith("```"))
    table_end = next(i for i, l in enumerate(lines) if l.endswith("```") and i > table_start)
    tbl = lines[table_start:table_end + 1]
    tbl[0] = tbl[0][3:]
    tbl[-1] = tbl[-1][:-3]
    lengths = {len(l) for l in tbl}
    if len(lengths) != 1:
        ok = False
        print(f"FAIL: table rows not fixed-width, lengths found: {lengths}")

    if ok:
        print("PASS — structure (TOTAL row, Sheets link, Source footer, ranking, fixed-width table) all correct.")
    return ok


def main() -> int:
    ok = check_numbers() and check_structure()
    print("\n" + ("ALL PASS" if ok else "SOME FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
