# Policy Day Runner — exact steps (Gusto rail since 2026-10-21) (read by the scheduled task "Policy Day runner", daily 8:41 AM ET)

Rules in `POLICY_CADENCE.md` govern. This file is the HOW. Unattended: act, don't ask. Paths are relative to
`~/Documents/Claude/Projects/`. Base = `Human Resources/policy_bundles/`.

## Fixed facts
- Signatures go through **Gusto** (Team document with signature, current team + all future hires) using the `gusto-access` skill. Company UUID 15bc2823-564f-4c1a-8464-9b0e7d79d3e8.
- **Gusto sign-in:** open https://app.gusto.com/payroll_admin in Claude in Chrome. On the login page click "Sign in with Google" and pick jdavis@fcfpawn.com. Never type a password or a code; never use a password manager. If a password or code is asked for: stop, add ONE line to `Life OS/HUMAN_QUEUE.md` ("Gusto wants a code — sign in once with 'Sign in with Google' in Chrome on the Mac and tick Remember this device"), retry next run.
- Slack (always through the fleet outbox: write `<name>.txt`, then `<name>.json` = {"channel": "...", "file": "<host path of the .txt>"} into `Valley Pawn OS/fleet/outbox/`; never call slack_send_message in a scheduled run):
  #policy-announcements `C03BHQ9RLR0` · #preston-claude `C0BGXSTT4TY` · Joshua `U03BB52MDSA`.
- Fleet dry-run guard before any outbox write: `python3 "Valley Pawn OS/bin/vp_dryrun.py" status` — exit 0 (armed) → write to `Valley Pawn OS/fleet/test_output/` instead.
- Email to Joshua: Gmail connector, from and to jdavis@fcfpawn.com.
- State file per update: `state/<YYYY-MM>.json` (create if missing):
  {slug, preview_sent_at, preview_subject, approved_at, approval_evidence, dropped_items[], sent_at, gusto_template_id,
   request_count, signers:[{name,status,signed_at}], slack_posted_at, preston_list_sent_at, manuals_published, closed_at, notes[]}
- Business day = Mon–Fri excluding New Year's Day, Memorial Day, July 4, Labor Day, Thanksgiving, Christmas.
  Policy Day = 1st business day of the month. Sign-by = the 10th (next business day if not one). Preston day = the 15th (same rule).
  The manifest's own `policy_day` / `sign_by` / `preston_day` override (November 2026: Wed 11/4 — Academy launch day — sign by Wed 11/4, unsigned list to the Market Manager Fri 11/6).

## Each run: figure out the phase, do only that, write the state file, end
Let NEXT = the update for next month (built on/after the 26th), CUR = the update whose Policy Day is this month.

### A. Preview (today ≥ 26th and NEXT has no preview_sent_at)
1. Sweep for approved-but-unsent staff-facing items since the last update: `POLICY_QUEUE.md`; `Compliance/FIELD_RELEASE_INVENTORY_*.md` (newest);
   `Life OS/OPEN_ITEMS_REGISTER.md`; `Valley Pawn OS/CHANGELOG.md` (last 35 days); Slack #policy-announcements (last 35 days, anything posted
   outside Policy Day = a leak: note it); `Human Resources/` new *_FINAL / policy PDFs (last 35 days); `Compliance/OBLIGATIONS.json` rows that
   say staff must sign or be told. Add any missing item to POLICY_QUEUE.md (status as found; `approved` only if Joshua's approval is on record).
2. Items in = queue rows with status `approved` (or `approved-pending` gated on Joshua) dated ≤ the 25th. `held`, `draft`, `plan only` stay out.
3. Write `manifests/<YYYY-MM>.json` (same schema as 2026-11.json): ≤12 `whats_new` lines in plain words (8th-grade, no tool names);
   each policy in house format (box + 3 lines); `handbook`/`pp` = current FINAL versions in `Human Resources/` with `handbook_new`/`pp_new`
   true only if the version changed since the last sent update; reminders of existing rules go in `whats_new` as "Reminder: …".
4. Run `python3 build_bundle.py manifests/<slug>.json` → `out/<slug>_Policy_Update.pdf` (+ page PNGs). Read every page image: each line must match the manuals and the source policy; the last pages are the acknowledgment (HR-2026-04 Rev2 or successor when a manual version changes, otherwise the generated monthly ack).
5. Academy check: search `Training Program/academy/lessons/*.json` for each item's key terms; list lessons that teach the old rule.
   Append them to `Training Program/academy/OPEN_ITEMS.md` as "Policy Update <Month>: update lesson X before <Policy Day>".
6. Preview to Joshua: ONE email (from/to jdavis@fcfpawn.com), subject `Policy Update — <Month> — reply "approve"`, with the Drive link to
   `out/<slug>_Policy_Update.pdf` (Human Resources is Drive-synced; find the file id with the Drive connector) and, in the body: Policy Day + sign-by;
   what's in (one line each); what's held or waiting and why; the exact #policy-announcements text; the exact 15th message to Preston (template below);
   Academy lessons that change; anything that leaked outside Policy Day last month. Last line: `Reply "approve" to send it as shown,
   "approve without <item>" to drop something, or reply with changes.` Empty queue → one short email "Nothing new for <Month> — nothing will be sent", mark closed.

### B. Approval watch (preview sent, not approved, today ≤ the 7th of CUR's month)
1. Gmail: the preview thread, plus `from:jdavis@fcfpawn.com subject:"Policy Update — <Month>"` newer than preview_sent_at. Approval =
   a later message in that thread from Joshua whose first word is approve/approved/yes/send it. "without X" → drop X (state dropped_items,
   rebuild). Changes requested → apply, rebuild, send a revised preview in the same thread, keep waiting. A Cowork session may also
   record approval directly in the state file (approval_evidence "chat <date>: <his words>").
2. Policy Day reached and no approval → send nothing; email Joshua once that day: "The <Month> Policy Update is waiting on your
   approve — nothing has gone out." After the 7th with no approval: move the items back to `approved` for the next month, email once, close.

### C. Send (approved AND today ≥ policy_day AND no sent_at)
1. Gusto sign-in (Fixed facts). Duplicate guard: GET /api/companies/15bc2823-564f-4c1a-8464-9b0e7d79d3e8/document_templates — a template named
   "Policy Update — <Month YYYY>" already approved → record its id, skip the upload.
2. Upload `out/<slug>_Policy_Update.pdf` as a **Team document** named "Policy Update — <Month YYYY>", signature required, signature field on the
   acknowledgment's employee signature line (gusto-access skill: Ghostscript-normalize the PDF first, Signature + Full name + Signing date fields), Send to **Current team members + Future hires** with
   "All N individuals" and "All future hires" selected. Stage the PDF with device_stage_files and pass the staged path to `file_upload`.
3. Verify (Rule #12): template `processing_state` "approved", `approved_at` set, requests count = active roster (Gusto connector list_employees,
   terminated=false). Record gusto_template_id + request_count. Mismatch → FAILURE_LEDGER row; never resend.
4. #policy-announcements: the approved text, via the outbox. Exactly once (slack_posted_at).
4b. Second documents (manifest `second_documents`, state `second_documents`): each is its OWN Gusto Team document with signature,
   sent the same run, after the update, with the same method as step 2 (Signature on the employee signature line + Full name + Signing date;
   current team + future hires) and the same duplicate guard by name. **November 2026:** "Name, Image, Likeness & Voice Release — November 2026"
   = `Valley_Pawn_Name_Image_Likeness_Voice_Release_HR-2026-09_Team.pdf` (HR root). Record its template id / request count in state
   `second_documents[0]`. Its status rides phases D and E with the update (one Market Manager list naming both documents).
5. Manuals: if handbook_new/pp_new — upload the new Handbook and P&P PDFs as view-only Team documents (no signature; current + future hires),
   then archive the superseded versions in Gusto. Set manuals_published.
6. POLICY_QUEUE.md rows → `sent PU-<slug>`. OBLIGATIONS.json `monthly-policy-update`: last_verified today, evidence = state file,
   due = next month's Policy Day; re-render `Compliance/bin/render_calendar.py`. CHANGELOG entry + Open Items Register row.

### D. Status (Mondays, and any run between sent_at and closed_at that has not refreshed in 7 days)
Gusto sign-in, then GET /api/document_templates/<gusto_template_id>/requests → update signers. If Gusto shows a "Send reminder" control for the
document, use it once per Monday for unsigned signers. No Slack or text messages to staff.

### E. Preston list (today ≥ Preston day, preston_list_sent_at empty)
Refresh statuses (D). Anyone not completed → outbox to #preston-claude:
"<Month> Policy Update — still not signed (due <sign-by>): <Store>: <names>; <Store>: <names>. It's waiting in their Gusto app under Documents —
please have them sign it today." All signed → send nothing. Record preston_list_sent_at.

### F. Close (today ≥ end of CUR's month)
Final status refresh; record signed/unsigned counts in the state file and one CHANGELOG line; unsigned people carry a line into the next
preview ("still unsigned from <Month>"). closed_at = today. 

## Never
Send anything to staff without Joshua's approve for that month · send twice (state file + duplicate guard) · message an employee directly in
Slack · post technical detail anywhere (Rule 16) · type a password or code anywhere.
