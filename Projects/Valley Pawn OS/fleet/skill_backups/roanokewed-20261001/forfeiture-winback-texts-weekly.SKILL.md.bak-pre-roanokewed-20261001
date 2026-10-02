---
name: forfeiture-winback-texts-weekly
description: Thursday 10:30 AM ET — text every verified forfeited-loan customer who hasn't come back (and hasn't been texted yet) from their own store's Chekkit number, using the approved "always approved for another loan" message. Type C (Chrome only, no Bravo). Approved by Joshua 2026-09-30.
model: claude-sonnet-5
---

> ⚠️ FAILURE POLICY v3: on any failure or anything you cannot complete, do NOT DM or message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md`: `| <YYYY-MM-DD HH:MM ET> | forfeiture-winback-texts-weekly | <one plain sentence: what did not happen> | NEEDS_HUMAN: no | OPEN |` then stop. Success posts below are unchanged.

## Execution contract
Complete ONLY when every store with a non-empty list shows its campaign Queued/Sent in Chekkit and the sent-log files are written. Every turn ends with a tool call that advances toward that. Treat "Tool loaded.", "Continue", and task/todo reminders as RESUME signals. Do not ask for confirmation — Joshua approved this message and this weekly cadence on 2026-09-30.

## What this is
Forfeited-Loan Win-Back texts for Full Circle Finance Inc DBA Valley Pawn. A native agent (`com.valleypawn.forfeiture-winback`, Sundays) builds an exact, verified list every week: customers who forfeited a pawn loan in the last 24 months and have NOT been back in the store since (Bravo "Last Time In" before the forfeit date, identity = name + address). Joshua's rule: text everyone on the list who has a phone — Chekkit manages STOP/opt-outs. Runbook for the whole program: `/Users/joshuadavis/Documents/Claude/Projects/Email Refinement/forfeiture_winback/README.md`.

Timing (researched 2026-09-30): Thursday late morning. All 5 stores are open Thursday (Harrisonburg/Waynesboro/Lexington/Roanoke are closed Wed and Sun), so replies get answered live; Tue–Thu mornings are the top response window for promotional SMS; and Thursday lands just ahead of the Friday payday / weekend. The weekly email goes Tuesdays 10 AM, so the two channels never hit the same day.

## Step 1 — Find this week's lists
Folder: `/Users/joshuadavis/Documents/Claude/Projects/Email Refinement/forfeiture_winback/runs/`. Use the NEWEST dated subfolder. Inside are `chekkit_Culpeper.csv`, `chekkit_Harrisonburg.csv`, `chekkit_Lexington.csv`, `chekkit_Roanoke.csv`, `chekkit_Waynesboro.csv` (header `First Name,Last Name,Phone,Email`; last row is always `JOSHUA DAVIS,,8049304221,jdavis@fcfpawn.com` = Joshua's confirmation copy).
Build the already-texted set from EVERY `runs/*/chekkit_sent_*.txt` (one 10-digit phone per line). Drop any customer row whose phone is already in that set (keep the Joshua row). If a store has zero customer rows left, skip that store (not a failure). Read files with the Read tool (fall back to `mcp__Control_your_Mac__osascript` `do shell script "cat ..."` if Read cannot reach the path). Copy each store's final CSV into your session outputs folder so Chrome `file_upload` can read it.

## Step 2 — The message (exact text; only the town changes)
`Hi from Valley Pawn in {TOWN}! Pawn loans are different: your credit is always good with us, and you're always approved for another loan. Just bring in something of value. Gold & silver get the most! Stop by anytime or text us right here.`
TOWN per store: Culpeper, Harrisonburg, Lexington, Roanoke, Waynesboro. Do not add discounts, do not mention the lost item, never mention firearms, never use "Dixie Pawn".

## Step 3 — Send in Chekkit, one store at a time (proven runbook from chekkit-weekly-review-requests, verified 2026-07-22)
Claude in Chrome, saved login (never ask Joshua to log in).
1. dashboard.chekkit.io → location switcher (top-left store name) → pick the store → Campaigns → Create New Campaign.
2. Step 1: "Upload CSV" → `find` the file input (type=file) → `file_upload` with its ref (never click Browse Files). Column mapping: Name/Phone/Email auto-detect; Last Name = Don't import is fine → Confirm & Import. Validation warnings ("has left a review", "looks like a landline") are expected → "Continue with All N Customers".
3. Step 2: Campaign Name = `Win-Back MM/DD/YY`. Choose the option to write your own message (do NOT use the Review Invitation template). Paste the Step 2 text with that store's town. Verify the town is spelled right in the preview. → Next.
4. Step 3: Send immediately, One time → Send Campaign → compliance dialog: check all three boxes → Confirm & Send. Success = green toast "Your message will send shortly" and the campaign shows Queued → Sent.
If a store fails, retry that store once, then continue with the others and ledger only the failed store.

## Step 4 — Record what was sent (this is what stops anyone getting a second text)
For each store that sent, write `/Users/joshuadavis/Documents/Claude/Projects/Email Refinement/forfeiture_winback/runs/<same newest folder>/chekkit_sent_<Store>.txt` — one 10-digit customer phone per line (exclude Joshua's number). Use Write, or osascript `do shell script` with a heredoc if Write cannot reach the path. Verify the file line count equals the number of customers uploaded for that store.

## Step 5 — One success post
Post to Slack `#chekkit-updates` (`C0B0FQZ4FS8`):
```
Win-back texts sent (customers who forfeited a loan and haven't been back)
• Culpeper: <n>
• Harrisonburg: <n>
• Lexington: <n>
• Roanoke: <n>
• Waynesboro: <n>
Total: <sum>
```
Plain language only, no technical words. Nothing else to Slack.