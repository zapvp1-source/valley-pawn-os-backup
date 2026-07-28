# Daily Funds Verification — 2026-07-27

**Status: COMPLETE — all 5 verified. ALL MATCHED.**

## Bottom line
$10,000.00 expected vs $10,000.00 actual across all 5 stores. Every store matched exactly.

## Step 1 — Slack ledger (today, 2026-07-27 ET)
| Store | Channel | Request(s) | Joshua's reply | Net expected |
|---|---|---|---|---|
| CUL — Culpeper | #pepper-funds | Sandi: "GA! Ops Cash needed \$2k" 12:32pm | "sent 2k" 12:35pm | \$2,000.00 |
| HAR — Harrisonburg | #harrisonburg-funds | Walker: "Ops cash need 2k" 9:12am; "Ops cash isn't there" 9:40am, "Halp" 9:42am | "sent 2k" 9:24am, "check in 2 min" 9:55am, "done" 9:55am (same transfer, troubleshot in-thread) | \$2,000.00 |
| LEX — Lexington | #lex-funds | Uriah: "Requesting funds for daily ops" 9:32am | "sent 2k" 9:55am | \$2,000.00 |
| ROA — Roanoke | #roanoke-funds | Benjie: "Ops cash need 2k" 9:47am | "snet 2k" (typo for sent) 9:55am | \$2,000.00 |
| WAY — Waynesboro | #boro-funds | Chadd: "Ops cash, need 2k" 10:08am | "sent 2k" 10:09am | \$2,000.00 |

Cancellations: none. **Total expected: \$10,000.00.**

## Step 2 — Bravo extraction
Trigger \`daily-funds-verification-2026-07-27T18-04-55\` → watcher status \`success\` on 5/5 cells (CUL, HAR, LEX, ROA, WAY all succeeded first attempt, ~67-70s each).

## Step 3 — Bravo signature rows (TENDER TRANSFER · BANK · Cash · negative leg)
| Store | Txn Num | Time | From→To | Amount |
|---|---|---|---|---|
| CUL | VP400063665 | 1:28 PM | BANK→Safe (Cash) | \$2,000.00 |
| HAR | VA500053479 | 10:07 AM | BANK→Safe (Cash) | \$2,000.00 |
| LEX | VA100109452 | 10:39 AM | BANK→Safe (Cash) | \$2,000.00 |
| ROA | ROA00031228 | 10:25 AM | BANK→Safe (Cash) | \$2,000.00 |
| WAY | VAP00073516 | 11:18 AM | BANK→Safe (Cash) | \$2,000.00 |

(CUL and WAY each also had a same-day Debit Card BANK transfer — till/safe close activity, not a funds-in, excluded from the sum.)

## Step 5 — Reconciliation
| Store | Net expected (Slack) | Net actual (Bravo) | Status |
|---|---|---|---|
| CUL — Culpeper | \$2,000.00 | \$2,000.00 | ✓ Matched |
| HAR — Harrisonburg | \$2,000.00 | \$2,000.00 | ✓ Matched |
| LEX — Lexington | \$2,000.00 | \$2,000.00 | ✓ Matched |
| ROA — Roanoke | \$2,000.00 | \$2,000.00 | ✓ Matched |
| WAY — Waynesboro | \$2,000.00 | \$2,000.00 | ✓ Matched |
| **Total** | **\$10,000.00** | **\$10,000.00** | **5/5 matched** |

**Slack post: made.**

_Report generated 2026-07-27 ~18:12 ET._
