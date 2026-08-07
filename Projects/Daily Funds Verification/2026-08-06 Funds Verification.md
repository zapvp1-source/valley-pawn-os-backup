# Daily Funds Verification — 2026-08-06

**Status: INCOMPLETE — see below.** Bravo could not reach a logged-in dashboard on the extraction VM even after a full guarded kill + relaunch escalation; only 1 of 5 stores has a usable CSV for today.

## Bottom line
Culpeper's cash-drawer CSV was captured earlier today (before the hang) and shows $0 in/out — matches the $0 expected. Harrisonburg, Lexington, Roanoke, and Waynesboro could not be pulled from Bravo within the time budget, so their reconciliation is incomplete.

## Step 1 — Slack ledger (today, 2026-08-06 ET)
| Store | Channel | Request(s) | Joshua's reply | Net expected |
|---|---|---|---|---|
| CUL — Culpeper | #pepper-funds | (none) | (none) | $0.00 |
| HAR — Harrisonburg | #harrisonburg-funds | Walker: "Ops cash need 2k" (16:09) | Joshua: "Sent 2k" (16:47) | $2,000.00 |
| LEX — Lexington | #lex-funds | Martin D. posted a photo (13:13), tagged Joshua/Preston (13:16); Joshua asked "did we get this done?" (15:40); Preston replied "Yes" (15:44) | No dollar figure stated in text — amount only visible in the attached image, which this run could not read | Unknown — flagged, not counted in totals |
| ROA — Roanoke | #roanoke-funds | (none) | (none) | $0.00 |
| WAY — Waynesboro | #boro-funds | (none) | (none) | $0.00 |

Cancellations: none observed. **Total expected (excluding LEX, unresolved): $2,000.00.**

## Step 2 — Bravo extraction
Background: the main 6 PM `daily-funds-verification` run had already tried 3 retries today, all aborted with "Skipped by safety rail: bravo-not-ready (could not reach a logged-in dashboard)" (see `results/daily-funds-verification-retry3-2026-08-06T18-05-14.result.json`).

This watchdog run:
1. Launched `bravo_ensure_healthy.sh` (backgrounded via nohup) at ~18:39 ET.
2. Guard escalated through Rung3 (window nudge, watcher consolidation) and Rung4/4b (recover-to-dashboard attempts, then a guarded force-kill + full relaunch of Bravo + watcher) — final result at 19:00:02: **FAIL no-dashboard after gentle recover + force-relaunch.**
3. Dropped a fresh trigger (`daily-funds-verification-watchdog-2026-08-06T19-00-30`) targeting all 5 stores anyway, in case the dashboard came up moments later. It was claimed by the watcher but had not produced a result by the time this run's budget ran out.

One earlier CSV from today (business date 8/6, printed 6:06 PM, before the hang set in) was already sitting in `output/2026-08-06_CUL_safe-register-journal.csv` — used for Culpeper below. No equivalent files exist yet for HAR, LEX, ROA, or WAY today.

## Step 3 — Bravo signature rows (TENDER TRANSFER · BANK · Cash · negative leg)
| Store | Txn Num | Time | From→To | Amount |
|---|---|---|---|---|
| CUL — Culpeper | — | — | (no cash TENDER TRANSFER to BANK today) | $0.00 |
| HAR — Harrisonburg | — | — | not pulled (no CSV) | — |
| LEX — Lexington | — | — | not pulled (no CSV) | — |
| ROA — Roanoke | — | — | not pulled (no CSV) | — |
| WAY — Waynesboro | — | — | not pulled (no CSV) | — |

## Step 5 — Reconciliation
| Store | Net expected (Slack) | Net actual (Bravo) | Status |
|---|---|---|---|
| CUL — Culpeper | $0.00 | $0.00 | ✓ Matched |
| HAR — Harrisonburg | $2,000.00 | — | ❓ Could not verify |
| LEX — Lexington | Unknown (image, no text amount) | — | ❓ Could not verify |
| ROA — Roanoke | $0.00 | — | ❓ Could not verify |
| WAY — Waynesboro | $0.00 | — | ❓ Could not verify |
| **Total** | **$2,000.00+ (LEX unresolved)** | **$0.00 confirmed** | **1/5 verified** |

**Slack post: skipped (not all 5 stores verified — per policy, only post when all 5 have a Matched/Discrepancy result).**

## For the next session
- Root cause looks deeper than a normal hang: even the guarded force-kill + full Bravo/watcher relaunch could not reach a logged-in dashboard (`FAIL no-dashboard`). Worth checking the Windows VM directly (screen state, ClickOnce prompt, credential/session issue) rather than retrying the same automated recovery again.
- A watchdog trigger (`daily-funds-verification-watchdog-2026-08-06T19-00-30`) is still claimed and may complete after this session ends — check `results/` for it before re-running.
- Lexington's request today came in as a photo with no dollar figure in the message text; if it needs to be included in tomorrow's or a corrected ledger, someone will need to open `F0BNJP8UD2N` (20260806_131313.jpg in #lex-funds) to read the amount.

_Report generated 2026-08-06 ~19:02 ET._
