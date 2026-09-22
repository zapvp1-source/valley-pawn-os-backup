# Daily Funds Verification — 2026-09-21

**Status: COMPLETE — all 5 verified. DISCREPANCY FOUND (Roanoke).**

## Bottom line
$4,000.00 expected (per confirmed Slack "Sent" replies) vs $7,100.00 actual in Bravo safes. Culpeper, Harrisonburg, Lexington, and Waynesboro matched. Roanoke shows $3,100.00 landed in the safe via a same-day cash transfer, but no "Sent" confirmation from Joshua was found in #roanoke-funds for that request — funds are present, just missing the text confirmation.

## Step 1 — Slack ledger (today, 2026-09-21 ET)
| Store | Channel | Request(s) | Joshua's reply | Net expected |
|---|---|---|---|---|
| CUL — Culpeper | #pepper-funds | Sandi, 2:17 PM: "GA! Cash Ops Needed $2k" | Joshua, 2:27 PM: "Set. 2k" | $2,000.00 |
| HAR — Harrisonburg | #harrisonburg-funds | Walker, 9:01 AM: "Ops cash need 2k" | Joshua, 11:33 AM: "Sent 2k" | $2,000.00 |
| LEX — Lexington | #lex-funds | (none today) | — | $0.00 |
| ROA — Roanoke | #roanoke-funds | Benjie, 4:27 PM: "Large buy cash need 3100" | **No reply found in channel** | $0.00 (unconfirmed) |
| WAY — Waynesboro | #boro-funds | (none today) | — | $0.00 |

Cancellations: none. **Total expected (confirmed Slack replies only): $4,000.00.**

## Step 2 — Bravo extraction
Trigger `daily-funds-verification-2026-09-21T1809` → watcher status `success` on 5/5 cells (via host job queue / `bravo_pull.sh`, health gate PASS).

## Step 3 — Bravo signature rows (TENDER TRANSFER · BANK · Cash · negative leg)
| Store | Txn Num | Time | From→To | Amount |
|---|---|---|---|---|
| CUL | VP400066387 | 3:00 PM | BANK→SAFE | $2,000.00 |
| HAR | VA500055691 | 12:05 PM | BANK→SAFE | $2,000.00 |
| LEX | — | — | (no cash transfer) | $0.00 |
| ROA | ROA00033256 | 5:01 PM | BANK→SAFE | $3,100.00 |
| WAY | — | — | (no cash transfer) | $0.00 |

## Step 5 — Reconciliation
| Store | Net expected (Slack) | Net actual (Bravo) | Status |
|---|---|---|---|
| CUL — Culpeper | $2,000.00 | $2,000.00 | ✓ Matched |
| HAR — Harrisonburg | $2,000.00 | $2,000.00 | ✓ Matched |
| LEX — Lexington | $0.00 | $0.00 | ✓ Matched |
| ROA — Roanoke | $0.00 | $3,100.00 | ⚠ Discrepancy (funds present, Slack confirmation text missing) |
| WAY — Waynesboro | $0.00 | $0.00 | ✓ Matched |
| **Total** | **$4,000.00** | **$7,100.00** | **4/5 matched** |

**Slack post: made (#daily-funds-reconcilation).**

_Report generated 2026-09-21 ~18:20 ET._
