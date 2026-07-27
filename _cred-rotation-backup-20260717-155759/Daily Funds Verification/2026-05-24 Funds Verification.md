# Daily Funds Verification — 2026-05-24 (Sunday)

**Bottom line:** No Slack funds activity today across any of the 5 stores ($0 net expected everywhere). Bravo verification could not run — the Bravo desktop app on the Windows VM is stuck pre-login and the watcher's `WaitForBravoReady` keeps timing out. **No financial risk today** since nothing was sent; the unblock is operational.

## Slack ledger

| Store | Channel | Requests | Sends | Cancellations | Net expected |
|---|---|---|---|---|---|
| CUL | #pepper-funds | — | — | — | $0 |
| HAR | #harrisonburg-funds | — | — | — | $0 |
| LEX | #lex-funds | — | — | — | $0 |
| ROA | #roanoke-funds | — | — | — | $0 |
| WAY | #boro-funds | — | — | — | $0 |

Zero messages in any funds channel since midnight local.

## Bravo Safe Register Journal

| Store | Status | Bravo total |
|---|---|---|
| CUL | ❓ Could not verify | — |
| HAR | ❓ Could not verify | — |
| LEX | ❓ Could not verify | — |
| ROA | ❓ Could not verify | — |
| WAY | ❓ Could not verify | — |

Pipeline error for all 5 stores (both at 18:07 ET and on retry next morning): `Bravo window not found/ready within 30s`.

## What I checked

- **Parallels Desktop:** running, VM `Windows 11` is up.
- **Watcher:** alive (it claimed and processed the trigger; result JSON written; ditto for this morning's weekly-loan-portfolio run at 07:12).
- **Bravo.exe state pre-relaunch:** running, PID 16652, Session 1, but `MainWindowTitle` was **empty** — stuck on a hidden splash/login/update dialog.
- **Relaunch attempt:** killed the stale Bravo and both duplicate AHK watchers, then re-ran `_relaunch_bravo_and_watcher.ps1` via `prlctl exec`. Second relaunch logged `WARN: Bravo not visible in tasklist yet (ClickOnce dfsvc may still be launching it)` — ClickOnce stalled and Bravo.exe never came back. The watcher (AHK PID 6396) is up and waiting on the next trigger.
- **UI access:** I couldn't drive the VM through the login/update dialog — the `request_access` approval timed out (you weren't at the desk).

## To unblock

Open the VM, click Bravo on the taskbar, dismiss whatever's hanging (likely an update prompt or login screen), and let it reach the normal `VALLEY PAWN -` title. Then drop a fresh trigger — the watcher's ready to pick it up. Or just let tomorrow's scheduled 6 PM run handle it.

## Trigger IDs (for log lookup)

- `daily-funds-verification-2026-05-24T18-00-00` (scheduled)
- `daily-funds-verification-2026-05-24T18-30-00-retry` (manual retry after watcher relaunch)
- `daily-funds-verification-2026-05-24-backfill-2026-05-25T18-10-00` (re-attempt on 2026-05-25 — see below)

## 2026-05-25 backfill attempt

Re-ran on 2026-05-25 at 18:10 ET to try and pull the Bravo CSVs for 05-24 now that some time had passed. Same outcome — **all 5 cells errored**, but with a *different* error pattern than the day-of run:

| Store | Error |
|---|---|
| CUL | BackToDashboard could not return Bravo to Dashboard |
| HAR | EnsureStore failed for HAR |
| LEX | EnsureStore failed for LEX |
| ROA | EnsureStore failed for ROA |
| WAY | EnsureStore failed for WAY |

So Bravo *is* now past the login/update screen, but it's stuck on a non-dashboard view — CUL fails to navigate back to Dashboard, then every downstream store-switch errors out. This is a different operational stuck-state, not a return to normal. Still no CSV data for 05-24.

**Net for 05-24:** Slack-side remains fully clear ($0 expected everywhere). Bravo-side remains unverifiable. No financial risk since the Slack ledger is empty.
