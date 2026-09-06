---
name: unified-search-index-refresh
description: Nightly 3:30 AM — LAUNCH Joshua's unified-search index rebuild (refresh_hardened.sh) in the background and EXIT within 3 minutes. Verification moved to the separate `unified-search-verify` task at 4:50 AM (Phase 1 of SCHEDULED_TASK_RELIABILITY_PLAN.md, 2026-09-04) so this no longer holds one of the scheduler's 3 concurrency slots for 60+ minutes.
model: claude-haiku-4-5
---
This is an automated run of a scheduled task. The user is not present. Execute autonomously — no clarifying questions. Do NOT call `mcp__cowork__request_cowork_directory` (it stalls unattended). All host access is via `mcp__Control_your_Mac__osascript` (load with ToolSearch `select:mcp__Control_your_Mac__osascript` if deferred).

## Why this task is short now
Until 2026-09-04 this session babysat the refresh for 40–75 minutes, holding one of the scheduler's THREE concurrent-task slots the whole time (the platform limit — see `Valley Pawn OS/SCHEDULED_TASK_RELIABILITY_PLAN.md`). The refresh itself is a self-healing shell wrapper that does not need a Claude session watching it. So: launch, confirm it started, exit. The companion task `unified-search-verify` (4:50 AM) checks the result and does fix-forward if needed.

## Steps (target: done in under 3 minutes)
1. Guard against a double launch — via osascript:
   `do shell script "pgrep -fl 'refresh_hardened.sh|refresh.sh' || echo NONE"`
   If a refresh is already running (anything other than NONE), do nothing else and end the turn silently — the verify task will handle it.
2. Launch the hardened wrapper in the background, fully detached, exactly like this:
   `do shell script "(bash ~/Documents/Claude/Projects/Unified\\ Search/refresh_hardened.sh) > /tmp/usearch_task_run.log 2>&1 < /dev/null & echo launched"`
3. Confirm it started (one check, ~20 s later):
   `do shell script "sleep 15; pgrep -fl 'refresh_hardened.sh' | head -2; tail -c 300 ~/Documents/Claude/Projects/Unified\\ Search/refresh_hardened.log | tr '\\r' '\\n' | tail -3"`
   If a `refresh_hardened.sh` process is listed → launched OK. End the turn with one line: "unified-search refresh launched <timestamp>". No Slack post.
4. If nothing is running after step 3, retry step 2 ONCE. If still nothing, write one line to `~/Documents/Claude/Projects/Unified Search/launch_failures.log` via osascript (`echo "<date> launch failed" >> ...`) and end the turn. Do NOT DM Joshua from this task — the verify task owns all reporting.

## Constraints
- `refresh_hardened.sh` is the ONLY entry point — never invoke `refresh.sh` directly.
- Never modify `refresh.sh`, `refresh_hardened.sh`, or any index script from this task.
- Do not re-enable or delete `com.valleypawn.unified-search-refresh.plist.disabled-20260821-brokenTCC`.
- Never wait, poll, or sleep beyond step 3. Exiting fast IS the job.
