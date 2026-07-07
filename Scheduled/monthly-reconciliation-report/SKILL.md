---
name: monthly-reconciliation-report
description: Pull QBO month-end reconciliation + close package for Valley Pawn and email it to Joshua and Silverline CPA
---

> ⚠️ **FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE.** If this task fails, errors out, or cannot complete its intended work for any reason, DO NOT post anything to Slack — no error messages, no partial results, no "I couldn't finish" notices. Joshua reviews every run inside Claude to confirm success or failure, so a failed run must stay completely silent on Slack. Only post to Slack once the task has genuinely completed the work it was designed to do. Posting failure or error noise clutters Slack and reflects poorly on the team.

You are compiling the monthly Reconciliation & Month-End Close Package for Full Circle Finance Inc DBA Valley Pawn and delivering it to Joshua and the outside CPA.

## Context
- Company: Full Circle Finance Inc DBA Valley Pawn (5 store locations: Staunton, Harrisonburg, Waynesboro, Culpeper, Roanoke)
- Active QBO book: login `jdavis@fcfpawn.com` (company name "Full Circle Finance Inc"). Chrome has the saved password — do NOT ask Joshua to enter credentials.
- Legacy QBO book: `butterfliesllc` (historical — do not pull reports from this one)
- CPA: Liana at Silverline — her email is stored in the valley-pawn-context skill under "team contacts"; read that skill first to get the current address.
- The Reconciliation Report in QBO is not directly schedulable inside QBO, which is why this runs as a Cowork scheduled task.

## Target period
"Last month" = the calendar month that ended most recently (if today is May 5, the target is April 1 – April 30).

## Steps

1. **Load context.** Read the `valley-pawn-context` skill to confirm the current CPA email, store list, and any updates to the QBO book login. Also read `/sessions/beautiful-lucid-ramanujan/mnt/Claude 4 back up/QBO-new-book-context-delta.md` if present for any pending book details.

2. **Log into QBO.** Open https://qbo.intuit.com/ in Chrome via the Claude-in-Chrome MCP. If prompted, pick the `jdavis@fcfpawn.com` account tile and let Chrome's saved password auto-fill the Continue page. If an MFA/SMS challenge appears, stop and tell Joshua in the notification — do not attempt to complete MFA.

3. **Pull the Reconciliation Reports** for every bank and credit-card account that was reconciled during the target month:
   - Go to https://qbo.intuit.com/app/reports → search "Reconciliation Reports" → open the hub.
   - For each account listed, find the reconciliation whose statement ending date falls in the target month and click into its Reconciliation Report (Summary + Detail).
   - Export each to PDF and save to `/sessions/beautiful-lucid-ramanujan/mnt/Claude 4 back up/reconciliation-reports/<YYYY-MM>/<account-name>.pdf`.
   - If any account was NOT reconciled for the month, note it explicitly in the summary — do NOT silently skip it.

4. **Pull the Month-End Close Package** for the same period:
   - Profit and Loss (this month, accrual basis, by Class so the store breakdown is visible)
   - Balance Sheet (as of last day of target month)
   - A/R Aging Summary (as of last day of target month)
   - A/P Aging Summary (as of last day of target month)
   - Reconciliation Discrepancy Report (for the target month, all accounts)
   Export each to PDF into the same `reconciliation-reports/<YYYY-MM>/` folder.

5. **Write a one-page summary** (`reconciliation-reports/<YYYY-MM>/SUMMARY.md`) covering:
   - Which accounts were reconciled and which were not
   - Any reconciliation discrepancies and their amounts
   - P&L top-line for the month (revenue, net income) and trend vs. prior month
   - A/R and A/P totals and anything >60 days
   - Action items for Joshua (what still needs attention before the CPA review)

6. **Email the package** via the Gmail MCP (`mcp__*__gmail_create_draft`):
   - To: Joshua (`zapvp1@me.com`) and Liana at Silverline (use the address from valley-pawn-context)
   - Subject: `Valley Pawn – <Month Year> Month-End Reconciliation Package`
   - Body: paste the SUMMARY.md contents inline, list the attached files, and sign off from Joshua. Do NOT send automatically — leave as a draft for Joshua's final review per the "explicit permission before sending" rule.
   - Attach the PDFs from step 3 and step 4.

7. **Post a short status message** to Joshua's Slack DM (or #accounting channel if configured in valley-pawn-context) noting the draft is ready for review with a link to the folder.

## Success criteria
- Folder `reconciliation-reports/<YYYY-MM>/` exists with a PDF for every reconciled account + the close-package reports + SUMMARY.md
- Gmail draft exists, addressed correctly, with all PDFs attached
- Slack notification posted
- If any step is blocked (MFA, missing account, locked period), stop at that step and notify Joshua rather than guessing

## Constraints
- Follow Joshua's standing directive: act autonomously, use Chrome saved passwords, do not ask permission for in-scope steps
- Never send the final email — always leave as draft
- If the QBO session expires mid-run, re-login and resume; don't restart from scratch
- Do not run this against the legacy `butterfliesllc` book under any circumstance