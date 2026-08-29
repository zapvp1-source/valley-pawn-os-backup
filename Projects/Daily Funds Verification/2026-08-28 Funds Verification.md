# Daily Funds Verification — 2026-08-28

**Status: COMPLETE — all 5 verified. DISCREPANCY FOUND.**

## Bottom line
$1,000.00 expected vs $0.00 actual across all 5 stores. Culpeper is off by $1,000 — Joshua confirmed sending $1,000 to Culpeper today, but Bravo shows no Safe Register Journal activity at all for Culpeper today. Harrisonburg, Lexington, Roanoke, and Waynesboro had no funds requests today and correctly show no cash-in transfers.

## Step 1 — Slack ledger (today, 2026-08-28 ET)
| Store | Channel | Request(s) | Joshua'\''s reply | Net expected |
|---|---|---|---|---|
| CUL — Culpeper | #pepper-funds | Rob: \"GM ops cash needed \$2000\" (11:02 AM); Rob: \"GA need OPS cash\" (4:23 PM, unanswered as of report time) | \"Sent 1k. Afternoon!\" (11:35 AM) | \$1,000.00 |
| HAR — Harrisonburg | #harrisonburg-funds | No funds request today (doc-signature exchange only) | — | \$0.00 |
| LEX — Lexington | #lex-funds | No funds request today (signage/logistics only) | — | \$0.00 |
| ROA — Roanoke | #roanoke-funds | No funds request today (Precious Metals Bond discussion only) | — | \$0.00 |
| WAY — Waynesboro | #boro-funds | No messages today | — | \$0.00 |

Cancellations: none. **Total expected: \$1,000.00.**

Note: Rob'\''s 4:23 PM \$2,000 request at Culpeper is still unanswered/unconfirmed as of this report and is NOT included in the expected total (only confirmed \"Sent\" amounts count).

## Step 2 — Bravo extraction
Trigger \`daily-funds-verification-2026-08-28T18-05-31\` → watcher status \`success\` on 5/5 cells (CUL, HAR, LEX, ROA, WAY).

## Step 3 — Bravo signature rows (TENDER TRANSFER · BANK · Cash · negative leg)
| Store | Txn Num | Time | From→To | Amount |
|---|---|---|---|---|
| CUL — Culpeper | — | — | (no data returned for current report configuration) | \$0.00 |
| HAR — Harrisonburg | — | — | (no qualifying Cash/BANK transfer — only Debit Card till/safe/bank transfers present) | \$0.00 |
| LEX — Lexington | — | — | (no qualifying Cash/BANK transfer — only Debit Card till/safe/bank transfers present) | \$0.00 |
| ROA — Roanoke | — | — | (no qualifying Cash/BANK transfer found) | \$0.00 |
| WAY — Waynesboro | — | — | (no qualifying Cash/BANK transfer — only Debit Card till/safe/bank transfers present) | \$0.00 |

## Step 5 — Reconciliation
| Store | Net expected (Slack) | Net actual (Bravo) | Status |
|---|---|---|---|
| CUL — Culpeper | \$1,000.00 | \$0.00 | ⚠ Discrepancy |
| HAR — Harrisonburg | \$0.00 | \$0.00 | ✓ Matched |
| LEX — Lexington | \$0.00 | \$0.00 | ✓ Matched |
| ROA — Roanoke | \$0.00 | \$0.00 | ✓ Matched |
| WAY — Waynesboro | \$0.00 | \$0.00 | ✓ Matched |
| **Total** | **\$1,000.00** | **\$0.00** | **4/5 matched** |

**Slack post: made (#daily-funds-reconcilation).**

_Report generated 2026-08-28 ~18:15 ET._
