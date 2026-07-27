---
name: vsp-nics-fee-monthly-check
description: Monthly check of Virginia State Police eReceivables for each store's NICS gun-check fee invoice; surface amounts for Joshua to approve before paying.
model: claude-sonnet-5
---

Check the Virginia State Police eReceivables billing portal for each Valley Pawn store's monthly NICS / firearms background-check (CHRI) fee invoice, and report what's due. DO NOT pay anything — only gather invoice details and surface them for Joshua to approve.

CONTEXT
- Full Circle Finance Inc DBA Valley Pawn operates 5 VA pawn stores, each a registered VFTP firearms dealer billed monthly by VSP for NICS/CHRI fees.
- VSP posts each invoice on the 1st of the month; this task runs on the 5th to catch the new invoice.
- Portal: https://ebilling.vsp.virginia.gov  (Oracle iReceivables "eReceivables Self Service Portal")
- Login username: X009686  (password is saved in Google Chrome — let it autofill; the username field pre-populates. If login fails, STOP and notify Joshua that the saved password needs re-entry. Never ask Joshua to do anything mid-run except this.)
- NICS invoices appear as transactions named "FIRE-#####" (Invoice type). Typical amounts are small (e.g. $64, $90).

STEPS (use the Claude in Chrome browser tools — this is a web app)
1. Navigate to https://ebilling.vsp.virginia.gov and log in as X009686 using the saved Chrome password.
2. On the "Customers / Search" page, click **Go** WITHOUT checking "Show All Sites" or "Show All Customers". This returns the 5 live billing accounts:
   - Roanoke  — VALLEY PAWN, customer #15848
   - Waynesboro — VALLEY PAWN 2/FULL CIRCLE FINANCE, INC., #16284
   - Harrisonburg — VALLEY PAWN 2/FULL CIRCLE FINANCE, INC., #16627
   - Culpeper — JOSHUA CHRISTIAN DAVIS, #280758
   - Lexington — VALLEY PAWN -4 LEXINGTON, #283759
3. For EACH of the 5 accounts, click its Account Summary (glasses) icon to open the Bill Management dashboard and read the **Account Balance / Overdue Receivables / Total Open Receivables**.
4. If an account shows a balance > $0, click the **Account** tab, set **Status = Open/pending**, click **Go**, and record each open invoice: invoice number (FIRE-#####), original amount, invoice date, and due date.
5. Return to Customer Search between accounts (link is "Return to Customer Search" or the Customer Search nav button).

OUTPUT
- Produce a clear summary table: per store — store name, customer #, balance, and any open invoice (number, amount, due date). Sum the total owed across all stores.
- If every store is $0.00, say so plainly ("all five stores clear, nothing due this month").
- If any invoices are open, list them with the total and end with: "Reply to approve and I'll go through the payment flow with you (open the account → Account tab → check the invoice → MAKE PAYMENT)."
- Do NOT initiate or submit any payment. Payment happens only after Joshua approves the amounts.

REMINDERS
- Reference: the pay flow once approved is Account Summary → Account tab → select the open FIRE invoice → MAKE PAYMENT (ACH preferred; credit card now carries a transaction fee per VSP policy).
- Known data issues to ignore for billing but keep in mind: Culpeper is billed under Joshua's personal name (#280758) and Lexington (#283759) still lists the old 439 East Nelson St address — these are pending corrections with VSP, not blockers to payment.