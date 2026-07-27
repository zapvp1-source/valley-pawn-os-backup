# Daily Funds Verification — 2026-06-20

**Status: COMPLETE — all 5 verified. Every dollar sent today is in the Bravo safes.**

## Bottom line
$8,000.00 expected vs $8,000.00 actual. All 5 stores matched; no exceptions.

## Step 1 — Slack ledger (today, 2026-06-20 ET)
| Store | Channel | Request(s) | Joshua's reply | Net expected |
|---|---|---|---|---|
| CUL — Culpeper | #pepper-funds | Ops cash $2k, then need $4k / +$2k | "Sent 2k" then "Sent 4k total" | $4,000.00 |
| HAR — Harrisonburg | #harrisonburg-funds | (images only, no amount) | none | $0.00 |
| LEX — Lexington | #lex-funds | Ops cash 1k ATM withdrawal | "Sent 1k" | $1,000.00 |
| ROA — Roanoke | #roanoke-funds | Ops cash need 1k | "sent 1k" | $1,000.00 |
| WAY — Waynesboro | #boro-funds | Ops cash, need 2k | "sent 2k" | $2,000.00 |

Cancellations: none. **Total expected: $8,000.00.**

## Step 2 — Bravo extraction
Trigger `daily-funds-verification-2026-06-20T18-05-05` → watcher status `success` on 5/5 cells. Health gate PASS before drop.

## Step 3 — Bravo signature rows (TENDER TRANSFER · BANK · Cash · negative leg)
| Store | Txn Num | Time | From→To | Amount |
|---|---|---|---|---|
| CUL — Culpeper | VP400061956 | 12:14 PM | BANK→SAFE | $4,000.00 |
| HAR — Harrisonburg | (none) | — | (no cash transfer) | $0.00 |
| LEX — Lexington | VA100108632 | 4:08 PM | BANK→SAFE | $1,000.00 |
| ROA — Roanoke | ROA00029882 | 3:17 PM | BANK→SAFE | $1,000.00 |
| WAY — Waynesboro | VAP00071976 | 10:46 AM | BANK→SAFE | $2,000.00 |

## Step 5 — Reconciliation
| Store | Net expected (Slack) | Net actual (Bravo) | Status |
|---|---|---|---|
| CUL — Culpeper | $4,000.00 | $4,000.00 | ✓ Matched |
| HAR — Harrisonburg | $0.00 | $0.00 | ✓ Matched |
| LEX — Lexington | $1,000.00 | $1,000.00 | ✓ Matched |
| ROA — Roanoke | $1,000.00 | $1,000.00 | ✓ Matched |
| WAY — Waynesboro | $2,000.00 | $2,000.00 | ✓ Matched |
| **Total** | **$8,000.00** | **$8,000.00** | **ALL MATCHED (5/5)** |

**Slack post: made.**

Note: Culpeper was a topped-up send (Joshua sent 2k, then "Sent 4k total"); Bravo recorded one $4,000 BANK→SAFE transfer at 12:14 PM — counted once. Roanoke's 6 PM card transfers (Debit/Visa) are non-Cash and excluded.

_Report generated 2026-06-20 ~18:12 ET._

