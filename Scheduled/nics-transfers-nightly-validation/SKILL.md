---
name: nics-transfers-nightly-validation
description: One-time 10 PM validation: when the Bravo pipeline is idle, run the fixed nics-transfers handler against Waynesboro; if it returns rows, pull all 5 stores for June and DM Joshua the result. Self-disables after.
---

ONE-TIME NIGHT VALIDATION of the FFL "nics-transfers" Bravo pull. Runs at 10 PM when the pipeline is quiet. Keep it BOUNDED — run the already-deployed handler and report; do NOT edit handler code, do NOT change display/resolution, do NOT screenshot-hunt. If it fails, report and stop.

CONTEXT: Read skills enterprise-map, valley-pawn-context, bravo-context first. All access to the Bravo Data Extraction folder MUST go through mcp__Control_your_Mac__osascript `do shell script` (it is outside the task sandbox). PROJECT DIR: /Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction (Windows Y: path: Y:\Documents\Claude\Projects\Bravo Data Extraction). VM UUID for prlctl: {7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a} (prlctl at /usr/local/bin/prlctl, fallback /Applications/Parallels Desktop.app/Contents/MacOS/prlctl).

The handler reports/NicsTransfers.ahk is already deployed and fixed. It does the flow Joshua confirmed: Void/View Transactions -> Custom Reports -> select "Claude NICS Transfers" -> (fee type "NICS Fee" is now pre-populated on the saved report by Joshua) -> OK -> renders. Today's fix: it now Cancels out of any open report to a clean Dashboard BEFORE the store switch (Bravo cannot Lock Session from inside a report editor).

STEP 1 — IDLE GUARD. Via osascript check: results written in last 6 min (`find "<DIR>/results" -name '*.result.json' -mmin -6`), live triggers in `<DIR>/triggers/*.json`, and `<DIR>/triggers/claimed`. Also check the newest per-run log (exclude foreground_keeper.log/watchdog logs) hasn't changed in ~4 min. If a run is active, wait 3 min and re-check (up to 4x). If still busy, EXIT and DM Joshua that it was busy and to reschedule.

STEP 2 — CLEAN BASELINE. Run the health gate to put Bravo on a WAY Dashboard: `do shell script "B='<DIR>'; rm -f \"$B/logs/_health_gate_status.txt\"; nohup bash \"$B/bravo_health_gate.sh\" WAY >/dev/null 2>&1 & echo started"`. Poll logs/_health_gate_status.txt (~25s x12) for `PASS WAY`. If it never passes, DM Joshua "Bravo health gate could not reach a Dashboard tonight" and STOP.

STEP 3 — VALIDATE WAYNESBORO (has real data). Drop a trigger into <DIR>/triggers/ named nics-val-WAY-<ts>.json: {"id":"nics-val-WAY-<ts>","requested_at":"<iso>","reports":[{"name":"nics-transfers","stores":["WAY"],"date":"2026-06-01..2026-06-30"}]}. Poll logs/nics-val-WAY-<ts>.log + results. SUCCESS = the output CSV output/2026-06-01_to_2026-06-30_WAY_nics-transfers.csv has MORE than the header line (real rows) with a fee/amount column.

STEP 4 — IF WAY SUCCEEDS: drop ONE trigger for the other four stores: {"reports":[{"name":"nics-transfers","stores":["CUL","HAR","LEX","ROA"],"date":"2026-06-01..2026-06-30"}]}. Let it run (each store several min; re-check idle between if needed). Then read all 5 CSVs, sum per store: transfer count = data-row count, revenue = sum of the fee/amount column. DM Joshua a per-store table (count + revenue) + company total, and note it matches (or not) the manual June figures: CUL 48/$1,345, HAR 2/$50, LEX 32/$840, ROA 19/$625, WAY 29/$795 (total 130/$3,655).

STEP 5 — IF WAY FAILS (still 0 rows / selection error): DM Joshua the exact failure (tail of the log — the step it failed at) and STOP. Do NOT keep retrying, do NOT edit code, do NOT touch resolution.

ALWAYS: leave Bravo on a clean Dashboard when done (the handler's pre-switch Cancel + BackToDashboard handle this). DM Joshua only (Slack user U03BB52MDSA) — never a public channel. When finished (success OR fail), you are done (this is a one-time task; it auto-disables after firing).