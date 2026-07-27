---
name: vp-new-customer-report
description: Monthly new-customer count (MoM/YoY) across all 5 Valley Pawn stores via the Bravo pipeline's chekkit-invites-range cell; updates the vp-new-customer-report Cowork artifact and posts to #store-performance
---

Run the monthly Valley Pawn new-customer report. This task is additive — it does not modify any existing Bravo saved report, AHK handler, pipeline cell, or scheduled task. No Parallels grant is used; all Bravo access goes through the existing pipeline (trigger-drop + poll), which already runs in the background independent of this task.

CRITICAL: `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/` is OUTSIDE this task's sandbox. Use `mcp__Control_your_Mac__osascript` `do shell script` for every read/write against that folder (same pattern as the `chekkit-weekly-review-requests` and `daily-funds-verification` SKILLs). Never use the Write tool against that path directly.

BACKGROUND: "New customer" at Valley Pawn = a Bravo customer whose "First Time In" date falls in the target window, per store. This is pulled via Bravo's existing Customers → Custom Reports → "Chekkit Invites 2" saved report (do not create a new saved report — it already exists and is proven). The pipeline cell that drives it is `chekkit-invites-range`, registered in `bravo_watcher.ahk` — accepts a `date` field of the form `YYYY-MM-DD..YYYY-MM-DD` filtered by First Time In. Output CSV columns: first_name, last_name, phone, email, dnt, last_visit (first_name/last_name/last_visit are typically blank; phone/email/dnt are populated). A non-empty row = one new customer at that store in that window.

STEP 1 — Determine target month. This task fires on the 3rd of the month; the target is the FULL PRIOR calendar month (e.g., if run on 2026-08-03, target = 2026-07-01..2026-07-31).

STEP 2 — Check for existing data. Via osascript, `cat` `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/new_customers_monthly_rollup.json`. This is a JSON array of `{"store":"CUL","month":"2026-07","count":N}` rows, one per store per month, going back to 2025-07 (plus one labeled baseline entry covering 2026-04-30..2026-06-30, all 5 stores, from an earlier smoke test — treat that one specially, it's not a clean calendar month). If a row for the target store+month already exists, skip re-pulling that store (idempotent re-run protection) — only pull missing store/month combos.

STEP 3 — Pull missing data via the pipeline. Generate a trigger ID `new-customers-monthly-<ISO timestamp>`. Write (via osascript) a trigger JSON to `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/<id>.json`:
`{"id":"<id>","requested_at":"<ISO>","reports":[{"name":"chekkit-invites-range","stores":["CUL","HAR","LEX","ROA","WAY"],"date":"<start>..<end>"}]}`
(only include stores still missing data for the target month). Poll for the CSVs landing in `output/` (filename pattern `<end-date>_<STORE>_chekkit-invites-range.csv`) every 60s, timeout 45 minutes (this pull can take a while — 5 stores × store-cycle logins). If the pipeline reports "bravo-not-ready" (Bravo not logged in on the Parallels VM — this has happened before), do NOT fabricate a number for that store — mark it "pending" for this run and note it plainly in the Slack post. Do not block the rest of the report on one missing store.

STEP 4 — Count. For each store CSV that landed, count data rows (excludes the header row; the AHK handler already drops empty phone+email rows, so every remaining row = one new customer). Append `{"store":"<CODE>","month":"<YYYY-MM>","count":<N>}` entries to the rollup JSON (read-modify-write via osascript; never delete existing rows — additive only) for every store that succeeded this run.

STEP 5 — Compute MoM and YoY from the rollup JSON:
- Per-store MoM: this month's count vs. last month's count (# and % change).
- Company-wide MoM: sum across 5 stores, same comparison. Company-wide total should be deduplicated by email (case-insensitive, fallback to phone if email blank) across the 5 stores' raw CSVs for that month — a customer whose "first time in" happened at two different stores in the same month should count once company-wide. Recompute this dedup from the raw CSVs in `output/`, not from the rollup counts (rollup counts are per-store, not deduplicated).
- Per-store and company-wide YoY: this month's count vs. the same calendar month one year prior, if that row exists in the rollup; otherwise state "YoY not yet available for <store>" rather than guessing.

STEP 6 — Update the dashboard artifact. Read the current `vp-new-customer-report` artifact via `mcp__cowork__list_artifacts`, then `Read` its `path`. Build an updated self-contained HTML (same visual style as the existing `vp-website-trend` / `asset-recovery-2025-vs-2026` artifacts — Chart.js line/bar trend by store and company total, plus a MoM/YoY summary table) with the new month's data baked in, and call `mcp__cowork__update_artifact` with `id: "vp-new-customer-report"`. Do NOT touch `vp-dashboard-refresh` or any other scheduled task — the nightly dashboard refresh already auto-syncs this artifact onto vp-dashboard.pages.dev.

STEP 7 — Slack. Post a summary to **#new-customers** (channel ID **C0BHF9NM0BH** — https://valleypawnworkspace.slack.com/archives/C0BHF9NM0BH). Use normal Slack report format (plain text, bullet per store):
```
📊 New Customers — <Month Year>
• Culpeper: <n> (MoM <±%>, YoY <±% or "n/a">)
• Harrisonburg: <n> (MoM <±%>, YoY <±% or "n/a">)
• Lexington: <n> (MoM <±%>, YoY <±% or "n/a">)
• Roanoke: <n> (MoM <±%>, YoY <±% or "n/a">)
• Waynesboro: <n> (MoM <±%>, YoY <±% or "n/a">)
Company total (deduped): <n> (MoM <±%>, YoY <±% or "n/a">)
```
If any store's pull failed this run, add a line: "⚠️ <store> pull failed this run — will retry next month; historical trend for that store has a gap for <month>." Never post fabricated or estimated numbers.

Never use the legacy "Dixie Pawn" name. Never ask Joshua to log in or click anything — this task is fully autonomous, pipeline-driven, no computer-use/Parallels grant needed.