# Daily Funds Verification — 2026-08-13

**Status: COMPLETE — all 5 verified. All stores matched.**

## Bottom line
$4,000.00 expected vs $4,000.00 actual across all 5 stores; all matched, no discrepancies.

## Step 1 — Slack ledger (today, 2026-08-13 ET)
| Store | Channel | Request(s) | Joshua's reply | Net expected |
|---|---|---|---|---|
| CUL — Culpeper | #pepper-funds | (no request today) | — | $0.00 |
| HAR — Harrisonburg | #harrisonburg-funds | (no funds request — modem/shipping thread only) | — | $0.00 |
| LEX — Lexington | #lex-funds | Uriah: "Ops cash need 2k" (10:41 AM) | "sent 2k" (11:27 AM) | $2,000.00 |
| ROA — Roanoke | #roanoke-funds | Benjie: "Ops cash need 2k" (1:12 PM); "Not showing money in the account" (2:06 PM) | "sent 2k" (1:36 PM); "Resent" (2:08 PM) → Benjie "Got it" (2:11 PM) | $2,000.00 |
| WAY — Waynesboro | #boro-funds | (no funds request — modem/shipping thread only) | — | $0.00 |

Cancellations: none. **Total expected: $4,000.00.**

## Step 2 — Bravo extraction
Trigger `daily-funds-verification-2026-08-13T18-04-00` → watcher status `success` on 5/5 cells.

## Step 3 — Bravo signature rows (TENDER TRANSFER · BANK · Cash · negative leg)
| Store | Txn Num | Time | From→To | Amount |
|---|---|---|---|---|
| CUL | — | — | (no cash transfer) | $0.00 |
| HAR | — | — | (no cash transfer) | $0.00 |
| LEX | VA100109895 | 12:02 PM | BANK→SAFE | $2,000.00 |
| ROA | ROA00031854 | 2:29 PM | BANK→SAFE | $2,000.00 |
| WAY | — | — | (no cash transfer) | $0.00 |

## Step 5 — Reconciliation
| Store | Net expected (Slack) | Net actual (Bravo) | Status |
|---|---|---|---|
| CUL — Culpeper | $0.00 | $0.00 | ✓ Matched |
| HAR — Harrisonburg | $0.00 | $0.00 | ✓ Matched |
| LEX — Lexington | $2,000.00 | $2,000.00 | ✓ Matched |
| ROA — Roanoke | $2,000.00 | $2,000.00 | ✓ Matched |
| WAY — Waynesboro | $0.00 | $0.00 | ✓ Matched |
| **Total** | **$4,000.00** | **$4,000.00** | **5/5 matched** |

**Slack post: made.**

_Report generated 2026-08-13 ~18:13 ET._
