# Bravo Data Extraction — KNOWN ISSUES (READ THIS FIRST)

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

---

## 🔁 RUN 2026-06-15 — combined run hung again on ROA End-of-Month (analysis + DECISION)
- Monday combined run dispatched 13:08 ET. Watcher fresh (started 10:11), trigger queue empty, all 5 preflight checks green.
- **ROA End-of-Month** (date range 2026-06-01..2026-06-14) was the first heavy cell. CSV never appeared at the LOCAL temp path within 240s; Bravo went **"(Not Responding)"** on the *rendered* ROA EOM preview (screenshot: `logs/monday-bravo-combined-2026-06-15_backtodashboard-unknown-state.png`). Every later cell then cascaded to "EnsureStore failed" exactly as documented. **0 CSVs produced.**
- **KEY:** `reports/EndOfMonth.ahk` is ALREADY the hardened gold standard — CS toggle removed 6/7; 6/8 rebuild added `EomWaitResponsive`/`IsHungAppWindow` gate, `EomSelectCsvVerified`, local-disk-export-then-copy-to-share, filesystem-only export wait, and removed `LogVisibleNames`. So today's ROA failure is a **RESIDUAL, ROA-specific issue** (heaviest store / date-range export exceeding 240s, or the export-OK click not registering) — NOT the CS toggle.
- **CONTRADICTION found in codebase:** `SafeRegisterJournal.ahk` header (dated 6/8) says it *added* the Continuous-Scrolling toggle-off block "verbatim from DepositsAndPaidOuts" as a fix — at the same time this file + EndOfMonth concluded the toggle MANIPULATION is the root cause and REMOVED it. **8 handlers still carry the toggle block** (CS_refs 7–8): DepositsAndPaidOuts, DisbursementJournal, EndOfDay, EndOfDayConsolidated, GeneralException, InterStoreCashTransfer, LargeCashTransactions, Transfers, SafeRegisterJournal. NOTE: `SafeRegisterJournal` runs **daily** via `daily-funds-verification`.
- **DECISION (Joshua, 2026-06-15, "full fix, phased"):** bring all 8 handlers up to the EndOfMonth gold standard (remove CS toggle block; add responsiveness gate; verified CSV; local-export-then-copy; filesystem-only wait; drop LogVisibleNames) — ONE at a time, backup + single-cell smoke test each. Separately diagnose the ROA EOM residual timeout (longer local-write window / confirm export-OK registers). Then add orchestrator: preflight responsiveness gate, fail-fast (abort a store after 2 EnsureStore failures), fail-loud (compile DMs Joshua if >25% cells error instead of posting nothing). Triage recovery = `_recover_to_dashboard.ahk`, **NEVER kill Bravo** (lockout risk).
- **Today's recovery in progress:** parked the 3 remaining `monday-eom` triggers + the `monthly-bonus-eom` trigger to `triggers/_hold-2026-06-15/` to stop the doom-loop re-hanging Bravo; will recover Bravo to dashboard after the combined trigger drains, re-drop today's reports, and restore the bonus trigger.

---

## ✅ WORKING RECOVERY CHAIN (proven 2026-06-15) — frozen/stuck Bravo → healthy dashboard, fully headless
Follow this EXACT sequence; do not re-derive. Each step proven on 2026-06-15 after the ROA-EOM freeze.
1. **Diagnose:** `prlctl exec '{GUID}' --current-user tasklist /v /fi "IMAGENAME eq Bravo.exe" /fo list` → if `Status: Not Responding`, the UI thread is hung and CANNOT be UIA-driven (the watcher's nav recovery + `_recover_to_dashboard.ahk` will FAIL on a hung window — confirmed today).
2. **Relaunch (only acceptable kill):** run `_relaunch_bravo_and_watcher.ps1` — kills the hung Bravo + relaunches Bravo AND the watcher into interactive **Session 1** via the scheduled-task trick. (Plain `prlctl exec AutoHotkey…` runs in Session 0 and cannot drive the real desktop — that's why direct recover-script launches did nothing.)
3. **MAKE BRAVO VISIBLE:** after relaunch Bravo comes up MINIMIZED / at the "Select a store" screen. **It must be un-minimized + visible or UIA/auto-login silently fail (Joshua's rule).** Run `_nudge_login.ahk` (WinRestore→WinActivate→WinMaximize) via the Session-1 launcher `_run_nudge_session1.ps1`.
4. **Select Store → Dashboard:** run `_recover_to_dashboard.ahk <STORE>` (GUI launch via `prlctl exec --current-user AutoHotkey64.exe …`). Lands on the store Dashboard (Reports sidebar visible). Verify with `prlctl capture` (GUI-safe screenshot), NOT tasklist.
5. **DO NOT console-poll during a run:** every `prlctl exec` of a console program (tasklist/powershell/cmd) spawns a Windows Terminal that **STEALS Bravo's foreground** → causes `Bravo window not found/ready within 30s` and fails the cell. While the watcher runs, check ONLY Mac-side files (logs/results/output CSVs) + `prlctl capture`.
6. **Smoke-verify:** drop a 1-cell trigger (`aged-inventory-summary`, one store) → expect result `success` + CSV in `output/`. Today: smoke3 = success, 16 rows, 999-byte CSV. THEN re-drop the full set.


---

## Custom-report selection + recovery gotchas (added 2026-06-18, NICS transfers build)

- **Saved-report name match is case-sensitive.** Selecting `Claude NICS transfers` failed because the report is actually `Claude NICS Transfers`. Always copy the exact saved name. (See bravo-context "Custom Reports" section.)
- **The Custom Reports editor loops on "Done."** `BackToDashboard` clicks `btnDone` repeatedly, exhausts hops, and fails "could not return to Dashboard." Handlers must exit via the named **"Cancel"** button, in BOTH the normal path and the pre-flight cleanup, so a failed run leaves Bravo on a Dashboard.
- **A stranded editor defeats `recover-to-dashboard.ahk` too.** When a failed handler leaves Bravo sitting in the Custom Reports editor, `bravo_health_gate.sh` Rung4 returns `FAIL no-dashboard` (recover can't Cancel out of that editor). Symptom looks like a wedged Bravo but isn't — Bravo is healthy, just stuck on a modal. Fix: Cancel/close the editor (manual click is fastest) → Dashboard; longer-term, teach `_recover_to_dashboard.ahk` to click the named "Cancel" in this editor.
- **Don't trust `_health_gate_status.txt` / `_health_gate.log` as *current* state.** They reflect the LAST gate run (e.g., the 5 AM scheduled run), not now. Check the file's timestamp and corroborate with the newest successful pipeline output before concluding Bravo is down. A `FAIL` older than a later successful run is stale.
