---
name: eom-bravo-gl-export
description: Monthly automated GL export — on the 5th, cycle all 5 Bravo stores to verify accounting posting for the prior month, export the Consolidated General Ledger, upload to Google Drive (Accounting Exports), and import into QuickBooks Online.
model: claude-sonnet-5
---

> ⚠️ FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE. If this task fails, errors out, or cannot complete for any reason, DO NOT post anything to any Slack channel. On failure: DM Joshua only with what happened and what he needs to do manually. Only post to Slack once the task has genuinely completed.

## Monthly Bravo GL Export & QuickBooks Import

You are running a scheduled monthly task for Valley Pawn (Full Circle Finance Inc). It is the 5th of the month. Export last month's Consolidated General Ledger from all 5 Bravo stores and post it into QuickBooks Online.

Note: Joshua is now managing the books directly — there is no external bookkeeper. QBO access uses the saved Chrome credentials for jdavis@fcfpawn.com.

---

### STEP 0: Concurrency guard (added 2026-07-07)
This task drives Bravo live via computer-use, which will collide with the trigger-pipeline watcher or the health-gate script if either is mid-run. Check first, and hold a flag while you work so nothing else starts on top of you.

Check:
```
do shell script "'/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/_bravo_foreground_guard.sh' check"
```
- If it prints `CLEAR`: immediately acquire the flag, then continue to Step 1:
  `do shell script "'/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/_bravo_foreground_guard.sh' acquire eom-bravo-gl-export"`
- If it prints `BUSY:...`: wait 5 minutes (a fresh osascript call — do not sleep >18s in one call) and check again. If still BUSY after one retry, DM Joshua: "Monthly GL export delayed — Bravo is busy (<reason>). Rescheduling automatically." then reschedule this task's own `fireAt` to +30 minutes via `mcp__scheduled-tasks__update_scheduled_task` and exit. Never force through a busy Bravo.

Whenever this task ends — success, failure, or the MFA-stop below — always release the flag:
`do shell script "'/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/_bravo_foreground_guard.sh' release eom-bravo-gl-export"`

### STEP 1: Notify Joshua and Request Computer Access

Send Joshua a Slack DM (search for Joshua Davis):

"Hey — starting the monthly GL export now (5th of the month). I'll cycle all 5 Bravo stores, verify accounting posting for last month, export the Consolidated GL, and upload it to QuickBooks. Approve the computer access dialog when it pops up and I'll get started."

Then immediately call request_access for Parallels Desktop (with clipboardWrite: true).

---

### STEP 2: Cycle All 5 Stores & Verify Accounting Posting

Use the bravo-store-cycle workflow to log into each store. Order: CUL, HAR, LEX, ROA, WAY.

Credentials:
- Username: FREE1@WAY (pre-filled on most screens; WAY store shows just FREE1)
- Password: Health2035! — always paste via clipboard: write_clipboard("Health2035!") then Ctrl+V

For each store, after reaching the Dashboard:
1. Navigate to Post to Accounting (left sidebar or Accounting section)
2. Verify every day of the previous calendar month shows as posted
3. If any days are unposted — post them now
4. Take a screenshot documenting the posting status
5. Note any days that errored or could not be posted

After verifying, lock session and cycle to next store:
Dashboard → Lock Session → Global Access → Store Selector → Next store → Login → Dashboard

---

### STEP 3: Export the Consolidated General Ledger

After all 5 stores are verified:
1. Navigate to Reports in Bravo
2. Find Consolidated General Ledger
3. Set date range: first day through last day of the previous month
4. Select All Stores (consolidated view)
5. Run the report
6. Export — prefer Excel/CSV. If no export button, take screenshots and extract into a structured file.
7. Save as: YYYY-MM Consolidated GL.xlsx (where YYYY-MM = prior month)

---

### STEP 4: Upload to Google Drive (Accounting Exports Folder)

Upload the GL file to:
- Folder: Valley Pawn Drive → Accounting Exports
- Direct URL: https://drive.google.com/drive/u/0/folders/1FzXIRPNZHaECOwfaKpQDMUTPRY3-d12_
- Account: jdavis@fcfpawn.com

Use Chrome MCP:
1. Navigate to the Accounting Exports folder URL
2. Upload the file
3. Confirm the upload completed

File naming: YYYY-MM Consolidated GL.xlsx

---

### STEP 5: Import into QuickBooks Online

Navigate to QBO using the Chrome MCP and follow the quickbooks-online skill Login Routine:
- URL: https://app.qbo.intuit.com
- Use saved Chrome password for jdavis@fcfpawn.com
- Company: Full Circle Finance Inc (Valley Pawn)

Once logged in, attempt to post the Bravo GL as a journal entry:
1. Go to + New → Journal Entry
2. Set the journal date to the last day of the prior month
3. Reference the GL export to build the debit/credit entries
4. Add a memo: "Bravo POS Consolidated GL — [Month Year]"
5. Save the journal entry

IMPORTANT — If you cannot determine the correct account mapping (the exact mappings between Bravo accounts and QBO chart of accounts may not be fully documented on first runs):
- Do NOT guess at QBO account assignments
- Save the GL to Drive (Step 4 complete) and skip the QBO journal entry
- Flag this clearly in the Step 6 summary so Joshua can map the accounts on his review

If QBO prompts MFA — DM Joshua immediately with what's needed. Do not guess codes.

Release the concurrency flag now that Bravo/computer-use work is done: `do shell script "'/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/_bravo_foreground_guard.sh' release eom-bravo-gl-export"`

### STEP 5.5: Kick off the per-store GL pull for the Sales Tax workbook (added 2026-07-14)

The `sales-tax-monthly-update` task (runs the 6th) needs this same Consolidated GL data broken out per-store as structured CSVs, not the single all-stores Excel export from Step 3. Rather than have that task independently drive Bravo again on its own day (a second monthly touch, doubling hang risk), this task hands it fresh data proactively.

Now that the concurrency flag is released and Bravo is free of your live/manual session, drop ONE trigger JSON for the automated pipeline. This does NOT re-enter Bravo yourself — the watcher process (which drives Bravo independently via AHK) picks it up on its own, so there's no conflict with the flag you just released:

Via `mcp__Control_your_Mac__osascript`, write a file to `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/` containing:
```
{"id": "eom-gl-export-taxfeed-<yyyymm>-<timestamp>", "requested_at": "<ISO8601>", "reports": [{"name": "post-to-accounting-gl", "stores": ["CUL","HAR","LEX","ROA","WAY"], "date": "YYYY-MM-01..YYYY-MM-DD"}]}
```
(YYYY-MM = the prior month you just exported, matching Step 3.)

This is fire-and-forget — do not poll or wait for it, and do not block Step 6 on it. The watcher will process it independently over the following ~10-15 minutes, well ahead of `sales-tax-monthly-update`'s run the next morning. If the trigger drop itself fails (e.g. folder unwritable), note it in the Step 6 summary but do not treat it as a task failure — `sales-tax-monthly-update` has its own fallback to pull this data itself if it finds nothing waiting when it runs.

### STEP 6: Report Results to Joshua

Send Joshua a Slack DM summarizing:
- Per-store posting verification status (which stores had all days posted, any exceptions)
- GL export — success or what format was exported
- Drive upload — file name and confirmation link
- QBO journal entry — posted successfully, OR "file is in Drive at [link] — account mapping needed before posting"
- Per-store GL pull for the Sales Tax workbook — trigger dropped successfully (or note if it failed to drop)
- Any items requiring his manual attention

---

### Important Notes
- Bravo POS runs inside Parallels Desktop (Windows 11 VM) on Joshua's Mac Studio
- Always use clipboard paste for passwords: write_clipboard("Health2035!") then Ctrl+V
- Take screenshots frequently to document UI state
- This task runs monthly on the 5th for the prior calendar month
- No external bookkeeper — Joshua reviews QBO directly; all GL reports go to him only
- Accounting Exports Drive folder: https://drive.google.com/drive/u/0/folders/1FzXIRPNZHaECOwfaKpQDMUTPRY3-d12_
- Step 5.5 (added 2026-07-14) feeds `sales-tax-monthly-update` so that task no longer needs to drive Bravo itself under normal conditions — see that task for the consumer side of this handoff.