# Daily Funds Verification — 2026-07-14

**Status: COMPLETE — all 5 verified. All matched.**

## Bottom line
$8,000.00 expected vs $8,000.00 actual across all 5 stores. All 5 matched (Waynesboro had no ops-cash request today, so $0 expected = $0 actual).

## Step 1 — Slack ledger (today, 2026-07-14 ET)
| Store | Channel | Request(s) | Joshua's reply | Net expected |
|---|---|---|---|---|
| CUL — Culpeper | #pepper-funds | Sandi: Ops cash needed $2k (09:35) | sent 2k (10:24) | $2,000.00 |
| HAR — Harrisonburg | #harrisonburg-funds | Walker: Ops cash need $2k (16:24) | Sent 2k (16:25) | $2,000.00 |
| LEX — Lexington | #lex-funds | Uriah: Ops cash need 2k (10:34) | sent 2k (10:39) | $2,000.00 |
| ROA — Roanoke | #roanoke-funds | Benjie: Ops cash need 2k (10:15); re-confirmed in-thread (not showing → try now → its there now) | sent 2k (10:24) | $2,000.00 |
| WAY — Waynesboro | #boro-funds | none today | none | $0.00 |

Cancellations: none. **Total expected: $8,000.00.**

## Step 2 — Bravo extraction
Trigger `daily-funds-verification-2026-07-14T18-05-14` → watcher status partial on first pass (2/5 success: LEX, ROA; CUL/HAR/WAY errored — CUL: UIA click sequence failed; HAR/WAY: EnsureStore failed). Retry trigger `daily-funds-verification-retry1-2026-07-14T18-11-56` for CUL, HAR, WAY → status success, 3/3 on retry. Final: 5/5 cells clean, no watcher restart needed.

## Step 3 — Bravo signature rows (TENDER TRANSFER · BANK · Cash · negative leg)
| Store | Txn Num | Time | From→To | Amount |
|---|---|---|---|---|
| CUL | VP400063060 | 10:46 AM | BANK→SAFE | $2,000.00 |
| HAR | VA500053089 | 4:54 PM | BANK→SAFE | $2,000.00 |
| LEX | VA100109196 | 10:58 AM | BANK→SAFE | $2,000.00 |
| ROA | ROA00030794 | 11:43 AM | BANK→SAFE | $2,000.00 |
| WAY | (no cash transfer) | — | — | $0.00 |

## Step 5 — Reconciliation
| Store | Net expected (Slack) | Net actual (Bravo) | Status |
|---|---|---|---|
| CUL — Culpeper | $2,000.00 | $2,000.00 | ✓ Matched |
| HAR — Harrisonburg | $2,000.00 | $2,000.00 | ✓ Matched |
| LEX — Lexington | $2,000.00 | $2,000.00 | ✓ Matched |
| ROA — Roanoke | $2,000.00 | $2,000.00 | ✓ Matched |
| WAY — Waynesboro | $0.00 | $0.00 | ✓ Matched |
| **Total** | **$8,000.00** | **$8,000.00** | **5/5 matched** |

**Slack post: made (#daily-funds-reconcilation).**

_Report generated 2026-07-14 ~18:20 ET._
