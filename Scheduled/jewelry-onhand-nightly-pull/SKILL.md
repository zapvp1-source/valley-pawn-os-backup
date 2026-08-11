---
name: jewelry-onhand-nightly-pull
description: Nightly 8:30 PM (Mon-Sat) — pull 5-store jewelry on-hand counts from Bravo inside the after-close freeze window, so they can be compared against the same night's manager PM count sheets.
model: claude-sonnet-5
---

Part 1 of 2 of Valley Pawn's nightly jewelry count reconciliation. Companion task `jewelry-onhand-nightly-compare` fires at 9:45 PM and does the analysis. Your only job: get a clean, complete 5-store jewelry on-hand pull from Bravo.

WHY THE TIMING MATTERS (this determines whether the run is valid at all):
Bravo's jewelry report is a LIVE on-hand query — no as-of-date capability, it always returns "right now." The manager's sheet is a physical case count taken at 6 PM close. Those two only line up if Bravo is queried while nothing is moving.

All 5 stores close at 6:00 PM and reopen at 10:00 AM, so 6 PM→10 AM is a nightly FREEZE WINDOW. You fire at 8:30 PM, inside it. That is what makes the numbers comparable. Earlier attempts that pulled during open hours and compared against a prior day's sheet produced meaningless deltas — that is the exact mistake this schedule exists to prevent. If you cannot run inside tonight's freeze window, do NOT pull anyway; report the miss and stop.

STORE-CLOSURE NUANCE — read before deciding what "complete" means:
- Culpeper (CUL): open Mon-Sat.
- Harrisonburg, Waynesboro, Lexington, Roanoke: open Mon, Tue, Thu, Fri, Sat — CLOSED WEDNESDAY.
On Wednesdays, only Culpeper traded and only Culpeper will have a fresh sheet tonight. Still pull all 5 stores (the other four's counts should be unchanged from Tuesday, which is itself a useful integrity check), but a Wednesday run is NOT incomplete just because four stores have no new sheet.

STEP 1 — Contention check (mandatory standing rule: never touch Bravo blind).
Bravo runs one shared login (FREE1) across every automation and hard-locks it per module.
- `ls "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/claimed/"` — compare file mtimes to now; anything claimed in the last ~30 min means Bravo is in use.
- Confirm tonight's earlier Bravo tasks have finished: daily-funds-verification (6:03 PM), funds-verification-watchdog (6:47 PM), asset-recovery-daily-refresh (7:17 PM), and jewelry-count-reconciliation (7:47 PM, which also pulls from Bravo). By 8:30 PM these are normally done — verify, don't assume.
- Check `logs/_health_gate_status.txt` for PASS.
If busy: wait and re-check up to 3 times at ~10 minute intervals. If still busy, STOP, do not force it, DM Joshua one plain line that tonight's jewelry count could not run. Never retry through a "FREE1 is busy" dialog.

STEP 2 — Drop the trigger.
Use osascript shell (the Write tool cannot reach this folder). Write to
/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/jewelry-onhand-<YYYY-MM-DD>.json :

{
  "id": "jewelry-onhand-<YYYY-MM-DD>",
  "requested_at": "<current ISO timestamp, -04:00 offset during EDT>",
  "reports": [
    {"name": "jewelry-case-counts", "stores": ["CUL","HAR","LEX","ROA","WAY"], "date": "<YYYY-MM-DD>"}
  ]
}

Confirm within ~60 seconds it moved to triggers/claimed/. If never claimed, the watcher may be down — DM Joshua one plain line and stop.

STEP 3 — Monitor hands-off. CRITICAL.
Tail logs/jewelry-onhand-<YYYY-MM-DD>.log periodically. Expect roughly 45-60 minutes for 5 stores.

DO NOT click, scroll, or interact with the Bravo window via computer-use while this runs — not even to diagnose a category that looks stuck or is retrying its report selection. On 2026-08-10 a manual click landed at the same instant the automation's own retry succeeded, and Culpeper's Rings was silently recorded as 25 when the true count was 644: no error, no crash, just a clean-looking wrong number. Read-only log tailing only. The handler has its own retry logic; let it work.

STEP 4 — Verify completeness and hand off.
When the log shows "Overall status", confirm all 5 CSVs exist for today (output/<YYYY-MM-DD>_<STORE>_jewelry-case-counts.csv) and every row has status=ok. Do not interpret or adjust the numbers — the 9:45 PM task does the analysis. Just make it unambiguous in your run output whether the pull was complete.

Failure policy: if this run fails or cannot complete, send Joshua exactly ONE plain-language Slack DM (channel D03BHQH5VGT) saying tonight's jewelry count did not complete. No technical detail in the DM — no error text, no file paths, no next steps. All technical detail goes in your run output for the next session.