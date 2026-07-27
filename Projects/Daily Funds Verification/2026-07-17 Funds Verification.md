# Daily Funds Verification — 2026-07-17

**Status: COMPLETE — all 5 verified. All matched.**

## Bottom line
$6,500.00 expected vs $6,500.00 actual across all 5 stores; every store matched with no discrepancies.

## Step 1 — Slack ledger (today, 2026-07-17 ET)
| Store | Channel | Request(s) | Joshua'\''s reply | Net expected |
|---|---|---|---|---|
| CUL — Culpeper | #pepper-funds | (Sandi Cole, no text captured — likely image/attachment ask) | "Sent 1500" @ 3:21 PM | \$1,500.00 |
| HAR — Harrisonburg | #harrisonburg-funds | Walker Tapley: "ops cash need \$2k" @ 9:33 AM | "sent 2k" @ 9:40 AM | \$2,000.00 |
| LEX — Lexington | #lex-funds | Uriah: "Need cash for daily ops if available" @ 9:40 AM | "sent 1k" @ 9:40 AM | \$1,000.00 |
| ROA — Roanoke | #roanoke-funds | (no messages today) | (none) | \$0.00 |
| WAY — Waynesboro | #boro-funds | Chadd: "Ops cash, need 2k" @ 9:16 AM, re-asked @ 9:52 AM (same request) | "Sent 2k" @ 10:04 AM | \$2,000.00 |

Cancellations: none. **Total expected: \$6,500.00.**

## Step 2 — Bravo extraction
Trigger `daily-funds-verification-2026-07-17T18-04-56` → watcher status `success` on 5/5 cells. Queue had 4 unrelated leftover eomxlsx batch triggers ahead of this one; all cleared normally before this trigger claimed. No watcher restart needed.

## Step 3 — Bravo signature rows (TENDER TRANSFER · BANK · Cash · negative leg)
| Store | Txn Num | Time | From→To | Amount |
|---|---|---|---|---|
| CUL | VP400063237 | 3:39 PM | BANK→SAFE | \$1,500.00 |
| HAR | VA500053152 | 9:56 AM | BANK→SAFE | \$2,000.00 |
| LEX | VA100109249 | 9:57 AM | BANK→SAFE | \$1,000.00 |
| ROA | (no cash transfer) | — | — | \$0.00 |
| WAY | VAP00073090 | 10:24 AM | BANK→SAFE | \$2,000.00 |

## Step 5 — Reconciliation
| Store | Net expected (Slack) | Net actual (Bravo) | Status |
|---|---|---|---|
| CUL — Culpeper | \$1,500.00 | \$1,500.00 | ✓ Matched |
| HAR — Harrisonburg | \$2,000.00 | \$2,000.00 | ✓ Matched |
| LEX — Lexington | \$1,000.00 | \$1,000.00 | ✓ Matched |
| ROA — Roanoke | \$0.00 | \$0.00 | ✓ Matched |
| WAY — Waynesboro | \$2,000.00 | \$2,000.00 | ✓ Matched |
| **Total** | **\$6,500.00** | **\$6,500.00** | **5/5 matched** |

**Slack post: made (#daily-funds-reconcilation).**

_Report generated 2026-07-17 ~18:26 ET._
