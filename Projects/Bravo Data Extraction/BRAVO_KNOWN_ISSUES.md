# READ-FIRST INDEX (maintain this block; chronological log below)

Any session diagnosing Bravo MUST read this index before forming a hypothesis,
and MUST verify+stamp any OPEN item's next-run outcome before starting new work.

## SOLVED - DO NOT RE-DIAGNOSE OR RE-PROPOSE (moved from OPEN 2026-08-04)
- 2026-08-03/04: post-to-accounting-gl (Consolidated General Ledger) appeared to hang on preview render for EVERY store attempted ("Export... never appeared" / "preview ribbon did not appear"). TWO FIX ATTEMPTS chasing a Continuous-Scrolling render-hang theory (toggle-off after the wait, then toggle-off before the wait with longer timeouts) BOTH FAILED live-tested 2026-08-03/04 — because Continuous Scrolling was never the actual cause.
- ACTUAL ROOT CAUSE (found 2026-08-04 via direct computer-use observation of a live run, not more timeout-guessing): Bravo's Consolidated GL report REFUSES to open at all if ANY day inside the requested date range is still unposted ("Post to Accounting" not yet run for that day). Submitting the report configuration in that state pops a `Warning` dialog — "There are dates that need to be posted first: <date>" — which the shared `DismissPopups()` correctly auto-dismisses, and then the automation is left waiting on a preview window that will NEVER appear, because the report was never generated. Every "did not render" / "ribbon did not appear" error of the last two days was this warning being silently swallowed, not a slow render.
- Confirmed live 2026-08-04: HAR had 7/31/2026 still unposted (visible on the Post to Accounting screen, "Days to Post to Accounting: 2"). Manually clicking that day's Post button posted it instantly and correctly (no rendering issue whatsoever). Immediately after, the exact same post-to-accounting-gl trigger for HAR/2026-07-01..2026-07-31 succeeded on the first try — 48 rows, real CSV written to output/2026-07-31_HAR_post-to-accounting-gl.csv, duration 69.6s (i.e. once the block is gone, this report is NOT slow).
- FIX: no AHK code change was actually needed for post-to-accounting-gl itself (the CS toggle-off block from the two failed attempts is harmless dead code — verified it does not interfere with a healthy run — but should be removed or clearly re-commented next time this file is touched, since it no longer reflects reality). The real fix is procedural/sequencing: `post-to-accounting-post` (Step 1) MUST actually succeed in posting every day through the target end date before `post-to-accounting-gl` (Step 2) is attempted for that store/range. `eom-bravo-gl-export`'s own SKILL.md already runs Step 1 before Step 2 — the 2026-08 failures happened because Step 1 itself was silently failing for HAR (see the "could not click Post button" entry below) and nothing downstream checked that Step 1's per-store result was actually clean before Step 2 ran anyway.
- REMAINING GAP: `post-to-accounting-gl`'s error message ("preview ribbon did not appear") does not distinguish "blocked by an unposted day" from "something is actually wrong". A future improvement would be to detect the `Warning`/`txtMessage` "dates that need to be posted first" text specifically and surface that as its own clear error rather than falling through to a generic timeout — would have made this a 5-minute diagnosis instead of a 2-day one.

## SOLVED 2026-08-09 - large-grid COUNTS no longer need the paging fix (workaround, additive)
- The DevExpress virtualiser paging bug (below, STILL OPEN) blocks any pull that needs full
  ROW DETAIL from a grid larger than ~270 rows. It does NOT block getting the ROW COUNT.
- Every Bravo grid row carries an accessibility Name of the form: Row N of TOTAL, Column ...
  TOTAL is the complete row count and is readable from the FIRST rendered page, before any
  scrolling. reports/BuysFromPublic.ahk already parses it (line ~329) purely to detect truncation.
- NEW reports/JewelryCaseCount.ahk (cell jewelry-case-counts) reads TOTAL and stops. Proven live
  2026-08-09 on WAY: Rings=329 read in 11s with zero paging, on the exact grid that hung the
  2026-08-06 probe at 22 of 327. All 5 categories, 5/5 success, 324s including 5 report runs.
- RULE OF THUMB going forward: if a task only needs HOW MANY, do not walk the grid - read the
  header total. Same technique ItemsToPrice.ahk already uses for its Price Items counter. Only
  walk the grid when the per-row DATA is actually consumed downstream.
- This does NOT fix the paging bug and does not claim to. Full-inventory ROW exports are still
  blocked and still fail loudly via the truncation guard.
- ALSO CLOSED by the same run: the open question of whether the 5 Claude Jewelry Audit saved
  reports need a Location filter to scope to case-only stock. They do NOT - every category
  landed within 1-3 of a manager count sheet. And Chains + Necklaces = 63 vs the sheet's single
  Necklaces line of 64, confirming those two reports must be summed. See the Jewelry Count
  Reconciliation STATUS.md 2026-08-09 entry.

## OPEN / AWAITING VERIFICATION
- 2026-08-04: post-to-accounting-post's `PtaPostClickPostFor` ("real-click" the per-day Post button) intermittently fails with "could not click Post button" even though the button is visibly present and a genuine manual mouse click on the same button works instantly (verified live on HAR 7/31/2026 2026-08-04). The function already uses a physical MouseMove+Click (not synthetic UIA Click) with a 30-pass scroll-into-view loop, so the bug is likely in the viewport-band math (bandTop/bandBot) or a stale grid re-render race, not a "needs real-click" issue like the GL Ok-button had. Reproduced 2x on HAR earlier in this same investigation before the manual post; the other 4 stores (CUL/LEX/ROA/WAY) posted successfully via the automation on the very next run with no code change, so this is intermittent, not a hard failure — needs a live repro with UIA element dump (log the row's BoundingRectangle vs bandTop/bandBot on failure) to pin down before attempting a fix. Do not re-attempt a blind timeout/reorder fix here — that pattern already cost 2 days on the GL issue above.
- 2026-08-03: Truncation guard is LIVE in the shared walker (see SOLVED). Remaining follow-up: large grids still only yield ~78-268 of 2331 rows before the DevExpress virtualiser stops - the guard now makes that a loud failure instead of silent bad data, but a paging fix is still needed before any full-inventory pull can succeed. Small pulls unaffected.
- 2026-08-03: ActiveInvDetails.ahk inv-select fix applied and verified live. Other Inventory-module handlers in the 07-30 ALREADY-FIXED bucket need the same re-check.
- 2026-08-03: Store-hours gate added to the jewelry scheduled task (Sun skip / Wed CUL-only). AWAITING first live Wednesday (2026-08-05) and Sunday (2026-08-09) to confirm no false alarm.
- 2026-07-31: Confirm-dialog fix rev2 in lib/Bravo.ahk BackToDashboard: clicks btnYes when IsEnabled and not IsOffscreen (dialog = txtMessage "Are you sure you want to cancel your changes?" + btnYes/btnNo; elements persist disabled when closed, so existence alone is NOT a valid check; there is no element named "Question"). Backup .bak-pre-question-dialog-fix-2026-07-31T1630. AWAITING live verification.
- 2026-07-31: scrap26 / scrap-2026 bucket handler exits via Cancel, triggers the Question dialog, reports SUCCESS, and leaves Bravo wedged for the next task (proof: scrap26-2026-07-31T13-13-39-WAY log 14:39-14:40 + jewelry-count-recon-2026-07-30b total failure at 15:49). Owner session must patch its exit to answer Yes or use a clean Done path.
- 2026-07-30: _recover_to_dashboard.ahk now calls BackToDashboard(4). PARTIALLY VERIFIED 07-31: it ran, but hit the then-unknown Question dialog (now handled, see above).
- 4 zero-row handlers (LoanPortfolio2026, LoanReviews, LowDollarBuys, LowDollarLoans) still accept a 0-row grid as success without confirming the generator dialog closed. Awaiting decision (see 2026-07-30 audit entry).
- Jewelry Count Reconciliation: desktop task IS REGISTERED and fired on schedule 2026-08-02 (first fire, a Sunday - see 08-03 entry). Formerly needed registration (SKILL.md at Scheduled/jewelry-count-reconciliation/ rewritten 2026-07-31 with the proven protocol; register daily 7:45 PM ET). Cloud watchdog already live at 9:30 PM ET. 2026-07-30 recon COMPLETE and posted to #jewlery-counts 2026-07-31. The 2026-07-30 pull COMPLETED 2026-07-31 16:51 after the wedge was cleared (jewelry-count-recon-2026-07-30c: all 5 stores success, CUL 13 / HAR 17 / LEX 10 / ROA 29 / WAY 28 rows). Rev2 BackToDashboard showed no regression across the full 5-store cycle.

## SOLVED - DO NOT RE-DIAGNOSE OR RE-PROPOSE
- Watchdog too slow / could be masked by unrelated tasks: 2026-08-02, see full writeup below. _watchdog.ps1 now scopes staleness to the pending trigger's own log/result file (not the whole logs\ dir), threshold tightened 15min->4min, throttle 20min->8min, Task Scheduler cadence tightened 15min->2min. Backup: _watchdog.ps1.bak-pre-tighten-2026-08-02.
- Silent grid truncation (partial reads reported as SUCCESS): FIXED 2026-08-03 in the shared walker WriteBuysGridToCsv (reports/BuysFromPublic.ahk, used by ~15 handlers incl. jewelry-count-audit, sold-inv-details, items-to-price, buys-from-public, loan-portfolio). The walk now compares captured rows against the grid's own "Row X of TOTAL" and throws before writing any CSV when materially short (tolerance: >5 missing AND <98% captured, so group/summary-row quirks do not break working reports). VERIFIED LIVE BOTH WAYS 2026-08-03: (A) active-inv-details WAY -> "Grid walk truncated: captured 78 of 2331 rows (2253 missing)", status=error, and NO partial CSV left on disk; (B) jewelry-count-audit WAY 2026-08-01 -> "captured all 39 rows", wrote 39, status=success. Backup: BuysFromPublic.ahk.bak-pre-truncation-guard-2026-08-03.
- UTF-8 BOM in logs/_recover_result.txt: already stripped in bravo_health_gate.sh (tr -d CR+BOM, lines ~185/~214). Not a live bug.
- Stranded Ad-Hoc generator dialog wedging recovery: fixed 2026-07-30 via BackToDashboard(4) in _recover_to_dashboard.ahk.
- Bravo 2026.6.0.79 ClickOnce Enter-doesnt-confirm regression: all 71 reports/*.ahk audited 2026-07-30; 5 patched; 48 not applicable; 18 already fixed.
- False-zero fallback in JewelryCountAudit.ahk: removed 2026-07-31 (backup .bak-pre-falsezero-fix). JewelrySoldMargin/AgedJewelrySales were never broken - they are the reference implementations.

## TRIED AND FAILED - DO NOT RE-PROPOSE
- Esc / Cancel / btnCancel to escape a Question confirmation dialog: re-raises it, never answers it.
- Session-1 scheduled-task trick to relaunch Bravo after force-kill: unreliable on 2026.6; direct ClickOnce .appref-ms Start-Process launch is the working method (see 07-28 entry).
- Cloud-scheduled (claude-code-remote) triggers for Bravo work: sandbox cannot reach the VM. RE-CONFIRMED by live self-test 2026-07-31: a scheduled cloud session has NO remote-devices bridge at all (no osascript, no Chrome, no filesystem). Bravo tasks run from the desktop scheduler only. Cloud triggers ARE useful as Slack-only watchdogs (jewelry-count-reconciliation-watchdog, 9:30 PM ET, checks #jewlery-counts for the daily post).
- Force-kill of Bravo as a recovery rung without a proven relaunch path: left Bravo down for hours on 07-31.

---

## 2026-08-03 PM - CRITICAL: grid walker SILENTLY TRUNCATES large grids (reports success on 11% of rows)

- Found while calibrating the jewelry case-count v2 design. Ran active-inv-details for WAY.
- The grid reported 2330 total rows. The walker captured 268, hit "no DataItems on pass 16",
  stopped, wrote 268 rows, and reported **SUCCESS: 268 data rows**. No warning, no error.
- This is the same class of defect as the false-zero bug fixed 2026-07-31, but worse: a zero-row
  result is obviously suspicious, whereas 268 plausible-looking rows will be silently analysed as
  if complete. ANY analysis built on a large-grid pull may be quietly wrong.
- The walker logs "seen=N/TOTAL" every pass, so the true total IS known at walk time. The fix is
  to compare final captured count against that TOTAL and throw when short (with a small tolerance
  for genuinely virtualised trailing rows), instead of trusting "no new items on this pass".
- SCOPE: affects any handler using the shared grid walk on a grid larger than the virtualisation
  window (~270 rows observed). Small pulls (jewelry-count-audit, items-to-price, safe-register)
  are well under this and are unaffected - their totals matched exactly. Needs an audit of which
  scheduled pulls routinely exceed ~270 rows: end-of-month, inventory-details, loan-portfolio,
  aged-inventory are the likely candidates.
- FIXED SAME DAY 2026-08-03. Guard added after the loop in WriteBuysGridToCsv: compare captured
  count to the grid-reported total, throw BEFORE writing the CSV when materially short. Tolerance
  >5 missing AND <98% captured so grids that report group/summary rows keep working.
- VERIFIED LIVE, BOTH DIRECTIONS:
    A) active-inv-details WAY (2331-row grid) -> ERROR "Grid walk truncated: captured 78 of 2331
       rows (2253 missing). Refusing to report a partial grid as a complete result." No partial
       CSV written. Previously this same pull returned 268 rows as SUCCESS.
    B) jewelry-count-audit WAY 2026-08-01 (39-row grid) -> "captured all 39 rows", wrote 39,
       status=success. Small pulls are unaffected by the guard.
- STILL OPEN (separate defect): the DevExpress virtualiser stops yielding new rows early on big
  grids (78 and 268 captured on two runs of the same 2331-row report - not even deterministic).
  Full-inventory pulls therefore CANNOT succeed yet; they now fail loudly instead of lying. Fixing
  the paging itself is the next piece of work if a large pull is ever needed. The jewelry case v2
  design deliberately sidesteps this by using a category-filtered saved report (~550 rows).

## 2026-08-03 PM - ActiveInvDetails.ahk was still broken by the 2026-07-28 ClickOnce regression

- The 2026-07-30 enterprise audit classified ActiveInvDetails as ALREADY-FIXED. It was not: it had
  received the Ok-click half of the fix but still called the generic SelectSavedReport, which does
  not commit the combo in the Inventory module. Live proof 2026-08-03 13:05: "SelectSavedReport:
  could not select 'Claude Active Inv Details' via click or keyboard walk".
- FIXED: now calls SelectInventorySavedReport, matching SoldInvDetails.ahk. Verified live at 13:09
  - the saved report selected and the report ran. Backup:
  reports/ActiveInvDetails.ahk.bak-pre-invselect-fix-2026-08-03.
- LESSON: the 07-30 audit's ALREADY-FIXED bucket was judged on the Ok-click pattern alone and did
  not separately verify the Inventory-module combo call. The other handlers in that bucket that
  drive the Inventory module should be re-checked for the same half-fix.

## 2026-08-03 PM - jewelry case v2 design: what the calibration established

- Joshua confirmed (2026-08-03): the manager count is the DISPLAY CASE ONLY. Nothing in the safe.
  Layaway and repair items are NOT counted. Decision: do NOT change what managers count - filter
  Bravo to match the humans, not the reverse.
- BLOCKER 1: the "Claude Active Inv Details" saved report does NOT export a Location column
  (actual header: Number,Status,Category,Description,Cost,Price,Date). Without Location we cannot
  separate case stock from safe/layaway/repair stock.
- BLOCKER 2: full active inventory is 2330 rows at WAY - inside the silent-truncation zone above,
  and ~3 minutes per store.
- BOTH are solved by ONE new saved report (additive, Rule #4 safe): "Claude Case Jewelry" =
  jewelry categories only + Location column exported. That lands ~550 rows (well under the
  truncation window), runs fast, and lets the location filter live in Bravo rather than in code.
- Location values observed in WAY data: SALESFLOOR, SAFE, BUYS, and bin codes B4/B7/B8/B9/B15/
  B26/B27. Which set equals "the case" is answerable empirically - pull jewelry-with-location and
  find the subset summing to the manager's PM count (WAY 2026-08-01 PM = 538). No need to ask.

## 2026-08-03 - Sunday 08-02 "total failure" was NOT a failure: stores are CLOSED Sun (and Wed)

- The 2026-08-02 scheduled run reported all 5 stores failing with "Grid never rendered after 2
  attempts (~3 min)" on both passes, and no manager count sheets in #end-of-day.
- ROOT CAUSE: 2026-08-02 was a SUNDAY. All 5 Valley Pawn stores are closed Sunday, so there were
  zero sales and no staff to count. The Sold Inventory report correctly returned an EMPTY grid,
  and the false-zero guard added 2026-07-31 (correctly) refuses to call 0 rows a clean result.
  Two correct behaviours combined into a false alarm. Bravo itself was healthy all evening -
  daily-funds-verification succeeded across all 5 stores at 18:03 that same night.
- CORROBORATION: 2026-07-29 was a Wednesday and produced exactly ONE jewelry CSV (CUL); the other
  four stores are closed Wednesdays. Same mechanism, previously unnoticed.
- VERIFIED 2026-08-03 09:30: re-pulled the identical report for Saturday 2026-08-01 (all stores
  open). First store returned 23 rows immediately. The handler, the grid wait, and the guard are
  all healthy. Nothing in lib/ or reports/ needed changing - NO code was touched.
- FIX (scheduled task only, additive): Scheduled/jewelry-count-reconciliation/SKILL.md now opens
  with a STORE-HOURS GATE - Sunday = skip entirely and post nothing; Wednesday = run CUL only;
  other days = all 5. An empty grid on a normally-open day with no EOD sheet is reported as
  "no data - store may have been closed", not as a failure. Backup:
  SKILL.md.bak-pre-hours-gate-2026-08-03. Cloud watchdog (trig_01Ep98CHWU9z3biWp9sGxMBi) given the
  same Sunday gate so it does not alarm on a correct no-op.
- STORE HOURS (source valley-pawn-context): CUL Mon-Sat, closed Sun. HAR/WAY/LEX/ROA Mon, Tue,
  Thu, Fri, Sat - closed WED and SUN.
- LESSON for every scheduled Bravo task: before treating an empty report as a failure, check
  whether the store was actually open that day. Other daily tasks may carry the same blind spot.

## 2026-07-31 PM - ROOT CAUSE of the recurring wedge: unanswered "Question" confirmation dialog (Scrap Bucket Detail)
- Screenshot jewelry-count-recon-2026-07-30b_backtodashboard-unknown-state.png shows the true stranded state: Scrap Bucket Detail (AUGUST 2026 GOLD SCRAP, WAY) with a modal "Question - Are you sure you want to cancel?" dialog on top.
- Chain: scrap26 handler (14:39) exits via Cancel -> Question dialog raised -> BackToDashboard clicks btnCancel 6x (re-raising it each time), Esc fallback fails -> handler still reports SUCCESS (it already had its 19 rows) -> Bravo left wedged -> jewelry-count-recon-2026-07-30b (15:49) loses all 5 stores (4x EnsureStore failed + 1x BackToDashboard failed).
- FIX: BackToDashboard (lib/Bravo.ahk) now answers Yes when BOTH a "Question" element and a "Yes" button are present, before the modal-Cancel checks. Backup: lib/Bravo.ahk.bak-pre-question-dialog-fix-2026-07-31T1630. Not yet live-verified against a real wedge.
- REMAINING: the scrap handler itself should stop leaving the dialog (it reports SUCCESS while wedging Bravo - a pipeline-wide hazard); fix by its owner session using the same Yes-answer pattern.


---
## 2026-08-02 - Watchdog hardening: scoped staleness + tightened cadence (fixes the recurring stranded/wedge outages)

CONTEXT: items-to-price daily run wedged mid-ROA-store-switch — log froze immediately after
"SwitchStore: double-click store row 'Roanoke'" for 10+ minutes with ZERO further log output.
Root cause: `DoubleClickByName` (lib/Bravo.ahk) issues `elem.Click("Left", 2)`, a synchronous
UIA COM call with no internal timeout. If the target window/provider is unresponsive at the
moment of the call, the whole single-threaded AHK watcher process blocks forever inside that
one call — no AHK-level timeout wrapper can intervene because the blocking happens inside the
call itself, not in the polling/wait logic around it. This is almost certainly the same root
disease behind the "no-dashboard" (07-22/07-23/07-29) and "no-window" (08-01) recurring
outages logged above — different UIA call, same failure mode: a hang with no internal timeout
that only an EXTERNAL process can clear.

The external backstop (_watchdog.ps1 + Windows Task Scheduler "BravoWatcherWatchdog") already
existed and already does the right thing (force-kill + relaunch via _restart_watcher.ps1,
proven clean today: I did it manually, watcher recovered in <60s). It just wasn't fast or
reliable enough to fire automatically:

1. BUG: staleness was `most-recently-modified file across the entire logs\ + results\ folders`.
   Those folders are shared by every other scheduled automation (funds verification, KPIs,
   directory monitor, etc.), so any unrelated task writing a log file reset the "activity"
   clock and masked a truly-hung watcher. This is the likely reason the watchdog never fired
   during the 07-22 through 08-01 recurrences despite matching symptoms.
2. SLOW: 15-min Task Scheduler poll interval + 15-min staleness threshold = up to ~30 min
   before even detecting a hang, on top of the masking bug above.

FIX (additive, parameter/scope-only — no change to any click/UI logic, so zero regression risk
to the automation itself):
- _watchdog.ps1: staleness now computed ONLY from the pending trigger's own
  `<triggerId>.log` / `<triggerId>.result.json` (looked up by trigger id), not the whole
  folder. Threshold 15min -> 4min (comfortably above the ~90s max legitimate gap observed
  during grid-walks/session-switches). Restart throttle 20min -> 8min. Backup:
  `_watchdog.ps1.bak-pre-tighten-2026-08-02`.
- Task Scheduler "BravoWatcherWatchdog": repeat interval 15min -> 2min (re-registered via XML
  export/edit/re-import since the task uses InteractiveToken logon, no password needed).
  Worst-case detection+restart latency: ~30-45+ min (or never, if masked) -> ~6 min.
- Verified: PowerShell tokenizer syntax-check clean; dry-run on live healthy state exits 0
  with no spurious log entry; schtasks /query confirms "Repeat: Every: 0 Hour(s), 2 Minute(s)".
  NOT yet verified against a live real hang (none occurred since the change) — next occurrence
  of any stranded/wedge signature should self-clear within ~6 min with a `RESTART:` line in
  logs/watchdog.log. If it doesn't, re-open this item.

REMAINING (longer-term, deferred — needs a proving ground per Rule #3, higher regression risk):
replace `elem.Click()` UIA COM calls in lib/Bravo.ahk (ClickByName/DoubleClickByName) with
native coordinate-based mouse clicks (derived from BoundingRectangle), which post Windows
messages asynchronously instead of blocking synchronously inside the calling thread. This
would eliminate the hang at its source rather than relying on external recovery, but touches
the single most shared low-level primitive in the whole pipeline and needs to be proven in
isolation before touching hardened handlers.

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

## 2026-08-02 PM - NEW: jewelry-count-audit grid-never-renders, all 5 stores, both original + retry pull
CONTEXT: jewelry-count-reconciliation scheduled task (~7:45 PM run) triggered
jewelry-count-recon-2026-08-02-auto for CUL/HAR/LEX/ROA/WAY. All 5 cells
failed identically: JewelryCountAudit.ahk clicks Ok, generator dialog closes
("report is running"), then no DataItem rows ever render within 90s. The
false-zero-fix retry (re-click Ok) also failed every time with
"ClickByName: element not found: Ok" - the Ok button is gone/not found on
retry, suggesting the report view is in some intermediate state, not simply
slow. Handler correctly throws rather than reporting a false zero, and
BackToDashboard/Done recovery worked cleanly every single time (no wedge, no
stranded dialog) - this is NOT the Question-dialog wedge documented above.
RETRY: a fresh trigger (jewelry-count-recon-2026-08-02-auto-b) was run per
protocol ~30 min later. Same result on 4/5 stores (HAR, LEX, ROA, WAY -
identical "Grid never rendered" after 90s+retry). CUL failed one step
earlier on the retry: could not select 'Claude Sold Inv Details' from the
saved-report dropdown at all (all 3 selection strategies + 3 attempts
failed) - a different symptom than the first pass, where CUL's dropdown
selection succeeded fine and only the grid render hung.
PATTERN: identical failure across all 5 stores on both attempts, ~40-90 min
apart, with two different symptoms (grid-render timeout vs dropdown-select
failure) both traceable to the "Claude Sold Inv Details" custom report
specifically. This looks like a live Bravo-side issue tonight (report
definition, server-side data prep, or ClickOnce client state) rather than a
UIA timing/automation bug - the existing 90s-wait + retry-once + clean
recovery logic (correctly) behaved exactly as designed and still could not
get real data.
STATUS: OPEN / UNRESOLVED. Not force-killed or further retried tonight per
jewelry-count-reconciliation's failure protocol (retry ONCE only). Full
detail in Jewelry Count Reconciliation/STATUS.md RUN RECORD 2026-08-02.
NEXT STEP for whoever picks this up: on 2026-08-03, check whether
'Claude Sold Inv Details' or any other saved report at any store shows the
same rendering hang. If yes across multiple reports, this is likely a Bravo
server/client-side regression, not specific to jewelry-count-audit - escalate
to Bravo support rather than continuing to patch the AHK handler.


---
## RUN -- 2026-08-03 (PAWN WALK) -- NEW FINDING: layout gate false-PASS on stale Age-based data
intake-detail (Claude Pawn Walks) for 2026-08-02: Bravo healthy all run (health gate PASS <35s, no restart needed). Trigger claimed instantly, cycled all 5 stores cleanly (no window loss, no wedge -- WAY worked fine this time, breaking its 5-run losing streak).

Result: CUL failed the old way (3/3 selection attempts exhausted, "wrong report / no item columns"). HAR/LEX/ROA/WAY all reported SUCCESS with the layout gate passing on attempt 1 ("correct report confirmed, item-detail columns present") and wrote 42-45 rows each (173 total).

BUT: inspected the actual CSV contents -- every single row across all 4 "successful" stores shows Disposition Date 6/16 or 6/18/2026 and a UNIFORM Age of 46-48, i.e. the same stale active-loan snapshot from ~6 weeks ago, completely unrelated to yesterday's (8/2) real activity. This is the SAME recurring "Claude Pawn Walks loads with Age= criteria instead of Transaction Date range" regression documented 6/16, 6/20, 7/10, 7/11, 7/27 -- but this is the FIRST time it slipped past the automation's own layout-verify gate undetected, because that gate only checks column PRESENCE (Category/FullDescription exist) not the actual date-criteria correctness. Compile script's single-day Disposition-Date backstop filter correctly rejected all 173 rows (working as designed), so run_daily_intake.py produced a clean-looking but empty (items=0) summary -- this is NOT a real quiet day, it's 100% garbage-in getting correctly filtered to zero.

Treated as a FAILURE per the 7/11 precedent (false quiet-day trap), not posted to #pawn-walks. Joshua DMed per v2 policy (plain one-liner only).

NEXT SESSION priority:
1. The core regression is still unresolved after 6 documented occurrences (6/16, 6/20, 7/10, 7/11, 7/27, now 8/3). It needs the permanent Bravo-side fix: per store, Loans/Buys -> Custom Reports -> open 'Claude Pawn Walks' -> re-save criteria as Transaction Date range (not Age=), confirm columns Ticket Number/Category/Full Description/Loan Amount, confirm list-view Saved Layout is the 4-col layout. This has been recommended 5+ times and not yet actioned.
2. Harden IntakeDetail.ahk's layout-verify gate to ALSO check date-criteria correctness (e.g. sample a row's Disposition/Transaction-adjacent date field against the requested range, or verify the criteria control shows 'Transaction Date' not 'Age' before running), not just column presence -- today's false-PASS shows column-check alone is insufficient.
3. Encouraging sign: WAY completed cleanly for the first time in 5 runs (7/21, 7/23, 7/27, 7/28, 7/31 all had window-loss) -- no window-loss issue today. Worth noting in case it self-resolved (VM reboot, resource pressure change) or was luck.

---

## 2026-08-03 -- CRITICAL: post-to-accounting-gl (Consolidated General Ledger) hangs on preview render, blocks sales-tax-monthly-update entirely

sales-tax-monthly-update ran for July 2026. No 2026-07-31_<STORE>_post-to-accounting-gl.csv existed yet (eom-bravo-gl-export had not produced them), so the task's own fallback triggered post-to-accounting-gl directly, then separately triggered eom-bravo-gl-export's own trigger chain (posting phase, then GL-export phase) after the direct attempt also failed.

**Posting phase (post-to-accounting-post) completed with partial success** -- 18-24 unposted July days existed per store (nobody had posted since the last run touched these stores). Posted OK except: CUL 7/24 (could not click Post), HAR 7/29 + 7/31 (could not click Post / still unposted after 90s), LEX 7/31, ROA 7/31, WAY 7/31 (all "could not click Post button"). Every store failed to post 7/31 specifically except CUL -- worth Joshua's attention since 7/31 is the last day of the month and matters for accuracy of ANY report pulling through end-of-July.

**GL-export phase (post-to-accounting-gl, "Consolidated General Ledger") failed 100% of attempts** -- 3 full-cycle attempts across ~50 minutes (12:44, 13:06/eom-chained, 13:19/manual retry), covering CUL (3/3 failed) and HAR (3/3 failed, one via EnsureStore/login-loop wedge, two via the same render timeout) before the run was called off. Failure signature is identical every time:
```
step 4: click Ok (immediate, verified close)
[popup] dismissed via btnOk
... ~60-90s silence ...
ERROR: UIA click sequence failed: Consolidated GL preview did not render within 60s (Export... never appeared)
```
This matches the documented-but-unpatched "Continuous Scrolling re-enables on every Bravo restart" issue (see bravo-context skill, UI Gotchas section) -- Bravo's Report Preview ribbon toggle resets ON after every restart, and wide multi-column reports (EOM, this GL report, etc.) then flatten into one continuous WPF canvas that locks the UI thread for 3+ minutes. bravo-context already flags that `EndOfMonth.ahk` and `EndOfDayConsolidated.ahk` still need the toggle-off patch applied to the 7 closing-report handlers on 2026-05-29. **PostToAccountingGL.ahk needs the same patch — add it to that list.**

`bravo_health_gate.sh` correctly detects Bravo as "running + responsive" during these hangs (Rung3 PASS) because Bravo's process is alive and the Dashboard nav responds -- it does NOT detect a wedged Report Preview pane mid-render. Running the health gate mid-hang does not unstick the in-flight AHK cell; only a full stop/relaunch (or the AHK-side toggle-off fix, which is the real cure) will.

**Net result: zero July 2026 GL CSVs obtained for any of the 5 stores.** sales-tax-monthly-update did NOT write anything to Sales Tax.xlsx this run -- correct behavior per forensic-accountant standard (no source data, no entry) rather than guessing or reusing stale figures.

**Fix needed (not applied — additive-only rule, requires the same kind of change already made to the 7 closing-report handlers):** add the "Enable Continuous Scrolling" read-toggle-off-sleep(5000) block to `reports/PostToAccountingGL.ahk` after the report preview renders, same pattern as `DepositsAndPaidOuts.ahk` etc. Until that's applied, expect this same hang on the 6th of every month.

**APPLIED 2026-08-03 (later same day):** block ported verbatim from `DepositsAndPaidOuts.ahk` into `PostToAccountingGL.ahk`, inserted after the preview-render wait and before the Export... click (step 5). Backup: `reports/PostToAccountingGL.ahk.bak-pre-cs-fix-2026-08-03`. This was the standing fix instruction above, now executed. NOT YET LIVE-VERIFIED — the next `eom-bravo-gl-export` or `sales-tax-monthly-update` run must confirm the Consolidated GL preview no longer hangs on export, then move this item to SOLVED.


---
## 2026-08-03 PM -- LIVE-VERIFIED: PostToAccountingGL.ahk Continuous-Scrolling fix did NOT resolve the hang

The toggle-off fix ported into `PostToAccountingGL.ahk` earlier today (see prior entry, backup `.bak-pre-cs-fix-2026-08-03`) was live-tested by `eom-bravo-gl-export` (trigger `eom-gl-export-202607-20260803T142100Z`, ran ~14:21-14:34 ET) for July 2026, all 5 stores.

**Result: 5/5 stores failed identically to the pre-fix behavior.** Same signature every time:
```
[popup] dismissed via btnOk
... ~60-90s silence ...
ERROR: UIA click sequence failed: Consolidated GL preview did not render within 60s (Export... never appeared)
```
Recovery (BackToDashboard, click Done) worked cleanly every time -- this is a report-render hang, not a Bravo wedge. Zero July 2026 GL CSVs obtained for any store, for the second consecutive run.

**CONCLUSION: the toggle-off patch, as inserted, does not fix this handler.** Do NOT mark this item SOLVED. Possible reasons the ported block didn't help (not yet diagnosed, needs a session with live Parallels/computer-use access to inspect the actual ribbon state during a hang):
- The Consolidated GL report's toggle control may live at a different UI location/selector than the 7 closing-report handlers this block was copied from.
- The toggle-off block may be getting inserted at the wrong point in the sequence (before vs. after the specific dialog this report uses).
- This report may have a genuinely different root cause that only resembles the Continuous-Scrolling symptom.

**NEXT STEP for whoever picks this up:** needs a live/supervised computer-use session watching the actual PostToAccountingGL run in Parallels to see what's on screen during the 60-90s hang, rather than another blind code-only patch attempt. Two blind-patch/live-test cycles have now failed to fix this handler.

Also affects: `sales-tax-monthly-update` (same dependency, will fail the same way until this is fixed).

