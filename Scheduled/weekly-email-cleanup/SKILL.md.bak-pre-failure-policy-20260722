---
name: weekly-email-cleanup
description: Weekly scan of Gmail for new commercial/marketing emails and unsubscribe from them
---

Perform a weekly email cleanup for Joshua's Gmail account (jdavis@fcfpawn.com):

1. Search Gmail for commercial/marketing emails received in the last 7 days using the query: "unsubscribe -category:updates after:{{7 days ago}} before:{{today}}"
2. Identify new commercial senders that haven't been unsubscribed from yet
3. Exclude transactional emails like order confirmations, shipping notifications, receipts, and account alerts
4. Present a summary of new commercial senders found
5. For each new commercial sender, use the Gmail unsubscribe link in the email header to unsubscribe
6. Report back with a summary of what was unsubscribed

Keep: Order/shipping notifications, receipts, account alerts, payroll (Gusto), banking (Wells Fargo), and other transactional emails.
Unsubscribe from: Marketing promotions, newsletters, sales emails, product announcements from commercial senders.