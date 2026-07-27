#!/usr/bin/env python3
"""
Golden test for Job D (loan + layaway review) — stdlib only.

Layaway review: percentages are self-contained ratios (no external loan
balance needed), so they're verified byte-for-byte against the real
2026-07-13 13:26 post's percentages and counts.

Loan review: counts/$ figures verified against the real 2026-07-13 09:28
post exactly, but percentages intentionally are NOT compared — that post
used a stale 2026-06-21 loan balance snapshot; this job always uses the
freshest available EOM data instead (see formats.py module docstring).

Run: python3 tests/test_loan_layaway_review.py
"""
from __future__ import annotations
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from vpops import bravo, formats  # noqa: E402

EXPECTED_LAYAWAY_2026_07_13 = {
    "CUL": {"overdue": 10, "past_pmt_due": 15, "contacted_no_activity": 13, "no_pmt_30d": 15, "locate": 0},
    "HAR": {"overdue": 22, "past_pmt_due": 20, "contacted_no_activity": 6, "no_pmt_30d": 20, "locate": 1},
    "LEX": {"overdue": 6, "past_pmt_due": 10, "contacted_no_activity": 1, "no_pmt_30d": 10, "locate": 0},
    "ROA": {"overdue": 16, "past_pmt_due": 16, "contacted_no_activity": 12, "no_pmt_30d": 16, "locate": 0},
    "WAY": {"overdue": 2, "past_pmt_due": 8, "contacted_no_activity": 1, "no_pmt_30d": 8, "locate": 0},
}

EXPECTED_LOAN_2026_07_13 = {
    "CUL": {"count": 0, "dollar_sum": 0.0},
    "HAR": {"count": 22, "dollar_sum": 8298.83},
    "LEX": {"count": 19, "dollar_sum": 2320.0},
    "ROA": {"count": 22, "dollar_sum": 6714.0},
    "WAY": {"count": 9, "dollar_sum": 1005.0},
}


def check_layaway_numbers() -> bool:
    files = bravo.locate_store_files("2026-07-13", "layaways.csv")
    if bravo.missing_stores(files):
        print("FAIL: missing layaway files")
        return False
    ok = True
    for store, path in files.items():
        got = formats.extract_layaways(path)
        expected = EXPECTED_LAYAWAY_2026_07_13[store]
        if got != expected:
            ok = False
            print(f"FAIL {store}: got {got}, expected {expected}")
    if ok:
        print("PASS — layaway counts match the real 2026-07-13 post for all 5 stores.")
    return ok


def check_layaway_percentages() -> bool:
    files = bravo.locate_store_files("2026-07-13", "layaways.csv")
    data = {s: formats.extract_layaways(p) for s, p in files.items()}
    msg = formats.render_layaway_review(data, "7/13/2026")
    # Real post: Culpeper 10(18%) 15(22%) 13(39%) 15(22%); Company 56 69 33 69 :red_circle:1
    checks = [
        "10 (18%)" in msg, "15 (22%)" in msg, "13 (39%)" in msg,
        "22 (39%)" in msg, "20 (29%)" in msg, "6 (18%)" in msg,
        "Company" in msg and "56" in msg and "69" in msg and "33" in msg,
        ":red_circle:1" in msg,
        "Harrisonburg has 1 Locate Layaway(s)" in msg,
    ]
    ok = all(checks)
    print(("PASS" if ok else "FAIL") + " — layaway percentages/company row/locate callout match the real post.")
    return ok


def check_loan_numbers() -> bool:
    files = bravo.locate_store_files("2026-07-13", "loans-75-days-past-due.csv")
    if bravo.missing_stores(files):
        print("FAIL: missing loan files")
        return False
    ok = True
    for store, path in files.items():
        got = formats.extract_loan_past_due(path)
        expected = EXPECTED_LOAN_2026_07_13[store]
        if got["count"] != expected["count"] or abs(got["dollar_sum"] - expected["dollar_sum"]) > 0.01:
            ok = False
            print(f"FAIL {store}: got {got}, expected {expected}")
    total = sum(formats.extract_loan_past_due(p)["dollar_sum"] for p in files.values())
    if abs(total - 18337.83) > 0.01:
        ok = False
        print(f"FAIL: company total {total:.2f} != 18337.83")
    if ok:
        print("PASS — loan past-due counts/$ match the real 2026-07-13 post exactly (company total $18,337.83, 72 items).")
    return ok


def main() -> int:
    ok = check_layaway_numbers() and check_layaway_percentages() and check_loan_numbers()
    print("\n" + ("ALL PASS" if ok else "SOME FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
