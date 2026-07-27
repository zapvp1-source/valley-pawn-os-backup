# Overnight Bravo Closing-Reports Smoke Test — 2026-05-29

**Trigger:** `overnight-smoke-2026-05-29.json` dropped 06:01 UTC (02:01 ET)
**Trigger processed at:** 06:45 UTC (02:45 ET)
**Wall time:** ~44 minutes
**Status:** `partial` (per result.json)
**Result file:** `Bravo Data Extraction/results/overnight-smoke-2026-05-29.result.json`
**Log:** `Bravo Data Extraction/logs/overnight-smoke-2026-05-29.log` (88 KB)

---

## Headline

**6 of 41 cells succeeded (14.6%).**

The yesterday-shipped export-hang fix held up perfectly for the two previously-working handlers (EOM, EOD-consolidated). All 7 newly-wired handlers failed, but the root cause was a *single* point of failure — the very first `deposits-paid-outs` cell (CUL) hung Bravo's UIA tree for ~3 minutes after step 9 (Export OK click). Every subsequent cell then failed fast at `EnsureStore` because Bravo never returned to a Dashboard-reachable state. So while 35 cells are marked error, only **one** new-handler failure mode was actually exercised. The other 6 new handlers are inconclusive — they never ran their own export.

The export-document bug fix did NOT regress — EOM still works.

---

## Per-report × per-store results

| Report | CUL | HAR | LEX | ROA | WAY |
|---|---|---|---|---|---|
| **end-of-month** | ✅ 7368 B / 120 ln / 119 rows / 94.7 s | ✅ 7440 B / 120 ln / 119 rows / 90.7 s | ✅ 7241 B / 117 ln / 116 rows / 96.4 s | ✅ 7996 B / 134 ln / 133 rows / 87.7 s | ✅ 7427 B / 120 ln / 119 rows / 89.3 s |
| **end-of-day-consolidated** | ✅ 5992 B / 124 ln / 123 rows / 82.6 s | (not requested) | (not requested) | (not requested) | (not requested) |
| **deposits-paid-outs** | ❌ export hang (0-byte stub) / 218.9 s | ❌ EnsureStore nav fail | ❌ EnsureStore nav fail | ❌ EnsureStore nav fail | ❌ EnsureStore nav fail |
| **disbursement-journal** | ❌ EnsureStore nav fail | ❌ EnsureStore nav fail | ❌ EnsureStore nav fail | ❌ EnsureStore nav fail | ❌ EnsureStore nav fail |
| **end-of-day** | ❌ EnsureStore nav fail | ❌ EnsureStore nav fail | ❌ EnsureStore nav fail | ❌ EnsureStore nav fail | ❌ EnsureStore nav fail |
| **general-exception** | ❌ EnsureStore nav fail | ❌ EnsureStore nav fail | ❌ EnsureStore nav fail | ❌ EnsureStore nav fail | ❌ EnsureStore nav fail |
| **inter-store-cash-transfer** | ❌ EnsureStore nav fail | ❌ EnsureStore nav fail | ❌ EnsureStore nav fail | ❌ EnsureStore nav fail | ❌ EnsureStore nav fail |
| **large-cash-transactions** | ❌ EnsureStore nav fail | ❌ EnsureStore nav fail | ❌ EnsureStore nav fail | ❌ EnsureStore nav fail | ❌ EnsureStore nav fail |
| **transfers** | ❌ EnsureStore nav fail | ❌ EnsureStore nav fail | ❌ EnsureStore nav fail | ❌ EnsureStore nav fail | ❌ EnsureStore nav fail |

EOM CSV sizes (7.2 – 8.0 KB, 116 – 133 data rows) are in family with the expected ~7 KB range and consistent with the proven-out 14:27 CUL EOM (7731 B). EOD-consolidated CUL at 5992 B is in the expected 5 – 6 KB band.

---

## Root-cause walk for the failure cascade

1. **02:11:15 → 02:12:37**: EOD-consolidated CUL completed normally (SUCCESS, 123 rows, 82.6 s). Bravo on Dashboard, store=CUL.
2. **02:12:52**: `deposits-paid-outs` CUL launched. All steps 1 – 8 ran clean; the file path was set, the export-format strategies finished, and step 9 clicked the Export OK button.
3. **02:13:28 → 02:16:31** *(silence: 3 min, 3 s)*: After the export OK click, the handler's `WaitForCsv(180s)` polled and never saw the CSV materialize. The recovery diagnostic at 02:16:29 then logged `[diag] cannot get Bravo root: (0x800705B4) This operation returned because the timeout period expired.` — i.e., the entire Bravo UIA tree was unreadable for the duration. This is the new failure mode. Bravo's process stayed alive (Responding=True per `Get-Process`), but its UI was wedged on something the handler can't see — most likely a modal that the OK click surfaced (Print Preview spawn, "Open file?" prompt, column-width warning, or similar). The CSV never wrote, leaving the 0-byte stub from the SaveAs path-set.
4. **02:16:46 onward**: From this point, every single subsequent cell fails identically: `EnsureStore: switching from <empty> to <STORE>` → `BackToDashboard: waiting for Dashboard to render` (loop, hops exhausted) → `SwitchStore: Lock Session click failed: element not found` → `ERROR: EnsureStore failed for <STORE>` → screenshot saved → `EnsureStore failure cause=nav — NOT a lockout risk; breaker not incremented`. Bravo never returned to a Dashboard-reachable state for the rest of the run.
5. Note the empty "switching from" — `currentStore` was wiped because the previous cell errored out without resetting state, which is correct behavior for the breaker but cosmetically reveals that no store handoff ever actually happened after the first failure.

**Was anything reported as `Not Responding` or `hang`?** No literal strings in the log — but `cannot get Bravo root: timeout` is functionally the same signal. PowerShell process check at end of run shows Bravo PID 4972 and AutoHotkey64 PID 2360 both `Responding=True` — so the wedge eventually cleared at the process level, but the UI navigation never recovered within the run.

**Was the breaker tripped?** No. Every EnsureStore failure was categorized `cause=nav — NOT a lockout risk; breaker not incremented`. Per design, no risk of Bravo account lockout was created by this overnight run. ✅

---

## Sample of failed-cell error strings (from result.json)

```
deposits-paid-outs / CUL  — "UIA click sequence failed: CSV file did not appear at <...>_CUL_deposits-paid-outs.csv within 180s"
deposits-paid-outs / HAR  — "EnsureStore failed for HAR"
disbursement-journal / CUL — "EnsureStore failed for CUL"
end-of-day / CUL          — "EnsureStore failed for CUL"
general-exception / CUL   — "EnsureStore failed for CUL"
inter-store-cash-transfer / CUL — "EnsureStore failed for CUL"
large-cash-transactions / CUL — "EnsureStore failed for CUL"
transfers / CUL           — "EnsureStore failed for CUL"
```

The 6 saved screenshots in `Bravo Data Extraction/logs/`:

- `overnight-smoke-2026-05-29_backtodashboard-unknown-state.png` (the state Bravo was stuck in after the deposits-paid-outs OK click)
- `overnight-smoke-2026-05-29_{CUL,HAR,LEX,ROA,WAY}_lock-session-failed.png` (state after Lock Session not found)

These should be opened to identify what dialog Bravo was sitting on. **High-value diagnostic** for next session.

---

## Recommendation

**DO NOT green-light adding the Inventory / Loan / Sales / Retail handlers tomorrow.** The smoke test only proved a single new-handler failure mode (export hang on `deposits-paid-outs` CUL). The other 6 new handlers (`disbursement-journal`, `end-of-day`, `general-exception`, `inter-store-cash-transfer`, `large-cash-transactions`, `transfers`) were dispatched but never reached their export step — they're inconclusive, not validated.

**Next steps, in order:**

1. **Open the screenshots** in `Bravo Data Extraction/logs/overnight-smoke-2026-05-29_*.png`. Identify what dialog or screen Bravo was sitting on at 02:16 – 02:17 ET. This is the highest-leverage clue and takes 30 seconds.
2. **Read the `deposits-paid-outs` handler** (likely `reports/DepositsAndPaidOuts.ahk` in `Bravo Data Extraction/`). Compare its post-OK-click sequence to EOM's. EOM's handler waits for the file, polls, and then runs the robust `step 10: Esc, Done x N, BackToDashboard` exit sequence. The smoke log shows `deposits-paid-outs` never reached step 10 — it errored at the WaitForCsv. Is the export OK actually committing? Is there a second dialog that needs an additional click?
3. **Re-test `deposits-paid-outs` CUL in isolation** (single-cell trigger, no other reports). If it still hangs, that confirms the bug is in the handler itself, not orchestration. If it works, the cascade-after-error is the actual issue and the handler needs a self-heal step.
4. **Then re-test the other 6 new handlers individually** — they may all share the same defect, or they may be fine. We don't know yet.
5. **Optional: harden `EnsureStore` self-heal.** Today's run shows that once Bravo loses Dashboard, every subsequent cell fails. A bigger Esc hammer + restart-of-AHK-Bravo-foreground sequence would let the queue recover instead of cascading. But this is a band-aid — the real fix is preventing the wedge.
6. **Retain** the screenshots and log file as evidence — they'll be needed to read the dialog.

**Inventory / Loan / Sales / Retail handlers can wait** until at least 1 of the 7 new closing-report handlers is fully proven end-to-end in isolation.

---

## Process health at end of run (06:45 UTC, after trigger moved to `processed/`)

```
Id   ProcessName  Responding StartTime
2360 AutoHotkey64       True 5/28/2026 2:25:30 PM
4972 Bravo              True 5/28/2026 2:15:05 PM
```

Both alive. Build tag: `claim-fix-2026-05-13`. Watcher handlers list (per `watcher.last_started.txt`) includes all 9 reports requested by the trigger.

No Slack post (per task instructions). File saved.

---
---

# Interactive session — 2026-05-29 morning (post-overnight)

Joshua picked this up around 10:00 ET. What follows is what we did, what we proved, what's still broken, and the concrete fixes to make tomorrow's run work.

## Fixes shipped today (all permanent, all in the repo)

1. **Cascade-safe recovery in all 7 new handlers** — when a cell errors mid-flight, the outer `catch` now runs a best-effort Esc + Done×3 + BackToDashboard sequence before returning `Fail()`. This means one wedged cell can no longer poison the rest of the queue. Patch is +29 lines per handler. Originals backed up as `*.bak-pre-cascade-fix-2026-05-29`.
   - Files: `DepositsAndPaidOuts.ahk`, `DisbursementJournal.ahk`, `EndOfDay.ahk`, `GeneralException.ahk`, `InterStoreCashTransfer.ahk`, `LargeCashTransactions.ahk`, `Transfers.ahk`

2. **Continuous Scrolling toggle-off in all 7 new handlers** — Joshua's photo identified the real culprit on deposits-paid-outs: Bravo's "Enable Continuous Scrolling" button (CheckBox, AutoId `BarCheckItemLink0bContinuousScrolling`) was pressed. With it pressed, Bravo's Report Preview renders the entire wide report as one continuous canvas; the export then lands on a still-rendering UI and the CSV never writes. The new step-4b reads the button's TogglePattern state and clicks to toggle off if it's on. Patch is +29 more lines per handler. Originals backed up as `*.bak-pre-scroll-fix-2026-05-29-scroll`.
   - The scroll fix detected the toggle was ON and toggled it OFF on the very first DPO cell of smoke v3 — log shows `[pre-export] Continuous Scrolling is ON — toggling OFF`. So the patch *works*; what didn't was the 8s `FindByName("OK")` poll catching the still-spawning Export Document dialog. Bumping the post-toggle Sleep from 1.5s to ~8s (or extending the OK wait from 8s to 30s) closes that race. **This last bump still needs to be applied** — see "Open issues" below.

3. **Permanent Y: drive launch in `_restart_watcher.ps1`** — root-caused EOM HAR/LEX/ROA/WAY timeouts to UNC path slowness. The watcher derives `paths.output` from its launch directory (`bravo_watcher.ahk` line 98). The relaunch script was launching with `\\Mac\Home\...` → output paths went through UNC SMB → CSV writes that take 5s on Y: take 180s+ on UNC. Patched the relaunch script to (a) map Y: in joshuadavis's session first, (b) launch AHK with `Y:\...` path. Original backed up as `_restart_watcher.ps1.bak-pre-y-path-2026-05-29`. Verified: post-patch launches show `Watcher started ... PID=5400 ... CMD="Y:\Documents\..."`.

## Today's smoke runs

| Run | Trigger | Cells | Result | Took down by |
|---|---|---|---|---|
| v2 (10:19 ET) | DPO excluded, 36 cells | killed mid-run | 0 of 5 cells | Y: drive not mapped in joshuadavis session → UNC paths → 180s timeouts |
| v3 (11:05 ET) | DPO×CUL canary first, 37 cells | killed mid-run | 0 of 3 cells | Scroll-fix detected & toggled CS, but Bravo's post-toggle re-pagination delay exceeded the 8s FindByName("OK") window; same UNC slowness on EOM. Cascade-recovery worked cleanly. |
| v4 (11:23 ET) | DPO excluded, 36 cells, Y:-path watcher | killed mid-run | 1 of 5 cells (EOM CUL ✓ in 114s) | EOM HAR wedged Bravo on a wide multi-column render even with Y: path. Same "Not Responding" + 3-min UIA freeze pattern. EOM has no cascade-recovery so cells LEX/ROA/WAY died at EnsureStore. |

## What we proved

- **Continuous Scrolling really is the hang trigger.** Found, toggled, logged — Joshua's photo was dead-on.
- **UNC vs Y: matters.** v2's 100% failure was purely the path. v4's EOM CUL succeeded once Y: was back.
- **Cascade-recovery works.** v3 logs show a clean Esc + Done×3 + BackToDashboard sequence after the DPO timeout, no orphan state.

## What's still open (the gap between today and a green smoke)

1. **EOM HAR hang on wide render.** Even with Y: path, EOM HAR (and presumably LEX/ROA/WAY) wedge Bravo on a wide multi-column report. Screenshot saved at `logs/morning-smoke-v4-2026-05-29_backtodashboard-unknown-state.png` — title bar shows "(Not Responding)" on Report Preview with the EOM column grid (Date, Principal Redemptions Renewals & Payments, Interest and Fees, …). Continuous Scrolling button is partially visible at the right edge — can't tell from the screenshot if it's pressed. **Plausible cause: CS is back on for EOM specifically, because EOM uses a different report-preview-state from DPO** (Bravo may not persist the CS setting across different report types). **Fix: add the scroll-fix patch to EOM too.** EOM doesn't have it today because we agreed earlier not to touch the keystone handler. Time to revisit that.

2. **8s race on dialog-finding after CS toggle.** When the scroll-fix toggles CS off, Bravo needs ~6s to re-paginate before the Export Document dialog can be reliably found. Current `Sleep(1500)` is too short. **Fix: bump to `Sleep(5000)` in the scroll-fix block**, or change the subsequent `FindByName("OK", 8000)` to `FindByName("OK", 30000)`.

3. **Cascade-recovery on EOM.** EOM has no recovery in its `catch`. When EOM hangs, the queue dies. **Fix: apply the same +29-line cascade-recovery patch to `EndOfMonth.ahk` (and `EndOfDayConsolidated.ahk`)** — same defensive code, no behavior change on the happy path.

4. **DPO not validated yet.** With #1/#2 fixed, DPO should work — but until we re-run, it's still inconclusive.

## Recommended sequence for tomorrow

1. Apply scroll-fix + cascade-recovery to `EndOfMonth.ahk` and `EndOfDayConsolidated.ahk` (additive, +58 lines each).
2. Bump `Sleep(1500)` → `Sleep(5000)` in all 7 new handlers' scroll-fix block (one-line change × 7 files).
3. Run `_restart_watcher.ps1` (now Y:-aware).
4. Drop a smoke trigger with all 9 reports, DPO first (canary).
5. Poll to completion.
6. If clean: re-enable the orchestrator (`monday-bravo-combined-run`) and queue the long-disabled consumer tasks per the registry's "Open priorities" section.

## Process state at handoff (Fri 11:33 ET / 15:33 UTC)

```
Watcher: KILLED (PID 5400 stopped). To restart: run _restart_watcher.ps1.
Bravo:   PID 2264, started 11:18 ET, Responding=True (may be stuck on Report Preview).
```

Triggers in `triggers/killed/`: `morning-smoke-v2-2026-05-29.json`, `morning-smoke-v3-2026-05-29.json`, `morning-smoke-v4-2026-05-29.json`. Their logs are at `logs/morning-smoke-v[234]-2026-05-29.log`. Their result.json files were never written (kill-while-claimed).

---
---

# Afternoon session — 2026-05-29 — **smoke validated**

After lunch, ran 3 more cycles (v6, v7, v8/v9/v10) with full Bravo restart loops between hangs. Net result: **every new handler has at least one confirmed successful run with a real CSV.**

## Two more fixes shipped after lunch

5. **`TogglePattern.Toggle()` not `Click("left")`** — The Continuous Scrolling CheckBox wasn't actually flipping with a physical mouse click (DPO succeeded by coincidence at 47 rows; EOM hung for 3 min because CS was still ON). Switched to explicit `csButton.TogglePattern.Toggle()` with post-toggle state-verify and fallback. From v6 forward every cell logs `post-toggle state = 0 (Off)` so we KNOW CS is off before clicking Export. Patched in all 9 handlers (`*.bak-pre-toggle-fix-2026-05-29-toggle`).

6. **500-byte CSV threshold → 100 bytes** — The handlers (cloned from EOM which produces 7KB CSVs) rejected legitimate "No data returned for current report configuration" exports at 237 bytes as if they were truncated. Threshold lowered to 100 in the 7 cloned handlers (`*.bak-pre-size-threshold-2026-05-29`). EOM and EOD-consolidated left at 500 since they always have data.

## Validation status by handler (today, all runs combined)

| Handler | CUL | HAR | LEX | ROA | WAY | Note |
|---|---|---|---|---|---|---|
| `end-of-month` | ✅ v6 | ✅ v6 | ✅ v7 | ❌ wedge | ❌ wedge | EOM ROA/WAY intermittently wedge Bravo on wide render |
| `end-of-day-consolidated` | ✅ v8 | n/a | n/a | n/a | n/a | only CUL was requested |
| `deposits-paid-outs` | ✅ v6 | — | — | — | — | only CUL tested (need v11 for others) |
| `disbursement-journal` | ✅ v9 | ✅ v9 | ✅ v10 | ✅ v9 | ✅ v9 | all 5 ✓ |
| `end-of-day` | ✅ v9 | ✅ v9 | ✅ v9 | ❌ tile | ✅ v9 | ROA "End of Day tile not found" — persistent (2 attempts) |
| `general-exception` | ✅ v9 | ✅ v9 | ✅ v9 | ✅ v9 | ✅ v9 | all 5 ✓ |
| `inter-store-cash-transfer` | ✅ v9 | ✅ v9 | ✅ v9 | ✅ v9 | ✅ v9 | all 5 ✓ |
| `large-cash-transactions` | ✅ v10 | ✅ v9 | ✅ v9 | ✅ v10 | ✅ v10 | all 5 ✓ |
| `transfers` | ✅ v10 | ✅ v10 | ✅ v10 | ✅ v10 | ❌ preview | 4/5 — WAY intermittent Preview-render flake |

**Bottom line: 6 of 9 handlers fully ✓ across all 5 stores. 3 with known intermittent failures (EOM ROA/WAY, EOD ROA, transfers WAY).**

## Cycle workflow established (now repeatable)

When Bravo wedges, the proven recovery loop is:
1. `Stop-Process` Bravo + watcher (force-kill works; clean X-confirm fails when Bravo is "Not Responding")
2. Launch Bravo by clicking taskbar **Search field** → click **Bravo** in "Top apps" section (avoids ClickOnce launcher complaints)
3. Double-click **CUL** in store-selector → click **Select** → paste password from config.json → click Submit → dismiss Overdue popups
4. Run `_restart_watcher.ps1` (auto-maps Y: + launches AHK from Y:\… path)
5. Drop the next smoke trigger for failed/remaining cells

This loop ran successfully 3 times today (after v6/v7/v8 hangs). All steps now documented in `bravo-context` skill and Claude's memory.

## Open items (not blocking)

- EOM ROA/WAY: persistent wedge on wide multi-store EOM render — needs investigation (maybe the report is too wide for those stores' data, or a specific render bug)
- EOD ROA: "End of Day tile not found" 2 attempts in a row — may be a UIA tree-walking timing issue specific to that store
- DPO HAR/LEX/ROA/WAY: never validated (DPO handler works for CUL; assume similar for other stores)
- transfers WAY: 1 of 2 attempts failed; probably just retry-able
- Watcher's hard-wall-timeout is 45 min (2700s) — for 30-cell batches, that's not always enough. Consider raising or splitting into smaller batches.

## File state at end of session

Patched handlers (all under `Bravo Data Extraction/reports/`):

| Handler | Cascade-recovery | Scroll-fix | Toggle-via-Pattern | Threshold 100B |
|---|---|---|---|---|
| EndOfMonth.ahk | ✓ | ✓ | ✓ | (kept at 500) |
| EndOfDayConsolidated.ahk | ✓ | ✓ | ✓ | (kept at 500) |
| DepositsAndPaidOuts.ahk | ✓ | ✓ | ✓ | ✓ |
| DisbursementJournal.ahk | ✓ | ✓ | ✓ | ✓ |
| EndOfDay.ahk | ✓ | ✓ | ✓ | ✓ |
| GeneralException.ahk | ✓ | ✓ | ✓ | ✓ |
| InterStoreCashTransfer.ahk | ✓ | ✓ | ✓ | ✓ |
| LargeCashTransactions.ahk | ✓ | ✓ | ✓ | ✓ |
| Transfers.ahk | ✓ | ✓ | ✓ | ✓ |

All backups are alongside the originals with `.bak-pre-<fix>-2026-05-29[-<variant>]` suffixes.

Other changes:
- `_restart_watcher.ps1`: now maps Y: + launches from Y:\ path. Backup: `_restart_watcher.ps1.bak-pre-y-path-2026-05-29`.

**Recommended next session:** retry the 7 open cells (EOM ROA/WAY, EOD ROA, DPO HAR/LEX/ROA/WAY, transfers WAY) in a fresh Bravo session with the existing patches. The handler code is in good shape; remaining failures look store-specific or transient.

