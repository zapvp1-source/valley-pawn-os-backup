---
name: vp-content-batch-quota-watchdog
description: Tuesday 10 AM ET — verifies the daily-cadence targets directly against live Publer data (not just the manifest): Brand FB/IG/X each 7/week, each store's FB+GBP each 7/week. DMs Joshua only on a sustained (2-week) per-account shortfall. Redesigned 2026-08-04 alongside vp-content-batch-weekly's routing redesign.
model: claude-sonnet-5
---

# vp-content-batch-quota-watchdog

> **LOCAL ACCESS GATE.** Runs on Joshua's Mac Studio via `mcp__Control_your_Mac__osascript` (may be deferred — `ToolSearch` query `select:mcp__Control_your_Mac__osascript` if needed, probe with `do shell script "echo READY"`, retry ~20s up to 12 min before concluding unavailable).
>
> **HARDENED 2026-08-21 — DO NOT use folder mounts.** A run stalled waiting on `request_cowork_directory` approval that never came (Joshua isn't present during scheduled runs). ALL file access in this task goes through osascript shell. Never call `request_cowork_directory`. Never rebuild the job logic inline — it lives in the script below.

⚠️ **FAILURE ALERT POLICY:** On failure, DM Joshua once (channel D03BHQH5VGT): `⚠️ Scheduled task "vp-content-batch-quota-watchdog" did not complete — <date>.` Nothing technical. Never post to any team channel.

Automated, unattended run. End with `<run-summary>...</run-summary>`.

## Why this exists / what changed

Originally an aggregate weekly item-count check; redesigned 2026-08-04 to per-account checks against live Publer data after Joshua gave exact per-platform targets (one post/day per store page, GBP consistently, Brand FB/IG/X 7/week each) — an aggregate count can look fine while individual accounts starve. **2026-08-21:** all job logic (window, pagination, from/to params, dedupe, per-account grouping, flagging, history comparison, result-file write) was moved into a hardened, committed script so every run executes one tested path instead of re-improvising it.

## Job

1. Probe local access (`do shell script "echo READY"`).
2. Run the watchdog script:
   ```
   do shell script "cd /Users/joshuadavis/Documents/Claude/Projects/'Refine Social Media' && /usr/bin/python3 quota_watchdog.py 2>/dev/null"
   ```
   The script does everything: trailing-7-day window, GET /posts for scheduled+published with explicit from/to (never omitted — endpoint silently caps ~15 without it) and pagination, dedupe by (post id, account id), per-account counts vs targets (13 accounts: Brand/BrandIG/BrandTwitter + 5 store FB + 5 GBP, all 7/week), flags accounts under 4/week, compares to the most recent prior `quota_watchdog_result.json`, and writes this week's full result to `Valley Pawn Studios/output/{today}/quota_watchdog_result.json`. It prints the result JSON to stdout.
3. Parse the printed JSON. Decision rule, unchanged:
   - `two_week_shortfalls` empty → stay silent. Note in run-summary only.
   - `two_week_shortfalls` non-empty → DM Joshua (D03BHQH5VGT), one message listing every qualifying account, short and plain:
     ```
     📊 A few social accounts have been running light 2 weeks running: {account} {this_week}/7, {last_week}/7. Worth a look when you have a minute.
     ```
   - `prior_run_date` null (first run / no history) → silent, run-summary only.
4. If the script exits non-zero (stderr has `WATCHDOG-FAIL:`), retry ONCE after 60s. If it fails again, follow the failure alert policy. Do NOT attempt to debug or rewrite the script mid-run — log the stderr in the run-summary; fixing the script is an interactive-session job.
5. Read-only toward the batch: never touch, re-run, or fix `vp-content-batch-weekly`. One short clause naming a likely cause in the DM is fine; self-healing is `vp-content-batch-postflight`'s job.

## Hard rule

Silent unless a specific account has a genuine 2-week-running shortfall. DM only, never a team channel.

## Script location (fix here, not inline)

`/Users/joshuadavis/Documents/Claude/Projects/Refine Social Media/quota_watchdog.py` — self-contained, uses `publer_client.py` + `publer_accounts.json` beside it. If the script needs a change, change the script (it's the single source of truth), not this prompt.

<!-- 2026-08-04: rewritten from aggregate item-count to per-account check. -->
<!-- 2026-08-21: hardened — logic moved to committed quota_watchdog.py; osascript-only file access; no folder mounts; retry-once-then-alert on script failure. First history file written 2026-08-21 (backfill run after the 8/18 run stalled on a mount request). -->
