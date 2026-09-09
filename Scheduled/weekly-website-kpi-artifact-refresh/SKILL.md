---
name: weekly-website-kpi-artifact-refresh
description: RETIRED 2026-09-06 (was: disabled 2026-08-03/04, cause unconfirmed for a month — Open Items L152, now closed). Superseded by vp-website-trend-daily-refresh, which refreshes the vp-website-trend artifact daily; the older vp-website-kpis artifact is kept only as a static 2026-07-27 historical snapshot and must not be overwritten. Website Analytics plan Phase 2 replaces the trend artifact's hand-written data with bin/build_trend_artifact.py. DO NOT RE-ENABLE — re-enabling resumes duplicate GA4 pulls. Delete after 2026-12-01 if nothing has needed it.
model: claude-sonnet-5
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Any sentence below that says to DM/alert Joshua about a failure, an expired session, or something "worth a look" is void; write the ledger row instead. Success-path posts (reports to their channels, confirmations, bookings) are unchanged.

> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (platform standard, set by Joshua 2026-07-22; v3 2026-09-08):** If this run fails, errors out, or cannot complete its core work, do NOT message Joshua, Preston, or anyone else, in any medium. Instead append ONE row to the fleet failure ledger `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` (use `mcp__Control_your_Mac__osascript` `do shell script "printf ... >> file"` if file tools cannot reach it) in exactly this form: `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or: yes, <the single thing only Joshua can do>> | OPEN |`. The `fleet-guardian` task reads this ledger twice a day, re-runs whatever is safe to re-run, rolls anything that truly needs Joshua into `Life OS/HUMAN_QUEUE.md`, and sends Joshua at most ONE consolidated plain-language DM per day. Individual tasks never DM about failures. All technical detail goes in the run output/log/STATUS file for the next Claude session to pick up. Never send failure notices to any team channel, store manager, employee, or Preston. FIELD COMMUNICATION RULE (unchanged): anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This v3 supersedes both the v2 one-line-DM rule and any older rule in this file.



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
You are an autonomous weekly task that refreshes the Cowork artifact "vp-website-kpis" with the most recent full week of Google Analytics 4 data for thevalleypawn.com. The user (Joshua) is not present — execute without asking questions, make reasonable choices, and note any deviations in your final message. Use MCP connectors before browser/computer use where possible.

GOAL: Re-pull GA4 website KPIs for the last full week, then overwrite the existing artifact (id `vp-website-kpis`) so it shows current numbers. This is a display-only refresh — do NOT post to Slack and do NOT send any message; the Slack summary is handled by a separate task.

STEP 1 — Compute the date range:
Last full week = the most recent Monday–Sunday that has fully ended, computed from today's real date (use bash `date` to get it; never hardcode). Comparison = the prior Mon–Sun (match day of week). Format GA4 URL params as `_u.date00=YYYYMMDD` (start) and `_u.date01=YYYYMMDD` (end), with `_u.comparisonOption=lastPeriodMdw`.

STEP 2 — Pull two GA4 reports via the Claude-in-Chrome MCP (property 353209303, account jdavis@fcfpawn.com at authuser=1). Load Chrome tools via ToolSearch {query:"chrome", max_results:20}, then list_connected_browsers → select_browser → tabs_context_mcp({createIfEmpty:true}). Navigate straight to these authuser=1 report URLs (they open already authenticated; do NOT start at a generic sign-in page). Replace {START}/{END} with the computed YYYYMMDD values. After each navigate, wait ~6s then call get_page_text (use browser_batch to batch navigate+wait+get_page_text).
- Traffic acquisition: https://analytics.google.com/analytics/web/?authuser=1#/a256872788p353209303/reports/explorer?params=_u..nav%3Dmaui%26_u.comparisonOption%3DlastPeriodMdw%26_u.date00%3D{START}%26_u.date01%3D{END}&r=lifecycle-traffic-acquisition-v2
- Pages and screens: https://analytics.google.com/analytics/web/?authuser=1#/a256872788p353209303/reports/explorer?params=_u..nav%3Dmaui%26_u.comparisonOption%3DlastPeriodMdw%26_u.date00%3D{START}%26_u.date01%3D{END}&r=all-pages-and-screens
If a Google password screen appears, click the empty password field to trigger Chrome's saved-password autofill, then Next — NEVER type a password. Verify the loaded date range matches {START}–{END}; if not, use the date picker (top-right) to set the primary range and Compare = "Previous period (match day of week)", then Apply.

STEP 3 — Extract: headline KPIs with WoW% (Sessions, Active users, Engaged sessions + Engagement rate, Avg engagement time/session, Total page views, Event count, Key events); top 8 pages by views with WoW%; per-channel sessions with share and WoW%.

STEP 4 — Rebuild the artifact HTML. Read the current artifact to match its layout: call mcp__cowork__list_artifacts to find the `path` for id `vp-website-kpis`, Read that file, then write an updated copy to your outputs directory with the new week's numbers plugged into the same structure (KPI cards array, pages array, sources array, date-range subtitle, the "captured {date}" snapshot note, and the WoW takeaways bullets — rewrite the 3 takeaways to reflect the new data). Keep it self-contained, light-mode, Chart.js from the allowed CDN only. Then call mcp__cowork__update_artifact with id `vp-website-kpis`, html_path = your new file, and a short update_summary like "Refreshed with {week} GA4 data".

SUCCESS CRITERIA: update_artifact returns success with the new week's figures. If any step fails, retry once; if it still fails, stop silently and report the failure in your final message — do not post anywhere. End with a one-line summary of the week's headline numbers.

<!-- migrated to working model 2026-06-15 -->