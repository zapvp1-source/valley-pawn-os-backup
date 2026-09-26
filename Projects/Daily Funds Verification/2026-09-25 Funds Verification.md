# Daily Funds Verification — 2026-09-25

**Status: COMPLETE — all 5 verified. All matched.**

## Bottom line
$2,000.00 expected vs $2,000.00 actual across all 5 stores; all 5 stores matched.

## Step 1 — Slack ledger (today, 2026-09-25 ET)
| Store | Channel | Request(s) | Joshua's reply | Net expected |
|---|---|---|---|---|
| CUL — Culpeper | #pepper-funds | Sandi: "Ops cash needed $2k" (13:10 ET) | "Sent 2k" (13:40 ET); Sandi "TY!" (13:43 ET) | $2,000.00 |
| HAR — Harrisonburg | #harrisonburg-funds | (no requests today) | — | $0.00 |
| LEX — Lexington | #lex-funds | (no requests today) | — | $0.00 |
| ROA — Roanoke | #roanoke-funds | (no requests today) | — | $0.00 |
| WAY — Waynesboro | #boro-funds | Chadd sent a photo, no text (11:18 ET) — confirmed by Bravo as a routine cash deposit to bank, not a funds-in request | "Tyty" (15:22 ET); Chadd "Np" (16:04 ET) | $0.00 |

Cancellations: none. **Total expected: $2,000.00.**

## Step 2 — Bravo extraction
Trigger `daily-funds-verification-2026-09-25T18-11-00` → watcher status `success` on 5/5 cells.

## Step 3 — Bravo signature rows (TENDER TRANSFER · BANK · Cash · negative leg)
| Store | Txn Num | Time | From→To | Amount |
|---|---|---|---|---|
| CUL — Culpeper | VP400066590 | 2:13 PM | BANK→SAFE | $2,000.00 |
| HAR — Harrisonburg | — | — | (no cash transfer) | $0.00 |
| LEX — Lexington | — | — | (no cash transfer) | $0.00 |
| ROA — Roanoke | — | — | (no cash transfer) | $0.00 |
| WAY — Waynesboro | — | — | (no cash transfer in; store recorded SAFE→BANK $1,850.00 cash deposit out, which does not count as a funds-in transfer) | $0.00 |

## Step 5 — Reconciliation
| Store | Net expected (Slack) | Net actual (Bravo) | Status |
|---|---|---|---|
| CUL — Culpeper | $2,000.00 | $2,000.00 | ✓ Matched |
| HAR — Harrisonburg | $0.00 | $0.00 | ✓ Matched |
| LEX — Lexington | $0.00 | $0.00 | ✓ Matched |
| ROA — Roanoke | $0.00 | $0.00 | ✓ Matched |
| WAY — Waynesboro | $0.00 | $0.00 | ✓ Matched |
| **Total** | **$2,000.00** | **$2,000.00** | **5/5 matched** |

**Slack post: made.**

_Report generated 2026-09-25 ~18:25 ET._
