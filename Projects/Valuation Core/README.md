# Valuation Core — STATUS / README

Shared valuation pieces used by the daily reports. Built 2026-09-28 from the 9/28 Joshua–Preston huddle
(Preston: sold-review gun values look wrong; discounts should be judged against how long the item sat).
Read this before changing any value, age or discount logic in Pawn Walks, Sold Margin Review or
Discount Outlier Review.

## Modules

| File | What it does | Used by |
|---|---|---|
| `item_age.py` | Days-on-shelf for any Bravo SKU, from the SKU counter's frontier across every sold pull. Cache `item_age_index.json`, rebuilt once a day (~2 s). | Discount review (age-aware flags), Sold review (aged-clearance tag, previously never fired) |
| `discount_policy.json` / `.py` | Discount allowed by age band. **Edit the JSON to change the policy.** | Discount review |
| `gun_value.py` | Firearm fair value: gun-category comps only, calibers never match keys, Glock bare model numbers handled, serials stripped; GunBroker official API when connected. | Sold review (fair value), Pawn walks (T2 for guns) |

## Decisions (and why)

- **Age source = SKU frontier, not a new Bravo pull.** The Bravo report that lists every on-shelf item with its
  date cannot be pulled (grid too large to walk — BRAVO_KNOWN_ISSUES). Adding more daily Bravo pulls also
  adds contention. The SKU method needs zero Bravo time and backtests at 89–98% within 14 days (median
  1–3 days) on the five main SKU series. Undatable series return no age and the report falls back to its
  original flat rule — never a guess. Upgrade path if ever needed: a Bravo sold report with the age
  spinner (the AgedJewelrySales handler already knows how to set it).
- **Discount allowance by age** (defaults, Joshua's direction 9/28): ≤30 days 10% · 31–60 15% · 61–90 20% ·
  91–180 30% · 181–365 40% · 365+ 50%. Flag = more off than allowed and ≥$5 off. P&P §05.03 still
  applies (30% store cap, 50% hard limit; the approver for 30–50% is open item J18).
- **Guns never comp against non-gun sales.** Root cause of "SIG P320 $460 → fair ~$22": the shared token
  index matched "9MM"/"P320" to magazine and ammo sales.
- **True Gun Value is not automated.** Its Terms of Service allow personal, non-commercial viewing only.
  Its numbers come from GunBroker completed auctions, which GunBroker licenses through its API — that is
  the automated source. Staff can still look a gun up on True Gun Value by hand.

## Backtests (2026-09-28)

- Item age: VP40 (CUL) 94.5% within 14 days (n=218) · VA50 (HAR) 89% (139) · VAP5 (WAY) 97% (88) ·
  ROA4 (ROA) 98% (198) · VA10 (LEX) 96% (45). 94% of recent sold items get an age.
- Gun values (Aug–Sep 2026 gun sales, each day excluded from its own comps): coverage 73% of 155 sales;
  model-level comps median error 17% (75% within 25%); brand-level median 27%. Old engine: SIG P320 $460 →
  $22, Glenfield 30-30 $600 → $35, Savage Axis $300 → $30, Tisas 1911 $404 → $60.
- Discount review, same days, old vs new flags: 9/26 29 → 30, 9/24 41 → 30. New flags are the fresh items
  discounted past their allowance (e.g. 35% off a 0-day-old item) instead of aged items that were meant
  to move.

## Wiring (all edits backed up as `*.bak-pre-age-20260928` / `*.bak-pre-gunvalue-20260928`)

- `Discount Outlier Review/run_daily_discount_review.py` — `_age_judge()` in `compute_discount`; header line,
  "avg discount by how long the item sat" line, age on each heavy-discount line; Excel columns Days Old /
  Age Band / OK Discount %.
- `Sold Margin Review/fair_value.py` — firearms routed to `gun_value` before the generic index.
- `Sold Margin Review/run_daily_sold_review.py` — `_fill_age()` fills days-on-shelf so the aged-clearance tag works.
- `Pawn Walks/run_daily_intake.py` — `_gun_t2()` for firearms; brand-level gun comps are `low` confidence
  (shown, never used to flag an overpay).
- Every hook fails soft: if this folder is unreachable, each report runs exactly as before.

## Open

- GunBroker connection: see `GUNBROKER_SETUP.md` (one-time, Joshua). Until then guns use our own gun sales only.
- Env overrides for testing outside the Mac: `VP_BRAVO_OUTPUT`, `VP_VALUATION_CORE`.
