# Daily Funds Verification — 2026-08-29

**Status: COMPLETE — all 5 verified. All matched.**

## Bottom line
\$3,000.00 expected vs \$3,000.00 actual across all 5 stores. All 5 stores matched.

## Step 1 — Slack ledger (today, 2026-08-29 ET)
| Store | Channel | Request(s) | Joshua's reply | Net expected |
|---|---|---|---|---|
| CUL — Culpeper | #pepper-funds | Ops cash 1k (9:52 AM); Need ops cash 1k (1:13 PM) | sent 1k (11:13 AM); Sent 1k (4:00 PM) | \$2,000.00 |
| HAR — Harrisonburg | #harrisonburg-funds | ops cash need \$2k (9:26 AM) | sent 1k (11:13 AM) | \$1,000.00 |
| LEX — Lexington | #lex-funds | (no messages today) | (none) | \$0.00 |
| ROA — Roanoke | #roanoke-funds | (no funds request; unrelated message re: application) | (none) | \$0.00 |
| WAY — Waynesboro | #boro-funds | (no funds request; "still got paying customers in the store") | (none) | \$0.00 |

Cancellations: none. **Total expected: \$3,000.00.**

## Step 2 — Bravo extraction
Trigger \`daily-funds-verification-2026-08-29T18-03-53\` → watcher status \`success\` on 5/5 cells.

## Step 3 — Bravo signature rows (TENDER TRANSFER · BANK · Cash · negative leg)
| Store | Txn Num | Time | From→To | Amount |
|---|---|---|---|---|
| CUL | VP400065268 | 12:32 PM | SAFE→BANK | (\$1,000.00) |
| CUL | VP400065298 | 4:48 PM | SAFE→BANK | (\$1,000.00) |
| HAR | VA500054782 | 12:46 PM | SAFE→BANK | (\$1,000.00) |
| LEX | (no cash transfer) | — | — | \$0.00 |
| ROA | (no cash transfer) | — | — | \$0.00 |
| WAY | (no cash transfer) | — | — | \$0.00 |

## Step 5 — Reconciliation
| Store | Net expected (Slack) | Net actual (Bravo) | Status |
|---|---|---|---|
| CUL — Culpeper | \$2,000.00 | \$2,000.00 | ✓ Matched |
| HAR — Harrisonburg | \$1,000.00 | \$1,000.00 | ✓ Matched |
| LEX — Lexington | \$0.00 | \$0.00 | ✓ Matched |
| ROA — Roanoke | \$0.00 | \$0.00 | ✓ Matched |
| WAY — Waynesboro | \$0.00 | \$0.00 | ✓ Matched |
| **Total** | **\$3,000.00** | **\$3,000.00** | **5/5 matched** |

**Slack post: made (#daily-funds-reconcilation).**

_Report generated 2026-08-29 ~18:13 ET._
