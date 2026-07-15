---
name: weekly-layaway-review-canvas-refresh
description: Monday 9:22 AM — overwrite the #layaway-review Slack Canvas from the latest pipeline output so it stays at the top, no manual pinning.
---

You keep the #layaway-review Slack channel's Canvas current so managers always see this week's layaway numbers at the top of the channel without anyone pinning. Runs Monday 9:22 AM, after the monday-bravo-combined-compile pipeline has produced the weekly report. Steps:

1. SOURCE NUMBERS. Use the Google Drive connector. Find the most recently modified file whose title begins with "Loan_Layaway_Review_" ending ".docx" (query: title contains 'Loan_Layaway_Review'). Read it. Use the "Layaway Review" table: columns Store, Overdue, Past Pmt Due, Contacted/No Act, 30d No Pmt, Locate, plus the Company row, and any action note (e.g. a store with a Locate item). Extract exact counts for all 5 stores (Culpeper, Harrisonburg, Lexington, Roanoke, Waynesboro) and Company totals. If no current-week Loan_Layaway_Review_*.docx exists, STOP and do nothing.

2. OVERWRITE THE CANVAS. Use Slack tool slack_update_canvas with canvas_id "F0BJ48BMZGQ", action "replace", NO section_id. Rebuild in this locked format, substituting numbers and the week/date:

# :large_green_circle: Status — Week of ![](slack_date:YYYY-MM-DD)
<one-line takeaway; if any store has a Locate item, call it out with :warning:>

# :card_index_dividers: Layaway Review
Counts by category. Percentages = each store's share of the company total.

| Store | Overdue | Past Pmt Due | Contacted/No Act | 30d No Pmt | Locate |
|---|---|---|---|---|---|
| ...all 5 stores + **Company** row... |

# :page_facing_up: Full Details
:arrow_right: [Loan & Layaway Review — Details (Live) spreadsheet](https://docs.google.com/spreadsheets/d/1OwUddmK1BJRBMpnstXw1frFBPW36d6i9nXKVnUdahX8/edit)

_This Canvas is overwritten each week with the latest numbers. Weekly history stays in the channel feed below. Source: Bravo POS Monday combined run._

3. Best-effort update the Google Sheet id "1OwUddmK1BJRBMpnstXw1frFBPW36d6i9nXKVnUdahX8" layaway section to match. If you cannot write it, leave as-is (the Canvas carries the full table). Do not create a new spreadsheet.

4. Do NOT post a feed message — the compile pipeline already posts it. Canvas only.

5. Notify Joshua with a one-line confirmation, or say so if you stopped because no current report was found.