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
