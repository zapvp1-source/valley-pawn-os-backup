---
name: bravo-end-of-month
description: >
  Canonical Bravo data source for any cross-store balance, sales, pawn service
  charge, layaway, or monthly snapshot question for Valley Pawn. Use this skill
  ANY time a task needs Ending Loan Base, Ending Inventory Base, Sales Revenue,
  Pawn Service Charges, Layaway activity, or any other End-of-Month metric for
  one store, several stores, or all 5 stores — including the asset-recovery
  artifact, the monday-store-rankings leaderboard, monthly business minutes,
  QBO Loans Receivable + Inventory Asset reconciliation, deep KPI analyses,
  and any new data project that needs Bravo balance data. Trigger whenever
  Joshua says "loan base," "inventory base," "EOM," "end of month," "month-end
  numbers," "monthly snapshot," "current loan balance," "current inventory,"
  "pull EOM for [store]," "give me the monthly," or any variation that implies
  needing a Bravo monthly aggregate. Pairs with `bravo-context` (general
  Bravo reference), `bravo-store-cycle` (login flow), and `qbo-context`
  (where the same numbers eventually land in the books).
---

# Bravo End-of-Month Report — Canonical Data Pipeline

The End of Month (EOM) report is Bravo's built-in monthly business snapshot.
It is now Valley Pawn's **single source of truth** for current cross-store
loan + inventory + sales + pawn-service-charge + layaway numbers. Any data
project that previously cobbled these numbers from QBO, ad-hoc Bravo screens,
or computer-use should now read the EOM CSV instead.

## Why EOM is the canonical source

- **One report, almost everything.** EOM covers Ending Loan Base, Ending
  Inventory Base, Sales Revenue, Pawn Service Charges (daily Interest +
  Fees), Layaway activity, and additional aggregates in one document.
- **Cross-store consistent.** Run the same trigger per store and you get
  identical column shape for every store — easy to sum across the chain.
- **Date-range aware.** Accepts a `YYYY-MM-DD..YYYY-MM-DD` range, so it works
  for MTD, full-month, quarter, or arbitrary windows.
- **Pipeline-driven.** No computer-use required at consumer skill time —
  drop a trigger, watcher fetches, output lands as CSV.
- **Same numbers Bravo itself uses for management reporting.** Matching to
  QBO is straightforward because the books-of-record (zapvp1) ultimately
  derive their Loans Receivable + Inventory Asset balances from Bravo.

## What the CSV contains

Per the handler header in `reports/EndOfMonth.ahk`, the report covers:

- **Ending Loan Base** — pawn loan portfolio balance as of the end date.
  Sum across 5 stores ≈ QBO Loans Receivable.
- **Ending Inventory Base** — inventory at cost as of the end date.
  Sum across 5 stores ≈ QBO Inventory Asset.
- **Sales Revenue** — retail sales for the date range.
- **Pawn Service Charges** — daily Interest + Fees totals aggregated.
- **Layaway activity** — new layaways, payments, completions.
- **Daily Detailed Section** — optional checkbox; expands the report with
  per-day rows. Handler currently leaves this off (compact monthly summary).
- Plus other line items the report exposes by default.

> **TODO** — once a clean EOM CSV is in hand, inspect column layout and
> document exact column names + their parse pattern here. The May 23 CUL
> test produced 138 rows but the file was truncated by a follow-up failed
> run. Re-pull a clean CUL CSV and capture the schema in this section.

## Pipeline cell

| Field | Value |
|---|---|
| Cell name | `end-of-month` |
| Handler | `reports/EndOfMonth.ahk` |
| Function | `PullEndOfMonth(store, dateOrRange, outputDir)` |
| Output filename | `<END_DATE>_<STORE>_end-of-month.csv` |
| Output folder | `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/` |
| Registered in | `bravo_watcher.ahk` (line 111) |
| Per-store runtime | ~60s when Bravo is on the Dashboard, plus ~10–15s per EnsureStore cycle |

## Trigger schema

Drop a JSON file into `triggers/` — the watcher polls every 30s. Force an
immediate poll with `Ctrl+Alt+R` inside the VM.

Single store:

```json
{
  "id": "eom-cul-2026-05-26",
  "requested_at": "2026-05-26T13:00:00-04:00",
  "reports": [
    {
      "name": "end-of-month",
      "stores": ["CUL"],
      "date": "2026-05-01..2026-05-26"
    }
  ]
}
```

All 5 stores, MTD:

```json
{
  "id": "eom-allstores-2026-05-26",
  "requested_at": "2026-05-26T13:00:00-04:00",
  "reports": [
    {
      "name": "end-of-month",
      "stores": ["CUL","HAR","LEX","ROA","WAY"],
      "date": "2026-05-01..2026-05-26"
    }
  ]
}
```

Full-month closing snapshot (e.g., to feed monthly minutes or QBO reconciliation):

```json
{
  "reports": [
    {
      "name": "end-of-month",
      "stores": ["CUL","HAR","LEX","ROA","WAY"],
      "date": "2026-04-01..2026-04-30"
    }
  ]
}
```

## Consumer skill pattern

Every downstream data project should read the EOM CSV(s) — never re-trigger
the underlying Bravo screen. Pattern:

1. **Check the output folder for a recent enough CSV.** Filenames are
   `YYYY-MM-DD_<STORE>_end-of-month.csv` where `YYYY-MM-DD` is the END date.
   If the window you need already has a CSV, reuse it (per the additive-only
   rule in `bravo-context`).
2. **If you need a fresher pull, drop an EOM trigger** with the date range
   you need, then poll `results/<trigger_id>.result.json` for completion.
3. **Parse the CSV** for the specific metric(s) you need.
4. **Never edit the EOM handler or rename the saved report.** Additive-only
   rule applies — clone if you need a different shape.

## Skills that should pull from EOM going forward

| Skill / artifact | Old source | New source |
|---|---|---|
| `asset-recovery-2025-vs-2026` artifact (daily refresh) | QBO zapvp1 (read-only browser) | EOM CSV — sum Ending Loan Base + Ending Inventory Base across 5 stores |
| `monday-store-rankings` | computer-use through Company KPIs | EOM CSV per store (already the planned source) |
| `compile-monthly-minutes` — financial-results section | QBO P&L screenshot | EOM CSV — full-month range |
| `qbo-context` Loans Receivable / Inventory Asset lookups | jdavis books or zapvp1 | EOM CSV (per qbo-context: Bravo is the upstream source anyway) |
| `new-inv-weekly-report` Inventory portion | aged-inventory-summary | EOM CSV for higher-fidelity inventory metrics |

## Known limitations (current)

- **Preview-render bug.** As of 2026-05-26, after `step 4: click config Ok`
  the report preview sometimes fails to render within 60s — the handler
  errors with `Preview did not render within 60s (Export Document button
  never appeared)`. Worked in the May 23 single-CUL test (138 rows in 60.8s),
  failed for ROA and WAY on May 26. Likely a UIA quirk on the Ok click that
  needs to land on the right modal Ok (compare against `AgedInventorySummary`
  which uses `btnOk` AutoId).
  - **Workaround until fixed:** run single-store triggers and retry on
    failure, or fall back to aged-inventory-summary + a separate loan-balance
    source while the bug is being worked.
- **Requires Bravo running on the Dashboard.** If Bravo is closed or on a
  non-Dashboard screen, the trigger errors fast with
  `Bravo window not found/ready within 30s`. Joshua should confirm Bravo is
  up before re-dropping.
- **EnsureStore cycles add ~10–15s per store transition.** 5-store run ≈
  5–7 minutes when everything works.
- **bravo_export.ahk dispatch table is stale.** It is missing `end-of-month`
  and several other handlers. The watcher path (`bravo_watcher.ahk`) is the
  production entry point — triggers dropped into `triggers/` always go
  through the watcher, so this hasn't blocked anything. If `bravo_export.ahk`
  is later resurrected as a manual one-shot tool, sync its dispatch.

## Don'ts (additive-only rule)

- Don't edit `EndOfMonth.ahk` to fit a different report shape. Clone to a
  new handler file with a distinct function name and a new pipeline cell
  name (per `bravo-context` additive-only rule).
- Don't rename the saved Bravo report tile.
- Don't re-trigger if a CSV that covers your window already exists.
- Don't run during the daily-funds-verification window (~6 PM ET) — the
  watcher serializes triggers and a long EOM run can delay verification.

## Companion skills

- `bravo-context` — general Bravo reference + UI quirks + reports catalog.
- `bravo-store-cycle` — owns the cross-store login flow that `EnsureStore`
  uses inside the handler.
- `qbo-context` — explains why Bravo (and therefore EOM) is the upstream
  source of truth for Loans Receivable and Inventory Asset.
- `monday-bravo-combined-run` — Monday combined run; EOM cell will be
  added to its trigger template once the Preview-render bug is fixed.
