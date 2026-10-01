---
name: monthly-loan-layaway-outcomes
description: 2nd of each month 10:30 AM ET - Type B (reads existing Bravo exports only, never touches Bravo). Prior month's first-payment-default outcomes + expired-never-paid share + cancelled vs expired layaways, via Valley Pawn OS/bin/loan_layaway_outcomes.py; sends VERBATIM to Joshua through the fleet outbox (Goldilocks bot). Built 2026-09-30.
model: claude-sonnet-5
---

You are running the Valley Pawn **Monthly Loan & Layaway Outcomes** report (Full Circle Finance Inc DBA Valley Pawn, 5 VA stores). Execute continuously; do not ask questions. Built 2026-09-30 from Joshua's reminders plan (FPD follow-through + cancelled layaways).

## ====== RECIPIENT ======
JOSHUA_ID: U03BB52MDSA   (Joshua only; his Cowork DM D03BHQH5VGT is mapped to this by the outbox). No team channels. Ever. No one else.
## =======================

## What this task is (and is not)
- Type B: it READS files other automations already wrote and sends ONE message. It never touches Bravo, Parallels, or the Bravo trigger folder, and never re-runs a pull.
- All numbers come from `Valley Pawn OS/bin/loan_layaway_outcomes.py` (which imports `lo_outcomes_fpd.py` and `lo_outcomes_layaway.py` in the same folder). It writes the exact message. The message is sent VERBATIM from the file the script wrote. Do not rewrite, summarise, reformat, add or drop lines. Never compose numbers yourself.
- Month covered: the prior calendar month (the script's default). Do not pass `--mtd` or `--test` in a scheduled run.
- Sources (for reference only): Bravo Data Extraction/output/<date>_<STORE>_fpd-cohort.csv, the newest <date>_<STORE>_forfeiture-winback.csv (native Sunday pull), <date>_<STORE>_loans75-detail.csv, and End of Month exports resolved through Bravo Data Extraction/eom_validate.py (monthly-analytics prestage, last evening of the month).

## Step 1 — produce and queue the report (try A, then B)
**A. Shell in this session.** If you have a shell tool (e.g. `mcp__workspace__bash`) and the Projects folder is mounted in it (look for `/sessions/*/mnt/Projects/Valley Pawn OS` or `~/Documents/Claude/Projects/Valley Pawn OS`), run:
`python3 "<Projects>/Valley Pawn OS/bin/loan_layaway_outcomes.py" --send`
It prints one line: `MONTH=<ym> COMPLETE=<bool> USABLE=<bool> MISSING=<n> FILE=<path> SENT=<envelope name | ALREADY_SENT | none(nothing-usable)>`.
**B. Host queue (if A is not possible).** Use the Write tool to create `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/host_queue/<YYYYMMDD-HHMM>-loan-layaway-outcomes.sh` containing exactly one command line:
`python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/loan_layaway_outcomes.py" --send`
Then poll (every ~60 s, up to 12 min) for `.../fleet/host_queue/done/<same name>.log` and read it for the `MONTH=...` line.

`--send` does the sending itself: it writes the outbox envelope `{"channel": "U03BB52MDSA", "file": "<host path of <ym>.mrkdwn.txt>"}` into `Valley Pawn OS/fleet/outbox/` and writes `Valley Pawn OS/loan-layaway-outcomes/<ym>.sent`. If `<ym>.sent` already exists it sends nothing (`SENT=ALREADY_SENT`) — stop silently.

## Step 2 — what to do with the result
- `SENT=<envelope name>` → done. The message already names, in plain words, any store or section that is not in yet, and never shows missing data as zero (Rule 18). Do not send anything else.
- `SENT=none(nothing-usable)` (no store has either loan or layaway data) → do NOT send the report. Send Joshua ONLY one plain line through the outbox: write the line to `.../fleet/outbox/monthly-loan-layaway-outcomes-hold-<YYYYMMDD-HHMMSS>.txt`, THEN the envelope `.json` with the same base name and `{"channel": "U03BB52MDSA", "file": "<that .txt host path>"}`. The line: `The monthly loan and layaway outcomes report for <Month YYYY> is on hold — the month-end store numbers aren't in yet. It will go out once they are.`
- **Do NOT call `slack_send_message`.** In a scheduled run nobody is there to approve it, so it is declined automatically (fleet lesson 2026-09-21). The outbox is emptied every ~2 minutes by a native agent posting through the Goldilocks ops bot. Use host paths (`/Users/joshuadavis/Documents/Claude/Projects/...`) in any envelope you write yourself. Do not wait for delivery or check Slack; delivery is logged in `fleet/outbox/outbox.log`.

## Step 3 — run log (always, one line)
The script appends its own line to `Valley Pawn OS/loan-layaway-outcomes/RUN_LOG.md`. If Step 1 failed both ways, append one line yourself: `- <now ET> | FAILED | path=A|B | note=<short reason>` — and send nothing to Slack.

## Hard rules
- Rule 16: nothing technical in Slack — no file names, paths, "script", "pipeline", "queue", error text, or retries. The only Slack outputs are the verbatim report or the single plain on-hold line above.
- Rule 18: never send numbers the script did not produce; never present a missing store as zero; never send a second "corrected" message for the same month.
- Never drive Bravo, never drop a trigger file, never run any other script.
- Native migration: this task is fully mechanical and is listed in `Valley Pawn OS/fleet/NATIVE_MIGRATION_PLAN_2026-09-30.md` §A. When it is converted to a launchd agent (same command, `--send`), this Cowork task must be disabled in the same step — never both (double send; the `.sent` marker is the backstop).