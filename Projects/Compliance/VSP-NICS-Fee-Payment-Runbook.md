# VSP NICS / Gun-Check Fee Payment — Runbook

**Purpose:** Pay each Valley Pawn store's monthly Virginia State Police firearms background-check (NICS/CHRI) fee through the VSP eReceivables billing portal.

**Portal:** https://ebilling.vsp.virginia.gov (Oracle iReceivables — "eReceivables Self Service Portal")
**Login username:** X009686 (password saved in Chrome)
**Billing cycle:** VSP posts each invoice on the **1st** of the month. We check and pay starting the **5th**.

**⚠️ There is NO automated VSP check.** A task called `vsp-nics-fee-monthly-check` is referenced in
older copies of this runbook and in `BUSINESS_OS.md` — **it has never existed** in the scheduled-task
registry or on disk (verified 2026-09-06). Do not go looking for it and do not assume the balance was
checked. The balance check is a **documented manual step on the 5th**, surfaced as a row in
`Compliance/OBLIGATIONS.json` (`vsp-nics-fee-monthly`) and reminded by the Monday compliance brief
(`Valley Pawn OS/bin/compliance_brief.py`, native launchd `com.valleypawn.compliance-brief`).

**⛔ BLOCKED as of 2026-09-06:** the portal rejected the Chrome-saved password on the first attempt
(the account locks after 5 failures, so no further attempts were made). **Joshua must sign in once
and re-save the password in Chrome**; after that the monthly balance read can resume. Until then no
balance has been verified since 2026-06-23.

---

## The 5 store billing accounts

Pulled by clicking **Go** on the Customers/Search page **with no boxes checked** (do NOT check "Show All Sites" / "Show All Customers" — that mixes in legacy inactive sites).

| Store | Account name in portal | Customer # | Address on file |
|---|---|---|---|
| Roanoke | VALLEY PAWN | 15848 | 2362 Peters Creek Rd ✓ |
| Waynesboro | VALLEY PAWN 2/FULL CIRCLE FINANCE, INC. | 16284 | 1321 W Broad St ✓ |
| Harrisonburg | VALLEY PAWN 2/FULL CIRCLE FINANCE, INC. | 16627 | 1790 E Market St ✓ |
| Culpeper | **JOSHUA CHRISTIAN DAVIS** | 280758 | 571 James Madison Hwy ✓ (account under personal name — pending correction) |
| Lexington | VALLEY PAWN -4 LEXINGTON | 283759 | **439 East Nelson St** ✗ (old address — should be 125 Walker St — pending correction) |

---

## Workflow

### 1. Log in
Go to https://ebilling.vsp.virginia.gov → username **X009686** (password autofills from Chrome) → **Login**.

### 2. Pull the accounts
On the **Customers / Search** page, click **Go** with nothing selected. The 5 live accounts above appear.

### 3. Check each store's balance (one at a time)
Click the **Account Summary** (glasses) icon on a store's row. The Bill Management dashboard shows:
- **Your Account Balance**, **Overdue Receivables**, **Total Open Receivables**.
- $0.00 across the board = nothing due for that store.

Use **Return to Customer Search** to go back and repeat for the next store.

### 4. Find the invoice(s) to pay
On a store with a balance > $0, click the **Account** tab → set **Status = Open/pending** → **Go**.
- Monthly NICS bills show as **FIRE-#####** (Invoice type), with an amount, invoice date, and due date.

### 5. Pay (only after confirming amounts)
Check the box next to each open FIRE invoice → click **MAKE PAYMENT** → complete the payment.
- **ACH/e-check preferred.** Per VSP's posted policy, **credit-card payments will soon carry a transaction fee**, and past-due invoices can incur late penalties (VA Code § 2.2-4805 / § 6.2-302).

---

## Notes & pending items
- The portal supports paying online (MAKE PAYMENT) — not just viewing. (Older VSP guidance said check-by-mail; the portal flow supersedes that.)
- **Pending VSP corrections (separate from payment):**
  1. Culpeper (#280758) is billed under "Joshua Christian Davis" — should be Full Circle Finance Inc / Valley Pawn.
  2. Lexington (#283759) address is the old 439 East Nelson St — should be 125 Walker St.
  - Both are FFL/VFTP premises records → route to VSP Firearms Transaction Center (firearms@vsp.virginia.gov), cc billing (billingandpayments@vsp.virginia.gov, 804-674-2151).
- Help desk: Firearms Transaction Center (804) 674-2292.

*Last verified: 2026-06-23. June invoices confirmed paid (e.g. Harrisonburg FIRE-49581, $64.00, paid 06/04).*
