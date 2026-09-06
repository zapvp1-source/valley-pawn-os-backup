# Bonus Program — Department Review & Automation Plan
**Date:** 2026-09-05 · **Domain:** 1 (Valley Pawn) · **Status:** PLAN — awaiting Joshua's go (nothing changed yet)

---

## 1. What exists today (verified against output, not run records)

| Piece | Where | Cadence | Verified state |
|---|---|---|---|
| `monthly-bonus-targets` | Cowork task, Opus | 2nd 9 AM | Bravo pull works (9/2: 5/5 stores, 9 min). Draft DM'd to Joshua; **he must hand-post**. Posted 5/8, 7/2, 8/12. **September targets still unposted (9/5).** Staff ask in #bonus-goals every month. |
| `monthly-bonus-qualifiers` | Cowork task | 10th 9 AM | 8/10 run: **no #bonus-goals post, no "Bonus Qualifiers" sheet in Drive, master tracker untouched since 7/21.** Zero evidence the July cycle was computed. |
| `monthly-bonus-payout` | Cowork task | 10th 11:30 AM | 8/12 run: **no DM, no "Bonus Payout — July 2026.xlsx".** Gusto shows `employee_bonuses = 0.00` on every payroll from 7/24 through 9/4. |
| `VP_Bonus_Tracker_MASTER_2026.xlsx` | Projects/Bonus Program + Drive | per run | Tabs: 2026-06 FINAL, 2026-07 MTD (7/21). Nothing since. |
| `VP BONUS FINAL Updated.xlsx` | Drive 1HKTW… (live) + local `_input_VP_BONUS_FINAL.xlsx` | per run | Targets task writes it (9/2 OK). Two copies, hand-synced via Chrome. |
| Rules | 3 places, **3 different rule sets** | — | see §3 |
| Data rails | Bravo pipeline output | Monday + EOM | EOM (rev/assets/txn), `chekkit-invites-range` (email %), `scrap-refining-gold` (gold by close date), `employee-activity-range` (assoc GP) — **all already exist headless for August.** Reviews = Chekkit weekly pulls / #google-reviews. FB follower gains = Publer (browser only). Roles = Gusto MCP. |

## 2. Findings (the friction)

**F1 — The July 2026 cycle never closed, and Roanoke appears unpaid.**
Recomputed July from the pipeline EOM files (`bonus_kpis_extract.py 2026-07-31`):
CUL $61,752 vs $77,117 ✗ · HAR $42,882 vs $57,724 ✗ · LEX $21,702 vs $27,545 ✗ · WAY $40,330 vs $48,694 ✗ · **ROA $48,832 vs $48,001 ✓ (Bridge 1 pass; also beats July 2025 $32,158).**
ROA July qualifiers: reviews 13 ✓, email ~90% ✓, gold 95.66 dwt ✗ → Tier 2 miss → manager 1.5% ≈ $732 + associates 3% of their GP + Preston $300. Gusto shows no bonus paid since the June run (7/22). *Money → Joshua's call (§6).*

**F2 — Live data-integrity trap that will corrupt the 9/10 run.**
`output/2026-08-31_*_end-of-month.xlsx` was overwritten on 9/5 14:20–14:28 by the monthly prestage's *trailing-12-month* window (same filename, different date range). `bonus_kpis_extract.py 2026-08-31` now returns Culpeper August net revenue **$767,113** (~10×). The qualifiers task reads exactly that file → every store passes Bridge 1 on 9/10. The correct August-only files live in the sidecar: `output/monthly-analytics/2026-08/same-month-current_{STORE}.xlsx` (80 KB vs 168 KB). Must be fixed before 9/10.

**F3 — Three conflicting rule books.**
- Policy docx (Drive, 7/16): 12 reviews, 4%+1% assoc, 2%+0.5% mgr, no penalty, "social follows".
- Handbook `SOURCES_CURRENT.md §01.08` (what staff sign): mgr 2.5% of revenue @100%/50%, pawnbroker 5% of GP with $3k min, $200 top-sales.
- Task SKILL.md "August regime" (what actually runs): 15 reviews, +15 FB followers (Publer), Rev YOY, mgr 2.5/1.5, assoc 5/3, $300 top store, Preston $300/store.
Whichever is "law," the other two contradict it in writing.

**F4 — Architecture is prompt-rendered math, 4 write targets, no gates.**
Three ~25 KB prompt files with 6 layered "CORRECTION"/"REGIME" sections each; the model re-derives the math every run (the same failure class that produced the illegible #aged-inventory-review EOM post — fixed 9/5 with a deterministic formatter). Writes go to 4 places (Drive live xlsx via Chrome, local copy, master tracker, Drive qualifier/payout sheets) with "guess the row layout" logic. No Rule-18 completeness/plausibility gate. Payout is a separate task 2.5 h after qualifiers with a file hand-off between them. No close-the-loop check that the money actually hit Gusto.

**F5 — Cadence has dead air.** Targets go out whenever Joshua gets to them; nothing between the 2nd and the 10th; no mid-month pace so stores fly blind; payday (first Friday after the 15th) has no verification step.

## 3. Expert board

**PANEL:** data-pipeline/SRE · compensation & payroll controller · release-management lead.

**Options weighed**
- *A — Patch the three SKILL.md files again* (add sidecar path, add gates): fastest, but keeps model-rendered math and 4 write targets; the board has watched this file accrete 6 patch layers already. Rejected.
- *B — One deterministic engine + thin scheduled launchers (recommended):* `bonus_engine.py` owns every number and every Slack body; rules live in one JSON; tasks only run it and post stdout verbatim. Same pattern as `format_aged_inventory.py` and `monthly_prestage_runner.py`, both proven this week.
- *C — Move it all to a native launchd agent:* removes Claude entirely, but Publer follower gains and Gusto approval still need a session; over-engineered for a monthly job. Deferred (engine is launchd-ready if wanted later).

**DECISION:** B. Additive — new files only; the three existing tasks stay registered (disabled after two clean cycles) as rollback.

## 4. Target design

**One source of truth for rules:** `Bonus Program/bonus_rules.json` — regimes keyed by first-effective month (thresholds, rates, Preston override, top-store pool, payday rule). The policy doc, the handbook §01.08, and the #bonus-goals pinned canvas are *generated* from it.

**One engine:** `Bonus Program/bin/bonus_engine.py targets|pace|close --month YYYY-MM`
- Inputs (all pipeline files, never Bravo GUI, never QBO): EOM sidecar `same-month-current_*` (net revenue = PSC + Sales Profit, loan+inventory, txn volume), `chekkit-invites-range` (email %), `scrap-refining-gold` (CLOSED + StatusDate in month), `employee-activity-range` (per-employee GP), Gusto MCP roster export (`roster_YYYY-MM.json`), Chekkit reviews CSV, `fb_gains_YYYY-MM.json` (Publer, written by the one browser step).
- **Gates (Rule 18):** 5/5 stores; file date-range header matches the month; net revenue within ±60% of that store's trailing-12 average (would have caught F2 cold); target present; roster non-empty; missing FB/gold → cell shows "—" and Tier 2 is *held*, never defaulted to pass or fail. Any gate failure → prints nothing, exit 2, one plain hold line to Joshua's DM.
- **Outputs:** the master ledger workbook (tabs: Targets · Qualifiers · Payouts · Trend · Gaps · Audit-log) mirrored to the Drive Bonus Program folder as a Google Sheet; Slack bodies emitted verbatim; a Gusto-ready bonus line list (`payout_YYYY-MM.csv`: employee uuid, amount, memo). `VP BONUS FINAL Updated.xlsx` becomes a *derived* export written last, best-effort (Preston keeps his view; it stops being a write-master).

**Cadence (new):**
| When | Task | Does |
|---|---|---|
| 1st 8 AM | `bonus-month-close-pull` | Drops one EOM trigger for the closed month into its own filename (`bonus/{YYYY-MM}/…`) so nothing can overwrite it; runs `targets` stage → DM Joshua the draft. |
| 2nd 9 AM | `bonus-targets-post` | Posts targets to #bonus-goals **unless Joshua replied "hold"** to the 1st-day DM (24 h veto instead of a manual send). |
| Mon 9:30 AM | `bonus-pace-monday` | One line per store: MTD net revenue vs target, % of pace, qualifier standings (reads the Monday combined run's data — no new Bravo touch). |
| 10th 9 AM | `bonus-month-close` | `close` stage: qualifiers + payouts in one run. Posts qualifier table to #bonus-goals; DMs Joshua the payout breakdown + the Gusto line list. |
| First Fri after 15th, 7 AM | `bonus-payday-prep` | If Joshua replied **"approve"** to the 10th DM: loads the bonus lines into that week's Gusto payroll via MCP as *unsubmitted* inputs (he still submits payroll). No reply = nothing loaded, reminder DM. |
| Payday + 3 days | `bonus-paid-verify` | Reads Gusto payroll totals; if expected > 0 and `employee_bonuses` = 0 → DM. Closes the month in the ledger. |
| — | fleet-guardian | `expected_outputs.json` rows for the 2nd, Monday, 10th, and payday-verify markers. |

## 5. Build sequence (additive, prove before deploy)

0. **Before 9/10 (this week):** engine `close` stage on July + August data using the sidecar; reconcile July to Preston's numbers; F2 filename isolation; hand the August close to Joshua on the 10th from the engine, not the legacy task (legacy task left registered but pointed at the engine output as a duplicate-guard). Post the pending September targets on his word.
1. Rules JSON + generated policy/handbook text via `policy-lifecycle` (needs §6 decision 2).
2. Targets + pace stages; new tasks registered; guardian rows.
3. Payday-prep + paid-verify.
4. Two clean cycles (Oct, Nov) → disable the three legacy tasks; CHANGELOG + BUSINESS_OS + PUBLICATION_CALENDAR updated.

## 6. Decisions that are Joshua's (everything else proceeds without him)
1. **Roanoke July bonus** — pay it now (≈ manager $732 + associates' 3% + Preston $300), or waive? 
2. **Which rule set is law** — recommend the August regime as announced 7/21 (15 reviews · 50% email · 100 dwt · +15 FB · Rev YOY · mgr 2.5/1.5 · assoc 5/3 · $300 top store · Preston $300/store). Handbook and policy doc get rewritten to match and re-signed.
3. **Targets auto-post on the 2nd with a 24-hour veto** instead of manual send — yes/no.
4. **Gusto loading on your "approve" reply** (never submitted automatically) — yes/no.
