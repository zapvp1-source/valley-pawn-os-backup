---
name: monthly-ebay-ratings-sweep
description: Monthly (1st, 10 AM ET) — sweep public eBay feedback profiles for all 5 Valley Pawn store accounts, rank by 12-month positive %, post digest to #ebay-performance, save monthly doc, compare to prior month. Migrated from cloud 2026-08-21.
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

This is an automated run of a scheduled task. The user is not present. Execute autonomously. End with <run-summary>one or two sentences</run-summary>.

> **MIGRATION NOTE (2026-08-21):** This task was moved from a claude.ai cloud scheduled task to this local task at Joshua's direction ("all cloud tasks should be moved to local"). The retired cloud trigger is disabled and will be deleted after this task's first clean local runs. Local tool names apply here: `mcp__Control_your_Mac__osascript`, `mcp__Control_Chrome__*`, `mcp__Filesystem__*` — never `mcp__remote-devices__*` (that prefix only exists in cloud sessions).

Run the monthly eBay ratings sweep for Valley Pawn's 5 eBay store accounts and post the results to Slack.

ACCOUNTS (all public eBay usernames):
- Roanoke: valley_pawn_roanoke
- Culpeper: valley_pawn_culpeper
- Waynesboro: valley_pawn_waynesboro
- Harrisonburg: valley_pawn_harrisonburg
- Lexington: valley_pawn_lexington

STEPS:
1. For each account, load its public feedback profile at https://www.ebay.com/fdbk/feedback_profile/<username> . NOTE: WebFetch is blocked by eBay's robots.txt on these pages — use the local Chrome tools (`mcp__Control_Chrome__open_url` + `execute_javascript` reading document.body.innerText) instead. From each page capture: feedback score, 12-month positive %, the 1-month/6-month/12-month positive/neutral/negative counts, and any Top Rated Seller badge.
2. Also open https://www.ebay.com/sh/performance/dashboard for whichever account Chrome is logged into and note the internal seller level (Top Rated / Above Standard / Below Standard) and its metrics. If not reachable, skip without failing.
3. Post ONE formatted message to the Slack channel #ebay-performance (channel ID C0ANVN5KX4Y) via the Slack connector: title it "eBay Store Ratings Sweep — all 5 accounts" with the month, rank stores best to worst by 12-month positive %, one block per store with feedback score, positive %, 12-mo pos/neutral/neg counts, Top Rated badge if present, and a warning line for any account with new negative/neutral feedback in the past month. End with a short "Bottom line" of priorities (e.g., accounts below standard, feedback needing replies).
4. Compare against last month's sweep if a prior doc exists in the "Online Store" Claude project (claude/online-sales-status-*.md or a monthly sweep doc) and note rating changes. Then save/update a doc in that project named claude/ebay-ratings-sweep-<YYYY-MM>.md with this month's numbers.

Do all of this autonomously — no check-ins with Joshua. Post whatever data you can get and note anything skipped.
