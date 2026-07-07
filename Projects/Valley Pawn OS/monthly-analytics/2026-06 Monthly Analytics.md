# 2026-06 Monthly Analytics — WORKING FILE (INCOMPLETE / FAILED PRESTAGE)

**Run:** 2026-07-01 03:00 (scheduled)
**Report month:** June 2026
**Status:** ❌ ABORTED — pre-stage CSVs missing. Silent-on-failure policy invoked. No Slack posts. No DM. (7 AM watchdog is the only notification path.)

## Date windows (June 2026)
| Window key | Start | End |
|---|---|---|
| same-month-current | 2026-06-01 | 2026-06-30 |
| same-month-prior | 2025-06-01 | 2025-06-30 |
| ytd-current | 2026-01-01 | 2026-06-30 |
| ytd-prior | 2025-01-01 | 2025-06-30 |
| t12m-current | 2025-07-01 | 2026-06-30 |
| t12m-prior | 2024-07-01 | 2025-06-30 |

## Inventory result (Step 2)
Folder: /Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/monthly-analytics/2026-06/
- Folder EXISTS (created 2026-06-30 20:10) but is EMPTY.
- CSVs found: 0 of 30 expected (5 stores × 6 windows).
- Missing: 30 of 30 → exceeds the 4-of-30 tolerance → ABORT.

Likely cause: `monthly-analytics-prestage` (night-of-2026-06-30) did not stage any sidecar CSVs. The empty window folder was created but no per-store CSVs were written.

## Steps not run
- Step 3 (parse_eom.py): skipped — no input CSVs.
- Step 4 (YoY): skipped — no data.
- Step 5 (Google Sheet): skipped — no data.
- Step 6 (Slack posts): NOT POSTED — success gate not met (0 of 30 CSVs; requires ≥26).

## Post status
- #company-performance: NOT POSTED
- #store-performance: NOT POSTED

## Watchdog note
No success post landed. The `monthly-analytics-watchdog` (07:00 on the 1st) will detect the missing post and DM Joshua. Recommend investigating `monthly-analytics-prestage`'s 2026-06-30 run.

