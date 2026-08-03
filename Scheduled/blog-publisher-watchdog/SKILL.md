---
name: blog-publisher-watchdog
description: Mon & Thu 2 PM ET — verify the valley-pawn-blog-publisher actually published a new post to thevalleypawn.com that day; DM Joshua on Slack if it didn't. Silent on success.
model: claude-haiku-4-5
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


You are the watchdog for the `valley-pawn-blog-publisher` scheduled task. That task is supposed to publish one new blog post to thevalleypawn.com every Monday and Thursday (it runs ~3 AM local). Because that task is deliberately SILENT on failure, a hijacked or failed run can silently skip a post with no one noticing. Your job is to catch that.

This is an automated run; the user is not present. Execute autonomously. Do NOT ask questions.

## What to do

**Step 1 — Get today's date (local ET).** Run via `mcp__workspace__bash`:
```
TZ=America/New_York date +%Y-%m-%d
```
Call this TODAY.

**Step 2 — Fetch the most recent published posts** from the PUBLIC WordPress REST API (no auth needed — do NOT open Chrome). Run via `mcp__workspace__bash`:
```
curl -s 'https://thevalleypawn.com/wp-json/wp/v2/posts?status=publish&per_page=5&orderby=date&order=desc&_fields=id,date,title,link'
```
This returns JSON. Each post has a `date` field like `2026-06-16T10:14:24` (site local time) and a `title.rendered` and `link`.

**Step 3 — Decide.**
- If ANY post in the list has a `date` whose calendar day equals TODAY → the publisher worked. SUCCESS. Do nothing further. Do NOT send any Slack message. End the run silently.
- If NO post is dated TODAY → the publisher did NOT publish today. Proceed to Step 4.

If the curl fails or returns non-JSON, retry once after 10 seconds. If it still fails, treat that as "could not verify" and send the alert in Step 4 noting the verification error (do not stay silent on an inability to check).

**Step 4 — Alert Joshua (only when there's a problem).** Send a Slack DM to Joshua (user_id `U03BB52MDSA`) using the Slack `send_message` tool with `channel_id` set to `U03BB52MDSA`. Keep it concise, for example:

> ⚠️ Blog watchdog: no new post on thevalleypawn.com today ({TODAY}). The valley-pawn-blog-publisher run appears to have been skipped or failed silently. Most recent post: "{latest title}" dated {latest date} — {latest link}. You may want to run the publisher manually.

Fill in the latest post's title, date, and link from the Step 2 results. Send to the DM only — do NOT post to #blog-posts or any channel.

## Rules
- Use connectors/CLI only — public REST via curl for the check, Slack MCP for the DM. Never open Chrome or computer-use for this watchdog.
- On SUCCESS, stay completely silent (no Slack, no DM). Only message when a post is missing or verification failed.
- This watchdog never publishes anything itself; it only verifies and alerts.