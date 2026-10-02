# September 2026 Employee Sales Rankings — Working File

**Run:** monthly-employee-sales-rankings, 2026-10-01 (02:12–02:19 ET)
**Trigger ID:** monthly-emp-rankings-2026-09-2026-10-01T06-12-13 — status: success, all 5 cells succeeded
**Metric:** Retail Sales Excluding Fees (same column as the weekly MTD board)
**Fleet publish guard:** OFF (publications live) — confirmed before posting

## Per-store file freshness
| Store | File | Row count | Date range confirmed |
|---|---|---|---|
| CUL | 2026-09-30_CUL_employee-activity-range.csv | 14 | 9/1/2026 - 9/30/2026 |
| HAR | 2026-09-30_HAR_employee-activity-range.csv | 16 | 9/1/2026 - 9/30/2026 |
| LEX | 2026-09-30_LEX_employee-activity-range.csv | 13 | 9/1/2026 - 9/30/2026 |
| ROA | 2026-09-30_ROA_employee-activity-range.csv | 13 | 9/1/2026 - 9/30/2026 |
| WAY | 2026-09-30_WAY_employee-activity-range.csv | 14 | 9/1/2026 - 9/30/2026 |

All 5 generated after the trigger's requested_at (2026-10-01T06:12:13Z) — fresh pull, not reused from an earlier partial-month file. Rule 18 gate passed (all 5 present, fresh, parsed with ≥1 row each).

Preston Peters excluded per hard rule (appeared as "PMONEY - PRESTON PETERS" in each store's raw CSV; $20.00 CUL / $944.61 HAR / $21.23 LEX / $0.00 ROA / $9,543.61 WAY — all stripped before consolidation).

## Duplicate guard
Read last 20 messages in #employee-performance (C0ATTLPQHR8) before posting — no existing "FINAL" + "September 2026" post found. Most recent related post was the 9/21 MTD board (VP OPS ENGINE bot). Proceeded to post.

## Ranked table (Retail Sales Excluding Fees, Preston Peters excluded)

| Rank | Employee | Store(s) | Retail Sales Excluding Fees |
|---|---|---|---|
| 1 | Free1 Valley Pawn | CUL+HAR+LEX+ROA+WAY | $68,105.32 |
| 2 | Walker Tapley | HAR+WAY | $28,291.94 |
| 3 | Uriah Tiglao | LEX | $23,870.75 |
| 4 | Chadd Mcclintic | LEX+WAY | $21,171.26 |
| 5 | Benjie Moore | ROA | $21,160.38 |
| 6 | Martin Dowden | CUL+LEX+ROA+WAY | $16,993.59 |
| 7 | Robert Swagger | CUL | $13,217.24 |
| 8 | Joshua Burnett | CUL | $12,904.53 |
| 9 | Sandra Cole | CUL | $12,624.21 |
| 10 | Michael Chambers | HAR | $12,179.45 |
| 11 | Joseph Epperly | ROA | $8,289.97 |
| 12 | Bridgett Grayson | CUL | $5,104.98 |
| 13 | Camden Ahern | HAR | $3,213.77 |
| 14 | Andrew Clark | HAR+WAY | $2,949.65 |
| 15 | Nelson Troche | CUL | $1,259.99 |
| 16 | Jacob Cox | ROA | $690.21 |
| 17 | Cris Lopez | ROA | $679.98 |
| 18 | Davon Camber | HAR | $199.99 |
| 19 | Logan Dean | HAR | $52.24 |
| 20 | System System | CUL+HAR+LEX+ROA+WAY | $0.00 |
| 21 | Emma Langford | HAR | $0.00 |
| 22 | Nadiushka Rios Cardona | HAR | $0.00 |
| 23 | Chonn Grinnage | LEX | $0.00 |
| 24 | Steve Burch | LEX | $0.00 |
| 25 | Lottie Obst | WAY | $0.00 |
| 26 | Timothy Thompson | WAY | $0.00 |

**Company Total: $252,959.45**

## By store
- Culpeper: $70,093.11
- Harrisonburg: $56,309.86
- Roanoke: $43,322.51
- Waynesboro: $50,216.38
- Lexington: $33,017.59

## Slack post
- Main post: https://valleypawnworkspace.slack.com/archives/C0ATTLPQHR8/p1790835653218369
- Thread reply (by-store): https://valleypawnworkspace.slack.com/archives/C0ATTLPQHR8/p1790835659863969?thread_ts=1790835653.218369&cid=C0ATTLPQHR8

## Workbook
Saved: `Valley Pawn OS/Employee Sales Rankings/Employee_Sales_Rankings_September_2026.xlsx` (3 sheets: Sales Rankings, By Store, Summary). Did not overwrite the existing August file.

## Notes
- "System System" and six employees with $0.00 Retail Sales Excluding Fees are included because they appear as real rows in the Bravo source CSVs with no activity this period on this metric — consistent with Rule 18 (post only complete, accurate data as reported, don't invent exclusions beyond the documented Preston Peters rule).
- "Free1 Valley Pawn" (shared login) included per the task's explicit instruction.
