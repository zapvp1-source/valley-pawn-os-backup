# Daily Funds Verification — 2026-08-21

**Status: COMPLETE — all 5 verified. ALL MATCHED.**

## Bottom line
$4,000.00 expected vs $4,000.00 actual across all 5 stores; all matched. Only Waynesboro had cash movement today.

## Step 1 — Slack ledger (today, 2026-08-21 ET)
| Store | Channel | Request(s) | Joshua's reply | Net expected |
|---|---|---|---|---|
| CUL — Culpeper | #pepper-funds | none (photo request only) | n/a | $0.00 |
| HAR — Harrisonburg | #harrisonburg-funds | none | n/a | $0.00 |
| LEX — Lexington | #lex-funds | none (phone issue only) | n/a | $0.00 |
| ROA — Roanoke | #roanoke-funds | none (no activity today) | n/a | $0.00 |
| WAY — Waynesboro | #boro-funds | Ops cash need 2k (9:26a, implied); Ops cash need 2k (1:32p, reconfirmed 1:55p) | Sent 2k (9:15a); sent 2k (2:02p) | $4,000.00 |

Cancellations: none. **Total expected: $4,000.00.**

Note: a third Waynesboro request, "Ops cash, need 2k" at 4:30 PM, had no confirmed "sent" reply from Joshua within today's scan window — not counted as expected since unconfirmed; flagged to Joshua in the Slack post.

## Step 2 — Bravo extraction
Trigger `daily-funds-verification-2026-08-21T18-04-43` → watcher status `success` on 5/5 cells.

## Step 3 — Bravo signature rows (TENDER TRANSFER · BANK · Cash · negative leg)
| Store | Txn Num | Time | From→To | Amount |
|---|---|---|---|---|
| CUL | — | — | (no cash transfer) | $0.00 |
| HAR | — | — | (no cash transfer) | $0.00 |
| LEX | — | — | (no cash transfer) | $0.00 |
| ROA | — | — | (no cash transfer) | $0.00 |
| WAY | VAP00074660 | 10:17 AM | BANK→SAFE | $2,000.00 |
| WAY | VAP00074691 | 2:26 PM | BANK→SAFE | $2,000.00 |

## Step 5 — Reconciliation
| Store | Net expected (Slack) | Net actual (Bravo) | Status |
|---|---|---|---|
| CUL — Culpeper | $0.00 | $0.00 | ✓ Matched |
| HAR — Harrisonburg | $0.00 | $0.00 | ✓ Matched |
| LEX — Lexington | $0.00 | $0.00 | ✓ Matched |
| ROA — Roanoke | $0.00 | $0.00 | ✓ Matched |
| WAY — Waynesboro | $4,000.00 | $4,000.00 | ✓ Matched |
| **Total** | **$4,000.00** | **$4,000.00** | **5/5 matched** |

**Slack post: made (#daily-funds-reconcilation).**

_Report generated 2026-08-21 ~18:12 ET._
