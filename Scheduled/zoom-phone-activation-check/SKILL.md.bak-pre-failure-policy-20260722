---
name: zoom-phone-activation-check
description: Check Zoom Phone line activation for Harrisonburg/Waynesboro and advance rollover setup.
model: claude-sonnet-5
---

Check on the Valley Pawn Zoom Phone rollout and report status to Joshua. Context: We're moving Valley Pawn stores to Zoom Phone. Two new lines were built — Harrisonburg (user harrisonburg@fcfpawn.com, extension 802) and Waynesboro (user waynesboro@fcfpawn.com, extension 803), both on the US/CA Unlimited calling plan. A third user lexington@fcfpawn.com was also created. The store numbers 540-574-4500 (Harrisonburg) and 540-221-6346 (Waynesboro) are being ported from Comcast to Zoom with a requested cutover date of July 9, 2026. Each store is getting a Poly VVX 250 (wired desk phone) + Grandstream WP822 (cordless), matching Lexington's setup. Store managers Walker (Harrisonburg) and Chadd (Waynesboro) were asked via Slack to accept the Zoom invite in their store inbox to activate the lines.

Do the following:
1. Using the Claude-in-Chrome browser tools, sign in is already saved — go to https://www.zoom.us/pbx/page/telephone/phoneUsers and check the activation status (User Status / Activation Status) of harrisonburg@fcfpawn.com, waynesboro@fcfpawn.com, and lexington@fcfpawn.com. Also check whether any desk phones (Poly VVX250 / Grandstream WP822) have been provisioned onto extensions 802 and 803.
2. If a store user is now ACTIVE and has at least one device provisioned: open that user's Profile/Call Handling settings and set the Call Handling Ring Mode to SEQUENTIAL so a busy primary phone rolls over to the cordless. (Do not configure it if the user is still Pending or has zero devices — it isn't available in that state.)
3. If lexington@fcfpawn.com is now active AND it looks safe (the live Lexington line, ext 800, number 540-461-8349, with its two online devices, won't be disrupted), you may proceed to reassign the Lexington line from jdavis@fcfpawn.com to lexington@fcfpawn.com for consistency. If there's any risk to the live phones, do NOT do it — flag it for Joshua instead.
4. Do NOT create any user accounts and do NOT submit/cancel anything irreversible without Joshua's confirmation.
5. Post a concise status summary to Joshua: who has/hasn't activated, whether the ring mode was set, status of the July 9 port (still pending), and any nudges needed (e.g. remind Walker/Chadd to accept invites). Send it as a Slack DM to Joshua (his Slack user_id is U03BB52MDSA) and also summarize it in the session.