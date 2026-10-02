# Scrap Rankings — Run Log

Run log for the `monthly-scrap-rankings` scheduled task (1st of month, 4:30 AM ET).
Newest first.

---

## 2026-10-01 — POSTED (2026-09; on-schedule 4:30 AM ET run)

- **Health gate:** could not run `bravo_ensure_healthy.sh` from this Cowork session (no `prlctl`/host
  shell access from the Linux sandbox this run executed in — a gap worth noting for future runs of
  this task from Cowork rather than a native agent). Proceeded straight to trigger-drop pulls per
  the task's own recipe, since trigger-drop is the lower-risk Type A path.
- **Pulls:** backed up all 10 `*_scrap-refining-gold.csv` files first (`output/_backups_20261001/`).
  Window `2026-08..2026-09`, one trigger per store. Bravo was genuinely unstable this morning —
  **10 consecutive EnsureStore/navigation failures** across 6 drop-rounds before the first store
  (ROA) succeeded; HAR/LEX/CUL needed 2-4 retries each before landing. No contention found (guard
  was CLEAR throughout, no other trigger running) — this was Bravo itself (auto-lock loops, store
  row not rendering, "Scrap Refining Process" not found), not a pull-logic problem, consistent with
  the task's own note that most failures are navigation, not data. All 5 stores eventually
  succeeded on a straight re-drop, no manual Bravo recovery was available/needed.
- **Merge-restore:** `_merge_scrap_weights.py` run after the pull; CUL's partial first pull (19 rows)
  was topped back up to the backup's 20; HAR/LEX/ROA/WAY all pulled >= backup row counts (net-new
  rows only, nothing lost). Verified row counts match before continuing.
- **DEFECT FOUND AND FIXED in `scrap_rankings.py`** (backup `scrap_rankings.py.bak-20261001-stdname-offset`).
  First build/report for September came back with `"cur": {}` — 0 dwt company-wide — despite HAR,
  LEX and ROA each having a real CLOSED, posted-in-September bucket on hand (confirmed by reading
  the raw CSVs directly, not trusting the script's own output). Root cause: the "HOUSE STANDARD
  FIRST" rule added 2026-08-13 assumed a `YYYY-MM GOLD` bucket name states its OWN period verbatim
  (name = period, no shift), on the theory that a standard bucket would be created+named+posted
  within one calendar month. That assumption has not held: by today, 6 CLOSED buckets across 3
  stores (HAR x2, LEX x2, ROA x2) had gone from created to posted under this naming format, and
  **every single one** posted exactly one calendar month after its own name (e.g. HAR "2026-08
  GOLD" created 9/1, posted 9/28) — i.e. stores adopted the new `YYYY-MM` string but kept naming it
  for the COLLECTION month, same as every legacy convention. Zero of six supported the no-shift
  assumption. Fixed `resolve_month()` to apply the same "name = collection month, period = name+1"
  offset to standard-name buckets as to legacy names (full confidence, not LOW-CONF, since the name
  itself is unambiguous). Verified via diff of `scrap_history.csv` before/after: the ONLY change was
  those 6 rows moving from period 2026-08 to 2026-09 — nothing else shifted, and none of the 6 were
  part of the already-published August total (all 6 were still OPEN as of the 9/5 August run, so no
  retroactive change to a number already in front of the stores).
- **Quality gate — all passed:** HAR/LEX/ROA have real September buckets (full-confidence
  `standard-name` source, not LOW-CONF); CUL and WAY verified via raw CSV to genuinely have nothing
  posted this period (CUL's Aug-named bucket has sat OPEN since 8/4; WAY has not opened a new bucket
  since its already-reported early-August one) — not a pull gap. Zero missing weights in the
  reported month. Zero blank-weight YTD rows Jan-Sep either year.
- **Published September 2026:** Company 308 dwt (vs 472 LY, −35%; vs 608 Aug, −49%).
  Roanoke 114 · Harrisonburg 105 · Lexington 89. Culpeper and Waynesboro had nothing posted yet —
  said so plainly in the post rather than showing a false zero or silently dropping them.
  YTD 5,046 vs 4,092 (+23%): Culpeper 1,779 · Harrisonburg 988 · Roanoke 810 · Waynesboro 755 ·
  Lexington 715.
- **Slack:** https://valleypawnworkspace.slack.com/archives/C05EHBH4G67/p1790854661991089 (no footer).
- **Trend workbook — NOT refreshed in Drive this run.** Rebuilt the workbook locally (20 posted
  months, matches the fixed history) but the Google Drive connector's `create_file` call to replace
  `Valley Pawn Drive/Trends/Valley Pawn - Gold Scrap Trend.xlsx` was auto-declined by the platform
  ("no one was available to approve it during this scheduled run"). This Cowork session has no
  mounted path to that Drive folder either (only `Documents/Claude/Projects` was connected), so
  there was no fallback write path. **Needs Joshua:** either approve a Drive-write action for this
  task going forward, or connect the Google Drive folder to this task's session so the native
  `scrap_trend_sheet.py` path works directly. The rebuilt workbook is sitting in the session's
  temp output, not yet delivered anywhere durable — next run should just rebuild fresh rather than
  trying to recover it from here.
- **Next run:** 2026-11-01 → report period 2026-10, pull window 2026-09..2026-10. Worth checking
  whether CUL's long-open bucket (open since 8/4, ~2 months — unusually long) and WAY's bucket gap
  have resolved by then; if CUL is still open at the next run it may be worth a plain-language nudge
  to the store rather than letting it run indefinitely.

## 2026-09-05 — POSTED (catch-up for 2026-08; the 9/1 4:30 AM run posted nothing)

- 16:50 ET: a second run of the catch-up one-shot fired; duplicate guard found the August post already in #scrap-rankings (16:22) → no pull, no post, no file changes.

- **Run:** one-shot `catchup-scrap-rankings-aug-2026`, 15:46–16:25 ET. Queue idle at start (no pending
  triggers, no prestage claims, guard CLEAR). Health gate PASS on CUL.
- **Pulls:** 5 single-store triggers, window `2026-07..2026-08`, all 5 `Overall status: success` on
  first attempt (CUL 3.0 min, HAR 4.9, LEX 8.8, ROA 5.6, WAY 4.7). Backup `output/_backups_20260905/`
  taken first; merge-restore run; every year file now has >= its backup row count (no truncation).
- **Duplicate guard:** #scrap-rankings had no August post (last was the July board, 8/12) — clean.
- **Published August 2026:** Company 608 dwt (vs 596 LY, +2%; vs 555 July, +10%).
  ROA 166.5 · CUL 162.8 · HAR 147.9 · WAY 79.9 · LEX 51.0.
  YTD 4,738 vs 3,620 (+31%): CUL 1,779 · HAR 883 · WAY 755 · ROA 695 · LEX 626.
  All 10 August buckets resolved from a real posted date; YTD blank-weight gate = 0.
- **Slack:** https://valleypawnworkspace.slack.com/archives/C05EHBH4G67/p1788639752443899 (no footer).
- **Trend workbook:** rewritten — `Valley Pawn Drive/Trends/Valley Pawn - Gold Scrap Trend.xlsx`
  (19 posted months).
- **DEFECT FOUND AND FIXED in `scrap_rankings.py`** (backup `scrap_rankings.py.bak-20260905`).
  First build showed Harrisonburg with ZERO August buckets even though the pull had both
  (`GOLD W STONES` 72.79 posted 8/6, `GOLD W/O STONES 7/31/26` 75.14 posted 8/6). Two causes:
  (1) HAR reuses the exact name `GOLD W STONES` every month, and `load_raw()` keyed by
  (store, bucket, file-year) folded the Aug bucket into the June-created one; (2) a stale row
  from an earlier pull still showed `GOLD W/O STONES 7/31/26` as OPEN, and first-seen-wins kept
  it OPEN → excluded. Fix: key now also includes CreatedOn, and a CLOSED read overrides a
  stale OPEN read (status, posted date, weight). Verified by diffing per-store/period totals
  old vs new script: the ONLY change is HAR 2026-08 0 → 147.9. Nothing else moved.
  Without this fix the board would have shipped 460 dwt (−23% YoY) with Harrisonburg silently
  absent — a Rule-18 miss the completeness gate did not catch, because the store had rows
  in the raw file, just none that resolved to the month.
- **Watch item:** Harrisonburg's naming (`GOLD W STONES` reused monthly, no month, no year) is
  the one store still far from the `YYYY-MM GOLD` standard announced 8/4. LEX/ROA/WAY have
  adopted it for their September (OPEN) buckets; CUL and HAR have not.
- **Why 9/1 posted nothing:** per CHANGELOG 2026-09-05 (5), the 9/1 run declined to execute
  (Rule 17 preamble for SKILL.md drafted at `_pubaudit/scrap.SKILL.md`, not yet installed).

## 2026-08-21 — NO-OP (duplicate guard) — off-cycle run, July already published

- **Trigger context:** Task was enabled/registered 2026-08-21 (see Valley Pawn OS CHANGELOG); this
  fire was an off-cycle/registration run, not the scheduled 1st-of-month 4:30 AM fire.
- **Reporting period for a run today:** 2026-07 (last complete posted month). August is not a
  complete posted month until 9/1.
- **Duplicate-guard check:** #scrap-rankings (C05EHBH4G67) already carries the July 2026 board,
  posted **2026-08-12 16:04 ET**. Verified against channel output (Rule 12), not run records.
- **Published July numbers (for reference):** Company 555 dwt (vs 442 LY, +26%). Culpeper 277,
  Roanoke 96, Lexington 65, Harrisonburg 61, Waynesboro 57. YTD 4,130 vs 3,023 (+37%).
- **Data state at time of run:** `output/scrap_history.csv` built 2026-08-13; five per-store 2026
  CSVs current as of 8/12–8/13; trend workbook refreshed 8/12. Consistent with the 8/12 publish.
- **Action taken:** none — no Bravo pull (avoids mid-day contention for zero new data), no Slack
  post (field channel dup), no trend-sheet rewrite. Silent success per Field Communication
  Standard v3 routing.
- **Note for next run:** the 8/12 post carries a "Sent using Claude" footer — v3 standard forbids
  signature footers. Omit it on the 2026-09-01 post.
- **Next real run:** 2026-09-01 4:30 AM ET → report period 2026-08, pull windows 2026-07..2026-08.
