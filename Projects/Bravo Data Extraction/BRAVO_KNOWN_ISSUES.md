
---
## RUN -- 2026-07-27 (PAWN WALK)
intake-detail (Claude Pawn Walks) for 2026-07-26: FAILED, 0 CSVs, no result.json.

Timeline:
- Health gate (bravo_ensure_healthy.sh CUL) PASSED instantly (Bravo already healthy/running).
- Trigger intake-detail-2026-07-27T09-10-06 dropped 09:10:06. NOT claimed by watcher for ~29 min even though Bravo/watcher were alive -- root cause was a legitimate backlog: watcher was mid-processing an unrelated Monday job (vpops-trigger-dropper-2026-07-27T09-06-58, multi-cell employee-activity + loans-75-days-past-due + layaways across all 5 stores), which didn't finish until 09:38. NOT a hang, just Monday-morning queue contention -- worth considering a later fire time or queue priority for PAWN WALK on Mondays.
- Did ONE watcher restart (_restart_watcher.ps1) at ~09:12 while diagnosing the claim delay, before realizing it was legitimate backlog. watcher.last_started.txt did NOT advance after the restart (confirms prior memory note this file is stale/unreliable -- verify by claim/output instead).
- Trigger finally claimed ~09:39. CUL: 3/3 attempts "Claude Pawn Walks did not load (wrong report / no item columns, loads with Age=1 criteria instead of Transaction Date/Category/FullDescription/LoanAmount)" -- same recurring regression documented 2026-06-16, 2026-06-20, 2026-07-10, 2026-07-11. Still unresolved.
- HAR: same wrong-report signature attempts 1-2. Attempt 3 hit a NEW failure: "GetBravoRoot: Bravo window not found" -- Bravo actually crashed/closed mid-run (PID changed 13272->13048, mem ~1.2GB->428MB, CPU reset, window title lost store suffix). Different from the wrong-report issue -- a genuine crash.
- LEX: EnsureStore failed -- could not reach Dashboard post-crash, "Lock Session" element not found. Correctly flagged cause=nav (not lockout), breaker not incremented -- no login-hammering occurred.
- A second trigger (re-dropped as intake-detail-2026-07-27T09-20-00 during the earlier claim-delay diagnosis) got picked up by an apparently-fresh watcher process (bravo_watcher.ahk PID 5084->9288, CPU reset to 0 -- possible auto-restart after the Bravo crash, cause not confirmed) at 09:46:42. Found Bravo at a "Select a store" screen (confirms the crash), self-recovered login to CUL, reached Dashboard 09:47:09, logged "settling 90s before report" -- then went SILENT. No further log lines through 09:53:27+ (6.5+ min past the expected 90s settle). No result.json, no CSVs from either trigger.
- Per policy (max ONE relaunch cycle beyond the health gate, no login-hammering), did not attempt a second watcher/Bravo restart. Stopped and reported failure per the v2 failure policy: DM to Joshua only, no post to #pawn-walks.

NEXT SESSION should investigate, in priority order:
1. The settling-90s-then-silent hang on the 09-20-00 run -- check for a screenshot/crash artifact, confirm whether Bravo.exe (was PID 13048) and bravo_watcher.ahk (was PID 9288) are still alive/responsive.
2. The recurring "Claude Pawn Walks wrong report / Age=1 criteria" regression -- 5th occurrence now (6/16, 6/20, 7/10, 7/11, 7/27). Needs the permanent Bravo-side fix (re-save/re-verify the saved report + list-view layout per store), not another automation retry-count bump.
   ^^ 2026-07-28 UPDATE: root cause likely FOUND -- see item 6 below (generic
   SelectSavedReport does not commit the report definition in some modules).
3. Whether the mid-run Bravo crash (GetBravoRoot: Bravo window not found on HAR) is a new failure mode or related to resource pressure from the Monday backlog job that ran immediately before.

---
## CRITICAL -- 2026-07-28: Bravo silently auto-updated 2026.2.2.3 -> 2026.6.0.79

At ~13:36 a ClickOnce update installed mid-session. ALL handlers were hardened
against 2026.2.2.3. Confirmed regressions and fixes:

1. Enter no longer fires the Custom Reports generator's Ok button.
   Any handler that runs a saved Ad Hoc report via Send Enter now silently
   NEVER RUNS the report -- the criteria dialog stays open, the background
   (empty) Inventory grid gets read, and the handler reports a false 0-row
   "success". FIX (in AgedJewelrySales.ahk + JewelrySoldMargin.ahk): click Ok
   by name, then VERIFY BoxReportName is gone before trusting any result.
   TODO: audit IntakeDetail / SoldInvDetails / ActiveInvDetails / LowDollar*
   and every other handler that sends Enter to the generator.

2. Update wedges Bravo mid-run. dfsvc.exe present + Bravo windowless =
   ClickOnce update in flight. Recovery that worked: kill Bravo AND dfsvc,
   clear logs/_health_gate_status.txt, re-run bravo_ensure_healthy.sh (its
   Session-1 relaunch + recover-to-dashboard PASSED on 2026.6 from clean state).

3. Windows 'Pick an app' (OpenWith.exe) modals appeared post-update and
   blocked UIA. Kill OpenWith processes via prlctl powershell Stop-Process.

4. Done-exit from Inventory module is slower on 2026.6 -- items-to-price
   needed Done x3 + BackToDashboard fallback. Works, just slower.

5. Saved-report COLUMN FORMATS (Object_Layouts) are slow/flaky per store.
   'Aged Jewelry Sold' format selected fine on CUL/HAR/LEX/ROA but rendered
   too slowly on WAY, and a fallback candidate matching the REPORT name
   caused a silent default-layout run. Never put the report's own name in a
   format candidate list; retry F4 with long settles instead (fixed).

6. Inventory-module saved-report selection requires SelectInventorySavedReport.
   The generic SelectSavedReport fills BoxReportName WITHOUT committing the
   report definition (verified: name box shows the right name, grid returns
   0 rows). SoldInvDetails.ahk still uses the generic selector -- known broken.
   This may ALSO be the root cause of the recurring 'Claude Pawn Walks wrong
   report / Age=1' regression (item 2 above).

New cells added (additive) 2026-07-28: aged-jewelry-sales (AgedJewelrySales.ahk;
date field supports 'saved', 'saved:<Report>', 'saved:<Report>|<from>..<to>',
'columns:<Report>' probe modes + 'Aged Jewelry Sold' format selection) and
jewelry-margin-sold (JewelrySoldMargin.ahk -> 'Claude Sold Inv Details').
Analysis helper: _analyze_aged_margin.py (per-store margin stats from the
aged-jewelry-sales CSVs). Project purpose: 12mo-vs-18mo jewelry scrap decision.

7. IMPORTANT DATA SEMANTICS -- Ad Hoc 'Age' criteria evaluate AS OF RUN TIME,
   not at time of sale. 'Aged Jewelry Sales' (>12mo criterion, Joshua-built)
   pulled with a trailing-12-month Date Sold range returns items that are
   >12mo old TODAY -- including items that sold young last year and merely
   aged since. Confirmed by Joshua + number-sequence evidence 2026-07-28.
   CLEAN usage: keep the Date Sold window short and recent (e.g. last 90
   days -> pieces were >=9mo at sale). For true age-at-sale history, join
   sold data to intake dates via the 'Date to Inventory' saved report
   (criteria dates = intake-date range; works, but a 2024-2026 window
   overwhelms the grid walker -- chunk into ~quarterly intake windows).
   Ok-fix smokes all PASSED on 2026.6.0.79 (15:45-15:50 run): safe-register-
   journal, employee-activity, loans-75-days-past-due, loan-reviews [ok-fix].

## 2026-07-28 evening addendum (aged jewelry sweep prep)
- Bravo failed to relaunch after 2026.6.0.79 wedge cleanup (~17:17-17:31). Fixed by launching the ClickOnce shortcut directly: Start-Process on 'C:\Users\joshuadavis\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Bravo Store Systems\Bravo.appref-ms' via prlctl exec + powershell -EncodedCommand (base64 avoids all quoting issues through osascript->prlctl). Gate PASS 17:38.
- Preston's saved report 'Claude Aged Sold' generator dialog exposes NO BravoDateEdit fields -> date overrides impossible (dates 0/2); age spinner + format DO work there. Use our 'Aged Jewelry Sales' saved report for date-windowed pulls.
- age:<N>|<range> (no saved:) on default report is the canonical sweep form: correct 8-col 'Aged Jewelry Sold' format + distinct jewelry-sold-age<N> slug. Smoke PASS 17:48 CUL (28 rows, Last Sold Price present).
- KNOWN GAP (deferred): when age: is combined with saved:<Report>, reportOverride slug wins over the age slug -> filename collision with non-age runs of same report+range. Fix later: append -age<N> suffix inside the reportOverride slug branch in AgedJewelrySales.ahk (requires watcher restart; do not restart near scheduled runs).

## 2026-07-29 overnight — aged jewelry 12v18 analysis wrap-up
- Inventory Age SpinEdit NEVER commits to the criteria model regardless of set method (ValuePattern, focus+Tab, type) — proven by age:9999 run returning the identical row set as saved >365. age:<N> override in AgedJewelrySales.ahk is a DEAD END for changing the cohort; readback lies. Do not trust spinner-based cohort pulls; all *_jewelry-sold-age0.csv.tainted-uncommitted-spinner files are invalid.
- Correct all-sold data path: jewelry-margin-sold ('Claude Sold Inv Details', SelectInventorySavedReport, working date overrides). Grid walker false-stops on large laggy grids (~quarter-size, 600+ rows) — pull MONTHLY windows; even monthly truncates ~1/3 of the time (stops days early) — check last-date vs month-end and retry.
- SoldInvDetails.ahk patched to SelectInventorySavedReport [inv-select fix 2026-07-28].
- Bravo relaunch failures (Session-1 trick produces no window): fixed twice tonight by direct ClickOnce shortcut launch — prlctl exec ... powershell -EncodedCommand Start-Process 'C:\Users\joshuadavis\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Bravo Store Systems\Bravo.appref-ms'. Consider adding as Rung3b in the health gate.
- Final analysis delivered 7/29 ~3:45 AM: keep 18mo scrap; 12mo policy = -$89k/yr GP company-wide. Report: jewelry-scrap-final-report.html (Cowork artifact jewelry-scrap-12v18-final).

## 2026-07-29 AM — CRITICAL: age-criteria discoveries (supersedes prior age notes)
- The real Inventory Age criteria control in the Custom Report generator is Name='BravoSpinEdit' (inner PART_Editor). Plain Name='SpinEdit' is an unrelated EMPTY background control — every prior age-override attempt poked the wrong element. AgedJewelrySales.ahk fixed [target-fix 2026-07-29]; focus+ValuePattern+Tab commits correctly on the real control.
- **The saved report 'Aged Jewelry Sales' operator is Inventory Age LESS THAN 365, not greater-than** — proven: with the real control, age:9999→37 rows (=all June jewelry), age:0→0 rows; and ZERO overlap between the 2025-07-28..2026-07-27 pulls and Preston's 'Claude Aged Sold' (>365 per screenshot). Therefore all 2025-07-28_to_2026-07-27_*_aged-jewelry-sales.csv files are the YOUNG (<12mo-at-sale) cohort despite the name. The 7/28 overnight analysis had cohort labels inverted; corrected analysis 7/29 AM.
- With less-than semantics + working override, cumulative age-threshold pulls (age:365/395/425/.../99999 over a fixed window) yield age-bucket distributions by set difference — this is the canonical way to get age-at-sale histograms.

## 2026-07-29 midday — age-curve analysis complete
- Threshold sweep (age:365/395/425/455/485/515/545/605/99999, window 2025-07-28..2026-07-27) delivered the full age-at-sale curve. Nesting verification (each larger threshold superset of smaller) is the mandatory QA check for cumulative pulls.
- ROA anomaly: age:605 reproducibly returns 59 rows and age:99999 returns inconsistent small sets (116, 40) that violate nesting, while ROA <=545 nests perfectly. Cause unknown (suspect saved-report state or dialog residue at high spinner values at ROA). ROA 18+ tail therefore partial. TODO: investigate before next ROA deep pull.
- Hard-wall (2700s) allows ~11-12 cells/trigger at ~3-4min each for year-window jewelry pulls — size triggers accordingly.
- FINAL BUSINESS RESULT (supersedes 7/28 report and 7/29 morning DM): no margin cliff at any age 12-20+ months (monthly multiples 3.0-3.9x); true aged (>12mo) sales = 886 pcs, $46.6k cost, $156.7k rev, 3.36x; policy cost/yr: 12mo cut -$70.4k, 14mo -$52.9k, 16mo -$41.0k, 18mo-enforced -$28.1k. Recommendation delivered: replace time-based scrap with piece-level value rule (melt if retail < ~1.5x melt at 12/18mo review).

## 2026-07-30 AM — root-caused + fixed the recurring health-gate "FAIL no-dashboard" (4th day)
- daily-items-to-price health gate failed for the 4th consecutive weekday morning (07-22, 07-23, 07-29, 07-30) with the same signature: full Rung3/Rung4/Rung4b escalation (nudge, consolidate watcher, guarded force-kill+relaunch, recover-to-dashboard x4 total) still ends `FAIL no-dashboard`, with a live AutoHotkey64.exe process visible in FAIL diagnostics.
- ROOT CAUSE FOUND: `_recover_to_dashboard.ahk` (the script Rung4/Rung4b actually runs) only calls `DismissPopups()` each attempt — which handles generic info/reminder popups but has NO case for a stranded Custom Reports / Ad-Hoc generator dialog (AutomationId `BoxReportName`). It never calls `BackToDashboard()` in lib/Bravo.ahk, which IS already hardened to Cancel out of exactly that dialog (`PART_CancelDialogButton`, `btnCancel`, Done, Cancel-by-name, Esc fallback) — every report handler uses BackToDashboard to exit stuck views, but the health-gate recovery path never did. So a stranded generator dialog (most likely left open by whatever ran right before the 8AM gate, or a crashed handler from the 2026.6.0.79 ClickOnce update — see 2026-07-28 entry below) had no way to be dismissed during recovery, and the gate just retried the same ineffective check five times before giving up.
- FIX (additive, reuses existing hardened helper — no new UI logic invented): `_recover_to_dashboard.ahk` now calls `BackToDashboard(4)` when not on the login screen and the Reports sidebar isn't immediately visible, before falling through to the login-repair path. Backup at `_recover_to_dashboard.ahk.bak-pre-backtodash-fix-2026-07-30T081900`.
- NOT YET LIVE-VERIFIED (no Parallels/computer-use grant in the session that made this fix) — next scheduled Bravo pull is the real-world test. If `FAIL no-dashboard` recurs with this fix in place, the stranded element is NOT one of BackToDashboard's known Cancel/Done targets and needs a screenshot-based follow-up (BackToDashboard already takes one on final failure — check `logs/` for it).
- Slack DM sent to Joshua on the 07-30 run per policy; nothing posted to #items-to-price (correct — total gate failure, no store data pulled that morning).

## 2026-07-30 — enterprise-wide audit of the 2026.6.0.79 ClickOnce regression across all report handlers
- Following the 07-28 entry below (Enter no longer confirms the Custom Reports generator's Ok button; generic SelectSavedReport doesn't commit in the Inventory module), only a handful of handlers had been patched (AgedJewelrySales, JewelrySoldMargin, JewelryCountAudit, SoldInvDetails, ActiveInvDetails, plus partial coverage in IntakeDetail/ChekkitInactives/ChekkitInvites/LoanPortfolio2026/LoanReviews/LowDollarBuys/LowDollarLoans/PostToAccountingGL/SoldYesterday). ~40 other handlers in reports/*.ahk still send a bare `{Enter}` with no Ok-click-and-verify pattern and no ClickOnce-era marker at all — full file-by-file audit in progress to determine which of those actually route through the Ad-Hoc generator dialog (candidates for the same fix) versus a different dialog type (not affected). See follow-up entry for results.

## 2026-07-30 (follow-up) — enterprise-wide audit RESULTS: all 71 reports/*.ahk handlers classified, 5 patched

Completed the full file-by-file audit announced above. All 71 non-`.bak` files in `reports/` were read and classified against the two 2026-07-28 ClickOnce regressions (bare-Enter-doesn't-confirm-Ok, and generic `SelectSavedReport` not committing in the Inventory module). Verdict counts:

- **NOT-APPLICABLE: 48** — do not drive the Custom Reports/Ad-Hoc generator dialog (`BoxReportName` / "Choose Saved Report" combo) at all. The large majority are the built-in Reports-sidebar "tile" dialogs (Start/End Date + Preview/Export...), which are a structurally different dialog that already had working Enter-primary + `ClickByName(Ok)` fallback + explicit render-wait confirmation (never relied on Enter alone) — correctly left untouched:
  ATFADBook, ATFADCount, AgedInventorySummary, BravoBusinessDashboard, ChekkitGridOnly, ChekkitInactivesDiag, CompanyKpis, CostAdjustment, CreditBalance, CreditJournal, DepositsAndPaidOuts, DigitalMarketingSettlement, DisbursementJournal, DropShipSettlement, EmployeeActivity, EndOfDay, EndOfDayConsolidated, EndOfMonth, GeneralException, InterStoreCashTransfer, InventoryBase, InventoryByLocation, ItemsToPrice, LargeCashTransactions, LayawayBalance, LayawayDeposits, LayawayJournal, Layaways, LoanBase, LoanDisposition, LoanHistory, LoanJournal, LostStolenOrDamaged, PawnActivitySummary, PostToAccountingGL, PostToAccountingPost (own verified-close loop on a different "Reporting Dates" dialog), RetailReportsDashboard, SafeRegisterJournal, SalesAccounting, SalesByVendor, ScrapRefiningGold, SoldInventory, Transfers, UIADiscover (diagnostic tool, no dialog), VendorPurchase, VendorReceiving, VendorRepairs, WebSettlement.

- **ALREADY-FIXED: 18** — drive the Ad-Hoc generator and already have a robust Ok-click + close/render verification (equal to or stronger than the reference pattern); not touched:
  AgedJewelrySales, JewelrySoldMargin, JewelryCountAudit, SoldInvDetails, ActiveInvDetails (the 5 pre-existing reference implementations), InventoryDetails (uses `ClickOkTextInDialog()` + a hard 300s DataItem-render gate — never depended on Enter to begin with), SalesDetail, IntakeDetail (shared `IntakeClickOkVerified()`/`IntakeSelectSavedReportCommitted()` helpers — the most thorough implementation found), BuysFromPublic, ChekkitInactives, ChekkitInactivesV2, ChekkitInvites, ChekkitInvitesRange (uses the shared `IntakeClickOkVerified()` helper), NicsTransfers.
  **Flagged with a residual concern (still ALREADY-FIXED, not patched this pass — see NEEDS-REVIEW note below): LoanPortfolio2026, LoanReviews, LowDollarBuys, LowDollarLoans.**

- **PATCHED: 5** — were AFFECTED (bare Ok-click or bare `{Enter}` with no verification the dialog actually closed before trusting the count/grid). Backed up to `<name>.ahk.bak-clickonce-okfix-2026-07-30` before editing, then given the Ok-click-with-`{Enter}`-fallback + bounded (~20s) poll for `BoxReportName` to disappear, re-clicking Ok every 3rd iteration, throwing a loud error if the dialog never closes:
  - `FpdCohort.ahk` — bare `ClickByName(Ok)` then trusted `ParseCountFromTitle()` immediately; now verified.
  - `FpdLookback12Mo.ahk` — identical vulnerability/fix as FpdCohort.
  - `Loans75DaysPastDue.ahk` — bare `ClickByName(Ok)` then trusted the title count; now verified.
  - `Loans75GridRead.ahk` — bare click then read `DataItem` rows straight off screen; now verified.
  - `SoldYesterday.ahk` — Inventory-module handler with TWO bugs fixed in one pass: (1) called generic `SelectSavedReport` instead of `SelectInventorySavedReport` (Inventory-module commit bug), and (2) sent a bare `{Enter}` with no close-verification. Both fixed, matching the `SoldInvDetails.ahk` pattern.

- **NEEDS-REVIEW: 0** classified as such, but one item deliberately NOT patched pending a human/next-session decision:
  `LoanPortfolio2026.ahk`, `LoanReviews.ahk`, `LowDollarBuys.ahk`, `LowDollarLoans.ahk` each already has the Ok-click+fallback and a bounded DataItem-grid-render poll from the 2026-07-28 partial-fix pass (see their `.bak-pre-okfix-2026-07-28T154508` predecessors). However, in all four, when the render poll times out with 0 DataItems found, the code currently treats that as a "legitimate empty result" and writes a zero-row sentinel CSV as **success** — with no secondary confirmation (e.g. the "Layouts caret present" check `AgedJewelrySales.ahk` uses) that the dialog actually closed and a real empty grid rendered, rather than the dialog being stuck open. If the Ok-click regression ever recurs on these four, `ParseCountFromTitle()`/the row count would likely also read 0, silently reproducing the exact false "0 rows success" this whole audit exists to prevent. This was NOT patched now because it changes existing empty-result business logic (not simply adding a missing verification step) on production financial-reporting handlers that could not be tested live in this session — **next session/human should decide whether to add a Layouts-caret (or equivalent) confirmation before accepting the zero-row sentinel in these four files**, the same way AgedJewelrySales already does.

All 5 patches were spot-checked by diffing against their `.bak-clickonce-okfix-2026-07-30` backups and match the intended pattern (Ok-click-with-fallback, then bounded `BoxReportName`-gone poll, throw-on-timeout). None of this session's changes have been live-verified against Bravo (no Parallels/computer-use grant available) — the next scheduled run against each patched handler is the real-world test.
