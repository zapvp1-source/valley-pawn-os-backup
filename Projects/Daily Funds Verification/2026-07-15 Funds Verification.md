# Daily Funds Verification — 2026-07-15

**Status: COMPLETE — all 5 verified. All matched.**

## Bottom line
$1,500.00 expected vs $1,500.00 actual across all 5 stores; every store matched exactly.

## Step 1 — Slack ledger (today, 2026-07-15 ET)
| Store | Channel | Request(s) | Joshua's reply | Net expected |
|---|---|---|---|---|
| CUL — Culpeper | #pepper-funds | Sandi: GM. Ops Cash Needed $1500 (9:38 AM) | Sent 1500. GM (10:00 AM) | $1,500.00 |
| HAR — Harrisonburg | #harrisonburg-funds | (no messages today) | — | $0.00 |
| LEX — Lexington | #lex-funds | (no messages today) | — | $0.00 |
| ROA — Roanoke | #roanoke-funds | (no messages today) | — | $0.00 |
| WAY — Waynesboro | #boro-funds | (no messages today) | — | $0.00 |

Cancellations: none. **Total expected: $1,500.00.**

## Step 2 — Bravo extraction
Trigger `daily-funds-verification-2026-07-15T18-05-16` → watcher status `success` on 5/5 cells.

## Step 3 — Bravo signature rows (TENDER TRANSFER · BANK · Cash · negative leg)
| Store | Txn Num | Time | From→To | Amount |
|---|---|---|---|---|
| Culpeper | VP400063113 | 10:40 AM | BANK→SAFE | $1,500.00 |
| Harrisonburg | — | — | (no cash transfer) | $0.00 |
| Lexington | — | — | (no cash transfer) | $0.00 |
| Roanoke | — | — | (no cash transfer) | $0.00 |
| Waynesboro | — | — | (no cash transfer) | $0.00 |

## Step 5 — Reconciliation
| Store | Net expected (Slack) | Net actual (Bravo) | Status |
|---|---|---|---|
| CUL — Culpeper | $1,500.00 | $1,500.00 | ✓ Matched |
| HAR — Harrisonburg | $0.00 | $0.00 | ✓ Matched |
| LEX — Lexington | $0.00 | $0.00 | ✓ Matched |
| ROA — Roanoke | $0.00 | $0.00 | ✓ Matched |
| WAY — Waynesboro | $0.00 | $0.00 | ✓ Matched |
| **Total** | **$1,500.00** | **$1,500.00** | **5/5 matched** |

**Slack post: made.**

_Report generated 2026-07-15 ~18:14 ET._
