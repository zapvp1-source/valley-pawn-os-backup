# Daily Funds Verification — 2026-06-24

**Status: COMPLETE — all 5 verified. Discrepancy found at Culpeper ($1,000 not yet in safe).**

## Bottom line
$3,000.00 expected vs $2,000.00 actual across all 5 stores. Four stores matched ($0 / $0). Culpeper's morning $2,000 is in the safe; the afternoon $1,000 (sent ~5:32 PM) has not yet been recorded in the Bravo safe register — store reported the funds "not showing available," a likely same-day timing lag.

## Step 1 — Slack ledger (today, 2026-06-24 ET)
| Store | Channel | Request(s) | Joshua's reply | Net expected |
|---|---|---|---|---|
| CUL — Culpeper | #pepper-funds | 09:39 "Ops cash needed $2k"; 17:30 "Ops cash needed $1k" (17:39 store: "Says no funds" — $1k not showing) | 10:52 "Sent 2k"; 17:32 "sent 1k" | $3,000.00 |
| HAR — Harrisonburg | #harrisonburg-funds | (none) | (none) | $0.00 |
| LEX — Lexington | #lex-funds | (none) | (none) | $0.00 |
| ROA — Roanoke | #roanoke-funds | (none) | (none) | $0.00 |
| WAY — Waynesboro | #boro-funds | (none) | (none) | $0.00 |

Cancellations: none. **Total expected: $3,000.00.**

## Step 2 — Bravo extraction
Trigger `daily-funds-verification-2026-06-24T18-11-38` → watcher status `success` on 5/5 cells. (Bravo health guard ran first and returned PASS before the trigger was dropped — Bravo had required a Rung3/Rung4b relaunch-to-dashboard recovery.)

## Step 3 — Bravo signature rows (TENDER TRANSFER · BANK · Cash · negative leg)
| Store | Txn Num | Time | From→To | Amount |
|---|---|---|---|---|
| CUL — Culpeper | VP400062116 | 12:28 PM | BANK→SAFE | $2,000.00 |
| HAR — Harrisonburg | — | — | (no cash transfer) | $0.00 |
| LEX — Lexington | — | — | (no cash transfer) | $0.00 |
| ROA — Roanoke | — | — | (no cash transfer) | $0.00 |
| WAY — Waynesboro | — | — | (no cash transfer) | $0.00 |

Note (CUL): non-qualifying transfers excluded — VP400062104 SAFE→TL-01 ($10) and VP400062117 SAFE→TL-01 ($2,000) are internal safe/till moves, not BANK funds-ins.

## Step 5 — Reconciliation
| Store | Net expected (Slack) | Net actual (Bravo) | Status |
|---|---|---|---|
| CUL — Culpeper | $3,000.00 | $2,000.00 | ⚠ Discrepancy |
| HAR — Harrisonburg | $0.00 | $0.00 | ✓ Matched |
| LEX — Lexington | $0.00 | $0.00 | ✓ Matched |
| ROA — Roanoke | $0.00 | $0.00 | ✓ Matched |
| WAY — Waynesboro | $0.00 | $0.00 | ✓ Matched |
| **Total** | **$3,000.00** | **$2,000.00** | **4/5 matched — DISCREPANCY FOUND** |

**Slack post: made** (to #daily-funds-reconcilation, C0B3R9B3S8H).

_Report generated 2026-06-24 ~18:20 ET._
