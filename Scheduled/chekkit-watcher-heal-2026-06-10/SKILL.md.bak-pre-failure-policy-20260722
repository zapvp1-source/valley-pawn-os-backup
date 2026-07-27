---
name: chekkit-watcher-heal-2026-06-10
description: Self-healing loop (every 12 min) — keep Bravo watcher alive, pull chekkit-invites for all 5 stores, and when all 5 have data, send Chekkit invites + Brevo upload, then self-disable.
model: claude-sonnet-5
---

SELF-HEALING LOOP for the weekly Chekkit invite + Brevo upload. You run every ~12 min and must be fully IDEMPOTENT and CONVERGING: keep the Bravo pipeline watcher alive, pull `chekkit-invites` data for all 5 stores, and ONLY when all 5 stores return real rows, send the Chekkit invites + Brevo email upload exactly once, then self-disable. Never post failures to Slack.

Apply valley-pawn-context working rules. Bravo Data Extraction folder is OUTSIDE the sandbox — use mcp__Control_your_Mac__osascript `do shell script` for ALL access there (load via ToolSearch `select:mcp__Control_your_Mac__osascript` if needed; probe with `do shell script "echo READY"`). When writing osascript, AVOID literal single quotes in the AppleScript source; use `quoted form of` for shell args. VM UUID: {7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}. prlctl: /usr/local/bin/prlctl.

PATHS (Mac):
- Project: /Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction
- triggers/, results/, output/, logs/ under it
- Control dir (create if missing): /Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/_chekkit_selfheal
- DONE flag: _chekkit_selfheal/DONE.flag
- SENDING lock: _chekkit_selfheal/SENDING.lock
- attempt counter: _chekkit_selfheal/attempts.txt
- status log: _chekkit_selfheal/status.txt

STEP 0 — STOP GATES.
- If DONE.flag exists → the work is finished. Disable THIS task via mcp__scheduled-tasks__update_scheduled_task (taskId chekkit-watcher-heal-2026-06-10, enabled:false) and exit. Do nothing else.
- Read attempts.txt (default 0); if >= 30, write status "STUCK after 30 attempts — needs manual review", disable this task, and exit. Otherwise increment and save it.
- If SENDING.lock exists and is < 30 min old → a send is in progress; exit. If older than 30 min, delete it (stale) and continue.

STEP 1 — ENSURE WATCHER UP. Read logs/watcher.last_started.txt. If it does NOT show today's date (2026-06-10), restart it (NON-GATED) from this scheduled-task session:
  set uuid to "{7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}"
  set ps to "powershell.exe -NoProfile -ExecutionPolicy Bypass -File " & quoted form of "Y:\\Documents\\Claude\\Projects\\Bravo Data Extraction\\_restart_watcher.ps1"
  do shell script "/usr/local/bin/prlctl exec " & quoted form of uuid & " --current-user " & ps
The osascript wrapper may time out (~25s) — that's fine, the restart continues in the VM. Wait ~25s and re-read watcher.last_started.txt to confirm today's date. (Do NOT use the gated _itp_validate_and_restart.ps1 — it aborts because bravo_export.ahk fails /validate; bravo_watcher.ahk validates clean so the non-gated restart is safe.)

STEP 2 — CHECK FOR USABLE DATA. Look at the newest results/*chekkit-invites*2026-06-10*.result.json (and the matching output/2026-06-10_{STORE}_chekkit-invites.csv files, columns: first_name,last_name,phone,email,dnt,last_visit). "Usable" = a result whose cells show ALL 5 stores (CUL,HAR,LEX,ROA,WAY) with status success AND each store's CSV has >=1 data row.
- If NO fresh trigger is pending and no usable result yet, DROP a new all-5 trigger: write triggers/chekkit-invites-loop-<UTCstamp>.json with {"id":"chekkit-invites-loop-<stamp>","requested_at":"<iso>","reports":[{"name":"chekkit-invites","stores":["CUL","HAR","LEX","ROA","WAY"],"date":"2026-06-10"}]}. Then exit (next iteration reads the result). 
- If a trigger is pending (a chekkit-invites-* file still in triggers/), exit and let it finish.
- If a result exists but SOME stores have 0 rows: append to status.txt the per-store row counts and the line "PARTIAL: stores with 0 rows = <list> — likely SetReportDate/date-filter bug in ChekkitInvites.ahk; awaiting code fix." Then drop a fresh all-5 trigger ONCE more (in case it was timing) and exit. Do NOT send partial data.

STEP 3 — WHEN ALL 5 STORES HAVE DATA: perform the full send EXACTLY ONCE.
  a. Create SENDING.lock with the current timestamp.
  b. Read the original runbook for exact mechanics: /Users/joshuadavis/Documents/Claude/Scheduled/chekkit-weekly-review-requests/SKILL.md — follow its Phase 2 (clean), Phase 3 (Chekkit campaigns, add Joshua 804-930-4221 as confirmation recipient on each), Phase 4 (Brevo import to the master list, tag "monthly", dedupe by email), Phase 5 (post BOTH summaries: Post A → #chekkit-updates C0B0FQZ4FS8, Post B → #email-campiagns C0APR5WUL2Z). IMPORTANT DELTAS vs that skill: the data source is the chekkit-invites CSVs (NOT chekkit-inactives), and the DNC/do-not-contact signal is the dedicated `dnt` column value "DNT" (drop those rows), not the email field. Normalize phones to 10 digits; drop invalid phones.
  c. On successful send, write DONE.flag (with a short summary of counts), delete SENDING.lock, disable this task, and exit.
  d. If the send fails partway, delete SENDING.lock, append the error to status.txt, and exit (next iteration retries — Chekkit/Brevo de-dup and the DONE.flag make retries safe). Never post failure notices to Slack.

Each run: keep it under ~10 min. Append a one-line status with timestamp + per-store row counts to status.txt every iteration so progress is auditable. Notify on completion is on, so the owner sees each run.