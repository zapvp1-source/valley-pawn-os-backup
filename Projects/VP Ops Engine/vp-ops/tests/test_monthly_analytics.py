#!/usr/bin/env python3
"""
Test for Job I (Monthly Analytics) — stdlib only.

Unlike Jobs A-D/H, there is no byte-exact historical Slack post to test
against: the real 2026-07-03 post's table bodies are unrecoverable (Slack
strips table blocks from plain-text history), and no Google Sheet exists for
June 2026 (see STATE.md's I-0 discovery notes). Instead this locks in:

1. extract_company_kpis() against the real 2026-06-30 company-kpis.xlsx,
   verified two independent ways: against Bravo's own "Net Revenue MTD"
   dashboard card ($230.09K), and against parse_eom.py's own hard-coded
   penny-verified CUL ($66,649.27) / HAR ($61,666.31) June 2026 figures.
2. compute_monthly_windows() against the real 2026-05-2026 post's own
   verbatim T12M-clamp note ("T12M Prior start = 6/3/2024 ... 2-day
   variance").
3. The title/View-1/YTD/T12M header LINES against the real verbatim
   2026-07-03 post text (the one part of that post that WAS recoverable).

Run: python3 tests/test_monthly_analytics.py
"""
from __future__ import annotations
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FIXTURES = Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(REPO))

from vpops import bravo, formats  # noqa: E402


def check(label, got, expected) -> bool:
    ok = got == expected
    print(f"{'PASS' if ok else 'FAIL'} — {label}" + ("" if ok else f" (got {got!r}, expected {expected!r})"))
    return ok


def main() -> int:
    all_ok = True

    # --- 1. extract_company_kpis vs real, independently-verified numbers ---
    data = formats.extract_company_kpis(FIXTURES / "company-kpis_2026-06-30.xlsx")
    all_ok &= check("GT Net Revenue == Bravo's own Net Revenue MTD card ($230,094.28 ~= $230.09K)",
                     round(data["GT"]["Net Revenue"], 2), 230094.28)
    all_ok &= check("CUL Net Revenue matches parse_eom.py's penny-verified figure",
                     round(data["CUL"]["Net Revenue"], 2), 66649.27)
    all_ok &= check("HAR Net Revenue matches parse_eom.py's penny-verified figure",
                     round(data["HAR"]["Net Revenue"], 2), 61666.31)
    all_ok &= check("GT Retail Sales", round(data["GT"]["Retail Sales"], 2), 192789.27)
    all_ok &= check("GT Scrap Sales", round(data["GT"]["Scrap Sales"], 2), 95181.44)
    all_ok &= check("GT Inventory Balance", round(data["GT"]["Inventory Balance"], 2), 683249.66)
    all_ok &= check("GT Loan Balance", round(data["GT"]["Loan Balance"], 2), 717753.48)

    # --- 2. compute_monthly_windows vs the real May 2026 post's T12M clamp note ---
    windows = bravo.compute_monthly_windows(datetime(2026, 5, 1))
    all_ok &= check("May 2026 report: T12M current", windows["t12m_current"], ("2025-06-01", "2026-05-31"))
    all_ok &= check("May 2026 report: T12M prior clamped", windows["t12m_prior_clamped"], True)
    all_ok &= check("May 2026 report: T12M prior start clamps to Bravo floor",
                     windows["t12m_prior"][0], "2024-06-03")

    # --- 3. Header lines vs the real, verbatim 2026-07-03 post text ---
    windows_meta = bravo.compute_monthly_windows(datetime(2026, 6, 1))
    fake = data  # same fixture standing in for both current and prior (values don't matter for header-line checks)
    win = {"current": fake, "prior": fake}
    company_msg = formats.render_monthly_analytics_company(
        {"same_month": win, "ytd": win, "t12m": win},
        "June 2026", "June 2025",
        {"ytd": "Jan-Jun 2026 vs Jan-Jun 2025", "t12m": "Jul 2025-Jun 2026 vs Jul 2024-Jun 2025"},
    )
    all_ok &= check(
        "Title line matches real 2026-07-03 post",
        company_msg.splitlines()[0],
        ":bar_chart: _Monthly Analytics - June 2026 | Company-Wide — Retail vs Scrap channel split_",
    )
    all_ok &= check(
        "Source line matches real 2026-07-03 post",
        company_msg.splitlines()[1],
        "_Source: Bravo Company Performance (KPI) report, all 6 windows | matches Bravo to the penny_",
    )
    all_ok &= check("VIEW 1 line matches real post", "_VIEW 1 - Same Month: June 2026 vs June 2025_" in company_msg, True)
    all_ok &= check("VIEW 2 line matches real post", "_VIEW 2 - YTD: Jan-Jun 2026 vs Jan-Jun 2025_" in company_msg, True)
    all_ok &= check("VIEW 3 line matches real post", "_VIEW 3 - T12M: Jul 2025-Jun 2026 vs Jul 2024-Jun 2025_" in company_msg, True)

    if all_ok:
        print("\nALL PASS — company-kpis extraction verified against real Bravo data two independent ways; "
              "window math + header lines verified against the real May/June 2026 posts.")
        return 0
    print("\nFAIL — see above.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
