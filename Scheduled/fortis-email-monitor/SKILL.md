---
name: fortis-email-monitor
description: Weekdays 9a/1p/5p: watch for Fortis replies, act on them, nudge if silent, disable itself when all 4 Fortis items are done.
---

Load the enterprise-map skill first, then vp-operating-rules, my-writing-style and unified-search.

SOURCE OF TRUTH: ~/Documents/Claude/Projects/Valley Pawn OS/FORTIS_STATUS.md — read it first every run (MIDs, store emails, contacts, thread IDs, item status, nudge log). Update it at the end of every run (item status + evidence, VT-by-store table, one run-log line). If the folder isn't mounted, request ~/Documents/Claude/Projects; if that fails (no human present), use the osascript/Mac-control fallback from enterprise-map.

GOAL: get Fortis (our card processor) to finish 4 items for Full Circle Finance Inc DBA Valley Pawn:
1. Contact on all active MIDs → Joshua Davis / jdavis@fcfpawn.com / (804) 930-4221, and send portal + virtual terminal logins.
2. Lock out any card-not-present transaction through the Mobile Pawn app after 3 failed attempts.
3. Confirm Salem + Staunton MIDs closed (Case #4D8A8C).
4. Virtual terminal ("crash portal" — keying sales when a card machine is down) active on all 5 MIDs, one user per store with invite to the store email, jdavis@fcfpawn.com admin on all 5.

EACH RUN:
A. Search for responses since the last run. Gmail connector (jdavis@fcfpawn.com): `(from:fortispay.com OR from:fortis.support OR from:fluidpay.com OR from:fortis.tech OR 964DBD OR 4D8A8C OR "virtual terminal") newer_than:3d`. Then the unified-search index (read-only) for "fortispay" / "fortis.support" / "fluidpay" / "fortis.tech" in the last 3 days — this covers the 5 store mailboxes (where VT invites land) and zapvp1@me.com (where Corey sometimes replies). Also check Slack DM D03C7RBGY56 (Joshua/Preston) for any Fortis update from Preston.
B. If Fortis replied:
 - Record exactly what they confirmed per item (quote the key line) in FORTIS_STATUS.md. Only mark an item DONE when Fortis states it is done or a login invite actually arrived — never infer.
 - If they asked a simple factual question you can answer from FORTIS_STATUS.md (MIDs, store emails, business name, Joshua's contact), reply on the same thread in Joshua's voice (short, no fluff), cc the same people.
 - If they need a signature, DocuSign, bank info, SSN/EIN, ownership verification, a phone call, or anything that commits money/fees: do NOT act. DM Joshua with exactly what's needed.
 - If a store login invite arrived at a store mailbox, note it in the VT table. Do NOT activate accounts, set passwords, or message store staff.
 - Send ONE plain-language Slack DM to Joshua (D03BHQH5VGT) summarizing what moved and what's still open. Only when something actually changed.
C. If NO reply for 2+ business days since our last outbound (see nudge log): send one short follow-up on support thread 1a0f325eb32b553e to customersupport@fortispay.com + premiersupport@fortispay.com, cc support@fortispay.com, Corey.Mantell@fortispay.com, preston@fcfpawn.com — Joshua's voice, e.g. "Following up on this. Still need the contact update, the 3 attempt lockout on Mobile Pawn and virtual terminal logins for all 5 stores. Joshua Davis (804) 930-4221". Max one nudge per 2 business days. Log it. After the 2nd unanswered nudge, DM Joshua once: Fortis isn't responding by email; calling (855) 465-9999 option 1 with a MID ready is the fastest path.
D. Otherwise do nothing and post nothing (no "no news" DMs).
E. When all 4 items are DONE with evidence: DM Joshua a short wrap-up (which stores have VT logins, the login URL), update the 2026-09-30 Fortis row in ~/Documents/Claude/Projects/Life OS/OPEN_ITEMS_REGISTER.md to CLOSED, add a line to Valley Pawn OS/CHANGELOG.md, then disable this task with update_scheduled_task (taskId fortis-email-monitor, enabled false).

RULES: Never post to team channels. No technical jargon or failure notices in Slack (Rule 16). If a tool fails, retry once, then log the detail in FORTIS_STATUS.md run log and carry on next run — never DM Joshua about tooling.