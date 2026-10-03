---
name: mobilepawn-bravo-reply-check
description: One-time 10/22: if Bravo hasn't agreed to a monthly MobilePawn download text, switch our own monthly Chekkit text to carry the app ask.
model: claude-sonnet-5
---

Valley Pawn (Full Circle Finance Inc). Joshua's standing decision 2026-09-29: "we will do monthly if bravo doesnt" — meaning if Bravo won't send their MobilePawn download text every month, our own monthly Chekkit text carries the app ask. Do not question this; just execute it.

1. Using the Gmail connector (account jdavis@fcfpawn.com), read thread "Free MobilePawn Marketing?" (thread id 19f1483f43d1a4c0). Joshua emailed Tahoe Mack (tahoe@bravostoresystems.com) on 2026-09-29 asking Bravo to run their free non-activated-customer SMS monthly and to state any cost. Look for any reply from @bravostoresystems.com dated after 2026-09-29.
2. Decide:
   - Bravo clearly AGREED to send monthly at no cost → do nothing to config. Result = "bravo".
   - Bravo agreed but quoted a COST → do not flip anything; DM Joshua (Slack D03BHQH5VGT) one plain line with the quoted cost and ask if he wants it. Result = "cost".
   - No reply, declined, or anything unclear/one-time only → set "app_sms_own": true in ~/Documents/Claude/Projects/eBay Customer Campaign/config.json (edit only that key; keep a backup copy config.json.bak-<date>-appsms first). Result = "own". The monthly build on the 24th then puts the app link in the monthly text automatically.
   (Mount ~/Documents/Claude/Projects with request_cowork_directory if needed; if no approver, use a Mac shell via osascript.)
3. Append one dated row describing the result to ~/Documents/Claude/Projects/Life OS/OPEN_ITEMS_REGISTER.md and one line to Valley Pawn OS/CHANGELOG.md.
4. For "bravo" or "own": send Joshua ONE plain DM, e.g. "Bravo didn't sign on for monthly app texts, so our own monthly text now includes the app link starting in November." or "Bravo is sending the app text every month." Nothing technical, no team channels (Rule 16). If something breaks, log it to Valley Pawn OS/fleet/FAILURE_LEDGER.md and send nothing to team channels.