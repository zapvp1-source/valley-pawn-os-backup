# Bravo Scrap Bucket Close-Out Procedure (Joshua-verified, UPDATED 2026-08-05)

Source: Joshua's exact instructions (v2, supersedes v1). THREE-PASS process per bucket
plus a store/till prerequisite before Pass 3. The final pass CANNOT BE UNDONE.
Never run Pass 3 without verified numbers and explicit approval on first runs.

## Pass 1 — Ship to vendor
1. Main screen → click "Inventory" (right side)
2. Click "Scrap Refining Process" (right side)
3. Select the bucket → click "Okay"
4. "Select Status" dropdown → "Shipping - Ship to Vendor"
5. "Total weight of scrap shipped" → enter in the number shown for "Combined Metal Weight"
   — VERIFY the two numbers match before proceeding
6. Click "Select Vendor" (bottom of left side)
7. In "E-mail address or business name" type "scrap" → Search → select the vendor
   that appears → OK
8. Click "Save" (top right)

## Pass 2 — Assay confirmation
9. Re-open the SAME bucket (steps 1-3). "Select Status" → "Assayed - Vendor Assay Result"
10. "Confirmed weight received" → enter the number from "Combined Metal Weight" (top right)
11. "Assay from vendor" → enter the number from "Calculated Assay-Gold" (top right)
12. VERIFY all numbers match → "Save"

## Prerequisite for Pass 3 — store and till MUST be open
- From main Dashboard: if "Open Store" shows, the store is closed — open it.
  If only "Open Till" shows, store is already open; just connect to the till.
- "Use expected values" for ALL counts when opening store and till → Save.
  If any receipt fails to print, click "OK" until all errors resolve.
- "Open Till" → Use expected values → Save.

## Pass 3 — Close (IRREVERSIBLE)
13. Inventory → Scrap Refining Process → same bucket. "Select Status" →
    "Close - Complete Transaction"
14. Click "Print Scrap Report" — shows estimated return vs actual received.
15. Enter actual payout for THIS bucket into "Amount Paid"
    → per-bucket dollar figure from the approved allocation workbook
    (reviews/YYYY-MM_allocations_*.csv, BUCKET DETAIL section). Never estimate.
16. "Tender Type" → "Cashiers Check" (avoids throwing off till or credit card numbers)
17. VERIFY every number before saving. THIS STEP CANNOT BE UNDONE.

## After all buckets closed at this store
- "Close Till" from main screen → Use expected values → Save.
- "Close Store" ONLY if processing OUTSIDE the store's business hours:
  Use expected values → Next → Use expected values → Save.
  DO NOT close the store during its business hours — close the till only.

## Rules
- Sum of all buckets' Amount Paid across all 5 stores must equal the settlement's
  net wire amount exactly.
- 2 gold buckets per store per cycle (no-stones + w/stones) = 10 buckets total.
- First runs are done WITH Joshua watching; pause for his explicit OK before EVERY
  Save. Unattended automation of this procedure requires his explicit sign-off
  after repeated verified successes.
- Store hours (for the close-store decision): CUL Mon-Sat 10-6; HAR/LEX/ROA/WAY
  Mon, Tue, Thu, Fri, Sat 10-6 (closed Wed & Sun).

## Live-run lessons (2026-08-05, ROA — first two buckets closed with Joshua)

1. ACTUAL status sequence in Bravo 2026.6.0.79: Open -> "Shipping - Ship to Vendor"
   -> "Received - Vendor Weight Confirmation" (enter BOTH Confirmed Weight Received
   AND Assay from Vendor here; saving this jumps the bucket straight to ASSAYED)
   -> "Close - Complete Transaction". There is no separate "Assayed" data-entry pass.
2. Once the Received/Assayed pass is saved, Confirmed Weight Received is LOCKED.
   Typos in it cannot be corrected afterward (observed: 63.50 vs 63.10 on ROA GOLD
   SCRAP — cosmetic only, does not affect money). Double-check before that save.
3. Clicking "Print Scrap Report" while "Close - Complete Transaction" is selected
   DISCARDS the unsaved status selection when you return. Order that works:
   view/print the report FIRST, then select Close status, then enter payment.
4. TYPING: Mac->Parallels keystrokes drop/buffer unpredictably. NEVER type dollar
   amounts directly. Method that works 100%: set the Mac clipboard to the exact
   value (osascript `set the clipboard to "6864.85"`), click the field, Ctrl+V,
   then zoom-verify the field shows the exact value before proceeding.
   prlctl exec SendKeys does NOT work (session 0, Access is denied).
5. Bravo's final dialog on Save: "Once Approved, this Scrap Process CANNOT BE
   VOIDED" -> Approve. Then a receipt-printer error ("Printer 'Receipts' does not
   exist") appears after most saves — click Ok through it, harmless.
6. Close Till triggers a Transfer Tender screen (Till -> Store Safe) carrying the
   cashiers checks; Close Store triggers Store Safe -> Bank Account for the same
   amount. Both prefill correctly with expected values; just Save through them.
7. Scrap report "Estimated Amount of Funds Receivable" is full-spot theoretical.
   Actual ~92-102% of estimate is normal under blended weight-pooled allocation
   (no-stones buckets land under estimate, stones buckets can land slightly over).
8. Completed this session: ROA GOLD SCRAP $6,864.85 (GP 59.97%), ROA GOLDW/STONE
   $11,249.13 (GP 53.59%). Till+store closed, $18,113.98 safe->bank transfer done.
   Remaining: CUL 17,710.11 / HAR 16,093.84 / LEX 5,550.69 / WAY 8,691.46 (2 buckets
   each, amounts per bucket in the workbook).
