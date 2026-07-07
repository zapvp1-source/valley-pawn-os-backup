# Daily Funds Verification — 2026-06-11

**Status: COMPLETE — all 5 verified. ALL MATCHED.**

## Bottom line
$9,000.00 expected vs $9,000.00 actual; all 5 stores matched, no exceptions.

## Step 1 — Slack ledger (today, 2026-06-11 ET)
| Store | Channel | Request(s) | Joshua's reply | Net expected |
|---|---|---|---|---|
| CUL — Culpeper | #pepper-funds | Bree Grayson: "Ops cash needed $2k" (4:04 PM) | "Sent 2k" (4:04 PM) | $2,000.00 |
| HAR — Harrisonburg | #harrisonburg-funds | Walker Tapley: "Ops cash need 2k" (9:23 AM); "ops cash need 1K" (5:32 PM) | "Sent 2k" (9:41 AM); "Sent 1k" (5:39 PM) | $3,000.00 |
| LEX — Lexington | #lex-funds | (no messages today) | — | $0.00 |
| ROA — Roanoke | #roanoke-funds | Benjie Moore: "Ops need cash 2k" (10:01 AM) | "sent 2k" (10:31 AM) | $2,000.00 |
| WAY — Waynesboro | #boro-funds | Martin D.: "Ops cash, need 2k" (4:12 PM); Joshua "still need?" → Chadd "Yes" | "sent 2k" (4:54 PM) | $2,000.00 |

Cancellations: none. **Total expected: $9,000.00.**

## Step 2 — Bravo extraction
Trigger `daily-funds-verification-2026-06-11T18-04-39` → watcher status `success` on 5/5 cells.

## Step 3 — Bravo signature rows (TENDER TRANSFER · BANK · Cash · negative leg)
| Store | Txn Num | Time | From→To | Amount |
|---|---|---|---|---|
| CUL | VP400061521 | 4:38 PM | BANK→SAFE | $2,000.00 |
| HAR | VA500051810 | 10:01 AM | BANK→SAFE | $2,000.00 |
| HAR | VA500051865 | 5:54 PM | BANK→SAFE | $1,000.00 |
| LEX | (no cash transfer) | — | — | $0.00 |
| ROA | ROA00029469 | 11:17 AM | BANK→SAFE | $2,000.00 |
| WAY | VAP00071639 | 6:09 PM | BANK→SAFE | $2,000.00 |

## Step 5 — Reconciliation
| Store | Net expected (Slack) | Net actual (Bravo) | Status |
|---|---|---|---|
| CUL — Culpeper | $2,000.00 | $2,000.00 | ✓ Matched |
| HAR — Harrisonburg | $3,000.00 | $3,000.00 | ✓ Matched |
| LEX — Lexington | $0.00 | $0.00 | ✓ Matched |
| ROA — Roanoke | $2,000.00 | $2,000.00 | ✓ Matched |
| WAY — Waynesboro | $2,000.00 | $2,000.00 | ✓ Matched |
| **Total** | **$9,000.00** | **$9,000.00** | **ALL MATCHED** |

**Slack post: made.**

Notes: Harrisonburg was a split send (two separate requests: $2k AM + $1k PM), counted as $3,000 total — both legs found in Bravo. Waynesboro's WAY entry was keyed by MDOWDEN@CUL at 6:09 PM (after the Slack send at 4:54 PM), same-day compliant. LEX's only BANK transfers today were Debit Card legs (till-close deposits), correctly excluded.

_Report generated 2026-06-11 ~18:14 ET._
