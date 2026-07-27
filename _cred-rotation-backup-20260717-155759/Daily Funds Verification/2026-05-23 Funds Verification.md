# Daily Funds Verification — 2026-05-23

**Bottom line: ❓ Could not verify any store — Bravo pipeline aborted.**

The Bravo Data Extraction watcher failed `EnsureStore` on the first three stores (CUL, HAR, LEX) in a row, which tripped the auth-failure circuit breaker and skipped the remaining two (ROA, WAY) to prevent a lockout. Zero CSVs were produced. Joshua needs to restart the watcher on the Windows VM.

## Slack ledger (what Joshua said he sent today)

| Store | Channel | Amount sent | Time | Notes |
|---|---|---|---|---|
| CUL (Culpeper) | #pepper-funds | $2,000 | 17:01 | Sandi requested $2,000 at 16:55, Joshua replied "Sent 2k" |
| LEX (Lexington) | #lex-funds | $0 | — | No activity |
| WAY (Waynesboro) | #boro-funds | $2,000 | 10:29 | Chadd needed 2k, Joshua replied "Sent 2k" |
| ROA (Roanoke) | #roanoke-funds | $1,000 | 16:20 | Benjie needed $1,000, Joshua replied "Sent 1k" |
| HAR (Harrisonburg) | #harrisonburg-funds | $3,000 | 10:14 + 14:44 | Walker needed 2k → "Sent 2k"; Andrew needed 1k → "Sent 1k" |
| **Total expected** | | **$8,000** | | |

## Bravo reconciliation

| Store | Expected | Bravo Safe Total | Status |
|---|---|---|---|
| CUL | $2,000 | — | ❓ Could not verify (EnsureStore failed) |
| HAR | $3,000 | — | ❓ Could not verify (EnsureStore failed) |
| LEX | $0 | — | ❓ Could not verify (EnsureStore failed) |
| ROA | $1,000 | — | ❓ Could not verify (skipped by circuit breaker) |
| WAY | $2,000 | — | ❓ Could not verify (skipped by circuit breaker) |

## Pipeline failure detail

- Trigger: `daily-funds-verification-2026-05-23T18-04-12`
- Started: 2026-05-23 18:06:02 → Finished: 2026-05-23 18:06:02
- Status: `aborted`
- CUL: `EnsureStore failed for CUL` (25.2s)
- HAR: `EnsureStore failed for HAR` (25.2s)
- LEX: `EnsureStore failed for LEX` (25.1s)
- ROA: skipped — `auth-failure circuit breaker (3 consecutive EnsureStore failures - possible lockout, stopping to prevent more bad logins)`
- WAY: same skip reason

## Next steps for Joshua

1. Restart the Bravo watcher on the Windows VM (run `restart_watcher.bat`).
2. Verify Bravo credentials still work — three consecutive EnsureStore failures suggest either a stuck UI state, a password issue, or the StoreCycle post-dblclick timeout being too thin.
3. Once the watcher is healthy, manually re-trigger the verification or wait for tomorrow's run.
