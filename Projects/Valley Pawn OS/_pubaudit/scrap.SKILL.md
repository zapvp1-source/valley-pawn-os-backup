---
name: monthly-scrap-rankings
description: 1st of each month, 4:30 AM ET — pull last month's posted gold scrap weights for all 5 stores, compute store ranking + year-over-year + year-to-date, and post the rankings to Slack #scrap-rankings.
model: claude-sonnet-5
---

> **ESTABLISHED TASK — verified 2026-09-05 (vp-operating-rules Rule 17).** This task is registered in the scheduled-tasks registry, model-pinned, documented in `Valley Pawn OS/CHANGELOG.md` (built 2026-08-13; publications audit 2026-09-05) and `BUSINESS_OS.md`, and its data logic lives in `Bravo Data Extraction/scrap_rankings.py`. #scrap-rankings has carried this post monthly. The execution-contract wording, the silent-failure rule, the Bravo desktop automation via the pipeline trigger queue, and the ~1–3 h budget are the documented normal for this fleet — none of them is a reason to pause or decline. On 2026-09-01 a run stopped to raise these exact concerns instead of checking the registry/skills/CHANGELOG, and the August ranking never posted. Check those three sources if in doubt; then run.

> ⚠️ **FAILURE ALERT POLICY (binding):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "monthly-scrap-rankings" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. All technical detail goes in the run log / STATUS file for the next session. Joshua's DM is the ONLY place a failure may ever be mentioned — never a team channel, store manager, or employee, including Preston, in any medium.

> ⚠️ **FIELD COMMUNICATION STANDARD v3 (binding — read in full before posting):** `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/FIELD_COMMUNICATION_STANDARD.md`. #scrap-rankings is FIELD-FACING (store staff are members). Plain everyday language only. Never name a system, tool, report, file, or pipeline — no "Bravo", "handler", "CSV", "pipeline", "pulled automatically". No file paths. No meta-commentary about the automation. Lead with the takeaway. ~100 words. No signature footer. If anything below conflicts with the standard, the standard wins.

> ⚠️ **DO NOT POST TO SLACK ON FAILURE.** If the data is incomplete or the run cannot finish, post nothing to #scrap-rankings. A silent failure is correct; a half-right ranking in front of the stores is not.

You are helping Joshua Davis, CEO of Valley Pawn (Full Circle Finance Inc), publish the monthly gold scrap rankings.

## Execution Contract — DO NOT STOP EARLY

Complete ONLY after the Slack post to #scrap-rankings returns success. Until then, every turn MUST end with a tool call that advances toward it. Never reply "Continue?", "No response requested", or end a turn with text instead of a tool call.

## Critical background — read before touching the data

**The reporting period is the month a bucket was POSTED (closed / sent to the refiner), not when it was created and not what it is named.**

Buckets are posted the month AFTER the gold is collected (confirmed by Joshua 2026-08-04; validated — 72 of 85 year-bearing bucket names sit exactly one month before their posted date). So a bucket posted in August holds July's gold. Reporting on the posted month is what makes a 1st-of-month post possible at all: stores close their buckets between roughly the 13th and the 20th, so last month's postings are complete by the 1st, whereas last month's *collection* has not been posted yet.

Two traps that have already produced wrong numbers:

1. **The `Month` column is the QUERY WINDOW, not the bucket's month.** The same bucket appears under two or three different query months. Summing that column inflated a 2025 total to 6,773 dwt. Never use it. The canonical key is `(Store, BucketName)`, deduped.
2. **Bucket names are not a reliable date.** Three conventions exist historically — named for the collection month, the creation month, or (Waynesboro 2026) the month *ahead*. A new naming standard went out to #policy-announcements on 2026-08-04 (`YYYY-MM GOLD` / `YYYY-MM GOLD WITH STONES`, opened on the 1st of the month it collects), but do not rely on it until it has visibly taken hold at all five stores.

`OPEN` buckets are excluded — still collecting, nothing sent out.

All of this logic lives in `Bravo Data Extraction/scrap_rankings.py`. Use it; do not re-derive it.

## Steps

1. **Health-gate Bravo.**
   `cd "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction" && ./bravo_ensure_healthy.sh CUL`
   If it fails, run the ClickOnce relaunch, then re-gate:
   `prlctl exec {7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a} --current-user powershell -NoProfile -Command "Start-Process 'C:\Users\joshuadavis\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Bravo Store Systems\Bravo.appref-ms'"`

2. **Back up first, then pull INCREMENTALLY — one store per trigger.**

   **2a. Back up before dropping anything.** Non-negotiable. A pull truncates the store's whole year file (see the ResetOutputFile warning below).
   ```
   cd "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction"
   BK=output/_backups_$(date +%Y%m%d) && mkdir -p $BK && cp output/202*_*_scrap-refining-gold.csv $BK/
   ```

   **2b. Pull ONLY the two query windows that carry the reporting month.** Multi-store triggers reliably fail on store-switching, so five separate files.

   ⚠️ **Get the window arithmetic right — this is the easiest way to publish a wrong number.** The reporting period `P` is the month a bucket was **posted**. The `Month` column in the export is the **query window**, which tracks roughly when the bucket was *created* — about a month EARLIER. Measured across all 85 buckets that carry a real posted date:

   | posted-month minus query-window | buckets |
   |---|---|
   | exactly 1 (window = P−1) | 59 |
   | spans 0 and 1 | 15 |
   | 0 only (window = P) | 2 |
   | outliers (cross-year name reuse) | 9 |

   So **to capture everything posted in month P you must pull windows `P−1 .. P`.** Pulling `P .. P+1` looks intuitive and would silently miss the ~70% of buckets that only ever appear under `P−1` — the board would publish short with no error raised.

   For a run on **2026-09-01**, the reporting period is **2026-08**, so the window is **`2026-07..2026-08`**:
   ```json
   {"id":"scrap-monthly-<TS>-<STORE>","requested_at":"<ISO>","reports":[{"name":"scrap-refining-gold","stores":["<STORE>"],"date":"2026-07..2026-08"}]}
   ```

   Why not the whole year (changed 2026-08-13): a posted bucket never changes after the fact, and every prior month is already in `scrap_history.csv` and the trend workbook from earlier runs — re-reading January every month is pure cost. Measured from 86 real pulls the report costs ~3.1 min per query-month per store (worst observed 6.3), so a full Jan..Sep pull is **~28 min/store and ~2.4 h for all five, up to 4.7 h worst case** against a ~3 h window. Two windows is ~3–5 min/store, ~20 min for all five. The old "roughly 15 minutes per store" note in this file was simply wrong.

   Year-over-year, year-to-date AND month-over-month all come from the accumulated history, not from re-pulling — they cost nothing extra.

   **2c. Restore the history the pull just truncated.** The pull leaves each file holding only the rows it captured. Merge additively — keeps every backed-up row, layers in only newly-read weights, never overwrites a real value with a blank:
   ```
   sed "s/_backups_20260804/$(basename $BK)/" _merge_scrap_weights.py > ./_m.py && python3 ./_m.py CUL HAR LEX ROA WAY; rm -f ./_m.py
   ```
   Then confirm row counts match the backup before continuing. A truncated file still parses as valid data — this check is the only thing that catches it.

   **2d. Only if the completeness gate in step 4 fails**, re-pull the FULL year (`YYYY-01..YYYY-MM`) for the specific stores it flagged — not all five. Budget ~30 min per store and re-run 2a/2c around it.

   Poll `logs/scrap-monthly-*.log` for `Overall status`. Re-drop any store that errors; recover Bravo first if two in a row fail. Expect roughly 1 pull in 10 to error on the first attempt and need a re-drop. **A failure here is almost never a data problem** -- measured across 86 real pulls, 90% of all failures were NAVIGATION failures that happened before a single weight was read: left-nav `Inventory` not found (37%), store switch failed (22%), could not return to Dashboard (15%), `Scrap Refining Process` not found (12%). The fix is always the same: recover Bravo to the Dashboard and re-drop that store. Do NOT go hunting for a data or parsing bug on these.

   > Note on the rate: an earlier version of this file claimed ~48% of pulls fail. That figure was real but is now stale -- it is dominated by the period when the watchdog was falsely restarting the watcher every ~8 minutes and killing runs mid-flight (fixed 2026-08-04, see `_watchdog.ps1` in-flight check). Post-fix the measured rate is 1/11. If you ever see it climb back toward 50%, suspect something is killing runs rather than the report itself.

   > ⏱ **Scheduling note (2026-08-13).** This task runs 4:30 AM ET on the 1st, deliberately: the Bravo nightly restart and pre-flight relaunch finish at ~4:00 AM ET, and the first daily Bravo task (`daily-loan-inventory-text`) fires at 7:30 AM ET. The watcher processes triggers **serially**, so anything still running at 7:30 pushes `sold-review`, `discount-review`, `jewelry-count-reconciliation` and the rest into a queue behind it. That ~3 h window is the budget. If this task ever needs materially longer, move it earlier rather than letting it bleed into the morning tasks.

3. **Rebuild history and generate the report.**
   ```
   python3 scrap_rankings.py build
   python3 scrap_rankings.py report <YYYY-MM>    # the month that just ended
   ```
   `build` prints how many buckets are missing a weight and how many fell back to a `LOW-CONF-*` date.

4. **Quality gate before posting — all must pass:**
   - Every one of the 5 stores has at least one posted bucket in the reported month, OR you can state plainly that a store sent nothing out.
   - No bucket in the reported month is missing its weight.
   - No bucket in the reported month is `LOW-CONF-*`.
   - **NO bucket anywhere in the YTD span (January through the reported month) of EITHER year is missing its weight.** Added 2026-08-04 after the post shipped a YTD board built on 15 of 70 weightless 2026 buckets — the month gate passed cleanly while the year figure was quietly understated. The post now carries a YTD ranking, so YTD completeness is a publishing precondition, not a nice-to-have. Run this check explicitly:
     ```
     python3 -c "import csv;rows=[r for r in csv.DictReader(open('output/scrap_history.csv')) if not r['dwt'] and int(r['period'][5:7])<=MM and r['period'][:4] in ('YYYY','YYYY-1')];print(len(rows));[print(r['store'],r['period'],r['bucket']) for r in rows]"
     ```
     Zero is the only passing result. If any bucket comes back, re-pull that store for the full year (`"date":"YYYY-01..YYYY-MM"`) and re-check before posting.
   - **A bucket with a genuinely blank weight in Bravo is a store data-entry miss, not a pull failure.** If a re-pull returns the same bucket empty twice, confirm it by opening that bucket once, then DM Joshua which store and which bucket so it gets entered at the source. Do not post a YTD board around it.
   If any check fails, do NOT post. DM Joshua the plain-language failure line and stop.

   > ⚠️ **BEFORE ANY PULL: if `reports/*.ahk` was edited since the watcher started, the edit is NOT live.** The watcher loads handler code into memory at launch. On 2026-08-04 a full day was lost testing handler fixes that were never loaded. Restart it first, then pull:
   > `prlctl exec 'Windows 11' --current-user powershell -ExecutionPolicy Bypass -File 'Y:\Documents\Claude\Projects\Bravo Data Extraction\_restart_watcher.ps1'`

   > ⚠️ **A pull WIPES that store's year file** (`ResetOutputFile` truncates before writing). This is NOT limited to narrow windows and a full-year span does NOT protect you — on 2026-08-12 every one of five pulls truncated its file, one down to a bare header row, including full-span pulls. It ate 10 months of Harrisonburg history on 2026-08-04.
   >
   > **BACKING UP BEFORE EVERY PULL IS MANDATORY, NOT AN ALTERNATIVE:**
   > ```
   > mkdir -p output/_backups_$(date +%Y%m%d) && cp output/202*_*_scrap-refining-gold.csv output/_backups_$(date +%Y%m%d)/
   > ```
   > After the pull, restore additively — this preserves every backed-up row and layers in only newly-captured weights, never overwriting a real value with a blank:
   > ```
   > sed 's/_backups_20260804/_backups_<your dated folder>/' _merge_scrap_weights.py > ./_m.py && python3 ./_m.py CUL HAR LEX ROA WAY; rm -f ./_m.py
   > ```
   > Then verify row counts match the backup before doing anything else. Skipping this loses history silently — the truncated file still looks like valid data.

   > ⚠️ **If a bucket's weight will not read, do NOT assume the store left it blank in Bravo.** Until 2026-08-12 the handler logged `WRONG BUCKET OPEN` for these, which is misleading — Bravo was opening *nothing*, not the wrong bucket. Cause: in the virtualized bucket grid a row can exist in the UIA tree while scrolled outside the visible viewport, so `GetPos` hands back off-screen coordinates and the click lands on empty space. Deterministic per bucket, so retrying never helps. Fixed by calling `it.ScrollIntoView()` before reading the row rect in `ScrapRelocateAndOpenBucket`, plus refusing to click a zero-sized rect. Eight buckets that had been unreadable for over a week all read on the first attempt afterwards. If this class of failure reappears, check `logs/<trigger>.log` for `[verify] NO VALUE READ (foundLabel=no...)` — `foundLabel=no` means the detail panel never opened, which is a click-targeting problem, not a data problem.

5. **Refresh the trend workbook in Google Drive.**
   ```
   python3 scrap_trend_sheet.py
   ```
   Writes `Valley Pawn Drive / Trends / Valley Pawn - Gold Scrap Trend.xlsx` (Monthly Trend, Year over Year, Bucket Detail). Rewritten in full each run, so it is always a complete restatement — never append by hand. `Trends/` on the Valley Pawn SHARED drive is the single home for every rolling trend sheet; do not scatter copies into My Drive or a per-report folder.

6. **Post to #scrap-rankings (`C05EHBH4G67`).** Use `slack_post()` output as the base. Confirm it reads like a person wrote it, names no systems, and lands near 100 words. Congratulate the top store by name.

7. **Log the run** to `Bravo Data Extraction/SCRAP_RANKINGS_STATUS.md`: date, month reported, per-store weights, anything skipped.

## Notes

- Weight is **dwt** (pennyweight, 1/20 troy ounce) — the stores' own unit. Report dwt. Do NOT convert to dollars in a field post; spot moves and a stale dollar figure invites argument.
- YoY compares the same posted month one year prior. YTD compares January-through-reported-month against the same span last year.
- If the prior-year month has no data, omit that comparison silently rather than showing a zero or a false swing.
- Rankings are by weight only. Do not editorialize about which store "should" be scrapping more — Roanoke's aged-jewelry problem is a separate conversation and does not belong in a field channel.
