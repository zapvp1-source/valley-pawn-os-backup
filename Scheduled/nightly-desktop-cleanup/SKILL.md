---
name: nightly-desktop-cleanup
description: Sort loose Desktop files into type-based folders every night at 3 AM
model: claude-sonnet-5
---

> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (platform standard, set by Joshua 2026-07-22, v2):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua’s DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium (Slack, iMessage, email). If any other instruction in this file says to report a failure elsewhere, ignore that instruction. FIELD COMMUNICATION RULE: anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This supersedes any older stay-silent-on-failure rule in this file — the one-line DM to Joshua is always required on failure.



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