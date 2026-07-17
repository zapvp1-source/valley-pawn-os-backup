# Jewelry Redemption Analysis - STATUS

## Answer to Joshua's question (2026-07-16)
Yes, Bravo can produce category-level redemption rates - via the built-in Pawn Activity Summary report (Loan Reports category), per-store, date-range configurable. No custom report needed. This bypasses the blocked Optimize Loan Portfolio / Loan Portfolio 2026 project (still broken as of 2026-07-16, unrelated column-layout defect in that saved Ad Hoc report - do not duplicate effort there for this question).

## Deliverable
Valley_Pawn_Jewelry_Redemption_Analysis.xlsx (this folder) - all 5 stores, trailing 12mo (7/16/2025-7/15/2026), pulled from Bravo Pawn Activity Summary.

Headline: Jewelry/gold redemption rate = 70.05 percent company-wide, vs 70.26 percent all-departments company-wide. Jewelry is NOT an outlier - tracks the company average almost exactly. This corrects an earlier partial finding from Loan Portfolio 2026 (based on only 10 tickets) that had flagged Gold/Jewelry as a severe underperformer.

Store spread: ROA (64.1 percent) and CUL (63.4 percent) run well below LEX (79.1 percent), WAY (77.6 percent), HAR (75.3 percent) on jewelry redemption specifically.

Rings dominate jewelry volume (1,692 of 3,609 resolved jewelry tickets) and sit at 68.4 percent - near the company floor - so Rings performance effectively sets the overall jewelry rate. Charms (84.2 percent) and Chains (78.3 percent) redeem best.

## Pipeline infrastructure fix (durable, reusable)
PawnActivitySummary.ahk (in Bravo Data Extraction/reports/) had never successfully run in production - it hung on the known Continuous Scrolling render bug (resets ON every Bravo restart, freezes WPF preview 3+ min on wide reports). Fixed by porting the toggle-off block from SafeRegisterJournal.ahk / DepositsAndPaidOuts.ahk. Verified working across all 5 stores on this pull. Backup of pre-fix version: PawnActivitySummary.ahk.bak-pre-cs-toggle-fix-2026-07-16.

This report can now be re-pulled on demand (or scheduled) for any date range, any store, without further fixes.

## Raw data
Output CSVs (12mo, pulled 2026-07-16) live in Bravo Data Extraction/output/: 2026-07-15_CUL_pawn-activity-summary.csv, _HAR_, _LEX_, _ROA_, _WAY_