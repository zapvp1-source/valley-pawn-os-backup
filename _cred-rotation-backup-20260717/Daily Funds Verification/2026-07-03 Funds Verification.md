# Daily Funds Verification — 2026-07-03

**Status: COMPLETE — all 5 verified. Every dollar sent today is in the Bravo safes.**

## Bottom line
$6,600.00 expected vs $6,600.00 actual — all 5 stores matched. Bravo required a full ClickOnce kill + relaunch mid-run (LEX/ROA/WAY errored on the first pass); recovered via the health guard and a two-store retry.

## Step 1 — Slack ledger (today, 2026-07-03 ET)
| Store | Channel | Request(s) | Joshua's reply | Net expected |
|---|---|---|---|---|
| CUL — Culpeper | #pepper-funds | Bree: ops cash $1500 | sent 1500 | $1,500.00 |
| HAR — Harrisonburg | #harrisonburg-funds | (no messages) | — | $0.00 |
| LEX — Lexington | #lex-funds | Uriah: ops cash 2k, then reloan jewelry | sent 1k (10:39), Sent 2100 (12:53) | $3,100.00 |
| ROA — Roanoke | #roanoke-funds | Benjie: 2k deposit made | TYTY (no send) | $0.00 |
| WAY — Waynesboro | #boro-funds | Chadd: ops cash 2k | sent 2k | $2,000.00 |

Cancellations: none. ROA was a store deposit, not an ops-cash send. **Total expected: $6,600.00.**

## Step 2 — Bravo extraction
First trigger `daily-funds-verification-2026-07-03T18-05-49` (all 5): CUL & HAR succeeded, LEX errored (UIA 'Ok' not found) and the watcher hung; in-VM watchdog restarted the watcher at 18:11:11.
Retry `daily-funds-verification-retry1-2026-07-03T18-13-39` (LEX/ROA/WAY): LEX succeeded; ROA errored ('Business Date' not found); WAY errored ('window not found') — Bravo dropped to a bad state.
Health guard force-killed + relaunched Bravo (2 gate cycles) → PASS at 18:29:48.
Retry `daily-funds-verification-retry2-2026-07-03T18-29-56` (ROA/WAY): both succeeded. Final: success on 5/5 cells.

## Step 3 — Bravo signature rows (TENDER TRANSFER · BANK · Cash · negative leg)
| Store | Txn Num | Time | From→To | Amount |
|---|---|---|---|---|
| CUL | VP400062637 | 5:00 PM | BANK→SAFE | $1,500.00 |
| HAR | — | — | (no cash transfer) | $0.00 |
| LEX | VA100108954 | 11:17 AM | BANK→SAFE | $1,000.00 |
| LEX | VA100108962 | 1:20 PM | BANK→SAFE | $2,100.00 |
| ROA | — | — | (no BANK→SAFE; store made SAFE→BANK deposit) | $0.00 |
| WAY | VAP00072540 | 11:01 AM | BANK→SAFE | $2,000.00 |

## Step 5 — Reconciliation
| Store | Net expected (Slack) | Net actual (Bravo) | Status |
|---|---|---|---|
| CUL — Culpeper | $1,500.00 | $1,500.00 | ✓ Matched |
| HAR — Harrisonburg | $0.00 | $0.00 | ✓ Matched |
| LEX — Lexington | $3,100.00 | $3,100.00 | ✓ Matched |
| ROA — Roanoke | $0.00 | $0.00 | ✓ Matched |
| WAY — Waynesboro | $2,000.00 | $2,000.00 | ✓ Matched |
| **Total** | **$6,600.00** | **$6,600.00** | **ALL MATCHED (5/5)** |

**Slack post: made.**

_Report generated 2026-07-03 ~18:34 ET._

