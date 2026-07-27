# Daily Funds Verification — 2026-07-08

**Status: COMPLETE — all 5 verified. All matched.**

## Bottom line
$1,500.00 expected vs $1,500.00 actual across all 5 stores; every store matched with no discrepancies.

## Step 1 — Slack ledger (today, 2026-07-08 ET)
| Store | Channel | Request(s) | Joshua's reply | Net expected |
|---|---|---|---|---|
| CUL — Culpeper | #pepper-funds | Sandi Cole: "Ops cash needed $1500" (9:50 AM), tagged Joshua (9:57 AM) | "Sent 1500" (10:12 AM) | $1,500.00 |
| HAR — Harrisonburg | #harrisonburg-funds | (none today) | (none) | $0.00 |
| LEX — Lexington | #lex-funds | (none today) | (none) | $0.00 |
| ROA — Roanoke | #roanoke-funds | (none today) | (none) | $0.00 |
| WAY — Waynesboro | #boro-funds | (none today) | (none) | $0.00 |

Cancellations: none. **Total expected: $1,500.00.**

## Step 2 — Bravo extraction
Trigger `daily-funds-verification-2026-07-08T18-04-18` → watcher status `success` on 5/5 cells.

## Step 3 — Bravo signature rows (TENDER TRANSFER · BANK · Cash · negative leg)
| Store | Txn Num | Time | From→To | Amount |
|---|---|---|---|---|
| CUL — Culpeper | VP400062826 | 1:09 PM | BANK→SAFE | $1,500.00 |
| HAR — Harrisonburg | — | — | (no cash transfer) | $0.00 |
| LEX — Lexington | — | — | (no cash transfer) | $0.00 |
| ROA — Roanoke | — | — | (no cash transfer) | $0.00 |
| WAY — Waynesboro | — | — | (no cash transfer) | $0.00 |

## Step 5 — Reconciliation
| Store | Net expected (Slack) | Net actual (Bravo) | Status |
|---|---|---|---|
| CUL — Culpeper | $1,500.00 | $1,500.00 | ✓ Matched |
| HAR — Harrisonburg | $0.00 | $0.00 | ✓ Matched |
| LEX — Lexington | $0.00 | $0.00 | ✓ Matched |
| ROA — Roanoke | $0.00 | $0.00 | ✓ Matched |
| WAY — Waynesboro | $0.00 | $0.00 | ✓ Matched |
| **Total** | **$1,500.00** | **$1,500.00** | **5/5 matched** |

**Slack post: made — #daily-funds-reconcilation.**

_Report generated 2026-07-08 ~18:11 ET._
