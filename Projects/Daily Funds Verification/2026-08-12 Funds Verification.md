# Daily Funds Verification — 2026-08-12

**Status: COMPLETE — all 5 verified. ALL MATCHED.**

## Bottom line
$2,000.00 expected vs $2,000.00 actual across all 5 stores; every store matched with no discrepancies.

## Step 1 — Slack ledger (today, 2026-08-12 ET)
| Store | Channel | Request(s) | Joshua's reply | Net expected |
|---|---|---|---|---|
| CUL — Culpeper | #pepper-funds | Bree Grayson 11:05:50 AM: "Ops Cash needed \$2k" | Joshua 11:19:26 AM: "GM, sent 2k. Lets get these Jewlery Counts Straightened out..." | \$2,000.00 |
| HAR — Harrisonburg | #harrisonburg-funds | none | none | \$0.00 |
| LEX — Lexington | #lex-funds | none | none | \$0.00 |
| ROA — Roanoke | #roanoke-funds | none | none | \$0.00 |
| WAY — Waynesboro | #boro-funds | none | none | \$0.00 |

Cancellations: none. **Total expected: \$2,000.00.**

## Step 2 — Bravo extraction
Trigger \`daily-funds-verification-2026-08-12T18-04-35\` → watcher status \`partial\` on 4/5 cells (LEX errored: "UIA click sequence failed: SetExportFilePath: File path LayoutItem not found"). Retry \`daily-funds-verification-retry1-2026-08-12T18-04-35\` → \`success\` on LEX. Final: 5/5 cells clean, no watcher restart needed.

## Step 3 — Bravo signature rows (TENDER TRANSFER · BANK · Cash · negative leg)
| Store | Txn Num | Time | From→To | Amount |
|---|---|---|---|---|
| CUL | VP400064467 | 12:17 PM | BANK→SAFE | \$2,000.00 |
| HAR | (no cash transfer) | — | — | \$0.00 |
| LEX | (no cash transfer) | — | — | \$0.00 |
| ROA | (no cash transfer) | — | — | \$0.00 |
| WAY | (no cash transfer) | — | — | \$0.00 |

## Step 5 — Reconciliation
| Store | Net expected (Slack) | Net actual (Bravo) | Status |
|---|---|---|---|
| CUL — Culpeper | \$2,000.00 | \$2,000.00 | ✓ Matched |
| HAR — Harrisonburg | \$0.00 | \$0.00 | ✓ Matched |
| LEX — Lexington | \$0.00 | \$0.00 | ✓ Matched |
| ROA — Roanoke | \$0.00 | \$0.00 | ✓ Matched |
| WAY — Waynesboro | \$0.00 | \$0.00 | ✓ Matched |
| **Total** | **\$2,000.00** | **\$2,000.00** | **5/5 matched** |

**Slack post: made (#daily-funds-reconcilation).**

_Report generated 2026-08-12 ~18:16 ET._
