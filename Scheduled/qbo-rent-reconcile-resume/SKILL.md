---
name: qbo-rent-reconcile-resume
description: One-time retry (~1 hr) — resume the FY2025 store-rent reconciliation in QBO after Intuit login throttling clears.
---

Resume the FY2025 store-rent reconciliation in QuickBooks Online for Full Circle Finance Inc DBA Valley Pawn. Joshua authorized this work and asked to retry ~1 hour after Intuit began throttling logins on 9/1/26.

## STEP 0 — MANDATORY CONTEXT LOAD
1. Read the `books-tax-strategy` skill IN FULL before touching QBO. Note §0 (session lock) and §3 failure mode (a) — double-posting a true-up is the single most repeated error in these books.
2. Read `~/Documents/Claude/Projects/Quickbooks Set UP/SESSION-COORDINATION.md`, newest section first. Sections 9/1/26 #15 and #16 contain the complete rent analysis, the approved plan, and the exact blocker.
3. Read `~/Documents/Claude/Projects/Quickbooks Set UP/QBO-SESSION-LOCK.md`. It is currently LOCKED by the rent work — that is this task's own lock. Keep it locked while working; release when done.

## STEP 1 — LOG IN (Chrome, autonomous, do NOT ask Joshua)
Open a FRESH Chrome tab to https://qbo.intuit.com/app/chartofaccounts. At the Intuit sign-in page, click the **jdavis@fcfpawn.com** account tile. Chrome autofills the password — do NOT type a password, just click **Continue**. The first navigation after login often bounces to the homepage; navigate again and it sticks.

If sign-in silently bounces back to the account picker more than TWICE, Intuit is still throttling. STOP, do not keep retrying (repeated attempts risk an account lockout), and DM Joshua one plain sentence saying you'll try again later. Do not post technical noise (vp-operating-rules Rule 16).

## STEP 2 — THE ONE CHECK BEFORE POSTING ANYTHING
Journal entry `RECLASS-2025-RENT` (txnId 13218, dated 12/31/2025, $71,210.15 each side) already booked FY2025 rent: Harrisonburg $38,362.80 + Waynesboro $29,347.35 + Culpeper $3,500. Its DEBIT account could not be read — the UI truncated it as "1 - Store Level Expenses:Store Occ…".

**Determine which account it debited.** Best method: run the `Rent & Lease` Account QuickReport, set Report period = Custom dates, From AND To both = 12/31/2025, and see whether RECLASS-2025-RENT appears. (Alternative: open https://qbo.intuit.com/app/journal?txnId=13218 and widen/read line 1 — but do NOT click into the account field, that marks the JE dirty; if it happens, leave via Cancel → Yes, never Save.)

- If it debited `Rent & Lease` → that $71,210.15 is already inside the current $84,245.31 balance. Reduce the top-up accordingly.
- If it debited a different account → adjust the math to suit.

Also note: `Rent & Lease` traced debits ($106,244.01) do not tie to its $84,245.31 total — roughly $21,998.70 of unexplained credits exist. Identify them before finalizing.

## STEP 3 — TARGET
Joshua's decision 9/1/26: **the lease / landlord rate letter is the source of truth, not the bank.** Book 12 months of contractual rent per store; any gap vs. cash paid becomes accrued rent payable.

TARGET `1 - Store Level Expenses:Store Occupancy:Rent & Lease` FY2025 = **$179,716**
- Culpeper $42,840.00 (4×$3,500 Jan–Apr + 8×$3,605 May–Dec)
- Harrisonburg $42,432.18 (9×$3,515.44 + 3×$3,597.74)
- Lexington $33,000.00 (12×$2,750)
- Waynesboro $31,827.81 (5×$2,614.43 + 7×$2,679.38, base+CAM)
- Roanoke $26,400.00 (12×$2,200)
- CubeSmart Culpeper storage $3,216.00 (actual — Joshua confirmed this is rent)

Post a 12/31/2025 JE numbered `RENT-TRUEUP-2025` for the NET difference only (target minus what is already correctly booked). Credit side: use `Uncategorized Expense` if that is where the underlying cash sits, otherwise an accrued-rent liability — decide based on what Step 2 reveals, and explain the choice in the memo. 2025 rule: no class values needed; click "Save" on the class dialog.

## STEP 4 — ALSO PENDING (only after rent is correct)
Joshua's coding decisions for the non-rent items currently sitting in `Rent & Lease`:
- Home mortgage (UnitedWholesale → ServiceMac, ~$57,394.75) → **Corp Rent** (interim, pending his Silverline consult)
- St. Johns County Utilities $986.73 → **Corp Utilities → Water & Sewer**
- Lowe's $54.95 → **Corp Repairs**
- St Johns Eye $328.00 → **Corp Medical**
- Sumter Rental Homes $4,400 and CubeSmart $3,216 → **stay** (both are real store rent)
- Richmond 1 ×2 ($313.58) → not yet assigned, leave

## STEP 5 — VERIFY AND LOG
Re-pull the FY2025 P&L. Confirm `Rent & Lease` hits the target and report the NEW Net Income (it was $382,129.72 before this rent work; rent corrections WILL move it — that is expected and intended here, unlike prior dollar-neutral reclasses). Then update SESSION-COORDINATION.md with what posted, update `books-tax-strategy` §7/§8 if the current-state table changed, and RELEASE the QBO session lock.

## STILL UNRESOLVED — do not skip
Lexington's payments have NOT been located in QBO. Paid by mailed check; lease came via James Larner (JML2P@uvahealth.org). Search QBO for likely payees before assuming the $33,000 is unbooked. Landlord payees already confirmed: Waynesboro = "Henry Liscio Com WEB PMTS"; Harrisonburg = "BEARSMANAGEMENT-"; Roanoke = "BLD*VALLEY RENTAL" (Feb–Oct) then "Sumter Rental Ho" (Nov–Dec); Culpeper = "ZELLE TO CARNES IRENE".

## TONE
Joshua's standing instruction, 9/1/26: "we find opportunities not problems… i dont want you to ever say problem again regarding our work." Frame findings as opportunities. Be concise and direct.