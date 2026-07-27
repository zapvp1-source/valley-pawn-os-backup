# Jewelry Redemption Analysis - STATUS

## Answer to Joshua's question (2026-07-16)
Yes, Bravo can produce category-level redemption rates via the built-in Pawn Activity Summary report, per-store, date-range configurable. Bypasses the blocked Loan Portfolio 2026 project (still broken as of 2026-07-16).

## Deliverable
Valley_Pawn_Jewelry_Redemption_Analysis.xlsx (this folder). Jewelry redemption = 70.05 percent company-wide; all-departments = 70.3 percent. ROA (64.1%) and CUL (63.4%) lag LEX (79.1%), WAY (77.6%), HAR (75.3%) on jewelry. Rings (68.4%, largest volume) set the jewelry floor; Charms (84.2%) and Chains (78.3%) redeem best.

Industry benchmark: NPA cites 80-85 percent national average; EZCORP targets 70-80 percent, actuals 84-86 percent. Valley Pawn's 70.3 percent trails benchmark company-wide, not just jewelry. Firearms (72.6%), Video Games (72.7%), Musical Instruments (73.3%) redeem best; Tools (60.5%), Sporting Goods (58.6%) redeem worst.

## Pipeline fix
PawnActivitySummary.ahk never ran in production before this - hung on the Continuous Scrolling bug. Fixed by porting the toggle-off block from SafeRegisterJournal.ahk. Verified across all 5 stores. Backup: PawnActivitySummary.ahk.bak-pre-cs-toggle-fix-2026-07-16.

## Follow-up investigation (2026-07-17): why the gap
Checked 75-Days-Past-Due percent of loan balance (loans-75-days-past-due pull 2026-07-13, Ending Loan Base from EOM 2026-07-16):
CUL 0.0pct, HAR 4.7pct, LEX 2.8pct, ROA 4.4pct, WAY 0.8pct.

Finding: does not cleanly explain the gap. HAR is near the 5pct threshold AND redeems well (75.3pct). ROA is near threshold AND redeems poorly (64.1pct) - consistent. CUL is at ZERO past-due AND is the weakest redeemer (63.4pct) - contradicts a simple collections story. CUL's 0.0pct needs verification: could be genuine discipline, or an aggressive same-day-expiration policy that cuts the redemption window short.

True underwriting/LTV data is BLOCKED - fpd-cohort pipeline output is stale (2026-05-18) and inconsistent across stores. Needs either the Loan Portfolio 2026 column-layout fix or a live Bravo session to get real FPD/LTV data. Not done this session.