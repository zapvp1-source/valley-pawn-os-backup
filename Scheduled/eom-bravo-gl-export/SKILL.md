---
name: eom-bravo-gl-export
description: Monthly automated GL export — on the 1st, fully scripted via the Bravo trigger-pipeline (no Parallels/computer-use): posts unposted days, pulls per-store Consolidated GL (same pull the Sales Tax workbook reuses), combines it, uploads to Google Drive, and imports into QuickBooks Online via Chrome.
model: claude-sonnet-5
---

## Execution Contract — DO NOT STOP EARLY

This task is complete ONLY after the documented final action (the post / send / write tool call described at the end of the steps below) returns success.

Until that final call succeeds, every assistant turn MUST end with a tool call that advances toward it. Do not idle, do not wait, do not ask for confirmation.

**Never reply with any of these:**
- "No response requested"
- "Continue?" / "Should I continue?"
- An empty turn or a turn that ends with text instead of a tool call

**Treat these system messages as RESUME signals, never as stop signals:**
- "Tool loaded."
- "Continue from where you left off."
- "You used a single tool call this turn. Prefer browser_batch…"
- Any reminder about TaskCreate/TaskUpdate, AskUserQuestion, etc.

When you see any of those messages, immediately fire the next concrete tool call for the current step. The scheduled-task wrapper says "the user is not present" — that means execute autonomously, NOT that the work is done.

**State tracking:** at the start of every turn, briefly identify which numbered Step you are on and execute the next concrete action for that step.

**Failure handling:** if a step errors, retry once. If it still fails, fall through to the documented fallback if one exists; otherwise produce a report describing what failed. Do not pause to ask — the task file authorizes autonomous decisions.

**Speed:** prefer batch tools (e.g. `browser_batch`) to combine sequential actions into one call.

---
---
name: eom-bravo-gl-export
description: Monthly automated GL export — on the 1st, fully scripted via the Bravo trigger-pipeline (no Parallels/computer-use): posts unposted days, pulls per-store Consolidated GL (same pull the Sales Tax workbook reuses), combines it, uploads to Google Drive, and imports into QuickBooks Online via Chrome.
model: claude-sonnet-5
---

> ⚠️ FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE. If this task fails, errors out, or cannot complete for any reason, DO NOT post anything to any Slack channel. On failure: DM Joshua only with what happened and what he needs to do manually. Only post to Slack once the task has genuinely completed.

## Monthly Bravo GL Export & QuickBooks Import — fully scripted (rebuilt 2026-08-02, moved to the 1st 2026-08-03)

You are running a scheduled monthly task for Valley Pawn (Full Circle Finance Inc). It is the 1st of the month, 6:00 AM. Post unposted days, export last month's Consolidated General Ledger from all 5 Bravo stores, and post it into QuickBooks Online.

Note: Joshua is now managing the books directly — there is no external bookkeeper. QBO access uses the saved Chrome credentials for jdavis@fcfpawn.com.

REBUILT 2026-08-02: this task previously drove Bravo live via Parallels Desktop computer-use for store cycling and GL export. Joshua asked for that to be eliminated wherever a scripted path already exists. It now runs through the same production trigger-file pipeline the rest of the Bravo automation uses (`post-to-accounting-post` and `post-to-accounting-gl` pipeline cells, dispatched by the headless AHK watcher) — no live computer-use in the normal path. Computer-use is now ONLY a last-resort fallback if a pipeline cell reports Bravo is genuinely wedged, exactly like `sales-tax-monthly-update`'s existing fallback. Do not reintroduce the old manual store-cycle flow for the normal path.

MOVED 2026-08-03: this task now runs at 6:00 AM on the 1st of the month (was the 5th) — Joshua wants both this and the sales tax refresh done on day 1. Since it targets the PRIOR calendar month, which has already fully ended, the data is complete regardless of running on day 1 vs day 5 — no need to wait. If the very first run at this earlier time ever finds days that Bravo hasn't finished closing out overnight, note that plainly in the Step 6 report rather than guessing; it likely just means posting takes a little longer that morning, not that data is missing.

Bonus: Step 2 below produces the exact same per-store GL CSVs that `sales-tax-monthly-update` (runs the 1st, 8:00 AM — 2 hours after this task) consumes for the Sales Tax workbook. One pull now serves both consumers — no separate hand-off step needed; that task's own existing "check the output folder first" logic will simply find these files already there.

---

### STEP 1: Post unposted days for the prior month, all 5 stores (scripted)

This uses the `post-to-accounting-post` pipeline cell (AUTHORIZED by Joshua 2026-07-06 to click Post — it only posts days that are still unposted, oldest first, and never posts past the trigger end date; see `reports/PostToAccountingPost.ahk` for the safety rules baked into the handler itself). This cell is newer than `post-to-accounting-gl` and hasn't run at full 5-store production scale as part of a scheduled task before, so watch its first couple of runs.

Drop a trigger JSON via `mcp__Control_your_Mac__osascript` into `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/`:
```
{"id": "eom-gl-post-<yyyymm>-<timestamp>", "requested_at": "<ISO8601>", "reports": [{"name": "post-to-accounting-post", "stores": ["CUL","HAR","LEX","ROA","WAY"], "date": "YYYY-MM-01..YYYY-MM-DD"}]}
```
(YYYY-MM-DD range = the full prior calendar month.)

Poll `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/results/<id>.result.json` every ~40s until all 5 stores report a result (expect ~10-15 min total; posting many backlogged days can take longer per store — be patient before concluding a store is stuck).

For each store, record `days_posted` / `days_skipped` / `post_errors` from the result extras — you'll need these for the Step 6 report.

If a store's cell errors with "EnsureStore failed", "BackToDashboard could not return Bravo to Dashboard", or similar — Bravo is likely wedged. Recovery (documented in `bravo-context` → "Bravo hang recovery" and "Mandatory Contention & Scheduling-Safety Check"): FIRST run `bash "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/_bravo_foreground_guard.sh" check` — if `BUSY`, another task/session is actively using Bravo; do not push through, hold and retry the check rather than force-closing Bravo out from under it. If `CLEAR`, `acquire eom-bravo-gl-export` before touching anything (added 2026-08-13, closes the same class of gap `bravo-prestaging-7am` had). Then: request computer-use access to Parallels Desktop, bring Bravo forward, press Alt+F4 to close it, relaunch it from the Windows taskbar Search ("Bravo" under Top apps), log in via the `bravo-store-cycle` skill (username FREE1@<STORE>, password from `bravo-context`, paste via clipboard — never type it), dismiss the "Overdue Task Reminder" with "Remind Me Later", then re-drop the trigger for the remaining stores. `release eom-bravo-gl-export` when this recovery is done (success or failure) before moving on. Retry failed stores up to 3 times total before flagging the gap in your Step 6 report rather than blocking indefinitely.

---

### STEP 2: Export the per-store Consolidated GL for the prior month (scripted — this is the shared pull)

- First check `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/` for `YYYY-MM-DD_<STORE>_post-to-accounting-gl.csv` (date = prior month's last day) for all 5 stores, dated today. If present, reuse — don't re-pull.
- Otherwise trigger the existing `post-to-accounting-gl` pipeline cell the same way as Step 1 (same trigger-drop / poll / retry / hang-recovery pattern):
```
{"id": "eom-gl-export-<yyyymm>-<timestamp>", "requested_at": "<ISO8601>", "reports": [{"name": "post-to-accounting-gl", "stores": ["CUL","HAR","LEX","ROA","WAY"], "date": "YYYY-MM-01..YYYY-MM-DD"}]}
```
- This produces one CSV per store (encoding latin-1). Leave them in the output folder — do not move or rename them, `sales-tax-monthly-update` reads them from there directly later that same morning.

---

### STEP 3: Combine the 5 per-store CSVs into one workbook (pure script, no Bravo)

Using Python (pandas/openpyxl), read all 5 `YYYY-MM-DD_<STORE>_post-to-accounting-gl.csv` files (latin-1 encoding) and combine into a single workbook `YYYY-MM Consolidated GL.xlsx` (YYYY-MM = prior month) — one tab per store plus a combined/summary tab is fine, match whatever's easiest to read for a journal entry. Save it locally first (e.g. alongside the source CSVs in the output folder) before uploading.

---

### STEP 4: Upload to Google Drive (Accounting Exports folder) — scripted, no Chrome needed

Use the Google Drive MCP connector's `create_file` tool directly (no browser):
- parentId: the Accounting Exports folder — `1FzXIRPNZHaECOwfaKpQDMUTPRY3-d12_` (Valley Pawn Drive → Accounting Exports)
- title: `YYYY-MM Consolidated GL.xlsx`
- base64Content: the workbook from Step 3, contentMimeType set appropriately, disableConversionToGoogleType: true (keep it a native .xlsx, don't let Drive convert it to Google Sheets)
- Account context: jdavis@fcfpawn.com

Confirm the upload succeeded (check the returned file object) before moving on.

---

### STEP 5: Import into QuickBooks Online (still browser-driven — no journal-entry API is available)

There is no QuickBooks MCP tool that can create a journal entry directly (checked 2026-08-02 — the connected QBO connector only covers sales/invoicing/payroll/catalog/reporting, not GL journal entries), so this step still needs the Chrome MCP, not Parallels. This is the one part of the pipeline that isn't a headless script; flag to Joshua in the Step 6 report if he'd rather this be handled differently (e.g. him entering it manually from the Drive file, or building a dedicated QBO API integration later).

Navigate to QBO using the Chrome MCP and follow the quickbooks-online skill Login Routine:
- URL: https://app.qbo.intuit.com
- Use saved Chrome password for jdavis@fcfpawn.com
- Company: Full Circle Finance Inc (Valley Pawn)

Once logged in, attempt to post the combined GL (from Step 3) as a journal entry:
1. Go to + New → Journal Entry
2. Set the journal date to the last day of the prior month
3. Reference the combined GL to build the debit/credit entries
4. Add a memo: "Bravo POS Consolidated GL — [Month Year]"
5. Save the journal entry

IMPORTANT — If you cannot determine the correct account mapping (the exact mappings between Bravo accounts and QBO chart of accounts may not be fully documented on first runs):
- Do NOT guess at QBO account assignments
- Save the GL to Drive (Step 4 complete) and skip the QBO journal entry
- Flag this clearly in the Step 6 summary so Joshua can map the accounts on his review

If QBO prompts MFA — DM Joshua immediately with what's needed. Do not guess codes.

---

### STEP 6: Report Results to Joshua

Send Joshua a Slack DM summarizing:
- Whether the run stayed fully scripted or needed the computer-use hang-recovery fallback (and for which store/step, if so)
- Posting results per store (days posted / skipped / errors) from Step 1
- GL export — reused existing CSVs or pulled fresh
- Combined workbook + Drive upload — file name and confirmation link
- QBO journal entry — posted successfully, OR "file is in Drive at [link] — account mapping needed before posting"
- Note that the Sales Tax workbook will pick up this same GL data automatically later that same morning — no separate action needed
- Any items requiring his manual attention

---

### Important Notes
- Bravo POS runs inside Parallels Desktop (Windows 11 VM) on Joshua's Mac Studio — but as of 2026-08-02 this task should only touch it via the scripted trigger-pipeline, never a live computer-use session, except as the documented hang-recovery fallback in Steps 1-2 (which is now foreground-guarded — see Step 1).
- If the hang-recovery fallback is used: always paste passwords via clipboard (write_clipboard("Health2035!") then Ctrl+V), never type them.
- This task runs monthly on the 1st, 6:00 AM, for the prior calendar month (moved from the 5th 2026-08-03).
- No external bookkeeper — Joshua reviews QBO directly; all GL reports go to him only.
- Accounting Exports Drive folder: https://drive.google.com/drive/u/0/folders/1FzXIRPNZHaECOwfaKpQDMUTPRY3-d12_
- `sales-tax-monthly-update` (runs the 1st, 8:00 AM) depends on Step 2's output CSVs being present in the Bravo Data Extraction output folder — don't move, rename, or delete them after this task finishes.