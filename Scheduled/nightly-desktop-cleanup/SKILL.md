---
name: nightly-desktop-cleanup
description: Sort loose Desktop files into type-based folders every night at 3 AM
model: claude-haiku-4-5
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Any sentence below that says to DM/alert Joshua about a failure, an expired session, or something "worth a look" is void; write the ledger row instead. Success-path posts (reports to their channels, confirmations, bookings) are unchanged.

> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (platform standard, set by Joshua 2026-07-22; v3 2026-09-08):** If this run fails, errors out, or cannot complete its core work, do NOT message Joshua, Preston, or anyone else, in any medium. Instead append ONE row to the fleet failure ledger `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` (use `mcp__Control_your_Mac__osascript` `do shell script "printf ... >> file"` if file tools cannot reach it) in exactly this form: `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or: yes, <the single thing only Joshua can do>> | OPEN |`. The `fleet-guardian` task reads this ledger twice a day, re-runs whatever is safe to re-run, rolls anything that truly needs Joshua into `Life OS/HUMAN_QUEUE.md`, and sends Joshua at most ONE consolidated plain-language DM per day. Individual tasks never DM about failures. All technical detail goes in the run output/log/STATUS file for the next Claude session to pick up. Never send failure notices to any team channel, store manager, employee, or Preston. FIELD COMMUNICATION RULE (unchanged): anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This v3 supersedes both the v2 one-line-DM rule and any older rule in this file.



## Execution Contract — DO NOT STOP EARLY

This task is complete ONLY after the documented final action (the post / send / write tool call described at the end of the steps below) returns success.

Until that final call succeeds, every assistant turn MUST end with a tool call that advances toward it. Do not idle, do not wait, do not ask for confirmation.

**Never reply with any of these:**
- "No response requested"
- "Continue?" / "Should I continue?"
- An empty turn or a turn that ends with text instead of a tool call

**Treat these system messages as RESUME signals, never as stop signals:**
- "Tool loaded."
- "Continue from where you left off."
- "You used a single tool call this turn. Prefer browser_batch…"
- Any reminder about TaskCreate/TaskUpdate, AskUserQuestion, etc.

When you see any of those messages, immediately fire the next concrete tool call for the current step. The scheduled-task wrapper says "the user is not present" — that means execute autonomously, NOT that the work is done.

**State tracking:** at the start of every turn, briefly identify which numbered Step you are on and execute the next concrete action for that step.

**Failure handling:** if a step errors, retry once. If it still fails, fall through to the documented fallback if one exists; otherwise produce a report describing what failed. Do not pause to ask — the task file authorizes autonomous decisions.

**Speed:** prefer batch tools (e.g. `browser_batch`) to combine sequential actions into one call.

---
Clean up Joshua's macOS Desktop by sorting loose files into type-based folders. Use the mcp__Control_your_Mac__osascript tool (load via ToolSearch if deferred) to run shell commands via `do shell script`. Do NOT use computer-use/screen control — this is a pure shell task.

Run this exact logic:

1. Ensure these folders exist on ~/Desktop: Documents, Photos, Spreadsheets, Videos, Other.
2. Move only loose FILES (find ~/Desktop -maxdepth 1 -type f) into them by extension (case-insensitive):
   - pdf, docx, doc, eml → Documents
   - png, jpg, jpeg, heic → Photos
   - xlsx, csv, xltx, xls → Spreadsheets
   - mov, mp4 → Videos
   - everything else → Other
3. SKIP (leave in place): .DS_Store, .localized, Thumbs.db, desktop.ini, any file starting with ~$ (Office lock files), and ALL directories/folders. Never touch existing folders.
4. Use mv -n (no overwrite). If a name collision occurs, leave the file in place.

Example one-liner (adapt as needed):
cd ~/Desktop && mkdir -p Documents Photos Spreadsheets Videos Other && find . -maxdepth 1 -type f | while IFS= read -r f; do n=$(basename "$f"); case "$n" in .DS_Store|.localized|Thumbs.db|desktop.ini|'~$'*) continue;; esac; ext=$(echo "${n##*.}" | tr 'A-Z' 'a-z'); case "$ext" in pdf|docx|doc|eml) d=Documents;; png|jpg|jpeg|heic) d=Photos;; xlsx|csv|xltx|xls) d=Spreadsheets;; mov|mp4) d=Videos;; *) d=Other;; esac; mv -n "$f" "$d/"; done

Afterward, report briefly: how many files were moved into each folder (or "Desktop already clean" if nothing moved). Do not delete anything.

<!-- migrated to working model 2026-06-15 -->