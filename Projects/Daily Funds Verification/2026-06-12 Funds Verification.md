# Daily Funds Verification — 2026-06-12

**Status: COMPLETE — all 5 verified. All matched.**

## Bottom line
$4,000.00 expected vs $4,000.00 actual; all 5 stores matched, no exceptions.

## Step 1 — Slack ledger (today, 2026-06-12 ET)
| Store | Channel | Request(s) | Joshua's reply | Net expected |
|---|---|---|---|---|
| CUL — Culpeper | #pepper-funds | (none) | — | $0.00 |
| HAR — Harrisonburg | #harrisonburg-funds | Walker: "ops cash need 2k" (9:25 AM) | "Sent 2k" (9:36 AM) | $2,000.00 |
| LEX — Lexington | #lex-funds | (none) | — | $0.00 |
| ROA — Roanoke | #roanoke-funds | (none) | — | $0.00 |
| WAY — Waynesboro | #boro-funds | Chadd: "Ops cash, need 2k" (1:11 PM) | "Still need?" → "Sent 2k" (1:29 PM) | $2,000.00 |

Cancellations: none. **Total expected: $4,000.00.**

## Step 2 — Bravo extraction
Trigger `daily-funds-verification-2026-06-12T18-03-46` → watcher status `partial` on 4/5 cells (CUL errored: Preview did not render within 60s). Retry trigger `daily-funds-verification-2026-06-12T18-12-41-retry-1` → `success` on CUL. Final: 5/5 clean CSVs.

## Step 3 — Bravo signature rows (TENDER TRANSFER · BANK · Cash · negative leg)
| Store | Txn Num | Time | From→To | Amount |
|---|---|---|---|---|
| CUL | (no cash transfer) | — | — | $0.00 |
| HAR | VA500051876 | 10:01 AM | BANK→SAFE (WTAPLEY) | $2,000.00 |
| LEX | (no cash transfer) | — | — | $0.00 |
| ROA | (no cash transfer) | — | — | $0.00 |
| WAY | VAP00071693 | 6:08 PM | BANK→SAFE (MDOWDEN@CUL) | $2,000.00 |

Ignored non-qualifying rows: SAFE→TL till floats (HAR VA500051877, WAY VAP00071694, CUL VP400061590) and Debit Card BANK transfers (card deposits, not cash funds-ins).

## Step 5 — Reconciliation
| Store | Net expected (Slack) | Net actual (Bravo) | Status |
|---|---|---|---|
| CUL — Culpeper | $0.00 | $0.00 | ✓ Matched |
| HAR — Harrisonburg | $2,000.00 | $2,000.00 | ✓ Matched |
| LEX — Lexington | $0.00 | $0.00 | ✓ Matched |
| ROA — Roanoke | $0.00 | $0.00 | ✓ Matched |
| WAY — Waynesboro | $2,000.00 | $2,000.00 | ✓ Matched |
| **Total** | **$4,000.00** | **$4,000.00** | **ALL MATCHED** |

**Slack post: made.**

Note: Waynesboro's $2,000 was entered at 6:08 PM by MDOWDEN@CUL — same-day, entered just before this run's extraction.

_Report generated 2026-06-12 ~18:15 ET._
