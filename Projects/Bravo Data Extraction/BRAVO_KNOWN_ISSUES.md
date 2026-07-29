
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
