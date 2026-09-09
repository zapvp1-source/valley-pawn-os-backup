# Daily Funds Verification — 2026-09-08

**Status: COMPLETE — all 5 verified. All stores matched.**

## Bottom line
$10,215.56 expected vs $10,215.56 actual across all 5 stores; every store matched exactly.

## Step 1 — Slack ledger (today, 2026-09-08 ET)
| Store | Channel | Request(s) | Joshua's reply | Net expected |
|---|---|---|---|---|
| CUL — Culpeper | #pepper-funds | GM cash ops $2k (9:39); large jewelry buy needs more (11:14); $2,500 more on top (11:45); Ops cash $2K (13:18) | Sent 1k (9:40), corrected to "Actually sent 1215.56" (9:41) — one transfer; sent 2k (11:56); sent 2k (13:28) | $5,215.56 |
| HAR — Harrisonburg | #harrisonburg-funds | ops cash need 2k (9:30); ops cash need 1K (14:10) | sent 1k (9:34); sent 1k (15:19) | $2,000.00 |
| LEX — Lexington | #lex-funds | (no funds request today — bonus-qualifier chat only) | (none) | $0.00 |
| ROA — Roanoke | #roanoke-funds | (no funds request today — two blank/media messages only) | (none) | $0.00 |
| WAY — Waynesboro | #boro-funds | Ops cash, need 2k (14:04); 900 in buys note (14:31) | sent 1k (9:34); Sent 2k (14:41) | $3,000.00 |

Cancellations: none. **Total expected: $10,215.56.**

## Step 2 — Bravo extraction
Trigger `daily-funds-verification-2026-09-08T18-05-32` → watcher status `success` on 5/5 cells.

## Step 3 — Bravo signature rows (TENDER TRANSFER · BANK · Cash · negative leg)
| Store | Txn Num | Time | From→To | Amount |
|---|---|---|---|---|
| CUL | VP400065730 | 12:17 PM | BANK→SAFE | $3,215.56 |
| CUL | VP400065747 | 1:51 PM | BANK→SAFE | $2,000.00 |
| HAR | VA500055145 | 9:48 AM | BANK→SAFE | $1,000.00 |
| HAR | VA500055179 | 3:46 PM | BANK→SAFE | $1,000.00 |
| LEX | — | — | (no cash transfer) | $0.00 |
| ROA | — | — | (no cash transfer) | $0.00 |
| WAY | VAP00075422 | 11:33 AM | BANK→SAFE | $1,000.00 |
| WAY | VAP00075446 | 3:38 PM | BANK→SAFE | $2,000.00 |

## Step 5 — Reconciliation
| Store | Net expected (Slack) | Net actual (Bravo) | Status |
|---|---|---|---|
| CUL — Culpeper | $5,215.56 | $5,215.56 | ✓ Matched |
| HAR — Harrisonburg | $2,000.00 | $2,000.00 | ✓ Matched |
| LEX — Lexington | $0.00 | $0.00 | ✓ Matched |
| ROA — Roanoke | $0.00 | $0.00 | ✓ Matched |
| WAY — Waynesboro | $3,000.00 | $3,000.00 | ✓ Matched |
| **Total** | **$10,215.56** | **$10,215.56** | **5/5 matched** |

**Slack post: made.**

_Report generated 2026-09-08 ~18:17 ET._
