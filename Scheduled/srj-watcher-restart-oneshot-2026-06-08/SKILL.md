---
name: srj-watcher-restart-oneshot-2026-06-08
description: One-shot watcher restart to activate SafeRegisterJournal CS-toggle patch (mirrors monday-bravo-combined-run preflight Check 2 path).
model: claude-sonnet-5
---

One-shot job: restart the Bravo watcher so it picks up the patched SafeRegisterJournal.ahk handler, then verify it took.

CONTEXT
- Patched handler is on disk at /Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/reports/SafeRegisterJournal.ahk. Backup at SafeRegisterJournal.ahk.bak-pre-cs-toggle-2026-06-08.
- The running watcher has the OLD code in memory (#Include compiles at script start).
- A prior session tried prlctl exec from an interactive osascript shell and it hung on terminal grab (BRAVO_KNOWN_ISSUES.md). Scheduled-task sessions run prlctl successfully (monday-bravo-combined-run Check 2 does this every Monday).

STEPS
1. Read /Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/logs/watcher.last_started.txt and remember the timestamp on line 1.
2. Run via osascript do shell script:
   /usr/local/bin/prlctl exec '{7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}' --current-user powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'Y:\Documents\Claude\Projects\Bravo Data Extraction\_restart_watcher.ps1'
   This is the canonical restart pattern from Scheduled/monday-bravo-combined-run/SKILL.md Check 2. The .ps1 creates Windows scheduled tasks to map Y: and launch AHK in joshuadavis's interactive session, so the AHK process runs in the right context.
3. Sleep 15 seconds, then read watcher.last_started.txt again. The line-1 timestamp should be NEWER than what you saw in step 1. If not, sleep another 15s and try once more. If still unchanged, post failure to Slack DM U03BB52MDSA with the prlctl output and stop.
4. On success: drop a single-store smoke trigger at /Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/srj-cs-fix-postrestart-2026-06-08T14-50-00.json with body:
   {"id": "srj-cs-fix-postrestart-2026-06-08T14-50-00", "requested_at": "2026-06-08T14:50:00-04:00", "reports": [{"name": "safe-register-journal", "stores": ["WAY"], "date": "2026-06-07"}]}
5. Poll every 30s for up to 8 min for /Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/results/srj-cs-fix-postrestart-2026-06-08T14-50-00.result.json.
6. When result lands, read the corresponding log file at logs/srj-cs-fix-postrestart-2026-06-08T14-50-00.log and grep for "[pre-export] Continuous Scrolling". Two outcomes worth reporting:
   - SUCCESS WITH CS LINE: post to Slack DM U03BB52MDSA — "SRJ CS-toggle patch is LIVE — saw '[pre-export] Continuous Scrolling ... post-toggle state = 0' in the log, cell SUCCESS." Patch confirmed.
   - SUCCESS WITHOUT CS LINE: rare — means CS was already off. Still a working cell. Note that the post-toggle line was absent.
   - FAILURE: include the last 20 lines of the log + the result.json.
7. Also: delete the leftover trigger /Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/srj-cs-fix-smoke-2026-06-08T14-27-00.json if it's still sitting unclaimed at top-level (a prior session dropped it before the watcher died). Use osascript do shell script "rm -f '...'" — never the Write tool, the pipeline folder is outside this task's sandbox.

OUTPUT
Post the final result as a Slack DM to U03BB52MDSA. Single message, concise — what happened, whether the patch is live, what to do next if not.