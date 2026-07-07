# Daily Funds Verification — 2026-06-23

**Status: COMPLETE — all 5 verified. Every dollar sent today is in the Bravo safes.**

## Bottom line
$2,000.00 expected vs $2,000.00 actual. All 5 stores matched. Only Waynesboro had a transfer today (Martin's $2,000 ops cash request).

## Step 1 — Slack ledger (today, 2026-06-23 ET)
| Store | Channel | Request(s) | Joshua's reply | Net expected |
|---|---|---|---|---|
| CUL — Culpeper | #pepper-funds | (none) | (none) | $0.00 |
| HAR — Harrisonburg | #harrisonburg-funds | (none) | (none) | $0.00 |
| LEX — Lexington | #lex-funds | (none) | (none) | $0.00 |
| ROA — Roanoke | #roanoke-funds | (none) | (none) | $0.00 |
| WAY — Waynesboro | #boro-funds | Martin: Ops cash, need 2k (09:37) | sent 2k (09:48) | $2,000.00 |

Cancellations: none. **Total expected: $2,000.00.**

## Step 2 — Bravo extraction
Trigger `daily-funds-verification-2026-06-23T18-05-14` → watcher status `success` on 5/5 cells (CUL 28 rows, HAR 47, LEX 29, ROA 29, WAY 44).

## Step 3 — Bravo signature rows (TENDER TRANSFER · BANK · Cash · negative leg)
| Store | Txn Num | Time | From→To | Amount |
|---|---|---|---|---|
| CUL — Culpeper | — | — | — | $0.00 (no cash transfer) |
| HAR — Harrisonburg | — | — | — | $0.00 (only Debit Card transfers) |
| LEX — Lexington | — | — | — | $0.00 (no cash transfer) |
| ROA — Roanoke | — | — | — | $0.00 (no cash transfer) |
| WAY — Waynesboro | VAP00072099 | 6/23/2026 10:55 AM | BANK→SAFE | $2,000.00 |

## Step 5 — Reconciliation
| Store | Net expected (Slack) | Net actual (Bravo) | Status |
|---|---|---|---|
| CUL — Culpeper | $0.00 | $0.00 | ✓ Matched |
| HAR — Harrisonburg | $0.00 | $0.00 | ✓ Matched |
| LEX — Lexington | $0.00 | $0.00 | ✓ Matched |
| ROA — Roanoke | $0.00 | $0.00 | ✓ Matched |
| WAY — Waynesboro | $2,000.00 | $2,000.00 | ✓ Matched |
| **Total** | **$2,000.00** | **$2,000.00** | **ALL MATCHED — 5/5** |

**Slack post: made.**

_Report generated 2026-06-23 ~18:12 ET._

