---
name: weekly-employee-perf-canvas-refresh
description: Monday 9:24 AM — overwrite the #employee-performance Slack Canvas from the latest employee sales rankings so it stays at the top, no manual pinning.
---

You keep the #employee-performance Slack channel's Canvas current so the team always sees this week's MTD sales leaderboard at the top without anyone pinning. Runs Monday 9:24 AM, after the monday-bravo-combined-compile pipeline runs. Steps:

1. SOURCE NUMBERS. Use the Google Drive connector. Find the most recently modified file whose title begins with "employee-sales-rankings-" ending ".xlsx" (query: title contains 'employee-sales-rankings'). Read it. It lists each employee, their store(s), and Total (Retail Sales Excluding Fees) for the MTD period, plus a Company Total row and the period dates. Build the RANKED view: exclude any employee with $0.00 total and exclude Preston Peters (he is ownership, shown only in the company total). Rank the rest high to low.

2. OVERWRITE THE CANVAS. Use Slack tool slack_update_canvas with canvas_id "F0BH9UK284S", action "replace", NO section_id. Rebuild in this locked format, substituting the period end date, the ranked rows, and the company total:

# :bar_chart: MTD Employee Sales — as of ![](slack_date:YYYY-MM-DD)
Retail sales excluding fees (Bravo POS). Period: <period>.
:trophy: <one-line takeaway: who leads, and which store total is strongest>

# :1234: Ranked Leaderboard

| # | Employee | Store | Retail Sales (excl. fees) |
|---|---|---|---|
| :first_place_medal: / :second_place_medal: / :third_place_medal: then 4,5,6... | ... | ... | ... |

_Company total (incl. Preston): **$XX,XXX.XX**_

# :page_facing_up: Full Details
:arrow_right: [Employee Sales Rankings — Details (Live) spreadsheet](https://docs.google.com/spreadsheets/d/1--Kn_2ybJCf6_PGnTdyMjCHBDsoEM4iCYPtokjHRIsg/edit)

_This Canvas is overwritten each week with the latest numbers. Weekly history stays in the channel feed below. Source: Bravo POS Monday combined run._

3. Best-effort update the Google Sheet id "1--Kn_2ybJCf6_PGnTdyMjCHBDsoEM4iCYPtokjHRIsg" to match this week's ranked list. If you cannot write it, leave as-is (the Canvas carries the full table). Do not create a new spreadsheet.

4. Do NOT post a feed message — the compile pipeline already posts it. Canvas only.

5. Notify Joshua with a one-line confirmation, or say so if you stopped because no current file was found.