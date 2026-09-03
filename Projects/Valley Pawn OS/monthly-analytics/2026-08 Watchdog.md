# Monthly Analytics Watchdog — August 2026 (report month)

**Run:** 2026-09-01, ~7:08 AM ET (monthly-analytics-watchdog scheduled task)
**Result:** Post NOT found in #company-performance (C0B26GD8D2R) as of run time. Diagnostics gathered below. One plain-language DM sent to Joshua per vp-operating-rules Rule 16/18 (no technical content on Slack).

## Step 2 — Channel scan
Read #company-performance from today-midnight-ET (unix 1788235200) forward, limit 10. Zero messages returned — no monthly analytics post today, at all.

## Step 3 — Diagnostics

**1. Pre-stage status file** (`2026-08 Prestage.md`): MISSING — does not exist. `monthly-analytics-prestage` did not write its own status file this run.

**2. Sidecar inventory** (`Bravo Data Extraction/output/monthly-analytics/2026-08/`): folder exists (created Aug 31 20:10) but is EMPTY. 0/30 expected CSVs present (0 files ≥ 2 KB).

**3. Main task working file** (`2026-08 Monthly Analytics.md`): FOUND. Summary of its contents:
- Result: HALTED before Sheet/Slack — sidecar 0/30 present. Exited silently per its own policy, deferring notification to this watchdog.
- Root cause identified by that run (NOT a Bravo login/pipeline-offline problem): all 6 date-window triggers (same-month-current through t12m-prior) actually completed successfully — all 5 stores, all 6 windows, between 8:11–9:05 PM ET on 8/31. The raw per-store EndOfMonth exports did land on disk.
- The break is in `monthly-analytics-prestage`'s window-tagged sidecar-copy step — the step that's supposed to copy each window's export to a window-tagged filename before the next window overwrites it. That copy step did not run (or failed silently) — none of the 6 trigger logs show any copy activity.
- Consequence: same-month-current, ytd-current, and t12m-current all end 2026-08-31 and share the same raw output filename per store; they ran sequentially and each later window overwrote the earlier one before any copy happened. Only t12m-current's totals survive per store. Mirror situation for the three -08-31(2025) windows — only t12m-prior survives. 4 of 6 windows' period-specific figures are gone, not just uncopied.
- Because the data can't be reconstructed, the run correctly did not attempt a partial post (matches Rule 18 — withhold, don't caveat).

**4. Stuck triggers in `Bravo Data Extraction/triggers/claimed/`:** none found matching "monthly-analytics" — the watcher did not hang mid-run; this is a data-handling bug in the copy step, not a stuck process.

## Likely cause (for the record — internal file only, not sent to Slack)
Code-level bug in `monthly-analytics-prestage`'s copy-to-sidecar logic (missing, silently failing, or racing against the next window's trigger). The underlying Bravo pipeline itself is healthy — confirmed via the actual trigger result.json files and raw export timestamps, not just run records (Rule 12 compliant).

## Recommended recovery (for the record — not sent to Slack)
Re-run `monthly-analytics-prestage` for the 2026-08 report month as soon as possible (the reasoning above about overwritten files is only valid while today's run is the most recent — re-running promptly avoids compounding with next month's cycle). Once 30/30 sidecar files exist, `monthly-analytics-report` completes in roughly a minute per its own SKILL.md. This watchdog task's hard rules keep it read-only/additive, so it did not attempt to trigger `monthly-analytics-prestage` itself — that's a fix that needs to happen the next time `monthly-analytics-prestage` itself is worked on, per Rule 15 (same-failure-twice = design problem, fix the task, not just relay the notice).

## Communication sent
One Slack DM to Joshua (`U03BB52MDSA` / `D03BHQH5VGT`), plain language only, no technical content, per vp-operating-rules Rule 16 & Rule 18.5:
> "The August 2026 company performance report needs another pull before it can go out — will post once it's ready."

No post made to #company-performance or #store-performance (nothing complete to post — Rule 18).

## Housekeeping this run also did
The `monthly-analytics-watchdog` SKILL.md at `~/Documents/Claude/Scheduled/monthly-analytics-watchdog/SKILL.md` still carried a pre-Rule-16/18 "Failure Alert Policy" wrapper and a Step 4 DM template that would have sent Joshua a heavily technical diagnostic DM (pre-stage status, sidecar counts, "likely cause," recovery command). Per vp-operating-rules Rule 16 point 5 ("any scheduled task whose SKILL.md still says to DM Joshua on failure should have that language corrected the next time that task is touched"), this run corrected that file in place: removed the old wrapper/template, replaced Step 4 with the Rule 16/18-compliant plain-language-only approach used above, and added a dated note explaining the change. No other task or production infra was touched.
