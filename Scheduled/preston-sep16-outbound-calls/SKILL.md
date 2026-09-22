---
name: preston-sep16-outbound-calls
description: Preston's Sep 16 outbound call count from T-Mobile. BLOCKED 2026-09-21: portal sign-in requires an attended session, so an unattended run can never complete it. Now a weekly one-step re-test only; the real pull happens live with Joshua.
---

GOAL: Get the number of OUTBOUND calls Preston Peters made on Wednesday September 16, 2026, and report it to Joshua.

=====================================================================
KNOWN BLOCKER — READ FIRST (verified 2026-09-21, do not rediscover it)
=====================================================================
This pull CANNOT be completed by an unattended scheduled run:
- request_credentials, list_granted_credentials and enter_verification_code all return
  "This tool requires an attended session." A scheduled run is unattended by definition.
- Chrome holds no T-Mobile session and does not autofill the sign-in page — the portal
  returned a cold "Log in" screen and the email field stayed empty after a click + autofill
  attempt on 2026-09-21.
- Typing a password directly is not an allowed action.

This is a PERMANENT STRUCTURAL CONSTRAINT, not the Sep 16 data lag described below.
Retrying the same login daily will never succeed.

Joshua was told once, in one plain Slack DM on 2026-09-21, that this number is waiting on a
single sign-in from him and that he should start a chat and ask for it. Do not tell him again —
repeating it is noise.

=====================================================================
WHAT THIS TASK DOES NOW (weekly, one step)
=====================================================================
1. Call list_granted_credentials. If it returns "requires an attended session" (the expected
   result), STOP. End the run silently. No Slack message, no file writes, nothing.
2. Only if credential tooling IS available — i.e. the constraint has changed — run the full
   flow below, then DM Joshua the number and delete this task.

=====================================================================
THE FLOW (correct as written — use it in a LIVE session with Joshua)
=====================================================================
BACKGROUND (2026-09-17 session): Joshua asked for this on 9/17. T-Mobile had not yet posted
voice call detail for 9/16 — the line showed TOTAL CALLS 0 with zero rows, a data-lag artifact,
NOT a real zero. Preston's line averages ~11-12 calls/day. NEVER report a zero as fact.

ACCOUNT DETAILS:
- Portal: https://tfb.t-mobile.com/apps/tfb_billing/dashboard (T-Mobile for Business)
- Account #960053854, 8 lines, logged in as Joshua Davis
- Preston Peters' line: (540) 836-4200
- Login: request_credentials for https://www.t-mobile.com, then autofill_credential. A 2FA SMS
  code goes to Joshua's ...4221 — use enter_verification_code. NEVER ask for the code in chat
  and never type it yourself.
- If the password step shows "Continue with Face ID/Fingerprint", click "Log in with password".

WHERE THE DATA LIVES:
Billing > Usage > set BILLING PERIOD (top right) > click subscriber (540) 836 4200 >
"Minutes" tab. Sep 16 falls in the cycle the portal labels "Current" (Sep 16 – Oct 15). Once
the Aug 17 – Sep 16 or Sep 17 – Oct 16 bill is issued it may move into a dated period in that
same dropdown — check "Current" first, then any newly-listed dated period covering Sep 16.

HOW TO COUNT:
Count only rows dated "Sep 16" whose DESCRIPTION indicates an outbound/placed call (e.g.
"to Culpeper/VA", "to Staunton/VA"). EXCLUDE rows described as "INCOMI CL" / incoming. Page
through EVERY page — the table paginates. Report the outbound count, plus total calls and
total minutes for that day.

IF POSTED: Send Joshua one plain Slack DM (D03BHQH5VGT): "Preston made N outbound calls on
Wed 9/16 (N total calls, N minutes)." No technical detail, no jargon. Then delete this task.

=====================================================================
HARD DON'TS
=====================================================================
- Do NOT report a zero, and do NOT tell Joshua the 9/16 detail "never posted." As of
  2026-09-21 the Minutes tab for Sep 16 has never actually been read. Claiming a negative from
  a source nobody opened is exactly what Rule 19 forbids. The old 2026-10-05 stop condition
  that said to send that message has been REMOVED for this reason.
- Do NOT delete this task while the number is still unpulled — Joshua asked for it and there is
  no other source of record.
- Do NOT send any failure notice, status ping, or technical detail to Slack (Rule 16).