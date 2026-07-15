---
name: weekly-loan-review-canvas-refresh
description: Monday 9:20 AM — overwrite the #loan-review Slack Canvas (current-week view) from the latest pipeline output so it always stays at the top, no manual pinning.
---

You keep the #loan-review Slack channel's Canvas current so managers always see this week's numbers at the top of the channel without anyone pinning a message. This runs Monday at 9:20 AM, after the monday-bravo-combined-compile pipeline (which fires earlier Monday morning) has produced the weekly loan/layaway report. Do the following:

1. SOURCE THE LATEST NUMBERS. Use the Google Drive connector. Search for the most recently modified file whose title begins with "Loan_Layaway_Review_" and ends in ".docx" (query: title contains 'Loan_Layaway_Review'). Read its content. It contains two tables plus a status line: (a) "Past-Due Loans (75-Day Rule)" with columns Store, Items 75+ Days, $ Past Due, % of Loan Bal, Status; and (b) "Layaway Review" with columns Store, Overdue, Past Pmt Due, Contacted/No Act, 30d No Pmt, Locate; plus a Company total row for each, the "as of" balance date, and any action note (e.g. a store with a Locate layaway). Extract the exact numbers for all 5 stores (Culpeper, Harrisonburg, Lexington, Roanoke, Waynesboro) and the Company totals. If no Loan_Layaway_Review_*.docx exists for the current week, STOP and do nothing (do not post stale data).

2. OVERWRITE THE CANVAS. Use the Slack connector tool slack_update_canvas with canvas_id "F0BH6BJ0PK7", action "replace", and NO section_id (this replaces the entire canvas). Rebuild it in exactly this locked format, substituting the extracted numbers and the report's week/date and balance-as-of date. Keep the Full Details link exactly as shown:

# :large_green_circle: Status — Week of ![](slack_date:YYYY-MM-DD)
<one-line takeaway: how many of 5 stores are within the 5% policy, and any action item such as a Locate layaway. If any store is OVER 5%, use :red_circle: in the heading instead of :large_green_circle: and name the store.>

# :bar_chart: Past-Due Loans (75-Day Rule)
Policy cap: 5% of store loan balance. Balances as of <balance date>.

| Store | Items 75+d | $ Past Due | % of Loan Bal | Status |
|---|---|---|---|---|
| Culpeper | ... |
| Harrisonburg | ... |
| Lexington | ... |
| Roanoke | ... |
| Waynesboro | ... |
| **Company** | ... |

(use :white_check_mark: for stores within 5%, :red_circle: for any over)

# :card_index_dividers: Layaway Review

| Store | Overdue | Past Pmt Due | Contacted/No Act | 30d No Pmt | Locate |
|---|---|---|---|---|---|
| ...all 5 stores + **Company** row... |

# :page_facing_up: Full Details
:arrow_right: [Loan & Layaway Review — Details (Live) spreadsheet](https://docs.google.com/spreadsheets/d/1OwUddmK1BJRBMpnstXw1frFBPW36d6i9nXKVnUdahX8/edit)

_This Canvas is overwritten each week with the latest numbers. Weekly history stays in the channel feed below. Source: Bravo POS Monday combined run._

3. UPDATE THE DETAILS SPREADSHEET (best-effort). Using the Google Drive connector, update the Google Sheet with id "1OwUddmK1BJRBMpnstXw1frFBPW36d6i9nXKVnUdahX8" so its Past-Due Loans and Layaway tables match this week's numbers and the "Week of" date. If you cannot write to the existing sheet, leave it as-is — the Canvas already carries the full tables, so no data is lost. Do not create a new spreadsheet.

4. DO NOT post a new message to the channel feed — the compile pipeline already posts the weekly feed message. Your only job is the Canvas (and best-effort the sheet). Keep the channel quiet otherwise.

5. Notify Joshua with a one-line confirmation of what you updated (e.g. "Refreshed #loan-review Canvas for week of Jul 20 — all 5 stores within policy"). If you stopped because no current report was found, say so.