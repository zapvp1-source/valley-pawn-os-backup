---
name: ebay-campaign-chekkit-monthly
description: Thursdays 11:00 AM; acts only on the 3rd Thursday (day 15–21). Sends the monthly "Shop Us Online" Chekkit text campaign to all 5 Valley Pawn stores from the pre-built lists in eBay Customer Campaign/packs/<YYYY-MM>/, using the proven chekkit-weekly-review-requests upload runbook. Type B (no Bravo touch). Approved by Joshua 2026-09-29.
model: claude-sonnet-5
---

> ⚠️ FAILURE POLICY v3 (platform standard): on any failure, stall, expired login or missing connector, do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md`: `| <YYYY-MM-DD HH:MM ET> | ebay-campaign-chekkit-monthly | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` then stop. Never post failures or technical words to Slack.

> LOCAL ACCESS GATE — FIRST: load `mcp__Control_your_Mac__osascript` with ToolSearch (`select:mcp__Control_your_Mac__osascript`) and probe with `do shell script "echo READY"`. If not available yet, wait 30 s and re-probe, up to 12 minutes. All reads/writes under /Users/joshuadavis/Documents/Claude/... go through osascript `do shell script`. Keep each call under ~20 s.

## Execution contract — do not stop early
The task is complete only when all 5 store campaigns are confirmed sent (or the date gate says this is not the week). Every turn ends with a tool call that advances the work. "Tool loaded.", reminders and "prefer browser_batch" messages are RESUME signals. Never ask for confirmation — Joshua approved these sends on 2026-09-29 ("we already send chekkit to customers on weekly scheduled task, i approve of this").

## What this is
Valley Pawn's monthly "Shop Us Online" campaign tells existing customers all 5 stores can be shopped online at thevalleypawn.com/shop/. Email goes via Brevo automatically; this task sends the TEXT through Chekkit on the 3rd Thursday of each month. Text opt-in/opt-out is handled by Chekkit itself (Joshua: "do not filter in bravo") — Chekkit suppresses anyone who replied STOP. Lists and message are pre-built by the native agent com.valleypawn.ebay-customer-campaign on the 24th of the prior month.

## Step 0 — date gate + idempotency
1. Get today's date in America/New_York (`date +%Y-%m-%d` via osascript). If the day of month is NOT between 15 and 21 inclusive, stop immediately with no output — this is not the 3rd Thursday.
2. M = current month as YYYY-MM. PACK = `/Users/joshuadavis/Documents/Claude/Projects/eBay Customer Campaign/packs/M`.
3. If `PACK/chekkit_sent.json` exists, stop (already sent this month).
4. Verify these exist and are non-empty: `PACK/sms.txt` and `PACK/chekkit_Culpeper.csv`, `chekkit_Waynesboro.csv`, `chekkit_Harrisonburg.csv`, `chekkit_Lexington.csv`, `chekkit_Roanoke.csv`. If any list is missing, first try to rebuild: `cd '/Users/joshuadavis/Documents/Claude/Projects/eBay Customer Campaign' && /usr/bin/python3 build_text_lists.py M`. If still missing → ledger row, stop. Never send to some stores and skip others silently — if a store cannot be sent, record it in the ledger.
5. The message is the LAST line of `PACK/sms.txt` (it starts with "Valley Pawn:" and ends with "Reply STOP to opt out"). Read it exactly; do not edit it. It must be ≤160 characters.

## Step 1 — stage upload files
The Chrome extension's file_upload only accepts files in this session's own outputs folder. For each store, read the CSV via osascript `cat` and write an identical copy into this session's outputs folder (Write tool), e.g. `chekkit_Lexington.csv`. Header is `First Name,Last Name,Phone,Email`; the last row is Joshua's confirmation copy (`JOSHUA DAVIS,,8049304221,jdavis@fcfpawn.com`). Do not alter rows.

## Step 2 — send in Chekkit (proven runbook, same as chekkit-weekly-review-requests, verified 2026-07-22)
Order: Lexington, Waynesboro, Harrisonburg, Roanoke, Culpeper. For each store, in Chrome via Claude-in-Chrome (saved login; never ask anyone to log in):
1. Open https://dashboard.chekkit.io/campaigns. If a support chat panel covers the right side, close it with its X first.
2. Location switcher (top-left combobox "Select account") → pick "Valley Pawn - Culpeper" / "Valley Pawn - Waynesboro" / "Valley Pawn - Harrisonburg" / "Valley Pawn - Roanoke" / "Valley Pawn-Lexington". Reload /campaigns and confirm the switcher shows the right store.
3. Create New Campaign → Step 1: click "Upload CSV" → use `find` for the file input (type=file) → `file_upload` with that ref and the staged file for THIS store. Never click Browse Files. Column mapping auto-detects (Name/Phone/Email; Last Name = Don't import is fine) → Confirm & Import.
4. Validation screen: "has left a review" and "looks like a landline" warnings are expected → "Continue with All N Customers".
5. Step 2: Campaign Name = `Shop Online M` (e.g. `Shop Online 2026-10`). Do NOT use a template — type the message from sms.txt exactly into the message box. Verify it reads exactly as sms.txt → Next.
6. Step 3: Send immediately, One time → Send Campaign → compliance dialog: check all three boxes (business identified / consent / STOP opt-out) → Confirm & Send. Success = green toast "Your message will send shortly"; the campaign shows Queued → Sent in the list.
7. Record store, customers sent (N from step 4), send time.
If a store fails, retry it once from step 1. Continue with the remaining stores regardless.

## Step 3 — record + report
1. Write `PACK/chekkit_sent.json` via osascript heredoc: {"month":M,"sent_at":..., "stores":{"Culpeper":n,...}} — only stores confirmed sent.
2. If all 5 were sent: post to Slack #chekkit-updates (C0B0FQZ4FS8), plain language only:
```
Shop Us Online texts sent
• Culpeper: <n>
• Harrisonburg: <n>
• Lexington: <n>
• Roanoke: <n>
• Waynesboro: <n>
Total: <sum>
```
If the Slack post fails, write the numbers into the ledger row instead — never retry-spam.
3. If any store did not send: do NOT post partial numbers to Slack; ledger row naming the unsent stores (NEEDS_HUMAN: no — next Thursday's run will not resend, so say which stores still need sending).

Rules: never mention firearms; never use the name "Dixie Pawn"; plain language everywhere.