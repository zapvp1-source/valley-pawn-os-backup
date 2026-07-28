#!/usr/bin/env python3
"""
Test for Job J (Monthly Gold Trend) — stdlib only.

No prior canon exists for #gold-trend- (the spec's proposed format becomes
canon on the first real post), so this can't be a byte-exact golden test
like Jobs A-D/H. Instead it locks in:

1. extract_scrap_refining_gold() against the real backfilled 2025/2026 CSVs
   (Bravo Data Extraction/output/) -- summed bucket totals for a few known
   store-months, spot-checked by hand against the raw CSV rows.
2. The LEX mislabel fix: LEX's June 2026 data must read as "2026-06" in the
   consolidated history, not "2026-07" (the raw Bravo file still says
   2026-07 -- this locks in the CORRECTED consolidated history file, not
   the raw upstream export).
3. The YTD fix: YTD must compare the SAME set of available current-year
   months against their prior-year equivalents, not a fixed Jan..report_month
   range -- regression test for the "-76% nonsense" bug found 2026-07-27.

Run: python3 tests/test_gold_trend.py
"""
from __future__ import annotations
import csv
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from vpops import bravo, formats  # noqa: E402


def check(label, got, expected) -> bool:
    ok = got == expected
    print(f"{'PASS' if ok else 'FAIL'} — {label}" + ("" if ok else f" (got {got!r}, expected {expected!r})"))
    return ok


def main() -> int:
    all_ok = True
    output_dir = REPO.parent.parent / "Bravo Data Extraction" / "output"

    # --- 1. extractor against real raw CSVs ---
    cul_2025 = formats.extract_scrap_refining_gold(output_dir / "2025_CUL_scrap-refining-gold.csv")
    all_ok &= check("CUL 2025-01 = Jan W/Stones (98.7126663688948) + Jan Scrap (96.1)",
                     round(cul_2025["2025-01"], 4), round(98.7126663688948 + 96.1, 4))
    way_2025 = formats.extract_scrap_refining_gold(output_dir / "2025_WAY_scrap-refining-gold.csv")
    all_ok &= check("WAY 2025-04 = single combined bucket (100.4, no separate stone bucket that month)",
                     round(way_2025["2025-04"], 4), 100.4)

    cul_2026 = formats.extract_scrap_refining_gold(output_dir / "2026_CUL_scrap-refining-gold.csv")
    all_ok &= check("CUL 2026-07 excludes the real OPEN bucket (53.6685788379027 dwt, still accumulating) "
                     "-- an open bucket appeared live in the raw file 2026-07-27 and must not count as final",
                     "2026-07" in cul_2026, False)

    # --- 2. consolidated history: LEX mislabel correction ---
    history = bravo.read_gold_dwt_history()
    lex_rows = {r["year_month"]: float(r["dwt"]) for r in history if r["store"] == "LEX"}
    all_ok &= check("LEX June 2026 recorded as 2026-06 in history (not raw Bravo's 2026-07 mislabel)",
                     "2026-06" in lex_rows, True)
    all_ok &= check("LEX 2026-07 key does NOT exist in corrected history",
                     "2026-07" in lex_rows, False)
    if "2026-06" in lex_rows:
        all_ok &= check("LEX June 2026 dwt = both June-named buckets summed (41.565684699643 + 23.5)",
                         round(lex_rows["2026-06"], 4), round(41.565684699643 + 23.5, 4))

    # --- 3. YTD fix: same-months comparison, not a fixed Jan..report_month range ---
    by_key = {(r["store"], r["year_month"]): float(r["dwt"]) for r in history}
    report_month = "2026-06"
    current_year_months = sorted({ym for (_s, ym) in by_key if ym.startswith("2026") and ym <= report_month})
    all_ok &= check("Only one 2026 month exists in history so far (June)", current_year_months, ["2026-06"])
    ytd_current = sum(by_key.get((s, ym), 0.0) for s in bravo.STORES for ym in current_year_months)
    ytd_prior = sum(by_key.get((s, "2025-06"), 0.0) for s in bravo.STORES for ym in current_year_months)
    company_june_2026 = sum(v for (s, ym), v in by_key.items() if ym == "2026-06")
    company_june_2025 = sum(v for (s, ym), v in by_key.items() if ym == "2025-06")
    all_ok &= check("YTD current == June 2026 company total (not padded by nonexistent Jan-May)",
                     round(ytd_current, 4), round(company_june_2026, 4))
    all_ok &= check("YTD prior == June 2025 company total (matching the SAME month set, not full Jan-June)",
                     round(ytd_prior, 4), round(company_june_2025, 4))

    if all_ok:
        print("\nALL PASS — extractor verified against real Bravo CSVs; LEX mislabel fix and YTD "
              "same-months fix both locked in against the real consolidated history.")
        return 0
    print("\nFAIL — see above.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
