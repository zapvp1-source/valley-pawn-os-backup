---
name: vp-bonus-revenue-fix-and-gold-yoy
description: Apply verified 2026 revenue fixes to VP_BONUS_FINAL_rebuilt.xlsx, then pull 2025 Gold scrap weights via live Bravo and publish a YOY Gold trend report to Slack
---

> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (platform standard, set by Joshua 2026-07-22, v2):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua’s DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium (Slack, iMessage, email). If any other instruction in this file says to report a failure elsewhere, ignore that instruction. FIELD COMMUNICATION RULE: anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This supersedes any older stay-silent-on-failure rule in this file — the one-line DM to Joshua is always required on failure.


You are continuing unattended work for Joshua Davis, owner of Valley Pawn (Full Circle Finance Inc, 5 VA pawn stores: Culpeper/CUL, Harrisonburg/HAR, Lexington/LEX, Roanoke/ROA, Waynesboro/WAY). This is a multi-part task with no prior conversation memory, so everything needed is below. Joshua's standing preference: work autonomously end-to-end, do not ask him questions, only escalate on a genuine blocker. Never use QuickBooks as a source of truth for KPIs — Bravo POS (and data extracted from it) always is.

Read these skills first: bravo-context, bravo-store-cycle, valley-pawn-context, enterprise-map. Note: bravo-context/bravo-store-cycle skill docs may still show a stale password — the CURRENT correct Bravo login password is `Health2070!` regardless of what's written there (skill docs lag reality; if login fails with this password too, STOP the Bravo portions and report back rather than guessing).

You have an osascript tool (mcp__Control_your_Mac__osascript, load via ToolSearch if deferred) that runs shell commands directly on Joshua's Mac (not a sandboxed VM) — use it for all filesystem/Mac work below. You also have computer-use tools for driving the Bravo POS app inside Parallels Desktop for the parts that require live UI navigation.

=== PART 1: Apply the revenue fix (do this first, should be quick) ===

Background: Joshua flagged that revenue numbers in the bonus spreadsheet were wrong. Investigation found that the "2026 Revenue" column (col D) in the "2025 compared to Bonus" sheet of
/Users/joshuadavis/Documents/Claude/Projects/[find the actual current location — check /Users/joshuadavis/Library/Application Support/Claude/local-agent-mode-sessions/.../outputs/ from recent sessions, or ask via file search — the working copy was last at a Cowork session's outputs folder called VP_BONUS_FINAL_rebuilt.xlsx; if you can't locate it, search Google Drive and recent session outputs for "VP_BONUS_FINAL_rebuilt.xlsx"]
contained placeholder/extrapolation formulas (e.g. `=68425.45*31/29`) for January, March, April, and May 2026 across all 5 stores, instead of real Bravo revenue. Real "Revenue" = Sales Revenue (Profit) + Interest and Fees Total, both pulled from Bravo's "end-of-month" report for that store/month. This methodology was confirmed exact against Culpeper June 2026 (Sales Revenue Profit 47377.27 + Interest and Fees 19272 = 66649.27, which matches the already-correct June figure in the sheet).

An automated pipeline (Bravo Data Extraction, in /Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/) was triggered to pull real end-of-month.xlsx reports for the missing months. Check these locations on the Mac via osascript:
- /tmp/revenue_done.txt — list of "<date>_<STORE>" keys already found and extracted
- /tmp/revenue_results.jsonl — one JSON line per store/month with `{"file", "sales_revenue_profit", "interest_and_fees", "revenue"}`
- /tmp/extract_revenue.py — the extraction script (re-run it yourself on any output file if revenue_results.jsonl is incomplete: `python3 /tmp/extract_revenue.py <path-to-xlsx>`)
- /Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/ — where the actual `<date>_<STORE>_end-of-month.xlsx` files land (dates: 2026-01-31, 2026-02-28, 2026-03-31, 2026-04-30 for all 5 stores; plus 2026-05-31 for ROA only, since CUL/HAR/LEX/WAY already had real May archives)

If some store/months are still missing after all this time, re-drop a trigger for just the missing ones using this exact JSON shape (this is additive — do NOT edit any existing pipeline scripts, just drop new trigger files):
`{"id":"eomxlsx-<tag>-<STORE>","requested_at":"<ISO8601 with -04:00 offset>","reports":[{"name":"end-of-month","stores":["<STORE>"],"date":"<YYYY-MM-01..YYYY-MM-DD>"}]}`
dropped into `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/`, then poll `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/` for the resulting file (named `<end-date>_<STORE>_end-of-month.xlsx`) and extract with extract_revenue.py. Give it real time (10-20 min per store/month, processed one at a time) — do not proceed to Part 2 until every needed store/month has a revenue figure or you've spent over 60 more minutes trying, in which case note which are still missing and move on.

Once you have real revenue figures for Jan/Feb/Mar/Apr (all 5 stores) and May (ROA), open VP_BONUS_FINAL_rebuilt.xlsx with openpyxl and update column D ("2026 Revenue") in the "2025 compared to Bonus" sheet for each affected store block (Culpeper rows 5-16, Harrisonburg 21-32, Roanoke 37-48, Lexington 53-64, Waynesboro 69-80 — row = 5 + month_index for Culpeper's block, similarly offset for others; January is the first row of each block). Replace the formula/placeholder with the real hardcoded number, and add an openpyxl Comment on each changed cell documenting: "Corrected <date> — Revenue = Sales Revenue (Profit) + Interest and Fees Total from Bravo end-of-month report dated <archive date>. Was: <old formula/value>." Use GREEN fill (C6E0B4) for these corrected real-data cells. Leave June/July alone (already real / not yet arrived). After all edits, recalculate the workbook with LibreOffice: `soffice --headless --convert-to xlsx --outdir /tmp/recalcN <path>` (use a fresh /tmp/recalcN dir each time, then copy the output back over the original — direct in-place conversion fails). Verify zero formula errors (scan all cells for values starting with "#", excluding the known false-positive header "# Stores Hit Bonus"). Save.

=== PART 2: Pull 2025 Gold (dwt) scrap weights via live Bravo, all 12 months, all 5 stores ===

IMPORTANT: Do not start this part until Part 1's Bravo-automation polling is completely finished (the automated pipeline and manual computer-use navigation use the SAME Parallels VM and will collide if run concurrently).

Goal: build a YOY Gold-weight trend (2025 vs 2026, monthly, per store). The 2026 Jan-June figures are ALREADY KNOWN — do not re-pull them, just reuse these exact figures (dwt, already vetted this session):

Culpeper: Jan 226.74, Feb 260.39, Mar 206.87, Apr 187.33, May 240.55, Jun "148.02+ (bucket still open, Threshold Met=Yes)"
Harrisonburg: Jan 67.23, Feb 76.04, Mar 231.62, Apr 55.75, May 92.45, Jun "25.89+ (bucket still open, PENDING)"
Roanoke: Jan 68.68, Feb 58.03, Mar 67.11, Apr 78.01, May 59.31, Jun "42.37+ (bucket still open, PENDING)"
Lexington: Jan 73.15, Feb 101.28, Mar 105.15, Apr 56.67, May 65.57, Jun "23.50+ (bucket still open, PENDING)"
Waynesboro: Jan 96.52, Feb "NO BUCKET FOUND", Mar 109.43, Apr 104.68, May 103.83, Jun 101.93

You need the SAME figure for 2025, Jan through Dec, for all 5 stores — pulled live from Bravo's "Scrap Refining Process" screen (NOT automatable via the pipeline — no scrap/gold report handler exists there, confirmed). Use the bravo-store-cycle skill to log into each store. Navigate: Dashboard → Inventory (sidebar) → "Scrap Refining Process" → dialog listing buckets (Created On | Name | Status | Status Date). Use the Status column filter funnel to toggle between OPEN (current, unlikely relevant for 2025) and CLOSED (historical — this is what you need for all of 2025) buckets. The dialog repositions every time it's reopened — re-screenshot before clicking anything. Double-click a bucket row to select it, click "Ok" (if you land on an empty Inventory search screen instead of the detail, click "Scrap Refining Process" again to get to "Scrap Bucket Detail," which shows "Combined Metal Weight" — that's the dwt figure you want). Click "Done" to exit back out.

Each store names/dates its buckets differently — expect this and document your methodology transparently per store rather than guessing:
- Watch for a store combining two variants per month (e.g. "...GOLD..." and "...GOLD W/STONES..." or "...NO STONES..." for the same month) — SUM both variants' Combined Metal Weight for that month's total, same as was done for 2026.
- If a store's bucket name embeds a different calendar month than its Created On date (seen last time with Waynesboro, offset by about a month), attribute the dwt to the month named IN the bucket, and say so in your documentation.
- If a month genuinely has no bucket at all, write "NO BUCKET FOUND" for that store/month rather than guessing or leaving it blank, and note it clearly.
- Threshold for context (not required for this report, but useful): 100 dwt/month has historically been the bonus qualifier bar, if you want to flag which months cleared it.

Record all 60 data points (5 stores × 12 months) in a simple table as you go so you don't lose progress if interrupted.

=== PART 3: Build the YOY report spreadsheet ===

New standalone file (do NOT edit VP_BONUS_FINAL_rebuilt.xlsx for this) — e.g. `Gold_Weight_YOY_2025_vs_2026.xlsx` — saved to the same outputs location as VP_BONUS_FINAL_rebuilt.xlsx (find it via recent file search if the exact path isn't obvious; check Google Drive too). One tab per store (Culpeper, Harrisonburg, Roanoke, Lexington, Waynesboro) with columns: Month | 2025 dwt | 2026 dwt | YoY Variance ($ dwt) | YoY Variance (%) | Notes (flag "bucket still open" / "no bucket found" months clearly, and note these are partial/estimate where applicable). Add a company-wide summary tab totaling all 5 stores per month for both years plus variance. Use plain, readable formatting (bold headers, currency-style number format for dwt to 2 decimals, a simple line or bar chart per store if straightforward with openpyxl, otherwise a numbers-only table is fine). Recalculate with LibreOffice and verify no formula errors, same process as Part 1.

=== PART 4: Publish to Slack ===

Joshua already created the destination channel: **#gold-trend-** (note the trailing hyphen is part of the actual name), a private channel, ID **C0BJ8SYTVBN**, created by Joshua Davis. Use slack_send_message with channel_id "C0BJ8SYTVBN" directly (no need to search for it). Post a concise summary of the YOY findings (which stores/months are trending up or down vs last year in Gold dwt, any notable gaps like Waynesboro's missing Feb bucket in one or both years, overall company-wide trend), and share the finished spreadsheet (present_files or whatever file-sharing mechanism is available in this session) so it's downloadable from that channel. Also mention in the message that the revenue-column fix (Part 1) was applied to VP_BONUS_FINAL_rebuilt.xlsx if relevant context is useful, but keep the Slack post focused on the Gold trend since that's the channel's purpose.

=== Reporting back ===
At the end, whether fully complete or partially blocked, leave a clear final written summary in your own final message covering: what revenue figures were corrected (old vs new, per store/month), what 2025 Gold figures were found (and any gaps/quirks per store), where the final YOY report file lives, and confirmation it was posted to #gold-trend-. If anything was blocked (e.g. Bravo login failed even with the given password, or a report never arrived from the pipeline), say so plainly rather than guessing or fabricating a number.