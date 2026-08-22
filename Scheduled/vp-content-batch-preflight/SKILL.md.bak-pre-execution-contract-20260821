---
name: vp-content-batch-preflight
description: Sunday 9 PM ET pre-flight for Monday's vp-content-batch-weekly. Verifies MJ credits, Publer session, Bravo export freshness, brand studio integrity. Fixes what it can, only DMs Joshua for blockers only he can fix.
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


> **REPORTING POLICY:** Joshua sees NOTHING unless there's a blocker only he can fix. Claude self-heals via completion notification.

Pre-flight for tomorrow's Monday 2:02 AM ET `vp-content-batch-weekly` run. Run every check, log results to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn Studios/output/preflight_{YYYY-MM-DD}.json`, DM Joshua ONLY if a check fails that only he can fix.

## Checks (retry each 3x with exponential backoff)

### 1. Bravo inventory export freshness
```bash
ls -lt "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/" | grep inventory_export | head -1
```
Newest file must be <24h old. If stale → **DM Joshua** (only he can trigger the Bravo pipeline):
```
🔴 Bravo inventory export is stale (>24h). Monday's batch won't have fresh SKUs. Please run the Bravo Data Extraction pipeline before 2 AM.
```

### 2. Publer authenticated session
Navigate to `app.publer.com` via Chrome MCP. If redirected to login page, session expired.
- Try to auto-restore via saved cookies at `~/.vp-studio/publer-session.json`
- If auto-restore fails → **DM Joshua**:
```
🔴 Publer session expired — please open app.publer.com in Chrome and log in. Monday's batch depends on this session being live.
```

### 3. MJ fast-hours balance
Navigate to `midjourney.com/account` via Chrome MCP, scrape the "Fast Time Remaining" number.
- If <45 min → **DM Joshua**:
```
🔴 Midjourney fast hours low ({X} min remaining). Monday's batch needs ~30-40 min. Please top up before 2 AM.
```

### 4. Skill file integrity
Verify these files exist and contain the Publer-only rules (grep for `graph.facebook.com` — should return zero hits):
- `/Users/joshuadavis/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin/f6b75d02-cca9-4943-ad6e-88390a3f201d/823f6874-6252-4031-ae4e-a3c22d37598e/skills/vp-content-batch/SKILL.md`
- `/Users/joshuadavis/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin/f6b75d02-cca9-4943-ad6e-88390a3f201d/823f6874-6252-4031-ae4e-a3c22d37598e/skills/vp-hero-image/SKILL.md`
- `/Users/joshuadavis/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin/f6b75d02-cca9-4943-ad6e-88390a3f201d/823f6874-6252-4031-ae4e-a3c22d37598e/skills/vp-brand-studio/SKILL.md`

If any file is missing or contains `facebook-post`/`graph.facebook.com` references (indicating skill got reset by an update) → run the patch scripts in `/tmp/vp_publisher_patch.py` + `/tmp/vp_reel_publisher_patch.py` + `/tmp/vp_ai_text_patch.py` to re-apply. Silent to Joshua unless patcher fails.

### 5. Slack channels reachable
Confirm `#vp-studio-queue` and `#deal-of-the-week` are accessible via Slack MCP. If not (session-scoped auth issue) → LOG that the Monday runner should note "Slack MCP unavailable — fell back to Publer-only calendar staging" but do NOT DM Joshua (this is a known cron-context limitation).

### 6. Disk space
`df -h /Users/joshuadavis` — flag if <5GB free. DM Joshua if critical (<2GB).

### 7. Text-composite helper installed
Check `~/.vp-studio/scripts/compose_text_on_hero.py` exists + is executable + Pillow importable. If missing, re-run setup: `python3 ~/.vp-studio/vp_helper_setup.py` (kept in the outputs dir as backup). Silent.

## Output
Write full preflight report to `output/preflight_{YYYY-MM-DD}.json`. If any check triggered a Joshua-DM, list which. Completion notification tells Claude about non-Joshua-facing issues to fix in-session.

Fires Sunday 9 PM ET via cron `0 21 * * 0`.