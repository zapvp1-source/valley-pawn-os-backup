# Daily Funds Verification — 2026-06-29

**Status: COMPLETE — all 5 verified. Every dollar sent today is in the Bravo safes.**

## Bottom line
$13,000.00 expected vs $13,000.00 actual across all 5 stores. 5/5 matched, no exceptions.

## Step 1 — Slack ledger (today, 2026-06-29 ET)
| Store | Channel | Request(s) | Joshua's reply | Net expected |
|---|---|---|---|---|
| CUL — Culpeper | #pepper-funds | $1k (09:51) + $2k (13:47) | Sent 1k (11:04); sent 2k (13:53) | $3,000.00 |
| HAR — Harrisonburg | #harrisonburg-funds | $2k (10:19) + $2k (16:28) | Sent 2k (11:01); sent 2k (16:32), re-sent 2k (16:47) after "cash isn't there" | $4,000.00 |
| LEX — Lexington | #lex-funds | $2k (09:44) | Sent 2k (11:04) | $2,000.00 |
| ROA — Roanoke | #roanoke-funds | $2k (11:43) | Sent 2k (12:03) | $2,000.00 |
| WAY — Waynesboro | #boro-funds | $2k (09:50) | Sent 2k (11:04) | $2,000.00 |

Cancellations: none. HAR afternoon counted as ONE transfer (the 16:47 re-send was a troubleshoot of the same 16:28 request, confirmed by a single Bravo entry at 4:54 PM). **Total expected: $13,000.00.**

## Step 2 — Bravo extraction
Trigger `daily-funds-verification-2026-06-29T18-05-40` → watcher status `success` on 5/5 cells (CUL 43 rows, HAR 35, LEX 58, ROA 33, WAY 31). Bravo health gate PASS before trigger drop.

## Step 3 — Bravo signature rows (TENDER TRANSFER · BANK · Cash · negative leg)
| Store | Txn Num | Time | From→To | Amount |
|---|---|---|---|---|
| CUL | VP400062370 | 12:16 PM | BANK→SAFE | $1,000.00 |
| CUL | VP400062383 | 2:21 PM | BANK→SAFE | $2,000.00 |
| HAR | VA500052524 | 11:36 AM | BANK→SAFE | $2,000.00 |
| HAR | VA500052548 | 4:54 PM | BANK→SAFE | $2,000.00 |
| LEX | VA100108821 | 11:47 AM | BANK→SAFE | $2,000.00 |
| ROA | ROA00030189 | 1:24 PM | BANK→SAFE | $2,000.00 |
| WAY | VAP00072346 | 11:40 AM | BANK→SAFE | $2,000.00 |

LEX also had a non-qualifying Debit Card BANK transfer ($237.25, positive leg) — ignored per rule.

## Step 5 — Reconciliation
| Store | Net expected (Slack) | Net actual (Bravo) | Status |
|---|---|---|---|
| CUL — Culpeper | $3,000.00 | $3,000.00 | ✓ Matched |
| HAR — Harrisonburg | $4,000.00 | $4,000.00 | ✓ Matched |
| LEX — Lexington | $2,000.00 | $2,000.00 | ✓ Matched |
| ROA — Roanoke | $2,000.00 | $2,000.00 | ✓ Matched |
| WAY — Waynesboro | $2,000.00 | $2,000.00 | ✓ Matched |
| **Total** | **$13,000.00** | **$13,000.00** | **ALL MATCHED — 5/5** |

**Slack post: made (#daily-funds-reconcilation).**

_Report generated 2026-06-29 ~18:16 ET._
