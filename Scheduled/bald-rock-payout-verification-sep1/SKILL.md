---
name: bald-rock-payout-verification-sep1
model: claude-sonnet-5
description: One-shot Sep 1: verify Bald Rock Airbnb (Claire ~Aug 22) and VRBO (Debra ~Aug 31) payouts actually disbursed; DM Joshua only if one is missing.
---

You are verifying that guest payouts for the Bald Rock short-term rental (282 Bald Rock Road, Verona VA — "Mountain Valley Luxury with Pool and Hot Tub", Vrbo listing #4752473) actually disbursed. Context: on 2026-08-10 Joshua changed the payout bank on BOTH platforms to DuPont Community Credit Union acct ending 0927. Airbnb had an ACH verification failure 8/12, re-verified 8/14, and payouts resumed (last verified payout 8/17 $2,883.98). VRBO's last deposit was 8/7 ($2,459.51 to the OLD acct ending 2291); after the bank change VRBO emailed "Tax form required for payments from Vrbo" (W-9 for the new account) on 8/10 — completion unconfirmed. If the W-9 was never completed, VRBO holds payouts.

Execution contract — DO NOT STOP EARLY. If a tool needs folder access and the request fails because no one can approve it, fall back to `mcp__Control_your_Mac__osascript` (`do shell script`) for all file reads/writes. Do not idle after any interruption; resume and finish.

STEP 1 — Search email evidence via the unified-search index (fastest, authoritative). Run via mcp__Control_your_Mac__osascript:
  do shell script "export PATH=/opt/homebrew/bin:$PATH; vpfind --mail --since 2026-08-18 --json -n 30 'airbnb payout'"
  do shell script "export PATH=/opt/homebrew/bin:$PATH; vpfind --mail --since 2026-08-25 --json -n 30 'vrbo deposit statement'"
If the index looks stale (no results at all), query the SQLite db directly: /Users/joshuadavis/Documents/Claude/Projects/Unified Search/index.db, table mail(subject, sender, ts) — look for sender LIKE '%airbnb%' AND subject LIKE '%payout%' since Aug 18, and sender LIKE '%payment.homeaway%' AND subject LIKE '%Deposit statement%' since Aug 25. Gmail MCP is a fallback only.

STEP 2 — Evaluate:
  (a) AIRBNB: expect a "We sent a payout of $..." email dated ~Aug 22–24 (guest Claire, check-in Aug 21) and possibly later ones. If at least one payout email exists after Aug 18 → Airbnb OK.
  (b) VRBO: expect a "Vrbo Online Payments - Deposit statement" email dated ~Aug 31–Sep 1 for reservation HA-TV6MLK (guest Debra Henning, check-in Aug 30, gross guest payment collected 8/9 + 8/21). Also check for any "Tax form required" reminder emails after Aug 21 (a reminder = W-9 still not done). VRBO deposits can lag 1 day after check-in; if today is Sep 1 and nothing arrived yet, that is INCONCLUSIVE-BUT-WATCH, not a confirmed failure — but a post-Aug-21 tax-form reminder plus no deposit statement = payouts likely HELD.

STEP 3 — Report per Failure Alert Policy v2: if both look OK, post a one-line all-clear to Joshua's Slack DM (channel D03BHQH5VGT) via the Slack MCP: "Bald Rock payout check: Airbnb payout(s) confirmed since 8/22 and no VRBO hold signals — Debra's VRBO deposit statement [arrived/expected by 9/2]. All flowing." If something is missing or a W-9 reminder was found, DM Joshua plainly: what's missing, and that the fix is completing the Vrbo W-9 (Vrbo dashboard → Property → Payment options → Add tax form for acct DuPont CCU 0927 — triggers a fresh emailed link since the original expired). No technical jargon in the DM.

STEP 4 — Log the outcome as an update to the 2026-08-21 payout-check row in /Users/joshuadavis/Documents/Claude/Projects/Life OS/OPEN_ITEMS_REGISTER.md (via osascript heredoc if file tools lack access). If both flows confirmed, mark that row's payout portion RESOLVED. If VRBO was still unconfirmed, reschedule yourself once: create a new one-shot task for 2026-09-03 09:30 ET with this same prompt (only once — do not create an infinite chain; if the 9/3 check also can't confirm, DM Joshua and stop).