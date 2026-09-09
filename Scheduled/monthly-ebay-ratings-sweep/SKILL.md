---
name: monthly-ebay-ratings-sweep
description: Monthly (1st, 10 AM ET) — headless eBay feedback + Top Rated + Seller Standards sweep for all 5 Valley Pawn store accounts via the Trading + Analytics APIs (no browser), rank by 12-month positive %, post digest to #ebay-performance, save monthly doc, compare to prior month. Seller Standards live since 2026-09-06 (analytics token re-consent complete).
model: claude-sonnet-5
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Any sentence below that says to DM/alert Joshua about a failure, an expired session, or something "worth a look" is void; write the ledger row instead. Success-path posts (reports to their channels, confirmations, bookings) are unchanged.

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

> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (platform standard, set by Joshua 2026-07-22; v3 2026-09-08):** If this run fails, errors out, or cannot complete its core work, do NOT message Joshua, Preston, or anyone else, in any medium. Instead append ONE row to the fleet failure ledger `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` (use `mcp__Control_your_Mac__osascript` `do shell script "printf ... >> file"` if file tools cannot reach it) in exactly this form: `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or: yes, <the single thing only Joshua can do>> | OPEN |`. The `fleet-guardian` task reads this ledger twice a day, re-runs whatever is safe to re-run, rolls anything that truly needs Joshua into `Life OS/HUMAN_QUEUE.md`, and sends Joshua at most ONE consolidated plain-language DM per day. Individual tasks never DM about failures. All technical detail goes in the run output/log/STATUS file for the next Claude session to pick up. Never send failure notices to any team channel, store manager, employee, or Preston. FIELD COMMUNICATION RULE (unchanged): anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This v3 supersedes both the v2 one-line-DM rule and any older rule in this file.

## Execution Contract — DO NOT STOP EARLY

This task is complete ONLY after the documented final action (the Slack post in Step 3) returns success.

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

---

This is an automated run of a scheduled task. The user is not present. Execute autonomously. End with <run-summary>one or two sentences</run-summary>.

> **REWIRED 2026-09-06, Seller Standards ADDED 2026-09-06.** The previous version scraped public feedback pages and the Seller Hub in Chrome, which only ever captured whichever store Chrome was signed into (August 2026 = Lexington only; September produced nothing). It now runs headless against all 5 store accounts via the Trading API (feedback/ratings) AND the Analytics REST API (Seller Standards), using refresh tokens Joshua minted 2026-09-06 via full 3-legged OAuth (good ~547 days, stored at `~/.vp_secrets/ebay_analytics_oauth.json`). No browser is used at any point. Previous prompt: `SKILL.md.bak-pre-headless-20260906`.

Run the monthly eBay ratings sweep for Valley Pawn's 5 eBay store accounts and post the results to Slack.

## Step 1 — pull the data (headless)

    cd ~ && /usr/bin/python3 "$HOME/Documents/Claude/Projects/eBay/ebay_ratings_headless.py" > "$HOME/Documents/Claude/Projects/eBay/ebay-ratings-sweep-$(date +%Y-%m).md" 2>&1

That writes the month's report directly as markdown: a ranked table (feedback score, 12-month positive %, Top Rated Seller yes/no), per-store 1/6/12-month positive/neutral/negative counts, AND a Seller Standards table (level, evaluation date, late shipment rate, defect rate, cases closed without seller resolution, tracking-on-time rate) for all 5 stores, plus a "Below standard on:" list naming exactly which metric(s) are driving any BELOW_STANDARD level. The Top Rated column is authoritative — eBay's `GetUser` only returns `TopRatedSellerDetails` for accounts in the program, so "No" means not Top Rated. The Seller Standards numbers are real API pulls, never estimated — if a store's row says UNAVAILABLE with a pull-failed reason, report that plainly rather than guessing a level.

The script may take a minute; if the shell call reports a timeout, wait ~15 s and read the file rather than re-running. If any store shows `PULL FAILED` in the feedback table, retry the script once. If it still fails for that store, post the stores that succeeded and name the missing one plainly — never fill in a number you did not get (Rule 18).

## Step 2 — compare to last month

Read the prior month's file, `~/Documents/Claude/Projects/eBay/ebay-ratings-sweep-<prior YYYY-MM>.md`. Note for each store: change in feedback score, change in 12-month positive %, change in Seller Standards level (e.g. "Lexington moved from BELOW_STANDARD to ABOVE_STANDARD"), and any NEW negative or neutral feedback in the past 30 days (the 1-mo column).

## Step 3 — post to Slack

ONE message to #ebay-performance (channel ID C0ANVN5KX4Y) via the Slack connector. Title it "eBay Store Ratings Sweep — all 5 accounts" with the month. Rank stores best to worst by 12-month positive %. One short block per store: feedback score, 12-mo positive %, 12-mo pos/neutral/neg counts, Top Rated yes/no, Seller Standards level, and month-over-month change. For any store below standard, name the SPECIFIC metric driving it (e.g. "Harrisonburg — Below Standard: defect rate 4.92% (target under 2%), 4 cases closed without seller resolution") — never just say "below standard" with no cause, since that's not actionable. End with a short "Bottom line" — which stores need attention and why. Plain language only; no tool names, file paths, or error text in the channel.

## Step 4 — Seller Standards evaluation-date watch

Each store's Seller Standards cycle re-evaluates roughly monthly (`eval_date` / `eval_month` in the pulled data — currently all 5 stores evaluated 2026-08-21, so the next cycle lands ~2026-09-20/21). If any store below standard this run has an evaluation date in the next 10 days, flag that explicitly in the Slack post as a near-term re-evaluation to watch, not just a standing issue.

Do all of this autonomously — no check-ins with Joshua.
