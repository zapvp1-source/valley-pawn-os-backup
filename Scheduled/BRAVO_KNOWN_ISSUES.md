# Bravo Data Extraction — KNOWN ISSUES (READ THIS FIRST)

## 🚫 SIGN INTO / RECOVER BRAVO WITHOUT PARALLELS — DO THIS, every time

If any Bravo pull stalls — trigger sits in `triggers/` or `triggers/claimed/` >2 min unprocessed, an all-cells-error result, or no output CSV after the expected time — Bravo is wedged or sitting at a login screen. **Recover it PROGRAMMATICALLY. Do NOT request Parallels access, do NOT drive the Parallels GUI with computer-use, do NOT ask Joshua to sign in.** The entire pipeline is "no Parallels grant required" by design.

**The mechanism (canonical — used by `daily-funds-verification`, `monday-bravo-combined-run`, `funds-verification-watchdog`):**
`prlctl exec` HANGS from an interactive osascript session but runs cleanly from a **scheduled-task session**. So fire a ONE-SHOT scheduled task (`mcp__scheduled-tasks__create_scheduled_task`, `fireAt` ≈ 60 s from now, taskId like `bravo-recover-oneshot-<timestamp>`) whose prompt runs ONE of:

- **Watcher only** (watcher hung/dead, Bravo still logged in on a Dashboard):
  `osascript do shell script "/usr/local/bin/prlctl exec '{7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}' --current-user powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'Y:\Documents\Claude\Projects\Bravo Data Extraction\_restart_watcher.ps1'"`

- **Full relaunch** (Bravo at a login screen, or not running — this launches Bravo via the `.appref-ms` shortcut + `BravoAutoLogin` AND restarts the watcher):
  `osascript do shell script "/usr/local/bin/prlctl exec '{7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}' --current-user powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'Y:\Documents\Claude\Projects\Bravo Data Extraction\_relaunch_bravo_and_watcher.ps1'"`

**Then:** wait ~90 s; confirm recovery with
`prlctl exec '{7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}' --current-user tasklist /v /fi "IMAGENAME eq Bravo.exe" /fo list` → `Status: Running` (not "Not Responding"), and `logs/watcher.last_started.txt` timestamp advanced. Then re-drop your trigger and resume polling.

**Rule for every Bravo-touching task/session:** stalled pipeline → fire the one-shot recovery above → re-drop → continue. Never Parallels GUI. Never ask Joshua to log in. (Restart is TRIAGE to clear a wedge so the pull can run — it is not a substitute for the closing-handler Continuous-Scrolling fix below.)

---

**Purpose:** Read this file BEFORE doing any Bravo combined-run, closing-report, or "Not Responding" work. Do not re-investigate settled facts. Append new confirmed findings; never delete history. Last updated: 2026-06-07.

---

## ⛔ TOP RULE
Killing/restarting Bravo is TRIAGE ONLY, never "the fix." The fix is to stop the automation from inducing the hang. Do not propose kill-and-rerun as a solution.

---

## ✅ CONFIRMED ROOT CAUSE — "(Not Responding)" is induced by OUR automation
Bravo NEVER hangs when Joshua runs reports by hand. The automation does something Joshua never does: **it manipulates the Report Preview "Enable Continuous Scrolling" toggle on every closing/journal report.**

- That toggle forces Bravo to render the ENTIRE multi-page report as one giant canvas. On wide closing reports (End of Month, etc.) this pins Bravo's UI thread → Windows marks it **"(Not Responding)"** for minutes. (Documented in the handler's own comments.)
- The toggle-state detection is fragile (button is labeled by action "Enable Continuous Scrolling", not state). History shows it was rewritten multiple times on 2026-05-29 (`.bak-pre-toggle-fix`, `.bak-pre-size-threshold`) and still fails — so the automation often ends up turning the freeze-inducing mode ON rather than OFF.
- The automation then fires UIA queries (ClickByName Export, FindByName) AT the frozen/rendering window with tight timeouts, which piles cross-process calls on a blocked UI thread and makes the wedge permanent.
- **Why Joshua never sees it:** he opens the paginated preview, looks at page 1, clicks Export → CSV. He never touches Continuous Scrolling. CSV export captures the full report REGARDLESS of view mode, so the toggle is both unnecessary AND the cause.

### Handlers that contain the toggle code (the suspects):
EndOfMonth, EndOfDay, EndOfDayConsolidated, DepositsAndPaidOuts, DisbursementJournal, GeneralException, InterStoreCashTransfer, LargeCashTransactions, Transfers.
(All in `reports/`. The `aged-inventory / loans-75 / layaways / employee-activity / chekkit-inactives` reports do NOT toggle CS — they only fail because a prior closing-report hang already wedged Bravo.)

---

## ✅ CONFIRMED CASCADE
Once Bravo is wedged on a Report Preview, `EnsureStore` → `SwitchStore` → `BackToDashboard` can't reach Dashboard or find "Lock Session", so EVERY later store fails ("EnsureStore failed"). The whole combined run returns `partial` with all cells errored. The watcher logs `cause=nav — NOT a lockout risk; breaker not incremented`, so it never escalates or self-heals — it just burns ~45s/cell failing, then the compile step has nothing to post. **This is why the Monday combined analysis has never completed.**

---

## 🔧 PERMANENT FIX PLAN (status tracked here)
1. **[CORE] Remove the Continuous Scrolling toggle manipulation** from all 9 closing/journal handlers. Export straight from the default paginated preview (mirror Joshua's manual path). — STATUS: pending Joshua go-ahead
2. **Don't fire UIA at a rendering/hung window.** Gate ribbon interactions on a responsiveness check (SendMessageTimeout SMTO_ABORTIFHUNG / IsHungAppWindow); wait for render to finish like a human. — STATUS: pending
3. **Always close Report Preview on exit AND on error; verify Dashboard before returning** so a failure can't cascade. — STATUS: partial (recovery block exists, still cascades)
4. **Preflight responsiveness gate** in monday-bravo-combined-run: check `tasklist /v` Status != "Not Responding" AND on Dashboard before dropping triggers; recover first if not. — STATUS: pending
5. **Fail loud:** compile task DMs Joshua if >25% cells error instead of posting nothing. — STATUS: pending
6. **Fail fast:** abort run after first store's EnsureStore fails twice (don't burn 19 min). — STATUS: pending

Roll-out rule: back up each file, edit ONE handler (EndOfMonth), smoke-test ONE cell, confirm CSV written + Bravo stays responsive + returns to Dashboard, THEN propagate to the other 8.

---

## 📋 RUN HISTORY
- **2026-06-07:** Combined run failed 25/25 cells. Bravo was ALREADY "(Not Responding)" on a HAR End-of-Month Report Preview (6/1 data) from a prior closing-report run before triggers were even dropped. Confirmed root cause above via code read (`reports/EndOfMonth.ahk`, `bravo_export.ahk`). Created this log.

## 🔑 ENV FACTS
- Parallels VM GUID: `{7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}`
- Project root (Mac): `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction`  (= `Y:\Documents\...` inside VM)
- Watcher: `bravo_watcher.ahk` (PID varies). Auto-login: `BravoAutoLogin.ahk`.
- Check Bravo responsiveness: `prlctl exec '{GUID}' --current-user tasklist /v /fi "IMAGENAME eq Bravo.exe" /fo list` → look at `Status:` field ("Running" vs "Not Responding").

## ✅ CONFIRMED 2026-06-07 — auto-login does NOT launch Bravo
`BravoAutoLogin.ahk` only fills the login form (on Ctrl+Shift+L / when the Bravo login window is active). It does NOT start the Bravo process. So after a kill, Bravo stays down until relaunched manually:
- Launch via ClickOnce ref: `C:\Users\joshuadavis\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Bravo Store Systems\Bravo.appref-ms`  (cmd: `start "" "<that path>"`)
- The `monday-bravo-combined-run` SKILL preflight wrongly assumes auto-login relaunches Bravo — it doesn't. Triage steps must explicitly relaunch Bravo, then let BravoAutoLogin fill creds.

## ✅ CONFIRMED 2026-06-07 (b) — headless re-login is unreliable; do NOT kill Bravo
After killing Bravo, getting it logged back in headlessly failed repeatedly. Root reason: BravoAutoLogin only acts when `WinActive("Bravo ahk_class")` is true, but external `WinActivate` from prlctl-launched AHK does NOT reliably bring Bravo to the foreground in the VM, and every `prlctl exec` of a console program (cmd/powershell/tasklist) spawns a Windows Terminal that grabs foreground. Net: Bravo sits at the login screen, unfocused, and never auto-logs-in.
- LESSON: treat "always logged in" as an invariant. Do NOT kill Bravo as triage. If Bravo is ever killed/closed, the fastest recovery is a human clicking the Bravo login once (or driving Parallels visually via computer-use), NOT headless keystrokes.
- The watcher (in-session) keeps Bravo foreground during normal store-switching, which is why auto-login works in production but not for external recovery.

## ✅ FIXES SHIPPED 2026-06-07
1. **CORE: Continuous Scrolling toggle REMOVED from `reports/EndOfMonth.ahk`** (backup `.bak-pre-cs-removal-2026-06-07`). 0 toggle refs remain; export path intact. This is the fix for the recurring "Not Responding" hang. STILL the other 8 closing/journal handlers to do AFTER a clean smoke test.
2. **`lib/StoreCycle.ahk` EnsureStore: added Select Store selector handling** (backup `.bak-pre-selector-fix-2026-06-07`) — on the Global Access store selector it now double-clicks the target store row, THEN RecoverFromAutoLock. PROVEN working in logs ("selector -> double-click 'Harrisonburg'", "store confirmed: HAR").
3. **Self-heal recovery script** `_recover_to_dashboard.ahk` — from Select Store/login → dashboard, verifies the "Reports" sidebar. Run in-VM: `AutoHotkey64.exe _recover_to_dashboard.ahk HAR`.

## ✅ NEW FINDINGS 2026-06-07 (render + bounce)
- **Freshly-relaunched Bravo renders BLACK** (window exists, title shows store, but client area unpainted; UIA finds no "Reports"). **Maximizing/activating the window wakes the renderer** (`WinRestore`+`WinActivate`+`WinMaximize` → Bravo splash paints). Root cause of the "black window" seen all session. ActivateBravo should probably maximize too.
- **Login BOUNCE/auto-lock:** after a successful Submit (onLogin=no, code=HAR, splash paints), Bravo drops BACK to the login screen within ~1 min idle. This makes cold-start login flaky and, with repeated retries, risks an account lockout (see 2026-05-13). DO NOT hammer logins.
- **`LogVisibleNames` HANGS** on the login/selector screen (UIA full-tree enumerate). Avoid it there; use bounded `ExistsByName`/`WaitForAnyByName`.
- The login screen's "Close" element is the **app window close** — clicking it QUITS Bravo. Never click "Close" to dismiss.

## 🚑 SAFE RECOVERY ORDER (after a kill, to avoid lockout)
1. Ensure Bravo running & rendered: launch via `Bravo.appref-ms`; then maximize/activate the window so it paints.
2. Run `_recover_to_dashboard.ahk <STORE>` ONCE; check `logs/_recover_result.txt`. If FAIL, wait, fix the specific screen — do NOT loop logins rapidly.
3. Once on a verified dashboard (Reports sidebar present), it stays logged in for normal watcher cycling (Resume Session, not fresh login).


## 📋 RUN HISTORY — 2026-06-12 (intake-detail prestage)
- intake-detail (Claude Pawn Walks) for 2026-06-11: CUL+HAR+ROA succeeded; LEX & WAY failed 3 consecutive runs (incl. after _restart_watcher.ps1). Errors: LEX EnsureStore failed (2x) / Could not set Start Date (1x); WAY Could not set Start Date (3x). Bravo Status: Running throughout — NOT a wedge. Diag dump shows report screen open (Show summary panel checkbox visible) but date control not found. Suspect IntakeDetail.ahk date-picker UIA selector fails on LEX/WAY report screens. Logs: intake-detail-2026-06-12T06-37-05 / 06-45-43 / 06-50-58 / 06-56-59. Joshua DMed.

## ✅ FIXES SHIPPED 2026-06-12 (intake-detail)
1. reports/IntakeDetail.ahk (backup .bak-pre-datefallback-2026-06-12): added IntakeSetDateByPopupEditor fallback — on stores where the loaded report's date criteria cells expose as PopupBaseEdit (PART_Editor) instead of BravoDateEdit (observed LEX/WAY), set them by x-position via ValuePattern. PROVEN: WAY now succeeds (19 rows).
2. Same file: IntakeCloseReportScreen() in the error path — a failed cell now closes the Loans/Buys screen before returning. Root cause of the EnsureStore cascade: leftover open screen triggers Bravo warning 'Cannot switch stores: FREE1 is busy with Loans/Buys' (screenshot intake-detail-2026-06-12T06-56-59_LEX_switchstore-store-row.png).
3. Same file: saved-report load verification via BoxReportName after selection (soft gate; BoxReportName reads '' on LEX so it cannot hard-verify there).

## ⚠️ OPEN ISSUE 2026-06-12 — 'Claude Pawn Walks' saved report is WRONG ON LEX
The saved report named 'Claude Pawn Walks' loads with a Loan-Reviews-style definition at LEX (columns Ticket Number/Disposition/Disposition Date/Due Date/Pull Date/Customer/Loan Amount/Age/MobilePawn, criteria 'Age =', no Transaction Date filter) → export is unfiltered garbage (250-row cap hit). CUL/HAR/ROA have the correct 4-column definition; WAY has a 6-column variant (extra Ticket Kind + Associate) that still parses fine. These are per-store variants, NOT one global definition. FIX NEEDED IN BRAVO AT LEX (manual, ~2 min): Loans/Buys -> Custom Reports -> load 'Claude Pawn Walks' -> columns Ticket Number, Category, Full Description, Loan Amount; criteria Transaction Date between -> Save. Until then LEX intake-detail cells produce bad CSVs (quarantined as .bad-wrong-report in output/).

## ⚠️ UPDATE 2026-06-12 (evening) — LEX 'Claude Pawn Walks' REPORT rebuilt + VERIFIED, but list-view EXPORT still wrong
Joshua-approved automated rebuild (_lex_pawnwalks_rebuild3.ahk) SUCCEEDED at the dialog level: saved report now has BoxColumns=Full description and cost (490f2277), criteria Disposition Date range + Ticket Kind=BUY. Reload-verify confirmed all three in-dialog (SAVED+VERIFIED).
BUT: when the daily handler loads the report and clicks Ok, the LEX list-view grid still renders the 10-column layout (Ticket Number/Disposition/Disposition Date/Due Date/Pull Date/Customer/Loan Amount/Age/MobilePawn/SMS) AND is UNFILTERED (CSV had 56 BUY + 194 ON LOAN across many dates, 250-row cap). So the report DEFINITION is fixed but the per-store LIST-VIEW 'Saved Layouts' selection is independent of the report's BoxColumns and is still the wrong 10-col layout on LEX. CUL/HAR/ROA render the correct 4-col layout because their list-view Saved Layout is already the right one.
Automation could NOT open the list-view 'Saved Layouts' dropdown ('layout option not visible after opening combo' — _lex_fix_layout.ahk). Likely needs a human: at LEX, Loans/Buys -> Custom Reports -> run Claude Pawn Walks -> in the list view, Layouts panel -> Saved Layouts -> pick the 4-column 'Full description and cost' layout (the one CUL uses) -> Save Layout. THEN re-run intake-detail for LEX to confirm 4-col BUY-only output.
Also shipped: IntakeDetail.ahk patch4 (.bak-pre-nodblclick-2026-06-12) — removed the double-click commit branch in saved-report selection (it half-loaded the dialog); click->Enter only now.
Bad LEX CSVs quarantined in output/ as .bad-wrong-report*, .bad-listview-layout.

## RUN HISTORY -- 2026-06-16 (intake-detail prestage) -- intake-detail (Claude Pawn Walks) for 2026-06-15: run completed status=success, all 5 store CSVs written, Bravo Running throughout (NOT wedged, no restart needed). BUT all 5 stores (CUL,HAR,LEX,ROA,WAY) exported the WRONG 10-col loan-review layout (Ticket Number,Disposition,Disposition Date,Due Date,Pull Date,Customer,Loan Amount,Age,MobilePawn,SMS) -- no Category/Full Description col, and each hit the 250-row cap (unfiltered/truncated). REGRESSION: previously LEX-only (per 2026-06-12), now ALL FIVE. Not a watcher hang -- Bravo-side saved-report/list-view layout problem. Fix: per-store Loans/Buys -> Custom Reports -> run Claude Pawn Walks -> list view Layouts -> Saved Layouts -> 4-col Full description and cost -> Save Layout, then re-run. Joshua DMed. Run id intake-detail-2026-06-16T06-36-49.

## RUN HISTORY -- 2026-06-20 (intake-detail prestage)
intake-detail (Claude Pawn Walks) for 2026-06-19: FAILED 10/10 cells across TWO runs (ids intake-detail-2026-06-20T06-36-24 and -06-44-13), all 5 stores, status=partial, 0 CSVs. Every cell errored: "SelectSavedReport: could not select 'Claude Pawn Walks' via click or keyboard walk" -> combobox found at y=983 but "ClickByName 'Claude Pawn Walks': element not found". Bravo Running/responsive throughout (clean store switches, BackToDashboard OK) -- NOT a wedge, no restart done (healthy Bravo not cycled). Regression from earlier 'wrong-layout' issues: now the saved report isn't even present/selectable in the Custom Reports dropdown on ALL 5 stores. Needs manual Bravo-side fix: per store Loans/Buys -> Custom Reports -> confirm/re-save 'Claude Pawn Walks' so it appears in the saved-report combobox. Joshua DMed.