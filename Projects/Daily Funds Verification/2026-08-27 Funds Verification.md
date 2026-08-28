# Daily Funds Verification — 2026-08-27

**Status: COMPLETE — all 5 verified. DISCREPANCY on Harrisonburg.**

## Bottom line
\$7,000.00 expected vs \$5,000.00 actual. 4/5 stores matched; Harrisonburg is short \$2,000.00 versus what Joshua said he sent.

## Step 1 — Slack ledger (today, 2026-08-27 ET)
| Store | Channel | Request(s) | Joshua's reply | Net expected |
|---|---|---|---|---|
| CUL — Culpeper | #pepper-funds | GA ops need \$2000 (12:23) · Need \$2000 (16:24) | Sent 1k (12:31) · sent 1k (16:40) | \$2,000.00 |
| HAR — Harrisonburg | #harrisonburg-funds | Ops cash need \$2k (09:23) · Sending 2k for Richard Jamal Silver (13:49) · Ops cash need 2k (16:33) | sent 1k (10:34) · Sending 2k for Richard Jamal Silver (13:49) · sent 1k (16:40) | \$4,000.00 |
| LEX — Lexington | #lex-funds | (no messages today) | — | \$0.00 |
| ROA — Roanoke | #roanoke-funds | Ops cash need 2k (11:02) | Sent 1k (12:29) | \$1,000.00 |
| WAY — Waynesboro | #boro-funds | (no messages today) | — | \$0.00 |

Cancellations: none. **Total expected: \$7,000.00.**

## Step 2 — Bravo extraction
Trigger `daily-funds-verification-2026-08-27T18-05-35` → watcher status `partial` on first pass (CUL failed: EnsureStore error). Retry trigger `daily-funds-verification-2026-08-27T18-05-35-retry-1` → `success` on CUL. Final: 5/5 cells clean.

## Step 3 — Bravo signature rows (TENDER TRANSFER · BANK · Cash · negative leg)
| Store | Txn Num | Time | From→To | Amount |
|---|---|---|---|---|
| CUL | VP400065169 | 1:40 PM | BANK→SAFE | \$1,000.00 |
| CUL | VP400065183 | 5:00 PM | BANK→SAFE | \$1,000.00 |
| HAR | VA500054660 | 11:02 AM | BANK→SAFE | \$1,000.00 |
| HAR | VA500054693 | 4:56 PM | BANK→SAFE | \$1,000.00 |
| LEX | (no cash transfer) | — | — | \$0.00 |
| ROA | ROA00032372 | 12:58 PM | BANK→SAFE | \$1,000.00 |
| WAY | (no cash transfer) | — | — | \$0.00 |

## Step 5 — Reconciliation
| Store | Net expected (Slack) | Net actual (Bravo) | Status |
|---|---|---|---|
| CUL — Culpeper | \$2,000.00 | \$2,000.00 | ✓ Matched |
| HAR — Harrisonburg | \$4,000.00 | \$2,000.00 | ⚠ Discrepancy |
| LEX — Lexington | \$0.00 | \$0.00 | ✓ Matched |
| ROA — Roanoke | \$1,000.00 | \$1,000.00 | ✓ Matched |
| WAY — Waynesboro | \$0.00 | \$0.00 | ✓ Matched |
| **Total** | **\$7,000.00** | **\$5,000.00** | **4/5 matched** |

**Slack post: made** (#daily-funds-reconcilation).

_Report generated 2026-08-27 ~18:16 ET._
