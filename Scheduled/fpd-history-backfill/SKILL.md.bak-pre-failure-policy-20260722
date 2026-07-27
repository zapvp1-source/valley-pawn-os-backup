---
name: fpd-history-backfill
description: One-time bootstrap of the 12-month FPD history archive. Runs the saved Bravo report 'Claude FPD 12-month Lookback' across all 5 stores via the Bravo Data Extraction pipeline, merges every row into /Users/joshuadavis/Documents/Claude/Scheduled/_fpd-archive/fpd-history.csv deduped by Ticket Number, and DMs Joshua a summary. Use this once after creating the saved report in Bravo to seed the chronic-risk view in weekly-fpd-ranking. Safe to run again later as a quarterly/monthly refresh.
---

You are running Joshua Davis's one-time (or periodic refresh) backfill of the FPD history archive. This skill seeds `_fpd-archive/fpd-history.csv` with every loan that has defaulted in the last 365 days, so the weekly-fpd-ranking skill's chronic-risk sections show meaningful data starting from week 1 instead of after a year of weekly accumulation.

**Prerequisite — saved Bravo report must exist.** Before running this skill, Joshua must create a saved Bravo report named exactly **"Claude FPD 12-month Lookback"** in any one store (saved reports are company-wide). Criteria:
- Loan Date in last 365 days (today minus 365 → today)
- Last Payment Date IS NULL
- Columns: Ticket Number, Category, Full Description, Loan Amount (same as "Claude First Payment Default")

If the report does not exist, every store cell will fail with a `SelectSavedReport` error. DM Joshua and stop.

═══════════════════════════════════════════════
STEP 1 — Drop the Bravo trigger
═══════════════════════════════════════════════

Generate a trigger ID and JSON, write via osascript:

```applescript
set triggerId to "fpd-history-backfill-2026-05-18T17-40-00"
set triggerJson to "{\"id\": \"" & triggerId & "\", \"requested_at\": \"2026-05-18T17:40:00-04:00\", \"reports\": [{\"name\": \"fpd-lookback-12mo\", \"stores\": [\"CUL\",\"HAR\",\"LEX\",\"ROA\",\"WAY\"], \"date\": \"2026-05-18\"}]}"
set triggerPath to "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/" & triggerId & ".json"
do shell script "echo " & quoted form of triggerJson & " > " & quoted form of triggerPath
return "dropped " & triggerPath
```

═══════════════════════════════════════════════
STEP 2 — Poll for completion (LONG)
═══════════════════════════════════════════════

A 12-month lookback grid can have hundreds of rows per store. The grid walker pages through them all. Budget **5–15 minutes per store**, **30–75 minutes for all 5**. Timeout at **90 minutes** (180 polls × 30s).

```applescript
do shell script "test -f '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/results/" & triggerId & ".result.json' && echo READY || echo PENDING"
```

If timeout fires, DM Joshua at `U03BB52MDSA` with the trigger ID and stop.

═══════════════════════════════════════════════
STEP 3 — Read each CSV and merge into the archive
═══════════════════════════════════════════════

For each successful cell, read its CSV via osascript. CSV shape:

```
Ticket Number,Category,Full Description,Loan Amount
BT-VAP015231,Gold-Stone Ring,4.2DWT 14K-Y/G ROUND CUT,$140.00
...
```

**Archive path:** `/Users/joshuadavis/Documents/Claude/Scheduled/_fpd-archive/fpd-history.csv`

**Archive columns:**
```
first_seen_date,store,ticket_number,category,full_description,loan_amount
```

**Merge logic:**
1. Create the `_fpd-archive` folder if it doesn't exist.
2. If `fpd-history.csv` doesn't exist, create it with the header row above.
3. Load existing ticket numbers from the archive into a set.
4. For each new row from this run, if `ticket_number` is not already in the archive set, append:
   - `first_seen_date` = today (YYYY-MM-DD)
   - `store` from the CSV filename
   - other fields from the row
5. Sum the new-row count and totals per store as you go.

Use real CSV parsing (Python `csv` module via osascript, or any library that handles quoted fields with embedded commas).

═══════════════════════════════════════════════
STEP 4 — Summarize and DM Joshua
═══════════════════════════════════════════════

Compute and DM Joshua (`U03BB52MDSA`) on Slack:

```
*FPD history backfill complete — [today]*

Loans added to archive:
• CUL — [N] loans • $[exposure]
• HAR — [N] loans • $[exposure]
• LEX — [N] loans • $[exposure]
• ROA — [N] loans • $[exposure]
• WAY — [N] loans • $[exposure]
*Total:* [ΣN] loans • $[Σexposure] now in fpd-history.csv

Top 3 chronic categories (12-month):
1. [CATEGORY] — [N] loans • $[exposure]
2. [CATEGORY] — [N] loans • $[exposure]
3. [CATEGORY] — [N] loans • $[exposure]

Top 10 chronic items (12-month, by Category + first-3-words-of-description):
1. [CATEGORY] / [CANONICAL DESCRIPTION] — [N] occurrences • $[exposure]
... (10 total)

Archive: /Users/joshuadavis/Documents/Claude/Scheduled/_fpd-archive/fpd-history.csv
```

Do NOT post to `#first-payment-default` — this is a backfill/maintenance action, not a weekly ops update. The ops channel stays clean.

═══════════════════════════════════════════════
If something goes wrong
═══════════════════════════════════════════════

- **Saved report not found** (cells fail with `SelectSavedReport` or `Claude FPD 12-month Lookback`): the saved Bravo report doesn't exist yet. DM Joshua and stop — he needs to create it in Bravo first.
- **Watcher not running** (no result JSON after 90 min): DM Joshua with the trigger ID and stop.
- **Some stores succeeded, others failed**: merge what you have, DM Joshua a partial summary noting which stores need a retry. Re-running the skill is safe — the archive dedupes by Ticket Number.
- **Archive file exists but header doesn't match expected**: stop and DM Joshua. Don't append potentially-misaligned rows.

═══════════════════════════════════════════════
Cadence
═══════════════════════════════════════════════

Run this once after the saved report is created in Bravo. Optionally re-run monthly or quarterly to capture loans that defaulted in the prior month that the weekly cohort (60–90 day rolling window) might have under-captured. The dedupe-by-ticket logic makes re-running a no-op if no new data is found.
