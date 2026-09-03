# Daily Funds Verification — 2026-09-01

**Status: COMPLETE — all 5 verified. All matched.**

## Bottom line
$4,000.00 expected vs $4,000.00 actual across all 5 stores. Every dollar Joshua sent today made it into the Bravo safe the same day.

## Step 1 — Slack ledger (today, 2026-09-01 ET)
| Store | Channel | Request(s) | Joshua's reply | Net expected |
|---|---|---|---|---|
| CUL — Culpeper | #pepper-funds | (no messages today) | (none) | $0.00 |
| HAR — Harrisonburg | #harrisonburg-funds | Photos posted (unrelated to funds) | (none) | $0.00 |
| LEX — Lexington | #lex-funds | Uriah: "Need cash daily ops 2k" (14:38) | "One sec" (16:37), "Sent 1k" (16:45) | $1,000.00 |
| ROA — Roanoke | #roanoke-funds | Bond application document shared (unrelated to funds) | (none) | $0.00 |
| WAY — Waynesboro | #boro-funds | Chadd: "Ops cash, need 2k" GM (09:20); Chadd: "Ops cash, need 2k" (16:15) | "setn 2k" (11:19), "One sec"/"Sent 1k" (16:37/16:45) | $3,000.00 |

Cancellations: none. **Total expected: $4,000.00.**

## Step 2 — Bravo extraction
Trigger \`daily-funds-verification-2026-09-01T18-04-58\` -> watcher status success on 5/5 cells.

## Step 3 — Bravo signature rows (TENDER TRANSFER . BANK . Cash . negative leg)
| Store | Txn Num | Time | From->To | Amount |
|---|---|---|---|---|
| CUL | (no cash transfer) | - | - | $0.00 |
| HAR | (no cash transfer) | - | - | $0.00 |
| LEX | VA100110370 | 5:10 PM | UTIGLAO | $1,000.00 |
| ROA | (no cash transfer) | - | - | $0.00 |
| WAY | VAP00075136 | 11:50 AM | MDOWDEN@CUL | $2,000.00 |
| WAY | VAP00075161 | 5:03 PM | CHADD | $1,000.00 |

## Step 5 — Reconciliation
| Store | Net expected (Slack) | Net actual (Bravo) | Status |
|---|---|---|---|
| CUL — Culpeper | $0.00 | $0.00 | Matched |
| HAR — Harrisonburg | $0.00 | $0.00 | Matched |
| LEX — Lexington | $1,000.00 | $1,000.00 | Matched |
| ROA — Roanoke | $0.00 | $0.00 | Matched |
| WAY — Waynesboro | $3,000.00 | $3,000.00 | Matched |
| **Total** | **$4,000.00** | **$4,000.00** | **5/5 matched** |

**Slack post: made (#daily-funds-reconcilation).**

_Report generated 2026-09-01 ~18:14 ET._
