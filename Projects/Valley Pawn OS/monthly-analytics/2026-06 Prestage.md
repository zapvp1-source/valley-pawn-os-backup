# Monthly Analytics Prestage — 2026-06

**Status:** FAILED 0/30

## Windows
| Window | Range | CSVs |
|---|---|---|
| same-month-current | 2026-06-01..2026-06-30 | 0/5 |
| same-month-prior   | 2025-06-01..2025-06-30 | 0/5 |
| ytd-current        | 2026-01-01..2026-06-30 | 0/5 |
| ytd-prior          | 2025-01-01..2025-06-30 | 0/5 |
| t12m-current       | 2025-07-01..2026-06-30 | 0/5 |
| t12m-prior         | 2024-07-01..2025-06-30 | 0/5  (no clamp; start 2024-07-01 is after the Bravo floor 2024-06-03) |

## Sidecar
`/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/monthly-analytics/2026-06/`
Empty — 0 files staged.

## Notes
- Last-day gate PASSed (tomorrow = 2026-07-01).
- Window 1 (same-month-current) trigger dropped 20:10 ET, processed 20:13:49 → status=`aborted`, all 5 stores skipped by the safety rail: `bravo-not-ready (could not reach a logged-in dashboard)`.
- Root cause: Bravo POS was HUNG (Not Responding) inside the Windows 11 VM.
- Ran `bravo_ensure_healthy.sh CUL` (non-computer-use, prlctl-exec self-heal path). The health gate escalated through its full ladder: force-kill Bravo.exe → relaunch Bravo+watcher → nudge/un-minimize → consolidate watcher → 2 gentle recover-to-dashboard attempts (both `FAIL no-window`) → ESCALATE force-kill+relaunch → 2 more recover attempts (both `FAIL no-window`). Final result: `FAIL no-dashboard` at 20:29:54.
- Bravo will not render a dashboard window even after a hard relaunch. Requires manual intervention (health gate exit code 1 = needs Joshua).
- Autonomous computer-use login was not possible: `request_access` for Parallels Desktop timed out at 180s (unattended 8 PM run, no approver present).
- Remaining 5 windows were NOT triggered — they would abort identically on `bravo-not-ready`; stopped to preserve the time budget.
- ADDITIVE: no production files modified (EndOfMonth.ahk, watcher dispatch, saved Bravo reports untouched). Only the net-new window-1 trigger/result plus the health-gate self-heal running its normal course.
- Downstream: `monthly-analytics-report` (3 AM) will find no staged CSVs; `monthly-analytics-watchdog` (7 AM) will surface the gap.

_Generated 2026-06-30 20:30 ET._
