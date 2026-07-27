# Sold Margin Review — Project STATUS

> READ FIRST. Resume from here; do not restart. Additive-only (Rule #4) — no existing Bravo report,
> handler, pipeline cell, or scheduled task was modified to build this.

**Built:** 2026-07-23
**Owner:** Joshua Davis
**Goal:** Daily report that grades what we ACTUALLY got when items SOLD — Sale Price vs Cost, both
exact numbers Bravo already tracks — and flags items that sold too cheap. Sales-side mirror of the
existing `pawn-walk` (buy-side intake margin) pipeline.

---

## Why this is a separate build from pawn-walk / daily-intake-margin

pawn-walk grades INTAKE (loans + buys) against an INDEPENDENT external market-value estimate,
because at the moment we acquire something there's no internal cost basis yet — we don't know what
"right" looks like without going outside Bravo (melt value, eBay comps, gun-value sites). That's why
it needs the whole T1/T2/T3 valuation engine.

Sold Review is the opposite direction and structurally simpler: once an item has SOLD, Bravo already
has both the exact Cost and the exact Sale Price on the ticket. No estimation, no external lookups —
just `(Sale Price − Cost) / Sale Price`. This project intentionally does NOT reuse any of the
T1/T2/T3 valuation code; margin here is exact, not estimated.

## Decisions made (do not re-ask — see Expert Review Board deliberation, 2026-07-23)
- Target margin: 50% (matches the company's actual retail-margin benchmark — 52.0% Jun'26, 53.5%
  YTD, 52.8% T12M per the monthly analytics DM to Joshua on 2026-07-02 — so this is descriptive of
  where the company already sits, not aspirational).
- Flag threshold: below 25% realized margin ("sold too cheap"). Chosen to mirror the buy-side
  pawn-walk convention (30% flag vs 50% target, ~60% of target) with a bit more headroom, since
  retail sales have legitimate reasons to run thinner (clearance, bundles, employee discount) that
  acquisition-side "overpay" doesn't have.
- CRITICAL sub-flag: any item sold AT OR BELOW COST (negative margin) is always flagged regardless
  of category — unambiguous signal, no threshold judgment needed.
- Aging: items with 90+ days on shelf get an "(aged clearance)" annotation on their flag line rather
  than being suppressed. Still visible (so Joshua isn't blind to real pricing mistakes hiding behind
  "well it was aged"), but contextualized so a legitimate markdown-to-move doesn't read the same as
  a fresh item priced wrong on day one.
- Cadence: 7:45 AM daily (75 min after pawn-walk's 6:30 AM run) so Joshua reads them back-to-back,
  not simultaneously — and so Bravo/the watcher aren't asked to do two concurrent multi-store pulls.
- Slack: NEW channel #sold-review (`C0BK802MP43`, created by Joshua 2026-07-23). Never posts to
  #pawn-walks — different signal, would dilute both.

## What's built (2026-07-23)

### Bravo pipeline (additive)
- `reports/SoldYesterday.ahk` — NEW handler, cloned from the proven `SoldInvDetails.ahk` template
  (same Inventory → Custom Reports → SelectSavedReport → SetReportDate → grid-walk → Cancel pattern).
  Points at Joshua's own saved report **"Claude Sold Yesterday"**.
- Registered pipeline cell `sold-yesterday` in `bravo_watcher.ahk` — ADDED two lines only (#Include
  + REPORT_HANDLERS entry), did not touch any existing line. Output:
  `<date>_to_<date>_<STORE>_sold-yesterday.csv` in the standard output/ folder.
- Watcher restarted 2026-07-23 (via the documented one-shot-scheduled-task `prlctl exec` mechanism
  per BRAVO_KNOWN_ISSUES.md — never interactive) to load the new handler.

### Compile / analysis (this folder)
- `run_daily_sold_review.py` — reads yesterday's sold-item CSVs per store (flexible column-name
  matching + multiple filename-pattern fallbacks, in case a separate task ever produces the CSV
  under a slightly different name), computes margin %, margin $, flags, and the aged-clearance tag,
  writes a 3-tab Excel (Items/Summary/Flags) + JSON summary, posts to Slack #sold-review.
  Tested against synthetic data in a sandbox before deployment — confirmed margin math, flag logic,
  Excel generation, and JSON output all work correctly.
- Output: `daily/{DATE}_sold_review.xlsx` + `daily/{DATE}_sold_review_summary.json`.

### Scheduled task
- `sold-review` — registered as a scheduled trigger, `45 11 * * *` UTC (7:45 AM ET), consolidated
  single-task pattern (health-gate → drop trigger → poll → compile → post → DM Joshua on
  failure/flags only), mirroring the proven `pawn-walk` architecture. SKILL.md staged at
  `/Users/joshuadavis/Documents/Claude/Scheduled/sold-review/SKILL.md` for the documentation
  convention BUSINESS_OS.md / enterprise-map expect.

## NOT YET PROVEN — first live run is the smoke test

This entire chain has never run against live Bravo. Specifically unverified:
1. **Exact location of "Claude Sold Yesterday" in Bravo.** Assumed Inventory → Custom Reports
   (same place as the existing, similar "Claude Sold Inv Details" report). If Joshua actually built
   it under Sales or Void/View Transactions, `SoldYesterday.ahk` will fail to find it — the handler
   logs a clear error and the scheduled task DMs Joshua rather than looping blindly (see SKILL.md
   "First live run note" and STEP 4b).
2. **Exact column headers the report exports.** The compile script does flexible case/space-
   insensitive header matching for Cost / Sale Price / Description / Category / Ticket / Date Sold /
   Days On Shelf, so minor naming differences self-resolve; a genuinely missing Cost or Sale Price
   column would just mean 0 items load — the task DMs Joshua on a data-driven zero-items night the
   same way an outright Bravo failure would (both look like "no rows found" but for different
   reasons — worth a manual check of the CSV if the first run comes back empty).

**Next session / first live run (2026-07-24 ~7:45 AM):** check the Slack post and, more importantly,
check `logs/sold-yesterday-*.log` if it DMs a failure — that log will say exactly which UIA step
failed, which almost always means updating one string constant in `SoldYesterday.ahk` (module name
or report name) rather than a deeper rebuild.

## Redundancy check performed (2026-07-23)
- No other scheduled task, live trigger, or project folder (checked recent Slack, live trigger
  list, and file-modification timestamps across the whole `Claude/` tree) is currently building or
  producing a "sold yesterday" / "sold-review" data feed. `pawn-walk` (buy-side) and
  `monthly-sold-inventory-refresh` (monthly CFO fringe-sale analysis on a *different* saved report,
  "Claude Sold Inv Details") are the only adjacent pieces of infrastructure, and neither overlaps in
  cadence, data direction, or Slack destination with this task.
