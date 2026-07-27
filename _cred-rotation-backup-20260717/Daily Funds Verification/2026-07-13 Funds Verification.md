# Daily Funds Verification — 2026-07-13

**Status: COMPLETE — all 5 verified. ALL MATCHED.**

## Bottom line
$12,500.00 expected vs $12,500.00 actual across all 5 stores; every store matched exactly.

## Step 1 — Slack ledger (today, 2026-07-13 ET)
| Store | Channel | Request(s) | Joshua's reply | Net expected |
|---|---|---|---|---|
| CUL — Culpeper | #pepper-funds | 9:33 AM $1,500; 4:36 PM $1,500 (gold loan $800 in front) | 9:44 AM sent $2,000 (GM); 4:39 PM sent $1,500 (Sandi: "Nothing available" / "not complete") then 4:52 PM sent $2,000, confirmed 5:01 PM "Got it" | $4,000.00 |
| HAR — Harrisonburg | #harrisonburg-funds | 9:57 AM $2,000 | 10:02 AM sent $2,000 | $2,000.00 |
| LEX — Lexington | #lex-funds | 4:31 PM $2,000 (or $1,000 ATM alt.) | 4:59 PM sent $1,000 | $1,000.00 |
| ROA — Roanoke | #roanoke-funds | 9:21 AM $2,000 | 9:44 AM sent $2,000 (GM) | $2,000.00 |
| WAY — Waynesboro | #boro-funds | 10:30 AM $2,000; 4:57 PM $2,000 | 11:00 AM sent $2,000; 4:59 PM sent $2,000, but Chadd clarified 5:24 PM "There was only 1500. Just was saying for claude purposes" | $3,500.00 |

Cancellations: none. **Total expected: $12,500.00.**

## Step 2 — Bravo extraction
Trigger `daily-funds-verification-2026-07-13T18-05-22` → watcher status `success` on 5/5 cells (CUL 36 rows, HAR 33 rows, LEX 33 rows, ROA 33 rows, WAY 35 rows).

## Step 3 — Bravo signature rows (TENDER TRANSFER · BANK · Cash · negative leg)
| Store | Txn Num | Time | From→To | Amount |
|---|---|---|---|---|
| CUL | VP400063012 | 10:48 AM | BANK→SAFE | $2,000.00 |
| CUL | VP400063047 | 5:51 PM | BANK→SAFE | $2,000.00 |
| HAR | VA500053009 | 10:41 AM | BANK→SAFE | $2,000.00 |
| LEX | VA100109182 | 5:15 PM | BANK→SAFE | $1,000.00 |
| ROA | ROA00030749 | 10:16 AM | BANK→SAFE | $2,000.00 |
| WAY | VAP00072950 | 12:01 PM | BANK→SAFE | $2,000.00 |
| WAY | VAP00072985 | 5:36 PM | BANK→SAFE | $1,500.00 |

## Step 5 — Reconciliation
| Store | Net expected (Slack) | Net actual (Bravo) | Status |
|---|---|---|---|
| CUL — Culpeper | $4,000.00 | $4,000.00 | ✓ Matched |
| HAR — Harrisonburg | $2,000.00 | $2,000.00 | ✓ Matched |
| LEX — Lexington | $1,000.00 | $1,000.00 | ✓ Matched |
| ROA — Roanoke | $2,000.00 | $2,000.00 | ✓ Matched |
| WAY — Waynesboro | $3,500.00 | $3,500.00 | ✓ Matched |
| **Total** | **$12,500.00** | **$12,500.00** | **ALL MATCHED** |

Notes: CUL's afternoon $1,500 send attempt showed as "not complete"/"nothing available" and was corrected by a $2,000 resend — treated as one transfer, matching the single $2,000 BANK cell at 5:51 PM. WAY's afternoon $2,000 send was explicitly clarified by Chadd ("There was only 1500... for claude purposes") — the Bravo entry confirms only $1,500 was actually transferred.

**Slack post: made.**

_Report generated 2026-07-13 ~18:13 ET._
