---
name: preston-sep16-outbound-calls
description: Retry pulling Preston Peters' Sep 16 2026 outbound call count from T-Mobile for Business once voice CDRs post.
---

GOAL: Get the number of OUTBOUND calls Preston Peters made on Wednesday September 16, 2026, and report it to Joshua.

BACKGROUND (from the 2026-09-17 session): Joshua asked for this on 9/17. T-Mobile had not yet posted voice call detail records for 9/16 — the line showed TOTAL CALLS 0 with zero rows, which is a data-lag artifact, NOT a real zero. Preston's line averages ~11-12 calls/day. Do NOT report a zero as fact.

ACCOUNT DETAILS:
- Portal: https://tfb.t-mobile.com/apps/tfb_billing/dashboard (T-Mobile for Business)
- Account #960053854, 8 lines, logged in as Joshua Davis
- Preston Peters' line: (540) 836-4200
- Login: use the claude-in-chrome credential tools (request_credentials for https://www.t-mobile.com, then autofill_credential). A 2FA SMS code goes to Joshua's ...4221 — use the enter_verification_code tool, NEVER ask for the code in chat and never type it yourself.
- If the password step shows "Continue with Face ID/Fingerprint", click "Log in with password" first.

WHERE THE DATA LIVES:
Billing > Usage > set BILLING PERIOD (top right) > click subscriber (540) 836 4200 > "Minutes" tab.
September 16 falls in the cycle that the portal labels "Current" (Sep 16 – Oct 15). Once the Aug 17 – Sep 16 or Sep 17 – Oct 16 bill is issued it may move into a dated period in that same dropdown — check "Current" first, then any newly-listed dated period covering Sep 16.

HOW TO COUNT:
Count only rows dated "Sep 16" whose DESCRIPTION indicates an outbound/placed call (e.g. "to Culpeper/VA", "to Staunton/VA"). EXCLUDE rows described as "INCOMI CL" / incoming. Page through every page of results — the table paginates. Report the outbound count, and separately note total calls and total minutes for that day.

IF STILL NOT POSTED:
If the Minutes tab still shows zero rows for Sep 16, do nothing further and do not message Joshua — just end the run quietly. Keep retrying daily.

IF POSTED:
Send Joshua one plain Slack DM (D03BHQH5VGT) with the number, e.g. "Preston made N outbound calls on Wed 9/16 (N total calls, N minutes)." No technical detail, no jargon. Then DELETE this scheduled task since it is complete.

STOP CONDITION: If Sep 16 detail has still not appeared by 2026-10-05, send Joshua one plain DM saying the 9/16 call detail never posted to the T-Mobile portal and he may need to request it from T-Mobile Business Care, then delete this task.