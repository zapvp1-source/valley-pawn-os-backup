# Monthly Analytics Prestage — 2026-10

**Status:** COMPLETE 30/30
**Runner:** bin/monthly_prestage_runner.py (native, launchd `com.valleypawn.monthly-prestage`) — no Claude session in the loop

## Windows
| Window | Range | CSVs |
|---|---|---|
| same-month-current | 2026-10-01..2026-10-31 | 5/5 |
| same-month-prior | 2025-10-01..2025-10-31 | 5/5 |
| ytd-current | 2026-01-01..2026-10-31 | 5/5 |
| ytd-prior | 2025-01-01..2025-10-31 | 5/5 |
| t12m-current | 2025-11-01..2026-10-31 | 5/5 |
| t12m-prior | 2024-11-01..2025-10-31 | 5/5 |

## Sidecar
`/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/monthly-analytics/2026-10/`

- same-month-current_CUL.xlsx (79708 bytes)
- same-month-current_HAR.xlsx (62752 bytes)
- same-month-current_LEX.xlsx (78723 bytes)
- same-month-current_ROA.xlsx (65743 bytes)
- same-month-current_WAY.xlsx (79655 bytes)
- same-month-prior_CUL.xlsx (80006 bytes)
- same-month-prior_HAR.xlsx (63057 bytes)
- same-month-prior_LEX.xlsx (79062 bytes)
- same-month-prior_ROA.xlsx (65470 bytes)
- same-month-prior_WAY.xlsx (79216 bytes)
- t12m-current_CUL.xlsx (169806 bytes)
- t12m-current_HAR.xlsx (150035 bytes)
- t12m-current_LEX.xlsx (164895 bytes)
- t12m-current_ROA.xlsx (150734 bytes)
- t12m-current_WAY.xlsx (167841 bytes)
- t12m-prior_CUL.xlsx (169495 bytes)
- t12m-prior_HAR.xlsx (149571 bytes)
- t12m-prior_LEX.xlsx (165269 bytes)
- t12m-prior_ROA.xlsx (152011 bytes)
- t12m-prior_WAY.xlsx (165711 bytes)
- ytd-current_CUL.xlsx (152275 bytes)
- ytd-current_HAR.xlsx (132721 bytes)
- ytd-current_LEX.xlsx (148278 bytes)
- ytd-current_ROA.xlsx (133629 bytes)
- ytd-current_WAY.xlsx (150207 bytes)
- ytd-prior_CUL.xlsx (151858 bytes)
- ytd-prior_HAR.xlsx (133611 bytes)
- ytd-prior_LEX.xlsx (148504 bytes)
- ytd-prior_ROA.xlsx (134884 bytes)
- ytd-prior_WAY.xlsx (148727 bytes)

## Notes
Native runner's own orchestrator logged `status: PARTIAL 20/30` at 21:37:07 ET on 2026-10-31 because it timed out (15-min window) waiting on the t12m-current and t12m-prior Bravo exports before they actually finished — the underlying exports succeeded moments to ~10 minutes after the runner gave up (confirmed via each window's `result.json`: all cells `status: "success"`), it just never reached the copy-to-sidecar step for those two windows before exiting. Per the runner's own stated design ("copy source = each cell's `output_path` from its result.json — authoritative, never guessed from the date"), a fleet-guardian pass on 2026-11-01 (the 21:45 ET run, delayed in wall-clock by DST rollover) verified the raw Bravo export files still on disk at their `output_path` locations matched the result.json file sizes exactly (e.g. CUL t12m-current 169806 bytes == CSV-size-check log line), confirmed no later-running window shared or re-wrote those same end-date raw filenames afterward (t12m-current and t12m-prior ran last, in that order, each with a distinct raw-filename end-date not reused again), and copied the 10 missing files to the window-tagged sidecar names using the exact same mapping the runner itself uses. **No Bravo/Parallels automation was run or re-triggered to do this — the Bravo exports already existed; this was a plain file copy on data already on disk**, consistent with the Hard Limit against driving the Bravo VM. `--dry-run` against the real runner was attempted first for comparison but is unusable from a cloud/device-bridge session: the script's `HOME`-relative paths resolve to the session's own sandbox home, not `/Users/joshuadavis`, so it reported `0/5` everywhere and would have dropped fresh duplicate triggers for all 6 windows if run for real — do not invoke `monthly_prestage_runner.py` directly from a Cowork device-bridge session; it must run natively via launchd or be invoked through the Host Job Queue instead.

_Generated 2026-11-01 01:55 ET (fleet-guardian 21:45 pass, file-recovery only)._
