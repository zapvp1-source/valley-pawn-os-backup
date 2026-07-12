# Daily Funds Verification — 2026-07-11

**Status: COMPLETE — all 5 verified. All matched.**

## Bottom line
$3,000.00 expected vs $3,000.00 actual across all 5 stores — every dollar sent today is in the Bravo safes.

## Step 1 — Slack ledger (today, 2026-07-11 ET)
| Store | Channel | Request(s) | Joshua's reply | Net expected |
|---|---|---|---|---|
| CUL — Culpeper | #pepper-funds | none today | none | $0.00 |
| HAR — Harrisonburg | #harrisonburg-funds | Walker: Deposited cash $1k (self-deposit note, not a funds request) | no send reply, not a Joshua-funded transfer | $0.00 |
| LEX — Lexington | #lex-funds | none today | none | $0.00 |
| ROA — Roanoke | #roanoke-funds | Benjie: Ops cash need 1k (16:05) | Joshua: sent 1k, go get em (17:01) | $1,000.00 |
| WAY — Waynesboro | #boro-funds | Chadd: Ops cash, need 2k (10:48, re-confirmed 14:13) | Joshua: Sent 2k (15:42) | $2,000.00 |

Cancellations: none. Total expected: $3,000.00.

## Step 2 — Bravo extraction
Trigger daily-funds-verification-2026-07-11T18-05-03 — watcher status success on 5/5 cells.

## Step 3 — Bravo signature rows (TENDER TRANSFER, BANK, Cash, negative leg)
| Store | Txn Num | Time | From to To | Amount |
|---|---|---|---|---|
| CUL — Culpeper | no cash transfer | — | — | $0.00 |
| HAR — Harrisonburg | no cash transfer, see note | — | — | $0.00 |
| LEX — Lexington | no cash transfer | — | — | $0.00 |
| ROA — Roanoke | ROA00030729 | 5:27 PM | BANK to Safe | $1,000.00 |
| WAY — Waynesboro | VAP00072919 | 4:10 PM | BANK to Safe | $2,000.00 |

Note: HAR had an unrelated SAFE to BANK Cash transfer of $1,000.00, a deposit-out in the opposite direction, plus a TL-01 to SAFE till drop. Neither is a BANK-to-store funds-in, so both are correctly excluded.

## Step 5 — Reconciliation
| Store | Net expected (Slack) | Net actual (Bravo) | Status |
|---|---|---|---|
| CUL — Culpeper | $0.00 | $0.00 | Matched |
| HAR — Harrisonburg | $0.00 | $0.00 | Matched |
| LEX — Lexington | $0.00 | $0.00 | Matched |
| ROA — Roanoke | $1,000.00 | $1,000.00 | Matched |
| WAY — Waynesboro | $2,000.00 | $2,000.00 | Matched |
| Total | $3,000.00 | $3,000.00 | 5/5 matched |

Slack post: made.

Report generated 2026-07-11 ~18:15 ET.
