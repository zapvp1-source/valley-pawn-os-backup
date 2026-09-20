# Daily Funds Verification — 2026-09-19

**Status: COMPLETE — all 5 verified. All matched.**

## Bottom line
$4,000.00 expected vs $4,000.00 actual across all 5 stores; every store matched.

## Step 1 — Slack ledger (today, 2026-09-19 ET)
| Store | Channel | Request(s) | Joshua's reply | Net expected |
|---|---|---|---|---|
| CUL — Culpeper | #pepper-funds | Sandi: "Good morning. Cash Ops Needed $2k" (9:35 AM) | "Sent 2k. GM" (10:57 AM) | $2,000.00 |
| HAR — Harrisonburg | #harrisonburg-funds | (none today) | (none today) | $0.00 |
| LEX — Lexington | #lex-funds | (none today) | (none today) | $0.00 |
| ROA — Roanoke | #roanoke-funds | Benjie Moore: "Ops cash need 2k" (11:25 AM) | "sent 2k" (11:30 AM) | $2,000.00 |
| WAY — Waynesboro | #boro-funds | (none today) | (none today) | $0.00 |

Cancellations: none. **Total expected: $4,000.00.**

## Step 2 — Bravo extraction
Trigger `daily-funds-verification-20260919-1804` → watcher status `success` on 5/5 cells.

## Step 3 — Bravo signature rows (TENDER TRANSFER · BANK · Cash · negative leg)
| Store | Txn Num | Time | From→To | Amount |
|---|---|---|---|---|
| CUL | VP400066293 | 11:27 AM | Bank→Safe (Sandi) | $2,000.00 |
| HAR | — | — | (no cash transfer) | $0.00 |
| LEX | — | — | (no cash transfer) | $0.00 |
| ROA | ROA00033185 | 12:39 PM | Bank→Safe (Benjie) | $2,000.00 |
| WAY | — | — | (no cash transfer) | $0.00 |

## Step 5 — Reconciliation
| Store | Net expected (Slack) | Net actual (Bravo) | Status |
|---|---|---|---|
| CUL — Culpeper | $2,000.00 | $2,000.00 | ✓ Matched |
| HAR — Harrisonburg | $0.00 | $0.00 | ✓ Matched |
| LEX — Lexington | $0.00 | $0.00 | ✓ Matched |
| ROA — Roanoke | $2,000.00 | $2,000.00 | ✓ Matched |
| WAY — Waynesboro | $0.00 | $0.00 | ✓ Matched |
| **Total** | **$4,000.00** | **$4,000.00** | **5/5 matched** |

**Slack post: made** (#daily-funds-reconcilation).

_Report generated 2026-09-19 ~18:16 ET._
