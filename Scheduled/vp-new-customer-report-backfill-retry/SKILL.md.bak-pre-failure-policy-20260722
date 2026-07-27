---
name: vp-new-customer-report-backfill-retry
description: One-time retry of the new-customer historical backfill pull (7 months x 5 stores via chekkit-invites-range), deferred to after the 5PM Bravo Health Gate since the 12:15PM attempt today aborted with Bravo not logged in
---

One-time follow-up for the Valley Pawn new-customer MoM/YoY report project. This task is additive only — do not modify any existing Bravo saved report, AHK handler, pipeline cell, or scheduled task.

CONTEXT: Earlier today (2026-07-16 ~12:15 PM) a historical backfill trigger for the `chekkit-invites-range` pipeline cell (7 monthly date windows x 5 stores = 35 cells: 2025-07-01..2025-07-31, 2026-02-01..2026-02-28, 2026-03-01..2026-03-31, 2026-04-01..2026-04-30, 2026-05-01..2026-05-31, 2026-06-01..2026-06-30, 2026-07-01..2026-07-16) aborted immediately with "Skipped by safety rail: bravo-not-ready (could not reach a logged-in dashboard)" — Bravo wasn't logged in on the Parallels VM at that time. This retry runs after the 5PM Bravo Health Gate task, which should have restored a logged-in dashboard.

`/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/` is OUTSIDE this task's sandbox — use `mcp__Control_your_Mac__osascript` `do shell script` for every read/write there, never the Write tool directly.

STEP 1 — Check readiness. Via osascript, check whether a recent Bravo Health Gate result indicates a healthy dashboard (look for the latest healthgate result file in `results/`, or just proceed to Step 2 and let the pipeline's own safety rail be the judge).

STEP 2 — Drop the backfill trigger. Generate id `new-customers-backfill-<ISO timestamp>`. Write trigger JSON to `triggers/<id>.json` with the 7 report entries above (reuse the exact date ranges listed in CONTEXT — `chekkit-invites-range`, stores CUL/HAR/LEX/ROA/WAY). Poll `results/<id>.result.json` every 90s, timeout 90 minutes (35 cells with store-cycling can take a while).

STEP 3 — If it aborts again with the same bravo-not-ready safety rail: do NOT fabricate data. Do NOT DM Joshua (per standing rule: scheduled tasks don't DM on failure). Just log the outcome clearly in this run's own output. The already-existing monthly recurring task `vp-new-customer-report` (fires 7 AM on the 3rd of each month) will keep trying going forward regardless, so this isn't a dead end — no further one-time retries need to be scheduled from here.

STEP 4 — If it succeeds (even partially — some stores/months landed and others didn't): for every CSV that landed in `output/` (pattern `<end-date>_<STORE>_chekkit-invites-range.csv`), count data rows (excluding header; blank phone+email rows are already dropped by the handler, so every remaining row = one new customer for that store/window). Write/append to `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/new_customers_monthly_rollup.json` (create if it doesn't exist) as a JSON array of `{"store":"CUL","month":"2026-07","count":N}` rows — one entry per store per successfully-pulled month (use "2025-07" for the July-2025 window; note the July-2026 window is partial, through the 16th — label its month key "2026-07" but do not treat it as a complete month in MoM comparisons involving prior full months; flag it as partial in the artifact).

ALSO fold in the existing real data point from `output/2026-06-30_{CUL,HAR,LEX,ROA,WAY}_chekkit-invites-range.csv` (a proven 2026-06-30 smoke test covering 2026-04-30..2026-06-30, all 5 stores, real row counts: CUL 236, HAR 177, LEX 93, ROA 214, WAY 240) — store this as a labeled baseline data point (not decomposed into individual months, since the pull spanned Apr 30–Jun 30 as one window) rather than discarding it.

STEP 5 — Compute MoM (consecutive-month deltas per store and company-wide, using whatever full months are now available) and YoY (2026-07 partial vs 2025-07 full — label clearly that this specific comparison uses a partial current-month figure) per store and company-wide (dedupe company total by email, fallback phone, across that month's 5 store CSVs).

STEP 6 — Build/update the Cowork artifact. Call `mcp__cowork__list_artifacts` — if `vp-new-customer-report` doesn't exist yet, build a new self-contained HTML (Chart.js trend line per store + company total, MoM/YoY summary table, styled like the existing `vp-website-trend`/`asset-recovery-2025-vs-2026` artifacts) and call `mcp__cowork__create_artifact` with id `vp-new-customer-report`. If it already exists, `Read` its current HTML and call `mcp__cowork__update_artifact`. Clearly mark any month with fewer than 5 stores' worth of data as "partial" in the UI rather than presenting it as complete. Do not touch `vp-dashboard-refresh` — it auto-syncs new artifacts nightly.

STEP 7 — Post to Slack **#new-customers** (channel ID **C0BHF9NM0BH** — https://valleypawnworkspace.slack.com/archives/C0BHF9NM0BH) ONLY if Step 4+ produced at least one genuinely complete month per store. Use normal Slack report format (matches other Valley Pawn automation posts — plain text, bullet per store, bolded/emoji header is fine, no code block needed):
```
📊 New Customers — Historical Backfill Complete
• Culpeper: <n> most recent complete month (MoM <±%>, YoY <±% or "n/a">)
• Harrisonburg: <n> (MoM <±%>, YoY <±% or "n/a">)
• Lexington: <n> (MoM <±%>, YoY <±% or "n/a">)
• Roanoke: <n> (MoM <±%>, YoY <±% or "n/a">)
• Waynesboro: <n> (MoM <±%>, YoY <±% or "n/a">)
Company total (deduped): <n>
Full trend now live on the VP dashboard.
```
If data is still incomplete (some stores/months missing), do NOT post to Slack — just leave the artifact/rollup in whatever state it landed in; the monthly recurring task will keep filling gaps.

Never use the legacy "Dixie Pawn" name. Never fabricate numbers. Never ask Joshua to log in or click anything.