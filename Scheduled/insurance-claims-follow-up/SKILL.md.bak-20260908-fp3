---
name: insurance-claims-follow-up
description: Weekly chase on every open insurance claim — nudges the adjuster at 7 days silent, tracks payment, flags the QBO reconciliation so a loss is never carried twice.
model: claude-sonnet-5
---

Weekly insurance claims follow-up for Joshua Davis. Runs Wednesdays 9:40 AM ET.

STEP 1 — Load context: invoke `enterprise-map`, then `insurance-context`. Connect ~/Documents/Claude/Projects (request_cowork_directory with that literal path; osascript shell fallback if unattended). Read `Life OS/Insurance/CLAIMS.md`.

STEP 2 — For each claim with status open or payment pending:
a) Search Gmail for the claim number and the adjuster's address for anything new since the last entry. Update CLAIMS.md with what you find — date of last contact, what was requested, what was sent.
b) If 7+ days have passed with no adjuster response, draft (Gmail draft on the existing thread, DO NOT SEND) a short nudge in Joshua's voice — invoke `my-writing-style` first. Ask the specific outstanding question: payment status, documents still needed, or a written decision.
c) If the carrier has paid, record the amount and date, and set the QBO reconciliation flag. Note in CLAIMS.md whether the payout has been reconciled against any settlement already paid to the customer — the business must not carry the same loss twice.

STEP 3 — Anything that needs Joshua (a denial, a reservation of rights, a settlement demand, a payout that does not match the loss) gets ONE plain-language Slack DM to D03BHQH5VGT. No technical detail, no failure notices, no other channel (vp-operating-rules Rule 16). Routine "still waiting" states get no message at all.

STEP 4 — If CLAIMS.md has no open claims, do nothing and write nothing.

Never send email. Never accept, settle, or release a claim on Joshua's behalf.