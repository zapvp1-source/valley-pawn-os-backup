# Jewelry On-Hand Nightly Pull — Run Records

## 2026-08-17 (Monday) — jewelry-onhand-nightly-pull

**Run window:** ~6:12 PM – 11:09 PM ET (extended by CUL combo-select flakiness; no manual intervention per task rules — retry logic ran on its own)

**Bravo pull (system on-hand, 8 categories x 5 stores):**
- CUL: success, 8/8 categories
- HAR: partial — Charms returned no rows (empty-category error, not a false zero). Cross-checked against 2026-08-15 CSV, Charms was also empty that day. Treated as 0 in tonight's table per the empty-category rule.
- LEX: partial — Brooches returned no rows (empty-category error). Cross-checked against 2026-08-15 CSV, Brooches was also empty. Treated as 0 in tonight's table per the empty-category rule.
- ROA: success, 8/8 categories
- WAY: success, 8/8 categories

**PM count sheets (#end-of-day):**
- CUL (Sandi, 6:12 PM): read and sum-verified against written total (1461). Match.
- HAR (Walker Tapley, 6:19 PM): read and sum-verified against written total (796). Match.
- ROA (Benjie Moore, 6:35 PM): read and sum-verified against written total (1089). Match.
- WAY (Chadd, 6:24 PM): individual category digits re-zoomed and confirmed unambiguous (378/42/66/51/66), but they do NOT sum to the sheet's own written total (563 written vs 603 actual sum). Treated as a manager arithmetic error, not a misread — used the individual digits, not the written total.
- LEX: **no PM count sheet posted to #end-of-day at any point tonight** (channel searched in full through 11:09 PM). Excluded from tonight's variance table — no data guessed or assumed. Bravo's expected-side numbers for LEX were pulled successfully and are on disk (2026-08-17_LEX_jewelry-case-counts.csv) for whenever/if a sheet shows up.

**Variance table:** posted to #jewlery-counts at 2026-08-17 ~11:10 PM ET. https://valleypawnworkspace.slack.com/archives/C0BM9NHGTT4/p1787022631315899

Store totals (Expected/Counted/Variance):
- CUL: 1462 / 1461 / -1
- HAR: 797 / 796 / -1
- ROA: 1088 / 1089 / +1
- WAY: 565 / 603 / +38 (driven almost entirely by Rings: 339 expected vs 378 counted)
- LEX: not compared — sheet missing

**Anomalies flagged / DM sent to Joshua (D03BHQH5VGT):**
1. WAY Rings +39 over expected (339 vs 378) — WAY's own count sheet doesn't even sum to its written total, points to a manager count/math issue at WAY rather than a Bravo pull error. Needs a look.
2. LEX PM sheet never posted tonight — flagged so it doesn't silently fall through the cracks.
3. HAR Charms / LEX Brooches empty-category-treated-as-zero noted per standing rule.

**Guardrails followed:** no manual Bravo UI interaction (let CUL's retry/fallback logic run on its own even though one category took ~35-50 min), no folder-access request needed (bash/file tools sufficed), no false zeros reported (empty categories cross-checked against prior day before being treated as 0), no partial/guessed post for LEX.

## 2026-08-21 (Friday) — 8/20 CATCH-UP eval + hardening

- Nightly task did NOT run 8/18, 8/19, 8/20: app was closed at 8:30 PM those nights (scheduler only fires while app is open). Task config itself verified healthy (enabled, cron, model pin).
- 8/20 catch-up executed manually Fri AM inside freeze window: all 5 stores pulled (CUL clean 10 min/store — no combo flakiness this time). HAR Charms + LEX Brooches empty (0, consistent w/ 8/15+8/17). WAY Charms errored (was 1 on 8/17) — WAY Pendants expected carried as 66-67 (±1).
- All 5 PM sheets read + sum-verified. Table posted to #jewlery-counts (CATCH-UP labeled).
- RESOLVED: WAY Monday +39 Rings anomaly = manager digit error (wrote 378, Bravo+Thursday sheet both say ~338/339).
- 8/18 + 8/19 nights unrecoverable (on-hand is live-state).
- LESSON: Chrome freezes while Parallels VM is pulling — never run Chrome + VM pulls concurrently. Sequencing rule codified in new catch-up task.
- HARDENING SHIPPED: (1) jewelry-pull-watchdog 9:15 AM Tue-Sun (haiku) — DMs Joshua if last night missing; (2) jewelry-onhand-catchup 7:45 AM Tue-Sun (sonnet) — auto-reruns a missed night inside the freeze window and posts the table. Count is now self-healing: miss at 8:30 PM -> auto-rerun 7:45 AM -> alert 9:15 AM only if both failed.

## 2026-08-22 07:30 — jewelry-onhand-catchup (Friday 8/21 CATCH-UP)
Nightly run partially completed (CUL, ROA only, both with a store-switch/read failure). Catch-up self-healed: pulled HAR, LEX, WAY fresh this morning inside freeze window (before 10 AM), then discovered CUL and ROA's overnight 2026-08-21 CSVs had corrupted category reads despite passing BoxReportName verification (CUL: Pendants 1336 vs 10-day trend ~250, Earrings 60 vs ~165, Necklaces 2 vs ~98; ROA: Bracelets 2 vs ~125-130) — re-pulled both fresh this morning, all 8/8 categories succeeded and matched historical trend + PM sheets closely.

Per-store final (Expected from Bravo / Counted from PM sheet, remapped PENDANTS=Pendants+Charms+Brooches, NECKLACES=Chains+Necklaces):
- CUL: Rings 631/631, Bracelets 123/122, Earrings 166/166, Pendants 296/296, Necklaces 211/211 — Total 1427/1426 (-1)
- HAR: Rings 453/455, Bracelets 49/49, Earrings 48/48, Pendants 121/118, Necklaces 121/134 — Total 792/804 (+12). Necklaces +13 over-variance flagged to Joshua via DM.
- LEX: Rings 277/278, Bracelets 37/38, Earrings 51/49, Pendants 54/52, Necklaces 46/46 — Total 465/463 (-2)
- ROA: Rings 559/559, Bracelets 129/129, Earrings 90/90, Pendants 156/155, Necklaces 163/165 — Total 1097/1098 (+1)
- WAY: Rings 339/338, Bracelets 42/42, Earrings 52/51, Pendants 66/66, Necklaces 66/67 — Total 565/564 (-1)

Empty-category treated as 0 (confirmed against prior-day CSV per rule): HAR Charms, LEX Brooches, WAY Charms.
Both sides confirmed inside the 6 PM-10 AM freeze window. No repeating variance pattern flagged beyond the HAR Necklaces note above; all other variances are small and in the expected scope-noise direction.
Posted to #jewlery-counts. DM sent to Joshua re: HAR Necklaces over-variance and the CUL/ROA bad-read self-heal.

## 2026-08-26 07:47 — jewelry-onhand-catchup (Tuesday 8/25 check)
Nightly 8:30 PM pull for 2026-08-25 confirmed successful — all 5 store jewelry-case-counts CSVs present (CUL, HAR, LEX, ROA, WAY) at pull time 07:47. Per catch-up Step 0.3, ended silently: no re-pull needed, no Slack post, no PM sheet cross-check performed.

## 2026-08-27 07:47 CATCH-UP CHECK
Yesterday: Wednesday 2026-08-26 (CUL-only per open-stores gate). CUL CSV present, all 8 rows status=ok. Nightly run complete — no catch-up action needed, nothing posted.
[2026-08-29 09:xx] jewelry-onhand-catchup: SKIPPED — 2026-08-28 nightly pull CSVs present for all 5 stores (CUL/HAR/LEX/ROA/WAY). No action needed.

## 2026-09-02 07:46-09:35 — Jewelry Onhand CATCH-UP for 2026-09-01 (Tuesday)
Trigger: nightly jewelry-onhand-nightly-pull did not run for 2026-09-01 (no CSVs found this morning) — catch-up self-heal executed before 9:30 AM freeze-window cutoff.
Open stores (Tue): CUL, HAR, LEX, ROA, WAY — all 5 completed.
Bravo pull (freeze-window Expected, this morning): CUL success 8/8. HAR partial 7/8 (Charms error — confirmed empty, matches prior-day 8/31, 8/28, 8/27, 8/25 CSVs, treated as 0). LEX partial 7/8 (Brooches error — confirmed empty, matches prior-day CSVs, treated as 0). ROA success 8/8. WAY partial 7/8 (Charms error — confirmed empty vs prior 4 days of CSVs incl 8/31, treated as 0; note: WAY Charms had a real positive count on 8/15 per prior list but has been error/0 consistently since 8/25-8/31, superseding that entry).
PM count sheets read from #end-of-day (Chrome vision pass), all 5 sum-verified against each sheet own written Totals line.
Per-store totals: CUL Expected 1425 / Counted 1424 (-1). HAR Expected 785 / Counted 793 (+8). LEX Expected 465 / Counted 467 (+2). ROA Expected 1092 / Counted 1093 (+1). WAY Expected 572 / Counted 571 (-1).
No anomalous OVER variance at category level beyond normal case-count-vs-system-scope noise (largest single-category delta: HAR Rings +4, HAR Necklaces +4). No DM sent to Joshua - clean night.
Posted Expected/Counted/Variance table to #jewlery-counts (C0BM9NHGTT4).
No repeating variance pattern flagged; HAR small positive Rings/Necklaces delta this run is a one-night reading, not an established pattern - watch next few nights if it recurs.

## 2026-09-03 07:47 CATCH-UP CHECK
Yesterday: Wednesday 2026-09-02 (CUL-only per open-stores gate). CUL CSV present, all 8 rows status=ok (Rings 631, Bracelets 123, Pendants 247, Charms 27, Brooches 21, Earrings 169, Chains 108, Necklaces 98). Nightly run complete — no catch-up action needed, nothing posted.
