# Daily Funds Verification — 2026-08-01

**Status: COMPLETE — all 5 verified. DISCREPANCY FOUND.**

## Bottom line
$1,000.00 expected vs $0.00 actual across all 5 stores; 4/5 stores matched (all $0 no-activity days). Culpeper is the exception: $1,000 was sent but does not yet appear as a BANK→Safe cash transfer in today's Bravo journal.

## Step 1 — Slack ledger (today, 2026-08-01 ET)
| Store | Channel | Request(s) | Joshua's reply | Net expected |
|---|---|---|---|---|
| CUL — Culpeper | #pepper-funds | Bree: Gm! Ops Cash needed $2k (11:22 AM) | one sec (12:54 PM) → Sent 1k (1:10 PM) | $1,000.00 |
| HAR — Harrisonburg | #harrisonburg-funds | (none — performance feedback thread only) | — | $0.00 |
| LEX — Lexington | #lex-funds | (none — congrats/feedback thread only) | — | $0.00 |
| ROA — Roanoke | #roanoke-funds | (none — congrats thread only) | — | $0.00 |
| WAY — Waynesboro | #boro-funds | (none — praise message only) | — | $0.00 |

Cancellations: none. Total expected: $1,000.00.

Note: Culpeper's request was for $2k; only $1,000 was actually sent, so net expected uses the confirmed Sent 1k amount, not the requested amount.

## Step 2 — Bravo extraction
Trigger daily-funds-verification-2026-08-01T18-04-15 → watcher status success on 5/5 cells (CUL 49.7s, HAR 67.9s, LEX 63.7s, ROA 62.7s, WAY 63.6s).

## Step 3 — Bravo signature rows (TENDER TRANSFER · BANK · Cash · negative leg)
| Store | Txn Num | Time | From→To | Amount |
|---|---|---|---|---|
| CUL — Culpeper | (none) | — | (no Cash BANK→SAFE transfer found) | $0.00 |
| HAR — Harrisonburg | (none) | — | (no cash transfer) | $0.00 |
| LEX — Lexington | (none) | — | (no cash transfer) | $0.00 |
| ROA — Roanoke | ROA00031482 | 6:08 PM | SAFE→BANK (card tenders only — Debit/Visa/MC/Discover, no Cash) | $0.00 |
| WAY — Waynesboro | (none) | — | (no cash transfer) | $0.00 |

## Step 5 — Reconciliation
| Store | Net expected (Slack) | Net actual (Bravo) | Status |
|---|---|---|---|
| CUL — Culpeper | $1,000.00 | $0.00 | Discrepancy |
| HAR — Harrisonburg | $0.00 | $0.00 | Matched |
| LEX — Lexington | $0.00 | $0.00 | Matched |
| ROA — Roanoke | $0.00 | $0.00 | Matched |
| WAY — Waynesboro | $0.00 | $0.00 | Matched |
| Total | $1,000.00 | $0.00 | 4/5 matched |

Slack post: made (#daily-funds-reconcilation, https://valleypawnworkspace.slack.com/archives/C0B3R9B3S8H/p1785622315472279).

Report generated 2026-08-01 ~18:12 ET.