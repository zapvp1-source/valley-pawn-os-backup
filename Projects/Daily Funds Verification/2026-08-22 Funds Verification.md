# Daily Funds Verification — 2026-08-22

**Status: COMPLETE — all 5 verified. ALL MATCHED.**

## Bottom line
\$4,000.00 expected vs \$4,000.00 actual across all 5 stores; every store matched exactly.

## Step 1 — Slack ledger (today, 2026-08-22 ET)
| Store | Channel | Request(s) | Joshua's reply | Net expected |
|---|---|---|---|---|
| CUL — Culpeper | #pepper-funds | (none — only "Still have several customers in store." at 6:01 PM) | — | \$0.00 |
| HAR — Harrisonburg | #harrisonburg-funds | (none — jewelry estimator/reloan chatter only) | — | \$0.00 |
| LEX — Lexington | #lex-funds | (none — one blank message at 12:49 PM) | — | \$0.00 |
| ROA — Roanoke | #roanoke-funds | Benjie 9:29 AM "Ops cash need 2k" | Joshua 10:14 AM "Down for the day"; 10:15 AM "Sent 2k. Nevermind" (read as walking back the "down" comment, not canceling — confirmed by Bravo) | \$2,000.00 |
| WAY — Waynesboro | #boro-funds | Chadd 9:11 AM "Ops cash, need 2k GM" | Joshua 10:15 AM "Sent 2k" | \$2,000.00 |

Cancellations: none. **Total expected: \$4,000.00.**

## Step 2 — Bravo extraction
Trigger \`daily-funds-verification-2026-08-22T18-05-11\` → watcher status \`success\` on 5/5 cells.

## Step 3 — Bravo signature rows (TENDER TRANSFER · BANK · Cash · negative leg)
| Store | Txn Num | Time | From→To | Amount |
|---|---|---|---|---|
| CUL | — | — | (no cash transfer) | \$0.00 |
| HAR | — | — | (no cash transfer) | \$0.00 |
| LEX | — | — | (no cash transfer) | \$0.00 |
| ROA | ROA00032187 | 11:38 AM | BANK→SAFE | \$2,000.00 |
| WAY | VAP00074722 | 10:51 AM | BANK→SAFE | \$2,000.00 |

## Step 5 — Reconciliation
| Store | Net expected (Slack) | Net actual (Bravo) | Status |
|---|---|---|---|
| CUL — Culpeper | \$0.00 | \$0.00 | ✓ Matched |
| HAR — Harrisonburg | \$0.00 | \$0.00 | ✓ Matched |
| LEX — Lexington | \$0.00 | \$0.00 | ✓ Matched |
| ROA — Roanoke | \$2,000.00 | \$2,000.00 | ✓ Matched |
| WAY — Waynesboro | \$2,000.00 | \$2,000.00 | ✓ Matched |
| **Total** | **\$4,000.00** | **\$4,000.00** | **5/5 matched** |

**Slack post: made (#daily-funds-reconcilation).**

_Report generated 2026-08-22 ~18:15 ET._
