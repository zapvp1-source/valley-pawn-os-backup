# MobilePawn Participation

**Source:** Bravo End-of-Month report xlsx already pulled daily/monthly by the Bravo Data Extraction pipeline (`Bravo Data Extraction/output/YYYY-MM-DD_<STORE>_end-of-month.xlsx`). No Bravo UI needed.

**Run:** `python3 mobilepawn_participation.py > mobilepawn_participation_by_store_month.csv`

**Metrics (per store, per month)**
- `pct_pmts_mobile` = MobilePawn Loan Payments ÷ (MobilePawn Loan Payments + In-Store Renewals + Partial Payments + Extensions). Redemptions excluded (in-store only).
- `pct_dollars_mobile` = MobilePawn Interest+Fees+Misc ÷ (that + In-Store Interest+Fees+Misc).
- `mp_customers_active` = Bravo "Customers Active" in the MobilePawn Activity block.
- Only files whose Reporting Dates = single calendar month are used; latest file per month wins (partial = MTD).

**Known gaps:** Aug 2025 has no single-month EOM on file (only a 12-month range); Aug 2026 latest single-month file is thru 8/27.

Built 2026-09-29. Verified: CUL Sep MTD 227 app pmts vs 7+7+428 in-store = 33.9%, matches raw report.

## Monthly publication (2026-09-29)
- Channel: #mobilepawn-participation (C0C55HRGPBP), Analytics section.
- Task: `monthly-mobilepawn-participation` — 1st–3rd 9:15 AM, posts once (POSTED.txt in out/<YM>/).
- Formatter: `Valley Pawn OS/bin/mobilepawn_monthly.py <YYYY-MM> [out_dir]` → exit 0 post / exit 2 HOLD.txt. Also refreshes `mobilepawn_participation_by_store_month.csv` (full-month staged values replace partial daily ones).
