# Daily Funds Verification — 2026-07-23

**Status: COMPLETE — all 5 verified. All matched.**

## Bottom line
$10,000.00 expected vs $10,000.00 actual across all 5 stores. Every dollar sent today is confirmed in the Bravo safes.

## Step 1 — Slack ledger (today, 2026-07-23 ET)
| Store | Channel | Request(s) | Joshua's reply | Net expected |
|---|---|---|---|---|
| CUL — Culpeper | #pepper-funds | (no funds request today) | (none) | $0.00 |
| HAR — Harrisonburg | #harrisonburg-funds | Ops cash need 2k (14:23) | sent 2k (14:25) | $2,000.00 |
| LEX — Lexington | #lex-funds | Need cash for daily ops if available (12:14) | sent 2k (12:33) | $2,000.00 |
| ROA — Roanoke | #roanoke-funds | Need funds 2k (11:32) | sent 2k (11:49) | $2,000.00 |
| WAY — Waynesboro | #boro-funds | Ops cash, need 2k! (10:03); Ops cash, need 2k (15:49) | sent 2k (10:08); sent 2k (15:55) | $4,000.00 |

Cancellations: none. **Total expected: $10,000.00.**

## Step 2 — Bravo extraction
Trigger `daily-funds-verification-2026-07-23T18-15-31` → watcher status `success` on 5/5 cells.

## Step 3 — Bravo signature rows (TENDER TRANSFER · BANK · Cash · negative leg)
| Store | Txn Num | Time | From→To | Amount |
|---|---|---|---|---|
| CUL | (none) | — | — | (no cash transfer) |
| HAR | VA500053376 | 6:15 PM | BANK→SAFE | $2,000.00 |
| LEX | VA100109375 | 1:51 PM | BANK→SAFE | $2,000.00 |
| ROA | ROA00031088 | 12:31 PM | BANK→SAFE | $2,000.00 |
| WAY | VAP00073329 | 11:10 AM | BANK→SAFE | $2,000.00 |
| WAY | VAP00073368 | 4:20 PM | BANK→SAFE | $2,000.00 |

## Step 5 — Reconciliation
| Store | Net expected (Slack) | Net actual (Bravo) | Status |
|---|---|---|---|
| CUL — Culpeper | $0.00 | $0.00 | ✓ Matched |
| HAR — Harrisonburg | $2,000.00 | $2,000.00 | ✓ Matched |
| LEX — Lexington | $2,000.00 | $2,000.00 | ✓ Matched |
| ROA — Roanoke | $2,000.00 | $2,000.00 | ✓ Matched |
| WAY — Waynesboro | $4,000.00 | $4,000.00 | ✓ Matched |
| **Total** | **$10,000.00** | **$10,000.00** | **5/5 matched** |

**Slack post: made.**

_Report generated 2026-07-23 ~18:22 ET._
