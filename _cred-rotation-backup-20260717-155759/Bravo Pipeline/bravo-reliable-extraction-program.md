# Bravo Reliable Extraction — Comprehensive Consolidation Program

**Owner:** Joshua Davis (Valley Pawn / Full Circle Finance Inc)
**Authored:** 2026-06-17 · **Status:** ✅ **Phase 0 PROVEN & LIVE (2026-06-17)** — grid-read works end-to-end via the watcher. Phases 1–4 are the sequenced rollout.

> ### ✅ Phase 0 result — 2026-06-17
> New cell **`loans75-gridread`** (handler `reports/Loans75GridRead.ahk`, registered additively in `bravo_watcher.ahk`) ran live on store WAY: **22 rows, 10 columns, `success`, ~45s, NO Export dialog, NO Continuous-Scrolling hang.** Output is a clean, properly-labeled CSV (`store,date,Ticket Number,Disposition,Disposition Date,Due Date,Pull Date,Customer,Loan Amount,Age,MobilePawn,SMS`) — the cell `.Name` metadata even supplies column headers, so grid-read output is *cleaner* than Bravo's own export. This validates the entire program: the #1 failure class (export hang) is eliminated for list-view reports. Proven path = clone handler → read `DataItem` rows → read each row's `Custom` cells (`.Value`, header from `.Name`) → write CSV → register additively in watcher → restart → trigger.
**Supersedes:** the scattered, per-handler one-off fixes. This is the single source of truth for how Valley Pawn gets data out of Bravo reliably.

---

## 0. Executive summary

Bravo has no API, no scheduled export, no web reporting portal, and its QuickBooks sync lacks the operational detail we need — so **automating the Bravo desktop app is the only way to extract our data.** For months the automation has been brittle because the same handful of failures kept recurring and each one was patched on a different handler at a different time, so no two tasks behave the same. This program does two things: (1) moves extraction off Bravo's hang-prone **Export** step to **reading report values directly off the screen** ("grid-read") wherever the report is a list-view grid, and (2) puts every handler and task on **one shared runtime standard** (one health-check, one restart, one patch profile, one watchdog). Built and proven on the island, deployed additively, daily tasks first.

---

## 1. Root cause — why Bravo extraction is unreliable

Five recurring failure classes, fixed unevenly across 61 handlers:

1. **Continuous-Scrolling export hang.** Bravo's "Enable Continuous Scrolling" toggle resets ON every Bravo restart; with it on, exporting a wide report flattens the preview into one canvas and the UI wedges 3+ min — CSV never writes. Fix (`TogglePattern.Toggle()`) is in only **9 of 61** handlers.
2. **Pre-login / ClickOnce stuck.** "Bravo window not found within 30s" / EnsureStore fails on all cells (took down funds verification 6/3–6/7).
3. **UNC vs Y: drive.** Watcher launched from `\\Mac\Home` makes CSV writes 30× slower → timeouts. Fixed only in `_restart_watcher.ps1`.
4. **Cascade poisoning.** One wedged cell kills the rest of the queue. Cascade-recovery is in the closing-9 handlers only (though now near-universal — see audit).
5. **No shared recovery.** Every task reinvents its own watchdog/heal/restart.

**The deeper cause:** there is no shared runtime standard. `monday-bravo-combined-run`'s preflight, `_restart_watcher.ps1`, the CS-toggle patch, and the cascade-recovery block are the *de facto* standard but are copied unevenly rather than shared.

---

## 2. What this session confirmed (decisions locked)

- **Vendor-native paths are out** (confirmed by Joshua): no Bravo API, no scheduled report email/SFTP, no separate web reporting portal; the QuickBooks sync does not carry loan/item/customer-level detail.
- **Private-channel replay is rejected:** replaying the desktop client's own cloud calls likely breaches Bravo's ToS/contract, is server-side detectable, and breaks on vendor updates. Off the table.
- **Desktop UI automation is the only door.** The question is only how to do it most reliably.
- **Grid-read is real, not a gamble:** the prod handler `Loans75DaysPastDue.ahk` ALREADY reads its values off the on-screen list (count from title bar, sum from summary panel) with **no export** — grid-read extends an existing, working, never-hangs pattern.
- **Handler audit (2026-06-17), 61 handlers:**
  - CS-toggle present in only **9** (the closing/GL family), all using the proven `TogglePattern.Toggle()`.
  - Cascade-recovery (`BackToDashboard`) present on **all consumer-wired** handlers (only the 2 diagnostics lack it).
  - File-wait timeouts inconsistent: most **180s**, an older cluster still **30s** (`AgedInventorySummary`, `EmployeeActivity`, `EndOfMonth`, `SafeRegisterJournal`, `SalesByVendor`) → can false-fail.
  - Empty-CSV thresholds all over the map (50 / 100 / 500 / 1000 / none).
  - **Conflict to resolve:** `EndOfMonth.ahk` *removed* its CS-toggle on 2026-06-07 because the toggle itself induced a hang — so the "proven fix" is NOT universally safe; it must be a profile a handler opts into, not a blanket apply.

---

## 3. Strategy

**Two extraction profiles, one standard each.**

- **Grid-read profile (preferred):** render the report as an on-screen list and read row/cell values from the UI Automation tree; write the CSV ourselves. **Never opens the Export dialog → the #1 hang cannot occur.** Applies to the list-view reports: loans, layaways, inventory lists, items-to-price, chekkit, intake, employee activity, KPI-style lists.
  - Known challenge: long grids virtualize (only on-screen rows exist in the tree) → scroll-and-accumulate.
- **Export profile (fallback, hardened):** for SSRS "closing" reports that only produce data via Export (EOM, Safe Register Journal, GL family), keep export but apply the unified hardening: `TogglePattern.Toggle()` CS-off **where it helps** (per the EOM conflict, opt-in), cascade-recovery, 180s wait, sane empty-CSV threshold.

Build the AHK in the **existing stack** (AutoHotkey + `lib/UIA-v2/UIA.ahk`, which already exposes the grid patterns). Do **not** re-platform to FlaUI/pywinauto unless AHK-UIA proves it cannot read a grid — that's the documented fallback, board reconvenes.

---

## 4. The shared Bravo runtime standard (the consolidation deliverable)

One canonical module every handler/task uses instead of its own copy:

| Component | Canonical source | Replaces |
|---|---|---|
| **Health-check / preflight** | `monday-bravo-combined-run` Step 0 (VM up, watcher alive, AutoLogin, last-started fresh, queue empty) | each task's bespoke preflight |
| **Watcher restart (Y:-aware) + pre-login recovery** | `_restart_watcher.ps1` (maps Y:, launches from Y: path, verifies) | ad-hoc restarts, the per-task heals |
| **Handler profile — grid-read** | new `lib` helper: render → enumerate `DataItem` rows → read cells → write CSV (no export) | export reliance on list-view reports |
| **Handler profile — export (hardened)** | the closing-9 pattern: CS-toggle opt-in + cascade + 180s + threshold | the uneven CS/timeout/threshold patches |
| **Watchdog** | one shared "did it post / did the CSV land; if not, self-heal once, silent" pattern | `funds-verification-watchdog`, `chekkit-watcher-heal`, `monthly-analytics-watchdog` copies |
| **Source of truth** | `bravo-pipeline-registry.md` (prod) + `island/island-registry.md` | drift |

---

## 5. Execution architecture — run via the WATCHER

**Critical finding (2026-06-17):** a *standalone* scheduled-task launch of a new AHK script does NOT work in this Parallels VM — the task runs but the script's code never executes (load-error dialog lands on the task's hidden window station; no heartbeat via Y: or UNC). Dead-ends proven and not to be repeated:
- `prlctl exec` direct → hangs (terminal grab).
- `cmd /c start /B` and `cmd /c "...AHK... > log"` → nested-quote eats the script arg / no run.
- `schtasks` direct-execute (even mirroring `_restart_watcher.ps1` + mapping Y:) → window-station isolation; invisible load dialog.

**Therefore: execute through the watcher + trigger mechanism** — the one thing that reliably drives Bravo here (it produced today's CSVs). It's resident in the live interactive session, so it has no window-station problem. New cells are registered **additively** (ADD `#Include` + ADD a `REPORT_HANDLERS[...]` line — never edit existing lines), watcher restarted via `_restart_watcher.ps1`, trigger dropped. Island is still where code is *written and reviewed*; the watcher is how it's *run*.

---

## 6. Phased migration plan

Each phase: build/clone on island → register additively → restart watcher → drop trigger → verify CSV matches prior output 3× → update registry → next.

- **Phase 0 — Prove grid-read (one cell).** `loans75-gridread` via the watcher: clone `Loans75DaysPastDue.ahk` → read FULL rows from the grid (not just count+sum), write CSV, no export. Current store only, no store-switch/password. Success = rows captured, matches the on-screen list, zero export interaction, 3×.
- **Phase 1 — Stabilize the live daily tasks.** Put the currently-enabled dailies (`daily-funds-verification`, `daily-intake-margin`/`-prestage`, `daily-items-to-price`) on the shared health-check + standard so they stop intermittently failing (the 6/3–6/10 pattern).
- **Phase 2 — Migrate list-view reports to grid-read.** Work the audit gap list: `loan-reviews`, `loans-75-days-past-due`, `layaways`, `fpd-cohort`, `fpd-lookback-12mo`, `aged-inventory-summary`, `active/sold-inv-details`, `employee-activity`, `company-kpis`, `chekkit-inactives`, `items-to-price`, `intake-detail`. Each becomes a hardened grid-read cell.
- **Phase 3 — Harden the export-only reports.** Apply the export profile to EOM, Safe Register Journal, GL family; **resolve the EOM CS-toggle conflict** (opt-in toggle, validated per store — ROA/WAY were the wedge cases). Standardize timeouts to 180s and thresholds.
- **Phase 4 — Turn the lights back on.** Re-enable the parked weekly consumers and the `monday-bravo-combined-run` orchestrator once their cells are on the standard.

---

## 7. Per-handler worklist (from the 2026-06-17 audit)

Targets = handlers wired to a real consumer that need work. Profile = where they land.

| Handler / cell | Consumer | Current gap | Target profile |
|---|---|---|---|
| loan-reviews, loans-75-days-past-due, low-dollar-loans, loan-portfolio-2026 | loan/layaway review, portfolio | no grid-read; mixed thresholds | grid-read |
| layaways, layaway-balance/deposits/journal | layaway review | no grid-read | grid-read |
| fpd-cohort, fpd-lookback-12mo | weekly-fpd-ranking | no grid-read | grid-read |
| aged-inventory-summary | aged-inventory report | 30s wait, no threshold | grid-read |
| active-inv-details, sold-inv-details, inventory-details | new-inv report | no grid-read | grid-read |
| employee-activity | employee rankings | 30s wait | grid-read |
| company-kpis | analytics, store-rankings | unique SSRS download path | grid-read or export-hardened (evaluate) |
| chekkit-inactives | chekkit campaigns | 50-byte threshold | grid-read |
| items-to-price | items-to-price | 100-byte threshold | grid-read |
| intake-detail | intake margin | most-iterated; no threshold | grid-read |
| end-of-month | GL, analytics, minutes | CS-toggle removed (hang); 30s wait | export-hardened (resolve CS conflict) |
| safe-register-journal | funds verification | 30s wait | export-hardened (already CS-patched) |
| GL family (sales-accounting, credit-*, settlements, cost-adjustment, etc.) | GL/QBO | no CS; mixed thresholds | export-hardened |
| LoanBase.ahk | loan composites | stray `Sleep(25000)` | clean up |

---

## 8. Verification & rollback

- **Verify per cell:** island/new CSV equals the prior export-based CSV for the same store/date (cell-for-cell on the columns that matter); 3× repeatability; zero "Continuous Scrolling" / Export-dialog interaction; completes under the wall timeout.
- **High-stakes cells** (funds, GL): verify with a parallel run against the existing handler before switching the consumer over.
- **Rollback:** everything additive; originals `.bak`'d; the registry tracks each cell's status; a consumer can be pointed back to the old cell instantly.

---

## 9. Cleanup carried from the 2026-06-17 session

- Unregister Windows scheduled tasks **`ClaudeIslandGridread`** and **`ClaudeIslandMapY`** (left registered; triggers 10 years out; benign).
- Remove the temp diagnostic heartbeat `FileAppend` lines from `island/source/Loans75_gridread_island.ahk` when porting to the watcher version.
- Island files staged this session: `Loans75_gridread_island.ahk`, `island_run.ps1`, `run_island.sh`, `read_island.sh`, `proof-of-concept/gridread-poc.md`.

---

## 10. First build session — exact steps (Phase 0)

1. Preflight + read both registries (prod + island).
2. Clone `reports/Loans75DaysPastDue.ahk` → `reports/Loans75GridRead.ahk`; keep `PullLoans75GridRead(store,date,outputDir)`; replace the count+sum read with a full-row grid harvest (`root.FindElements({Type:"DataItem"})` → per-row cell `.Name`/`.Value` → `WriteCsvRow`); **no** Export, **no** CS toggle. Handle virtualization (scroll-accumulate) if rows exceed one screen.
3. ADD `#Include reports\Loans75GridRead.ahk` and `REPORT_HANDLERS["loans75-gridread"] := PullLoans75GridRead` to `bravo_watcher.ahk` (ADD lines only).
4. `_restart_watcher.ps1`; confirm `loans75-gridread` in the handler list.
5. Drop a one-cell trigger `{ "reports":[{"name":"loans75-gridread","stores":["<current>"],"date":"<today>"}] }`.
6. Read the CSV; confirm rows match the on-screen list; 3×.
7. Update both registries. Proceed to Phase 1.
