# Monthly Analytics Prestage — 2026-07

**Status:** FAILED — 0/30 (blocked, not a data problem)

## Root cause
Every trigger (initial + 1 retry, same-month-current window) came back `status: aborted` with all 5 stores skipped: `Skipped by safety rail: bravo-not-ready (could not reach a logged-in dashboard)`. This is the pipeline's own safety rail firing consistently — it is not a Bravo data issue, a report-config issue, or a per-store issue. Bravo POS in the Parallels VM is not in a logged-in state and the automated AHK login path did not recover it.

Root-cause is systemic across all 5 stores, so it will block every one of the 6 windows identically. Rather than burn the full 90-minute budget re-running 5 more windows against the same blocker, I stopped after confirming the failure was not transient (2 consecutive identical aborts, ~5 min apart) so the watchdog/next session has time to react.

## What I could not do
- Log Bravo back into a dashboard myself: this normally requires the `bravo-store-cycle` skill (computer-use driving the Parallels VM UI), but `request_access` for Parallels Desktop is explicitly blocked during scheduled/non-interactive runs ("can't be approved during a scheduled run... send a message in this conversation, or add the app to the scheduled task's settings").
- Touch `EndOfMonth.ahk` / `bravo_watcher.ahk` / the login handler myself — out of scope per this task's additive-only rule.

## Windows attempted
| Window | Range | Result |
|---|---|---|
| same-month-current | 2026-07-01..2026-07-31 | ABORTED (bravo-not-ready), retried once, ABORTED again |
| same-month-prior | 2025-07-01..2025-07-31 | NOT ATTEMPTED (root cause confirmed systemic, skipped to preserve budget) |
| ytd-current | 2026-01-01..2026-07-31 | NOT ATTEMPTED |
| ytd-prior | 2025-01-01..2025-07-31 | NOT ATTEMPTED |
| t12m-current | 2025-08-01..2026-07-31 | NOT ATTEMPTED |
| t12m-prior | 2024-08-01..2025-07-31 | NOT ATTEMPTED (no clamp needed — start is after the 2024-06-03 Bravo floor) |

## Sidecar
`/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/monthly-analytics/2026-07/` — folder created, empty (0 of 30 files copied).

## What the next session needs to do
1. Get a human to open Parallels Desktop / Bravo POS and confirm at least one store shows a logged-in Dashboard (or run `bravo-store-cycle` interactively — it cannot run headless from a scheduled task).
2. Once Bravo is confirmed reachable, re-run this prestage task manually, or let `monthly-analytics-watchdog` (7 AM) and `monthly-analytics-report` (3 AM) handle it — both should surface the same 0/30 gap.
3. If `bravo-not-ready` recurs even with a visibly logged-in dashboard, the safety-rail's detection logic itself may need review (see `BRAVO_KNOWN_ISSUES.md` for other recent Ok-click/dialog-verification issues in this pipeline — unrelated but same codebase).

_Generated 2026-08-01 00:20 ET (run started 2026-07-31 20:10 ET)._
