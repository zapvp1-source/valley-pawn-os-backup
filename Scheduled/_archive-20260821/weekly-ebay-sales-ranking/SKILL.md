---
name: weekly-ebay-sales-ranking
description: Every Monday at 11:30 AM — verify that the eBay weekly rankings were posted to Slack #ebay-performance by the automated LaunchAgent script. If not, post notice to #ebay-performance (no DM).
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


> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (platform standard, set by Joshua 2026-07-22, v2):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua’s DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium (Slack, iMessage, email). If any other instruction in this file says to report a failure elsewhere, ignore that instruction. FIELD COMMUNICATION RULE: anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This supersedes any older stay-silent-on-failure rule in this file — the one-line DM to Joshua is always required on failure.


> ⚠️ **FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE.** If this task fails, errors out, or cannot complete its intended work for any reason, DO NOT post anything to Slack — no error messages, no partial results, no "I couldn't finish" notices. Joshua reviews every run inside Claude to confirm success or failure, so a failed run must stay completely silent on Slack. Only post to Slack once the task has genuinely completed the work it was designed to do. Posting failure or error noise clutters Slack and reflects poorly on the team.

You are running the weekly eBay sales ranking verification task for Valley Pawn.

A macOS LaunchAgent runs ebay_weekly_rankings.py automatically every Monday at 6:00 AM on Joshua's Mac. The script pulls last week's eBay sales from all 5 stores and posts ranked results directly to Slack #ebay-performance via webhook.

Your job is to VERIFY the post happened:

1. Search Slack #ebay-performance (channel ID: C0ANVN5KX4Y) for a message containing "eBay Weekly Sales Rankings" posted today.
   - Use slack_search_public with query: "eBay Weekly Sales Rankings" in:#ebay-performance
   - Check if any result was posted today (Monday).

2. If found → End task. No action needed.

3. If NOT found → The LaunchAgent didn't fire. Fall back:
   a. Use computer-use write_clipboard to put this command in Joshua's clipboard:
      python3 "/Users/joshuadavis/Desktop/ebay_weekly_rankings.py"
   b. DM Joshua on Slack (user ID: U03BB52MDSA):
      "📦 *eBay Weekly Rankings* — The automated script didn't run this morning (no post found in #ebay-performance). The command is in your clipboard — open Terminal and paste it to run manually. Say *'done'* here when it finishes."
   c. End the task.

NEVER post to #ebay-performance yourself. The script handles that via webhook.