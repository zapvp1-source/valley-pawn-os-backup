---
name: bravo-prestaging-7am
model: sonnet
description: Bravo pre-staging relaunch + verification before the 7 AM pipeline exports (Type C — direct process control, foreground-guarded as of 2026-08-13)
---

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
---
name: bravo-prestaging-7am
description: Bravo pre-staging relaunch + verification before the 7 AM pipeline exports (Type C — direct process control, foreground-guarded)
---

Run Bravo pre-staging for the 7 AM pipeline exports. This task runs on the user's computer and has full access to Parallels and osascript (use the mcp__Control_your_Mac__osascript tool, or equivalent osascript MCP tool if the name differs).

Steps:
0. CONTENTION CHECK — MANDATORY, added 2026-08-13 after this task was found to force-relaunch (kill + restart) Bravo with zero check for an in-flight trigger, which could kill a mid-transaction GL export or any other trigger mid-run. Run via osascript "do shell script":
bash "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/_bravo_foreground_guard.sh" check
- If it prints "CLEAR" (exit 0): immediately acquire the flag before doing anything else —
  bash "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/_bravo_foreground_guard.sh" acquire bravo-prestaging-7am
  — then proceed to step 1.
- If it prints "BUSY:<reason>" (exit 1): Bravo is already up and mid-work (a recent trigger claim/result, or another task holding the foreground flag). That means this task's actual goal — Bravo being alive and staged — is already satisfied, so a relaunch is both unnecessary and dangerous (it would kill whatever is running). Do NOT relaunch. SILENT SUCCESS — skip straight to step 7 (do not post to Slack, do not message Joshua, do not retry).

1. Execute the relaunch script via prlctl. Use an AppleScript "do shell script" call (NOT a shell command that itself invokes osascript -e with nested quoting — just pass the shell command directly as the script argument to the osascript tool, escaping double quotes as \" and backslashes as \\ within the AppleScript string). The shell command to run is:
/usr/local/bin/prlctl exec '{7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}' --current-user powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'Y:\Documents\Claude\Projects\Bravo Data Extraction\_relaunch_bravo_and_watcher.ps1'
Wrap it as: do shell script "<command with internal double quotes escaped as \" and backslashes escaped as \\>" with timeout 120
2. Wait 90 seconds for Bravo to launch.
3. Verify both Bravo.exe and dfsvc.exe are running via prlctl. Shell command:
/usr/local/bin/prlctl exec '{7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}' --current-user powershell.exe -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'Bravo.exe' -or $_.Name -eq 'dfsvc.exe' }"
Wrap similarly as a "do shell script ... with timeout 60" AppleScript call, being careful with the nested double quotes around the PowerShell -Command argument (escape them as \" ) and the $_ variable references (no special AppleScript escaping needed for $, but make sure the PowerShell single/double quote structure survives — using \" for the outer PowerShell string boundaries).
4. If both processes are running → SILENT SUCCESS (do not post to Slack, do not message Joshua). Proceed to step 7 (release the guard).
5. If NOT running → wait 60 seconds, retry the relaunch exactly once (repeat step 1), then verify again (step 3).
6. If still not running after the retry → send a Slack DM to Joshua (channel_id D03BHQH5VGT) via the Slack MCP send-message tool:
"⚠️ Bravo pre-staging failed — 2 relaunch attempts did not bring up Bravo.exe/dfsvc.exe. Today's 7 AM pipeline exports and daily-loan-inventory-text may fail. Check the VM desktop directly. (This matches the 2026-07-21 and 2026-07-23 failure mode — not yet understood.)"
Then proceed to step 7 regardless of outcome.
7. RELEASE THE GUARD — always run this last, whether this run relaunched, silent-succeeded, or failed (skip only if step 0 itself returned BUSY, since in that case you never acquired it):
bash "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/_bravo_foreground_guard.sh" release bravo-prestaging-7am
8. Do not modify any files other than what the guard script itself writes. This task only runs the existing _relaunch_bravo_and_watcher.ps1 script (when clear to do so) and reports outcome. Follow the Valley Pawn Failure Alert Policy v2: on failure, send ONE plain-language Slack DM to Joshua (D03BHQH5VGT) only — never post to any team/store channel. On success or on a BUSY silent-skip, do nothing (no Slack post).