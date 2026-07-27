# Island PoC — Grid-Read Extraction (skip Bravo's Export dialog)

**Decision date:** 2026-06-17 — board-approved.
**Goal:** eliminate the single biggest Bravo failure class — the Continuous-Scrolling / export-document hang — by reading report values straight off the rendered grid via UI Automation and writing the CSV ourselves, instead of clicking Bravo's "Export Document → Save as CSV."

---

## Why (grounding)

- Reliability audit (2026-06-17): the export path is where Bravo wedges. Continuous Scrolling re-paginates the whole report into one canvas; the UIA tree goes unreadable for 3+ minutes; the CSV never writes. CS-toggle exists in only **9 of 61** handlers, and `EndOfMonth.ahk` actually **removed** its CS-toggle on 2026-06-07 because the toggle *itself* induced the hang. File-wait timeouts (180s vs 30s) and empty-CSV thresholds (50/100/500/1000/none) are inconsistent across handlers — evidence the fixes were applied unevenly.
- Vendor-native alternatives confirmed unavailable by Joshua (2026-06-17): no Bravo API, no scheduled export, no web reporting portal, and the QuickBooks sync lacks the operational (loan/item/customer) detail we need.
- Private-channel replay (replaying the desktop client's own cloud calls) **rejected**: violates Bravo ToS/contract, server-side detectable, brittle on vendor updates. Off the table.
- Therefore desktop UI automation is the only door. The question is only *how* to read the screen most reliably.

## Hypothesis

Bravo's report grid is a WPF data grid whose cell values are exposed through the UI Automation tree (Grid/Table/Value patterns). The existing `lib/UIA-v2/UIA.ahk` already exposes these patterns (the handlers already use `TogglePattern`). If we read cells from the rendered grid and write the CSV ourselves, **the Export dialog is never opened — so the #1 hang trigger cannot occur.**

## Approach — AHK-first (reuse, don't rebuild)

Reuse the existing watcher, dispatch tables, `StoreCycle.ahk`, `Bravo.ahk` render/recovery primitives, and `lib/UIA-v2/UIA.ahk`. **Do not** re-platform to FlaUI/pywinauto unless AHK-UIA proves it cannot read the grid (that's the fallback, not the first move).

## Two-step proof (build + test on the island only; prod frozen)

**Step A — Mechanism check (narrow report).**
- Target: **Safe Register Journal** (already has an island clone; few rows; feeds daily-funds-verification).
- Build `SafeRegisterJournal_gridread_island.ahk`: render the report, read grid cells via UIA-v2, write CSV to `island/output/` with the prod naming + columns. **No Export dialog opened.**
- Pass criteria: island CSV matches the export-based CSV cell-for-cell for the same store/date; produced in <60s; repeatable 3×; zero "Continuous Scrolling" interaction.

**Step B — Virtualization check (wide report).**
- Target: **End of Month** — the canonical wide-render hang case (ROA/WAY currently wedge).
- Clone as `EndOfMonth_gridread_island.ahk`.
- Known challenge: WPF grids **virtualize** — only on-screen rows exist in the UIA tree. Must scroll-and-accumulate (ScrollPattern or paged `{PgDn}`, realize rows, dedupe) to capture every row *without* triggering the continuous-canvas render that hangs.
- Pass criteria: island EOM CSV equals the prod EOM CSV row-for-row for CUL (known-good), AND completes cleanly on ROA/WAY (the wedge stores); 3×.

## Decision gates

- Step A fails (cells not readable via UIA) → escalate to framework eval (FlaUI/C# has stronger WPF-grid support). Board reconvenes.
- Both steps pass → deploy per `ISLAND.md` checklist as **new** `*-gridread` cells (additive), and migrate consumers store-by-store, **daily tasks first** (funds, intake, items-to-price), then re-enable the parked weeklies.

## Live-run requirement (what's NOT doable off-VM)

Building and testing these handlers is iterative against **live Bravo in the Parallels VM** — it cannot be unit-tested from a Mac-only session. Execution needs: a Parallels/computer-use grant, the island watcher running in the VM, and `bravo-store-cycle` for login. This document is the staged plan; the build happens in a VM-enabled session.

## Live build log — 2026-06-17 (first build session)

**What got built + staged (all additive, prod untouched):**
- `island/source/Loans75_gridread_island.ahk` — Step A harvester. Targets the CURRENT store (no store-switch, no password → zero lockout risk). Renders "75 Days Past Due", reads grid rows via UIA (`FindElements({Type:"DataItem"})` + cell `.Name`/`.Value`), writes CSV. NEVER opens the export dialog. Includes a discovery dump of row[1] cell structure.
- `island/source/island_run.ps1` — launches the AHK via a one-shot Windows Scheduled Task as the interactive user `joshuadavis` (mirrors the proven `_restart_watcher.ps1` mechanism). Direct `prlctl exec` launches fail (terminal-grab) and don't get a UI session.
- `island/source/run_island.sh` / `read_island.sh` — Mac-side launch + readback via `prlctl`/osascript.

**Confirmed this session:**
- Concept is sound: prod `Loans75DaysPastDue.ahk` already reads count+sum off the UI with NO export — grid-read is an extension of an existing working pattern.
- Launch plumbing solved: the schtasks path runs a custom island AHK in the VM. `/ErrorStdOut` capture file came back EMPTY → the script COMPILES cleanly (the `#Include Y:\...` absolute paths resolve).
- Fixed a real bug: the harvester first derived its output dir as a relative `...\source\..\output`; on the mapped Y: drive that path silently fails `FileAppend` (LogMessage wraps writes in `try`), so the script ran but its log/CSV writes were discarded. Changed to an ABSOLUTE `Y:\...\island\output` path.

**Still open (where it stopped):**
- After the absolute-path fix, a re-run still produced no `loans75-gridread.log` and `ahk_stdout.log` did not refresh on the latest launch — points to a scheduled-task re-trigger / redirect nuance (task instance state, or the cmd `>` redirect under the task session), NOT the grid logic.
- KEY HANDICAP this session: the Cowork screenshot filter hides the Windows guest window (owned by a Parallels worker not in the app grant), so the Windows screen could not be visually inspected — blind debugging only.

**Fastest path to finish (next session):**
1. Run from a session that can SEE the VM screen (so an AHK dialog / Bravo state is visible), OR
2. Simplify the launcher to write a heartbeat line to an absolute file as its very first action (before any nav) to confirm execution, then iterate the harvest + cell selectors.
3. CLEANUP: a one-shot Windows Scheduled Task **`ClaudeIslandGridread`** was left registered by `island_run.ps1` (benign — trigger is 10 years out — but unregister it). Add `Unregister-ScheduledTask` to the ps1 tail like `_restart_watcher.ps1` does.

## Update 2 — 2026-06-17 (~11:35): standalone island launch is blocked by Windows session isolation

Tried every standalone launch variant to run the island AHK against live Bravo:
- `prlctl exec` direct (hangs — terminal grab), `cmd /c start /B` (no run), schtasks via `cmd /c` wrapper (nested-quote ate the script arg), schtasks **direct-execute** (mirrors the working `_restart_watcher.ps1`), with `-MultipleInstances Parallel`, prior-instance kill, AND the Y:-drive map step copied from `_restart_watcher.ps1`.
- Result every time: the scheduled task reports "running" but the script's `Main()` never executes — **no heartbeat via Y: OR via UNC `\\Mac\Home`** (UNC needs no drive mapping), no nav, and **no error dialog visible** on the interactive console.
- Conclusion: AutoHotkey is launching but failing to load/run in the **scheduled task's window station**, where any AHK load-error MsgBox is invisible to the interactive-console screenshot. This is a Windows session-isolation issue, NOT the grid-read logic. The watcher avoids this because it was launched once into the interactive session and stays resident.

**Recommended pivot (next session): run the grid-read handler through the WATCHER, not standalone.**
The watcher is the ONE mechanism that reliably runs AHK against Bravo in this VM (it produced today's CSVs). Additively (ADD lines only — permitted by the additive rule):
1. Copy `Loans75_gridread_island.ahk` → `reports/Loans75GridRead.ahk` (prod), strip the standalone bootstrap (`Main()/ExitApp()` + `#Include` block — the watcher provides those), keep `PullLoans75GridRead(store,date,outputDir)` as the entry, writing to a **dedicated `loans75-gridread` cell** so it never collides with the real `loans-75-days-past-due`.
2. ADD `#Include reports\Loans75GridRead.ahk` and a `REPORT_HANDLERS["loans75-gridread"] := PullLoans75GridRead` dispatch line.
3. Restart the watcher (`_restart_watcher.ps1`), drop a one-cell trigger for the current store, read the CSV. Pure read, no export, no store-switch.
This proves grid-read end-to-end using the proven runner, then the result feeds the consolidation.

**Cleanup left for next session (benign):** Windows scheduled tasks `ClaudeIslandGridread` and `ClaudeIslandMapY` were left registered (triggers 10 years out). Unregister them. Temp diagnostic heartbeat lines are still in `Loans75_gridread_island.ahk` (the two `FileAppend` heartbeat writes) — remove when porting to the watcher version.

## Status

🔨 In progress 2026-06-17. Concept proven from code; harvester + launch scaffolding built & staged. Standalone island execution blocked by Windows scheduled-task window-station isolation → pivot to the watcher-trigger mechanism (additive) next session. Prod untouched; no store-switch/password used; Bravo never navigated (script halts before nav — confirmed on screen, Bravo healthy on WAY Dashboard).
