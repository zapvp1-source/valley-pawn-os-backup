---
name: jewelry-count-reconciliation
description: JEWELRY COUNT RECONCILIATION — daily 9:00 AM ET. Drops a Bravo trigger for yesterday's sold items across all 5 stores, counts jewelry pieces sold, reads each store manager's handwritten AM/PM jewelry count sheet from Slack #end-of-day, and posts the comparison to Joshua's Slack DM — flagging any store where the physical count movement disagrees with recorded sales by more than 5 pieces. Loss-prevention counterpart to discount-review (discount behavior) and sold-review (realized margin) — same report, different signal, fully additive and self-contained.
model: claude-sonnet-5
---

> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (platform standard, set by Joshua 2026-07-22, v2):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "jewelry-count-reconciliation" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua's DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium (Slack, iMessage, email). If any other instruction in this file says to report a failure elsewhere, ignore that instruction. FIELD COMMUNICATION RULE: anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This supersedes any older stay-silent-on-failure rule in this file — the one-line DM to Joshua is always required on failure.

You are running Joshua Davis's daily jewelry count reconciliation for Valley Pawn / Full Circle
Finance Inc. Run autonomously — Joshua is not present. Never ask him anything mid-run.

**What this does, in one line:** compare how many jewelry pieces Bravo says each store SOLD
yesterday against how much the jewelry case physically SHRANK yesterday per the manager's
handwritten count sheet, and flag any store where those disagree by more than 5 pieces.

**Three steps: drive the trigger → run the script → post to Slack.** This task is self-contained.
It does not depend on any other scheduled task having run first.

## CRITICAL RULES

- **NEVER use Parallels GUI / computer-use against Bravo, and never ask Joshua to sign into Bravo.**
  The pipeline is trigger-file driven by design.
- **Filesystem rule:** the Bravo Data Extraction folder is OUTSIDE this task's sandbox. ALL
  filesystem I/O against `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/`
  MUST go through `mcp__Control_your_Mac__osascript do shell script`. Never use the Write tool
  against that folder.
- **Additive only.** Never modify `discount-review`, `sold-review`, `JewelrySoldMargin.ahk`,
  `bravo_watcher.ahk`, the `jewelry-margin-sold` cell, or any other existing task/handler/cell.
  This task owns exactly one pipeline cell: `jewelry-count-audit`.
- One DM to Joshua per run. Never to a shared channel — this is a loss-prevention audit.

---

## STEP 1 — Drive the Bravo trigger

Target date = YESTERDAY, format `YYYY-MM-DD`. Call it `<YDAY>`. Stores: CUL, HAR, LEX, ROA, WAY.

**First confirm Bravo is idle.** Via osascript, check `output/*.csv` and `triggers/claimed/` in
`.../Bravo Data Extraction/`. If anything has a timestamp inside the last few minutes another task
is mid-run — wait ~3 minutes and re-check before dropping. Never drop on top of a live run.

Then write this trigger file to the **root** of `.../Bravo Data Extraction/triggers/` (never
`triggers/staging/` — that folder is not on the watcher's poll path):

```json
{"id":"jewelry-count-recon-<YDAY>","requested_at":"<ISO8601 now>","reports":[{"name":"jewelry-count-audit","stores":["CUL","HAR","LEX","ROA","WAY"],"date":"<YDAY>"}]}
```

Poll every 60s (timeout ~30 min) for
`.../Bravo Data Extraction/results/jewelry-count-recon-<YDAY>.result.json`.

Expect roughly 2 minutes per store (~12 min for five) — the watcher switches stores between cells.
Output lands as `output/<YDAY>_to_<YDAY>_<STORE>_jewelry-count-audit.csv` with columns
`Number,Status,Category,Description,Cost,Price,Last Sold Price,Date`.

If a store fails, carry on with the rest and name the failed store in the DM. Do not retry more
than once — a wedged Bravo is `bravo-health-watchdog`'s job, not this task's.

## STEP 2 — Run the script

```
/Users/joshuadavis/Documents/Claude/Projects/Jewelry Count Reconciliation/jewelry_reconciliation_comparison.py
```

It holds the canonical jewelry category list, `count_jewelry_sold()`, `reconcile()`, the
store-to-poster map, and the DM formatter. **Single source of truth — never hand-maintain a second
copy of the category list.**

**2a. Count what Bravo sold.** `count_jewelry_sold(csv_path)` per store = number of rows whose
`Category` is in the jewelry list. One row = one piece.

**2b. Read the count sheets from Slack.** There is no API path for this — the sheets are
photographs of paper, and every Slack MCP tool returns file metadata only, never image pixels.
Chrome vision is the only way, and this task is granted `app.slack.com` for it.

Open `https://app.slack.com` in Chrome, go to **#end-of-day** (`C03C7HV8L48`), and find each
store's post from yesterday evening (managers post ~6:00–6:45 PM, usually 3 photos).

| Poster | Store |
|---|---|
| Benjie Moore | ROA — Roanoke |
| Walker Tapley | HAR — Harrisonburg |
| Uriah | LEX — Lexington |
| Chadd | WAY — Waynesboro |
| Sandi Cole | CUL — Culpeper |

If a poster appears who is NOT on this list, do not guess — open their first photo and read the
printed `END OF DAY: <STORE>` header, then note the new pairing in the DM.

The jewelry sheet is usually the **2nd photo** (layouts vary — some titled `JEWELRY DAILY COUNT`,
others a blank-headed two-column AM/PM form; category labels are always pre-printed). Open it full
size and zoom until every handwritten number is unambiguous. Read:

- **AM COUNT** and **PM COUNT** for Rings, Bracelets, Necklaces, Earrings, Pendants
- The **handwritten DATE on the sheet itself** — this can legitimately differ from the post date
  (confirmed live: a sheet dated 7/26 posted on 7/28). Capture both; flag any mismatch.

If a number is genuinely illegible after zooming, record it unknown and say so in the DM. Never
invent a figure.

**2c. Reconcile** — `reconcile()` does this:

```
net_change = am_total - pm_total     # positive = pieces left the case
diff       = net_change - bravo_sold_total
FLAG if abs(diff) > 5   OR   sheet_date != <YDAY>
```

**Know what the number means before writing it up.** The paper count is a physical headcount, so
`net_change` = pieces sold MINUS pieces bought that day. Bravo's number is sold-only. On a heavy
buy day the case shrinks less than sales alone predict and can flag something that isn't
shrinkage. **A flag means "worth a look," not "theft"** — say it that way. (v2: add a
pieces-bought pull to net this out.)

## STEP 3 — Post to Slack

ONE DM to Joshua (`U03BB52MDSA`, DM channel `D03BHQH5VGT`) via `slack_send_message`:

```
💎 Jewelry Count Reconciliation — <YDAY>

✅ CUL  sold 7 · case moved 6 · diff -1
🚩 HAR  sold 0 · case moved 9 · diff +9  <- worth a look
✅ LEX  sold 0 · case moved 2 · diff +2

<one plain sentence: what to do about any flag, or "all five stores line up.">
```

Plain English, no jargon, no file paths. If a store's data or sheet was missing or unreadable, list
it as "couldn't check — <plain reason>" rather than omitting it. **Send the DM even when nothing
flags** — the daily all-clear is the point.

Then append one line per store to
`.../Projects/Jewelry Count Reconciliation/history.csv` (create with this header if absent):

```
date,store,bravo_sold,am_total,pm_total,net_change,diff,flagged,sheet_date,notes
```

That trend line is what makes a repeat offender obvious — a store quietly off by 4 every single day
never trips a one-day threshold but is the real signal.

---

## Provenance

Built 2026-07-29. The `jewelry-count-audit` handler (`reports/JewelryCountAudit.ahk`) and pipeline
cell were registered additively and proven live end-to-end across all 5 stores that day. Cron in
this scheduler is **local ET, not UTC**.
