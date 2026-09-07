---
name: monthly-gun-audit-report
description: Read the 5 monthly gun audit forms from Slack, update the Valley Pawn Trends Google Sheet, and post a summary in #monthly-gun-audit built by Compliance/bin/gun_audit_format.py (never hand-written, never carrying a Drive link). Deadline is the 15th of each month (changed from 5th starting April 2026 — historical data before Apr 2026 uses old 5th deadline). Submissions on or before the 15th = on-time (✓); after the 15th = Late.
model: claude-sonnet-5
---

> ⚠️ **FAILURE ALERT POLICY (still binding):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua's DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium.
>
> ⚠️ **FIELD COMMUNICATION STANDARD v3 (binding — read in full before posting anything to a team channel or employee DM):** `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/FIELD_COMMUNICATION_STANDARD.md`. Summary: run the routing test (is this something a clerk needs to know/act on today — if no, it's internal, it does not go to the field); plain everyday language only, no tool/system/pipeline names (never say Bravo, Cowork, Chekkit, Gusto, Brevo, QBO, Publer, "pipeline," "handler," "watchdog," "sync," "CSV," "export"); no file paths, doc IDs, task IDs, or spreadsheet cell/column refs in the posted text; no meta-commentary about the automation itself ("verified against," "supersedes," "this is a manual test run," "pulled automatically from"); lead with the one-line takeaway; ~100 words max for a routine post; no signature footers. If anything later in this file conflicts with this standard, this standard wins.



> ⚠️ **FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE.** If this task fails, errors out, or cannot complete its intended work for any reason, DO NOT post anything to Slack — no error messages, no partial results, no "I couldn't finish" notices. Joshua reviews every run inside Claude to confirm success or failure, so a failed run must stay completely silent on Slack. Only post to Slack once the task has genuinely completed the work it was designed to do. Posting failure or error noise clutters Slack and reflects poorly on the team.

You are updating the monthly gun audit trend report for Valley Pawn. This task runs on the 16th of each month. Stores submit by the 15th (submissions on or before the 15th are on time; after the 15th is Late). The old 5th/7th dates are dead — do not reintroduce them. Follow these steps:

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

## CONTEXT

Valley Pawn has 5 pawn shop locations. Each location submits a handwritten gun audit form monthly to the Slack channel #monthly-gun-audit. The forms contain: Store name, Date, Auditor, # Forms Checked, # Errors Found, # Errors Corrected, Notes, and Signature.

**Locations and responsible people:**
- Waynesboro — Chad
- Harrisonburg — Andrew Clark
- Culpeper — Martin D. / Bree Grayson
- Roanoke — Benjie Moore
- Lexington — Uriah

**Slack channel:** #monthly-gun-audit (Channel ID: C07CPN020G0, Workspace: T03BL4W1DCL / Valley Pawn)

**Google Sheet:** "Valley Pawn Trends" — https://docs.google.com/spreadsheets/d/1sLid9zjLUkH-B8MOE5Fr_aemw35bxyAbtuUz4BTVA6s/edit

The spreadsheet has 4 tabs:
1. **Submission Tracker** — columns: Location, Responsible, then 12 monthly columns. Values are ✓ (on-time), Late, or — (missing).
2. **Audit Metrics** — columns: Location, Month, Forms Checked, Errors Found, Errors Corrected, Error Rate. One row per location per month.
3. **Location Summary** — columns: Location, Responsible, Total Submitted, On-Time, Late, Missing, Submission %, Compliance Rating.
4. **Key Takeaways** — columns: Finding, Detail. High-level observations.

The report uses a **rolling 12-month window**. Each month, add the new month's data and drop the oldest month.

## STEPS

1. **Read the Slack channel** (#monthly-gun-audit, C07CPN020G0) for new audit form posts from the current month. Use the Slack MCP tools (slack_read_channel, slack_read_thread) to find messages with attached images or PDFs of completed audit forms. Look for posts from the past ~5 weeks.

2. **Extract data from each form.** For each of the 5 locations, record:
   - Forms Checked (number)
   - Errors Found (number)
   - Errors Corrected (number)
   - Whether the submission was on time (on or before the 15th), late, or missing
   You may need to open form images in Chrome to read handwritten data. Use the Claude in Chrome tools (navigate, read_page, screenshot, zoom) to view Slack file attachments.

3. **Update the Google Sheet** "Valley Pawn Trends":
   - Open https://docs.google.com/spreadsheets/d/1sLid9zjLUkH-B8MOE5Fr_aemw35bxyAbtuUz4BTVA6s/edit in Chrome
   - On the **Submission Tracker** tab: Remove the oldest month column, add the new month column with ✓/Late/— for each location
   - On the **Audit Metrics** tab: Remove the 5 oldest-month rows (one per location), add 5 new rows with the current month's data and computed error rates
   - On the **Location Summary** tab: Recalculate totals, submission %, and compliance ratings based on the updated 12-month window
   - On the **Key Takeaways** tab: Update findings with any new observations (new trends, improvements, concerns)
   - Use JavaScript clipboard (navigator.clipboard.writeText + Ctrl+V) to paste TSV data efficiently

4. **Build the Slack message with the formatter — DO NOT HAND-WRITE THIS POST.**

   Write the extracted numbers to a JSON file and run:

   ```
   python3 "/Users/joshuadavis/Documents/Claude/Projects/Compliance/bin/gun_audit_format.py" --file /tmp/gun_audit_<YYYY-MM>.json
   ```

   Input shape (all 5 stores, always; a store that did not submit gets `"submitted": null`):

   ```json
   {"period": "August 2026", "deadline": "2026-09-15",
    "stores": [{"store": "Culpeper", "person": "Bree", "submitted": "2026-09-03",
                "forms_checked": 133, "errors_found": 4, "errors_corrected": 0}, ...]}
   ```

   - **exit 0** → post stdout to #monthly-gun-audit (C07CPN020G0) **verbatim**, nothing added,
     nothing removed. Post it directly with slack_send_message (this is a routine data post).
   - **exit 2** → post NOTHING. Put the stderr reason in the run record and send Joshua ONE plain
     line in his DM. Never post a partial or caveated table (Rule 18).

   The formatter owns the wording, the ordering, the on-time/late calls and the error-rate math.
   It refuses to emit a message whose numbers are internally impossible (e.g. errors_found larger
   than forms_checked — the mis-mapped-column bug), and it refuses to emit any Drive/Sheets link.

   **NEVER put the Google Sheet link (or any Drive link) in this channel** — store staff are
   members, and no employee gets Drive content in any form (BUSINESS_OS Rule 13). The sheet stays
   an internal reference.

5. **Chase uncorrected errors.** If the formatter's "Still to fix" section is non-empty, DM each
   affected store manager directly (not the channel) asking for the correction status on those
   specific forms, and note it in the run record. Do not chase in the channel.

## IMPORTANT NOTES
- Audit forms are usually handwritten on paper and photographed or scanned as PDFs
- Waynesboro (Chad) typically submits clean PDFs; others submit photo images
- Preston Peters is the manager who monitors compliance and sends reminders
- Error Rate = (Errors Found / Forms Checked) × 100
- If a location has not submitted by the 15th, it is Late. If still nothing on the 16th, the post says it is still needed.
- The Google Sheet file upload is blocked; you must edit the sheet directly in Chrome using clipboard paste