# Policy Day Runner — exact steps (read by the scheduled task "Policy Day runner", daily 8:41 AM ET)

Rules in `../POLICY_CADENCE.md` govern. This file is the HOW. Unattended: act, don't ask. Paths are relative to
`~/Documents/Claude/Projects/`. Base = `Human Resources/policy_bundles/`.

## Fixed facts
- DocuSign account `320a0ff8-3001-4e1a-93b4-4fc3004b1116` (connector; no logins). Sender name stays as is (HR E-Sign Playbook §8).
- Blank form URL: `docusign/FORM_URL.txt` (hosted blank PDF, no policy text). Missing → the preview says so; nothing is sent.
- Slack (always through the fleet outbox: write `<name>.txt`, then `<name>.json` = {"channel": "...", "file": "<host path of the .txt>"} into `Valley Pawn OS/fleet/outbox/`; never call slack_send_message in a scheduled run):
  #policy-announcements `C03BHQ9RLR0` · #preston-claude `C0BGXSTT4TY` · Joshua `U03BB52MDSA`.
- Fleet dry-run guard before any outbox write: `python3 "Valley Pawn OS/bin/vp_dryrun.py" status` — exit 0 (armed) → write to `Valley Pawn OS/fleet/test_output/` instead.
- Email to Joshua: Gmail connector, from and to jdavis@fcfpawn.com.
- State file per update: `docusign/state/<YYYY-MM>.json` (create if missing):
  {slug, preview_sent_at, preview_subject, preview_envelope_id, approved_at, approval_evidence, dropped_items[], sent_at,
   envelopes:[{name,email,store,envelopeId,status,completed_at}], skipped_no_email[], slack_posted_at, preston_list_sent_at,
   manuals_published, closed_at, notes[]}
- Business day = Mon–Fri excluding New Year's Day, Memorial Day, July 4, Labor Day, Thanksgiving, Christmas.
  Policy Day = 1st business day of the month. Sign-by = the 10th (next business day if not one). Preston day = the 15th (same rule).
  The manifest's own `policy_day` / `sign_by` override (November 2026: Thu 11/5, sign by Fri 11/13).

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
4. Run `python3 build_bundle.py manifests/<slug>.json` (proof PDF) and
   `python3 docusign/policy_update_envelope.py manifests/<slug>.json docusign/_preview_recipient.json docusign/out_<slug>_preview`
   (exit 2 = shorten text and re-run). Read `<slug>__preview.txt` end to end: every line must match the manuals and the source policy.
5. Academy check: search `Training Program/academy/lessons/*.json` for each item's key terms; list lessons that teach the old rule.
   Append them to `Training Program/academy/OPEN_ITEMS.md` as "Policy Update <Month>: update lesson X before <Policy Day>".
6. Preview to Joshua: create the DocuSign envelope from the preview JSON (status `sent`, signer Joshua jdavis@fcfpawn.com,
   subject prefixed "PREVIEW — ") so he sees exactly what staff will see; record preview_envelope_id. Then ONE email, subject
   `Policy Update — <Month> — reply "approve"`: Policy Day + sign-by; what's in (one line each); what's held or waiting and why;
   the exact #policy-announcements text; the exact 15th message to Preston (template below); Academy lessons that change; anything that
   leaked outside Policy Day last month. Last line: `Reply "approve" to send it as shown, "approve without <item>" to drop something,
   or reply with changes.` Empty queue → one short email "Nothing new for <Month> — nothing will be sent", mark closed.

### B. Approval watch (preview sent, not approved, today ≤ the 7th of CUR's month)
1. Gmail: the preview thread, plus `from:jdavis@fcfpawn.com subject:"Policy Update — <Month>"` newer than preview_sent_at. Approval =
   a later message in that thread from Joshua whose first word is approve/approved/yes/send it. "without X" → drop X (state dropped_items,
   rebuild). Changes requested → apply, rebuild, send a revised preview in the same thread, keep waiting. A Cowork session may also
   record approval directly in the state file (approval_evidence "chat <date>: <his words>").
2. Policy Day reached and no approval → send nothing; email Joshua once that day: "The <Month> Policy Update is waiting on your
   approve — nothing has gone out." After the 7th with no approval: move the items back to `approved` for the next month, email once, close.

### C. Send (approved AND today ≥ policy_day AND no sent_at)
1. Recipients: Gusto connector list_employees(terminated=false). Each: legal first+last (preferred first name if set), personal email
   (else work email), department = store. Exclude Joshua Davis. No email → skip and list in skipped_no_email.
2. Duplicate guard: getEnvelopes(from_date = policy_day − 5 days, search_text = "<Month> Policy Update", count 40); anyone already sent → skip.
3. Build with `policy_update_envelope.py` (no --draft) into `docusign/out_<slug>/`; createEnvelope per person; record envelopeId at once.
   Failure → retry once; still failing → FAILURE_LEDGER row (`| time | policy-day-runner | plain sentence | NEEDS_HUMAN: no | OPEN |`)
   and continue with the rest; the next run retries the missing ones.
4. #policy-announcements: the approved text, via the outbox. Exactly once (slack_posted_at).
5. Manuals: if handbook_new/pp_new — upload the new PDFs to Gusto as view-only Team documents ONLY if Chrome already has a Gusto
   session (gusto-access skill; never sign in); otherwise add one line to `Life OS/HUMAN_QUEUE.md`:
   "Gusto: upload Handbook v… and P&P v… as view-only documents (2 min) — staff were told they're there." Set manuals_published.
6. POLICY_QUEUE.md rows → `sent PU-<slug>`. OBLIGATIONS.json `monthly-policy-update`: last_verified today, evidence = state file,
   due = next month's Policy Day; re-render `Compliance/bin/render_calendar.py`. CHANGELOG entry + Open Items Register row.

### D. Status (Mondays, and any run between sent_at and closed_at that has not refreshed in 7 days)
getEnvelopes(from_date = policy_day − 5, search_text "<Month> Policy Update", count 40, page as needed) → update each envelope status.
No messages to staff — DocuSign reminds them every 3 days.

### E. Preston list (today ≥ Preston day, preston_list_sent_at empty)
Refresh statuses (D). Anyone not completed → outbox to #preston-claude:
"<Month> Policy Update — still not signed (due <sign-by>): <Store>: <names>; <Store>: <names>. It's in their email from DocuSign —
please have them sign it today." All signed → send nothing. Record preston_list_sent_at.

### F. Close (today ≥ end of CUR's month)
Final status refresh; record signed/unsigned counts in the state file and one CHANGELOG line; unsigned people carry a line into the next
preview ("still unsigned from <Month>"). closed_at = today. Declined = delivered (note it; never resend).

## Never
Send anything to staff without Joshua's approve for that month · send twice (state file + duplicate guard) · put policy text on a public
page (the hosted form stays blank) · message an employee directly in Slack · post technical detail anywhere (Rule 16) · sign in anywhere.
