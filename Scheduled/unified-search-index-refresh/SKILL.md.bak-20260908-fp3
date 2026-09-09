---
name: unified-search-index-refresh
description: Nightly 3:30 AM — rebuild Joshua's unified-search index (Mail, Drive, iMessage, Notes, Reminders, Photos OCR, stats) via the self-healing refresh_hardened.sh wrapper. Replaces the broken native launchd agent (TCC-blocked). Hardened 2026-08-21 — retries and stale-lock reclaim are built into the wrapper; a failure DM is only sent after ALL self-healing is exhausted.
model: claude-sonnet-5
---

This is an automated run of a scheduled task. The user is not present to answer questions. Execute autonomously — no clarifying questions. Only take "write" actions this file specifically asks for. FIX-FORWARD (Rule 15): if something breaks mid-run, the job is to overcome it in-run, not to report it.

## Background
This task replaces `com.valleypawn.unified-search-refresh`, a native launchd agent that failed every run with `Operation not permitted` (macOS TCC blocks launchd-invoked bash from `~/Documents` without Full Disk Access). The broken plist is parked as `com.valleypawn.unified-search-refresh.plist.disabled-20260821-brokenTCC` — never re-enable it.

**Hardened 2026-08-21** after the first Cowork run hit two snags that are now handled automatically:
1. A refresh attempt died silently mid-files-step (parent killed — likely memory pressure — workers threw BrokenPipe, no error, no done marker). An identical retry succeeded. → `refresh_hardened.sh` now retries up to 3× and reclaims the stale lock a SIGKILL'd run leaves behind.
2. The photos step silently failed on ~97% of new screenshots (edited screenshots export as `<uuid>_edited.jpeg`, old code only matched `<uuid>.*`). Fixed in `photosindex.py` the same day.

## What to do

1. **Launch the hardened wrapper in the BACKGROUND** via `mcp__Control_your_Mac__osascript`. A foreground call WILL fail — the osascript tool times out at ~30s and the refresh takes 20–70+ minutes. Use exactly this pattern (fully-redirected backgrounded subshell, so the tool call returns instantly):
   ```
   do shell script "(bash ~/Documents/Claude/Projects/Unified\\ Search/refresh_hardened.sh) > /tmp/usearch_task_run.log 2>&1 < /dev/null & echo launched"
   ```

2. **Poll instead of blocking.** Between polls, sleep in your sandbox shell (`sleep 170` chunks — the osascript tool itself can't sleep more than ~25s). Every few minutes:
   ```
   do shell script "tail -c 400 ~/Documents/Claude/Projects/Unified\\ Search/refresh_hardened.log | tr '\\r' '\\n' | tail -5"
   ```

3. **Time budget: up to 75 minutes.** Normal-night runs are ~20–40 min (the mail scan alone walks 300k+ messages). Known-slow-but-fine behavior — do NOT treat these as hangs:
   - Mail scan prints progress every 3000 messages; long gaps early are buffering.
   - `remindersindex.py` can sit 10+ minutes at 0% CPU on `fetching list '...'` — Reminders AppleScript is just that slow. It finishes.
   If in doubt whether it's alive: `ps aux | grep -E 'usearch|msgindex|notesindex|remindersindex|photosindex|refresh'`.

4. **Success test (Rule 12 — verify against output, never exit codes):** `refresh_hardened.log` contains `=== hardened success on attempt N ===` (the wrapper only prints that after seeing refresh.sh's own `=== done <timestamp> ===` marker). Also confirm `stats.txt` in the same folder has today's mtime.

5. **If it completed cleanly:** silent success — no Slack post. Note counts from `stats.txt` in your final turn.

6. **If the wrapper printed `=== hardened FAILED after 3 attempts ===`:** the automatic self-healing is exhausted, but YOUR job is still fix-forward. Read the log, identify the root cause, and if it is surgically fixable in-run (a bad filename match, a stale lock the wrapper somehow missed, a full disk, a crashed helper process), fix it and relaunch the wrapper once more. Only if that ALSO fails: send ONE plain-language Slack DM to Joshua (channel `D03BHQH5VGT`): "⚠️ Scheduled task \"unified-search-index-refresh\" did not complete — <date>." Nothing technical in the DM; full detail goes in your final report only. Never post failure detail to any team channel.

7. **Light self-check:** if the run claims success but `stats.txt` mtime is older than 36h, flag the discrepancy in your report (silent no-op risk) — not fatal, just note it.

## Constraints
- `refresh_hardened.sh` is the ONLY entry point — do not invoke `refresh.sh` directly (it has no retry/lock-reclaim and a bare foreground call times out the tool).
- Additive only: never modify `refresh.sh`. Index scripts (`usearch.py`, `photosindex.py`, etc.) may receive surgical bug fixes when a run exposes a defect (fix-forward), but log any such fix in the Valley Pawn OS CHANGELOG before ending the turn.
- Do not re-enable or delete the disabled `.plist.disabled-20260821-brokenTCC` file.
- This task's only job is running the refresh reliably; interpreting search results is the `unified-search` skill's job.
