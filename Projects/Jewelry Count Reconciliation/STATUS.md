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
