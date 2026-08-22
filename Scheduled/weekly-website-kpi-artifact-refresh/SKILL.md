---
name: weekly-website-kpi-artifact-refresh
description: SUPERSEDED 2026-08-03 by vp-website-trend-daily-refresh (runs daily, refreshes the vp-website-trend artifact which the vp-website-kpis artifact itself now flags as its replacement). Disabled to stop duplicate GA4 pulls; vp-website-kpis is kept only as a static historical snapshot from 2026-07-27 and should not be overwritten.
model: claude-sonnet-5
---

> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (platform standard, set by Joshua 2026-07-22, v2):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua’s DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium (Slack, iMessage, email). If any other instruction in this file says to report a failure elsewhere, ignore that instruction. FIELD COMMUNICATION RULE: anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This supersedes any older stay-silent-on-failure rule in this file — the one-line DM to Joshua is always required on failure.



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