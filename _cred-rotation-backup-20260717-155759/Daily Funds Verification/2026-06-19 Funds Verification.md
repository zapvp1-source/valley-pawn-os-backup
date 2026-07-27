# Daily Funds Verification — 2026-06-19

**Status: COMPLETE — all 5 verified. Discrepancy found at Culpeper (+$200 in Bravo vs Slack).**

## Bottom line
$4,000.00 expected vs $4,200.00 actual. 4 of 5 stores matched. Culpeper's safe shows a third cash BANK→safe transfer of $200.00 (VP400061879, 9:49 AM) with no matching "Sent" message in #pepper-funds — likely a store-initiated bank-to-safe move or a send not logged in Slack.

## Step 1 — Slack ledger (today, 2026-06-19 ET)
| Store | Channel | Request(s) | Joshua's reply | Net expected |
|---|---|---|---|---|
| CUL — Culpeper | #pepper-funds | "Ops cash needed $1k" (10:03), "Ops cash needed $1k" (14:29) | "Sent 1k GM" (10:03), "Sent 1k" (14:32) | $2,000.00 |
| HAR — Harrisonburg | #harrisonburg-funds | (none) | (none) | $0.00 |
| LEX — Lexington | #lex-funds | "OPS cash 1k ATM withdrawal" (10:13) | "Sent 1k. GM" (10:18) | $1,000.00 |
| ROA — Roanoke | #roanoke-funds | "Ops cash neek 1k" (10:04) | "sent 1k" (11:38) | $1,000.00 |
| WAY — Waynesboro | #boro-funds | (none) | (none) | $0.00 |

Cancellations: none. **Total expected: $4,000.00.**

## Step 2 — Bravo extraction
Trigger `daily-funds-verification-2026-06-19T18-10-12` → watcher status `success` on 5/5 cells.

## Step 3 — Bravo signature rows (TENDER TRANSFER · BANK · Cash · negative leg)
| Store | Txn Num | Time | From→To | Amount |
|---|---|---|---|---|
| CUL | VP400061879 | 9:49 AM | BANK→SAFE | $200.00 |
| CUL | VP400061892 | 12:40 PM | BANK→SAFE | $1,000.00 |
| CUL | VP400061912 | 3:50 PM | BANK→SAFE | $1,000.00 |
| HAR | — | — | (no cash transfer; one Debit Card BANK deposit $1,544.70 ignored) | $0.00 |
| LEX | VA100108582 | 10:30 AM | BANK→SAFE | $1,000.00 |
| ROA | ROA00029827 | 3:42 PM | BANK→SAFE | $1,000.00 |
| WAY | — | — | (no cash transfer) | $0.00 |

## Step 5 — Reconciliation
| Store | Net expected (Slack) | Net actual (Bravo) | Status |
|---|---|---|---|
| CUL — Culpeper | $2,000.00 | $2,200.00 | ⚠ Discrepancy |
| HAR — Harrisonburg | $0.00 | $0.00 | ✓ Matched |
| LEX — Lexington | $1,000.00 | $1,000.00 | ✓ Matched |
| ROA — Roanoke | $1,000.00 | $1,000.00 | ✓ Matched |
| WAY — Waynesboro | $0.00 | $0.00 | ✓ Matched |
| **Total** | **$4,000.00** | **$4,200.00** | **DISCREPANCY FOUND — 4/5 matched** |

**Slack post: made.**

_Report generated 2026-06-19 ~18:18 ET._
