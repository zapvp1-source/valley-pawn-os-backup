# Bonus Program — Run Log

Newest first. One entry per engine run or material change. Scheduled tasks append here.

## 2026-09-21 — bonus-paid-verify: August 2026 payout — MISMATCH found

Payday 2026-09-18 (August 2026 earning month, close.json). Expected total per `gusto_lines.csv`:
$4,837.84 across 7 people. Actual Gusto payroll (main run check-date 9/18, uuid a6a40624…, +
off-cycle correction check-date 9/21, uuid 30f9d1cb…) paid $5,220.15 in bonus lines. NOT a clean
match — DM sent to Joshua (D03BHQH5VGT) with the breakdown:
- Michael Chambers (HAR) — owed $344.48 — **not paid at all**
- Martin Dowden (LEX $182.51 + ROA $2.00 = $184.51) — **not paid at all**
- Walker Tapley $1,088.26, Uriah Tiglao $555.09, Benjie Moore $1,354.20 (Gusto legal name "George
  Moore"), Joseph Epperly $411.30 (paid via the 9/21 correction) — all match.
- Preston Peters — owed $900, actually paid $1,400 (+$500 via the 9/21 correction run).
- A Gusto employee "Robert Swagger" (uuid 1f74c46d…) received a $411.30 bonus in the main 9/18
  run — not in the August bonus calc at all; same dollar amount as Joseph Epperly's, so possibly a
  UUID mix-up rather than an intentional extra payment. Flagged to Joshua, not corrected (this task
  never touches Gusto).
No changes made in Gusto. Trend tab note not yet added — see follow-up.

## 2026-09-06 — REBUILD + July & August 2026 closes (session: bonus department review)

**Built (all additive, nothing hardened was modified):**
- `bonus_rules.json` — single source of truth: regimes by earning month, thresholds, rates, eligibility,
  data-rail definitions, gates, `field_posting` flag (currently **false** per Joshua 2026-09-06: "do not alert the field").
- `bin/bonus_engine.py` — deterministic engine, stages `collect` / `close` / `targets`. Owns every number and
  every Slack body. Exit 2 = HELD (publishes nothing).
- `bin/render_policy.py` → `BONUS_POLICY_2026-08.md`, `HANDBOOK_01.08_2026-08.md` — generated from the rules
  file so the policy, the handbook and the math cannot drift apart again.
- `ledger/VP_Bonus_Ledger_2026.xlsx` — Qualifiers / Payouts / Trend tabs, rewritten idempotently per month.
- Scheduled: `bonus-month-close-pull` (1st 11:30), `bonus-month-close` (10th 9:00), `bonus-pace-monday` (Mon 9:35),
  `bonus-paid-verify` (Mon 10:00, no-ops except after a payday). `bonus-payday-prep` was blocked by the permission
  classifier — staged at `Valley Pawn OS/pending-tasks/bonus-payday-prep/SKILL.md` for Joshua to register.
- Legacy `monthly-bonus-targets` / `-qualifiers` / `-payout`: **disabled**, kept as rollback holds, delete after
  two clean cycles (Oct + Nov 2026). `fleet/expected_outputs.json` +4 entries, old two marked superseded.

**The data trap this was built to stop.** On 2026-09-05 the monthly-analytics prestage overwrote
`output/2026-08-31_<STORE>_end-of-month.xlsx` with **trailing-12-month** pulls under the same filename.
`bonus_kpis_extract.py 2026-08-31` therefore returned Culpeper August net revenue of **$767,112.67** (~10× real).
The 9/10 legacy qualifiers run would have passed every store on Bridge 1. The engine's gate — an EOM file is only
accepted if its Reporting Dates equal the month, plus a ±60% trailing-12 plausibility band — rejects those files and
uses the sidecar `monthly-analytics/2026-08/same-month-current_<STORE>.xlsx` instead. The same trap was found in
`2025-08-31_*_end-of-month.xlsx` (actually 9/1/2024–8/31/2025) and rejected the same way; Aug-2025 prior-year figures
came from `monthly-analytics/2026-08/same-month-prior_*` and match the tracker to the dollar.

**July 2026 close (regime: Jul-2026 two-bridge).** Only **Roanoke** hit its target ($48,831.78 vs $48,001;
also up YoY vs $32,158.85). Task bonus missed (gold 95.66 dwt vs the 100 bar), so the miss rates apply.
Benjie Moore (Manager) **$732.48**; Preston 1/5 stores × $300 = **$300**. Roanoke associate lines (Joseph Epperly,
hired 7/23) still pending — July's month-range employee-activity CSV did not exist; a pipeline trigger
(`bonus-july-empact-20260906T0110`) is queued behind another session's Monday gapfill. Culpeper $61,751.95 / target
$77,117 ✗, Harrisonburg $42,881.84 / $57,724 ✗, Lexington $21,701.62 / $27,545 ✗, Waynesboro $40,329.99 / $48,694 ✗.
Gusto shows **no bonus paid on any payroll since 2026-07-22**, so July looks unpaid.

**August 2026 close (regime: Aug-2026).** Three stores hit: Harrisonburg $54,413.07 / $53,282, Lexington
$27,754.28 / $26,657, Roanoke $48,167.81 / $43,879. Culpeper $61,998.28 / $72,235 ✗ and Waynesboro $40,705.46 /
$50,721 ✗. Every store missed the task set — the **+15 Facebook followers** goal was missed everywhere
(best was Waynesboro +3), so the miss rates apply across the board. Reviews: ROA 23 ✓, WAY 18 ✓, HAR 11, CUL 9,
LEX 6 (bar is 15). Gold: ROA 166.5 ✓, CUL 162.79 ✓, HAR 147.93 ✓, WAY 79.89, LEX 51.02. Email: all five above 50%.
Top store **Roanoke** (gold + reviews; tie with Waynesboro broken on gold).
Payouts: Walker Tapley $816.20 (de facto lead at Harrisonburg — no titled manager for the full month; Logan Dean
started 8/31), Michael Chambers $258.36, Uriah Tiglao $416.31, Benjie Moore $722.52, Joseph Epperly $156.78,
Martin Dowden $136.88 + $1.20 (GP earned at Lexington and Roanoke; his home store Waynesboro missed —
flagged for Joshua), Roanoke top-store pool $300, Preston $900 (3/5 stores). **Total $3,408.25.**
Not paid, not posted anywhere — output is in Joshua's DM only.

**Ineligible-but-earned (terminated before payout), flagged not paid:** Andrew Clark $584.98 GP, Davon Camber
$425.00, Chonn Grinnage $99.99, Steven Burch $379.99, Cris Lopez $625.93 (all August GP).

## 2026-09-07 — bonus-pace-monday (September MTD pace check)

September `data/2026-09/targets.json` did not exist (month-close-pull hadn't seeded it, and
#bonus-goals had no September post — Sandi asked that morning, unanswered). Ran
`bin/bonus_engine.py targets --month 2026-08` off already-collected August EOM/pipeline data to
generate them (no new Bravo trigger) — targets: CUL $72,645 · HAR $53,216 · LEX $28,158 ·
ROA $45,941 · WAY $50,019. Written to `data/2026-09/targets.json`, source noted as
"bonus_engine targets from 2026-08". Not posted to #bonus-goals — Joshua still needs to send that.

MTD net revenue (9/1–9/6, from newest 2026-09-06 EOM files, Reporting Dates verified as
month-only): CUL $11,413.27 (15.7% of target, 79% of straight-line pace) · HAR $12,884.80 (24.2%,
121% of pace — only store ahead) · LEX $4,077.64 (14.5%, 72% of pace) · ROA $7,145.19 (15.6%, 78%
of pace) · WAY $7,670.20 (15.3%, 77% of pace). All 5 stores had usable data.

Qualifiers: gold 0 dwt closed at every store (normal 6 days in). Reviews and email % left as a
dash — the weekly #google-reviews recap straddles the Aug/Sep boundary so no clean September-only
count exists yet, and no September chekkit-invites-range pull has run. DM'd Joshua
(D03BHQH5VGT) only, per `field_posting: false`.

## 2026-09-07 (cont'd) — WAY September target overridden per Joshua

Joshua asked, mid-session: use the "top store yield over the past year" for Waynesboro's
September target instead of Waynesboro's own trailing-12 historical average, since Waynesboro's
yield was so high last year. Checked: Waynesboro's own trail-12 average (20.03%) is *already* the
highest average yield of any store — so "top store yield" and "Waynesboro's own yield" are the
same store. Read literally as wanting Waynesboro's peak rather than its average, used
Waynesboro's single best trailing-12 monthly yield instead: **22.7918% (November 2025)**, next
closest was Culpeper at 22.59% (October 2025). Applied to August 2026 ending assets ($249,683.44)
→ **September WAY target $56,907** (vs $50,019 under the standard trail-12-average method).
CUL/HAR/LEX/ROA unchanged. Updated `data/2026-09/targets.json` with a `way_override` block
documenting the reasoning and both numbers. Not posted to #bonus-goals — `field_posting` is still
false; drafted for Joshua's DM instead.

## 2026-09-09T09:58 — sheet_sync 2026-08
Sheet refreshed with 2026-08 actuals; 2026-09 targets from sheet: CUL $63,239, HAR $52,739, ROA $57,087, LEX $32,065, WAY $41,335. Plan source: sheet.

## 2026-09-09 — interactive session with Joshua: target method review + sheet rebuild
Findings: (1) trail-12 yield-on-ending-assets penalises asset growth (r=-0.37 over 95 store-months; fast-growth months average 15.35% yield vs 17.28% flat); (2) yield is seasonally distorted because assets fall in tax season while revenue rises (Mar implied yield 1.09x, Jul 0.93x) — hit rate by month under the live method ran Jan 100%/Mar 100%/May 20%/Jul 20%; (3) Gusto actual store-only bonus TTM Sep25–Aug26 = $29,786 (prior year $35,594; calendar YTD +34%; Preston separately +96%); (4) Facebook +15 qualifier confirmed NOT implemented — Roanoke August mis-scored, $587.00 owed; (5) the plan sheet had gone stale in May and its monthly targets were unusable. Actions: sheet rebuilt (annual plan preserved, seasonal spread, run-rate floor); `bin/sheet_sync.py` added; `bonus-month-close-pull` step 7 now calls it; `data/2026-09/targets.json` rewritten from the sheet with the trail-12/WAY-override numbers kept under `superseded`; `_proposals[0]` in bonus_rules.json holds the sandbox regime (effective 2999-01, never selectable). `bin/bonus_sandbox.py` and `sandbox/2026-08/` hold the comparison runs. No live regime rates changed. Nothing posted to the field except the #eom-task-rankings format check Joshua requested.

## 2026-09-09T17:48 — sheet_sync 2026-08
Sheet refreshed with 2026-08 actuals; 2026-09 targets from sheet: CUL $63,239, HAR $53,804, ROA $47,629, LEX $27,444, WAY $41,335. Plan source: sheet.

## 2026-09-10 — bonus-month-close (scheduled, 10th 9:00) — August 2026 DM'd to Joshua
Data (reviews.json, fb_gains.json, roster.json, targets.json) and the engine `close --month 2026-08`
run were already on disk from earlier today's rate-correction rebuild (`out/2026-08/close_report.md`
generated 2026-09-10T10:55:57, using the corrected 2%/2.5% mgr and 4%/5% associate rates). Verified
Joshua's DM history had NOT yet received the August payout content (checked before resending —
nothing else on the fleet-note/mail-brief/backup-health/Bald-Rock posts between 10:00 and 11:19
today mentioned bonus). Sent the full payout breakdown + qualifiers table to Joshua's DM
(D03BHQH5VGT) with the approve/hold prompt. `field_posting` is false — nothing went to
#bonus-goals or any store/manager.

**Stores that hit:** Harrisonburg ($54,413.07/$53,282), Lexington ($27,754.28/$26,657), Roanoke
($48,167.81/$43,879, also top store — reviews + gold). **Missed:** Culpeper ($61,998.28/$72,235),
Waynesboro ($40,705.46/$50,721) — $0 for those stores. Task bonus (all qualifiers) hit only at
Roanoke; Harrisonburg and Lexington hit revenue but missed reviews/gold respectively.
**Total payout $4,537.84** — Walker Tapley $1,088.26, Michael Chambers $344.48, Uriah Tiglao
$555.09, Martin Dowden $182.51 + $2.00, Benjie Moore $1,204.20, Joseph Epperly $261.30, Roanoke
top-store pool $300.00, Preston Peters $900.00 (3/5 stores).
**Held/missing:** nothing — engine did not exit HELD, no gates tripped. **Flagged, not paid:**
five terminated employees who earned GP in August (Andrew Clark $584.98, Davon Camber $425.00,
Chonn Grinnage $99.99, Steven Burch $379.99, Cris Lopez $625.93) — ineligible per the
employed-at-payday rule. **Not yet resolved from prior entries:** July 2026 ($1,032 at Roanoke)
still shows unpaid in Gusto as of this run; August is now computed and awaiting Joshua's
approve/hold reply — nothing loaded into payroll yet.

## 2026-10-01 12:18 ET — bonus-month-close-pull (Sept 2026 close)
- Trigger dropped bonusclose-2026-09-20261001T153236Z; claimed within ~1 min, scrap-refining-gold for LEX/ROA/WAY took ~70 min to land (queue depth, not a hang) — all 5 stores landed clean before the collect step.
- `collect --month 2026-09`: no gaps, no holds. All 5 EOM files validated to Reporting Dates 9/1/2026–9/30/2026.
- Sept actuals vs Sept target (revenue gate): CUL hit (+$2,344), WAY hit (+$4,321), HAR missed (-$862), LEX missed (-$759), ROA missed (-$3,459).
- `targets --month 2026-09`: exit 0, trailing-12 method. October targets: CUL $76,997 · HAR $54,380 · LEX $28,232 · ROA $46,807 · WAY $50,503.
- `sheet_sync.py --month 2026-09`: FAILED — FileNotFoundError, Google Drive CloudStorage path not mounted in this session (no Control_your_Mac/osascript tool available this run; used the sandboxed bash + mounted Projects folder instead). Kept the step-6 trailing-12 targets per the documented fallback. Logged to FAILURE_LEDGER.
- DM drafted to outbox for Joshua (bonus-month-close-pull-joshua-20261001-161830) — nothing posted to #bonus-goals, field_posting still false.

## 2026-10-01 17:25 ET — October targets CORRECTED to the sheet method (interactive, Joshua asked)
The 12:18 bonus-month-close-pull run fell back to the trailing-12 yield method because sheet_sync could not reach the Drive file. That is the method retired on 2026-09-09 (it penalises asset growth and is seasonally distorted). Re-ran the sheet_sync calculation (same code, `seasonal()` + `open_targets()`) against history.json through 2026-09, annual plan verified via the Drive connector against VP BONUS FINAL Updated.xlsx (unchanged: CUL 726,042 / HAR 599,708 / ROA 585,973 / LEX 335,431 / WAY 448,674), ROA/LEX no-catch-up rule applied.
**October targets now: CUL $71,664 · HAR $57,850 · ROA $51,419 · LEX $29,159 · WAY $49,889 (company $259,981).** Trailing-12 numbers (CUL 76,997 / HAR 54,380 / ROA 46,807 / LEX 28,232 / WAY 50,503) kept under `superseded` in data/2026-10/targets.json; backup `targets.json.bak-trail12-*`. out/2026-09/slack_targets.txt rewritten; old body kept as slack_targets.trail12-superseded.txt.
Drive sheet NOT rewritten — the local synced copy is cloud-only and can't be read from the sandbox. Harmless: the 11/1 sheet_sync rebuilds the sheet and reads October's target from targets.json. Rates unchanged (2%/2.5% mgr, 4%/5% assoc, FB qualifier off). Nothing posted to the field (field_posting false).

## 2026-10-15 — September 2026 close (interactive, Joshua asked) — 10/10 scheduled close had not run
Inputs added: data/2026-09/roster.json (Gusto list_employees active+terminated, 82 rows), data/2026-09/reviews.json (Chekkit Leaderboard, Last month = Sep 01–30: CUL 18, HAR 7, LEX 4, ROA 10, WAY 16). fb_gains.json not collected (Publer blocked in browser; FB qualifier is null in the Aug-2026 regime so it affects neither Tier 2 nor category wins). `close --month 2026-09` exit 0.
Hit revenue: CUL ($65,583.45/$63,239), WAY ($45,656.05/$41,335). Missed: HAR (-$862), LEX (-$759), ROA (-$3,459) → $0. Task bonus missed at CUL and WAY on gold only (0 dwt — no buckets closed in Sept at either store; August buckets never created per Bravo). ROA top store on gold but failed Bridge 1 → $300 pool not paid.
**Total $3,793.56** — Sandi Cole $1,311.67, Joshua Burnett $294.14, Robert Swagger $271.09, Chadd McClintic $913.12, Martin Dowden $403.54 ($399.16 WAY + $4.38 cross-store CUL), Preston Peters $600.00. Ineligible (terminated before payday): Bridgett Grayson (GP $2,995.91 at CUL despite 8/24 termination — Bravo login likely still in use by someone else), Nelson Troche ($742.72). Payday 2026-10-16. Nothing posted to the field.

## 2026-10-15 (cont'd) — September gold CORRECTED; total $4,891.96
Joshua asked to double-check gold. The 10/1 gold snapshots were stale: CUL and WAY were pulled before the 9/28 afternoon closeout of the August buckets, and HAR's snapshot was copied at 16:17, before the complete 16:30 pull landed. Today's re-pull (trigger goldverify-20261015-1547) still could not see the closed CUL buckets, and the WAY/HAR cells errored ("No bucket rows captured"). Source of truth used instead: Precious Metals Settlements/reviews/2026-08_allocations_v2_CLOSED.csv. That file has weights read LIVE in Bravo on 9/28, all 10 buckets were closed and post-approve verified on 9/28, and it ties to the Elemetal wires to the penny (CHANGELOG 2026-09-28). Appended the closed 2026-08 bucket rows to data/2026-09/gold_{CUL,WAY,HAR}.csv (originals kept as .bak-20261015-stale).
September gold (closed in Sept): CUL 241.90 · HAR 104.65 · LEX 88.85 · ROA 114.29 · WAY 102.59 dwt. CUL and WAY now pass every task goal, so Tier 2 is hit (mgr 2.5%, assoc 5%). Culpeper is top store (gold + reviews) and its $300 pool is split $100 x 3.
Engine fix: stage_close's total left out the top-store pool shares, so the reported total was $300 short. Gusto lines were already right. Patched with backup bonus_engine.py.bak-20261015-pre-pooltotal. The August report total ($4,537.84) was understated the same way; true August is $4,837.84.
FINAL Sept: Sandi Cole $1,739.59 · Chadd McClintic $1,141.40 · Preston Peters $600.00 · Martin Dowden $504.43 · Joshua Burnett $467.67 · Robert Swagger $438.87 = $4,891.96. Previous outputs are in out/2026-09.bak-20261015-pre-goldfix.
Pipeline issue (not fixed today): the scrap-refining-gold handler misses closed buckets / fails on store switch. Use the settlement workbooks for gold until it is repaired.

## 2026-10-15 (cont'd) — Preston gold bonus added; September total $5,391.96
Joshua, verbatim: "gold bonus contuimues but its 500 for 60k, and 300per store that hits". Added `market_manager_gold_bonus` to bonus_rules.json ($500 when gold scrap settlements in the month > $60,000, gold karat + stone removal, silver excluded) and an additive engine block that reads data/<month>/gold_settlements.json. Backups: *.bak-20261015-pre-goldbonus. September gold settled $146,380.44 (4 Elemetal settlements) → +$500. Preston September = $600 (2 stores) + $500 gold = $1,100. Total $5,391.96.
2026 reconciliation of Preston vs Gusto done in chat (see Open Items Register).

## 2026-10-15 (cont'd) — gold bonus threshold set to $65,000; past payouts left alone
Joshua: "its 500 for gold over 65k and 300 per hit, we wil leave it alone for past payouts." bonus_rules.json market_manager_gold_bonus.threshold_usd = 65000. September gold $146,380.44 still qualifies, so Preston stays at $1,100 and the total stays at $5,391.96. The Jan-Aug 2026 overpayment (about $2,000) is closed with no action.

## 2026-10-19 09:16 ET — bonus-paid-verify (scheduled, September 2026 / payday 2026-10-16)
Checked September close ($5,391.96 owed, 6 people, out/2026-09/close.json + gusto_lines.csv) against the
2026-10-16 Gusto payroll (list_payrolls check_date=2026-10-16, include=totals; get_employee_earnings_summary
2026-10-01..2026-10-16). Gusto's payroll-wide bonus total was $5,387.53, and the per-employee breakdown shows
why: Sandi Cole $1,739.59, Joshua Burnett $467.67, Robert Swagger $438.87, Chadd McClintic $1,141.40, and
Preston Peters $1,100.00 all paid exactly right. Martin Dowden ($504.43 owed — $5.48 CUL + $498.95 WAY) got
$0. Instead, Walker Tapley (Harrisonburg manager, not in this month's bonus at all) was paid a $500.00 bonus
on the same check — looks like Dowden's line was keyed to the wrong employee. Confirmed both are real,
distinct, active Gusto employees (not a name variant). DM sent to Joshua (D03BHQH5VGT) with the plain finding.
Trend tab Paid Verify Note updated for 2026-09. Fleet publish guard checked first (vp_dryrun.py status — not
armed, exit 1), published for real.

## 2026-10-21 — management rights added (interactive, Joshua asked)
bonus_rules.json management_rights (effective earning month 2026-12) + management_actions.json + engine load_management_actions(). Sept 2026 close re-run in a scratch copy: $5,391.96, identical. Synthetic tests (effective_from forced to 2026-09 in the copy only): WAY suspend → $0 store line, pool excluded; CUL per-employee withhold → $0 line, pool split among the rest; back-dated suspension → HELD. Live out/ and ledger untouched. Policy + handbook section re-rendered.

## 2026-10-22 — September Martin Dowden bonus corrected (interactive)
Gusto payroll check date 2026-10-23 (processed 10/22) pays Martin Dowden $604.43 bonus = $504.43 Sept bonus + $100 one-off (breaker errand). Verified via get_employee_earnings_summary. Martin notified in Slack DM at Joshua's approval. Still open: Walker Tapley's $500 overpayment on the 10/16 check.
Update 2026-10-22: Walker Tapley's $500 bonus on the 10/16 check was INTENTIONAL — Joshua paid it as a discretionary effort bonus, outside the bonus program. Not an error; do not flag or recover. September 2026 is fully closed and paid.

## 2026-11-01 11:30 — bonus-month-close-pull (native)
pulled end-of-month; pulled chekkit-invites-range; pulled employee-activity-range; gold: year files already refreshed today by the scrap rankings agent — no second pull; collect rc=2; collect (retry) rc=0; targets rc=0; sheet_sync rc=1; DM sent

## 2026-11-01 14:17 — bonus-month-close-pull (native)
collect rc=0; targets rc=0; sheet_sync rc=1; DM sent

## 2026-11-01 19:21 ET — October 2026 close (interactive, Joshua asked) — run 9 days ahead of the 11/10 scheduled close
Inputs added to data/2026-10: roster.json (Gusto list_employees active 19 + terminated 64 = 83 rows), reviews.json (Chekkit Leaderboard, Last month = Oct 01–31: CUL 20, HAR 13, LEX 7, ROA 19, WAY 16), gold_settlements.json ($28,509.15 — one Elemetal settlement INV-20261030-348183, Scrap Gold Karat 287.8 dwt, read from the Gmail raw MIME attachment; the stone-removal lot from the 10/29 shipment had not settled by 10/31). fb_gains.json not collected — FB qualifier is null in the Aug-2026 regime (October is still under it).
Gold fix (same defect as 10/15): the scrap-refining-gold handler reported NO BUCKET FOUND for CUL and WAY 2026-09, but all 10 September buckets were closed in Bravo 10/1 (HAR/LEX/ROA/WAY) and 10/2 (CUL) per Precious Metals Settlements/reviews/2026-09-buckets_allocations_CLOSED.csv (live weights, ties to both Elemetal wires). Appended those closed rows to data/2026-10/gold_CUL.csv and gold_WAY.csv (originals kept as .bak-20261101-stale; the pipeline's year files were not touched — separate inodes). October gold by StatusDate: CUL 313.26 · HAR 119.19 · LEX 75.81 · ROA 130.51 · WAY 52.03 dwt.
`close --month 2026-10` exit 0, Aug-2026 regime, payday 2026-11-20. Revenue gate: CUL $80,738.81/$75,111 hit · ROA $53,980.68/$51,419 hit · LEX $29,775.80/$29,159 hit · WAY $50,119.05/$49,889 hit · HAR $46,224.05/$57,850 MISSED (-$11,626; also under Oct 2025) → $0 for Harrisonburg. Task goals: CUL and ROA hit all (Tier 2); LEX missed reviews (7) and gold (75.8); WAY missed gold (52.0). Top store CUL (gold + reviews) — $300 pool split $100 × 3.
**Total $8,677.75** — Sandi Cole $2,118.47 (incl. $100 pool) · George Moore $1,349.52 · Preston Peters $1,200.00 (4 stores × $300; gold bonus not earned, $28,509 settled vs $65,000 bar) · Chadd McClintic $1,002.38 · Robert Swagger $647.16 (incl. $100 pool) · Joshua Burnett $599.33 (incl. $100 pool) · Uriah Tiglao $595.52 · Martin Dowden $520.63 ($500.27 WAY + $20.36 cross-store CUL) · Joseph Epperly $363.92 · Stephanie Chaplin $223.05 · Brendon Thomas $57.77. Ineligible (terminated before payday): Bridgett Grayson (GP $844.98 at CUL — login still in use, same as Sept), Nelson Troche ($296.96), Cris Lopez ($199.99), Jacob Cox ($604.21, term 10/20). Nothing posted to the field; nothing loaded in Gusto — awaiting Joshua's approve/hold.

## 2026-11-01 19:30 ET — November targets CORRECTED to the sheet method (interactive)
The 11:30 bonus-month-close-pull fell back to trailing-12 again (sheet_sync rc=1 — Drive CloudStorage path unreadable from the bridge), the method retired 2026-09-09. Re-ran seasonal() + open_targets() on history.json through 2026-10 with the DEFAULT_PLAN annual plan (same plan behind the Sept and Oct targets; ROA/LEX no-catch-up). **November targets: CUL $74,561 · HAR $50,054 · ROA $49,850 · LEX $27,497 · WAY $46,284 (company $248,246).** All five sit above Nov-2025 actuals, so no override like October's Culpeper case is needed. Trailing-12 numbers (CUL 75,591 / HAR 55,541 / LEX 27,281 / ROA 46,177 / WAY 51,437) kept under `superseded` in data/2026-11/targets.json (backup targets.json.bak-trail12-20261101); out/2026-10/slack_targets.txt rewritten with the Nov-2026 regime task goals (17 reviews / 60% email / 110 dwt / +5 FB / beat Nov 2025; no Store of the Month). Old body kept as slack_targets.trail12-superseded.txt. Not posted (field_posting false) — Joshua posts to #bonus-goals when he chooses.
Standing defect, two months running: sheet_sync.py cannot reach the Drive sheet from the bridge, so the engine's 1st-of-month run always publishes trailing-12 targets to Joshua's DM. Fix for the 12/1 run: make bonus-month-close-pull compute targets with the sheet method from history.json (no Drive dependency) and treat the Drive sheet rewrite as optional.

## 2026-11-01 15:30 ET — sheet_sync Drive dependency removed (fleet session)
sheet_sync.py now works on a local mirror, data/VP BONUS FINAL Updated.mirror.xlsx (seeded from the Drive file via the Drive API, id 1dX_E2txo56JJFS_FKC7Pb4uMxZBwvRLh). Each run refreshes the mirror when the Drive file reads cleanly; on EDEADLK or any read error it uses the mirror. It writes the mirror, then pushes it back to Drive; if the push fails it leaves data/sheet_push_pending and the next run pushes again. The mirror's annual plan rows equal DEFAULT_PLAN exactly (CUL 726,042 / HAR 599,708 / ROA 585,973 / LEX 335,431 / WAY 448,674), so the November targets corrected above are confirmed right. No extra DM sent. Backup: bin/sheet_sync.py.bak-pre-mirror-20261101.

## 2026-11-01 (cont'd) — gold settlement attribution corrected to posted month (Joshua)
Joshua: the 10/30 Elemetal settlement ($28,509.15) is for October-collected gold that posts to Bravo in November, so it counts for the NOVEMBER bonus along with the second (stone-removal) settlement still to come. October's gold dwt (September buckets closed 10/1–10/2) was already right. Changes: data/2026-10/gold_settlements.json -> $0 (no October settlement counts); data/2026-11/gold_settlements.json seeded with the 10/30 settlement and a pending marker for the stone lot; bonus_rules.json market_manager_gold_bonus.attribution = posted_month (backup bonus_rules.json.bak-20261101-goldattrib). Re-ran `close --month 2026-10`: **total unchanged, $8,677.75**; Preston $1,200 (gold bonus not earned either way).

## 2026-11-01 (cont'd) — full-month eligibility for everyone (Joshua); October total $8,396.93
Joshua, verbatim: "any one who did not work all of october does not gibe a boinus so any new hires in that month would not qualify". Added eligibility.employed_full_month = true to bonus_rules.json (backup .bak-20261101-pre-fullmonth) and an additive check in stage_close's associate loop (backup bin/bonus_engine.py.bak-20261101-pre-fullmonth): hired after the 1st of the earning month -> no bonus that month, noted in the report. Managers were already covered by manager_full_month. Re-ran `close --month 2026-10`: Stephanie Chaplin (hired 10/8, GP $5,576.24) and Brendon Thomas (hired 10/26, GP $1,155.44) removed. **October total now $8,396.93** — Sandi Cole $2,118.47 · George Moore $1,349.52 · Preston Peters $1,200.00 · Chadd McClintic $1,002.38 · Robert Swagger $647.16 · Joshua Burnett $599.33 · Uriah Tiglao $595.52 · Martin Dowden $520.63 · Joseph Epperly $363.92. Policy + handbook re-rendered. Still awaiting approve/hold; nothing posted, nothing in Gusto.

## 2026-11-01 (cont'd) — November targets FINAL: yield method +4% (Joshua)
Joshua reviewed the payout doubling ($8,396.93, 3.2% of net revenue vs 2.1–2.3% Aug/Sep) and the asset-growth case (ending assets +24% YoY) and chose yield-based targets edged up 4%. Base = per store max(sheet-method target, Oct-26 ending assets x own trailing-12 yield), Harrisonburg held at $52,500 (its T12 yield carries the June scrap month; ex-scrap June ≈ $50k). x1.04 → **CUL $78,615 · HAR $54,600 · ROA $51,844 · LEX $28,597 · WAY $53,494 (company $267,150)**. Written to data/2026-11/targets.json (sheet-method set kept as targets.json.bak-sheet-20261101 and under `superseded`); out/2026-10/slack_targets.txt rebuilt. Not posted — field_posting false; Joshua posts when ready. Engine rule change for 12/1 still pending: compute max(sheet, yield) in bonus-month-close-pull without the Drive dependency.
