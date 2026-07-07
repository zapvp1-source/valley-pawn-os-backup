# Daily Funds Verification — 2026-07-07

**Status: COMPLETE — all 5 verified. All matched.**

## Bottom line
$8,000.00 expected vs $8,000.00 actual across all 5 stores; every store matched.

## Step 1 — Slack ledger (today, 2026-07-07 ET)
| Store | Channel | Request(s) | Joshua's reply | Net expected |
|---|---|---|---|---|
| CUL — Culpeper | #pepper-funds | Ops Cash Needed $2k (12:22pm); gold loan cash check (5:16pm) | Sent 1k (9:21am), Sent 2k (12:23pm), sent 1k (5:19pm) | $4,000.00 |
| HAR — Harrisonburg | #harrisonburg-funds | (none logged) | Sent 1k (9:21am) | $1,000.00 |
| LEX — Lexington | #lex-funds | (none logged) | Sent 1k (9:21am) | $1,000.00 |
| ROA — Roanoke | #roanoke-funds | (no activity today) | (none) | $0.00 |
| WAY — Waynesboro | #boro-funds | Ops cash, Need 2k (12:28pm, re-confirmed 1:50pm - same request) | sent 2k (3:29pm, didnt know if this was old request) | $2,000.00 |

Cancellations: none. **Total expected: $8,000.00.**

## Step 2 — Bravo extraction
Trigger daily-funds-verification-2026-07-07T18-04-06 -> watcher status success on 5/5 cells.

## Step 3 — Bravo signature rows (TENDER TRANSFER x BANK x Cash x negative leg)
| Store | Txn Num | Time | From->To | Amount |
|---|---|---|---|---|
| CUL | VP400062785 | 12:22 PM | BANK->SAFE | $1,000.00 |
| CUL | VP400062787 | 12:42 PM | BANK->SAFE | $2,000.00 |
| CUL | VP400062803 | 5:40 PM | BANK->SAFE | $1,000.00 |
| HAR | VA500052821 | 9:59 AM | BANK->SAFE | $1,000.00 |
| LEX | VA100109037 | 9:57 AM | BANK->SAFE | $1,000.00 |
| ROA | (no cash transfer) | - | - | $0.00 |
| WAY | VAP00072717 | 3:50 PM | BANK->SAFE | $2,000.00 |

## Step 5 — Reconciliation
| Store | Net expected (Slack) | Net actual (Bravo) | Status |
|---|---|---|---|
| CUL — Culpeper | $4,000.00 | $4,000.00 | Matched |
| HAR — Harrisonburg | $1,000.00 | $1,000.00 | Matched |
| LEX — Lexington | $1,000.00 | $1,000.00 | Matched |
| ROA — Roanoke | $0.00 | $0.00 | Matched |
| WAY — Waynesboro | $2,000.00 | $2,000.00 | Matched |
| Total | $8,000.00 | $8,000.00 | 5/5 matched |

**Slack post: made.**

Report generated 2026-07-07 ~18:14 ET.
