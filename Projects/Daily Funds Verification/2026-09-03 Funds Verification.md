# Daily Funds Verification — 2026-09-03

**Status: COMPLETE — all 5 verified. ALL MATCHED.**

## Bottom line
$3,500.00 expected vs $3,500.00 actual across all 5 stores; every store matched. Lexington had an open cash request from Uriah (large buy + daily ops) that Joshua had not yet funded as of this pull — correctly $0/$0, not a discrepancy.

## Step 1 — Slack ledger (today, 2026-09-03 ET)
| Store | Channel | Request(s) | Joshua's reply | Net expected |
|---|---|---|---|---|
| CUL — Culpeper | #pepper-funds | Sandi sent images/screenshot requesting funds | "sent 2500, need sales, yesterday was a bummer, cash flow has to balance, more in than out!! Nice job on the new hire..." | $2,500.00 |
| HAR — Harrisonburg | #harrisonburg-funds | (no messages today) | — | $0.00 |
| LEX — Lexington | #lex-funds | Uriah: "I have the money for large buy, just need some for daily ops now"; later "Current till $63.06" | (no reply/send from Joshua today) | $0.00 |
| ROA — Roanoke | #roanoke-funds | (no messages today) | — | $0.00 |
| WAY — Waynesboro | #boro-funds | Chadd: "Ops cash, need 2k" | "setn 1k, choose deal wisely today" | $1,000.00 |

Cancellations: none. **Total expected: $3,500.00.**

## Step 2 — Bravo extraction
Trigger `daily-funds-verification-2026-09-03T18-05-21` -> watcher status `success` on 5/5 cells (CUL 87.3s/56 rows, HAR 83.9s/27 rows, LEX 86.8s/29 rows, ROA 107.8s/29 rows, WAY 95.3s/56 rows). Health gate PASS before drop, no retries needed, no watcher restart needed.

## Step 3 — Bravo signature rows (TENDER TRANSFER · BANK · Cash · negative leg)
| Store | Txn Num | Time | From->To | Amount |
|---|---|---|---|---|
| CUL | VP400065483 | 11:43 AM | BANK->SAFE | $2,500.00 |
| HAR | (no cash transfer) | — | — | $0.00 |
| LEX | (no cash transfer) | — | — | $0.00 |
| ROA | (no cash transfer) | — | — | $0.00 |
| WAY | VAP00075189 | 11:55 AM | BANK->SAFE | $1,000.00 |

## Step 5 — Reconciliation
| Store | Net expected (Slack) | Net actual (Bravo) | Status |
|---|---|---|---|
| CUL — Culpeper | $2,500.00 | $2,500.00 | Matched |
| HAR — Harrisonburg | $0.00 | $0.00 | Matched |
| LEX — Lexington | $0.00 | $0.00 | Matched |
| ROA — Roanoke | $0.00 | $0.00 | Matched |
| WAY — Waynesboro | $1,000.00 | $1,000.00 | Matched |
| **Total** | **$3,500.00** | **$3,500.00** | **5/5 matched** |

**Slack post: made** (https://valleypawnworkspace.slack.com/archives/C0B3R9B3S8H/p1788473732155219).

_Report generated 2026-09-03 ~18:15 ET._
