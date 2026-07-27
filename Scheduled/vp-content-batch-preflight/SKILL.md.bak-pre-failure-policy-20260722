---
name: vp-content-batch-preflight
description: Sunday 9 PM ET pre-flight for Monday's vp-content-batch-weekly. Verifies MJ credits, Publer session, Bravo export freshness, brand studio integrity. Fixes what it can, only DMs Joshua for blockers only he can fix.
model: claude-sonnet-5
---

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