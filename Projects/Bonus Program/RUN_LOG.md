# Bonus Program — Run Log

Newest first. One entry per engine run or material change. Scheduled tasks append here.

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
