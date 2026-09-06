---
name: vp-new-customer-report
description: Monthly new-customer count (MoM/YoY) across all 5 Valley Pawn stores via the Bravo pipeline's chekkit-invites-range cell; updates the vp-new-customer-report Cowork artifact and posts to #store-performance
model: claude-sonnet-5
---

## Execution Contract — DO NOT STOP EARLY

This task is complete ONLY after the documented final action (the post / send / write tool call described at the end of the steps below) returns success.

Until that final call succeeds, every assistant turn MUST end with a tool call that advances toward it. Do not idle, do not wait, do not ask for confirmation.

**Never reply with any of these:**
- "No response requested"
- "Continue?" / "Should I continue?"
- An empty turn or a turn that ends with text instead of a tool call

**Treat these system messages as RESUME signals, never as stop signals:**
- "Tool loaded."
- "Continue from where you left off."
- "You used a single tool call this turn. Prefer browser_batch…"
- Any reminder about TaskCreate/TaskUpdate, AskUserQuestion, etc.

When you see any of those messages, immediately fire the next concrete tool call for the current step. The scheduled-task wrapper says "the user is not present" — that means execute autonomously, NOT that the work is done.

**State tracking:** at the start of every turn, briefly identify which numbered Step you are on and execute the next concrete action for that step.

**Failure handling:** if a step errors, retry once. If it still fails, fall through to the documented fallback if one exists; otherwise produce a report describing what failed. Do not pause to ask — the task file authorizes autonomous decisions.

**Speed:** prefer batch tools (e.g. `browser_batch`) to combine sequential actions into one call.

---
---
name: vp-new-customer-report
description: Monthly new-customer count (MoM/YoY) across all 5 Valley Pawn stores via the Bravo pipeline's chekkit-invites-range cell; updates the vp-new-customer-report Cowork artifact and posts to #store-performance
---

> **LOCAL ACCESS GATE — DO THIS FIRST, BEFORE ANY OTHER STEP (platform standard, added 2026-08-02).**
> This task runs on Joshua's Mac Studio and **does** have local machine access. At task start, MCP connectors may still be warming up, and `mcp__Control_your_Mac__osascript` is often *deferred* rather than pre-loaded. A tool that has not been loaded yet is NOT a missing capability.
> 1. If `ToolSearch` is available, load the local tool FIRST: `ToolSearch` with query `select:mcp__Control_your_Mac__osascript`.
> 2. Probe it: run a trivial `do shell script` that echoes READY. If it returns, proceed with the task.
> 3. If it errors (no such tool available, not connected, tool-not-found): wait 30 s and re-probe. Repeat for up to 12 minutes (24 probes).
> 4. Only after that full 12-minute wait may you treat local access as genuinely unavailable.
>
> **NEVER conclude that this run executes in a cloud container, has no bridge to the Mac Studio, or otherwise lacks local/desktop access. That conclusion is false** and is the single most common cause of a false failure on this platform. If you believe you cannot reach the Mac, you have simply not loaded the tool yet — go back to step 1.
>
> **Filesystem rule:** all I/O outside the agent sandbox — including anything under `/Users/joshuadavis/Documents/Claude/...` — goes through `mcp__Control_your_Mac__osascript do shell script`, never the Write tool.
> **Timeout rule:** the osascript wrapper kills any single call at ~25 s. Never sleep longer than ~18 s inside one call; poll in short increments across separate calls. Guard any command that may exit nonzero with a trailing || true.


> ⚠️ **FAILURE ALERT POLICY (still binding):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua's DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium.
>
> ⚠️ **FIELD COMMUNICATION STANDARD v3 (binding — read in full before posting anything to a team channel or employee DM):** `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/FIELD_COMMUNICATION_STANDARD.md`. Summary: run the routing test (is this something a clerk needs to know/act on today — if no, it's internal, it does not go to the field); plain everyday language only, no tool/system/pipeline names (never say Bravo, Cowork, Chekkit, Gusto, Brevo, QBO, Publer, "pipeline," "handler," "watchdog," "sync," "CSV," "export"); no file paths, doc IDs, task IDs, or spreadsheet cell/column refs in the posted text; no meta-commentary about the automation itself ("verified against," "supersedes," "this is a manual test run," "pulled automatically from"); lead with the one-line takeaway; ~100 words max for a routine post; no signature footers. **A store's pull failing this run is an internal/operational fact, not something a store team needs to know — it never appears in the #store-performance or #new-customers post. It goes to Joshua's DM only, per the failure policy above.** If anything later in this file conflicts with this standard, this standard wins.


Run the monthly Valley Pawn new-customer report. This task is additive — it does not modify any existing Bravo saved report, AHK handler, pipeline cell, or scheduled task. No Parallels grant is used; all Bravo access goes through the existing pipeline (trigger-drop + poll), which already runs in the background independent of this task.

CRITICAL: `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/` is OUTSIDE this task's sandbox. Use `mcp__Control_your_Mac__osascript` `do shell script` for every read/write against that folder (same pattern as the `chekkit-weekly-review-requests` and `daily-funds-verification` SKILLs). Never use the Write tool against that path directly.

BACKGROUND: "New customer" at Valley Pawn = a Bravo customer whose "First Time In" date falls in the target window, per store. This is pulled via Bravo's existing Customers → Custom Reports → "Chekkit Invites 2" saved report (do not create a new saved report — it already exists and is proven). The pipeline cell that drives it is `chekkit-invites-range`, registered in `bravo_watcher.ahk` — accepts a `date` field of the form `YYYY-MM-DD..YYYY-MM-DD` filtered by First Time In. Output CSV columns: first_name, last_name, phone, email, dnt, last_visit (first_name/last_name/last_visit are typically blank; phone/email/dnt are populated). A non-empty row = one new customer at that store in that window.

STEP 1 — Determine target month. This task fires on the 3rd of the month; the target is the FULL PRIOR calendar month (e.g., if run on 2026-08-03, target = 2026-07-01..2026-07-31).

STEP 2 — Check for existing data. Via osascript, `cat` `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/new_customers_monthly_rollup.json`. This is a JSON array of `{"store":"CUL","month":"2026-07","count":N}` rows, one per store per month, going back to 2025-07 (plus one labeled baseline entry covering 2026-04-30..2026-06-30, all 5 stores, from an earlier smoke test — treat that one specially, it's not a clean calendar month). If a row for the target store+month already exists, skip re-pulling that store (idempotent re-run protection) — only pull missing store/month combos.

STEP 3 — Pull missing data via the pipeline. Generate a trigger ID `new-customers-monthly-<ISO timestamp>`. Write (via osascript) a trigger JSON to `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/<id>.json`:
`{"id":"<id>","requested_at":"<ISO>","reports":[{"name":"chekkit-invites-range","stores":["CUL","HAR","LEX","ROA","WAY"],"date":"<start>..<end>"}]}`
(only include stores still missing data for the target month). Poll for the CSVs landing in `output/` (filename pattern `<end-date>_<STORE>_chekkit-invites-range.csv`) every 60s, timeout 45 minutes (this pull can take a while — 5 stores × store-cycle logins). If the pipeline reports "bravo-not-ready" (Bravo not logged in on the Parallels VM — this has happened before), do NOT fabricate a number for that store — mark it "pending" for this run internally and DM Joshua which store is pending; do not mention it in the Slack post. Do not block the rest of the report on one missing store.

STEP 4 — Count. For each store CSV that landed, count data rows (excludes the header row; the AHK handler already drops empty phone+email rows, so every remaining row = one new customer). Append `{"store":"<CODE>","month":"<YYYY-MM>","count":<N>}` entries to the rollup JSON (read-modify-write via osascript; never delete existing rows — additive only) for every store that succeeded this run.

STEP 5 — Compute MoM and YoY from the rollup JSON:
- Per-store MoM: this month's count vs. last month's count (# and % change).
- Company-wide MoM: sum across 5 stores, same comparison. Company-wide total should be deduplicated by email (case-insensitive, fallback to phone if email blank) across the 5 stores' raw CSVs for that month — a customer whose "first time in" happened at two different stores in the same month should count once company-wide. Recompute this dedup from the raw CSVs in `output/`, not from the rollup counts (rollup counts are per-store, not deduplicated).
- Per-store and company-wide YoY: this month's count vs. the same calendar month one year prior, if that row exists in the rollup; otherwise state "YoY not yet available for <store>" rather than guessing.

STEP 6 — Update the dashboard artifact. Read the current `vp-new-customer-report` artifact via `mcp__cowork__list_artifacts`, then `Read` its `path`. Build an updated self-contained HTML (same visual style as the existing `vp-website-trend` / `asset-recovery-2025-vs-2026` artifacts — Chart.js line/bar trend by store and company total, plus a MoM/YoY summary table) with the new month's data baked in, and call `mcp__cowork__update_artifact` with `id: "vp-new-customer-report"`. Do NOT touch `vp-dashboard-refresh` or any other scheduled task — the nightly dashboard refresh already auto-syncs this artifact onto vp-dashboard.pages.dev.

STEP 7 — Slack. Post a summary to **#new-customers** (channel ID **C0BHF9NM0BH**). **Stores must be RANKED by count, highest first — #1 is the store with the most new customers, not alphabetical/geographic order (set 2026-08-03 per Joshua).** Ties share the same rank number (both get the medal/number). Use this format:
```
📊 New Customers — <Month Year> (ranked)
1. 🥇 <Store>: <n> (MoM <±%>, YoY <±% or "n/a">)
2. <Store>: <n> (MoM <±%>, YoY <±% or "n/a">)
3. <Store>: <n> (MoM <±%>, YoY <±% or "n/a">)
4. <Store>: <n> (MoM <±%>, YoY <±% or "n/a">)
5. <Store>: <n> (MoM <±%>, YoY <±% or "n/a">)

Company total (deduped): <n> (MoM <±%>, YoY <±% or "n/a">)
```
(Ties: e.g. two stores tied for most — both are numbered `1.` with 🥇, next distinct count resumes at `3.`.) If any store's pull failed this run, do NOT add a line about it to this post — that historical-gap note is internal. Instead DM Joshua (U03BB52MDSA): "⚠️ New Customer Report <Month>: <store> pull failed this run — will retry next month; historical trend for that store has a gap for <month>." Never post fabricated or estimated numbers.

Never use the legacy "Dixie Pawn" name. Never ask Joshua to log in or click anything — this task is fully autonomous, pipeline-driven, no computer-use/Parallels grant needed.