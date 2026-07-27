---
name: overnight-closing-reports-smoke-2026-05-29
description: Overnight 2 AM May 29: 9 closing handlers × 5 stores (41 cells). Validates the {Enter}→{Tab} export fix at scale.
model: claude-sonnet-5
---

> ⚠️ **FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE.** If this task fails, errors out, or cannot complete its intended work for any reason, DO NOT post anything to Slack — no error messages, no partial results, no "I couldn't finish" notices. Joshua reviews every run inside Claude to confirm success or failure, so a failed run must stay completely silent on Slack. Only post to Slack once the task has genuinely completed the work it was designed to do. Posting failure or error noise clutters Slack and reflects poorly on the team.

Overnight smoke test of Bravo closing-report handlers. The export-hang bug was fixed today (2026-05-28) — the keyboard strategy in SetExportFormatCsv now uses Send("{Tab}") instead of Send("{Enter}") so the Export Document dialog stays open while picking CSV. EOM proved out with a real 7731-byte CSV at 14:27.

PRE-FLIGHT (CRITICAL):
1. Run via prlctl exec inside VM 7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a:
   powershell -Command "Get-Process Bravo*,AutoHotkey* | Select-Object Id,ProcessName,Responding,StartTime | Format-Table -AutoSize"
   Bravo must be running AND Responding=True. Exactly one AutoHotkey64 (watcher). If not, STOP and alert.
2. /Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/logs/watcher.last_started.txt must list end-of-month + end-of-day-consolidated in Handlers line.

DROP TRIGGER at /Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/overnight-smoke-2026-05-29.json:

{
  "id": "overnight-smoke-2026-05-29",
  "requested_at": "2026-05-29T02:00:00-04:00",
  "reports": [
    { "name": "end-of-month",             "stores": ["CUL","HAR","LEX","ROA","WAY"], "date": "2026-05-28" },
    { "name": "end-of-day-consolidated",  "stores": ["CUL"],                          "date": "2026-05-28" },
    { "name": "deposits-paid-outs",       "stores": ["CUL","HAR","LEX","ROA","WAY"], "date": "2026-05-28" },
    { "name": "disbursement-journal",     "stores": ["CUL","HAR","LEX","ROA","WAY"], "date": "2026-05-28" },
    { "name": "end-of-day",               "stores": ["CUL","HAR","LEX","ROA","WAY"], "date": "2026-05-28" },
    { "name": "general-exception",        "stores": ["CUL","HAR","LEX","ROA","WAY"], "date": "2026-05-28" },
    { "name": "inter-store-cash-transfer","stores": ["CUL","HAR","LEX","ROA","WAY"], "date": "2026-05-28" },
    { "name": "large-cash-transactions",  "stores": ["CUL","HAR","LEX","ROA","WAY"], "date": "2026-05-28" },
    { "name": "transfers",                "stores": ["CUL","HAR","LEX","ROA","WAY"], "date": "2026-05-28" }
  ]
}

41 cells. ~75-105s each with 15s pacing = ~60-75 min total.

EXCLUDED: bravo-business-dashboard (SSRS — opens in Chrome, current handler can't drive it).

POLL: wait 5 min, then poll triggers/processed/overnight-smoke-2026-05-29.json every 90s. Hard timeout: 120 min.

AUDIT: read results/overnight-smoke-2026-05-29.result.json and output/2026-05-28_*.csv listings. Expected CSV sizes: EOM ~7-8 KB per store; EOD-consolidated ~5-6 KB; unknowns for the 7 new reports.

SUMMARY at /Users/joshuadavis/Documents/Claude/Projects/Bravo Pipeline/morning-smoke-summary-2026-05-29.md:
- X of 41 cells succeeded
- Per-report table of sizes per store
- Any hangs (grep "Not Responding\|hang" in log)
- For failed cells, paste error lines
- Recommendation: green-light to add Inventory/Loan/Sales/Retail handlers tomorrow, or what to fix

Do NOT post to Slack. Save the file only.

RULES: additive only, never edit existing handlers/dispatch, never delete files, no computer-use revival if Bravo hangs.