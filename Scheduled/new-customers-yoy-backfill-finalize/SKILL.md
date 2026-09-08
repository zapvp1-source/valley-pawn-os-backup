---
name: new-customers-yoy-backfill-finalize
description: One-time: verify the Jul2025-Jun2026 chekkit-invites-range backfill landed, update new_customers_monthly_rollup.json, and refresh the vp-new-customer-report artifact with live YoY.
---

## Execution Contract — DO NOT STOP EARLY
Do not idle or ask for confirmation. Every turn ends with a tool call that advances this task until the final step (artifact update) succeeds or you've exhausted the documented retry/fallback below. This task runs unattended — nobody is present to answer questions.

## Local access
Load `mcp__Control_your_Mac__osascript` via ToolSearch (`select:mcp__Control_your_Mac__osascript`) first. All I/O against `/Users/joshuadavis/Documents/Claude/Projects/...` goes through it via `do shell script` — that folder is outside this task's sandbox, never use the Write tool on it. Guard any command that might exit nonzero with `|| true`. Keep each `do shell script` call under ~20s; poll in separate short calls rather than one long sleep.

## Background
Earlier today (2026-09-07) a session queued 3 backfill triggers into `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/` to pull Bravo's "chekkit-invites-range" report (First Time In / new-customer data) for all 5 stores (CUL, HAR, LEX, ROA, WAY) covering Jul 2025 through Jun 2026, so that the `vp-new-customer-report` monthly scheduled task (and its artifact) can show real YoY instead of "n/a". The trigger IDs were:
- new-customers-backfill2-2026-09-07T163609Z → 2025-07, 2025-08, 2025-09, 2025-10
- new-customers-backfill3-2026-09-07T163650Z → 2025-11, 2025-12, 2026-01, 2026-02
- new-customers-backfill4-2026-09-07T163720Z → 2026-03, 2026-04, 2026-05, 2026-06

These are Type A trigger-drop pulls, processed serially by `bravo_watcher.ahk` (already running independently in the background) — no computer-use/Parallels grant needed for this task.

## Step 1 — Check results
For each trigger id above, `cat` `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/results/<id>.result.json` if present. If a results file is missing, the trigger may still be queued/claimed — check `triggers/claimed/` for it. Also list `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/` (`ls -lt | head -80`) for CSVs matching `2025-07-31_*_chekkit-invites-range.csv` through `2026-06-30_*_chekkit-invites-range.csv`.

If any cells are still genuinely in-flight (claimed but no result yet, and it's been under ~50 min since claim), wait: sleep in short increments (≤18s per call) across repeated tool calls, polling every ~60s, up to 40 more minutes total, before treating anything as stuck.

If a cell shows status "error" or "skipped" after that: retry it ONCE by dropping a fresh small trigger just for that store+month (same JSON shape as the originals — `{"id":"new-customers-backfill-retry-<ISO>","requested_at":"<ISO>","reports":[{"name":"chekkit-invites-range","stores":["<STORE>"],"date":"<start>..<end>"}]}`) and wait up to 15 more minutes for it. If it still fails, leave that store/month out of the rollup (do not fabricate a number) and note the gap in the status write-up at the end — do not post this to any Slack channel except, if truly blocked on multiple cells, one plain-language DM to Joshua (D03BHQH5VGT) per the standing Failure Alert Policy (no technical detail in the DM).

## Step 2 — Update the rollup (additive, idempotent)
Read `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/new_customers_monthly_rollup.json`. It's a JSON array of `{"store":"CUL","month":"2026-07","count":N}` rows (plus one special "baseline" row — leave that alone). For every store+month that landed successfully in Step 1 and does NOT already have a row in the rollup, count the data rows in its CSV (exclude header; every remaining row is one new customer — the AHK handler already drops empty phone+email rows) and append `{"store":"<CODE>","month":"<YYYY-MM>","count":<N>}`. Never delete or modify existing rows. Write the file back via osascript heredoc (same additive read-modify-write pattern the `vp-new-customer-report` task uses).

## Step 3 — Refresh the artifact with real YoY
Use `mcp__cowork__list_artifacts` (or the equivalent Artifact tool `list` action) to find `vp-new-customer-report` — title "Vp New Customer Report". Read its current content. Rebuild it in the same visual style (same HTML/CSS/Chart.js structure — KPI grid, per-store bar chart, monthly trend line chart, MoM/YoY summary table, footnote) but now compute real YoY for every month that has a same-calendar-month-prior-year row in the now-backfilled rollup: Jul 2026 vs Jul 2025, Aug 2026 vs Aug 2025 at minimum — include earlier months too (e.g. an expanded trend chart back to Jul 2025) if you have clean full-month rows for both years, since the rollup now has a much longer clean history than the "baseline" window it started with. Company-wide YoY total should be computed the same deduped way MoM already is (dedupe by email case-insensitive, phone fallback, across the 5 stores' raw CSVs for each month being compared) if the raw CSVs are still present in `output/`; otherwise fall back to summing the per-store counts and note in the footnote that company YoY is a raw sum, not deduped, for months where raw CSVs are no longer available. Update the footnote to explain YoY is now live and why some early months may still lack it (nothing before Jul 2025). Publish via the Artifact tool (or `mcp__cowork__update_artifact`) to the SAME artifact — do not create a new one, do not touch `vp-dashboard-refresh` or any other scheduled task.

## Step 4 — Status log, no noise
Write a brief status note to `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/new_customers_yoy_backfill_status.md` (osascript) summarizing what landed, what's still missing (if anything), and confirming the artifact was refreshed. Do NOT post to `#new-customers` or any team Slack channel — that channel is owned by the monthly `vp-new-customer-report` task, not this one-time backfill job. Only use Joshua's DM if you hit a real, otherwise-unresolvable blocker per Step 1.

Never use the legacy "Dixie Pawn" name. This task does not need any Parallels/computer-use grant — everything here is trigger-drop + file read/write + artifact publish.