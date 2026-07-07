# Daily Funds Verification — 2026-06-18

**Status: COMPLETE — all 5 verified. Every dollar sent today is in the Bravo safes.**

## Bottom line
$6,000.00 expected vs $6,000.00 actual — all 5 stores matched, no exceptions. Funds were sent to Harrisonburg, Lexington, and Waynesboro ($2,000 each); Culpeper and Roanoke had no transfers today.

## Step 1 — Slack ledger (today, 2026-06-18 ET)
| Store | Channel | Request(s) | Joshua's reply | Net expected |
|---|---|---|---|---|
| CUL — Culpeper | #pepper-funds | (none) | (none) | $0.00 |
| HAR — Harrisonburg | #harrisonburg-funds | Andrew Clark: "Ops cash need 2k" | "Sent 2k" | $2,000.00 |
| LEX — Lexington | #lex-funds | Uriah: requesting 1700 for a deal | "Sent 1k" + "Sent another 1k" | $2,000.00 |
| ROA — Roanoke | #roanoke-funds | (none) | (none) | $0.00 |
| WAY — Waynesboro | #boro-funds | Chadd: "Ops cash, need 2k" | "Sent 2k" | $2,000.00 |

Cancellations: none. **Total expected: $6,000.00.**

## Step 2 — Bravo extraction
Trigger `daily-funds-verification-2026-06-18T18-03-38` → watcher status `success` on 5/5 cells (CUL 30 rows, HAR 51, LEX 33, ROA 29, WAY 31).

## Step 3 — Bravo signature rows (TENDER TRANSFER · BANK · Cash · negative leg)
| Store | Txn Num | Time | From→To | Amount |
|---|---|---|---|---|
| CUL — Culpeper | — | — | (no cash BANK transfer) | $0.00 |
| HAR — Harrisonburg | VA500052134 | 3:55 PM | BANK→SAFE | $2,000.00 |
| LEX — Lexington | VA100108555 | 11:14 AM | BANK→SAFE | $2,000.00 |
| ROA — Roanoke | — | — | (no cash BANK transfer) | $0.00 |
| WAY — Waynesboro | VAP00071900 | 4:03 PM | BANK→SAFE | $2,000.00 |

## Step 5 — Reconciliation
| Store | Net expected (Slack) | Net actual (Bravo) | Status |
|---|---|---|---|
| CUL — Culpeper | $0.00 | $0.00 | ✓ Matched |
| HAR — Harrisonburg | $2,000.00 | $2,000.00 | ✓ Matched |
| LEX — Lexington | $2,000.00 | $2,000.00 | ✓ Matched |
| ROA — Roanoke | $0.00 | $0.00 | ✓ Matched |
| WAY — Waynesboro | $2,000.00 | $2,000.00 | ✓ Matched |
| **Total** | **$6,000.00** | **$6,000.00** | **ALL MATCHED — 5/5** |

Note: Lexington's two separate $1k sends were entered in Bravo as a single $2,000 BANK→SAFE transfer (VA100108555). Net actual $2,000 matches net expected $2,000.

**Slack post: made (#daily-funds-reconcilation, C0B3R9B3S8H).**

_Report generated 2026-06-18 ~18:15 ET._
