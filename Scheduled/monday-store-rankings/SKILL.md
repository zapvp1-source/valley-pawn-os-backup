---
name: monday-store-rankings
description: Monday morning: open Bravo POS, run the Company KPI dashboard report for the current month-to-date, build a ranked store performance spreadsheet, and post results to Slack #store-performance.
---

> ⚠️ **FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE.** If this task fails, errors out, or cannot complete its intended work for any reason, DO NOT post anything to Slack — no error messages, no partial results, no "I couldn't finish" notices. Joshua reviews every run inside Claude to confirm success or failure, so a failed run must stay completely silent on Slack. Only post to Slack once the task has genuinely completed the work it was designed to do. Posting failure or error noise clutters Slack and reflects poorly on the team.

You are helping Joshua Davis, CEO of Valley Pawn (Full Circle Finance Inc), with a weekly Monday morning store performance workflow.

==========================================================================
🛑 FORMAT IS LOCKED — DO NOT DEVIATE 🛑
==========================================================================

The Slack post format below (Step 6) is the **canonical, user-approved format**. Joshua specifically said on 2026-05-11: "_When you publish via Slack the publishing format must remain consistent. You published store rankings and they are different from week prior. Has to be same every week. We like the one from previous week._"

That means:
- ❌ Do NOT replace the parent message with a single narrative paragraph. The parent message must lead with "_Valley Pawn — Weekly Store Performance Rankings_" and contain the 🏆 *Overall Store Rankings* list (Avg Rank | category wins) + 💡 *Quick Summary*.
- ❌ Do NOT replace the thread reply's category-by-category list with a wide code-block table (rank | store | retail | GP% | GP$ | Inv | Loan | Turns | Net). That format was tried on 2026-05-11 and is the exact deviation Joshua called out.
- ❌ Do NOT skip any of the 8 ranked categories. Even when Scrap Sales is $0 across all stores, include the line `*Scrap Sales*` followed by `All stores at $0.00 (no scrap activity for the period)`.
- ✅ Follow the templates in Step 6 EXACTLY. Compare your draft to the example posts at lines 90–112 before sending.

If you find yourself wanting to "make it cleaner" or "consolidate the data into one table", stop — that's the failure mode this rule exists to prevent. The category-by-category format is more readable on mobile, lets each store team see exactly where they rank in every metric, and is what the team has come to expect every Monday.

## Objective
Read the 5 per-store End of Month CSVs produced by the Bravo Data Extraction pipeline (the `end-of-month` cell of the Monday combined run), build a ranked store performance spreadsheet, and post the results to the Slack #store-performance channel (ID: C03CGTN3KN1).

**Architecture note (2026-06-22 — EOM split out):** Store-rankings is now a
STANDALONE Monday flow, decoupled from `monday-bravo-combined-run`/`-compile`
(which handle the four reliable reports). A new task, `monday-store-rankings-run`
(Mon ~10:30 AM), runs the resilient EOM runner (`eom_runner.sh` — settle-after-
login + kill/retry, because the Bravo 2026.6.0.76 EOM export intermittently
freezes and writes 0-byte files) to produce the 5 per-store CSVs on a settled
Bravo, then fires THIS poster ~45 min later. This poster only reads the CSVs and
posts; it does not drive Bravo. If the runner couldn't get all 5 (Bravo export
bug), this poster skips silently — the four main reports already posted earlier.

**Architecture note (2026-05-23):** This skill is now PIPELINE-DRIVEN. The
prior approach drove Bravo's Dashboard "Company KPIs" SSRS report via
computer-use. That path is preserved in git history but no longer used —
SSRS Forms-auth and Akamai bot-protection made it unreliable, AND Bravo's
native "End of Month" report (under Reports → Closing Reports) carries
every metric we need with a clean CSV export. The orchestrator drops 5
sequential single-store triggers for `end-of-month` (one per store, 90s
spacing) before invoking this compile step.

## Steps

1. **Load the 5 per-store CSVs:**
   - Expect 5 files in `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/`:
     - `<END_DATE>_CUL_end-of-month.csv`
     - `<END_DATE>_HAR_end-of-month.csv`
     - `<END_DATE>_LEX_end-of-month.csv`
     - `<END_DATE>_ROA_end-of-month.csv`
     - `<END_DATE>_WAY_end-of-month.csv`
   - `<END_DATE>` is the period end date (typically yesterday) in `YYYY-MM-DD` format.
   - If any CSV is missing OR less than 500 bytes, **SKIP this run silently** — do NOT post a partial leaderboard, and per the failure policy do NOT DM or post anything (Joshua reviews runs himself). The EOM export is a known-flaky Bravo 2026.6.0.76 step; a missing-CSV week just means store-rankings doesn't post that week. The four main reports are unaffected (they run in the separate `monday-bravo-combined-run`).

2. **Parse each store's CSV to extract the 8 ranking metrics:**

   The End of Month CSV is a flat report (~138 rows × 20 cols). Each metric
   lives at a known row/column. Use a stable text-based locator (anchor on
   the row label, not on absolute row number — Bravo may insert blank rows).

   For each store, extract:
   - **Loan Balance**:  find the row starting with `Ending Loan Base ` (note trailing space + date) → take the dollar value in the "5/22/2026" column (typically column 5).
   - **Inventory Balance**: find the row starting with `Ending Inventory Base ` → same column.
   - **Total Assets**: calculated = Loan Balance + Inventory Balance.
   - **Retail Sales Total Amt**: In the **Sales Activity** section, sum the `Taxable Sales` Total + `Nontaxable Sales` Total (rightmost column of each row). Do NOT read from the `Total:` row in the top daily summary -- that row is blank in multi-day EOM CSV exports.
   - **Pawn Service Charges**: Sum of (a) In-Store Txns subtotal: Interest + Fees only (exclude Misc Charges and Principal Pymt), AND (b) MobilePawn Activity Totals row: Interest + Fees only (exclude Misc Charges). Do NOT read from the `Total:` row column 2 -- blank in multi-day exports. Read from the Pawn Activity and MobilePawn Activity sections directly.
   - **Scrap Sales**: In the Inventory section, find the row labeled `Refined (Cost of Sales)` and extract the Month-column dollar value (strip parens = positive). This is the cost-basis of gold sent to the refinery.
   - **Layaway Balance**: find the `Ending Balance` row under the Layaways subsection and take the dollar value.
   - **Net Revenue MTD**: ⚠️ FIXED 2026-06-01. Previous formula used `Sales Revenue (Profit)` alone which EXCLUDED PSC entirely, understating total revenue by ~40%.
     **Correct formula: Net Revenue MTD = PSC + In-store Misc Charges + Mobile Misc Charges + MobilePawn Convenience Fees + Sales Revenue (Profit)**
     - PSC = In-store (Interest + Fees) + Mobile (Interest + Fees) [same as Pawn Service Charges above]
     - In-store Misc Charges = Misc Charges subtotal from In-Store Txns section
     - Mobile Misc Charges = Misc Charges column from MobilePawn Activity Totals row
     - MobilePawn Convenience Fees = the `MobilePawn Convenience Fees` row value
     - Sales Revenue (Profit) = the `Sales Revenue (Profit)` row total (last column) in Sales Activity section
     WAY verification (May 1-26): $12,860.19 PSC + $820.00 in-store misc + $410.50 mobile misc + $312.43 conv fees + $20,727.64 sales profit = $35,130.76 (~$10 rounding gap vs Joshua's $35,140.72)
     DO NOT use `Sales Revenue (Profit)` alone -- it is retail/merchandise profit only and omits pawn service revenue, which is Valley Pawn's primary income stream.

   All dollar values in the CSV are formatted like `"$1,234.56"` or `($999.99)` (negatives in parens). Strip `$`, `,`, and parens; treat parens as negative.

4. **Rank stores per category:** For each metric, sort the 5 stores from highest to lowest value. #1 = highest value in ALL categories. Also compute an overall average rank and count of #1 finishes per store.

5. **Create the spreadsheet** using openpyxl with the ranked leaderboard layout:
   - Title: "VALLEY PAWN — Store Performance Rankings"
   - Subtitle: Report period dates from the Bravo report
   - Column headers: Category, #1, #2, #3, #4, #5, Company Total
   - Each metric gets TWO rows: store names row + dollar values row, sorted in rank order
   - Gold/silver/bronze styling for top 3 positions
   - Overall Rankings section at bottom with avg rank and #1 finishes
   - Brand colors: Purple (#2D1A5E), Blue (#0099DD), Coral (#F58C8A), Light Blue (#3DB8E8)
   - Font: Arial throughout
   - Save to /sessions/*/mnt/outputs/ AND copy to the workspace folder so Joshua can open it
   - Run recalc: `python mnt/.skills/skills/xlsx/scripts/recalc.py <filepath>`

6. **Post to Slack #store-performance (C03CGTN3KN1)** using TWO messages — this is the **canonical format locked in 2026-05-04**.

   The third "spreadsheet link" message is optional and only sent if the xlsx was actually generated; if you skipped the xlsx (which is acceptable — the data is fully readable from the two messages alone), do not post the third message. The two below are the required posts.

   - **First message:** Summary post with overall store rankings AND a brief narrative analysis. Use rank-counted-by-category-wins where the count denominator is the number of categories with a non-tied #1 (skip categories where all stores tied at $0.00, e.g. Scrap Sales when no scrap was sold). Note "X out of N" reflects only ranked categories.

     ```
     *Valley Pawn — Weekly Store Performance Rankings*
     📊 Report Period: [start–end]

     *🏆 Overall Store Rankings:*
     🥇 *[Store]* — Avg Rank X.XX | X category wins out of N
     🥈 *[Store]* — Avg Rank X.XX | X category win[s]
     🥉 *[Store]* — Avg Rank X.XX | X wins
     4th *[Store]* — Avg Rank X.XX | X wins
     5th *[Store]* — Avg Rank X.XX | X wins

     *💡 Quick Summary:*
     [2–3 sentences. Call out the winner and what drove the top ranking. Note close races, surprising performances, or which categories anchored the bottom store. Italicize store names with underscores like _Lexington_. Conversational and upbeat — Monday-morning-coach voice, not a financial-report voice.]

     Full ranked breakdown in thread 👇
     ```

   - **Second message:** Thread reply on the first message (`thread_ts` = first message's `ts`, `reply_broadcast=true`). Full category-by-category rankings with store name + dollar value at every position. Include all 8 metrics in this exact order:
     1. Loan Balance
     2. Inventory Balance
     3. Total Assets (Inventory + Loan)
     4. Retail Sales Total Amt
     5. Pawn Service Charges
     6. Scrap Sales (if all stores tied at $0.00, write the single line `*Scrap Sales*` then `All stores at $0.00 (no scrap activity for the period)` instead of a ranked list)
     7. Layaway Balance
     8. Net Revenue MTD

     End the thread reply with a `*Company Totals*` single-line summary covering Loan Balance, Inventory Balance, Layaway Balance, Net Revenue MTD.

     Format example (locked in 2026-05-04):
     ```
     *📊 Full Category Rankings*

     *Loan Balance*
     🥇 Culpeper — $154,604.43
     🥈 Harrisonburg — $151,174.04
     🥉 Roanoke — $129,290.46
     4th Waynesboro — $99,030.78
     5th Lexington — $64,998.85

     *Inventory Balance*
     🥇 Culpeper — $198,581.94
     ...

     *Scrap Sales*
     All stores at $0.00 (no scrap activity for the period)

     ...

     *Company Totals*
     Loan Balance: $599,098.56 | Inventory Balance: $635,917.05 | Layaway Balance: $98,109.64 | Net Revenue MTD: $23,872.72
     ```

   - **Third message (optional):** Only post if the xlsx was actually saved. Thread reply (no `reply_broadcast`):
     ```
     📎 Full ranked spreadsheet saved to the shared outputs folder: `Valley_Pawn_Store_Rankings_[Month][Year].xlsx`
     ```

## Important Notes
- Data source is the per-store `end-of-month` CSV produced by the Bravo Data Extraction pipeline. No Parallels grant needed for this skill — the orchestrator handles pipeline data collection upstream.
- Rankings: #1 = highest value for ALL categories
- Do NOT try to create Slack Canvases or upload files — just use slack_send_message for all three posts
- Valley Pawn stores: Culpeper (Cul), Harrisonburg (Har), Lexington (Lex), Roanoke (Roa), Waynesboro (Way)
- ALWAYS include the spreadsheet file reference at the bottom of the Slack thread
- If any CSV is missing or under-sized (< 500 bytes), DM Joshua (U03BB52MDSA) with the failing stores and SKIP the post — never publish a partial leaderboard.

## Legacy reference (computer-use path) — no longer used
The prior version of this skill drove Bravo's "Company KPIs" Dashboard button via Parallels + computer-use, reading the rendered SSRS report from Edge inside the VM with screenshots + zoom. That path is preserved in git history under the same path. It was retired 2026-05-23 in favor of the pipeline + native "End of Month" report. If the pipeline path fails for an extended period and you need to fall back, see the git history of this file.