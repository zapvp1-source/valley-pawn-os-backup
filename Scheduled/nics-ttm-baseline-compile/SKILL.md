---
name: nics-ttm-baseline-compile
description: One-time ~5:15 PM: compile the trailing-12-month FFL transfer baseline (Aug 2025–Jul 2026, all 5 stores) from the CSVs the watcher pulled, re-run any missing store-months, build an xlsx baseline, and post the summary to #ffl-transfer-performance + DM Joshua.
---

Finish the trailing-12-month FFL "nics-transfers" baseline (fill remaining gaps), update the Drive trend report in place, and post. Runs LATE (11 PM) on purpose — after the evening Bravo tasks (daily-funds ~6, funds-watchdog ~6:47, jewelry ~7:47/8:30/9:45). BOUNDED — do not rebuild the handler, do not touch the display, do not re-enable scrap.

CONTEXT: Read skills enterprise-map, valley-pawn-context, bravo-context. Bravo folder access via mcp__Control_your_Mac__osascript `do shell script` only. PROJECT: /Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction (=<DIR>). CSVs: <DIR>/output/YYYY-MM-01_to_YYYY-MM-LAST_<STORE>_nics-transfers.csv. Stores WAY,CUL,HAR,LEX,ROA. VM UUID {7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}; prlctl /usr/local/bin/prlctl (fallback /Applications/Parallels Desktop.app/Contents/MacOS/prlctl).

SCOPE: 12 months Aug 2025..Jul 2026 x 5 stores = 60 store-months. Ranges 1st..last day (calendar last day; Feb 2026=28). ~52 of 60 were already pulled this afternoon; the likely gaps are CUL 2025-11/2026-01/2026-02, LEX 2026-07, ROA 2025-08/09/10/11 (recompute — do not assume).

STEP 1 — inventory (osascript+python3): list which of the 60 store-months are MISSING a csv.

STEP 2 — fill gaps: IDLE-GUARD FIRST — confirm the watcher is idle (no <DIR>/logs/*.log modified in ~2 min; nothing in <DIR>/triggers or triggers/claimed in flight) and no other Bravo automation is mid-run. If busy, wait up to 15 min, re-check; only abort if you truly cannot get an idle window. Then drop single-store triggers ttmfix2-<STORE>-<YYYYMM>-<ts>.json STORE-FIRST (all of one store's months before the next store, to avoid store re-cycling), a few at a time, wait for each csv (poll ~4 min), and re-drop each missing store-month at most ONCE. Leave any still-failed store-month blank and label it "pending".

STEP 3 — Drive trend report IN PLACE (this is how we update all our analytics; NEVER use the Drive create_file connector for updates): run `/usr/bin/python3 "<DIR>/ffl_trend_sync.py"`. It rebuilds every COMPLETE month (all 5 stores) from the raw CSVs and upserts them keyed by Month into "Valley Pawn - FFL Transfer Trend (Monthly)" (id 1cek7S5KNKAywF_cPWgiASOZaNAVrF4e1EpMv-4KDURs, tab Monthly). Print its output. URL: https://docs.google.com/spreadsheets/d/1cek7S5KNKAywF_cPWgiASOZaNAVrF4e1EpMv-4KDURs/edit

STEP 4 — local xlsx: build FFL_Transfers_TTM_Baseline_Aug2025-Jul2026.xlsx (xlsx skill) in outputs — matrix (rows=12 months, cols=5 stores; counts + revenue; per-month + per-store totals) + a sheet listing any still-pending store-months. present_files it.

STEP 5 — post to Slack #ffl-transfer-performance (C0BPH5T1NFL): concise 12-month baseline table (transfers by store by month + company total per month) + 12-mo company total, plus the trend sheet URL. Then DM Joshua (U03BB52MDSA): months complete vs any still pending, 12-mo totals, xlsx link, trend sheet URL, and a reminder that the scrap-closeout system is PAUSED (Windows task ScrapCloseoutWatcherWatchdog disabled + watcher killed) — tell me to re-enable when he wants scrap back.

Never present partial data as complete — label missing store-months "pending", never zero. One-time task; done after this run.