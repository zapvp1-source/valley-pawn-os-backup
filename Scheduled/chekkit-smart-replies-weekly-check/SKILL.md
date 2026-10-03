---
name: chekkit-smart-replies-weekly-check
description: Daily 6:30 PM: did Chekkit Smart Replies (instant FAQ answers, all 5 stores) help customers today or cause friction? One short DM to Joshua.
model: claude-sonnet-5
---

Valley Pawn (Full Circle Finance Inc) — DAILY check on Chekkit Smart Replies ("FAQ Instant Answers" folder, 12 keyword rules per store, live since 2026-09-29 at Culpeper, Waynesboro, Harrisonburg, Lexington, Roanoke). Joshua wants to know FAST if customers are not getting what they need. READ ONLY — never edit any Chekkit setting, never text a customer.

Window: since yesterday's 6:30 PM run (first run: since 2026-09-29 3:00 PM).

Per store:
1. Automated answers sent: in Chekkit (dashboard.chekkit.io via Claude in Chrome; switch store with the top-left location dropdown; check both Open and Closed tabs for conversations with activity in the window) find outbound messages ending in "(Automated reply". Note which rule it was (Hours, Location, Sell or pawn, Payments and due dates, Gold and silver, In stock, How pawn loans work, Layaway, Warranty, FFL transfer, Guns, Jobs) and whether the answer actually fit what the customer asked (a wrong-rule fire = friction).
2. Customer's next message after each automated answer: FRICTION = "?", "that's not what I asked", "real person", "human", "you didn't answer", annoyance, repeat of the same question, or STOP/unsubscribe. SUCCESS = sends photos, "ok/thanks", says they're coming in, or asks a normal follow-up a person then answered.
3. Did a staff member reply after the automated answer, and how long did it take.
4. Unanswered texts: Gmail (jdavis@fcfpawn.com) threads from support@chekkit.io, subject "Unanswered Message Alert", in the window, per store ("Sent to Valley Pawn - <Store>"). Pre-launch baseline: Harrisonburg ~1.2/day.

Send Joshua ONE short Slack DM (user U03BB52MDSA), plain language, his style (short, no headers, one line per store), e.g. "Instant answers today: CUL 3 sent, 3 good. HAR 5 sent, 1 friction (In stock fired on 'looking for a job'). ... Unanswered texts 4 (yesterday 6)." Put any friction example FIRST with the rule name and a one-line fix recommendation. If a rule caused friction 2+ times in a day, say "recommend pulling <rule> at <store>". If zero automated answers fired anywhere, still send one line saying so plus the unanswered count. Do not change anything yourself. If you cannot reach Chekkit or Gmail, append one line to ~/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md and do not message anyone.