# Daily Funds Verification — 2026-09-22

**Status: COMPLETE — all 5 verified. ALL MATCHED.**

## Bottom line
$4,000.00 expected vs $4,000.00 actual across all 5 stores — every dollar sent today is in the Bravo safes.

## Step 1 — Slack ledger (today, 2026-09-22 ET)
| Store | Channel | Request(s) | Joshua's reply | Net expected |
|---|---|---|---|---|
| CUL — Culpeper | #pepper-funds | No cash request today (channel only had phone/WiFi setup chatter) | — | $0.00 |
| HAR — Harrisonburg | #harrisonburg-funds | Walker: "Ops cash need 2k" (9:34 AM) | "Sent 2k" (9:52 AM) | $2,000.00 |
| LEX — Lexington | #lex-funds | Uriah: "Need cash daily ops 2k" (9:42 AM) | "sent 2k" (9:55 AM); Uriah confirmed "Made deposit" (10:13 AM) | $2,000.00 |
| ROA — Roanoke | #roanoke-funds | No cash request today (channel activity was phone/WiFi provisioning; Benjie's "Sent" referred to a MAC address sent to Preston, not cash) | — | $0.00 |
| WAY — Waynesboro | #boro-funds | No activity today | — | $0.00 |

Cancellations: none. **Total expected: $4,000.00.**

## Step 2 — Bravo extraction
Trigger `daily-funds-verification-2026-09-22` → watcher status `success` on 5/5 cells.

## Step 3 — Bravo signature rows (TENDER TRANSFER · BANK · Cash · negative leg)
| Store | Txn Num | Time | From→To | Amount |
|---|---|---|---|---|
| CUL — Culpeper | (no cash transfer) | — | — | $0.00 |
| HAR — Harrisonburg | VA500055736 | 10:14 AM | BANK→SAFE (Cash) | $2,000.00 |
| LEX — Lexington | VA100110842 | 10:24 AM | BANK→SAFE (Cash) | $2,000.00 |
| ROA — Roanoke | (no cash transfer) | — | — | $0.00 |
| WAY — Waynesboro | (no cash transfer) | — | — | $0.00 |

## Step 5 — Reconciliation
| Store | Net expected (Slack) | Net actual (Bravo) | Status |
|---|---|---|---|
| CUL — Culpeper | $0.00 | $0.00 | ✓ Matched |
| HAR — Harrisonburg | $2,000.00 | $2,000.00 | ✓ Matched |
| LEX — Lexington | $2,000.00 | $2,000.00 | ✓ Matched |
| ROA — Roanoke | $0.00 | $0.00 | ✓ Matched |
| WAY — Waynesboro | $0.00 | $0.00 | ✓ Matched |
| **Total** | **$4,000.00** | **$4,000.00** | **5/5 matched** |

**Slack post: made.**

_Report generated 2026-09-22 ~18:25 ET._
