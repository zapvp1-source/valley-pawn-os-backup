# Daily Funds Verification — 2026-06-16

**Status: INCOMPLETE — Bravo could not be read. 5/5 cells failed with "Bravo window not found/ready"; no store verified.**

## Bottom line
$5,500.00 expected across all 5 stores (CUL $1,500 + HAR $2,000 + LEX $2,000). The Bravo Safe Register Journal could not be extracted: the Bravo POS window in the VM never reached a ready/detectable state, so no actual figures are available. Per the standing failure policy, nothing was posted to Slack and no DM was sent. This file is the audit record.

## Step 1 — Slack ledger (today, 2026-06-16 ET)
| Store | Channel | Request(s) | Joshua's reply | Net expected |
|---|---|---|---|---|
| CUL — Culpeper | #pepper-funds | Sandi Cole: "Ops cash needed \$1500" (16:21) | "Set 1500" (16:38) | \$1,500.00 |
| HAR — Harrisonburg | #harrisonburg-funds | Walker Tapley: "Ops cash need 2k" (09:30) | "sent 2k" (09:55) | \$2,000.00 |
| LEX — Lexington | #lex-funds | Uriah: "ops cash need 2k" (09:31) | "sent 2k" (11:15) | \$2,000.00 |
| ROA — Roanoke | #roanoke-funds | (no activity) | — | \$0.00 |
| WAY — Waynesboro | #boro-funds | (no activity) | — | \$0.00 |

Cancellations: none. **Total expected: \$5,500.00.**

## Step 2 — Bravo extraction
Three triggers dropped against safe-register-journal (date=2026-06-16, stores CUL/HAR/LEX/ROA/WAY):
- watchdog-funds-verification-2026-06-16T18-48-05 → status partial, 5/5 cells error "Bravo window not found/ready within 30s".
- watchdog-funds-verification-retry-2026-06-17T10-02-30 → claimed by a stale UNC-path watcher, hung.
- watchdog-funds-verification-retry2-2026-06-17T10-07-45 → 5/5 cells error "Bravo window not found/ready within 30s".

Recovery performed: ran _relaunch_bravo_and_watcher.ps1 (Bravo + watcher came up, 3 Bravo PIDs in Session 1); ran _restart_watcher.ps1 to kill a duplicate UNC-path watcher and leave a single Y:-path watcher (PID 5448, started 2026-06-17 10:06:54); ran _kick_dismiss_ad.ps1 to clear the startup ad. Despite Bravo processes being up, the watcher's window-ready check failed on every cell across ~10 minutes of retries — the window never reached a detectable ready state (consistent with Bravo sitting at a login/intermediate screen that unattended automation could not clear). The 6 PM main run (daily-funds-verification-2026-06-16T18-04-02) hit the same failure (overall status: partial, all cells window-not-ready).

## Step 3 — Bravo signature rows (TENDER TRANSFER · BANK · Cash · negative leg)
| Store | Txn Num | Time | From→To | Amount |
|---|---|---|---|---|
| CUL — Culpeper | (no CSV — Bravo unavailable) | — | — | — |
| HAR — Harrisonburg | (no CSV — Bravo unavailable) | — | — | — |
| LEX — Lexington | (no CSV — Bravo unavailable) | — | — | — |
| ROA — Roanoke | (no CSV — Bravo unavailable) | — | — | — |
| WAY — Waynesboro | (no CSV — Bravo unavailable) | — | — | — |

## Step 5 — Reconciliation
| Store | Net expected (Slack) | Net actual (Bravo) | Status |
|---|---|---|---|
| CUL — Culpeper | \$1,500.00 | — | ❓ Could not verify |
| HAR — Harrisonburg | \$2,000.00 | — | ❓ Could not verify |
| LEX — Lexington | \$2,000.00 | — | ❓ Could not verify |
| ROA — Roanoke | \$0.00 | — | ❓ Could not verify |
| WAY — Waynesboro | \$0.00 | — | ❓ Could not verify |
| **Total** | **\$5,500.00** | **—** | **0/5 verified — Bravo window unavailable** |

**Slack post: skipped — failure policy prohibits posting on a non-success run (no store verified). No DM sent.**

_Report generated 2026-06-17 ~10:12 ET (watchdog re-run of the 6 PM verification; Bravo window remained unavailable through all recovery attempts)._

