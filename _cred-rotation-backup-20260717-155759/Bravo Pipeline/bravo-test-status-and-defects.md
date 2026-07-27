# Bravo Test Campaign — Status & Defect Log

**Started:** 2026-06-17 · Per-scheduled-task testing of Bravo report cells (store WAY, run via the watcher). Live tracker.

---

## Scorecard — list-view cells (smoke `scheduled-task-smoke-2026-06-17`)

| Scheduled task | Cell | Result |
|---|---|---|
| daily-funds-verification | `safe-register-journal` | ✅ PASS — 5 rows |
| weekly-aged-inventory-report | `aged-inventory-summary` | ✅ PASS — 16 rows |
| weekly/monthly-employee-rankings | `employee-activity` | ✅ PASS — 13 rows |
| weekly-loan-layaway-review (loans) | `loans-75-days-past-due` | ✅ PASS — 1 loan / $80 (matches grid-read) |
| weekly-loan-layaway-review (layaways) | `layaways` | ✅ PASS |
| chekkit-weekly-review-requests | `chekkit-inactives` | ✅ PASS — 0 rows (verify 0 is correct for WAY today) |
| daily-items-to-price | `items-to-price` | 🔴 DEFECT D-1 — only 43 of 176 rows |
| weekly-fpd-ranking | `fpd-cohort` | 🟠 DEFECT D-2 — title count 22 ≠ 29 rows written |
| monday-store-rankings / analytics | `company-kpis` | ⏳ completing |
| new-inv-weekly-report | `active-inv-details` | ⏳ completing |

**Headline:** 7 cells ran back-to-back with ZERO Bravo hangs (the June 3–10 failure mode did not recur). 6 pass, 2 defects, 2 completing.

---

## DEFECTS — what we're doing about each

### 🔴 D-1 — `items-to-price` captures only 43 of 176 rows (virtualization)
- **Impact:** HIGH. `daily-items-to-price` is ENABLED and posts to #items-to-price daily — it has been **silently under-counting** unpriced inventory (reports ~43 when the real worklist is 176). Not a regression we caused; a latent bug now surfaced.
- **Root cause:** the handler walks the grid (PageDown + "Show More") but the scroll-accumulate stalls — after row ~43 no new DataItems realize (WPF virtualization not advancing).
- **Fix (additive, per program):** clone `ItemsToPrice.ahk` → a hardened grid-read handler with a *correct* scroll-accumulate (scroll the grid's ScrollPattern to force row realization, detect end-of-list by stable total, not by "no new in one pass"). **This virtualization routine is the keystone reusable technique** — the same one EOM/long reports need, so solve it once here and reuse everywhere. Validate: captured rows == the "Price Items" badge count (176). Then cut `daily-items-to-price` over. Goes to the FRONT of Phase 2.
- **Interim:** treat today's items-to-price count as a floor, not a total, until the fix ships.

### 🟠 D-2 — `fpd-cohort` row/count mismatch (22 title vs 29 written)
- **Impact:** MEDIUM. `weekly-fpd-ranking` is DISABLED — no live posting today — but must be fixed before re-enable.
- **Root cause:** the title-bar count (22) and the rows written (29) disagree — likely the handler counts a filtered figure but writes a broader set (or includes non-data rows).
- **Fix (additive):** clone → reconcile so written rows == the authoritative count; validate by shadow against the title count. Phase 2.

---

### 🔴 D-3 — clean-exit / BackToDashboard fragility between back-to-back cells (the real "cascade" cause)
- **Found 2026-06-17:** an `end-of-month` test on WAY did NOT hang on export — it never reached export. It failed at `BackToDashboard` because the PRIOR smoke cell (`active-inv-details`) left the "Custom Inventory Report Generator" dialog open, and EOM's recovery couldn't get past it (clicked "Done" 6×, gave up). Bravo was NOT wedged — fully responsive; cleaned back to dashboard manually.
- **Impact:** HIGH for full/back-to-back runs (the Monday combined run). If any cell doesn't return cleanly to the Dashboard, the next cell fails — this is the true mechanism behind "cascade" failures, distinct from the export hang.
- **Two sub-fixes:** (a) every cell must Cancel/close its report dialog and confirm Dashboard before returning success (e.g., `active-inv-details` leaked its dialog); (b) make the shared `BackToDashboard` robust to an open "*Custom * Report Generator*" dialog (detect + click Cancel). (b) touches shared infra — board to weigh additive-vs-clone.
- **Note on the export hang:** it did NOT reproduce today; EOM last produced a WAY CSV on 2026-06-08. The export hang appears intermittent/partly-mitigated; the clean-exit gap (D-3) is the more pressing blocker for full runs. Grid-read (no export) sidesteps both for list-view reports.

## LIVE RESULTS — 2026-06-17 afternoon

- ✅ **D-3 FIXED & PROVEN.** Added a guarded step to shared `BackToDashboard` (lib/Bravo.ahk, backed up `.bak-pre-d3-cleanexit-2026-06-17`): if a "Custom * Report Generator" modal is open (detected via its unique "New Report" control), dismiss its Cancel BEFORE the Done step. Validated live: EOM ran right after a failed `active-inv-details` left its generator dialog open, and `BackToDashboard: dismissed Report Generator via Cancel (Name) [D-3]` fired — EOM proceeded where it previously dead-looped. Guarded so normal views are unaffected; funds cell re-validated after.
- ✅ **EOM EXPORT PROVEN — NO HANG.** `end-of-month` on WAY exported a real 10,318-byte CSV (134 rows), log `[export-wait] local-file=no bravo-hung=no`. The export hang did NOT occur. (EOM exports to a LOCAL temp path then copies to the share — fast-path, avoids UNC.)
- 🔴 **D-5 — EOM Report Preview exit is sticky (CAUSED a recovery today).** After EOM exports, its DevExpress Report Preview will NOT close via `btnDone` or Esc (the handler looped btnDone 8×, Esc fallback, gave up — left Bravo stuck on the preview; a follow-on cell then couldn't navigate). **ROOT-CAUSE FIX FOUND: send `Ctrl+W`** — it closes the DevExpress preview cleanly (manually confirmed: Ctrl+W → returned to Reports menu → Done → Dashboard). **Action:** add a `Send("^w")` step to the EOM/closing-report preview-exit sequence (and/or a Ctrl+W attempt in `BackToDashboard`'s recovery ladder) so the preview releases without a manual restart.
- 🔧 **Recovery performed:** the stuck preview required closing Bravo and relaunching via `_relaunch_bravo_and_watcher.ps1`; Bravo re-logged-in (watcher credential path), funds cell re-ran green. Bravo is healthy on the WAY dashboard; 6 PM funds run unaffected. Also surfaced: an SSRS browser error (`EmployeeNameDataSet` query failed — relevant to `company-kpis`/employee SSRS reports) and a leftover island-AHK warning dialog (now killed).
- 🟠 **D-4 — `active-inv-details` failed:** "Grid did not render within 120s after click Ok" on WAY, and it left its generator dialog open (the trigger for the D-3 scenario). Separate handler defect to investigate.

**Net:** the export hang is NOT the blocker — it's the **report-preview exit** (D-5, fix = Ctrl+W). With D-3 done and D-5's fix identified, a clean full run is close.

## Monday combined run (`monday-bravo-combined-run`) — coverage

The orchestrator drops these cells: `aged-inventory-summary`, `loans-75-days-past-due`, `layaways`, `employee-activity`, `chekkit-invites`, and **5 per-store `end-of-month`** triggers.

| Component | Tested? |
|---|---|
| aged-inventory-summary, loans-75, layaways, employee-activity | ✅ tested & passing (this campaign) |
| `chekkit-invites` (the Monday cell; `chekkit-inactives` is a sibling) | ⏳ not yet tested directly |
| **5× `end-of-month`** (wide SSRS export reports) | 🔴 NOT TESTED — this is the historical hang risk (ROA/WAY wedge). Phase 3 (export-hardening). |

**So:** the Monday run's list-view parts are validated; the **EOM export cells are the untested risk** and are the real reason the orchestrator has been fragile. Test plan: (1) validate one `end-of-month` cell in isolation per store under the export profile (CS-toggle opt-in + cascade), then (2) test `chekkit-invites`, then (3) dry-run the orchestrator end-to-end to a test channel before trusting the Monday 5:38am run.

---

## Next actions (sequenced)
1. **D-1 virtualization fix** (keystone) — front of Phase 2.
2. **D-2 fpd reconcile** — Phase 2.
3. **EOM cell test** per store (Phase 3) — unblocks the Monday combined run.
4. Test `chekkit-invites`; then orchestrator dry-run to a test channel.
5. Re-run this smoke per store (CUL/HAR/LEX/ROA) to catch store-specific issues.
