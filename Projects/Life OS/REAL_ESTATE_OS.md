# Real Estate OS — Master Reference

**Created:** 2026-08-07 · **Domain 2 of 3** in the Life Map (`Life OS/LIFE_MAP.md`)
**Mission:** every property Joshua owns or is evaluating — business or personal, short-term
rental or long-term hold — tracked in one place so no session re-discovers the same facts.

This file is a living reference, same pattern as `bald-rock-property` and `BUSINESS_OS.md`.
Jump to the property that's relevant; don't read end-to-end every time.

---

## Portfolio at a glance

| Property | Type | Owner | Status | Detail |
|---|---|---|---|---|
| **282 Bald Rock Road, Verona, VA 24482** | Short-term rental (Airbnb + VRBO) | Full Circle Finance Inc (same entity as Valley Pawn) | Active, performing well | See "Bald Rock" below + `bald-rock-property` skill |
| **844 Cypress Crossing Trail, St. Augustine, FL 32095** (Parcel 072085-0710) | Was long-term rental → converted to **primary personal residence ~Aug 2025** | Joshua & Hillary Davis, personally | Owner-occupied since conversion | See "Cypress Crossing" below |
| Jacksonville, FL area | Prospective acquisition | TBD | Search-stage — `weekly-jacksonville-property-search` scheduled task exists but is on-disk/unregistered (never fires) | Future expansion |
| St. Johns County / St. Augustine, FL area | Prospective acquisition | TBD | Search-stage — `weekly-st-augustine-property-search` scheduled task exists but is on-disk/unregistered (never fires) | Future expansion |

**Both property-search tasks are built but not live.** Before doing new work on prospective FL
acquisitions, decide whether to register those tasks (Rule #4 — additive, don't just flip them on
without checking why they were never registered) or replace them.

---

## 282 Bald Rock Road — the short-term rental

Full operating detail (Wi-Fi, lockbox, guest messaging, DocuSign contract flow, cleaning,
pricing) lives in the **`bald-rock-property`** skill — always read that skill directly for
day-to-day guest/booking work. This section covers the parts that skill doesn't: acquisition,
ownership, and tax/basis.

- **Purchased:** 2016. Contract 8/8/2016 via Charlotte McAlister (RE/MAX Advantage); financing
  through BNC National Bank; appraisal ordered 9/13/2016 (United States Appraisal LLC).
- **Purchase price / basis:** $405,000.00 per recorded deed (`CONSIDERATION: 405,000.00`).
  Deed source: Google Drive `.../02 Real Estate/282 Bald Rock Rd - Verona VA (Rental)/282 Bald
  Rock Deed:Closing.pdf` (image-only PDF, OCR'd 2026-08-05).
- **Owner entity:** Full Circle Finance Inc — same legal entity as Valley Pawn. Financially and
  operationally tracked separately (own P&L, own guests, own vendors) but same tax return.
- **Capital improvements / basis substantiation:** `Taxes 2026/282 Bald Rock — Full Evidence
  Log.md` (built 2026-08-05 from the unified Apple Mail + iMessage + iCloud Drive index) is the
  **current, authoritative** evidence log — headline: $97,615.40 proof-of-payment,
  $110,673.74 invoiced-not-proven, ~$176,000 quoted-only, against a claimed $305,086.51 total.
  **`Taxes 2026/Bald Rock Improvements Substantiation.md` is SUPERSEDED and unreliable** — it
  searched only Gmail (missed Apple Mail accounts) and had a broken SQL date filter that silently
  returned zero rows on every date-filtered query. Do not cite its negative findings.
  ⚠️ The "quoted" figures include competing/losing bids for the same job (e.g. two losing bids
  for the retaining wall Red Rock actually built) — don't double-count quotes against a job that
  has a winning, paid invoice elsewhere.
- **Cost segregation:** `Short Term Rental Optimization/Portfolio_Cost_Seg_Readiness.docx` and
  `Bald_Rock_Cost_Seg_Intake_Package.docx` — readiness package for a cost-seg study covering the
  portfolio (both properties, likely). Read these before any depreciation/basis work.
- **Revenue tracking:** `Short Term Rental Optimization/Bald_Rock_Year1_Revenue_Report.xlsx`.

**Guest operations, contracts, pricing, cleaning → always defer to the `bald-rock-property`
skill, not this file.**

---

## 844 Cypress Crossing Trail, St. Augustine, FL — the personal residence

- **Address:** 844 Cypress Crossing Trail, St. Augustine, FL 32095 (Parcel 072085-0710).
- **Owners:** Joshua & Hillary Davis, personally — **not** Full Circle Finance Inc, not Valley
  Pawn. Treat as Domain 3 (Personal) for money/tax purposes even though it lives in this file for
  property-tracking convenience.
- **History:** was a long-term rental; **converted to primary personal residence ~August 2025.**
  This conversion date matters for tax treatment (basis step, depreciation recapture exposure,
  what counts as a deductible improvement vs. personal capital improvement going forward).
- **Capital improvements substantiation:** `Taxes 2026/844 Cypress Crossing Improvements
  Substantiation.md` (prepared 2026-08-04, sources: Gmail jdavis@fcfpawn.com, Google Drive folder
  `1fUZiD0rjBCzqkaVeI_Ye-Ztg-RPuvZUf` "844 Cap Gain Improvemnts" + parent "07 Improvements &
  Maintenance" tree, existing `844 CAP GAIN Improvements Log.xlsx`).
  - **Documented and paid: $94,663.42** — $49.00 pre-conversion (rental period), $8.51 at/around
    conversion, $94,605.91 post-conversion (personal residence period: flooring, doors, water
    heater, pool deposit, mechanical permit, impact windows).
  - **Quoted/estimated but NOT proven paid: ~$289,912.80** — not deductible or basis-eligible as
    currently substantiated. 100% of this falls post-conversion.
  - The existing `844 CAP GAIN Improvements Log.xlsx` shows $118,073.79 total but **is not usable
    as filed** — it mixes proven payments with unproven quotes and double-counts at least one job
    (Manning Building Supply doors — a Returned Check email exists for the same cashier's check
    day; needs resolution before relying on that line).
- **Vehicle Purchase Docs** and **Bank Statements** subfolders exist under `Taxes 2026/` — likely
  relevant to Cypress Crossing conversion or general personal tax prep; not yet indexed here.

---

## Landscape / grounds work (cross-reference only)

`Projects/Landscap Plan` and `Projects/Landscape design` project folders hold front-bed landscape
plans (PDFs). Not yet clear which property these belong to (Bald Rock, Cypress Crossing, or Salt
Run Landscape Co.'s own work) — **confirm the property before doing landscape-related work**,
don't assume.

**Salt Run Landscape Co.** is a separate business Joshua owns (own analytics/SEO cadence:
`salt-run-weekly-analytics`, `salt-run-monthly-seo-audit`, `salt-run-quarterly-phase-check`, all
currently disabled per BUSINESS_OS.md live state). It is NOT a real-estate holding — it's a
services business — but is closely adjacent to this domain because of the landscape-work overlap
above. If a task is clearly about Salt Run's own operations (not a property Joshua owns), treat
Salt Run as its own 4th-ish domain and flag it for its own OS file if work there becomes
recurring.

---

## Where the documents actually live

Three sources, all already reachable — no per-session reconnection needed for the first two:

- **Google Drive** (`jdavis@fcfpawn.com`, connector-based, always live): root folder **"02 Real
  Estate"** — `https://drive.google.com/drive/folders/1ffpSkmXB6djnHAVftWl-62emmEsYuOCc` —
  contains **"282 Bald Rock Rd - Verona VA (Rental)"**
  (`https://drive.google.com/drive/folders/1RyxXAassRDIWmww7Mb3n-0a-Ekq0aRz9`) and
  **"844 Cypress Crossing Trail - FL (Home)"**
  (`https://drive.google.com/drive/folders/1AsSEp9UYoNXHJ5-_Bd8YHmT46WVYD8hm`). There is also a
  newer, mostly-empty **"Real Estate"** folder (created 2026-08-06,
  `https://drive.google.com/drive/folders/1XfjEGWYw_lfsXVWo3PJRPucjiHKPdFsT`, currently just a
  "Leases" subfolder) and a **"Real Estate Improvements (Desktop Import)"** folder — unclear if
  these are an in-progress reorg or abandoned duplicates. **Don't assume which is canonical** —
  check both before concluding a document doesn't exist, and flag the duplication to Joshua if it
  becomes a real source of confusion.
- **Local files** — `~/Documents/Claude/Projects/Taxes 2026/`, `Short Term Rental Optimization/`,
  and this `Life OS/` folder. Reachable in Cowork after the one-time-per-session folder connect
  (see `enterprise-map` Step -1 — self-healing, requests access automatically if missing).
- **Apple ecosystem** (Mail, iMessage, iCloud Drive — all accounts, back to 2009 for Mail) — via
  the `unified-search` skill. This does NOT depend on Cowork's folder-mount system at all (it runs
  through native Mac automation, not the sandboxed Read/Grep tools), so it's effectively always
  available regardless of what's connected this session. Use it before concluding something
  "doesn't exist" — several of the evidence logs above were built specifically because earlier
  passes only checked Gmail and missed material sitting in other Apple Mail accounts.

---

## Working rules for this domain

Same four hard rules as Valley Pawn (`valley-pawn-context` Rules #1–#4: act autonomously, never
ask Joshua to log in, check prior work before redoing, build additive). Two additions specific to
real estate:

1. **Never mix entity money.** Bald Rock expenses go through Full Circle Finance Inc. Cypress
   Crossing expenses are Joshua & Hillary personally. Don't let a receipt, invoice, or basis
   calculation cross that line without Joshua explicitly saying so.
2. **Tax/basis claims need a documented-and-paid citation, not a quote.** Both evidence logs above
   already learned this the hard way (double-counted bids, unproven quotes). Any new capital
   improvement claim should specify which evidence tier it's in (paid / invoiced-unpaid / quoted)
   before it goes near a tax filing.

---

## How to extend this file

New property → add a row to the portfolio table and its own section. New capital improvement
evidence → update the relevant property's substantiation-log pointer (don't duplicate the log
here, keep this file as the index). New prospective-acquisition activity (Jacksonville/St.
Augustine search tasks going live, an offer, a closing) → update the portfolio table's Status
column and note the date.
