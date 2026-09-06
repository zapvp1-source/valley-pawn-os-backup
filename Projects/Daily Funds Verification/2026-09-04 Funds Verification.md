# Daily Funds Verification — 2026-09-04

**Status: COMPLETE — all 5 verified. ALL MATCHED.**

## Bottom line
\$2,000.00 expected vs \$2,000.00 actual across all 5 stores; all 5 matched exactly.

## Step 1 — Slack ledger (today, 2026-09-04 ET)
| Store | Channel | Request(s) | Joshua's reply | Net expected |
|---|---|---|---|---|
| CUL — Culpeper | #pepper-funds | \$500 ops cash (10:54 AM); Joshua replied "yes" (12:23 PM) but Sandi then said "Going to try and make due for now. TY!" (12:24 PM) — request called off. Second request: \$1,500 ops cash (3:04 PM), tagged again (3:44 PM), no reply in window. | "yes" (approval only, no send confirmed); no reply to 2nd ask | \$0.00 |
| HAR — Harrisonburg | #harrisonburg-funds | No funds request from the store. Preston posted "Deposited 2k" (4:48 PM) — this is a safe→bank deposit (see Step 3), not a Joshua funds-in. | n/a | \$0.00 |
| LEX — Lexington | #lex-funds | Need cash daily ops 2k (9:59 AM) | "sent 1k" (10:33 AM) | \$1,000.00 |
| ROA — Roanoke | #roanoke-funds | No activity today. | n/a | \$0.00 |
| WAY — Waynesboro | #boro-funds | Ops cash, need 2k (4:35 PM) | "Sent 2k" (4:54 PM); Chadd: "Only took 1k cause bank was closed. Thank you" (6:01 PM) — only \$1,000 actually picked up today, \$1,000 remains for a later pickup. | \$1,000.00 |

Cancellations: Culpeper \$500 ask called off by Sandi after approval; Culpeper \$1,500 ask never answered/sent. **Total expected: \$2,000.00.**

## Step 2 — Bravo extraction
Trigger \`daily-funds-verification-2026-09-04T18-05-32\` → watcher status \`success\` on 5/5 cells (CUL, HAR, LEX, ROA, WAY).

## Step 3 — Bravo signature rows (TENDER TRANSFER · BANK · Cash · negative leg)
| Store | Txn Num | Time | From→To | Amount |
|---|---|---|---|---|
| CUL | — | — | (no cash transfer) | \$0.00 |
| HAR | — | — | (no cash transfer — the SAFE→BANK \$2,000 deposit at 4:56 PM is an outgoing bank deposit, not a funds-in; excluded per signature) | \$0.00 |
| LEX | VA100110414 | 11:12 AM | BANK→SAFE | \$1,000.00 |
| ROA | — | — | (no cash transfer) | \$0.00 |
| WAY | VAP00075282 | 5:12 PM | BANK→SAFE | \$1,000.00 |

## Step 5 — Reconciliation
| Store | Net expected (Slack) | Net actual (Bravo) | Status |
|---|---|---|---|
| CUL — Culpeper | \$0.00 | \$0.00 | ✓ Matched |
| HAR — Harrisonburg | \$0.00 | \$0.00 | ✓ Matched |
| LEX — Lexington | \$1,000.00 | \$1,000.00 | ✓ Matched |
| ROA — Roanoke | \$0.00 | \$0.00 | ✓ Matched |
| WAY — Waynesboro | \$1,000.00 | \$1,000.00 | ✓ Matched |
| **Total** | **\$2,000.00** | **\$2,000.00** | **5/5 matched** |

**Slack post: made** (#daily-funds-reconcilation).

_Report generated 2026-09-04 ~18:14 ET._
