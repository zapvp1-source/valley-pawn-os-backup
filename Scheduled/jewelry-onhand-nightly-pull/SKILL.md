---
name: jewelry-onhand-nightly-pull
description: Nightly 8:30 PM (Mon-Sat) — pull 5-store jewelry on-hand counts from Bravo inside the after-close freeze window, so they can be compared against the same night's manager PM count sheets.
model: claude-sonnet-5
---

Part 1 of 2 of Valley Pawn's nightly jewelry count reconciliation. Companion task `jewelry-onhand-nightly-compare` fires at 9:45 PM and does the analysis. Your only job: get a clean, complete 5-store jewelry on-hand pull from Bravo.

## STEP 0 — OPEN-STORES GATE (Joshua, 2026-08-12). Do this before anything else.

Only pull stores that ACTUALLY TRADED TODAY. A store that was closed all day has no new
count sheet, so pulling it produces a number with nothing to compare it against. Do not
pull closed stores "for an integrity check" — Joshua's instruction is to skip them.

Store hours:
- Culpeper (CUL): open Mon-Sat.
- Harrisonburg (HAR), Waynesboro (WAY), Lexington (LEX), Roanoke (ROA):
  open Mon, Tue, Thu, Fri, Sat. CLOSED WEDNESDAY.
- All 5 closed Sunday.

So the store list for tonight is:
- Sunday                      -> NOBODY IS OPEN. Skip the entire run. Pull nothing, post
                                 nothing, DM nothing. This is a correct no-op, not a failure.
- Wednesday                   -> ["CUL"] only.
- Mon, Tue, Thu, Fri, Sat     -> ["CUL","HAR","LEX","ROA","WAY"]

Get the real weekday first — do not assume:
    date '+%A %Y-%m-%d'
via mcp__Control_your_Mac__osascript. Use that result to build the store list, and use that
same list everywhere below (the trigger JSON, the completeness check, and your run output).
"COMPLETE" means every OPEN store returned a count. It does not mean five stores.

═══ RULE 0 — NEVER REQUEST FOLDER ACCESS. THIS KILLED THE FIRST TWO RUNS. ═══
Do NOT call `mcp__cowork__request_cowork_directory` under any circumstances, and do not use the Read/Write/Edit tools for anything under /Users/joshuadavis/Documents/. That tool opens an interactive approval prompt. You run unattended at 8:30 PM with nobody at the keyboard, so the prompt times out and the entire run aborts having done nothing. That is exactly what happened on 2026-08-10: both nightly tasks fired on time, sat on a folder-permission prompt for ~30 minutes, then died silently without pulling anything.

You do not need folder access. Reach EVERY file — read or write, any path — through `mcp__Control_your_Mac__osascript` running shell commands (cat, ls, printf, python3). That is how the other unattended Bravo tasks (daily-funds-verification, daily-items-to-price, jewelry-count-reconciliation) do all their file work, and it never prompts. If a path seems unreachable, the answer is always another osascript shell command, never a folder request.

Two osascript quirks: the wrapper dies after ~25 seconds, so never chain sleeps longer than ~18s in one call (poll with repeated short calls instead); and a shell command whose last stage exits non-zero (e.g. grep with no match) makes the call throw, so append `|| true` where that's possible.

WHY THE TIMING MATTERS (this determines whether the run is valid at all):
Bravo's jewelry report is a LIVE on-hand query — no as-of-date capability, it always returns "right now." The manager's sheet is a physical case count taken at 6 PM close. Those two only line up if Bravo is queried while nothing is moving.

All 5 stores close at 6:00 PM and reopen at 10:00 AM, so 6 PM→10 AM is a nightly FREEZE WINDOW. You fire at 8:30 PM, inside it. That is what makes the numbers comparable. Earlier attempts that pulled during open hours and compared against a prior day's sheet produced meaningless deltas — that is the exact mistake this schedule exists to prevent. If you cannot run inside tonight's freeze window, do NOT pull anyway; report the miss and stop.

STORE HOURS: see STEP 0 above — pull OPEN stores only.

STEP 1 — Contention check (mandatory standing rule: never touch Bravo blind).
Bravo runs one shared login (FREE1) across every automation and hard-locks it per module.
- Via osascript: `ls -la "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/claimed/"` — compare file mtimes to now; anything claimed in the last ~30 min means Bravo is in use.
- Confirm tonight's earlier Bravo tasks have finished: daily-funds-verification (6:03 PM), funds-verification-watchdog (6:47 PM), asset-recovery-daily-refresh (7:17 PM), jewelry-count-reconciliation (7:47 PM). By 8:30 PM these are normally done — verify, don't assume.
- RUN the health gate, do not just read its status file. The status file is written by the LAST
  gate run and is routinely hours stale, so reading it proves nothing. Execute:
      bash "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/bravo_health_gate.sh"
  It exits 0 = PASS (Bravo verified on a Dashboard) and 1 = FAIL. It escalates on its own:
  start the VM, bounce a dead guest agent, relaunch Bravo, and finally restart the VM. Give it a
  few minutes (poll with short osascript calls, never one long sleep). Only drop the trigger on
  exit 0.
  WHY THIS EXISTS (2026-08-11): asset-recovery-daily-refresh at 7:17 PM failed a password submit
  during the Lexington store switch and left Bravo parked on the LEX login screen. The auth circuit
  breaker correctly stopped that task, but nothing un-wedged Bravo. Every recovery attempt for the
  next 13 hours re-submitted the password into the same dead screen and timed out — the state only
  cleared when the health gate restarted the VM at 8:19 AM. Your 8:30 PM run was the victim: 6
  failed recovery attempts, all 5 stores skipped, zero data. Running the gate first turns that
  13-hour outage into a ~3-minute VM restart.
If busy: wait and re-check up to 3 times at ~10 minute intervals. If still busy, STOP, do not force it, DM Joshua one plain line that tonight's jewelry count could not run. Never retry through a "FREE1 is busy" dialog.

STEP 2 — Drop the trigger (via osascript, e.g. printf redirected to the file).
Write to /Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/jewelry-onhand-<YYYY-MM-DD>.json :

{
  "id": "jewelry-onhand-<YYYY-MM-DD>",
  "requested_at": "<current ISO timestamp, -04:00 offset during EDT>",
  "reports": [
    {"name": "jewelry-case-counts", "stores": <OPEN STORES FOR TODAY from STEP 0 — e.g. ["CUL"] on a Wednesday>, "date": "<YYYY-MM-DD>"}
  ]
}

Confirm within ~60 seconds it moved to triggers/claimed/. If never claimed, the watcher may be down — DM Joshua one plain line and stop.

STEP 3 — Monitor hands-off. CRITICAL.
Tail logs/jewelry-onhand-<YYYY-MM-DD>.log periodically via osascript. Expect roughly 10-12 minutes per store (so ~10 min on a Wednesday, ~50 min on a full day).

DO NOT click, scroll, or interact with the Bravo window via computer-use while this runs — not even to diagnose a category that looks stuck or is retrying its report selection. On 2026-08-10 a manual click landed at the same instant the automation's own retry succeeded, and Culpeper's Rings was silently recorded as 25 when the true count was 644: no error, no crash, just a clean-looking wrong number. Read-only log tailing only. The handler has its own retry logic; let it work.

STEP 4 — Verify completeness and hand off.
When the log shows "Overall status", confirm a CSV exists for every OPEN store from STEP 0 (not necessarily 5) (output/<YYYY-MM-DD>_<STORE>_jewelry-case-counts.csv) and every row has status=ok. Do not interpret or adjust the numbers — the 9:45 PM task does the analysis. Just make it unambiguous in your run output whether the pull was complete.

Failure policy: if this run fails or cannot complete, send Joshua exactly ONE plain-language Slack DM (channel D03BHQH5VGT) saying tonight's jewelry count did not complete. No technical detail in the DM — no error text, no file paths, no next steps. All technical detail goes in your run output for the next session.