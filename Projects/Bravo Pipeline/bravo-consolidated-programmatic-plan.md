# Bravo → Slack: Consolidated Programmatic Plan

**Goal:** every scheduled task that depends on Bravo reliably extracts its data and publishes to Slack — **100% programmatically. No computer-use, no manual clicking, ever — including recovery.** Computer-use is banned from the task flow; it is only a last-resort human-diagnosis tool, not part of any task or recovery.

**What today proved (so this is grounded, not theory):**
- The pipeline already works for most cells when run programmatically: `safe-register-journal`, `loans-75-days-past-due`, `layaways`, `aged-inventory-summary`, `employee-activity`, `chekkit-inactives`, and `end-of-month` all produced clean CSVs via the watcher.
- The "hangs/sticking" I hit were **self-inflicted** (manual clicking + a bad Ctrl+W edit), not the handlers. Removed/reverted.
- 3 cells have **real** defects from clean runs: `items-to-price` (reads 43 of 176 — virtualization), `active-inv-details` (grid won't render), `company-kpis` (SSRS query error).

---

## The one architecture (every task, identical shape)

```
scheduled task  ──drops──>  trigger JSON  ──>  AHK watcher (in VM)  ──drives Bravo──>  CSV
                                                                                         │
scheduled task  <──reads CSV──  (file)  ──parses/formats──>  Slack post (API)  <─────────┘
```

- **One engine:** the AHK watcher in the Parallels VM. It is the ONLY thing that touches Bravo. Tasks never drive Bravo; they drop a trigger file and read a CSV file.
- **One trigger format:** `{ "reports": [ {"name": <cell>, "stores": [<codes>], "date": <date>} ] }`.
- **One output convention:** `<date>_<STORE>_<cell>.csv` in the pipeline output folder.
- **Slack:** each task reads its CSV(s) and posts via the Slack API. Zero computer-use.

## The 5 reliability rules every handler must follow (THE consolidation)

These are the levers that make extraction consistent. Bring every handler to this standard (additively, proven on the island first — never edit a working handler in place):

1. **Launch the watcher from `Y:\` (mapped drive), never `\\Mac\Home` (UNC).** UNC writes are 30× slower and time out. (`_restart_watcher.ps1` already maps Y: — make every restart path use it.)
2. **Toggle "Continuous Scrolling" OFF before exporting wide reports** (the closing/SSRS family) — the documented hang trigger. Opt-in per handler (EOM is sensitive — validate per store).
3. **Return cleanly to the Dashboard between cells.** A handler must leave Bravo on the Dashboard so the next cell starts clean; a leftover dialog/preview from one cell is the true cause of "cascade" failures.
4. **Programmatic login recovery.** When the watcher meets a login/store-select screen, it pastes the stored credential from config (`RecoverFromAutoLock`) — never a human, never typed.
5. **Prefer "read the grid" over "export" where the report is a list view** (grid-read, proven by `loans75-gridread`) — no export dialog means the hang cannot occur. Use export only for the SSRS closing reports.

## Programmatic recovery / self-healing (no human, no computer-use)

This is what makes it *consistent* day after day:

- **VM-side watchdog (PowerShell scheduled task):** every N minutes, detect a wedged Bravo (Not-Responding / stuck window title via `_bravo_titles.ps1` / `_diag_state.ps1`) or a trigger stalled in `claimed/` too long → automatically run `_relaunch_bravo_and_watcher.ps1` (force-kill Bravo, relaunch, watcher re-login). Pieces already exist: `_bravo_guard_watchdog.ps1`, `funds-verification-watchdog`.
- **Cowork-side watchdog:** each consumer task that posts to Slack has a paired watchdog (e.g. `funds-verification-watchdog`, `monthly-analytics-watchdog`) that re-runs the flow once if the post didn't land, silently. Standardize this pattern for every Bravo task.
- **No recovery ever uses computer-use.** All recovery = prlctl + PowerShell + trigger files.

## The 3 real defects to fix (island-first, additive)

| Cell | Symptom | Fix |
|---|---|---|
| `items-to-price` | reads 43 of 176 rows | grid-read with a correct scroll-accumulate (ScrollPattern to force row realization; stop on stable total). Reusable for any long grid. |
| `active-inv-details` | "grid did not render within 120s" | investigate render wait / store-specific; likely needs the same grid-read pattern. |
| `company-kpis` | SSRS "query execution failed (EmployeeNameDataSet)" | this is a Bravo/SSRS-side report error — reproduce, then either fix the saved report params or pull the KPI numbers from `end-of-month` CSVs instead. |

## Validation method (programmatic, per task)

1. **Shadow + reconcile:** drop the task's cell(s) across all 5 stores via the watcher; confirm every CSV lands and the numbers reconcile (e.g. row count == title count, $ column == summary total).
2. **Dry-run to a TEST Slack channel:** task reads the CSVs and posts its real-format message to a test channel; eyeball it.
3. **Cut over:** point the task at the real channel; run once on demand; watch it land.
4. **Watchdog on:** the paired watchdog guarantees the next scheduled run self-heals.

## Rollout order

1. **Harden the auto-recovery watchdog first** — so any wedge self-heals programmatically without me. This is the foundation of "consistent."
2. **Run each reliably-working task end-to-end to Slack, one at a time, all 5 stores:** funds → loan/layaway review → aged-inventory → employee rankings → chekkit → EOM-fed analytics. Each: shadow → test channel → cutover.
3. **Fix the 3 defective cells** on the island, deploy additively.
4. **Re-enable the parked weekly tasks + the Monday orchestrator** once their cells are all green.

## Definition of done

Every Bravo-dependent scheduled task: drops its trigger, gets its CSV, posts to its real Slack channel, and **self-heals on failure — with zero computer-use anywhere in the loop.**
