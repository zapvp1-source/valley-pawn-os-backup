---
name: weekly-employee-sales-rankings
description: Monday 1:30 AM (overnight) — compile MTD employee sales rankings using "Retail Sales Excluding Fees" from Bravo's Employee Activity report. Pipeline-driven — no Parallels grant required. Schedule Slack post to #employee-performance for 9 AM Monday.
---

You are running as an overnight background task at 1:30 AM Monday. Compile MTD employee sales rankings for all 5 Valley Pawn stores via the Bravo Data Extraction pipeline, then schedule a ranked Slack post to #employee-performance for 9:00 AM Monday.

============================================================
CRITICAL — WHICH METRIC TO USE
============================================================
The metric for this ranking is **"Retail Sales Excluding Fees"** from Bravo's Employee Activity report.

DO NOT use "Total Productivity." Total Productivity includes fees and other non-retail activity and is the WRONG number.

If the CSV doesn't expose "Retail Sales Excluding Fees" as a column header, locate the closest equivalent (retail sales with fees subtracted out). NEVER fall back to Total Productivity.

============================================================
STEP 1 — Drop the Bravo trigger and wait
============================================================

Generate a trigger ID like `employee-activity-YYYY-MM-DDTHH-MM-SS`. Write to `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/<id>.json`:

```json
{
  "id": "employee-activity-2026-05-12T01-30-00",
  "requested_at": "2026-05-12T01:30:00-04:00",
  "reports": [
    {
      "name": "employee-activity",
      "stores": ["CUL", "HAR", "LEX", "ROA", "WAY"],
      "date": "2026-05-01"
    }
  ]
}
```

The `date` field is the **Start Date** for the report — first of the current month. End Date defaults to today.

Poll `results/<id>.result.json`. Full 5-store cycle takes ~3-5 minutes. Time out at 10 minutes.

============================================================
STEP 2 — Parse the CSVs
============================================================

For each successful cell, read its CSV from `output_path`. The Employee Activity CSV is a DevExpress export. The data table has rows per employee with columns like:
- Employee Name | Retail Sales Excluding Fees | (various other metrics)

Extract per-employee:
- Name
- Store (from filename: `_<STORE>_employee-activity.csv`)
- Retail Sales Excluding Fees (the column whose header exactly matches; if not present, use the retail-sales-minus-fees column)

Filter out:
- SYSTEM rows
- Header repetitions in the CSV
- Empty rows

============================================================
STEP 3 — Aggregate across stores
============================================================

- Sum across stores for multi-store employees (Preston Peters, Martin Dowden, Chadd McClintic, etc.)
- Rank highest-to-lowest by total Retail Sales Excluding Fees (MTD)
- Include zero and negative figures at the bottom; negatives reflect canceled layaways/returns exceeding sales

============================================================
STEP 4 — Slack post (canonical format from 2026-05-04)
============================================================

Channel: `#employee-performance` (`C0ATTLPQHR8`)

- Before 9:00 AM Monday → `slack_schedule_message` for 9:00 AM Monday.
- At or after 9:00 AM Monday → `slack_send_message` (post immediately).

**Use this exact format.** Use medal emoji for ranks 1-3, then "4th", "5th", "Nth" for the rest. Italicize the metric in the footer.

```
*MTD Employee Sales Rankings — Retail Sales Excluding Fees (Bravo POS)*
📊 Period: [start–end]

🥇 *[Employee Name]* ([STORE]) — $X,XXX.XX
🥈 *[Employee Name]* ([STORE]) — $X,XXX.XX
🥉 *[Employee Name]* ([STORE]) — $X,XXX.XX
4th *[Employee Name]* ([STORE]) — $X,XXX.XX
5th *[Employee Name]* ([STORE]) — $X,XXX.XX
...
Nth *[Employee Name]* ([STORE]) — $X,XXX.XX

_Source: Bravo POS · Employee Activity report. Multi-store employees summed across stores._
```

- Multi-store employees show all their stores in parens with a `+`, e.g., `(HAR + LEX)`.
- Include $0.00 and negative figures at the bottom — don't filter them.
- List ALL non-SYSTEM employees who appeared, even if their value is $0.00.

============================================================
STEP 5 — Save the spreadsheet
============================================================

Save to `/Users/joshuadavis/Documents/Claude/Scheduled/employee-sales-rankings-YYYY-MM-DD.xlsx` with two sheets:
- **Sheet 1 "Employee Sales Rankings"** — overall ranked list (Rank, Employee, Store(s), Retail Sales Excluding Fees). Gold/silver/bronze fill on top 3. Brand colors: Purple `#2D1A5E`, Blue `#0099DD`. Arial throughout.
- **Sheet 2 "Per Store"** — store-by-store breakdown with employees sorted highest-to-lowest within each store.

============================================================
VERIFY BEFORE POSTING
============================================================
- Numbers came from "Retail Sales Excluding Fees," NOT "Total Productivity."
- The Slack header says "Retail Sales Excluding Fees" so the team can see which metric.
- Multi-store employees summed once across stores (no double-counting).

## If something goes wrong
- **Pipeline failure (any store)**: include the store in the rankings if you got any data; note the failure in a footer line.
- **All 5 cells failed**: DM Joshua and stop; he'll restart the watcher.

## Background
This SKILL was rewritten 2026-05-12 to use the Bravo Data Extraction pipeline instead of driving Bravo via computer-use.
