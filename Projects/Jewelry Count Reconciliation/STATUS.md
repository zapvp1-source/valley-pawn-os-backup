# Jewelry Count Reconciliation — STATUS

> ## ▶ NEXT SESSION — READ THIS FIRST (one job, ~2 minutes)
>
> **Everything is built. The ONLY thing left is registering the scheduled task.**
>
> Register a Cowork scheduled task with these exact settings:
>
> - **id / name:** `jewelry-count-reconciliation`
> - **file:** `/Users/joshuadavis/Documents/Claude/Scheduled/jewelry-count-reconciliation/SKILL.md` (already written)
> - **cron:** `0 9 * * *`  — 9:00 AM, **LOCAL ET** (this scheduler is local time, NOT UTC — verified:
>   `daily-funds-verification` is `0 18` and fires 6 PM ET)
> - **enabled:** true
> - **userSelectedFolders:** `/Users/joshuadavis/Documents/Claude/Projects/Jewelry Count Reconciliation`
> - **chromePermissionMode:** `follow_a_plan`
> - **chromeAllowedDomains:** `valleypawnworkspace.slack.com`, `app.slack.com`
>   (required — the EOD count sheets are photos; Slack's API cannot return image pixels)
> - **approvedPermissions:** Slack `slack_send_message` + `mcp__Control_your_Mac__osascript`
>
> **⚠️ This MUST be done from a session running ON JOSHUA'S COMPUTER**, using the
> `mcp__scheduled-tasks__*` tools. A cloud session does not have those tools. Do NOT try to
> hand-edit `~/Library/Application Support/Claude/.../scheduled-tasks.json` — that was attempted
> 2026-07-29, appeared to succeed and verified as present, then the running app silently reverted
> it within minutes. Same for toggling `enabled` on any existing task. The app owns that file.
>
> After registering, confirm it appears in the task list, then let the first 9:00 AM run be the
> end-to-end test — success looks like a Slack DM to Joshua.
>
> **Also pending (separate, Joshua asked for it):** disable `ffl-web-form-to-slack`. It runs
> `*/15 * * * *` and is responsible for 255 of the 580 usage-cap skips recorded 7/22–7/29,
> starving other tasks. Must also be done via the scheduled-tasks tools, not a file edit.


## 🔧 v2 FIXES — 2026-07-30 (after first live end-to-end run)

The first real run on 2026-07-29 data surfaced two defects. Both are fixed.

### Fix 1 — FALSE ZEROS (serious; was a silent all-clear)

`JewelryCountAudit.ahk`, if no grid row ever rendered, looked for the "Layouts"
caret and — finding it — declared the report a *"legitimate empty result"*,
returning `row_count: 0` with `status: success`. That caret is present whenever
the report editor is open, so **any** render failure was reported as a clean zero.

Observed live: HAR, LEX, ROA and WAY each sat exactly 180s then "succeeded" with
0 rows, while CUL rendered in 6s with 12 rows. Four identical timeouts reported as
four clean zeros. For a loss-prevention control this is the worst failure mode —
it reports an all-clear on a day it learned nothing.

**Fixed:** the empty-grid heuristic is gone. The handler now waits 90s, re-clicks
Ok and retries once, then throws. Zero rows is treated as FAILURE, never as data —
this report returns ALL sold items, so a store with zero rows across a full trading
day is effectively impossible. Backup: `reports/JewelryCountAudit.ahk.bak-pre-falsezero-fix-*`.

> ⚠️ **The same defect exists in `JewelrySoldMargin.ahk` and `AgedJewelrySales.ahk`**,
> which means **`discount-review` and `sold-review` can also silently report zeros.**
> Those are hardened files owned by other projects — NOT touched here (Rule #4).
> They should be fixed the same way by their owners. This is the highest-value
> follow-up in this document.

### Fix 2 — CATEGORY MISMATCH (would have caused phantom flags)

v1 compared Bravo's full ~90-category jewelry list against a paper sheet that only
counts **five buckets**: Rings, Bracelets, Necklaces, Earrings, Pendants. Culpeper
sold a gold bracelet *and* a TAG Heuer wristwatch on 7/29 — v1 would have counted 2
against a case that dropped by 1, a phantom flag. The watch was never in the counted
case.

**Fixed:** `bucket_for()` maps each Bravo category into one of the five buckets and
excludes watches, scrap, bullion, brooches and loose stones. Comparison is now
**per bucket** as well as total (bucket tolerance 3, total tolerance 5) — a sharper
signal, since a total can self-cancel.

A first pass using plain substring matching put a **STIHL CHAINSAW into Necklaces**
("Chainsaw" contains "chain"). So bucketing is now **gated on the known jewelry
category set first** — non-jewelry categories are never considered. 19 regression
cases pass, including Chainsaw, Miter Saw, charm bracelets, wedding bands, scrap,
bullion and wristwatches.

### Verified result — CUL, 2026-07-29

Bravo: 1 gold bracelet sold (TAG Heuer watch correctly excluded).
Sheet: bracelets 119 → 118, every other bucket unchanged. **diff 0, no flags.**
Exact match at bucket level, not just total.

### Live-run findings

- **Only Culpeper posted EOD paperwork for 7/29.** HAR, LEX, ROA, WAY posted nothing.
- 4 of 5 stores produced no usable Bravo data that run (the false-zero defect above).
- New posters seen in #end-of-day not yet in `STORE_POSTER_MAP`: **Bree**, **Martin D.**,
  **Preston Peters**. Confirm from a sheet header before scoring those days.

### Deployment state

The AHK fix is on disk but **the watcher must restart to load it** (`#Include` is
compile-time). Deliberately NOT restarted at 22:30 on 7/30 — a failed restart leaves
the watcher dead and breaks every morning Bravo task, and this fix only affects the
`jewelry-count-audit` cell. The watcher restarts each morning (~08:13 observed
2026-07-30), well before the 9:00 AM run.

**Watcher restart, when needed — now a solved problem:** `prlctl` IS reachable from
the Mac shell via `mcp__Control_your_Mac__osascript` (`/usr/local/bin/prlctl`), VM
UUID `{7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}`. Note `prlctl exec` runs in a session
where **Y: is not mapped**, so `restart_watcher.bat` fails with "cannot find the
drive specified". Use `_restart_watcher.ps1` instead — it registers a Windows
scheduled task as user `joshuadavis` (Interactive) to map Y: and launch AHK in the
interactive session. Do not launch the watcher from a UNC path: UNC over Parallels
shared folders is ~30x slower and every cell times out.

---

**Last updated:** 2026-07-30
**Purpose:** catch unaccounted jewelry shrinkage daily, by comparing what Bravo says each store
SOLD yesterday against how much the jewelry case physically shrank per the manager's handwritten
AM/PM count sheet photographed into Slack `#end-of-day`.

---

## Current state: BUILT — one manual step left to go live

| Piece | State |
|---|---|
| Bravo data source | ✅ Done — reuses `discount-review`'s existing daily pull (no new pull) |
| Jewelry category list | ✅ Done — `jewelry_reconciliation_comparison.py` |
| Store ↔ poster map | ✅ Done — all 5 confirmed |
| Reconciliation logic | ✅ Done + tested on live data |
| Scheduled task file | ✅ Written — `~/Documents/Claude/Scheduled/jewelry-count-reconciliation/SKILL.md` |
| **Registered in scheduler** | ❌ **NOT YET — needs to be added via the Cowork desktop app** |

**To go live:** in the Cowork desktop app, add a scheduled task pointing at
`~/Documents/Claude/Scheduled/jewelry-count-reconciliation/SKILL.md`, daily **9:00 AM**, and grant
it Chrome access to `app.slack.com` + `valleypawnworkspace.slack.com` plus the
`Jewelry Count Reconciliation` project folder. (Writing the registry entry by hand into the app's
own `scheduled-tasks.json` was deliberately not done — the app owns that file while running and a
hand edit risks clobbering all 140 task definitions.)

---

## How it works

1. **9:00 AM ET daily.** Runs 45 min after `discount-review` (8:15 AM), which already pulls
   yesterday's "Claude Sold Inv Details" for all 5 stores.
2. **Reads** `output/<YDAY>_to_<YDAY>_<STORE>_jewelry-margin-sold.csv` — no Bravo pull.
3. **Counts** jewelry rows by `Category` against the canonical jewelry list.
4. **Reads** each store's handwritten AM/PM count sheet from `#end-of-day` via Chrome vision.
5. **Flags** any store where `(AM − PM) − Bravo_sold` exceeds ±5 pieces, or where the sheet's
   handwritten date ≠ yesterday.
6. **DMs Joshua only** (`D03BHQH5VGT`). Never a shared channel — this is a loss-prevention audit.
7. **Appends** to `history.csv` so a store that's quietly off by 4 *every day* becomes visible.

### Store ↔ poster map (confirmed 2026-07-29 from each sheet's printed header)

| Poster | Store |
|---|---|
| Benjie Moore | ROA — Roanoke |
| Walker Tapley | HAR — Harrisonburg |
| Uriah | LEX — Lexington |
| Chadd | WAY — Waynesboro |
| Sandi Cole | CUL — Culpeper |

---

## Findings that shaped the design

**1. The EOD sheet is not a sales record — it's a physical headcount.**
It records jewelry in the case at open (AM) and close (PM), by category (Rings, Bracelets,
Necklaces, Earrings, Pendants). So `AM − PM` = pieces sold MINUS pieces bought that day. Bravo's
number is sold-only. **Known v1 limitation:** on a heavy buy day the case shrinks less than sales
alone predict, which can throw a flag that isn't shrinkage. A flag means "worth a look," not
"theft," and the DM must say it that way. **v2:** add a Bravo pieces-bought pull to net this out.

**2. Slack's API cannot read the count sheets.** They're photographs of paper. Every Slack MCP tool
returns file metadata only, never image pixels, and there is no file-download tool on the
connector. Chrome vision is the only path — and it's a proven pattern here:
`weekly-returns-summary` and `dismiss-employee` are both live scheduled tasks with Slack in their
allowed Chrome domains.

**3. The sheet's handwritten date can differ from the Slack post date.** Confirmed live: a sheet
dated 7/26 was posted 7/28. Always capture both; flag the mismatch, never assume.

**4. The Bravo pull was redundant.** A `jewelry-count-audit` handler + pipeline cell was built and
proven live across all 5 stores on 2026-07-29 — then found to produce output **byte-for-byte
identical** to what `discount-review` already writes each morning (verified by diff on all five
2026-07-28 files). It is retained as the Step 2b fallback for days `discount-review` is skipped or
fails, but is not used routinely. Nothing existing was modified (Rule #4).

---

## Live verification, 2026-07-28 data

Jewelry pieces sold, pulled and counted end-to-end:

| Store | Pieces |
|---|---|
| CUL | 7 |
| HAR | 0 |
| LEX | 0 |
| ROA | 0 |
| WAY | 0 |

CUL's 7: 3× Lady's Silver & Stone Ring, 1× Silver-Stone Pendant, 1× Silver Pendant,
1× Silver Bracelet, 1× Lady's Stone & Diamond Ring.

---

## Process lessons — read this before extending anything here

**The Valley Pawn scheduler is the Cowork desktop one.** 140 tasks live in
`~/Documents/Claude/Scheduled/<id>/SKILL.md`, registered in the desktop app's
`scheduled-tasks.json`. Each entry carries its own `cronExpression`, `userSelectedFolders`, and
`chromeAllowedDomains` — that last one is how a scheduled task gets browser access.

- **`cronExpression` in this scheduler is LOCAL (ET), not UTC.** Verified: `daily-funds-verification`
  is `0 18 * * *` and fires at 22:00 UTC. Do not convert to UTC.
- **The cloud/remote trigger tools are a DIFFERENT scheduler.** A task created there fires in a
  locked-down sandbox with no folder grants and no Chrome, and silently does nothing useful. One
  was created here on 2026-07-29, never touched Bravo across two test fires, and has been disabled.
  Do not use those tools to schedule Valley Pawn work.
- **Inventory the 140 existing tasks BEFORE building.** 53 of them are Bravo-related and ~30 are
  enabled; most drop trigger files and read output CSVs exactly the way new work needs to. Nearly
  every "blocker" hit while building this turned out to be an already-solved pattern sitting in
  that folder. That's what `enterprise-map` step 3 is for.

## Separate issue worth attention (not jewelry)

31 of the 140 scheduled tasks recorded **580 skipped runs between 2026-07-22 and 2026-07-29** — all
`global_limit` / `per_task_limit`, i.e. usage caps rather than errors. `ffl-web-form-to-slack`
accounts for 255 of them (it runs every 15 min and re-retries each minute when throttled).
Casualties include `daily-clockin-check`, `weekly-store-kpis`, and three canvas refreshes. Worth
fixing on its own terms.

---

## Files

- `jewelry_reconciliation_comparison.py` — category list, `count_jewelry_sold()`, `reconcile()`,
  `STORE_POSTER_MAP`, DM formatter. Single source of truth for the logic.
- `history.csv` — created on first run; daily per-store trend line.
- `~/Documents/Claude/Scheduled/jewelry-count-reconciliation/SKILL.md` — the task itself.


## RUN RECORD - 2026-07-30 reconciliation (executed 2026-07-31)
Bravo pull: jewelry-count-recon-2026-07-30c, all 5 stores success (after clearing the
Scrap-Bucket Question-dialog wedge; see BRAVO_KNOWN_ISSUES.md READ-FIRST INDEX).
Sheets: all 5 posted 7/30 evening, all dated 7/30 (no date mismatch), all AM/PM totals
sum-verified. New posters confirmed by sheet header: Bree (Grayson) = CUL, Martin D. (Dowden) = WAY.

| Store | Bravo sold (bucketed) | AM | PM | Net | Diff | Result |
|-------|----------------------|------|------|-----|------|--------|
| CUL | 2 (1 Ring, 1 Pendant) | 1236 | 1234 | 2 | 0 | OK |
| HAR | 1 (1 Necklace) | 802 | 807 | -5 | -6 | FLAG (case grew; sheet tick-marks show ~6 intraday adds - consistent with buys backfilling, known v1 limitation) |
| LEX | 0 | 432 | 432 | 0 | 0 | OK |
| ROA | 0 (29 sold rows, none case jewelry) | 1060 | 1060 | 0 | 0 | OK |
| WAY | 0 | 549 | 545 | 4 | +4 | OK within tolerance, but note: 4 rings left the case with zero jewelry sales recorded (manager annotated -4 in blue). Plausibly moved to the AUGUST 2026 GOLD SCRAP bucket. Worth a glance. |

Tolerance +/-5 per board decision 2026-07-27.

## RUN RECORD - 2026-08-02 reconciliation (executed 2026-08-02, ~7:45 PM run)
FAILED — no reconciliation computed. Both required inputs were unavailable:
- Bravo pull: jewelry-count-recon-2026-08-02-auto (7:48-8:13 PM) then retry
  jewelry-count-recon-2026-08-02-auto-b (8:13-8:42 PM) per failure protocol
  (retry once, fresh id). ALL 5 stores (CUL, HAR, LEX, ROA, WAY) failed on
  BOTH passes with the same symptom: JewelryCountAudit.ahk step 6b
  "waiting for DataItem rows to render" times out at 90s, re-click Ok fails
  with "ClickByName: element not found: Ok", handler correctly refuses to
  report a false zero, recovers cleanly to Dashboard (BackToDashboard/Done
  worked every time - no wedge), and throws "Grid never rendered after 2
  attempts (~3 min)". CUL's retry additionally failed one step earlier -
  could not select 'Claude Sold Inv Details' from the saved-report dropdown
  after 3 strategies (type-ahead, keyboard walk, page-by-page), Esc/retry x3.
  Identical failure across all 5 stores on both attempts = this is a live
  Bravo-side report-rendering issue tonight (client, server, or report
  definition), not store-specific flakiness or a fixable automation bug.
  No CSVs produced for 2026-08-02. New finding logged to
  BRAVO_KNOWN_ISSUES.md READ-FIRST INDEX (additive).
- Count sheets: as of 8:43 PM ET check (after waiting through the full ~55min
  Bravo retry cycle), no store had posted a jewelry count photo for 8/2 in
  #end-of-day. Newest post in the channel was Martin D. (WAY), 1 day old,
  filename timestamp 20260801_185050.jpg. No usable sheet data for any store.
- Posted failure honestly to #jewlery-counts (C0BM9NHGTT4) per failure
  protocol. Did not fabricate a per-store table with no data.
- Next run (2026-08-03) should re-check whether this was a one-night Bravo
  outage or persists; if it recurs identically, escalate as a genuine Bravo
  regression rather than retrying again.


## RUN RECORD - 2026-08-01 (Saturday) reconciliation - BACKFILL, executed 2026-08-03
Never ran on the day: the scheduled task went live 8/2. Bravo pull
jewelry-count-recon-2026-08-01-verify, all 5 stores success (23/35/21/28/40 sold rows).
This pull doubled as proof that the 8/2 "failure" was a closed-Sunday artifact, not a defect.
All 5 sheets posted, dated 8/1, all AM and PM columns sum-verified.

| Store | Sold | AM | PM | Net | Diff | Result |
|-------|------|------|------|-----|------|--------|
| CUL | 7 | 1260 | 1271 | -11 | -18 | FLAG - case GREW 11; rings 613->624 vs 6 sold, ~18 pieces in. Heavy Saturday buy day; check buy tickets. |
| HAR | 3 | 813 | 790 | 23 | +20 | FLAG but EXPLAINED - sheet annotated "Scrap": -16 rings, -1 bracelet, -3 necklaces, -3 pendants = 23, exactly the drop. Process working as designed. |
| LEX | 2 | 427 | 426 | 1 | -1 | OK |
| ROA | 2 | 1055 | 1010 | 45 | +43 | FLAG - UNEXPLAINED. 46 rings + 6 bracelets left the case vs 2 sales. Same shape as HAR's scrap pull but undocumented. Ask Benjie. NOTE: AM column sums to 1056, written total says 1055. |
| WAY | 4 | 542 | 538 | 4 | 0 | PERFECT - exact at category level (2 rings, 1 earring, 1 pendant). |

Tolerance +/-5. New poster confirmed by sheet header: Preston Peters posted HAR on 8/1.
Posted to #jewlery-counts 2026-08-03.

LESSON: HAR vs ROA is the template for reading these. Both had a large undocumented-looking
drop; HAR annotated the scrap pull on the sheet and is instantly explainable, ROA did not.
Encouraging managers to annotate scrap/transfer pulls on the count sheet turns a flag into a
non-event. Worth making that a documented expectation.

## RUN RECORD - 2026-08-03 (Monday) - full 5-store protocol, DM-only (no channel post)

Store-hours gate: Monday, all 5 stores open, full protocol run.

Bravo pull jewelry-count-recon-2026-08-03-auto: all 5 stores SUCCESS (CUL 32 / HAR 6 / LEX 10 / ROA 11 / WAY 32 sold rows, ~11 min total).

Bucketed jewelry-only sold (JEWELRY_CATEGORIES gate applied):
| Store | Sold (bucket) | Sheet status |
|-------|----|------|
| CUL | 6 (Rings 4, Necklaces 2) | Sheet posted by Sandi 6:27 PM but dated 8/2/26, NOT 8/3 - date mismatch, could not reconcile today's sale total against it. |
| HAR | 2 (Necklaces 2) | NO sheet posted in #end-of-day as of 8:17 PM after a full 30-min wait past the normal 6:00-7:15 PM window. |
| LEX | 0 | NO sheet posted, same as HAR. |
| ROA | 0 | Benjie Moore posted 6:36 PM, dated 8/3/26 correctly. AM 1010 / PM 1010, net 0, diff 0. MATCH. |
| WAY | 2 (Rings 1, Earrings 1) | Preston Peters posted 7:27 PM (header says WAYNESBORO despite Preston normally posting HAR - used header per protocol). AM 538 / PM 536, net 2, diff 0. MATCH. |

3 of 5 stores (CUL, HAR, LEX) had an incomplete count-sheet read (date mismatch or not posted) even after the one-time 30-min wait. Per the rewritten Field Communication Standard v3 Section 5 (2026-08-03), an incomplete count-sheet read for ANY store being checked means: post NOTHING to #jewlery-counts, DM Joshua one plain line only. Did that (DM sent 8:17 PM to D03BHQH5VGT, corrected a stray trailing character with an edit at 8:18 PM).

ROA and WAY, the two stores that did reconcile, both matched exactly (diff 0) - no shrinkage concern on the data actually available.

Follow-up for next session: check whether HAR/LEX are chronically late posters and whether Sandi's CUL sheet needs a reminder to post same-day (this is the second time CUL's photo has trailed the business date - see 8/1 backfill note above about Sandi being replaced by Bree/Bree Grayson as poster; Sandi may be posting stale/leftover photos).

## RUN 2026-08-04 (Tue) - COMPLETE, ALL CLEAN, POSTED
- Store-hours gate: Tuesday = all 5 stores open. Full 5-store protocol run.
- Bravo trigger: jewelry-count-recon-2026-08-04-auto. Overall status SUCCESS, 5/5 cells success,
  no retry needed. Row counts (ALL sold items, not jewelry): CUL 23, HAR 16, LEX 11, ROA 17, WAY 20.
  No empty grids. Durations ~108-116s per cell; full cycle 19:50-19:58 ET.
- Count sheets: all 5 posted to #end-of-day before the run, all dated 8/4/26 (no date mismatch).
- POSTER MAP DRIFT (identify store by the sheet header, NOT the poster - this run proves why):
  Preston Peters -> WAYNESBORO   (map says Martin=WAY)
  Martin D.      -> LEXINGTON    (map says Martin=WAY, Uriah=LEX)
  Benjie Moore   -> ROANOKE      (matches map)
  Walker Tapley  -> HARRISONBURG (matches map)
  Sandi Cole     -> CULPEPER     (matches historic map)
  Uriah did not post today. All stores identified off the END OF DAY: <STORE> header.
- Sum-verify: every AM and PM column re-added against its written total.
  CUL AM 620/121/147/125/253=1266 OK; PM 618/121/147/125/253=1264 OK.
  HAR AM 452/49/124/50/115=790 OK;  PM 451/49/124/50/116=790 OK.
  LEX AM 258/32/45/43/48=426 OK;    PM same =426 OK.
      (AM Bracelets glyph reads 38 or 32; the column sum forces 32 - recorded as 32.)
  ROA AM 529/167/151/77/146=1070;   PM 528/167/151/77/146=1069.
      Manager WRITTEN totals read 1010 / 1009 - third digit ambiguous, both understated by the
      same amount. Net is identical either way (1), so the reconciliation is unaffected.
      Recorded the computed column sums.
  WAY AM 326/40/64/48/58=536 OK;    PM same =536 OK.
- Results (bucketed per jewelry_reconciliation_comparison.py; flag when |diff| > 5):
  STORE | soldJ | AM   | PM   | net | diff | status
  CUL   |   1   | 1266 | 1264 |  2  |  +1  | ok
  HAR   |   1   |  790 |  790 |  0  |  -1  | ok
  LEX   |   0   |  426 |  426 |  0  |   0  | ok
  ROA   |   0   | 1070 | 1069 |  1  |  +1  | ok
  WAY   |   0   |  536 |  536 |  0  |   0  | ok
- Bucket-level deltas: CUL +1 Rings, ROA +1 Rings, HAR -1 Pendants. All inside BUCKET_TOLERANCE (3).
  HAR -1 Pendants matches the manager own +1 Pendants adjustment written on the sheet - self-consistent.
- Excluded (real jewelry, deliberately not on the counted sheet): WAY 1x Gent Wristwatch
  (CITIZEN ECO-DRIVE WATCH). Correctly ignored by the bucketer - lives in the watch case, not the
  counted case. This is exactly the v2 phantom-flag case the bucketing exists to prevent.
- FLAGS: none. No date mismatch, no missing sheet, no empty grid, no pipeline failure.
- Posted the clean per-store summary to #jewlery-counts (C0BM9NHGTT4) at 20:00 ET in the
  plain-language format required by FIELD COMMUNICATION STANDARD v3. No DM to Joshua (no failure).

## 2026-08-05 (Wednesday) - run COMPLETE, posted to #jewlery-counts

FIRST LIVE WEDNESDAY TEST of the store-hours gate (added 2026-08-03). Gate worked as
designed: weekday resolved to Wednesday in America/New_York -> stores array = CUL only.
HAR/LEX/ROA/WAY were NOT pulled and NOT read. No false alarm. This closes the
AWAITING-first-live-Wednesday (2026-08-05) item in the BRAVO_KNOWN_ISSUES.md OPEN section.
(Sunday 2026-08-09 skip still awaiting its own first live verification.)

Bravo pull: trigger jewelry-count-recon-2026-08-05-auto.json written 19:48 ET, claimed and
completed on the FIRST attempt, no retry needed.
  - result: status=success, 1 cell, 0 errors
  - CUL jewelry-count-audit 2026-08-05 -> 33 rows, 130,985 ms
  - CSV: output/2026-08-05_to_2026-08-05_CUL_jewelry-count-audit.csv
  - grid walker logged captured-all-33-rows (truncation guard clean)

Count sheet: Sandi Cole posted to #end-of-day at 18:13:29 ET (3 files, IMG_5808/5809/5810).
Store identified from the EOD summary header END OF DAY: CULPEPER - matches the historic
Sandi-Cole=CUL poster map. Sheet date read as 8/5/26 = business date, no date mismatch.
Jewelry block read from IMG_5810.

  AM COUNT: Rings 619, Bracelets 121, Necklaces 147, Earrings 125, Pendants 253
            written total 1265 - SUM-VERIFIED (619+121+147+125+253 = 1265) OK
  PM COUNT: Rings 626, Bracelets 122, Necklaces 149, Earrings 125, Pendants 253
            written total 1275 - SUM-VERIFIED (626+122+149+125+253 = 1275) OK
            (PM Bracelets figure is written over a correction; the column total
             independently confirms 122, not 128.)

Compute: none of the 33 sold rows fall in JEWELRY_CATEGORIES - the CUL sold list was
entirely tools, firearms/ammo, coins, records, a guitar and a PSP. sold = 0 every bucket.

  net  = AM_total - PM_total = 1265 - 1275 = -10
  sold = 0
  diff = net - sold = -10   ->  abs(diff) = 10 > 5  ->  FLAGGED

Per-category movement (AM -> PM): Rings +7, Bracelets +1, Necklaces +2, Earrings 0,
Pendants 0. Case count went UP 10 pieces on a day with zero jewelry sales, which is the
signature of new intake being placed into the cases during the day rather than a shrink
event. Reported to the channel as worth-a-quick-confirm-with-the-manager per the Field
Communication Standard (plain language, no system names, no dollar figures, no breakdown).

Posted to #jewlery-counts (C0BM9NHGTT4) at 19:52 ET, ts 1785973956.447489, including the
required Wednesday footer line. No failure path taken; no DM sent to Joshua.

## Run: 2026-08-06 (Thursday, full 5-store day)

- Store-hours gate: Thursday -> all 5 stores open (CUL, HAR, WAY, LEX, ROA). Correct branch taken.
- Trigger 1: jewelry-count-recon-2026-08-06-auto (submitted 19:48:40 -0400) -> status "aborted", all 5 cells "skipped", error on every store: "Skipped by safety rail: bravo-not-ready (could not reach a logged-in dashboard)".
- Retry (per protocol, ONE retry with fresh id): jewelry-count-recon-2026-08-06-auto-b (submitted 19:56:41 -0400) -> same result, all 5 cells skipped, same bravo-not-ready error. Bravo/Parallels dashboard was not in a logged-in state for either attempt.
- Per Section 5 failure path: posted NOTHING to #jewlery-counts. Sent Joshua one plain-language DM in D03BHQH5VGT: "Jewelry count check for 2026-08-06 didn't complete - needs a look."
- Count-sheet (vision) side was completed successfully for all 5 stores before the Bravo failure was discovered - captured here so the numbers aren't lost, but NOT posted anywhere since Bravo-side sold-jewelry data never generated (nothing to reconcile against):
  - CUL (Bree Grayson, header confirmed CULPEPER): AM Rings619/Bracelets121/Necklaces147/Earrings125/Pendants253/Total1265; PM Rings626/Bracelets122/Necklaces149/Earrings125/Pendants253/Total1275. Net(AM-PM) = -10.
  - HAR (Walker Tapley, header confirmed HARRISONBURG): AM Rings451/Bracelets49/Necklaces124/Earrings50/Pendants116/Total790; PM Rings451/Bracelets49/Necklaces124/Earrings49/Pendants114/Total~787. Net = +3. (Sheet was photographed sideways/rotated - read via zoom, moderate confidence.)
  - WAY (Preston Peters, header confirmed WAYNESBORO, posted late at 19:52): AM Rings326/Bracelets40/Necklaces64/Earrings48/Pendants58/Total536; PM Rings326/Bracelets40/Necklaces64/Earrings46/Pendants57/Total532. Net = +4. High confidence, clean sheet.
  - LEX (Martin D., header confirmed LEXINGTON - note: Martin posts for LEX, not WAY as the old poster map assumed; header rule caught this correctly): AM Rings258/Bracelets32/Necklaces45/Earrings43/Pendants48/Total426; PM same values, Total426. Net = 0.
  - ROA (Benjie Moore, header confirmed ROANOKE): AM Rings528/Bracelets107/Necklaces157/Earrings77/Pendants146/Total~1010-1015 (sum vs written total off by ~5); PM Rings534/Bracelets115/Necklaces153/Earrings79/Pendants146/Total~1027 (written total illegible/inconsistent, ~1609 or 1009 as written - likely a writing error, sum used instead). Net = ~-12 to -17. LOW CONFIDENCE - sheet was rotated 90 degrees and handwriting on totals row was ambiguous; would need a second look if Bravo comes back and this store shows as flagged.
- ACTION NEEDED next run/session: check why Bravo/Parallels was not logged in at ~19:50-19:59 ET. Once Bravo access is confirmed working, this date (2026-08-06) can be re-pulled and reconciled against the AM/PM counts captured above without needing to re-read the Slack photos.

## RUN 2026-08-07 (Friday) - COMPLETE, ALL CLEAN, POSTED
- Store-hours gate: Friday -> all 5 stores open. Full 5-store protocol run.
- Bravo trigger: jewelry-count-recon-2026-08-07-auto. Overall status SUCCESS, 5/5 cells success, no retry needed.
  Row counts (ALL sold items, not jewelry): CUL 25, HAR 4, LEX 8, ROA 19, WAY 33. No empty grids.
  Cycle ~19:48-20:01 ET, durations ~100-107s per cell.
- Count sheets: all 5 posted to #end-of-day. Store identified from EOD summary header, not poster.
  CUL: Sandi Cole (header CULPEPER). HAR: Walker Tapley (header HARRISONBURG). LEX: Martin D. (header LEXINGTON).
  ROA: Benjie Moore (header ROANOKE, sheet rotated 90deg as usual - read via zoom). WAY: Preston Peters (header WAYNESBORO).
- Sum-verify: CUL AM 626/122/149/125/253=1275 OK; PM 626/120/150/122/253=1271 OK (wrote as 127_, edge-cropped, computed 1271).
  HAR AM+PM 451/48/124/49/114=786 OK both. ROA AM+PM 534/115/153/79/149=1030 OK both (order corrected after re-zoom: R/Bra/Nec/Ear/Pen).
  LEX AM 257/32/45/42/47 -> computed sum 423, written total on sheet read as 426 (off by 3); PM same bucket values -> computed 423,
  written total read as 462. LOW CONFIDENCE on LEX's written totals digits; used computed column sums (423/423, net 0) per
  standing practice of trusting the sum over an ambiguous written total. Sold-jewelry for LEX was 0 anyway so this does not
  change the flag outcome either way.
  WAY: sheet contained two blocks - top block dated 8/6/26 exactly matches the already-recorded 2026-08-06 numbers (AM536/PM532,
  confirms that was yesterday's leftover data on the same physical sheet), bottom block (today, date partly obscured but
  positionally the current entry) AM=PM=326/40/64/46/57=532, net 0. Used the bottom block as 8/7's count.
- Results (bucketed per jewelry_reconciliation_comparison.py; flag when |diff| > 5 or bucket diff > 3):
  STORE | soldJ | AM   | PM   | net | diff | status
  CUL   |   5   | 1275 | 1271 |  4  |  -1  | ok   (sold: Earrings 4, Necklaces 1)
  HAR   |   0   |  786 |  786 |  0  |   0  | ok
  LEX   |   0   |  423 |  423 |  0  |   0  | ok
  ROA   |   0   | 1030 | 1030 |  0  |   0  | ok   (1x Pocket Watch sold, correctly excluded - not on counted sheet)
  WAY   |   0   |  532 |  532 |  0  |   0  | ok
- Bucket-level deltas (CUL only, others net 0 across the board): Bracelets AM122/PM120 (+2, sold0, diff+2); Necklaces AM149/PM150
  (-1, sold1, diff-2); Earrings AM125/PM122 (+3, sold4, diff-1). All inside BUCKET_TOLERANCE (3).
- Excluded (real jewelry, deliberately not on the counted sheet): ROA 1x Hamilton Pocket Watch. WAY had 1x Apple Watch (Smart Watch
  category) sold but Smart Watch is not in the JEWELRY_CATEGORIES gate at all (only Gent's/Lady's/Unisex Wristwatch, Pocket Watch,
  Watch Band are) so it was excluded before even reaching the ignored-list step - correct behavior, watches live in a separate case.
- FLAGS: none. No date mismatch on the business-date field itself (all EOD summary headers dated 8/7/26), no missing sheet, no
  empty grid, no pipeline failure.
- Posted the clean per-store summary to #jewlery-counts (C0BM9NHGTT4) at ts 1786147319.375499 in the plain-language format
  required by FIELD COMMUNICATION STANDARD v3. No DM to Joshua (no failure).
- FOLLOW-UP for next session: LEX's written column totals (426/462) did not match the column sums (423/423) on this sheet -
  worth a reminder to Martin D. to re-add before writing the total, though it did not affect today's reconciliation outcome.


## 2026-08-09 — BREAKTHROUGH: count-only pull. On-hand reconciliation is UNBLOCKED.

**Root cause of the 3-day stall was a wrong approach, not a broken tool.**
`JewelryCaseAudit.ahk` (08-06) exported every on-hand ROW and counted them. That runs
straight into the DevExpress virtualiser paging bug (BRAVO_KNOWN_ISSUES.md, STILL OPEN):
on grids >~270 rows the walker stops yielding non-deterministically. The 08-06 WAY probe
hung at 22 of 327 Rings for exactly this reason.

But that same probe log proved Bravo HANDED US THE ANSWER before the walk began. Every
grid row carries an accessibility Name `"Row N of TOTAL, ..."` and TOTAL is the full
on-hand count, readable from the FIRST rendered page. We were exporting 327 rows of ring
detail to arrive at a number Bravo stated in 11 seconds.

**NEW: `reports/JewelryCaseCount.ahk`, cell `jewelry-case-counts`** (additive; Rule #4).
Reads TOTAL off the first page, never walks the grid, so the paging bug cannot affect it
at any inventory size. ONE store visit runs all 5 categories (the store switch was the
expensive step). Writes a 5-row CSV: `store,category,as_of,count,status`.
Same technique already proven in production by ItemsToPrice.ahk (header-counter read).
No false zeros: a category that renders nothing is retried once then recorded as ERROR,
never as 0.

### FIRST LIVE RUN — WAY, 2026-08-09 — 5/5 SUCCESS, 324s total
| Category | Bravo on-hand (8/9) | Manager sheet AM (8/4) | Delta |
|---|---|---|---|
| Rings | 329 | 326 | +3 |
| Pendants | 59 | 58 | +1 |
| Earrings | 47 | 48 | -1 |
| Chains 41 + Necklaces 22 | **63** | 64 | **-1** |
| Bracelets | **NO SAVED REPORT** | 40 | — |
| Total (ex-bracelets) | 498 | 496 | +2 |

### TWO OPEN QUESTIONS — BOTH NOW ANSWERED EMPIRICALLY
1. **Is the `Location` column needed to scope to case-only stock?** NO. The saved reports
   are already case-scoped. Every category lands within 1-3 of a manager sheet taken 5 days
   earlier (normal daily drift from sales/buys). If safe/layaway/repair stock were bleeding
   in, totals would be wildly high, not within 1%. The Location question is MOOT — close it.
2. **Do Chains + Necklaces sum to the sheet's single Necklaces line?** YES. 41+22=63 vs
   sheet 64. Confirmed exactly as Joshua predicted 2026-08-06.

### THE ONE REMAINING GAP — needs Joshua (2 minutes in Bravo)
**There is no "Claude Jewelry Audit - Bracelets" saved report.** The manager sheet counts
five buckets; Bravo currently gives us four of them (with neck-worn split across two
reports). Until a Bracelets report exists, WAY's ~40 bracelets are invisible and the TOTAL
line cannot be reconciled — only the four covered buckets can.
Action: create it in Bravo exactly like the other five, then add "Bracelets" to
`JEWELRY_CASE_COUNT_REPORTS` in reports/JewelryCaseCount.ahk. One-line change.

### NEXT
- Add Bracelets report -> rerun WAY -> reconcile all 5 buckets + total against a same-day sheet.
- Roll out to all 5 stores (one trigger, stores array).
- Point the `jewelry-count-reconciliation` scheduled task at on-hand counts instead of the
  sold-based flow comparison. The sold-based version STAYS LIVE and untouched until the
  on-hand version is backtested clean (Rule #4).

## 2026-08-10 — Monday, full 5-store run, all stores open
- Bravo pull: trigger jewelry-count-recon-2026-08-10-auto, all 5 cells SUCCESS (CUL 11 rows/105s, HAR 25 rows/103s, LEX 13 rows/101s, ROA 3 rows/96s, WAY 18 rows/99s). No BOM issue, no truncation-guard errors.
- Count sheets: read via Chrome from #end-of-day. All 5 managers posted between 6:16-6:31 PM ET. Poster/store map held (Sandi=CUL, Walker=HAR, Uriah=LEX, Martin D.=WAY, Benjie=ROA), confirmed against each EOD summary sheet header. All sheets dated 8/10/26 (CUL, ROA single-block; HAR, LEX, WAY multi-block sheets, used the 8/10/26-dated block).
- Bucketed per jewelry_reconciliation_comparison.py rules (JEWELRY_CATEGORIES gate, then bracelet/earring/ring/necklace-chain/pendant-charm mapping; scrap/bullion/wristwatch/pocket watch/watch band/brooch/misc + bare Diamond excluded).

STORE | soldJ | AM   | PM   | net | diff | status
CUL   |   1   | 1261 | 1279 | -18 |  -19 | FLAG (sold: Bracelets 1 - VP4027719 Silver Bracelet S925 1.9DWT)
HAR   |   4   |  782 |  779 |   3 |   -1 | ok   (sold: Rings 3 - VA5019289 Diamond Cluster Ring, VA5019865 + VA5019869 Silver-Diamond Rings; Pendants 1 - VA5014379 Gold Pendant)
LEX   |   0   |  423 |  423 |   0 |    0 | ok
ROA   |   0   | 1026 | 1033 |  -7 |   -7 | FLAG (written PM total read as 1042; column sum computed as 1033 - used computed sum per standing practice, see note below)
WAY   |   2   |  531 |  529 |   2 |    0 | ok   (sold: Rings 1 - VAP030380 Lady's Silver Ring; Pendants 1 - VAP031101 Silver Pendant)

- Bucket-level detail:
  CUL: Rings AM625/PM637 (+12 net increase, no rings sold - largest driver of the flag); Bracelets AM118/PM120 (-2, sold1, diff-3, borderline ok); Necklaces AM151/PM154 (-3, sold0, borderline ok); Earrings AM122/PM123 (-1, ok); Pendants AM245/PM245 (0, ok).
  ROA: Rings AM531/PM541 (-10, sold0 - largest driver); Bracelets AM116/PM114 (+2, ok); Necklaces AM153/PM157 (-4, sold0, borderline); Earrings AM78/PM76 (+2, ok); Pendants AM148/PM145 (+3, ok). ROA sold zero jewelry-category items this run (PlayStation 4, Film Camera, Battery Charger only).
- ROA written-total mismatch: PM column digits read as Rings 541/Bracelets 114/Necklaces 157/Earrings 76/Pendants 145, summing to 1033. The sheet's written PM TOTALS line reads 1042 (off by 9 from the column sum). Re-zoomed twice to confirm digits; used the computed column sum (1033) as per standing practice (see 2026-08-07 LEX entry). Did not affect the FLAG outcome (already flagged either way). Worth a reminder to Benjie to re-add before writing the total.
- CUL and ROA both show a NET INCREASE in on-hand case count with a Rings-heavy pattern and no rings sold - consistent with new intake/buys added to the Rings case during the day rather than a miscount, but not confirmed. Flagged to the channel in plain language; no dollar or breakdown detail posted (Field Communication Standard v3).
- No date mismatches, no missing sheets, no empty-grid pipeline failures.
- Posted clean/flagged per-store summary to #jewlery-counts (C0BM9NHGTT4) at ts 1786406431.580749. No DM to Joshua (pipeline did not fail - two stores are OVER threshold on the count delta, which is a normal operational flag, not a pipeline failure, so channel post was used per Section 5).


## 2026-08-11 — Tuesday, on-hand comparison — DID NOT RUN (pipeline gap)
- jewelry-onhand-nightly-pull (8:30 PM trigger) did not produce output. No 2026-08-11_*_jewelry-case-counts.csv exists for any of the 5 stores as of 9:48 PM check.
- Other 8/11 pipeline cells DID run normally same day (items-to-price at ~8 AM, safe-register-journal at ~6:11-6:16 PM) — so this looks like an isolated failure of the jewelry-case-counts cell/trigger specifically, not a broader pipeline outage.
- Most recent jewelry-case-counts files on disk are dated 2026-08-10 (CUL 10:32 AM, HAR 9:55 AM, LEX 10:02 AM, ROA 10:10 AM, WAY prior WAY file from 8/9 13:27) — these are stale, not from a freeze window, and were not used.
- Per hard all-or-nothing rule: did NOT read Slack #end-of-day sheets, did NOT build any comparison table, did NOT publish any numbers.
- Sent Joshua one plain-language Slack DM (D03BHQH5VGT) noting tonight's comparison didn't complete. No technical detail in that DM.
- FOLLOW-UP NEEDED: someone should check why jewelry-onhand-nightly-pull didn't fire/complete tonight (trigger registration, Bravo pipeline handler, or timing conflict with the 8:30 PM window). Leaving diagnosis to a future session per additive-only rule — this run's job was analysis only, not pipeline repair.

## 2026-08-12 — Wednesday, Culpeper-only run
- Store-hours gate: Wed -> CUL only per section 0. No other stores checked (correct, not a failure).
- Bravo pull: trigger jewelry-count-recon-2026-08-12-auto, cell CUL SUCCESS, 20 rows, 111.2s. No BOM issue, no truncation-guard error.
- Count sheet: read via Chrome from #end-of-day. Sandi Cole (CUL) posted at 6:18 PM ET, dated 8/12/26 (matches business date). EOD summary header confirmed CULPEPER. Sum-verified: AM 637+120+155+122+243=1277 matches written AM total; PM 637+120+155+122+243=1277 matches written PM total.
- Bucketed per jewelry_reconciliation_comparison.py rules: only jewelry-category sold row was VP4028904 "Unisex Silver Ring" (RING S000 3.2DWT COSTUME JEWELRY) -> Rings bucket, sold=1. All other buckets sold=0.
STORE | soldJ | AM   | PM   | net | diff | status
CUL   |   1   | 1277 | 1277 |   0 |   -1 | ok
- Bucket detail: Rings AM637/PM637 (net0, sold1, diff-1); Bracelets AM120/PM120 (net0,sold0,diff0); Necklaces AM155/PM155 (net0,sold0,diff0); Earrings AM122/PM122 (net0,sold0,diff0); Pendants AM243/PM243 (net0,sold0,diff0). No date mismatch, no missing sheet, no empty-grid failure.
- Posted clean summary to #jewlery-counts (C0BM9NHGTT4). No DM to Joshua (pipeline succeeded, no flags).

## 2026-08-12 (night, 9:45 PM run) - Wednesday, Culpeper-only on-hand vs PM sheet - jewelry-onhand-nightly-compare
- Store-hours gate: Wednesday -> CUL only per Section 0 (correct, not partial; complete for the day).
- Bravo side: output/2026-08-12_CUL_jewelry-case-counts.csv, file mtime 8:43 PM (after the 8:30 PM freeze trigger, not stale). All 6 rows status=ok.
- Manager side: Sandi posted the CUL Jewelry Daily Count sheet to #end-of-day at 6:18 PM, handwritten date 8/12/26 (matches business date). Used PM COUNT column. Sheet total line (1277) matches the sum of its 5 categories (637+120+155+122+243=1277) - no misread.
- Category mapping: Chains(116) + Necklaces(100) = 216, compared against the sheet single NECKLACES line.
CUL comparison (OVER/SHORT from the sheet point of view; variance = sheet minus Bravo; Bravo = expected, sheet = actual case count):
  Rings      Bravo 648  Sheet 637  -> SHORT 11
  Bracelets  Bravo 127  Sheet 120  -> SHORT 7
  Necklaces  Bravo 216  Sheet 155  -> SHORT 61  (Chains 116 + Necklaces 100)
  Earrings   Bravo 173  Sheet 122  -> SHORT 51
  Pendants   Bravo 249  Sheet 243  -> SHORT 6
  Store total: Bravo 1413, Sheet 1277, SHORT 136 overall.
  Exact matches: 0 of 5 cells today (only CUL open on Wednesday).
- Direction: all 5 cells SHORT (Bravo higher than the physical case) - the expected scope-noise direction per BRAVO_KNOWN_ISSUES.md 2026-08-12 (Bravo counts case+safe+back-stock+bins; the manager sheet counts the display case only). No OVER (anomalous) cells tonight.
- Pattern check vs this morning freeze-window read (8/12 AM Bravo pull vs 8/11 PM sheet, logged in BRAVO_KNOWN_ISSUES.md): Necklaces +61 and Earrings +51 are identical to two nights ago read; Pendants +6 identical; Rings +11 vs +13 and Bracelets +7 vs +8 essentially unchanged. This is a stable, repeating pattern across two consecutive freeze-window comparisons, not a one-night miscount - it reinforces the existing scope-gap explanation rather than pointing to a new event. Per the standing caveat (no Location column on the saved jewelry reports yet, Claude Case Jewelry fix still open), none of tonight SHORT variance should be treated as loss.
- No date mismatch, no missing or stale files, no non-ok rows. Freeze window valid on both sides (store closed 6 PM, Bravo pulled 8:43 PM, sheet taken at 6:18 PM close).
- Reported to Joshua via Slack DM (D03BHQH5VGT) only - loss-prevention audit, never a shared channel or store manager. Message: https://valleypawnworkspace.slack.com/archives/D03BHQH5VGT/p1786585827927029

## 2026-08-13 (night, 9:45 PM run) - Thursday, all-5-store on-hand vs PM sheet - jewelry-onhand-nightly-compare
- Store-hours gate: Thursday -> all 5 stores open (CUL, HAR, LEX, ROA, WAY). Correct branch taken; complete.
- Bravo side: output/2026-08-13_{CUL,HAR,LEX,ROA,WAY}_jewelry-case-counts.csv, mtimes 20:51-21:17 (after 8:30 PM freeze trigger, not stale). All 30 rows status=ok.
- Manager side: read via Chrome from #end-of-day, all photographed sheets dated 8/13/26. Poster/store map confirmed from each sheet's own header: Sandi=CUL (6:17 PM), Walker Tapley=HAR (6:36 PM), Uriah=LEX (6:27 PM), Martin D.=WAY (6:31 PM), Benjie Moore=ROA (6:22 PM). Used PM COUNT column throughout. Every sheet's own TOTALS line sum-verified against its 5 categories before use (CUL 638+120+155+123+243=1279 OK; HAR 462+49+124+49+118=802 OK, ring digit recovered via total-minus-other-categories since it was scribbled/corrected on the sheet; LEX 272+37+45+49+51=454 OK; ROA 552+123+161+89+153=1078 OK, sheet rotated 90deg as usual, re-zoomed; WAY 324+40+64+46+55=529 OK). Category mapping: Chains+Necklaces summed vs Bravo, compared to sheet's single NECKLACES line.

Comparison (OVER/SHORT/MATCH from the sheet's point of view; variance = sheet minus Bravo; Bravo = expected/system, sheet = actual physical case count):

CUL   Rings     Bravo 649  Sheet 638  -> SHORT 11
CUL   Bracelets Bravo 127  Sheet 120  -> SHORT 7
CUL   Necklaces Bravo 215  Sheet 155  -> SHORT 60  (Chains 116 + Necklaces 99)
CUL   Earrings  Bravo 172  Sheet 123  -> SHORT 49
CUL   Pendants  Bravo 253  Sheet 243  -> SHORT 10
CUL store total: Bravo 1416, Sheet 1279, SHORT 137

HAR   Rings     Bravo 457  Sheet 462  -> OVER 5
HAR   Bracelets Bravo 50   Sheet 49   -> SHORT 1
HAR   Necklaces Bravo 128  Sheet 124  -> SHORT 4  (Chains 77 + Necklaces 51)
HAR   Earrings  Bravo 48   Sheet 49   -> OVER 1
HAR   Pendants  Bravo 117  Sheet 118  -> OVER 1
HAR store total: Bravo 800, Sheet 802, OVER 2

LEX   Rings     Bravo 268  Sheet 272  -> OVER 4
LEX   Bracelets Bravo 36   Sheet 37   -> OVER 1
LEX   Necklaces Bravo 44   Sheet 45   -> OVER 1  (Chains 26 + Necklaces 18)
LEX   Earrings  Bravo 51   Sheet 49   -> SHORT 2
LEX   Pendants  Bravo 52   Sheet 51   -> SHORT 1
LEX store total: Bravo 451, Sheet 454, OVER 3

ROA   Rings     Bravo 554  Sheet 552  -> SHORT 2
ROA   Bracelets Bravo 124  Sheet 123  -> SHORT 1
ROA   Necklaces Bravo 161  Sheet 161  -> MATCH  (Chains 98 + Necklaces 63)
ROA   Earrings  Bravo 94   Sheet 89   -> SHORT 5
ROA   Pendants  Bravo 92   Sheet 153  -> OVER 61  *** FLAG - anomalous direction ***
ROA store total: Bravo 1025, Sheet 1078, OVER 53 (driven entirely by Pendants)

WAY   Rings     Bravo 336  Sheet 324  -> SHORT 12
WAY   Bracelets Bravo 41   Sheet 40   -> SHORT 1
WAY   Necklaces Bravo 63   Sheet 64   -> OVER 1  (Chains 41 + Necklaces 22)
WAY   Earrings  Bravo 47   Sheet 46   -> SHORT 1
WAY   Pendants  Bravo 59   Sheet 55   -> SHORT 4
WAY store total: Bravo 546, Sheet 529, SHORT 17

Exact matches: 1 of 25 cells (ROA Necklaces). All other 24 cells non-zero - per zero-tolerance standard, none of those 24 called clean/close/within-tolerance; each is reported exactly as OVER/SHORT above.

ANALYSIS:
- ROA Pendants OVER 61 is the headline item tonight - the anomalous (system-lower-than-case) direction, sharpest attention per standing rule. This is consistent with the known, already-confirmed 2026-08-12 issue at Roanoke: pendant-type pieces entered in Bravo under Charms rather than Pendants, so the Pendants report undercounts what's physically in the case. Not new, but this is the first clean freeze-window read that quantifies it (61 pieces) - worth pushing the Bravo recategorization fix.
- CUL Necklaces SHORT 60 and Earrings SHORT 49 match the magnitude of the 2026-08-10 and both 2026-08-12 freeze-window reads almost exactly (prior: Necklaces SHORT 60-61, Earrings SHORT 49-51, Rings SHORT 11-13, Bracelets SHORT 7-8, Pendants SHORT 6-10). Third+ consecutive night this pattern repeats at near-identical size - stable and explained by the standing scope gap (Bravo = case+safe+back-stock+bins; sheet = display case only), NOT loss. Do not re-flag as new unless the size changes materially.
- WAY Rings SHORT 12 and ROA Rings/Earrings/Bracelets small SHORTs: this is the first clean freeze-window on-hand comparison on record for HAR, LEX, ROA, WAY (prior nights only had CUL fully validated). No baseline yet to call WAY Rings SHORT 12 a pattern or a one-off - watch next few nights.
- HAR and LEX small OVER cells (1-5 pieces each) are within normal miscount/timing noise, not flagged individually.
- No date mismatches, no missing/stale files, no non-ok rows. Freeze window valid on both sides (all stores close 6 PM, sheets taken 6:17-6:36 PM, Bravo pulled 8:51-9:17 PM).
- Reported to Joshua via Slack DM (D03BHQH5VGT) only, plain language, per Field Communication Standard - led with ROA pendants finding and the CUL known-pattern caveat.

## 2026-08-13 (sold-based reconciliation — BACKFILLED 2026-08-14 ~2:20 PM) - jewelry-count-reconciliation
- WHY LATE: the 7:47 PM Cowork task was found UNREGISTERED on 2026-08-14 (present on disk at Scheduled/jewelry-count-reconciliation/, absent from the registered task list; last successful run 2026-08-12). The 9:30 PM cloud watchdog correctly DMd Joshua. Root cause of the unregistration not pinned down — registration lost sometime after the 8/12 evening run. FIX: re-registered 2026-08-14 via create_scheduled_task (cron 47 19 * * *, registered as 7:49 PM daily with dispatch offset), original SKILL.md restored byte-identical (backup: SKILL.md.bak-pre-reregister-20260814), model claude-sonnet-5 frontmatter intact, enabled, next run tonight.
- Bravo pull: trigger jewelry-count-recon-2026-08-13-auto (dropped 2026-08-14 14:06, health gate PASS first). All 5 cells success: CUL 15, HAR 7, LEX 5, ROA 5, WAY 12 rows. Grids non-empty (valid), ZERO jewelry-category items among sold rows at all 5 stores -> sold buckets all 0 (verified via count_jewelry_sold + manual category listing: tools/games/firearms/handbags/coins only).
- Sheets (read 2026-08-14 via Chrome, 8/13-dated blocks, all sum-verified):
  CUL AM 637/120/155/122/243=1277 OK (PM 1279 per 8/13 night compare)
  HAR AM 450/48/124/49/112 sum 783 vs written total 784 (1-piece read ambiguity on sheet, annotations +5+4+1 rings, used written 784) (PM 802)
  LEX AM 264/33/44/42/48=431 OK (PM 454)
  ROA AM 541/118/157/79/148=1043 OK (rotated sheet, lightbox-verified; necklaces 157 pendants 148 disambiguated by total) (PM 1078)
  WAY AM 324/40/64/46/55=529 OK (PM 529)
- Reconciliation (net = AM-PM; sold=0 all stores; diff=net-sold): CUL -2 ok, HAR -18 FLAG, LEX -23 FLAG, ROA -35 FLAG, WAY 0 MATCH.
- All three flags are the case-GREW direction with matching intraday add tally-marks on the AM sheets (LEX rings 264+8 tallies -> PM 272 etc.) = new intake to case, NOT missing stock. No store shrank beyond sales.
- Posted plain-language summary to #jewlery-counts 2026-08-14 ~2:19 PM (a day late, no meta-commentary in channel).


## 2026-08-14 (~3 PM) - CULPEPER RECONCILIATION under new Jewelry Category Standard - manual, Joshua-directed
- Handler JewelryCaseCount.ahk extended to 8 categories (Charms, Brooches added; backup kept), watcher restarted cleanly.
- CUL live pull 2026-08-14 ~2:47-3:08 PM, trigger jewelry-onhand-cul-recount-2026-08-14, all 8 rows ok.
- Bravo unchanged vs 8/13 8:51 PM freeze pull on all 6 overlapping categories (no CUL jewelry transactions in between) -> values are freeze-window-valid against the 8/14 AM count sheet (Preston counted pre-open).
- Expected (grouped): Rings 649, Bracelets 127, Necklaces 215 (116+99), Earrings 172, Pendants 325 (253+44+28). Total 1488.
- Counted (Preston, 8/14 AM): 639 / 122 / 212 / 168 / 323. Total 1464.
- Variance: -10 / -5 / -3 / -4 / -2. Total -24 (all SHORT direction = scope gap: Bravo counts case+safe+back-stock+bins, count is display case only).
- Agreement with Preston: exact on Rings/Bracelets/Earrings/Pendants expected; Necklaces expected 215 (mine, verified twice) vs 214 (his) — 1 unit.
- The old ROA-style pendant anomaly is now explained/absorbed by the grouping standard (charms+brooches were the missing pieces).
- Nightly task now uses the 8-category pull + grouped mapping going forward.

## 2026-08-14 (~4:35 PM) - ALL 5 STORES pulled under 8-category standard; 8/13 EOD sheets reconciled
- Pulls: CUL (cul-recount trigger), HAR/LEX/ROA (4store trigger; WAY skipped by the 2700s hard-wall guard after retry loops), WAY (way trigger, status partial = Charms empty).
- KEY FINDING 1: the 2026-08-13 ROA Pendants OVER 61 was NOT a Bravo mis-categorization. ROA Charms=60, Brooches=2. Grouped expected 92+60+2=154 vs sheet 153 = -1. ROA counters were ALREADY counting pendants+charms+brooches together while the report pulled pendants only. Prior conclusion SUPERSEDED.
- KEY FINDING 2: the 8/13 sheets are INCONSISTENT store-to-store on what the PENDANTS line includes. Pendants-only vs grouped variance: CUL -10/-82, HAR +1/-5, LEX -1/-2, ROA +61/-1, WAY -4/-9. ROA counted GROUPED; CUL/HAR/LEX/WAY counted PENDANTS-ONLY. From 8/14 forward all stores are on the grouped standard (CUL 8/14: 323 counted vs 325 grouped expected).
- KEY FINDING 3: EMPTY CATEGORIES LOG AS ERRORS. HAR Charms, WAY Charms, LEX Brooches rendered zero rows, recorded error not 0 (no-false-zeros design). Verified genuine. Nightly SKILL.md updated with the empty-category rule: Charms/Brooches error counts as 0 ONLY if the prior-day CSV was also 0/error; positive prior day means real read failure. Other 6 categories: error always a failure.
- Bravo drift check (today live vs 8/13 freeze, 6 overlapping categories): CUL identical, LEX identical, ROA identical. HAR moved (Rings 457-456, Pendants 117-116); WAY moved (Rings 336-341, Pendants 59-62, Earrings 47-52, Chains 41-43, Necklaces 22-23). Both HAR and WAY have Charms=0 so only Brooches carries proxy risk.
- Reliability: SelectInventorySavedReport combo flaky (CUL Brooches, LEX Rings, ROA Charms each failed a full attempt then recovered on category retry). Burned the 45-min wall clock and cost WAY its slot. Consider raising the hard wall or splitting the nightly run now that it is 5 stores x 8 categories.

## 2026-08-14 (~8:30-9:35 PM ET) - Nightly jewelry-onhand-nightly-pull (consolidated task), all 5 stores

- Weekday gate: Friday -> all 5 stores (CUL, HAR, LEX, ROA, WAY).
- Contention check: no claim in last 30 min (most recent prior claim 2026-08-13). Health gate PASS (target CUL, 2026-08-14 20:35:53).
- Trigger jewelry-onhand-2026-08-14 dropped 20:35:59 EDT, claimed within 15s.
- Bravo pull (freeze-window, stores closed 6:00 PM): completed 21:31:41. Overall status partial - all 5 stores processed, 3 known empty-category errors (HAR Charms, LEX Brooches, WAY Charms), each confirmed empty per two retry attempts (90s no-parseable-row-total each) and matches the 2026-08-14 confirmed-empty list already in the nightly SKILL.md. Treated as 0 per the empty-category rule. CUL and ROA: all 8/8 categories success, no errors.
- PM count sheets read via Chrome vision from #end-of-day, 8/14-dated block on each sheet, all sum-verified against written TOTALS line (ROA required total-minus-categories disambiguation on Earrings AM/PM digits - illegible digit, math-derived 85/87, both totals then matched exactly).
- Store-to-sheet mapping confirmed via each sheet's own printed header (not poster identity): Sandi=CUL, Walker Tapley=HAR, Uriah=LEX, Benjie Moore=ROA (rotated 90 deg sheet), Chadd=WAY.

Expected (Bravo, grouped) vs Counted (PM sheet), Rings/Bracelets/Earrings/Pendants/Necklaces:
- CUL: 639/123/168/323/212 vs 639/122/168/323/212. Variance 0/-1/0/0/0. Total 1465 vs 1464 (-1).
- HAR: 451/49/48/121/122 vs 461/49/49/118/124. Variance +10/0/+1/-3/+2. Total 791 vs 801 (+10).
- LEX: 268/36/51/54/44 vs 272/37/49/52/46. Variance +4/+1/-2/-2/+2. Total 453 vs 456 (+3).
- ROA: 553/124/92/154/161 vs 552/123/87/153/161. Variance -1/-1/-5/-1/0. Total 1084 vs 1076 (-8).
- WAY: 338/41/52/66/66 vs 321/40/46/60/64. Variance -17/-1/-6/-6/-2. Total 563 vs 531 (-32).

- Table posted to #jewlery-counts 2026-08-14 ~9:41 PM, no commentary per format.
- DM sent to Joshua: HAR Rings +10 OVER (counted 461 > expected 451) - this is the only anomalous OVER variance tonight and does not match any previously logged standing case. No prior-night HAR Rings variance of this size found in this file on a quick pass - flag as a one-night event pending next comparison, not yet a confirmed repeating pattern. All other variances are in the expected SHORT direction (Bravo scope: case+safe+back-stock+bins vs sheet display-case-only) or small enough (LEX +3, CUL -1) to be counting noise.
- No repeat-pattern conclusion possible yet for WAY -32 / ROA -8 vs prior nights without a systematic night-over-night diff; flagging for a future session to build one if this file keeps growing ad hoc.
