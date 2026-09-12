# Daily Funds Verification — 2026-09-11

**Status: COMPLETE — all 5 verified. ALL MATCHED.**

## Bottom line
$6,000.00 expected vs $6,000.00 actual across all 5 stores. Every dollar Joshua sent today landed in the correct store's Bravo safe the same day.

## Step 1 — Slack ledger (today, 2026-09-11 ET)
| Store | Channel | Request(s) | Joshua's reply | Net expected |
|---|---|---|---|---|
| CUL — Culpeper | #pepper-funds | Sandi 9:40 AM "Cash ops needed \$2k" | "I'm sent 2k" 10:43 AM | \$2,000.00 |
| HAR — Harrisonburg | #harrisonburg-funds | Walker 10:01 AM "ops cash need 2k" | "Sent 2k" 10:43 AM | \$2,000.00 |
| LEX — Lexington | #lex-funds | (no requests today) | — | \$0.00 |
| ROA — Roanoke | #roanoke-funds | (photos only, no cash request) | — | \$0.00 |
| WAY — Waynesboro | #boro-funds | Martin D. 11:10 AM "Ops cash, need 2k" | "Sent 2k" 11:13 AM | \$2,000.00 |

Cancellations: none. Open item: Preston requested a SECOND \$2k for Waynesboro at 4:20 PM (re-tagged Joshua 4:38 PM) — as of this report, no "Sent" confirmation exists in Slack, so it is NOT included in net expected and correctly does not appear in Bravo. **Total expected: \$6,000.00.**

## Step 2 — Bravo extraction
Trigger \`daily-funds-verification-2026-09-11T18-05-56\` → watcher status \`success\` on 5/5 cells (CUL, HAR, LEX, ROA, WAY), no retries needed.

## Step 3 — Bravo signature rows (TENDER TRANSFER · BANK · Cash · negative leg)
| Store | Txn Num | Time | From→To | Amount |
|---|---|---|---|---|
| CUL — Culpeper | VP400065899 | 11:56 AM | BANK→SAFE | \$2,000.00 |
| HAR — Harrisonburg | VA500055266 | 10:58 AM | BANK→SAFE | \$2,000.00 |
| LEX — Lexington | (no cash transfer) | — | — | \$0.00 |
| ROA — Roanoke | (no cash transfer) | — | — | \$0.00 |
| WAY — Waynesboro | VAP00075570 | 11:32 AM | BANK→SAFE | \$2,000.00 |

## Step 5 — Reconciliation
| Store | Net expected (Slack) | Net actual (Bravo) | Status |
|---|---|---|---|
| CUL — Culpeper | \$2,000.00 | \$2,000.00 | ✓ Matched |
| HAR — Harrisonburg | \$2,000.00 | \$2,000.00 | ✓ Matched |
| LEX — Lexington | \$0.00 | \$0.00 | ✓ Matched |
| ROA — Roanoke | \$0.00 | \$0.00 | ✓ Matched |
| WAY — Waynesboro | \$2,000.00 | \$2,000.00 | ✓ Matched |
| **Total** | **\$6,000.00** | **\$6,000.00** | **5/5 matched** |

**Slack post: made (#daily-funds-reconcilation).**

_Report generated 2026-09-11 ~18:14 ET._
