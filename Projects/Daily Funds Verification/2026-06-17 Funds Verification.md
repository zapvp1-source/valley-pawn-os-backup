# Daily Funds Verification — 2026-06-17

**Status: COMPLETE — all 5 verified. Every dollar sent today is in the Bravo safes.**

## Bottom line
$1,000.00 expected vs $1,000.00 actual. All 5 stores matched; no discrepancies. Only Culpeper had a transfer today ($1,000 reloan); the other four stores had no funds sent and no safe entries.

## Step 1 — Slack ledger (today, 2026-06-17 ET)
| Store | Channel | Request(s) | Joshua's reply | Net expected |
|---|---|---|---|---|
| CUL — Culpeper | #pepper-funds | Sandi: reloan, customer local, waiting for VA ID (10:37 AM) | "sent 1k! GM" (10:39 AM) | $1,000.00 |
| HAR — Harrisonburg | #harrisonburg-funds | (none) | (none) | $0.00 |
| LEX — Lexington | #lex-funds | (none) | (none) | $0.00 |
| ROA — Roanoke | #roanoke-funds | (none) | (none) | $0.00 |
| WAY — Waynesboro | #boro-funds | (none) | (none) | $0.00 |

Cancellations: none. **Total expected: $1,000.00.**

## Step 2 — Bravo extraction
Trigger `daily-funds-verification-2026-06-17T18-03-39` → watcher status `success` on 5/5 cells. Row counts: CUL 39, HAR 5, LEX 5, ROA 5, WAY 5. Finished 18:12 ET.

## Step 3 — Bravo signature rows (TENDER TRANSFER · BANK · Cash · negative leg)
| Store | Txn Num | Time | From→To | Amount |
|---|---|---|---|---|
| CUL — Culpeper | VP400061768 | 6/17/2026 10:55 AM | BANK→SAFE | $1,000.00 |
| HAR — Harrisonburg | — | — | (no cash transfer) | $0.00 |
| LEX — Lexington | — | — | (no cash transfer) | $0.00 |
| ROA — Roanoke | — | — | (no cash transfer) | $0.00 |
| WAY — Waynesboro | — | — | (no cash transfer) | $0.00 |

Note: CUL also had a SAFE→TL-01 cash transfer ($1,250) and a TL-02 close debit/visa transfer — neither is a BANK→SAFE funds-in, so both are correctly excluded.

## Step 5 — Reconciliation
| Store | Net expected (Slack) | Net actual (Bravo) | Status |
|---|---|---|---|
| CUL — Culpeper | $1,000.00 | $1,000.00 | ✓ Matched |
| HAR — Harrisonburg | $0.00 | $0.00 | ✓ Matched |
| LEX — Lexington | $0.00 | $0.00 | ✓ Matched |
| ROA — Roanoke | $0.00 | $0.00 | ✓ Matched |
| WAY — Waynesboro | $0.00 | $0.00 | ✓ Matched |
| **Total** | **$1,000.00** | **$1,000.00** | **ALL MATCHED** |

**Slack post: made.**

_Report generated 2026-06-17 ~18:13 ET._
