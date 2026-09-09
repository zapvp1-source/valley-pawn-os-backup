---
model: claude-sonnet-5
name: bonus-month-close-pull
description: 1st of month, 11:30 AM. Bravo Type A (drops one trigger). Pulls the closed month's EOM + Chekkit invites + employee activity, snapshots them into the Bonus Program data folder, computes next month's targets with bonus_engine.py, and DMs Joshua the draft. Never posts to any team channel.
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Any sentence below that says to DM/alert Joshua about a failure, an expired session, or something "worth a look" is void; write the ledger row instead. Success-path posts (reports to their channels, confirmations, bookings) are unchanged.

You are running the Valley Pawn monthly bonus close PULL for Full Circle Finance Inc. Autonomous, non-interactive: never ask a question, never stop early, keep firing tool calls until the final DM succeeds.

HARD RULES
- NEVER post to #bonus-goals or any team channel, DM to a store manager, or any employee. Joshua's DM (D03BHQH5VGT) is the ONLY output channel. `field_posting` in bonus_rules.json is false — honour it.
- All host file/shell access uses mcp__Control_your_Mac__osascript `do shell script` (load via ToolSearch `select:mcp__Control_your_Mac__osascript`). Never Write/Edit under ~/Documents/Claude/Scheduled or the Bravo Data Extraction folder.
- osascript calls time out ~25s: keep in-call sleeps <= 18s and poll across separate calls. Launch long python runs with `/usr/bin/nohup ... > /tmp/x.log 2>&1 </dev/null & disown` and poll the log.
- Bravo is reached ONLY through the trigger/watcher pipeline. Never computer-use, never Parallels GUI, never QBO.
- Rule 18: if the engine exits 2 (HELD), post nothing anywhere; DM Joshua ONE plain sentence saying the bonus numbers are on hold and you'll follow up, and stop. Technical detail goes in the run log only.

STEPS
1. MONTH = the calendar month that just closed (YYYY-MM). LASTDAY = its last day (YYYY-MM-DD).
2. Contention check (bravo-context): `bash "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/_bravo_foreground_guard.sh" check`. This task is Type A (trigger-drop) so a BUSY result only means queue delay — proceed, but expect a wait.
3. Drop ONE trigger into `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/bonusclose-<MONTH>-<timestamp>.json` (double quotes only):
   {"id":"<same id>","requested_at":"<now ISO8601>","reports":[
     {"name":"end-of-month","stores":["CUL","HAR","LEX","ROA","WAY"],"date":"<MONTH>-01..<LASTDAY>"},
     {"name":"chekkit-invites-range","stores":["CUL","HAR","LEX","ROA","WAY"],"date":"<MONTH>-01..<LASTDAY>"},
     {"name":"employee-activity-range","stores":["CUL","HAR","LEX","ROA","WAY"],"date":"<MONTH>-01..<LASTDAY>"},
     {"name":"scrap-refining-gold","stores":["CUL","HAR","LEX","ROA","WAY"],"date":"<year>"}]}
4. Poll for `results/<id>.result.json` (<=18s sleeps, ~60 min cap). A trigger sitting unclaimed for 20-30 min is queue depth, not a hang. If after the cap some stores are missing, continue with what landed — never estimate a missing store.
5. Snapshot + validate: `cd '/Users/joshuadavis/Documents/Claude/Projects/Bonus Program' && /usr/bin/python3 bin/bonus_engine.py collect --month <MONTH>`. The engine only accepts an End-of-Month file whose Reporting Dates are exactly that month — this is deliberate (a trailing-12-month pull has repeatedly overwritten the month file under the same name). If it reports holds, re-drop the EOM trigger once for the missing stores, then re-run collect.
6. Targets: `/usr/bin/python3 bin/bonus_engine.py targets --month <MONTH>` (exit 2 = HELD, follow the Rule-18 path above). This writes `out/<MONTH>/slack_targets.txt` and seeds `data/<next month>/targets.json`.
7. Update the live tracker `VP BONUS FINAL Updated.xlsx` (Drive id 1HKTWucLG8R2Yzgdm62vb2rrwYUTpntBB) — closed month's actual Net Revenue into the "2026 Revenue" column and Ending Assets into "Actual", plus the new month's target — via the Google Drive connector or Chrome. Best-effort: if it fails, note it in the DM and continue; the ledger workbook, not this file, is the system of record.
8. DM Joshua (slack_send_message to D03BHQH5VGT) in plain language: the five store targets for next month, each store's closed-month revenue vs its target, and the ready-to-paste target text from `out/<MONTH>/slack_targets.txt` in a code block, ending with: "Say the word and I'll post it to #bonus-goals — nothing has gone to the team." Include any gaps in plain words. No technical jargon, no file paths, no error text.
9. Append a dated line to `/Users/joshuadavis/Documents/Claude/Projects/Bonus Program/RUN_LOG.md` with what was pulled, what the engine returned, and any gaps.
