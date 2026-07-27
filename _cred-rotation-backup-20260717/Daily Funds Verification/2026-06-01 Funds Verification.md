# Daily Funds Verification — 2026-06-01

**Status:** Partial — Bravo UI unavailable (see notes)
**Run time:** 2026-06-01 ~21:30 ET
**Trigger ID:** daily-funds-verification-2026-06-01T21-30-00

## Results

| Store | Funds Sent (Slack) | Bravo Safe Verified | Status |
|-------|-------------------|---------------------|--------|
| CUL | $3,000 (2:45 PM) | Could not verify | ⚠️ |
| HAR | $2,000 (9:51 AM) | Could not verify | ⚠️ |
| LEX | — | — | ✅ No activity |
| ROA | — | — | ✅ No activity |
| WAY | $2,000 (12:11 PM) | Could not verify | ⚠️ |

## What Happened

### Root Cause
Bravo's UI was stuck in an unknown state (not on Dashboard) all day — both the 6 PM scheduled run and a manual 8:50 PM run failed with `EnsureStore failed` / `Lock Session not found`.

### Recovery Steps Taken
1. Identified failure pattern from logs: `BackToDashboard: hops exhausted`, `Lock Session click failed`
2. Killed stuck Bravo process (PID 11604) and two AHK watcher instances (PID 5828, 8912)
3. Successfully restarted AHK watcher via `_restart_watcher.ps1` — running from Y: path (PID 6940, Session 1) ✅
4. Attempted Bravo relaunch multiple ways (.appref-ms scheduled task, direct .exe) — all produced processes with no visible window (MainWindowHandle = 0)
5. The pipeline requires Bravo to show `VALLEY PAWN - [store]` in the window title (Dashboard state); this only exists after login

### Blocker
Bravo must be manually launched and logged into a store by Joshua. Once on any store Dashboard, the pipeline can run immediately.

### Action Taken
- Posted partial report to #daily-funds-reconcilation
- DM'd Joshua with exact steps needed

## Slack Evidence
- **CUL:** Joshua → Sandi: "Sent 3k" at 14:45 ET (request was "Ops cash needed $3000")
- **HAR:** Joshua → Andrew Clark: "Sent 2k" at 09:51 ET (request was "Ops cash need 2k")
- **WAY:** Joshua → Preston Peters: "Sent 2k" at 12:11 ET (request was "Ops cash, need 2k")
- **LEX:** No messages today
- **ROA:** No messages today
