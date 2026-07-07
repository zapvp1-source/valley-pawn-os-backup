# Daily Funds Verification — 2026-06-09

**Status: COMPLETE — all 5 verified. Every dollar sent today is in the Bravo safes.**

## Bottom line
$13,000.00 expected vs $13,000.00 actual. All 5 stores matched, no discrepancies. Two of three sends landed in Harrisonburg ($1k + $10k), one in Culpeper ($2k); Lexington, Roanoke, and Waynesboro had no funds requests today.

## Step 1 — Slack ledger (today, 2026-06-09 ET)
| Store | Channel | Request(s) | Joshua's reply | Net expected |
|---|---|---|---|---|
| CUL — Culpeper | #pepper-funds | Sandi: Ops cash needed $2k (10:33) | "seent 2k" (11:10) | $2,000.00 |
| HAR — Harrisonburg | #harrisonburg-funds | Walker: ops cash need 2k (17:15); earlier ops cash (12:48) | "Sent 10k" (12:48) + "sent 1k" (17:39) | $11,000.00 |
| LEX — Lexington | #lex-funds | (none) | (none) | $0.00 |
| ROA — Roanoke | #roanoke-funds | (none) | (none) | $0.00 |
| WAY — Waynesboro | #boro-funds | (none) | (none) | $0.00 |

Cancellations: none. **Total expected: $13,000.00.**

## Step 2 — Bravo extraction
Trigger `daily-funds-verification-2026-06-09T18-04-20` → watcher status `success` on 5/5 cells (CUL 32 rows, HAR 35, LEX 29, ROA 29, WAY 27).

## Step 3 — Bravo signature rows (TENDER TRANSFER · BANK · Cash · negative leg)
| Store | Txn Num | Time | From→To | Amount |
|---|---|---|---|---|
| CUL — Culpeper | VP400061433 | 12:00 PM | BANK→SAFE | $2,000.00 |
| HAR — Harrisonburg | VA500051780 | 5:53 PM | BANK→SAFE | $1,000.00 |
| HAR — Harrisonburg | VA500051783 | 5:56 PM | BANK→SAFE | $10,000.00 |
| LEX — Lexington | — | — | (no cash transfer) | $0.00 |
| ROA — Roanoke | — | — | (no cash transfer) | $0.00 |
| WAY — Waynesboro | — | — | (no cash transfer) | $0.00 |

## Step 5 — Reconciliation
| Store | Net expected (Slack) | Net actual (Bravo) | Status |
|---|---|---|---|
| CUL — Culpeper | $2,000.00 | $2,000.00 | ✓ Matched |
| HAR — Harrisonburg | $11,000.00 | $11,000.00 | ✓ Matched |
| LEX — Lexington | $0.00 | $0.00 | ✓ Matched |
| ROA — Roanoke | $0.00 | $0.00 | ✓ Matched |
| WAY — Waynesboro | $0.00 | $0.00 | ✓ Matched |
| **Total** | **$13,000.00** | **$13,000.00** | **ALL MATCHED — 5/5** |

**Slack post: made.**

_Report generated 2026-06-09 ~18:13 ET._
