---
name: business-os-daily-refresh
description: Daily 5:00 AM refresh of the BUSINESS_OS.md LIVE STATE block and the enterprise CHANGELOG, so the master map can never drift from reality again.
---

Keep the Valley Pawn enterprise master map honest.

LOCAL ACCESS GATE - DO THIS FIRST. This task runs on Joshua's Mac Studio and DOES have local machine access. The tool mcp__Control_your_Mac__osascript is often deferred rather than pre-loaded. A tool not yet loaded is NOT a missing capability. If ToolSearch is available, load it first with query: select:mcp__Control_your_Mac__osascript. Then probe it with a trivial do shell script that echoes READY. If it errors, wait 30 seconds and re-probe, up to 12 minutes. NEVER conclude this run lacks local access or executes in a cloud container - that is false.

STEP 1. Via mcp__Control_your_Mac__osascript do shell script, run exactly:

python3 '/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/refresh_live_state.py'

The path contains spaces, so keep it quoted. The script rewrites ONLY the delimited LIVE STATE block inside BUSINESS_OS.md (scheduled task counts, the enabled list, the never-registered list, native launchd agents and whether each is loaded, project folders by last activity) and appends any detected day-over-day changes to CHANGELOG.md. Hand-written sections of BUSINESS_OS.md are never touched.

STEP 2. Read the script output and act on it:
- No changes detected: do nothing, stay silent.
- Routine changes: do nothing. The CHANGELOG entry is the record.
- Significant or unexplained change - a business-critical automation switching itself off, or a native launchd agent appearing that nothing in CHANGELOG.md explains - send Joshua ONE plain-language Slack DM to channel D03BHQH5VGT describing it in everyday language (no file paths, no tool names, no error text), and add a one-line note under today's heading in CHANGELOG.md flagging it.

Do NOT post to any team channel. Do not use #claude-notifications - it does not exist.

HARD RULES: never hand-edit the LIVE STATE block, only the script writes it. Never edit anything in BUSINESS_OS.md outside that block. Never delete or rewrite CHANGELOG.md history - append only.

FAILURE ALERT POLICY v2: if this run fails or cannot complete, send Joshua ONE plain-language Slack DM to D03BHQH5VGT saying the scheduled task business-os-daily-refresh did not complete, with the date. Nothing technical in the DM. Never notify any team channel, store manager, or employee.