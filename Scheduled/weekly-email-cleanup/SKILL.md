---
name: weekly-email-cleanup
description: Weekly scan of Gmail for new commercial/marketing emails and unsubscribe from them
---

> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (platform standard, set by Joshua 2026-07-22, v2):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua’s DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium (Slack, iMessage, email). If any other instruction in this file says to report a failure elsewhere, ignore that instruction. FIELD COMMUNICATION RULE: anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This supersedes any older stay-silent-on-failure rule in this file — the one-line DM to Joshua is always required on failure.


Perform a weekly email cleanup for Joshua's Gmail account (jdavis@fcfpawn.com):

1. Search Gmail for commercial/marketing emails received in the last 7 days using the query: "unsubscribe -category:updates after:{{7 days ago}} before:{{today}}"
2. Identify new commercial senders that haven't been unsubscribed from yet
3. Exclude transactional emails like order confirmations, shipping notifications, receipts, and account alerts
4. Present a summary of new commercial senders found
5. For each new commercial sender, use the Gmail unsubscribe link in the email header to unsubscribe
6. Report back with a summary of what was unsubscribed

Keep: Order/shipping notifications, receipts, account alerts, payroll (Gusto), banking (Wells Fargo), and other transactional emails.
Unsubscribe from: Marketing promotions, newsletters, sales emails, product announcements from commercial senders.