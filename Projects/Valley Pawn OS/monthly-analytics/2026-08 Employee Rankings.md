# Employee Sales Rankings — August 2026 (FINAL) — catch-up 2026-09-05

**Source:** pipeline cell `employee-activity-range` (new 2026-09-05), triggers
`monthly-emp-rankings-2026-08-2026-09-05T14-42-59` (HAR/LEX/ROA/WAY success; CUL preview timeout at 30 s)
+ `...T14-52-00-retry-1` (CUL success after the handler's preview budget was raised to 120 s and the watcher restarted 14:51, PID 3028).
All 5 CSVs: `output/2026-08-31_{STORE}_employee-activity-range.csv`, Reporting Dates 8/1/2026 - 8/31/2026.
**Metric:** Retail Sales Excluding Fees (same as the weekly MTD board). Preston Peters + SYSTEM excluded; zero-sales logins omitted.

| # | Employee | Stores | Aug 2026 |
|---|---|---|---|
| 1 | Free1 Valley Pawn | CUL+HAR+LEX+ROA+WAY | $66,160.08 |
| 2 | Walker Tapley | HAR | $28,179.30 |
| 3 | Chadd Mcclintic | WAY | $23,611.31 |
| 4 | Martin Dowden | CUL+LEX+ROA+WAY | $22,880.95 |
| 5 | Benjie Moore | ROA | $21,828.11 |
| 6 | Uriah Tiglao | LEX | $17,569.63 |
| 7 | Bridgett Grayson | CUL | $16,030.72 |
| 8 | Michael Chambers | HAR | $15,610.78 |
| 9 | Robert Swagger | CUL | $13,565.14 |
| 10 | Sandra Cole | CUL | $12,605.17 |
| 11 | Joseph Epperly | ROA | $8,755.05 |
| 12 | Andrew Clark | HAR | $1,469.98 |
| 13 | Davon Camber | HAR | $1,150.00 |
| 14 | Cris Lopez | ROA | $1,044.93 |
| 15 | Steve Burch | LEX | $599.99 |
| 16 | Chonn Grinnage | LEX | $399.99 |
| 17 | Lee Cornelison | WAY | $274.41 |

Store totals (Total Store row): CUL $63,889 · HAR $63,012 · ROA $49,812 · WAY $47,562 · LEX $31,902 → Company $256,177.92.
Cross-check: every figure ≥ the 8/31 08:14 MTD board (which ran on data through ~8/27) and the same 17 names in the same order — consistent.

**Slack:** posting to #employee-performance from this session was blocked by the permission classifier; a DRAFT was created in #employee-performance (draft Dr0BV6NSAJ1L) for Joshua to send. The rebuilt `monthly-employee-sales-rankings` task has a duplicate guard ("FINAL" + "August 2026") so a guardian rerun will not double-post once the draft is sent.

## Scheduled run 2026-09-05 16:34 ET (monthly-employee-sales-rankings, rebuilt task — first run)
- Duplicate guard HIT: FINAL August 2026 post already live in #employee-performance (Joshua sent the draft 16:30:46 EDT). No Slack post made, no new trigger dropped (no Bravo touch).
- Permanent workbook created (folder was missing): `Employee Sales Rankings/Employee_Sales_Rankings_August_2026.xlsx` — built from the same 5 fresh CSVs (`2026-08-31_{CUL,HAR,LEX,ROA,WAY}_employee-activity-range.csv`, mtime 14:46–14:53, Reporting Dates 8/1/2026 - 8/31/2026). Re-parse reproduced the live post exactly: 17 employees, company $256,177.92, identical order.
- Outcome: August 2026 cycle CLOSED — post live, workbook saved, working file current.
