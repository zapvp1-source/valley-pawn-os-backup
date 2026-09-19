# Daily Funds Verification — 2026-09-18

**Status: COMPLETE — all 5 verified. ALL MATCHED.**

## Bottom line
$4,000.00 expected vs $4,000.00 actual — matched across all 5 stores. Harrisonburg and Lexington each received a $2,000 cash transfer, confirmed in Bravo; Culpeper, Roanoke, and Waynesboro had no cash requests today.

## Step 1 — Slack ledger (today, 2026-09-18 ET)
| Store | Channel | Request(s) | Joshua's reply | Net expected |
|---|---|---|---|---|
| CUL — Culpeper | #pepper-funds | none (channel activity was Sandi noting customers in store + Joshua's eBay/phone-order notes, unrelated to cash) | n/a | $0.00 |
| HAR — Harrisonburg | #harrisonburg-funds | Walker: "Ops cash need 2k" (8:19 AM) | Joshua: "Sent 2k" (9:15 AM) | $2,000.00 |
| LEX — Lexington | #lex-funds | Uriah: "Need cash daily ops 2k" (9:44 AM); "Says funds not available" (10:06 AM, after Joshua's send) | Joshua: "sent 2k" (9:57 AM); troubleshot in-thread ("one sec" / "try now"); Uriah confirmed "Good now" (10:14 AM) — one transfer, re-confirmed once | $2,000.00 |
| ROA — Roanoke | #roanoke-funds | none | n/a | $0.00 |
| WAY — Waynesboro | #boro-funds | none (Chadd posted two photos with checkmark reactions + Joshua's "TYTY" — not a cash request) | n/a | $0.00 |

Cancellations: none. **Total expected: $4,000.00.**

## Step 2 — Bravo extraction
Trigger `daily-funds-verification-2026-09-18T1810-00` → watcher status `success` on 5/5 cells (CUL 28 rows, HAR 31 rows, LEX 33 rows, ROA 29 rows, WAY 35 rows).

## Step 3 — Bravo signature rows (TENDER TRANSFER · BANK · Cash · negative leg)
| Store | Txn Num | Time | From→To | Amount |
|---|---|---|---|---|
| CUL | — | — | (no cash transfer) | $0.00 |
| HAR | VA500055543 | 9:35 AM | BANK→SAFE | $2,000.00 |
| LEX | VA100110722 | 10:22 AM | BANK→SAFE | $2,000.00 |
| ROA | — | — | (no cash transfer) | $0.00 |
| WAY | — | — | (no cash transfer — BANK-leg activity present was two SAFE→BANK deposits ($1,200 + $2,000), i.e. cash going out to the bank, not funds received) | $0.00 |

## Step 5 — Reconciliation
| Store | Net expected (Slack) | Net actual (Bravo) | Status |
|---|---|---|---|
| CUL — Culpeper | $0.00 | $0.00 | ✓ Matched |
| HAR — Harrisonburg | $2,000.00 | $2,000.00 | ✓ Matched |
| LEX — Lexington | $2,000.00 | $2,000.00 | ✓ Matched |
| ROA — Roanoke | $0.00 | $0.00 | ✓ Matched |
| WAY — Waynesboro | $0.00 | $0.00 | ✓ Matched |
| **Total** | **$4,000.00** | **$4,000.00** | **5/5 matched** |

**Slack post: made** (#daily-funds-reconcilation).

_Report generated 2026-09-18 ~18:14 ET._
