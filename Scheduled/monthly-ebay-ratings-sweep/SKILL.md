---
name: monthly-ebay-ratings-sweep
description: Monthly (1st, 10 AM ET) — headless eBay feedback + Top Rated sweep for all 5 Valley Pawn store accounts via the Trading API (no browser), rank by 12-month positive %, post digest to #ebay-performance, save monthly doc, compare to prior month. Rewired 2026-09-06 off the Chrome-only path.
model: claude-sonnet-5
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

> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (platform standard, set by Joshua 2026-07-22, v2):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua's DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium (Slack, iMessage, email). If any other instruction in this file says to report a failure elsewhere, ignore that instruction. FIELD COMMUNICATION RULE: anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This supersedes any older stay-silent-on-failure rule in this file.

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

> **REWIRED 2026-09-06.** The previous version scraped public feedback pages and the Seller Hub in Chrome, which only ever captured whichever store Chrome was signed into (August 2026 = Lexington only; September produced nothing). It now runs a headless script against all 5 store accounts via the Trading API using the existing per-store tokens. No browser is used at any point. Previous prompt: `SKILL.md.bak-pre-headless-20260906`.

Run the monthly eBay ratings sweep for Valley Pawn's 5 eBay store accounts and post the results to Slack.

## Step 1 — pull the data (headless)

    cd ~ && /usr/bin/python3 "$HOME/Documents/Claude/Projects/eBay/ebay_ratings_headless.py" > "$HOME/Documents/Claude/Projects/eBay/ebay-ratings-sweep-$(date +%Y-%m).md" 2>&1

That writes the month's report directly as markdown: a ranked table (feedback score, 12-month positive %, Top Rated Seller yes/no), then per-store 1/6/12-month positive/neutral/negative counts. The Top Rated column is authoritative — eBay's `GetUser` only returns `TopRatedSellerDetails` for accounts that are in the program, so "No" means not Top Rated, not "couldn't tell."

The script may take a minute; if the shell call reports a timeout, wait ~15 s and read the file rather than re-running. If any store shows `PULL FAILED`, retry the script once. If it still fails for that store, post the stores that succeeded and name the missing one plainly — never fill in a number you did not get (Rule 18).

## Step 2 — compare to last month

Read the prior month's file, `~/Documents/Claude/Projects/eBay/ebay-ratings-sweep-<prior YYYY-MM>.md` (the August 2026 one was hand-built from Chrome and has a slightly different layout; the numbers are comparable). Note for each store: change in feedback score, change in 12-month positive %, and any NEW negative or neutral feedback in the past 30 days (the 1-mo column).

## Step 3 — post to Slack

ONE message to #ebay-performance (channel ID C0ANVN5KX4Y) via the Slack connector. Title it "eBay Store Ratings Sweep — all 5 accounts" with the month. Rank stores best to worst by 12-month positive %. One short block per store: feedback score, 12-mo positive %, 12-mo pos/neutral/neg counts, Top Rated yes/no, and month-over-month change. Add a plain-language warning line for any store with new negative/neutral feedback this month. End with a short "Bottom line" — which stores need attention and why. Plain language only; no tool names, file paths, or error text in the channel.

## Step 4 — Seller Standards (late shipment, defect rate, evaluation dates)

These are NOT in the report and must not be estimated. eBay retired `GetSellerDashboard`, and the REST `sell/analytics/v1/seller_standards_profile` endpoint returns 403 because the store tokens lack the `sell.analytics.readonly` scope. Until Joshua re-consents the 5 tokens with that scope (logged in the Open Items Register 2026-09-05), the report's Seller Standards section says UNAVAILABLE. Do not open Chrome to try to scrape Seller Hub — that is the behaviour this rewrite removed. If the tokens have since been re-consented, the script will need a small update to call that endpoint; note it in the run summary and move on.

Do all of this autonomously — no check-ins with Joshua.
