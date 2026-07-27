# Daily Funds Verification — 2026-07-09

**Status: COMPLETE — all 5 verified. All matched.**

## Bottom line
\$6,000.00 expected vs \$6,000.00 actual; all 5 stores matched exactly.

## Step 1 — Slack ledger (today, 2026-07-09 ET)
| Store | Channel | Request(s) | Joshua'"'"'s reply | Net expected |
|---|---|---|---|---|
| CUL — Culpeper | #pepper-funds | Sandi: Ops Cash Needed \$2k (11:42) | Sent 1k (11:43) | \$1,000.00 |
| HAR — Harrisonburg | #harrisonburg-funds | Walker: Ops cash need 1k (14:30) | cancel (15:00) | \$0.00 |
| LEX — Lexington | #lex-funds | Uriah: Ops cash need 2k (10:17) | sent 1k (11:35) | \$1,000.00 |
| ROA — Roanoke | #roanoke-funds | Benjie: Ops cash need 2k (09:46) | sent 1k (11:35) | \$1,000.00 |
| WAY — Waynesboro | #boro-funds | Chadd: need 2k (10:52); need 2k again (15:29) | sent 1k (11:35); Sent 2k (15:51) | \$3,000.00 |

Cancellations: Harrisonburg'"'"'s \$1k request was cancelled in-thread before any send. **Total expected: \$6,000.00.**

## Step 2 — Bravo extraction
Trigger \`daily-funds-verification-2026-07-09T18-05-04\` → watcher status \`success\` on 5/5 cells (health gate PASS, no retries needed).

## Step 3 — Bravo signature rows (TENDER TRANSFER · BANK · Cash · negative leg)
| Store | Txn Num | Time | From→To | Amount |
|---|---|---|---|---|
| CUL | VP400062879 | 12:11 PM | BANK→SAFE | \$1,000.00 |
| HAR | (no cash transfer) | — | — | \$0.00 |
| LEX | VA100109075 | 12:15 PM | BANK→SAFE | \$1,000.00 |
| ROA | ROA00030587 | 12:07 PM | BANK→SAFE | \$1,000.00 |
| WAY | VAP00072758 | 12:02 PM | BANK→SAFE | \$1,000.00 |
| WAY | VAP00072801 | 4:59 PM | BANK→SAFE | \$2,000.00 |

## Step 5 — Reconciliation
| Store | Net expected (Slack) | Net actual (Bravo) | Status |
|---|---|---|---|
| CUL — Culpeper | \$1,000.00 | \$1,000.00 | ✓ Matched |
| HAR — Harrisonburg | \$0.00 | \$0.00 | ✓ Matched |
| LEX — Lexington | \$1,000.00 | \$1,000.00 | ✓ Matched |
| ROA — Roanoke | \$1,000.00 | \$1,000.00 | ✓ Matched |
| WAY — Waynesboro | \$3,000.00 | \$3,000.00 | ✓ Matched |
| **Total** | **\$6,000.00** | **\$6,000.00** | **5/5 matched** |

**Slack post: made.**

_Report generated 2026-07-09 ~18:12 ET._
