# Monthly Analytics Watchdog — July 2026

**Run:** 2026-08-01, 7 AM check
**Result:** Post NOT found in #company-performance. DM sent to Joshua (D03BHQH5VGT).

## Diagnostics
- **Pre-stage status:** FAILED — 0/30. Every trigger (initial + 1 retry) came back `status: aborted`, all 5 stores skipped with `Skipped by safety rail: bravo-not-ready (could not reach a logged-in dashboard)`. Confirmed systemic (2 consecutive identical aborts ~5 min apart), not transient. Prestage stopped early to preserve budget/give watchdog time to react.
- **Sidecar CSVs:** 0/30 present in output/monthly-analytics/2026-07/ (folder created, empty).
- **Main task working file:** found. monthly-analytics-report ran at 3 AM, detected 0/30 sidecar files (>4-missing threshold), halted before Sheet creation or Slack posting. Exited silently per policy (watchdog is the notification path).
- **Stuck triggers in claimed/:** none found.

## Root cause
Bravo POS in the Parallels VM was not in a logged-in state; the automated AHK login path did not recover it. This blocks prestage identically across all 5 stores/6 windows, so it is a pipeline-availability problem, not a data or per-store issue.

## Recovery path
1. A human needs to open Parallels Desktop / Bravo POS and confirm at least one store shows a logged-in Dashboard (request_access for Parallels is blocked during scheduled/non-interactive runs), or run bravo-store-cycle interactively.
2. Once Bravo is reachable, re-run monthly-analytics-prestage for 2026-07 manually.
3. Then re-run monthly-analytics-report — with 30/30 sidecar files present it completes in ~1 minute.
4. If bravo-not-ready recurs with a visibly logged-in dashboard, the safety-rail detection logic itself may need review (see BRAVO_KNOWN_ISSUES.md).
