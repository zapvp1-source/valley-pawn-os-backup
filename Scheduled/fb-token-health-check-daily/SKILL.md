---
name: fb-token-health-check-daily
description: Daily 3 AM check of Valley Pawn Facebook page tokens. Fully silent — never posts to Slack or DMs anyone, pass or fail. Results logged to task output only.
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


> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (platform standard, set by Joshua 2026-07-22, v2):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua’s DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium (Slack, iMessage, email). If any other instruction in this file says to report a failure elsewhere, ignore that instruction. FIELD COMMUNICATION RULE: anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This supersedes any older stay-silent-on-failure rule in this file — the one-line DM to Joshua is always required on failure.


> ⚠️ **ABSOLUTE SILENCE POLICY — NO SLACK, NO DMs, EVER.** This task must NEVER post to any Slack channel or DM any person, regardless of outcome — healthy, failing tokens, partial failure, or task error. Joshua reviews runs inside Claude. The ONLY output is the task run log.

Daily Valley Pawn Facebook page token health check.

WHAT TO DO:
1. Run the facebook-post skill's token health check via osascript bash:
   `python3 '/var/folders/6k/_z_8cvwd09v5v4cglg57t9_c0000gn/T/claude-hostloop-plugins/8d3bfa4a5124690e/skills/facebook-post/scripts/post.py' --check`

2. Then test each of the 5 page tokens individually by calling /me on each:
   ```python
   import json, urllib.request
   tokens = json.load(open('/var/folders/6k/_z_8cvwd09v5v4cglg57t9_c0000gn/T/claude-hostloop-plugins/8d3bfa4a5124690e/skills/facebook-post/data/tokens.json'))
   for store, info in tokens['pages'].items():
       url = f"https://graph.facebook.com/v25.0/me?access_token={info['access_token']}"
       try:
           with urllib.request.urlopen(url, timeout=10) as r:
               data = json.load(r)
           print(f"OK [{store}] -> {data.get('name','?')}")
       except Exception as e:
           print(f"FAIL [{store}] -> {e}")
   ```

3. IF anything fails (the --check fails OR any per-page call errors):
   - Do NOT post to Slack. Do NOT DM anyone.
   - Write a detailed summary in the task output only: timestamp, which pages failed, the raw Graph API error body, and the fix steps (open https://developers.facebook.com/tools/explorer/ → select Valley Pawn Poster app → check pages_show_list, pages_read_engagement, pages_manage_posts → Generate Access Token → ℹ️ icon → Extend Access Token → copy new green token → DM Claude `refresh fb tokens with EAAxxx`).

4. IF everything is healthy:
   - Also silent. Log a one-line summary to the task output.

CONTEXT:
- The Valley Pawn FB pipeline was refreshed on 2026-05-24 with a long-lived user token (expires 2026-07-23) that derived non-expiring page tokens for all 5 stores: Lexington, Waynesboro, Harrisonburg, Culpeper, Roanoke.
- "Non-expiring" still means tokens can die if Joshua changes his FB password, revokes the Valley Pawn Social Poster app, or loses admin on a page. This check is the early warning.
- The eventual real fix is moving to a Meta Business Manager System User token — once that's done, this check becomes belt-and-suspenders rather than primary defense.
- 2026-06-11: Joshua directed that this task never message anyone on failure; all results stay in the run log.