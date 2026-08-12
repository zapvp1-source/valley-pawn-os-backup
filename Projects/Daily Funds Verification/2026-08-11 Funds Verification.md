# Daily Funds Verification — 2026-08-11

**Status: COMPLETE — all 5 verified. All stores matched.**

## Bottom line
All $6,000.00 in confirmed cash transfers sent to stores today were entered into Bravo the same day. One additional Culpeper request ($2k gold buy) was still open at day's end with no confirmed "Sent" reply in Slack, so it was correctly excluded from expected totals and Bravo shows no matching transfer for it.

## Step 1 — Slack ledger (today, 2026-08-11 ET)
| Store | Channel | Request(s) | Joshua's reply | Net expected |
|---|---|---|---|---|
| CUL — Culpeper | #pepper-funds | Sandi 11:11am "Working on a \$2k Gold buy"; Sandi 2:16pm "Ops Cash Needed \$2k" (confirmed still needed 4:59pm, no send reply found) | "sent 2k" 11:36am | \$2,000.00 |
| HAR — Harrisonburg | #harrisonburg-funds | (no messages today) | — | \$0.00 |
| LEX — Lexington | #lex-funds | (no messages today) | — | \$0.00 |
| ROA — Roanoke | #roanoke-funds | Benjie 10:11am "Ops cash need 2k" | "sent 2k" 11:36am | \$2,000.00 |
| WAY — Waynesboro | #boro-funds | Chadd 9:09am "Ops cash, need 2k" | "Sent 2k. Go get em" 9:37am | \$2,000.00 |

Cancellations: none. Open/unconfirmed: Culpeper's 2:16pm \$2k request (Sandi confirmed still needed at 4:59pm; no "Sent" reply captured in today's window) — excluded from expected total, flagged for follow-up. **Total expected: \$6,000.00.**

## Step 2 — Bravo extraction
Trigger `daily-funds-verification-2026-08-11T18-10-20` → watcher status `success` on 5/5 cells (CUL 59 rows, HAR 29 rows, LEX 29 rows, ROA 33 rows, WAY 35 rows). No retries needed.

## Step 3 — Bravo signature rows (TENDER TRANSFER · BANK · Cash · negative leg)
| Store | Txn Num | Time | From→To | Amount |
|---|---|---|---|---|
| CUL | VP400064415 | 11:58 AM | BANK→SAFE | \$2,000.00 |
| HAR | (none) | — | — | \$0.00 |
| LEX | (none) | — | — | \$0.00 |
| ROA | ROA00031806 | 12:05 PM | BANK→SAFE | \$2,000.00 |
| WAY | VAP00074255 | 10:17 AM | BANK→SAFE | \$2,000.00 |

Note: WAY also shows a same-day \$4,000 SAFE→TL-01→SAFE→BANK round trip (11:25-11:26 AM) — a store deposit back to bank, not a funds-in transfer; correctly excluded per the Till Number=BANK + negative-leg rule.

## Step 5 — Reconciliation
| Store | Net expected (Slack) | Net actual (Bravo) | Status |
|---|---|---|---|
| CUL — Culpeper | \$2,000.00 | \$2,000.00 | ✓ Matched |
| HAR — Harrisonburg | \$0.00 | \$0.00 | ✓ Matched |
| LEX — Lexington | \$0.00 | \$0.00 | ✓ Matched |
| ROA — Roanoke | \$2,000.00 | \$2,000.00 | ✓ Matched |
| WAY — Waynesboro | \$2,000.00 | \$2,000.00 | ✓ Matched |
| **Total** | **\$6,000.00** | **\$6,000.00** | **5/5 matched** |

**Slack post: made (#daily-funds-reconcilation, C0B3R9B3S8H).**

_Report generated 2026-08-11 ~18:20 ET._
