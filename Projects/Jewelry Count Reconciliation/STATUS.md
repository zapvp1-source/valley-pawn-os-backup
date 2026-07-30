# Jewelry Count Reconciliation — STATUS

**Last updated:** 2026-07-29
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
