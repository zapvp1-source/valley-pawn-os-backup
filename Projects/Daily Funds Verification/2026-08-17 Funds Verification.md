# Daily Funds Verification — 2026-08-17

**Status: COMPLETE — all 5 verified. ALL MATCHED.**

## Bottom line
$10,000.00 expected vs $10,000.00 actual across all 5 stores — every dollar sent today is confirmed in the Bravo safes.

## Step 1 — Slack ledger (today, 2026-08-17 ET)
| Store | Channel | Request(s) | Joshua's reply | Net expected |
|---|---|---|---|---|
| CUL — Culpeper | #pepper-funds | 15:34 GA! Ops Cash Needed $2k | 15:45 Sent 2k | $2,000.00 |
| HAR — Harrisonburg | #harrisonburg-funds | 09:32 Ops cash need 2k; 11:50 Ops cash need 2k (after $1,300 eBay metals sales cleaned out till) | 09:45 Sent 2k. Gm; 12:50 Sent 2k | $4,000.00 |
| LEX — Lexington | #lex-funds | 12:54 Ops cash need 2k | 13:03 Sent 2k | $2,000.00 |
| ROA — Roanoke | #roanoke-funds | 16:24 Ops cash need 2k | 16:27 Sent 2k | $2,000.00 |
| WAY — Waynesboro | #boro-funds | (no messages today) | — | $0.00 |

Cancellations: none. **Total expected: $10,000.00.**

Note: the Lexington thread also contained an unrelated $20 till refund to a customer ("give the lady back her 20 bucks") — not a store funds transfer, excluded from the ledger.

## Step 2 — Bravo extraction
Trigger `daily-funds-verification-2026-08-17T18-04-50` → watcher status `success` on 5/5 cells.

## Step 3 — Bravo signature rows (TENDER TRANSFER · BANK · Cash · negative leg)
| Store | Txn Num | Time | From→To | Amount |
|---|---|---|---|---|
| CUL — Culpeper | VP400064699 | 4:12 PM | BANK→SAFE | $2,000.00 |
| HAR — Harrisonburg | VA500054289 | 10:04 AM | BANK→SAFE | $2,000.00 |
| HAR — Harrisonburg | VA500054301 | 1:26 PM | BANK→SAFE | $2,000.00 |
| LEX — Lexington | VA100109994 | 2:52 PM | BANK→SAFE | $2,000.00 |
| ROA — Roanoke | ROA00031999 | 4:56 PM | BANK→SAFE | $2,000.00 |
| WAY — Waynesboro | — | — | (no cash transfer) | $0.00 |

## Step 5 — Reconciliation
| Store | Net expected (Slack) | Net actual (Bravo) | Status |
|---|---|---|---|
| CUL — Culpeper | $2,000.00 | $2,000.00 | ✓ Matched |
| HAR — Harrisonburg | $4,000.00 | $4,000.00 | ✓ Matched |
| LEX — Lexington | $2,000.00 | $2,000.00 | ✓ Matched |
| ROA — Roanoke | $2,000.00 | $2,000.00 | ✓ Matched |
| WAY — Waynesboro | $0.00 | $0.00 | ✓ Matched |
| **Total** | **$10,000.00** | **$10,000.00** | **5/5 matched** |

**Slack post: made (#daily-funds-reconcilation).**

_Report generated 2026-08-17 ~18:15 ET._
