# Gusto HR Filing — signed DocuSign documents into each employee's Gusto file (runbook)

Joshua 2026-10-21: keep all HR paperwork "nice and neat and properly stored in Gusto", with no sign-ins from him.
Read by the scheduled task "Gusto HR filing (weekly)". Unattended: act, don't ask. Paths relative to ~/Documents/Claude/Projects.

## What gets filed
Since 2026-10-21 HR documents are signed directly in Gusto, so this only catches fallbacks: every COMPLETED DocuSign envelope from the Valley Pawn HR rails (DocuSign account 320a0ff8-3001-4e1a-93b4-4fc3004b1116):
- HR E-Sign Playbook forms — Record of Warning, Action Plan, Policy Acknowledgment (Drive HR_ESIGN_LOG.md, id 1HMJZ1rBtBYJFNzH2FTQstNzG__MHZPJ9)
Skip: subjects starting "PREVIEW —" or "TEST", anything voided/declined (log declined as delivered, nothing to file), Bald Rock / vendor envelopes,
and anything for Joshua himself. Signer must match an active or terminated Gusto employee (Gusto connector list_employees, terminated true and false).

## Each run
1. **Find work:** DocuSign getEnvelopes(from_date = 45 days ago, status "completed", count 40, page through). Keep HR envelopes (above) whose envelopeId
   is not in `FILED_LEDGER.json`. None → stop ("nothing to file").
2. **Gusto session (no password, ever):** open https://app.gusto.com/payroll_admin in Claude in Chrome. Signed in → continue. On the login page:
   click "Sign in with Google", choose jdavis@fcfpawn.com. Never type a password or a code, never use a password manager. If Google or Gusto asks for
   a password or a verification code → stop, add ONE line to `Life OS/HUMAN_QUEUE.md` (if not already there today):
   "Gusto wants a code — sign in once with 'Sign in with Google' in Chrome on the Mac and tick Remember this device (2 min). HR filing resumes on its own."
   Files wait; next run catches up.
3. **For each envelope (oldest first):**
   a. Get the signed PDF: Gmail search `from:docusign.net subject:"Completed" "<envelope subject words>" newer_than:60d` → open the message's viewUrl in
      Chrome → `find` "Download attachment <name>.pdf" → click it. Wait, then confirm the new PDF in ~/Downloads (device shell: newest *.pdf, modified
      in the last 2 minutes). No attachment → ledger row status "no_pdf", try again next run (max 3 tries, then one HUMAN_QUEUE line).
   b. Name it: `<YYYY-MM-DD signed> <Type> - <First Last> - signed.pdf` where Type = "Policy Update <Month YYYY>", "Record of Warning",
      "Action Plan" or "Policy Acknowledgment - <policy title>".
   c. Archive copy (Drive = source of truth): copy into
      `GoogleDrive-jdavis@fcfpawn.com/My Drive/01 Business/Full Circle Finance (Valley Pawn)/03 Human Resources/Employee Files/<Last, First>/` (create the
      person's folder if missing). Then move the Downloads file into `~/Downloads/_filed/` (never delete).
   d. Gusto: People → the employee (match by Gusto uuid from list_employees) → `https://app.gusto.com/payroll_admin/people/<uuid>/documents` → check the
      list: a document with the same name already there → skip upload, mark filed. Otherwise click "Add document" (opens
      `/documents?action=add-document`), Name = `<Type> (<YYYY-MM-DD>)` (short, e.g. "Policy Update Nov 2026 (2026-11-06)"), stage the Drive copy with
      device_stage_files and pass the staged path to `file_upload` on the "Select files…" input, click Save. Confirm the row appears in the list.
   e. Ledger row: {envelopeId, subject, employee, gusto_uuid, type, signed_date, drive_path, gusto_name, filed_at}. Write the ledger after EVERY file.
4. **Policy Day manuals:** if `policy_bundles/state/<YYYY-MM>.json` has manuals_published false and handbook_new/pp_new, upload the new
   Handbook / P&P PDFs as company-wide view-only documents (gusto-access skill, Team document, no signature, current + future hires), then set
   manuals_published true and remove the matching HUMAN_QUEUE line.
5. **Log:** one line per run in `Human Resources/gusto_filing/RUN_LOG.md` (date, filed N, skipped N, waiting N). CHANGELOG line only when N > 0.

## Never
Type a password or verification code · use a password manager · file a document to the wrong person (name AND email must match Gusto) · upload twice ·
delete anything · message employees or Slack · open or file anything about Davis-family pay.
