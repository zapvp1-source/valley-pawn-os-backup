# Fair-Value Blend v2 — Full Evaluation & Build Plan
**2026-08-14 · Requested by Joshua: "all items looked up, most accurate market+internal blend of what the item should have sold for"**

---

## Honest evaluation of what exists today

**What's solid (keep, don't touch):**
- Data acquisition: `sold-discount-detail` cell proven on all 5 stores; open-stores gate; REUSE-FIRST; completeness rule (never post partial); per-store retry; daily canary against a saved fixture.
- Parts filtering: proven essential (STIHL headline $61.84 vs true $195 — 8 of 14 rows were parts). One shared `PARTS_RE` across both external paths.
- SoldComps API client with correct quota handling; Terapeak browser path as fallback into the same cache.
- Internal comp index: ~29k of our own sold rows, 3-tier matching (model → brand+category → category p25), self-vouching prevented via exclude_date.

**Three places accuracy is still being lost:**

### Flaw 1 — the lower-of blend structurally discards the market signal
Current rule on disagreement: take the LOWER of internal vs eBay. If we systematically
underprice (the one item with both benchmarks says we do: $104 ours vs $195 market), the
internal number is *always* lower, so eBay *never* changes any output. The circularity
Joshua objected to survived inside the blend. Conservative was right for FLAGGING; it is
wrong for answering "what should this have sold for."

### Flaw 2 — the two sources aren't measuring the same thing (apples vs oranges)
An eBay sold price is a DIFFERENT MARKET, not just a second opinion:
- Seller nets ~87% after final value fees (~13%); free-shipping listings absorb ~$10-25 more.
- eBay reaches national demand; our counter reaches walk-in local demand.
- eBay comps mix NEW and USED; pawn inventory is essentially all used. We currently query
  condition=any, which inflates comps with new-in-box prices.
Blending a gross national new+used price against a net local used price mismeasures both.
The $195 eBay figure is really ~$160-170 net-equivalent — still well above our $104, but
the honest gap is ~55%, not ~90%.

### Flaw 3 — internal comps ignore time
The 12-month index weighs a May 2025 sale equally with last week's. Electronics depreciate
~2-4%/month; tools and jewelry are flat. A GPU's 12-month median overstates today's fair
value. No recency weighting exists.

**Also missing:** any measurement of whether the blend is actually accurate. Today the
weights (65/35, 25% agree-band) are educated guesses. Nothing validates them against
reality.

---

## The design correction: ONE question was doing two jobs

- **FAIR VALUE** — "what should this item have sold for?" → wants the most ACCURATE
  estimate. This is what Joshua asked for. New, defined below.
- **FLAG FLOOR** — "is this sale bad enough to alert on?" → wants CONSERVATIVE, to
  protect the report's credibility (3.3% flag rate, validated). Keep as-is.

The daily report shows FAIR VALUE per item; flags keep firing off the conservative floor.
Same data, two purposes, no longer conflated.

---

## Fair Value v2 — the formula

For each sold item:

1. **INTERNAL comp** = time-decayed median of our own realized prices for the match tier
   (half-life 6 months for electronics/tools, 12 months for everything else; recent sales
   dominate). Carries n and dispersion.
2. **EXTERNAL comp** = SoldComps parts-filtered median, queried with
   `itemCondition=used` (except categories where new-in-box is common pawn stock), then
   **channel-normalized to net-equivalent**:
   `ebay_net = ebay_gross × (1 − 0.13 fee) − shipping_absorbed(category)`
   (fee/shipping constants start from eBay's published schedule, then get CALIBRATED —
   see step 5 — against our own eBay store's actual orders in `ebay_weekly_rankings.py`,
   which is real gross→net data we already own.)
3. **BLEND by precision, not by policy:**
   `weight_source ∝ n_source / (1 + dispersion_source)` — a 45-sale tight internal comp
   outweighs a 6-sale scattered eBay comp, and vice versa. No hardcoded 65/35.
4. **Output an uncertainty band, not just a point:** `fair_value ± band` from the pooled
   dispersion. The report prints "$104 (±$18)" so a thin estimate LOOKS thin.
5. **Disagreement is a finding, not a nuisance:** when internal and eBay-net still
   disagree >30% after normalization, don't average them — report both and log the pair
   to the pricing-health dataset. Persistent per-category disagreement IS the
   underpricing signal.

## Pricing-health aggregate (the money finding)
Daily accumulate {category, our_price, ebay_net} pairs. Weekly (and in the daily post once
n≥30 per category): "our realized prices vs eBay net: power tools −41% (n=37), handbags
−22% (n=14)…" Gated on sample size so it never publishes confident noise. This is where
systematic underpricing becomes visible and actionable — per-item flags structurally
cannot see it.

## Coverage: every item, every store, every day
- Remove the 8-item cap. Eligibility ladder per item:
  a) Precious metals → melt (spot feed), never comped. ~7% of items.
  b) Firearms → internal comps + (existing) gun-value-site path; NEVER eBay. ~10%.
  c) Everything else → SoldComps lookup: model-key query first, brand+category query as
     fallback for no-model items ("COACH KLARE CROSSBODY" → "COACH crossbody bag" +
     category filter). Cache 30d.
- Volume: ~35-40 fresh lookups/day ≈ 1,100/mo vs 2,000 quota ($9 plan). Safety ceiling
  60/day; if quota guard trips, degrade by sale-value priority and DM once. Upgrade to
  $29/10k only if reality demands it.
- Cache compounding: repeat models stop costing requests; effective coverage rises over
  weeks while spend falls.

## Validation loop — accuracy as a measured number, not a claim
Weekly backtest (`--validate`): for every item sold this week that ALSO has ≥2 prior
internal sales, compute what each estimator (internal-only, ebay-net-only, blend-v2,
old lower-of) would have predicted, versus the realized price. Report MAPE per estimator.
The blend weights get tuned from this evidence. Success criterion: blend-v2 beats both
single sources within 4 weeks; if it doesn't, the weighting is wrong and gets revisited —
publicly, in STATUS.md, not silently.

## Build order
1. **Phase 1 (first session with the API key):** key self-test → remove cap → eligibility
   ladder → condition-matched queries → quota guard. Every item covered daily.
2. **Phase 2:** channel normalization + time-decay + precision-weighted blend + uncertainty
   band → fair value in the daily post per item.
3. **Phase 3:** pricing-health aggregate accumulation + gated weekly section.
4. **Phase 4:** validation loop + calibration of fee/shipping constants from our own eBay
   orders (`ebay_weekly_rankings.py` data — real, already flowing, sanctioned API).
5. Unchanged: completeness rule, canary, flag floor, additive-only, failure-DM policy.

## Prerequisite
SoldComps API key in `<project>/.soldcomps_key` (Joshua). Then `python3 soldcomps.py --test`.
