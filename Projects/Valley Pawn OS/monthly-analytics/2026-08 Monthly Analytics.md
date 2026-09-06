# Monthly Analytics Report — August 2026 (report month)

**Run:** 2026-09-01, ~1:48 AM ET (monthly-analytics-report scheduled task)
**Result:** HALTED before Sheet/Slack — sidecar CSVs 0/30 present. Exited silently per policy (watchdog at 7 AM is the notification path).

## Step 1 — Date windows computed

| Window | Start | End |
|---|---|---|
| same-month-current | 2026-08-01 | 2026-08-31 |
| same-month-prior | 2025-08-01 | 2025-08-31 |
| ytd-current | 2026-01-01 | 2026-08-31 |
| ytd-prior | 2025-01-01 | 2025-08-31 |
| t12m-current | 2025-09-01 | 2026-08-31 |
| t12m-prior | 2024-09-01 | 2025-08-31 |

## Step 2 — Sidecar inventory

`output/monthly-analytics/2026-08/` — folder exists (created Aug 31 20:10) but is EMPTY. 0/30 XLSX files present. No `2026-08 Prestage.md` working file was written by monthly-analytics-prestage at all this run (July's equivalent failure at least produced its own status file — this is a new, different, and worse symptom).

Per the >4-missing threshold, halted here. Steps 3-6 (parse, YoY compute, Google Sheet, Slack posts) NOT executed. Nothing posted to #company-performance or #store-performance. No Google Sheet created this run.

## Root cause — DIFFERENT from July's failure, and NOT a Bravo-login problem this time

Checked the actual Bravo Data Extraction pipeline results (not just the sidecar folder):
- All 6 window triggers (same-month-current through t12m-prior) show `"status": "success"` in their result.json files, with all 5 stores (`CUL/HAR/LEX/ROA/WAY`) succeeding on every window — 30/30 Bravo cells actually completed cleanly between 8:11 PM and 9:05 PM ET on 8/31. This is the opposite of July (which was blocked by `bravo-not-ready` before any cell ran).
- The raw per-store EndOfMonth exports DID land on the Mac side (verified on disk, e.g. `2025-08-31_WAY_end-of-month.xlsx` written 9:04 PM, `2025-08-31_ROA_end-of-month.xlsx` 9:02 PM, etc.) — confirmed via `ls` and by tailing the raw pipeline logs (no errors, "Overall status: success" on every log).
- **The actual break is the window-tagged sidecar COPY step that monthly-analytics-prestage is supposed to perform after each window** ("copies each window's CSVs to a window-tagged sidecar so the same-End-date overwrites don't stomp each other" — per its own task description). None of the 6 trigger logs show any copy/sidecar activity at all — the raw pipeline script and the copy step appear to be decoupled, and the copy step did not run (or errored silently) this cycle.
- **Consequence — this is NOT safely recoverable by copying the surviving raw files after the fact:** same-month-current, ytd-current, and t12m-current all end on 2026-08-31 and therefore all write to the SAME shared Windows-side output filename per store. They ran sequentially (same-month-current finished ~8:20 PM, ytd-current ~8:36 PM, t12m-current ~8:55 PM), so each later window's export overwrote the earlier one's file before any copy happened. Only t12m-current's 12-month totals survive on disk under that filename — same-month-current's (August-only) and ytd-current's (Jan-Aug) period totals are gone, not just missing a copy. Mirror situation for the three 2025-08-31-ending windows (same-month-prior/ytd-prior/t12m-prior) — only t12m-prior survives.
- Because 4 of the 6 windows' period-specific sales/revenue figures cannot be reconstructed from what remains on disk, and Rule 18 / the completeness gate forbid posting anything not fully accurate, no attempt was made to reconstruct or partially post this run.

## What the next session / a human needs to do

1. This is a code bug in `monthly-analytics-prestage`'s copy-to-sidecar logic (missing, or failing silently, or racing against the next window's trigger) — not a Bravo/login/data problem. Needs a look at that task's own script, not a re-run of this one.
2. Fastest real fix: re-run `monthly-analytics-prestage` for the 2026-08 report month NOW (tonight, before the copy-collision reasoning above goes stale) — the underlying Bravo pipeline itself is healthy, so a fresh prestage pass should succeed IF the sidecar-copy step is fixed or if each window is fully copied out before the next window starts.
3. Once real sidecar files exist (30/30) for 2026-08, `monthly-analytics-report` completes in about a minute per its own SKILL.md — no need to touch this file's logic.
4. Per this task's own hard rules (no computer-use, no touching `EndOfMonth.ahk`/other production infra, additive-only), this run intentionally did not attempt to patch `monthly-analytics-prestage` itself.

## Slack posts

Neither #company-performance nor #store-performance was posted to this run (COMPLETENESS GATE — 0/30, not 30/30). `monthly-analytics-watchdog` (7 AM ET) is the one authorized notification path and should DM Joshua referencing this file.

## Catch-up 2026-09-05 (task `catchup-monthly-analytics-aug-2026`, 15:38 ET)

**Result: POSTED.** #company-performance post https://valleypawnworkspace.slack.com/archives/C0B26GD8D2R/p1788637103494969 (ts 1788637103.494969). Duplicate guard checked first — no prior August 2026 post existed. Not posted to #store-performance (removed 2026-09-05).
Google Sheet: Monthly Analytics - August 2026 — https://docs.google.com/spreadsheets/d/1-jAXcWZnQiZk_jR4pawiivlXzkjIa5gVHQ-lWDFkN9U/edit (Monthly Reports folder).

Readiness gate: sidecar 30/30 xlsx all ≥ 2 KB (60–170 KB); `2026-08 Prestage.md` Status COMPLETE 30/30; runner not running (finished 14:40). parse_eom.py returned real non-zero values for all 30 (store × window) — Rule 18 completeness gate passed, no incomplete cells.

### Windows (all reporting_dates from CSV line 1 matched exactly — no T12M calendar clamp variance)
| Window | Range |
|---|---|
| same-month-current | 8/1/2026 - 8/31/2026 |
| same-month-prior | 8/1/2025 - 8/31/2025 |
| ytd-current | 1/1/2026 - 8/31/2026 |
| ytd-prior | 1/1/2025 - 8/31/2025 |
| t12m-current | 9/1/2025 - 8/31/2026 |
| t12m-prior | 9/1/2024 - 8/31/2025 |

### Parsed values (store × window) — inventory / loans / total_sales / scrap_cost / psc / net_revenue
- same-month-current: CUL 201146.92/200202.75/64396.37/6823.34/24598.83/61998.28 · HAR 164819.61/175232.55/63145.84/7030.57/21447.30/54413.07 · LEX 92923.68/86672.60/32293.46/2092.00/9680.77/27754.28 · ROA 138932.75/152087.22/50498.59/7969.00/18434.77/48167.81 · WAY 131099.90/118583.54/47908.10/3406.98/15819.45/40705.46
- same-month-prior: CUL 178881.67/138007.75/66704.86/8544.07/15879.87/50163.53 · HAR 115188.96/180793.33/39840.94/4487.41/21098.94/39769.17 · LEX 67324.58/78373.00/26681.52/4532.88/9385.69/21270.08 · ROA 114147.24/122031.17/33867.88/5140.66/15532.70/32867.08 · WAY 62365.19/82862.38/38851.58/4785.02/11933.40/31240.09
- ytd-current: CUL —/—/652195.76/98382.90/157820.89/528104.46 · HAR —/—/468770.20/54616.15/164602.66/403703.34 · LEX —/—/234885.83/28988.39/77413.89/201015.68 · ROA —/—/374327.07/45652.29/138032.07/346668.48 · WAY —/—/378207.79/37833.36/108084.72/311601.00 (balances identical to same-month-current, as expected)
- ytd-prior: CUL —/—/435087.79/52483.43/123236.32/350052.10 · HAR —/—/293612.48/21356.36/154558.57/301990.11 · LEX —/—/180533.24/15812.88/83963.84/172922.92 · ROA —/—/245345.62/28343.16/115652.66/241279.04 · WAY —/—/293705.55/28912.50/89615.13/237209.94
- t12m-current: CUL —/—/976811.15/140248.92/223637.70/767112.67 · HAR —/—/646990.53/74278.69/258487.84/589329.21 · LEX —/—/345639.36/43521.00/118247.83/297865.28 · ROA —/—/542354.91/67290.39/199837.30/494571.54 · WAY —/—/547206.34/54410.15/154000.26/440535.35
- t12m-prior: CUL —/—/667063.59/76225.89/183063.19/528790.46 · HAR —/—/443979.81/32477.28/231113.54/453240.00 · LEX —/—/277770.70/20861.35/121831.09/259353.42 · ROA —/—/353051.16/35248.66/170981.06/352895.61 · WAY —/—/456093.75/45417.14/133184.28/362705.32

### YoY — Grand Total + per-store Var %
#### Same Month: Aug 2026 vs Aug 2025
| Metric | GT Cur | GT Prior | Var $ | Var % | CUL | HAR | LEX | ROA | WAY |
|---|---|---|---|---|---|---|---|---|---|
| Inventory | 728,922.86 | 537,907.64 | 191,015.22 | +35.5% | +12.4% | +43.1% | +38.0% | +21.7% | +110.2% |
| Loans Out | 732,778.66 | 602,067.63 | 130,711.03 | +21.7% | +45.1% | -3.1% | +10.6% | +24.6% | +43.1% |
| Total Sales | 258,242.36 | 205,946.78 | 52,295.58 | +25.4% | -3.5% | +58.5% | +21.0% | +49.1% | +23.3% |
| Scrap Cost | 27,321.89 | 27,490.04 | -168.15 | -0.6% | -20.1% | +56.7% | -53.8% | +55.0% | -28.8% |
| Service Charges | 89,981.12 | 73,830.60 | 16,150.52 | +21.9% | +54.9% | +1.7% | +3.1% | +18.7% | +32.6% |
| Net Revenue | 233,038.90 | 175,309.95 | 57,728.95 | +32.9% | +23.6% | +36.8% | +30.5% | +46.6% | +30.3% |

#### YTD: Jan-Aug 2026 vs Jan-Aug 2025
| Metric | GT Cur | GT Prior | Var $ | Var % | CUL | HAR | LEX | ROA | WAY |
|---|---|---|---|---|---|---|---|---|---|
| Total Sales | 2,108,386.65 | 1,448,284.68 | 660,101.97 | +45.6% | +49.9% | +59.7% | +30.1% | +52.6% | +28.8% |
| Scrap Cost | 265,473.09 | 146,908.33 | 118,564.76 | +80.7% | +87.5% | +155.7% | +83.3% | +61.1% | +30.9% |
| Service Charges | 645,954.23 | 567,026.52 | 78,927.71 | +13.9% | +28.1% | +6.5% | -7.8% | +19.4% | +20.6% |
| Net Revenue | 1,791,092.96 | 1,303,454.11 | 487,638.85 | +37.4% | +50.9% | +33.7% | +16.2% | +43.7% | +31.4% |

#### T12M: Sep 2025-Aug 2026 vs Sep 2024-Aug 2025
| Metric | GT Cur | GT Prior | Var $ | Var % | CUL | HAR | LEX | ROA | WAY |
|---|---|---|---|---|---|---|---|---|---|
| Total Sales | 3,059,002.29 | 2,197,959.01 | 861,043.28 | +39.2% | +46.4% | +45.7% | +24.4% | +53.6% | +20.0% |
| Scrap Cost | 379,749.15 | 210,230.32 | 169,518.83 | +80.6% | +84.0% | +128.7% | +108.6% | +90.9% | +19.8% |
| Service Charges | 954,210.93 | 840,173.16 | 114,037.77 | +13.6% | +22.2% | +11.8% | -2.9% | +16.9% | +15.6% |
| Net Revenue | 2,589,414.05 | 1,956,984.81 | 632,429.24 | +32.3% | +45.1% | +30.0% | +14.8% | +40.1% | +21.5% |
(Inventory / Loans Out are point-in-time and identical across YTD and T12M views — see Same Month table.)

Watch items (internal only): CUL same-month Total Sales -3.5%; HAR Loans Out -3.1%; LEX Service Charges -7.8% YTD / -2.9% T12M. Net Revenue formula per locked 2026-07-02 rule (In-Store Svc Charges + Sales Profit). Slack post used Total Sales / Scrap Cost labels (no retail/scrap sales split exists in EOM source).
