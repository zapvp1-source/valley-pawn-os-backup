---
name: vp-ai-visibility-metrics
description: Weekly Valley Pawn AI-visibility scorecard — competitor-benchmarked prompt tests across 5 AI engines + GA4 AI-referral traffic; computes a Visibility Index, logs to the AI Visibility Tracker sheet, posts to Slack #ai-marketing with week-over-week delta
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
Produce the weekly Valley Pawn AI-visibility scorecard and post it to Slack #ai-marketing (private, channel ID C0BCEESUANM). Use the Claude in Chrome browser tools for the web/GA4 checks and the Slack MCP connector to post. Each run starts fresh — everything needed is below. This measures whether Valley Pawn is SHOWING UP in AI search, whether it BEATS its top local competitor, and whether AI tools send real traffic.

=== PART A — AI VISIBILITY, COMPETITOR-BENCHMARKED (prompt tests) ===
Run each customer-style query below on each engine. For BOTH Valley Pawn AND the named rival for that query's market, record: (a) does the business appear in the answer? (b) is it named/ranked #1? (c) is it cited/linked? For Valley Pawn also flag any WRONG info (old hours, missing Suite C for Roanoke, wrong phone, or the legacy "Dixie Pawn" name — that name must never appear).

Engines to test (all work with saved logins / no login):
- Perplexity — https://www.perplexity.ai (no login)
- Google AI Overview — search at https://www.google.com/search?q=<query> and read the AI Overview box. If no AI Overview appears, note that and instead read the local pack / top organic and score presence there.
- Gemini — https://gemini.google.com (logged in via the Google account)
- ChatGPT — https://chatgpt.com (logged in; start a new chat each query)
- Microsoft Copilot — https://copilot.microsoft.com (logged in / no login)

Queries and the primary local rival to benchmark against (the rival is a SEED — if an engine ranks a DIFFERENT competitor above Valley Pawn, record that competitor's name instead and note it):
  1. best pawn shop near Roanoke VA            → rival: The PawnShop (Roanoke)
  2. where can I sell gold in Harrisonburg VA   → rival: JBS Pawn
  3. pawn shop open on Wednesday near Culpeper VA → rival: Pawn-Mart (Culpeper is our only Wed-open store)
  4. no credit check pawn loan Shenandoah Valley VA → rival: whichever pawn shop the engine names ahead of us (region-wide)
  5. where to sell jewelry in Waynesboro VA     → rival: Tobey's Pawn Shop
  6. pawn shop near Lexington VA                → rival: Rockbridge Pawn and Guns

For each engine, tally Valley Pawn mentions (e.g. "Perplexity 5/6"). Then compute the VISIBILITY INDEX = across all query×engine cells actually tested, the % where Valley Pawn appears AND is ranked at least even with (or ahead of) the rival. Example: 30 cells tested, we match-or-beat the rival in 24 → Index = 80%. Report the Index as the headline number.

=== PART B — AI REFERRAL TRAFFIC (GA4) ===
Open GA4 for thevalleypawn.com: https://analytics.google.com/analytics/web/?authuser=1#/p353209303/reports/explorer?params=_u..nav%3Dmaui&r=lifecycle-traffic-acquisition-v2 (Reports > Acquisition > Traffic acquisition). If the deep link doesn't land, go to analytics.google.com (authuser=1), pick the "thevalleypawn.com" property, open Reports > Acquisition > Traffic acquisition. Set date range to last 7 days. Set the channel group / primary dimension to "AI Assistants Tracking" and read the "AI Assistants" row: Sessions, Active users, Key events. Also note total site sessions. (As of 2026-07-04 the "AI Assistants" channel now also matches Source regex chatgpt|openai|perplexity|gemini|copilot|claude|bard, so chatgpt.com traffic should land here rather than Unassigned — if it still shows nothing, switch the dimension to "Session source" and look for rows containing chatgpt/openai/perplexity/gemini/copilot/claude and report those.) Property: account a256872788, property p353209303, Google account fullcirclepawn@gmail.com = authuser=1.

=== PART C — TREND LOG ===
Trend ledger = Google Sheet "Valley Pawn — AI Visibility Tracker" (ID 17gkCl9BpB8yAQZcCs6cg8SDXQfaSGdyKceNJKfwMRMs) in Valley Pawn Drive > Weekly KPIS, opened at https://docs.google.com/spreadsheets/d/17gkCl9BpB8yAQZcCs6cg8SDXQfaSGdyKceNJKfwMRMs/edit (account authuser=0 / jdavis@fcfpawn.com). Columns: Week Of | Visibility Index % | Perplexity /6 | Google /6 | Gemini /6 | ChatGPT /6 | Copilot /6 | AI Sessions (7d) | Total Sessions (7d) | Top AI Source | Wins | Fixes / Action Items.
1. Before posting, read the LAST row of the sheet (previous week) to get the prior Visibility Index — you'll show the delta in Slack.
2. After computing this week's numbers, APPEND a new row to the first empty row with this week's values. Best-effort: if the sheet can't be reached this run, don't fail — just skip the append and note it.

=== POST TO SLACK — #ai-marketing (ID C0BCEESUANM; do NOT DM anyone) ===
Skimmable weekly scorecard:
  *📊 Valley Pawn — AI Visibility Scorecard (week of <date>)*
  *Visibility Index:* <N>% — we match-or-beat our top local rival on <X> of <Y> AI answers  (<▲/▼ N pts vs last week>, or "first competitor-benchmarked week")
  *Showing up in AI answers:* Perplexity X/6 · Google X/6 · Gemini X/6 · ChatGPT X/6 · Copilot X/6
  *Head-to-head:* <per-market one-liners where a rival beat us, e.g. "Roanoke: The PawnShop still ranked above us on Perplexity + Google">
  *AI referral traffic (last 7 days):* <N> sessions / <N> users from AI assistants (top source: <source>); <N> key events. (or "no measurable AI referral traffic yet — normal this early")
  *Wins:* <queries/engines where we led>
  *Fix:* <wrong info an AI showed, or markets where a rival beat us, each with the suggested fix; if none, "nothing flagged">
Keep it phone-readable. If a particular engine, GA4, or the sheet can't be reached this run, note it briefly and report what you did get rather than failing the whole run. Do NOT duplicate the Monday AI-search health check (schema/llms.txt/NAP) — that is a separate task; this one is prompt tests + competitor benchmark + GA4 traffic only.