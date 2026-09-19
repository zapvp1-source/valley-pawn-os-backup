---
name: entity-compliance-check
description: Monthly check of Joshua's entity filing deadlines (VA SCC, TN SOS, registered agent, property tax) with a 90-day lookahead; DMs Joshua only when something needs action.
---

Monthly entity-compliance check for Joshua Davis's business and real-estate entities.

STEP 1 — Load context.
Read `/Users/joshuadavis/Documents/Claude/Projects/Life OS/ENTITY_COMPLIANCE_CALENDAR.md`. That file is the authority for filing deadlines and registrations. If the Projects folder is not mounted, call `mcp__cowork__request_cowork_directory` with path `~/Documents/Claude/Projects`; if that fails (non-interactive run), read the file via the Control-your-Mac osascript tool using `do shell script "cat '<path>'"`.

STEP 2 — Build a 90-day lookahead.
Using today's date, list every obligation in that file falling due within the next 90 days. The hard recurring ones are:
- Virginia LLC annual registration fee, $50 per LLC, due the LAST DAY of the LLC's anniversary month. Farming Infinity, LLC = May 31. Farming Infinity Virginia LLC, Farming Infinity Tennessee LLC and Farming Infinity Mountains LLC all = July 31 (first ones due July 31, 2027). Unpaid 3 months past due = the LLC is CANCELLED by operation of law.
- Tennessee annual report for Farming Infinity Tennessee LLC (foreign, Certificate of Authority, TN control number 002134214), due APRIL 1 each year, $300 minimum, 60-day grace then administrative dissolution. First one due April 1, 2027.
- Full Circle Finance Inc (VA corporation, SCC entity ID 07794274) annual report + share-based registration fee — the date and fee are flagged UNVERIFIED in the calendar file. If it is still unverified, include it as a verification task, not as a date.
- Registered agent renewals (Northwest Registered Agent services FI Virginia, FI Mountains, FI Tennessee) and the unconfirmed Tennessee registered agent.
- Property tax cycles: Augusta County VA, Chesterfield County VA, City of Staunton VA, Roane County TN, St. Johns County FL.

STEP 3 — Check whether anything already happened.
Before flagging an item as outstanding, search for evidence it was already filed or paid, using the `unified-search` skill (vpfind against the local index of Apple Mail + iMessage + iCloud). Look for confirmation emails from scc.virginia.gov, tnsos.gov, fisgov.com, northwestregisteredagent.com, and county treasurers. Rule 12 applies: verify against actual output, never from a run record or an assumption. Also check `Life OS/OPEN_ITEMS_REGISTER.md` for anything a prior session already started.

STEP 4 — Update the record.
Append any newly-confirmed filing to ENTITY_COMPLIANCE_CALENDAR.md with its date, confirmation/tracking number and amount. Correct any deadline you verified against the source of record and note that you verified it and when. Never overwrite a verified date with a remembered one.

STEP 5 — Report.
If NOTHING is due in 90 days and nothing needs verification, do nothing and send no message. Silence is the correct output.
If something IS due or needs action, send ONE plain-language Slack DM to Joshua (user ID D03BHQH5VGT) — no technical jargon, no failure notices, no status chatter. Format it as a short list: entity, what is due, the date, and the one action that closes it. Put any detail or diagnosis in the calendar file, not in the message.

Never post to any team channel. Never contact anyone other than Joshua.