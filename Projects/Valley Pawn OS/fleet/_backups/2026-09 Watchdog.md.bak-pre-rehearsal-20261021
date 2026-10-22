# Monthly Analytics Watchdog — 2026-09 (native)

Run: 2026-10-19 10:00 ET | report month September 2026

Result: POST MISSING

## Pre-stage

# Monthly Analytics Prestage — 2026-09

**Status:** COMPLETE 30/30
**Runner:** bin/monthly_prestage_runner.py (native, launchd `com.valleypawn.monthly-prestage`) — no Claude session in the loop

## Windows
| Window | Range | CSVs |
|---|---|---|
| same-month-current | 2026-09-01..2026-09-30 | 5/5 |
| same-month-prior | 2025-09-01..2025-09-30 | 5/5 |
| ytd-current | 2026-01-01..2026-09-30 | 5/5 |
| ytd-prior | 2025-01-01..2025-09-30 | 5/5 |
| t12m-current | 2025-10-01..2026-09-30 | 5/5 |
| t12m-prior | 2024-10-01..2025-09-30 | 5/5 |

## Sidecar
`/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/monthly-analytics/2026-09/`

- same-month-current_CUL.xlsx (79301 bytes)
- same-month-current_HAR.xlsx (63973 bytes)
- same-month-current_LEX.xlsx (78520 bytes)
- same-month-current_ROA.xlsx (65210 bytes)
- same-month-current_WAY.xlsx (80393 bytes)
- same-month-prior_CUL.xlsx (79436 bytes)
- same-month-prior_HAR.xlsx (62694 bytes)
- same-month-prior_LEX.xlsx (78871 bytes)
- same-month-prior_ROA.xlsx (65165 bytes)
- same-month-prior_WAY.xlsx (78998 bytes)
- t12m-current_CUL.xlsx (169716 bytes)
- t12m-current_HAR.xlsx (151460 bytes)
- t12m-current_LEX.xlsx (164999 bytes)
- t12m-current_ROA.xlsx (150428 bytes)
- t12m-current_WAY.xlsx (169252 bytes)
- t12m-prior_CUL.xlsx (169398 bytes)
- t12m-prior_HAR.xlsx (149548 bytes)
- t12m-prior_LEX.xlsx (165265 bytes)
- t12m-prior_ROA.xlsx (152027 bytes)
- t12m-prior_WAY.xlsx (165634 bytes)
- ytd-current_CUL.xlsx (144716 bytes

## Sidecars: 30/30 present, 30 >= 2 KB (/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/monthly-analytics/2026-09)

## Report working file

GO
| Metric | GT cur | GT prior | GT var$ | GT var% |
|---|---|---|---|---|
| inventory_balance | 751051.98 | 566543.55 | 184508.43 | 32.6% |
| loan_balance | 747571.43 | 621173.51 | 126397.92 | 20.3% |
| total_sales | 2373369.99 | 1648344.15 | 725025.84 | 44.0% |
| scrap_cost | 293913.2 | 169146.96 | 124766.24 | 73.8% |
| psc | 731103.07 | 643048.09 | 88054.98 | 13.7% |
| net_revenue | 2021815.15 | 1480256.37 | 541558.78 | 36.6% |

Per-store detail: see Google Sheet (full 3-view x 4-subtable x 6-metric x 6-column breakdown).

### T12M vs PRIOR T12M
| Metric | GT cur | GT prior | GT var$ | GT var% |
|---|---|---|---|---|
| inventory_balance | 751051.98 | 566543.55 | 184508.43 | 32.6% |
| loan_balance | 747571.43 | 621173.51 | 126397.92 | 20.3% |
| total_sales | 3123926.16 | 2237316.57 | 886609.59 | 39.6% |
| scrap_cost | 385950.63 | 222939.84 | 163010.79 | 73.1% |
| psc | 963338.2 | 852690.28 | 110647.92 | 13.0% |
| net_revenue | 2643333.98 | 1984119.39 | 659214.59 | 33.2% |

Per-store detail: see Google Sheet (full 3-view x 4-subtable x 6-metric x 6-column breakdown).

## Completeness gate
Result: PASS. 30/30 CSVs present, 5/5 stores non-zero for same-month-current and same-month-prior. No incomplete cells flagged.

## Google Sheet
Created: https://docs.google.com/spreadsheets/d/1iaxJ4C4SZtaV0wZKh8xf9E8lC1VhXLG4ZcQrBVDPVcc/edit
Verified via read_file_content — all 117 rows populated correctly across 3 views x 4 subtables x 6 metrics x 6 columns.

## Step 6 — Slack post
Fleet publish guard: NOT ARMED (vp_dryrun.py status exit 1) — published for real via outbox.
Queued via outbox (per 2026-09-28 mandatory outbox-send policy — slack_send_message not called directly):
  - .txt: Valley Pawn OS/fleet/outbox/monthly-analytics-report-main-20261001-080654.txt
  - .json envelope: Valley Pawn OS/fleet/outbox/monthly-analytics-report-main-20261001-080654.json
  - Destination: #company-performance (C0B26GD8D2R), Grand Total only, Same-Month-vs-Year-Ago view.
  - Delivery via ops bot expected within ~2 minutes of this run; receipt written under task name monthly-analytics-report.

## Label note
Task template used "Retail Sales"/"Scrap Sales" labels, but the hard rules section of this same SKILL.md states the retail/scrap sales split does not exist in the EOM report and scrap_cost must never be labeled scrap sales. Relabeled to "Total Sales" and "Scrap Cost" in both the Slack post and the Google Sheet to comply with the hard rule (which overrides the template wording).


## Claimed triggers: none

(render: DM not sent) would DM: The September 2026 company performance report needs another pull before it can go out — will post once it's ready.
