---
name: vp-publer-analytics-friday
description: Friday 4 PM ET — Publer API weekly performance digest: top/bottom 20% by engagement, writes weekly-adjustments.json for Monday's batch, DMs Joshua a one-line digest. Replaces the broken Meta Graph analytics loop.
model: claude-sonnet-5
---

This is an automated run of a scheduled task. The user is not present. Execute autonomously. End with <run-summary>one or two sentences</run-summary>.

⚠️ FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE. If the digest cannot be produced, stay silent on Slack; explain in the run-summary only (Claude self-heals via completion notification). Joshua gets exactly one DM, and only on success.

## Job
Close Valley Pawn's weekly content loop using PUBLER's analytics API (the Meta Graph API path is retired/blocked — never use it, never browser-fallback to instagram.com/facebook.com).

## Steps
1. Run the digest via the Control-your-Mac osascript tool:
   `do shell script "cd ~/Documents/Claude/Projects/'Refine Social Media' && python3 publer_weekly_digest.py 2>&1 | tail -15"`
2. The script pulls last-7-day post-level insights across all connected Publer accounts, ranks by engagement, identifies top/bottom 20%, classifies content types, and writes:
   - `friday_digests/friday_digest_{date}.md` (full report)
   - `weekly-adjustments.json` (Monday's vp-content-batch-weekly reads this — the adjust loop)
   - appends to `adjustments_log.jsonl` and `~/.vp-studio/lessons.md`
3. Its LAST stdout line starts with "DIGEST:". DM exactly that line (minus the "DIGEST: " prefix) to Joshua Davis on Slack (find him via user search), prefixed with "📊 Weekly social digest — ".
4. If the line says no insights were available (Publer analytics can lag 24-48h), do NOT DM Joshua — note it in run-summary only.
5. Sanity check: confirm weekly-adjustments.json was updated today (osascript: `do shell script "stat -f '%Sm' ~/Documents/Claude/Projects/'Refine Social Media'/weekly-adjustments.json"`). If not, treat as failure (silent).

Guardrails: Publer API only. No Meta Graph API. No instagram.com/facebook.com browsing. Do not modify the digest script during a run — if it errors, report in run-summary and let interactive Claude fix it.
