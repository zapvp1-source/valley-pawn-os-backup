# Bonus Cycle Status — verified 2026-09-05 (evening)

Read-only investigation of the monthly bonus cycle (targets / qualifiers / payout) for June–September 2026. Everything below was verified against OUTPUT (Slack channel, Drive files, the local master xlsx, pipeline result files), not against task run records (Rule 12). Nothing was posted to Slack. No SKILL.md was edited. The master xlsx was NOT modified (see section 6 for why).

Sources read:
- Slack #bonus-goals (C04TXF0KGNL), full history 2026-06-02 → 2026-09-05 (no earlier messages in the range; channel has nothing after 8/12).
- Drive: `VP BONUS FINAL Updated.xlsx` (live, id 1HKTWucLG8R2Yzgdm62vb2rrwYUTpntBB, modified 2026-09-02 13:46Z), its three backups, `VP_Bonus_Tracker_MASTER_2026.xlsx` Drive copy (id 10osZp4-rlMIu5y3uOmq2NU2NFyF0Hqy1, modified 7/21), pipeline result files `bonustargets-20260812T155144Z.result.json` and `bonustargets-20260902T090920.result.json`.
- Local: `/Users/joshuadavis/Documents/Claude/Projects/Bonus Program/VP_Bonus_Tracker_MASTER_2026.xlsx` (mtime Jul 21 14:52), `BONUS_PROGRAM_REVIEW_AND_PLAN_2026-09-05.md` (written earlier today by another session).
- The three SKILL.md files under `/Users/joshuadavis/Documents/Claude/Scheduled/monthly-bonus-{targets,qualifiers,payout}/`.

---

## 1. What #bonus-goals shows, by month

Every bonus-related post in the channel, June 1 → today. Times are EDT as rendered by Slack.

| Date | Poster | What it is |
|---|---|---|
| 06-02 10:37 | Sandi | asks for monthly goals |
| 06-02 12:29 | Joshua | "Let me ask Claude" |
| 06-06, 06-12, 06-15 | Sandi, Chadd | repeated asks for June goals |
| 06-15 09:25 | Joshua | "Claude had a meltdown" — working on it |
| 06-18 09:30 | Joshua | **No June targets** — Joshua will award June bonuses to "extraordinary performances" by hand |
| 06-19 10:08 | Joshua | Congratulates May top-bonus earners (Sandi ~$2k, Bree ~$1k) |
| 07-01 13:50 | Sandi | asks for July goals |
| 07-02 15:13 | Joshua (Sent using Claude) | **July 2026 Bonus Targets** — CUL $77,117 · HAR $57,724 · ROA $48,001 · LEX $27,545 · WAY $48,694. Method: June ending assets × 2026 YTD yield × 1.03 Friday multiplier |
| 07-02 15:23 | Joshua | Mid-year bonus update: $31,000 paid YTD vs $14,155 same point 2025 |
| 07-02 15:25 | Joshua | "PEOPLE ARE GETTING PAID" morale post |
| 08-03 13:32 | Sandi | asks for August goals |
| 08-03 14:30 | Joshua | "you dont want me to send these out! Working on the formula, somethings off" |
| 08-03 14:41 | Joshua | explains the yield window problem (TTM/tax-season yield applied to summer) — "Stay Tuned" |
| 08-12 12:40 | Joshua (Sent using Claude) | **August 2026 Bonus Targets** — CUL $72,235 · HAR $53,282 · ROA $43,879 · LEX $26,657 · WAY $50,721. Method: July ending assets × trailing-12 yield, no Friday adjustment |
| — | — | *(nothing posted after 08-12)* |

Answers to the three specific questions:
- **July qualifiers table (expected ~8/10): NOT POSTED.** There is no qualifier table for June, July, or August anywhere in the channel. The `🎯 *Bonus Qualifiers — {Month Year}*` format has never appeared.
- **August targets (expected ~8/2): POSTED, but on 8/12, ten days late**, after a false start on 8/3 that Joshua pulled back ("somethings off").
- **September targets (expected ~9/2): NOT POSTED as of 9/5.** The targets task did run on 9/2 (see section 2) and wrote September targets into the live VP BONUS FINAL sheet, but the channel post requires Joshua's hand-send and it has not happened.

Pattern: targets reach the channel only when Joshua hand-posts (5/8, 7/2, 8/12 per the earlier review doc); the field asks for goals in the channel every single month; qualifiers have never reached the channel.

---

## 2. What Drive shows

Searches run: `title contains 'Bonus Qualifiers'`, `'VP BONUS FINAL'`, `'Bonus Payout'`, `'VP_BONUS'`, plus a catch-all `Qualifier|Payout|bonus` modified after 7/22, plus a listing of the Drive "Bonus Program" folder and the two task folders.

| File | Drive id | Modified | Finding |
|---|---|---|---|
| **"Bonus Qualifiers" sheet** | — | — | **DOES NOT EXIST.** No file with that title anywhere in Drive. |
| **"Bonus Payout — July 2026.xlsx"** (or any month) | — | — | **DOES NOT EXIST.** |
| **Drive folder 1nR6j_0IL6Jqtn2pXlc4hqJjo_uahM7Ru** (the folder both SKILL.md files tell the tasks to write into) | 1nR6j_… | — | **`get_file_metadata` → "Requested entity was not found."** The folder id in the SKILL.md files does not resolve. The real Drive "Bonus Program" folder (where the master xlsx copy and today's review doc live) is **1az4UOVebmEU28RNOIZJF9j7hFdkJBrsf**. This alone would make the qualifiers/payout Drive write fail every run. |
| `VP BONUS FINAL Updated.xlsx` (LIVE) | 1HKTWucLG8R2Yzgdm62vb2rrwYUTpntBB | 2026-09-02 13:46Z | Written by the targets task on 9/2. Has July and August 2026 actuals in col D and September targets in col C (details below). |
| `VP BONUS FINAL Updated.BACKUP-2026-09-02-pre-sep-targets.xlsx` | 1f7sueNJdG75uGntKWFxQtyXVDfsPQUs9 | 9/2 | backup taken by the 9/2 targets run |
| `…BACKUP-2026-08-06-pre-trail12-revision.xlsx` | 1UHmYAQ2qZ_Zx6lyxE3pfyDq3v4gfo9RN | 8/6 | backup from the trailing-12 method change |
| `…BACKUP-2026-08-03-pre-aug-targets.xlsx` | 1lQfOZ2eQb8gpmO-kAtLb5W9eRtWtAr76 | 8/3 | backup from the retracted 8/3 attempt |
| `…BACKUP-2026-07-02.xlsx` | 1AC-LF0gEPDLY0oUWZ7D1hCITt_xECHcx | 7/2 | the id the SKILL.md "SCHEDULE + OUTPUT TARGETS" section still names as "the live file" (contradicted by the later FILE-ID CORRECTION in the same file) |
| `VP_Bonus_Tracker_MASTER_2026.xlsx` (Drive copy) | 10osZp4-rlMIu5y3uOmq2NU2NFyF0Hqy1 | 2026-07-21 | identical vintage to the local file — no month tab written since 7/21 |
| `_input_VP_BONUS_FINAL.xlsx` | 1TPc-bV4O6lmFQ9rwbA2KKye-VCSCOyG9 | 7/21 | local reference copy the tasks are supposed to keep in sync — 6 weeks stale vs the live file |
| `bonustargets-20260812T155144Z.result.json` | 1TVB4Q4sCCq_LqAWgY5hlIrqn_7zJhyU5 | 8/12 | status "success", 5/5 stores, date range 2026-07-01..2026-07-31 → the July EOM pull that produced July col-D actuals |
| `bonustargets-20260902T090920.result.json` | 1Rq0P5YZfonY9nR1NUBpjI0RIAc-pLjGQ | 9/2 | status "success", 5/5 stores, date range 2026-08-01..2026-08-31 → the August EOM pull that produced August col-D actuals (pulled 9/2, i.e. BEFORE the 9/5 same-filename overwrite flagged as F2 in the review doc, so these August values are August-only) |

### 2a. Per-store results that DO exist — from the live VP BONUS FINAL "2025 compared to Bonus" sheet (read 9/5)

Columns: B = 2025 same-month revenue, C = 2026 target, D = 2026 actual (written by the targets task from `bonus_kpis_extract.py`).

**June 2026 (col D was populated before the targets-task rewrite; see section 3 on why it is a different definition)**

| Store | 2025 Rev (B) | Target (C) | Actual (D) | D ≥ C (Bridge 1) | D ≥ B (Bridge 2) |
|---|---|---|---|---|---|
| Culpeper | 37,538.00 | 54,000.00 | 74,594.07 | PASS | PASS |
| Harrisonburg | 40,365.00 | 40,980.68 | 71,550.31 | PASS | PASS |
| Lexington | 23,134.00 | 24,064.52 | 24,977.23 | **PASS** (+912.71) | PASS |
| Roanoke | 31,824.00 | 47,164.52 | 42,193.38 | FAIL (−4,971.14) | PASS |
| Waynesboro | 31,514.00 | 33,048.39 | 48,931.66 | PASS | PASS |

**July 2026 (col D written 8/12 by the targets task = Net Revenue per `bonus_kpis_extract.py`)**

| Store | 2025 Rev (B) | Target (C) | Actual (D) | % of target | Bridge 1 | Bridge 2 |
|---|---|---|---|---|---|---|
| Culpeper | 51,013.00 | 77,117.00 | 61,751.95 | 80.1% | FAIL | PASS |
| Harrisonburg | 44,202.00 | 57,724.00 | 42,881.84 | 74.3% | FAIL | FAIL |
| Lexington | 22,618.00 | 27,545.00 | 21,701.62 | 78.8% | FAIL | FAIL |
| **Roanoke** | 32,158.00 | 48,001.00 | **48,831.78** | **101.7%** | **PASS** | **PASS** |
| Waynesboro | 25,380.00 | 48,694.00 | 40,329.99 | 82.8% | FAIL | PASS |

Roanoke is the only July Bridge-1 pass. Under the July regime that is: manager 2.5% (Tier 2 hit) or 1.5% (Tier 2 miss) of Roanoke Net Revenue, associates 5%/3% of their GP, Preston 1 × $300. July gold for Roanoke per the qualifiers SKILL.md text = 95.66 dwt (< 100 → Tier 2 miss on gold alone, if that figure is accepted). Reviews / Email % / QR views for full July were never computed by any task — the only July values on record are the 7/1–7/21 MTD ones in the master's 2026-07 tab (ROA reviews 13, email 63/70 = 90%).

**August 2026 (col D written 9/2 by the targets task; August regime applies)**

| Store | 2025 Rev (B) | Target (C) | Actual (D) | % of target | Bridge 1 | Rev YOY (Bridge 2) |
|---|---|---|---|---|---|---|
| Culpeper | 50,164.00 | 72,235.00 | 61,998.28 | 85.8% | FAIL | PASS |
| Harrisonburg | 39,769.00 | 53,282.00 | 54,413.07 | 102.1% | **PASS** | PASS |
| Lexington | 21,270.00 | 26,657.00 | 27,754.28 | 104.1% | **PASS** | PASS |
| Roanoke | 32,867.00 | 43,879.00 | 48,167.81 | 109.8% | **PASS** | PASS |
| Waynesboro | 31,240.00 | 50,721.00 | 40,705.46 | 80.3% | FAIL | PASS |

Three stores pass Bridge 1 for August → Preston 3 × $300 = $900 minimum, plus HAR/LEX/ROA employee commissions once the four task qualifiers (Reviews ≥15, Email ≥50%, Gold ≥100 dwt, FB followers +15 via Publer) are measured. None of those four have been measured for August by any task.

**September 2026 targets (col C, written 9/2, NOT posted):** Culpeper $73,397 · Harrisonburg $54,131 · Roanoke $45,283 · Lexington $28,489 · Waynesboro $50,570. Ending-assets basis (col F = Aug actual G): CUL 401,349.67 · HAR 340,052.16 · ROA 291,019.97 · LEX 179,596.28 · WAY 249,683.44.

---

## 3. The revenue-formula discrepancy, side by side

Exact quotes from the three SKILL.md files as they read on 2026-09-05.

| File | Section | Quoted formula | Where it says the number comes from |
|---|---|---|---|
| **monthly-bonus-targets** | "CRITICAL — 'Net Revenue' definition (corrected 2026-07-16)" | `Net Revenue = Pawn Service Charges (interest & fees, MTD, in-store only) + Sales Revenue (Profit) (MTD)` | Bravo **End-of-Month** xlsx via `bonus_kpis_extract.py` (which "reuses [store_kpis_compile.py's] already-penny-verified Net Revenue formula (Pawn Service Charges + Sales Revenue (Profit))"). Also: "Column D ('2026 Revenue Actual') must be Bravo's **Net Revenue** KPI, and nothing else." |
| **monthly-bonus-qualifiers** | "Standing fact — 'Revenue' definition (confirmed 2026-07-16)" | `Net Revenue = Pawn Service Charges (interest & fees, MTD) + Retail Sales Gross Profit Amt (MTD) + Scrap Sales Gross Profit Amt (MTD)` | Bravo **Company Performance** / KPI report. And, critically: "it is NOT the same as VP BONUS FINAL's column D (2026 Revenue), which runs consistently $5,300–$9,900+ higher per store per month … VP BONUS FINAL's column D is a useful target-tracking figure for the Bridge 1/Bridge 2 gate logic below, but is NOT the number to multiply by a commission rate." |
| **monthly-bonus-qualifiers** | "SCHEDULE + OUTPUT TARGETS (set 2026-07-21)" item 1 | `Revenue = Sales Revenue Profit + Interest & Fees Total from Bravo EOM (the verified methodology)` | Bravo EOM — a third wording, in the same file, for what to write into column D |
| **monthly-bonus-payout** | "Basis sourcing — CORRECTED 2026-07-16" | `Net Revenue = Pawn Service Charges (interest & fees, MTD) + Retail Sales Gross Profit Amt (MTD) + Scrap Sales Gross Profit Amt (MTD)` | Bravo Company Performance report. "VP BONUS FINAL's column D runs $5,300–$9,900+ higher per store per month than actual Net Revenue and must NOT be used as the commission basis." |
| **monthly-bonus-payout** | "SCHEDULE + OUTPUT TARGETS" item 1 | `Revenue = Sales Revenue Profit + Interest & Fees Total from Bravo EOM` | same third wording as qualifiers |

All three files claim their formula was "verified to the penny" against the same June 2026 Preston figures (Culpeper $66,649.27, Harrisonburg $61,666.31, Roanoke $36,906.77, Waynesboro $43,416.44; targets also lists Lexington $21,455.49). If both verifications are true, then PSC + Sales Revenue (Profit) [EOM] and PSC + Retail GP + Scrap GP [Company Performance] are the same quantity under two report labels, and the naming is not the real problem.

**The real problem is what is sitting in column D, and therefore what the targets and the bridges are built on:**

- June 2026 column D = Culpeper **74,594.07**, but the penny-verified June Net Revenue for Culpeper = **66,649.27**. Difference **7,944.80** — exactly the "$5,300–$9,900 higher" broader figure the qualifiers/payout files warn about. Same for Lexington: D = 24,977.23 vs Net Revenue 21,455.49 (+3,521.74). So **Jan–Jun 2026 column D is the broader (gross-based) figure.**
- July and August 2026 column D were written by the rewritten targets task from `bonus_kpis_extract.py`, so they ARE Net Revenue (the narrower, gross-profit-based figure).
- The July targets were computed on 7/2 as June ending assets × YTD yield, where every YTD yield used the **broader** Jan–Jun D values (and a ×1.03 Friday multiplier since removed). The July actuals that were then compared against those targets were the **narrower** Net Revenue. That mismatch is on the order of 10–13% per store — roughly the same size as the shortfalls in the July table above (CUL 80%, HAR 74%, LEX 79%, WAY 83%). Four of five stores "failing" July is at least partly an artifact of measuring a narrower number against a target built from a broader one. This is consistent with Joshua's 8/3 message that "somethings off."
- The August targets (trailing-12 yield, Aug 2025–Jul 2026) mix 2025 months pulled fresh via `bonus_kpis_extract.py` (Net Revenue) with Jan–Jun 2026 sheet values (broader) and Jul 2026 (Net Revenue). Still a mixed series.

**Recommendation — adopt ONE definition, the targets task's, everywhere:**

> Revenue (for targets, Bridge 1, Bridge 2, and the Manager commission basis) = Bravo End-of-Month report: `Pawn Service Charges (in-store) + Sales Revenue (Profit)`, computed by `bonus_kpis_extract.py` / `store_kpis_compile.py`.

Why this one:
1. **Targets set the number; qualifiers and payout measure against it.** They must be the same quantity or Bridge 1 is meaningless. The targets task is the only one of the three whose formula is implemented in code, runs headless on a schedule, and has actually produced output three months running (7/2, 8/12, 9/2). The qualifiers/payout definition depends on a Company Performance report the pipeline does not pull.
2. It is the same formula `weekly-store-kpis` already publishes every week, so stores and Joshua see one revenue number all month and the same number at bonus time.
3. It reconciles to Preston's real June commission basis (the figure people were actually paid on), so the Manager 2%/2.5%/1.5% math needs no second "basis" column.

Required follow-through if adopted (not done in this session — outside the write scope):
- Restate Jan–Jun 2026 column D (and the Jan–Jun yields in col H) with Net Revenue from the cached 2025/2026 EOM files so the trailing-12 series is one definition end to end. Then the September targets should be regenerated; the 9/2 targets (built on the mixed series) are probably a few percent high.
- Re-evaluate June Bridge 1 on the restated basis before anyone treats the June tab as "final" (see section 4 — Lexington flips).
- Collapse the three wordings in the SKILL.md files to the single sentence above (another agent is editing those files now; hand them this section).

---

## 4. The Lexington June Bridge-1 discrepancy

Three sources, three answers:

| Source | Lexington June Bridge 1 | Basis used |
|---|---|---|
| Master xlsx, tab `2026-06`, row 5 | **E5 = FAIL**, F5 = "—", J5 = "—", K5 = $0; note A12: "LEX+ROA $0 (Bridge 1 fail) · Preston 300x3=900"; Trend tab B49 = FAIL; Preston override B42 = 900 (3 stores) | Internally inconsistent: the same row carries B5 = 24,977.23 and C5 = 24,064.52, and 24,977.23 ≥ 24,064.52 is a PASS by the row's own numbers. |
| Both qualifiers and payout SKILL.md, "Verified real-world impact (June 2026)" | "Lexington passed BOTH bridges (Actual $24,977.23 >= Target $24,064.52, and >= prior-year $23,134.00) — Uriah was paid $0 in June under the old process but should have qualified." Payout SKILL example: "Culpeper, Harrisonburg, Lexington, and Waynesboro passed Bridge 1; Roanoke failed. Preston's June payout = 4 x $300 = $1,200." | Column D (broader figure) |
| Live VP BONUS FINAL sheet, Lexington June row | D = 24,977.23, C = 24,064.52, Variance +912.71 → PASS | Column D (broader figure) |

Most likely explanation: the xlsx author gated Lexington on the penny-verified **Net Revenue** ($21,455.49, which IS below the $24,064.52 target) while the SKILL.md text gated on **column D** ($24,977.23, above target). The Lexington row is the formula discrepancy from section 3 made concrete — the pass/fail result flips depending on which revenue definition you pick, which is exactly why one definition has to be chosen and the targets built on the same one. (Roanoke fails June either way: 42,193.38 or 36,906.77, both < 47,164.52.)

Money impact if Lexington June is ruled a PASS: Preston +$300 (4 stores, $1,200 not $900); Lexington manager (Uriah) 2% of Lexington June basis (Tier 2 = No, reviews 4 < 12) ≈ $429 on the $21,455.49 basis or ≈ $500 on the $24,977.23 basis, plus associates' 4% of their June GP. Per both SKILL.md files this is Joshua's call, not something a task may pay retroactively. Nothing was changed in the xlsx.

---

## 5. Other things verified on the way

- **Master xlsx README is stale:** row A3 says "monthly-bonus-qualifiers (2nd, 9AM) … monthly-bonus-payout (3rd, 9AM)"; both SKILL.md files moved to the 10th (9:00 / 11:30) on 7/21. The qualifiers SKILL.md gold "Pipeline note" also still says "The monthly qualifiers run (2nd)".
- **Master 2026-07 tab is an MTD snapshot dated 7/21** (A1: "2026-07 - MTD through 7/21"), with every Bridge 1 = "AT RISK" and gold = 0. It was never replaced with a final. Anyone opening the file today would read July as unresolved.
- **June gold in the master (LEX 65.57) vs the SKILL.md gold rule:** SKILL.md says July gold = buckets closed 7/20, and lists LEX 41.57+23.50 = **65.07** for July; the master's 2026-06 tab lists LEX **65.57** for June and its 2026-07 note says the LEX "JUNE 2026 GOLD" buckets totaling 65.07 "are June-cycle, already counted in June." The two documents attribute the same Lexington buckets to different months (and differ by 0.50 dwt). Needs a single ruling before July gold is finalized — the SKILL.md's own attribution rule (by close date, 7/20 → July) says July.
- The targets SKILL.md "Context" section still points at "the 'Claude 4 back up' mounted folder" for the spreadsheet, while the FILE-ID CORRECTION in the other two files points at Drive id 1HKTW…; the 9/2 run evidently found the right file, but the instructions disagree.
- The qualifiers/payout SKILL.md files (SCHEDULE + OUTPUT TARGETS item 1) name Drive id 1AC-LF0gEPDLY0oUWZ7D1hCITt_xECHcx as "the live file Preston uses" and then the FILE-ID CORRECTION at the bottom says that id is the 7/2 BACKUP and must not be written. Same file, opposite instructions.

---

## 6. What was reconciled

**Nothing was written to `VP_Bonus_Tracker_MASTER_2026.xlsx`, and no backup was created.**

Reason: the reconciliation step was conditional on "a July FINAL qualifier/payout result exist[ing] in Drive or the channel." None does — no qualifier table was ever posted, no "Bonus Qualifiers" sheet exists, no "Bonus Payout — July 2026.xlsx" exists, and the Drive folder the tasks were told to write to does not resolve. What DOES exist for July is (a) revenue actuals and targets in the live VP BONUS FINAL sheet, written by the targets task on 8/12, and (b) July gold figures stated in SKILL.md prose. Reviews, Email %, and Social/QR for full July exist nowhere. Writing a `2026-07 FINAL` tab with 5 of 11 columns filled and the rest blank would (1) contradict the tab's own "FINAL" label, (2) be read by the payout task as "qualifiers ran," and (3) bake in the mixed-definition revenue series from section 3. Fabrication was explicitly prohibited, so the file was left exactly as found (mtime Jul 21 14:52).

Ready-to-write July rows (revenue side only, from the live VP BONUS FINAL sheet), for whoever closes July once the qualifiers are measured — same column order as the 2026-06 tab (Store | Revenue | Target | 2025 Rev | Bridge 1 | Bridge 2 | Reviews | Email % | Gold dwt | Tier 2 | Store Payout $):

```
Culpeper     | 61751.95 | 77117 | 51013 | FAIL | —    | ? | ? | 276.65* | —  | 0
Harrisonburg | 42881.84 | 57724 | 44202 | FAIL | —    | ? | ? | 60.68*  | —  | 0
Lexington    | 21701.62 | 27545 | 22618 | FAIL | —    | ? | ? | 65.07*  | —  | 0
Roanoke      | 48831.78 | 48001 | 32158 | PASS | PASS | ? | ? | 95.66*  | ?  | ?
Waynesboro   | 40329.99 | 48694 | 25380 | FAIL | —    | ? | ? | 56.54*  | —  | 0
Preston override: 1 × 300 = 300
* gold figures are from SKILL.md prose (buckets closed 7/20), not from a task output file — confirm against the scrap-refining-gold pipeline output before using.
```

And August (revenue side only; August regime — Reviews ≥15, Email ≥50%, Gold ≥100, FB +15, Rev YOY):

```
Culpeper     | 61998.28 | 72235 | 50164 | FAIL | —    | 0
Harrisonburg | 54413.07 | 53282 | 39769 | PASS | PASS | ?
Lexington    | 27754.28 | 26657 | 21270 | PASS | PASS | ?
Roanoke      | 48167.81 | 43879 | 32867 | PASS | PASS | ?
Waynesboro   | 40705.46 | 50721 | 31240 | FAIL | —    | 0
Preston override: 3 × 300 = 900
```

Caveat on both: these bridges use the targets task's Net Revenue actuals against targets built on the mixed series (section 3). If Joshua adopts the single definition and restates Jan–Jun, the July/August targets change and some of these bridge results may change with them.

---

## 7. Still unknown / not verifiable from here

1. **Whether the qualifiers task ran at all on 8/10, and what it did.** No output exists in any of its three write targets. Run logs under `/Users/joshuadavis/Documents/Claude/Scheduled/…` are outside this session's connected folders and could not be read. The nonexistent Drive folder id (1nR6j…) is a sufficient cause for the Drive write to fail, but it does not explain the missing Slack post or the untouched master xlsx.
2. **Whether the payout task ran on 8/12 and DM'd Joshua.** DMs to Joshua were not read in this session. Today's review doc states Gusto shows `employee_bonuses = 0.00` on every payroll 7/24–9/4 — that was that session's finding, not re-verified here.
3. **July and August qualifier values** (Reviews, Email %, QR views / FB follower gains) for full months — never measured by any task; only the 7/1–7/21 MTD numbers in the master's 2026-07 tab exist.
4. **Whether the two "penny-verified" formulas are truly identical** (EOM "Sales Revenue (Profit)" vs Company Performance "Retail Sales GP + Scrap Sales GP"). Both files claim a match to the same June figures; nobody has put the two report lines side by side for one month in writing.
5. **What Preston actually paid for July**, if anything, and on what basis.
6. **Which rule set is law** (policy docx vs handbook §01.08 vs SKILL.md "August regime") — open decision in today's review doc §6.

---

## 8. fleet/expected_outputs.json — proposed entries

**Qualifiers: NOT proposed.** The task specification asked for a marker copied from a REAL successful qualifiers post. No qualifiers post has ever been made to #bonus-goals, so there is no real marker to copy. The SKILL.md template header is `🎯 *Bonus Qualifiers — {Month Year}*`, but a guardian row keyed on an unverified template would just confirm the template, not the task. Add the qualifiers row after the first real post lands (expected 9/10), copying the exact first line from that message.

**Targets: proposed (marker verified from two real posts, 7/2 and 8/12).** Both posts begin with the calendar emoji followed by "{Month} {Year} Bonus Targets" and carry Slack's "Sent using Claude" trailer:

```json
{
  "task": "monthly-bonus-targets",
  "channel": "C04TXF0KGNL",
  "channel_name": "#bonus-goals",
  "marker": "Bonus Targets",
  "marker_example": "📅 August 2026 Bonus Targets",
  "cadence": "monthly-day2-0900et",
  "grace_days": 3,
  "note": "Post is hand-sent by Joshua after the task DMs a draft; verified real posts 2026-07-02 15:13 EDT and 2026-08-12 12:40 EDT. September 2026 not posted as of 2026-09-05 despite a successful 9/2 run — the guardian should alert on the missing post, not on the run."
}
```

Placeholder to fill in after 9/10 (do not enable until a real post exists):

```json
{
  "task": "monthly-bonus-qualifiers",
  "channel": "C04TXF0KGNL",
  "channel_name": "#bonus-goals",
  "marker": "<copy verbatim from the first real post — expected form: 🎯 *Bonus Qualifiers — September 2026*>",
  "cadence": "monthly-day10-0900et",
  "grace_days": 1,
  "enabled": false
}
```

---

## 9. Bottom line

- Targets: run and write the sheet on schedule (7/2, 8/12, 9/2) but only reach the field when Joshua hand-posts; September is sitting unposted.
- Qualifiers and payout: zero output of any kind for June, July, or August in any of their declared destinations; the Drive folder they target does not exist.
- The one July Bridge-1 pass (Roanoke, $48,831.78 vs $48,001) and three August passes (Harrisonburg, Lexington, Roanoke) are real and unpaid-as-far-as-anything-here-shows.
- The three SKILL.md files disagree on the revenue definition, and column D of the tracker is a mixed series (Jan–Jun broader figure, Jul–Aug Net Revenue) — which inflated July targets relative to July actuals and is the root of the Lexington June contradiction. Adopt the targets task's `PSC + Sales Revenue (Profit)` definition everywhere and restate Jan–Jun.
- Master xlsx deliberately left untouched — no verified FINAL July or August qualifier/payout result exists to reconcile from.
