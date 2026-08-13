---
name: monthly-scrap-rankings
description: 1st of each month, 8 AM ET — pull last month's posted gold scrap weights for all 5 stores, compute store ranking + year-over-year + year-to-date, and post the rankings to Slack #scrap-rankings.
model: claude-sonnet-5
---

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

2. **Pull fresh scrap data, ONE STORE PER TRIGGER.** Multi-store triggers reliably fail partway through on store-switching. Drop five separate trigger files into `triggers/`, one per store, covering the current year through the current month — e.g. for a run on 2026-09-01:
   ```json
   {"id":"scrap-monthly-<TS>-<STORE>","requested_at":"<ISO>","reports":[{"name":"scrap-refining-gold","stores":["<STORE>"],"date":"2026-01..2026-09"}]}
   ```
   Each store takes roughly 15 minutes (the report opens every bucket individually to read its weight). Poll `logs/scrap-monthly-*.log` for `Overall status`. Re-drop any store that errors; recover Bravo first if two in a row fail.

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
