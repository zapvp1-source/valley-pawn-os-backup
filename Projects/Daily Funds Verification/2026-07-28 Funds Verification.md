# Daily Funds Verification — 2026-07-28

**Status: COMPLETE — all 5 verified. ALL MATCHED.**

## Bottom line
$2,750.00 expected vs $2,750.00 actual across all 5 stores — every store matched exactly.

## Step 1 — Slack ledger (today, 2026-07-28 ET)
| Store | Channel | Request(s) | Joshua's reply | Net expected |
|---|---|---|---|---|
| CUL — Culpeper | #pepper-funds | (none today) | — | $0.00 |
| HAR — Harrisonburg | #harrisonburg-funds | Walker 12:11pm "Ops cash need 2k"; Walker 3:20pm "Ops cash need 2k" (2nd, unconfirmed) | Joshua 12:40pm "sent 750" | $750.00 |
| LEX — Lexington | #lex-funds | (none today) | — | $0.00 |
| ROA — Roanoke | #roanoke-funds | (none today) | — | $0.00 |
| WAY — Waynesboro | #boro-funds | Chadd 9:14am "Ops cash, need 2k"; Chadd 4:06pm "Ops cash, need 2k" (2nd, unconfirmed) | Joshua 9:15am "Sent 2k" | $2,000.00 |

Cancellations: none. HAR's 3:20pm request and WAY's 4:06pm request had no confirmed "Sent" reply in today's window, so they were NOT counted toward net expected. **Total expected: $2,750.00.**

## Step 2 — Bravo extraction
Trigger `daily-funds-verification-2026-07-28T18-05-20` → watcher status `partial` on first pass (4/5 cells success, ROA errored "EnsureStore failed for ROA"). Retry trigger `daily-funds-verification-2026-07-28T18-05-20-retry-1` (ROA only) → `success`. Final: 5/5 cells clean.

## Step 3 — Bravo signature rows (TENDER TRANSFER · BANK · Cash · negative leg)
| Store | Txn Num | Time | From→To | Amount |
|---|---|---|---|---|
| CUL — Culpeper | (no cash transfer) | — | — | $0.00 |
| HAR — Harrisonburg | VA500053530 | 1:04 PM | BANK→SAFE | $750.00 |
| LEX — Lexington | (no cash transfer) | — | — | $0.00 |
| ROA — Roanoke | (no cash transfer) | — | — | $0.00 |
| WAY — Waynesboro | VAP00073578 | 10:55 AM | BANK→SAFE | $2,000.00 |

## Step 5 — Reconciliation
| Store | Net expected (Slack) | Net actual (Bravo) | Status |
|---|---|---|---|
| CUL — Culpeper | $0.00 | $0.00 | ✓ Matched |
| HAR — Harrisonburg | $750.00 | $750.00 | ✓ Matched |
| LEX — Lexington | $0.00 | $0.00 | ✓ Matched |
| ROA — Roanoke | $0.00 | $0.00 | ✓ Matched |
| WAY — Waynesboro | $2,000.00 | $2,000.00 | ✓ Matched |
| **Total** | **$2,750.00** | **$2,750.00** | **5/5 matched** |

**Slack post: made** (#daily-funds-reconcilation).

_Report generated 2026-07-28 ~18:17 ET._
