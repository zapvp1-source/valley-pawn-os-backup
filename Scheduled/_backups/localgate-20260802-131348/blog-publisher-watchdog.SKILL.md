---
name: blog-publisher-watchdog
description: Mon & Thu 2 PM ET — verify the valley-pawn-blog-publisher actually published a new post to thevalleypawn.com that day; DM Joshua on Slack if it didn't. Silent on success.
model: claude-haiku-4-5
---

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