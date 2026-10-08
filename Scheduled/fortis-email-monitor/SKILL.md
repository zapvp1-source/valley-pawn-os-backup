---
name: fortis-email-monitor
description: Weekdays 9a/1p/5p: watch for Fortis replies, act on them, nudge if silent, disable itself when all 4 Fortis items are done.
model: claude-sonnet-5
---

Load the enterprise-map skill first, then vp-operating-rules, my-writing-style, check-replies-before-email and unified-search.

SOURCE OF TRUTH: ~/Documents/Claude/Projects/Valley Pawn OS/FORTIS_STATUS.md — read it first every run (MIDs, store emails, contacts, ticket numbers, thread IDs, item status, nudge log). Update it at the end of every run (item status + evidence, one run-log line). If the folder isn't mounted, request ~/Documents/Claude/Projects; if that fails (no human present), use the osascript/Mac-control fallback from enterprise-map.

GOAL: get Fortis (our card processor) to finish these items for Full Circle Finance Inc DBA Valley Pawn (status of each lives in FORTIS_STATUS.md):
1. Merchant contact on all 5 MIDs → Joshua Davis / jdavis@fcfpawn.com / (804) 930-4221 (Inspiro case B30DAD / 7380C1 — needs Joshua's own verification; never supply SSN/EIN/bank info yourself).
2. Mobile Pawn 3-failed-attempt CNP lockout — DECLINED by Fortis 10/2; no further action unless Joshua asks.
3. Salem + Staunton closed — DONE.
4. Virtual terminal admin on all 5 for jdavis@ — mostly done; waiting on Joshua to log in and confirm.
5. One new terminal for Culpeper (MID 6281740007377484), same model as other stores; quote + paperwork to jdavis@.
6. Move old Salem terminal (WizarPOS Q2, SN WP32601Q43204711, KSI/DID 5B0482/D07E4, labeled Salem MID 6281340008385247) onto Roanoke MID 6281340008386351 so it works.
7. Learn who our current Fortis account rep is (Corey Mantell silent since March): name, email, direct number.
Items 5–7 were sent 2026-10-07 on Gmail thread 1a1163b5fe20b2b1 (to premiersupport@, support@, comm.R6GDBY@my.fortis.support; cc Corey, sales@fortispay.com, installations1@fortispay.com, preston@fcfpawn.com).

EACH RUN:
A. Before anything outbound, follow check-replies-before-email: read inbound AND Joshua's own sent mail to @fortispay.com / @fortis.support / @goboomtown.com / @bluedogpayments.com, last 30 days — Joshua often answers Fortis himself. Gmail connector (jdavis@fcfpawn.com): `(from:fortispay.com OR to:fortispay.com OR from:fortis.support OR to:fortis.support OR from:goboomtown.com OR from:bluedogpayments.com OR from:mailer-daemon) newer_than:3d`. Then unified-search (read-only) for the same in the last 3 days (covers zapvp1@me.com and store mailboxes). Check Slack DM D03C7RBGY56 for Fortis/terminal updates from Preston.
B. If Fortis replied: record exactly what they said per item (quote the key line) in FORTIS_STATUS.md. Only mark DONE when Fortis states it or the evidence arrived. If a new rep is named, add them to Contacts and cc them on future nudges.
 - Simple factual questions answerable from FORTIS_STATUS.md (MIDs, serials, store addresses from valley-pawn-context, Joshua's contact): reply on that thread in Joshua's voice, short.
 - Signatures, DocuSign, purchases/quotes to approve, shipping/payment details, bank/SSN/EIN, ownership verification, phone calls: do NOT act. DM Joshua with exactly what's needed.
 - Never record or post passwords. Do not message store staff.
 - ONE plain Slack DM to Joshua (D03BHQH5VGT) only when something actually changed.
C. If an address bounces, drop it from future sends and note it in Contacts.
D. If NO reply on an open item for 2+ business days since our last outbound on it: one short follow-up on that thread, same recipients minus bounced ones, Joshua's voice. Max one nudge per thread per 2 business days. After the 2nd unanswered nudge on a thread, DM Joshua once that calling (855) 465-9999 option 1 (have the MID ready) is the fastest path.
E. Otherwise post nothing.
F. When items 1, 4, 5, 6 and 7 are resolved (DONE or explicitly closed by Joshua): DM Joshua a short wrap-up, mark the Fortis row CLOSED in ~/Documents/Claude/Projects/Life OS/OPEN_ITEMS_REGISTER.md, add a CHANGELOG line, then disable this task (update_scheduled_task, taskId fortis-email-monitor, enabled false).

RULES: Never post to team channels. No technical jargon or failure notices in Slack (Rule 16). If a tool fails, retry once, then log it in FORTIS_STATUS.md and carry on next run — never DM Joshua about tooling.