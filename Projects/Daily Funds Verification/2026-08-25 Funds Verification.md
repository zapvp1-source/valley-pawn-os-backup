# Daily Funds Verification — 2026-08-25

**Status: COMPLETE — all 5 verified. All matched.**

## Bottom line
$9,000.00 expected vs $9,000.00 actual across all 5 stores; every store matched.

## Step 1 — Slack ledger (today, 2026-08-25 ET)
| Store | Channel | Request(s) | Joshua's reply | Net expected |
|---|---|---|---|---|
| CUL — Culpeper | #pepper-funds | Rob: need \$1500 (9:53a); Rob: Ops cash, need 2k (2:17p, jewelry buy) | sent 2k (9:58a); sent 2k (2:34p) | \$4,000.00 |
| HAR — Harrisonburg | #harrisonburg-funds | Walker: need \$2k (9:30a); Walker: need \$1k asap (4:50p) | sent 2k (9:58a); Sent 1k (4:54p) | \$3,000.00 |
| LEX — Lexington | #lex-funds | (none today) | (none) | \$0.00 |
| ROA — Roanoke | #roanoke-funds | (none today) | (none) | \$0.00 |
| WAY — Waynesboro | #boro-funds | Chadd: Ops cash, need 2k (9:22a) | Sent 2K (9:58a) | \$2,000.00 |

Cancellations: none. **Total expected: \$9,000.00.**

## Step 2 — Bravo extraction
Trigger \`daily-funds-verification-2026-08-25T18-04-43\` → watcher status \`success\` on 5/5 cells.

## Step 3 — Bravo signature rows (TENDER TRANSFER · BANK · Cash · negative leg)
| Store | Txn Num | Time | From→To | Amount |
|---|---|---|---|---|
| CUL | VP400065051 | 11:15 AM | BANK→SAFE | \$2,000.00 |
| CUL | VP400065065 | 2:55 PM | BANK→SAFE | \$2,000.00 |
| HAR | VA500054601 | 10:15 AM | BANK→SAFE | \$2,000.00 |
| HAR | VA500054626 | 5:15 PM | BANK→SAFE | \$1,000.00 |
| LEX | (no cash transfer) | — | — | \$0.00 |
| ROA | (no cash transfer) | — | — | \$0.00 |
| WAY | VAP00074829 | 10:41 AM | BANK→SAFE | \$2,000.00 |

## Step 5 — Reconciliation
| Store | Net expected (Slack) | Net actual (Bravo) | Status |
|---|---|---|---|
| CUL — Culpeper | \$4,000.00 | \$4,000.00 | ✓ Matched |
| HAR — Harrisonburg | \$3,000.00 | \$3,000.00 | ✓ Matched |
| LEX — Lexington | \$0.00 | \$0.00 | ✓ Matched |
| ROA — Roanoke | \$0.00 | \$0.00 | ✓ Matched |
| WAY — Waynesboro | \$2,000.00 | \$2,000.00 | ✓ Matched |
| **Total** | **\$9,000.00** | **\$9,000.00** | **5/5 matched** |

**Slack post: made (#daily-funds-reconcilation).**

_Report generated 2026-08-25 ~18:15 ET._
