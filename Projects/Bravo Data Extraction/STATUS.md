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

## 2026-09-11 09:48 ET — jewelry-onhand-catchup run (for 2026-09-10, Thursday)
Nightly jewelry-onhand-nightly-pull did not produce 2026-09-10 CSVs (no run found for that date) — catch-up pull fired this morning inside the 6PM-10AM freeze window (started 07:49 ET, well before the 09:30 cutoff).

Bravo pull (Expected, on-hand this morning, reflects 9/10 close): all 5 open stores (CUL, HAR, LEX, ROA, WAY — Thursday is a full-open day) completed via jewelry-case-counts-v2. Combo-select flakiness caused retries at CUL Rings, LEX Chains, ROA Chains (all recovered via the handler's own retry/GUID-probe/outer-retry ladder — no manual intervention). Confirmed-empty-category reads: HAR Charms, LEX Brooches, WAY Charms — each cross-checked against the most recent prior-day CSV (2026-09-08), which also showed error/empty for the same store+category, so treated as 0 per the no-false-zeros rule.

PM count sheets read via Chrome from #end-of-day (C03C7HV8L48), 2026-09-10 date block on each store's sheet, sum-verified against each sheet's own written TOTALS line.

Per-store Total (Expected/Counted/Variance): CUL 1458/1457/-1, HAR 785/791/+6, LEX 471/473/+2, ROA 1126/1126/0, WAY 573/572/-1. All variances small and within normal scope-noise range (Bravo counts case+safe+back-stock+bins vs sheet's display case only) — no anomalous OVER variance, no DM sent to Joshua.

Posted Expected/Counted/Variance table to #jewlery-counts (C0BM9NHGTT4): https://valleypawnworkspace.slack.com/archives/C0BM9NHGTT4/p1789134489387119

No variance repeats a prior night's pattern in a way that suggests a process/data problem (single-night figures, not compared multi-night here — see nightly runs for trend).

## 2026-09-21 23:50 ET — jewelry-onhand-nightly-pull

Monday — all 5 stores open (Culpeper + HAR/LEX/ROA/WAY). Freeze window (6PM close → 10AM reopen) confirmed on both sides: Bravo pulled between 21:06-23:47 ET tonight (within window), PM count sheets photographed by managers 18:08-18:37 ET tonight (also within window, before close-adjacent freeze).

Host-access note: `mcp__Control_your_Mac__osascript` is confirmed permanently gone from this session class (per CHANGELOG 2026-09-20). Ran entirely via the host job queue (`bravo_pull.sh`, one trigger per store) per this task's own 2026-09-17 HOST ACCESS override. HAR and LEX both wedged on their first pass (host-queue TIMEOUT after self-heal) — ran `bravo_unwedge.sh` once, then re-queued both; both completed clean on retry (HAR finished 23:14, LEX finished 23:47 after a long combo-select stall on Chains that resolved via the handler's own outer-retry ladder, no manual intervention).

**Bravo (expected, on-hand tonight) — all 5 stores 7/8 or 8/8, all errors are the already-confirmed-empty categories (matched against 2026-09-19 CSVs, same category also errored that night):**
- CUL: 8/8 ok
- HAR: 7/8 ok, Charms error (confirmed empty, treated as 0)
- LEX: 7/8 ok, Brooches error (confirmed empty, treated as 0)
- ROA: 8/8 ok
- WAY: 7/8 ok, Charms error (confirmed empty, treated as 0)

**PM count sheets (#end-of-day, Chrome vision, sum-verified against each sheet's own TOTALS line):**
- CUL (Sandi): Rings 672, Bracelets 117, Necklaces 149, Earrings 142, Pendants 260 — sheet total 1340 ✓
- HAR (Walker Tapley): Rings 461, Bracelets 47, Necklaces 114, Earrings 47, Pendants 116 — sheet total 785 ✓
- LEX (Uriah): Rings 297, Bracelets 38, Necklaces 47, Earrings 47, Pendants 55 — sheet total 484 ✓
- ROA (Benjie Moore): Rings 566, Bracelets 139, Necklaces 168, Earrings 74, Pendants 177 — sheet total 1124 ✓
- WAY (Chadd): **NOT USABLE.** The photo posted tonight is the same physical sheet flagged 9/19 — 9/19 and 9/20 blocks are filled, but the 9/21 block was left blank. No correction posted afterward. Excluded from tonight's table, no data guessed. This is the 2nd time in 3 nights this has happened at Waynesboro — worth a direct nudge to Chadd/Martin D. to consolidate onto one current sheet.

**Variance table (Counted − Expected; category mapping: PENDANTS = Pendants+Charms+Brooches, NECKLACES = Chains+Necklaces per the 2026-08-14 standard):**

| Store | Category | Expected | Counted | Variance |
|---|---|---|---|---|
| CUL | Rings | 672 | 672 | 0 |
| CUL | Bracelets | 118 | 117 | -1 |
| CUL | Necklaces | 149 | 149 | 0 |
| CUL | Earrings | 142 | 142 | 0 |
| CUL | Pendants | 260 | 260 | 0 |
| **CUL** | **Total** | **1341** | **1340** | **-1** |
| HAR | Rings | 461 | 461 | 0 |
| HAR | Bracelets | 47 | 47 | 0 |
| HAR | Necklaces | 112 | 114 | +2 |
| HAR | Earrings | 46 | 47 | +1 |
| HAR | Pendants | 117 | 116 | -1 |
| **HAR** | **Total** | **783** | **785** | **+2** |
| LEX | Rings | 294 | 297 | +3 |
| LEX | Bracelets | 37 | 38 | +1 |
| LEX | Necklaces | 47 | 47 | 0 |
| LEX | Earrings | 47 | 47 | 0 |
| LEX | Pendants | 56 | 55 | -1 |
| **LEX** | **Total** | **481** | **484** | **+3** |
| ROA | Rings | 566 | 566 | 0 |
| ROA | Bracelets | 139 | 139 | 0 |
| ROA | Necklaces | 166 | 168 | +2 |
| ROA | Earrings | 79 | 74 | -5 |
| ROA | Pendants | 179 | 177 | -2 |
| **ROA** | **Total** | **1129** | **1124** | **-5** |
| WAY | — | — | — | excluded, no usable PM sheet tonight |

No variance is anomalous in the OVER direction beyond routine noise (largest single-category over is HAR/LEX +2/+3, nowhere near the ROA-pendants-as-charms magnitude that would warrant urgent attention). All within normal scope-noise range documented for this task (Bravo counts case+safe+back-stock+bins vs. sheet counts display case only).

**NOT POSTED to #jewlery-counts** — `slack_send_message` was auto-declined ("no one was available to approve it during this scheduled run"), the same unattended-approval gap already on record fleet-wide for browser/Slack-writing tasks in this session class. Table above is ready to post verbatim once approved. Logged to FAILURE_LEDGER.md per Failure Policy v3 — no DM sent.

Repeat-check: no store/category combo above repeats a prior night's anomaly pattern (HAR/LEX small overs and ROA -5 look like independent one-night noise, not a recurring drift — nothing here matches the standing ROA-pendants-as-charms swing).
