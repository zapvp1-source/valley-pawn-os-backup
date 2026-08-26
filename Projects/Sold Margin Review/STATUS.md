# Sold Margin Review — Project STATUS

## 2026-08-16 — morning run failed 5/5 stores; recovered + posted same day; queue hardening shipped

The 7:50 run and the 8:34 retry both failed every store on the Bravo saved-report dropdown, and the retry hung the AHK mid-HAR. ROOT CAUSE (confirmed in logs): Bravo was stranded several dialogs deep (stacked report screens) — in that state the dropdown never populates, so retries without a recovery could never work. Once the health-gate recovery cleared the stack (~09:16), the identical selection code worked first try on all 5 stores; the retry2 trigger that looked unclaimed was actually just queued behind a concurrent discount-review retry (the watcher is serial). All 5 sold-discount-detail CSVs for 2026-08-15 landed by 09:49 and were content-verified (CUL 27 / HAR 33 / LEX 13 / ROA 19 / WAY 47 rows, all dated 8/15). Fair-value sweep (quota already at 60/60, 1 eligible item skipped), compile (138 items, avg margin 54%, 8 flags, 0 critical, no missing stores), the verbatim #sold-review post, the flags DM, and the quota DM all completed ~12:15. Terapeak/browser enrichment intentionally skipped for the recovery run.

**Hardening shipped (additive, in Bravo Data Extraction):** `_cleanup_stale_claims.ps1` (moves claimed triggers >90 min old with no matching result into `triggers/failed/` — first sweep quarantined 95 orphans, nothing deleted) and `_restart_watcher_v2.ps1` (sweep + unmodified original restart + 60-second watcher liveness verification + queue-depth log to `logs/_restart_watcher_v2.log`). Escalation ladder appended to `Scheduled/BRAVO_KNOWN_ISSUES.md`: an all-stores dropdown failure means recover/relaunch Bravo FIRST via the health gate — never raw retries — and check whether another trigger's log is advancing before declaring the watcher dead. Still open (logged in Life OS OPEN_ITEMS_REGISTER): root cause of the two mid-HAR AHK hangs, and WAY grid-walk truncation flakiness (40/47 twice, complete on 3rd try).

## 2026-08-15 — first full live run: data perfect, post killed by an interruption (FIXED)

The 7:45 run completed everything — 5-store pull, compile (75 items, 4 flags), STEP 4.8
API sweep (60/60 quota, 65/75 fair-valued) — then opened Chrome for the Terapeak browser
step and was **manually interrupted** (browser moving on Joshua's screen). Everything
after the interruption died, INCLUDING the Slack post. A complete report sat on disk at
08:05 and never published. Joshua noticed and asked; posted manually ~11 AM.

**Fixes shipped same morning:**
1. **Step order:** the browser step now runs LAST (renamed STEP 6b), after the post and
   the DMs. It only feeds tomorrow's cache; interrupting it is now harmless. SKILL.md
   fully rebuilt (an earlier sed-style patch spliced at the wrong "STEP 5b" occurrence
   and scrambled section order — mangled version kept at `SKILL.md.mangled-backup-2026-08-15`;
   current file verified: frontmatter + 0→0.5→1→1.5→2→3→4→4b→4c→4.8→5→6→7→6b).
2. **Console contamination, BOTH directions:** a $450 PS5 drew "fair ~$37" — externally
   from used-listing games/controllers, and INTERNALLY because model-key "PS5" matches
   every game title containing PS5. `AMBIGUOUS_RE` broadened (searches anywhere, covers
   PlayStation/Xbox/Switch/Wii); ambiguous items skip external AND skip the internal
   model tier, resolving via brand+category (console category separates games). PS5 now
   fair ~$332. Health log purged of pre-fix pairs.
3. Lesson for the register: an interrupted scheduled session sends NO failure DM — the
   DM logic lives inside the session that was killed. Silence + no post = check
   `daily/<date>_sold_review_summary.json` (compile writes it BEFORE any Slack step).


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

## STATUS AS OF 2026-08-14 — LIVE, HARDENED, PROVEN

`sold-review` is registered as a real local scheduled task (`45 7 * * *`, ~7:45 AM ET) and has
been publishing to `#sold-review`. The data source has changed twice since the original 2026-07-23
build — read the History section below before touching anything. The current state:

- **Data source:** `sold-discount-detail` cell / `reports/SoldDiscountDetail.ahk` handler, saved
  report **"Claude Sold Inv Details"** (Inventory → Custom Reports). Shared with the sibling task
  `discount-review` — whichever task's trigger completes first, the other reuses the same CSVs
  (REUSE-FIRST check, STEP 1.5 in both SKILL.md files) instead of dropping a second identical
  5-store pull.
- **Compile script:** `run_daily_sold_review.py` — margin = (Last Sold Price − Cost) / Last Sold
  Price, using the actual realized sale price, not the ticketed "Price." Target margin 50%, flag
  <25%, critical sub-flag for at-or-below-cost sales, "(aged clearance)" annotation at 90+ days on
  shelf (not suppressed).
- **Open-stores gate:** built into both the SKILL.md (STEP 0.5) and the compile script itself
  (`open_stores_for()`) — Sunday is a full no-op (all 5 closed), Wednesday pulls CUL only, every
  other day pulls all 5. Closed stores are never reported as "missing" — they're excluded from the
  store list entirely so a closed Wednesday doesn't look like 4 failed stores.
- **Scheduled task registration:** `/Users/joshuadavis/Documents/Claude/Scheduled/sold-review/SKILL.md`
  — confirmed current (read directly 2026-08-14): correct cell name, correct compile script path,
  correct Slack channel, REUSE-FIRST step present, open-stores gate present, failure-DM policy
  correct. Sibling `discount-review` registration cross-checked the same day and is consistent
  (same cell, same REUSE-FIRST pattern, posts to its own `#discount-review` channel).

## FAIR VALUE v2 — precision-weighted blend (built 2026-08-14, per BLEND_V2_PLAN.md)

**All 4 phases SHIPPED and verified against real output the same session.** The plan file
(`BLEND_V2_PLAN.md`) is the design record; this is the build record.

**The split that fixed the design:** ONE question was doing two jobs. The FLAG FLOOR
("bad enough to alert?") stays with `market_benchmark.py` — conservative, lower-of,
3.3% flag rate, **completely untouched**. FAIR VALUE ("what SHOULD it have sold for?")
is new: `fair_value.py`. The daily report now carries both.

**What shipped, by phase:**
1. **Coverage (no 8-item cap):** `fair_value.py --lookup-all <date>` sweeps EVERY sold
   item, highest sale value first — melt for precious metals (live spot via Pawn Walks
   `intake_valuation_engine.melt_value`), internal-only for firearms, SoldComps API
   (condition=used, model-key then brand+category fallback) for everything else. Quota
   guard lives INSIDE `soldcomps.fetch_comp` (60/day hard ceiling, `.soldcomps_usage.json`,
   shared by every caller; degraded misses are NEVER cached). Wired into the live task as
   STEP 4.8. **KEY RECEIVED AND LIVE 2026-08-14** — `--test` passes, full sweep of the
   2026-08-13 sold day completed (56 API requests, 36 keywords cached: 20 comps + 16
   honest misses). ⚠️ Ops note: `--lookup-all` outruns osascript's ~2-min timeout — the
   process KEEPS RUNNING after the tool call "errors"; do NOT re-invoke (two concurrent
   sweeps double-burn quota; happened once, caught at 56/60). Background with nohup and
   poll, and check `.soldcomps_usage.json` + `terapeak.py --stats` before any retry.
   **Two accuracy fixes proven by the first live sweep (same day):**
   - `soldcomps.py`: self-test queried condition=any and the parts regex missed
     mufflers/throttle parts → STIHL BG 50 came back $32.54. Fixed: used-condition
     self-test, additive `EXTRA_PARTS_RE`, and a cohort-relative price floor (drop
     anything under 20% of p75 when n≥6). Result: $114.99 (n=11 real blowers) —
     in-ballpark of Terapeak's $195 (n=6, skewed high). Terapeak fixture still passes.
   - `fair_value.keyword_ok()`: generic descriptions bought confidently wrong comps
     ("MISC TOOLS"→$17.66, "APPLE IPAD PRO" all-generations→$341, "NINTENDO SWITCH"
     games-contaminated→$39.50). External lookups now require a model key or a
     non-generic brand + qualifier; failures stay internal-only. Six junk pairs purged
     from pricing_health.jsonl; disputes on the test day went 16 → 10, all defensible.
2. **The blend:** time-decayed internal comps (half-life 182d electronics/tools, 365d
   else, weighted median + weighted IQR) blended with channel-normalized eBay
   (`net = gross×(1−fee) − ship_absorb(category)`) by precision weight `n/(1+cv)` — no
   hardcoded 65/35, no lower-of. Output is `fair ± band`. Disagreement >30% AFTER
   normalization is NOT averaged: point goes to the higher-precision source, marked
   DISPUTED, both numbers surfaced, pair logged. Verified on the canonical case:
   STIHL BG 50 → int $104 (n_raw 46) vs eBay-net $155 (from $195 gross) = 32% apart →
   disputed, exactly as designed. In the report: Excel cols L-N (Fair Value, ±Band,
   Sale vs Fair), flag lines in Slack get `fair ~$X ±$Y`.
3. **Pricing health (the money finding):** every internal+external pair accumulates to
   `pricing_health.jsonl`; `--health` / the Slack section aggregate per-category
   "our prices vs eBay net", gated at n≥30 per category so it never publishes noise.
   Silent for the first weeks BY DESIGN while pairs accumulate.
4. **Validation + calibration:** `--validate` backtests internal-only vs ebay-net vs
   blend-v2 vs old lower-of (MAPE), appends to `validation_history.jsonl`. First run:
   40 items but only 1 had an external comp (cache is nearly empty pre-key) — MAPE
   numbers are not yet meaningful; re-read after ~2 weeks of API volume. Success
   criterion stands: blend beats both single sources within 4 weeks or the weighting
   gets revisited publicly. **Fee calibration is DONE and real:** `calibrate_fees.py`
   measured 260 of our own transactions across all 5 stores via GetSellerTransactions
   ($40,728 gross, $5,663 fees) → **fee_rate 13.9%** (store range 13.5–14.3%), 62.7%
   free-shipping share, persisted to `.channel_calibration.json` which `fair_value.py`
   auto-prefers. The 13% guess lasted one day.

**Live compile verified (2026-08-13 data), post-key:** 42 items, flags unchanged (2),
**fair value on 34/42** (remaining 8: no internal history AND no defensible external —
honest no-opinion, mostly generic/one-off descriptions), 10 disputes logged to pricing
health, canary OK. Early dispute read: internal realized prices sit WELL below eBay-net
on STIHL ($104 vs $155), HP OMEN laptop ($190 vs $1,202 — thin internal comp, treat
carefully), Pokémon DS games ($5 vs $28) — and ABOVE eBay-net on DEWALT/Michael Kors/
TI calculators. The n≥30-per-category gate decides when any of this is publishable.

**Files:** `fair_value.py` (engine+CLI), `calibrate_fees.py`, `.channel_calibration.json`,
`pricing_health.jsonl`, `validation_history.jsonl`, `.soldcomps_usage.json`. Modified:
`soldcomps.py` (quota guard + rate-limit retry + condition recorded), `run_daily_sold_review.py`
(attach_fair_value, Excel cols, Slack fair values + gated health section, summary JSON fields),
live `sold-review/SKILL.md` (STEP 4.8, 5b note, two STEP 7 DM rules). Untouched:
`market_benchmark.py`, `terapeak.py` fixture/canary, all flag logic, all Bravo infra.

## Coverage-gap analysis + fixes (2026-08-14, "do we care about ungraded items?")

Ungraded on the 8-13 test day: 8 items, $1,216 = 19% of revenue. Split three ways:
- **$717 coins/bullion** — melt-ruler items; ungradeable only because tickets lack coin
  COUNT/weight. Counter-habit fix (recommended to Joshua: put count in the description,
  e.g. "12X"), not a system fix. `LOT_RE` already parses "12X" if they write it.
- **~$400 niche-brand gear with model numbers** (FIELDPIECE SDMN6, BLCKTEC 460T) — used-only
  90d search too thin. FIXED: widen-ladder (retry condition=any, 180d before "no opinion")
  in `fair_value.external()` + `lookup_all()`.
- **$200 garbage description** ("WESTERN DIGITAL COMPUTER ACCESSO") — ungradeable by anyone.
  Real fix is a counter description convention (brand+model on $100+ items); offered to
  Joshua as an official policy push, awaiting his word.

**Also fixed same session — quota leak:** `terapeak.get()` filters value-less entries, so
cached MISSES were invisible → known-dud keywords were re-fetched (re-billed) daily. Added
`terapeak.get_any()` (additive); `soldcomps.fetch_comp` now honors cached misses, except a
used-condition miss does not block the wider any-condition retry. Verified: guard tripped
at exactly 60/60 during the widen sweep and stopped cleanly; remainder runs tomorrow.

## Reporting strategy (Joshua delegated the call 2026-08-14 — this is the decision of record)

Joshua: non-technical, wants business + analysis strategy only. Chosen priorities, built
into `build_slack_message` the same day and verified on 2026-08-13 output:

1. **Big-ticket review, daily.** Every item ≥$100 gets a verdict vs fair value
   (✔ got market / ▼ $X under / melt-priced / no benchmark). Rationale: on the test day
   items ≥$100 were 15 of 42 tickets but 83% of revenue AND the thinnest margins (47%
   vs 57% on small stuff). This is where counter discipline pays.
2. **Day scorecard line**: Revenue · Profit · "Left on table ~$X" (graded gaps ≥$25).
3. **Small items (<$25): NOT graded per-item** — 26% of tickets, 2% of revenue, $49
   profit on the test day. Below-cost criticals still flag. Deliberate attention budget.
4. **Category pricing health** stays the strategic payoff (n≥30 gate, unchanged).
5. **Week-in-review ticket-size mix** posts only on the Saturday report (Sunday-morning
   run) via `_week_mix()` — mix is a trend question, not a daily one.

## Market benchmark — the second flag (added 2026-08-14)

**The gap it closes.** Cost-margin alone cannot answer "did we sell it too cheap." An item
bought for $10, worth $200, sold for $60 posts an 83% margin and never flags — it reads as
a win. That was the actual blind spot. The report now carries TWO independent signals:

1. `🚨 SOLD TOO CHEAP` — realized margin below 25% of **our cost** (original).
2. `📉 SOLD BELOW WHAT WE NORMALLY GET` — sale below what that item **typically brings**.

**How the benchmark is built** (`market_benchmark.py`, same folder):
- Internal comp index from ~29,400 of our own SOLD rows — the 12-month `inventory-details`
  export (HAR/LEX/ROA only; CUL/WAY were never exported — known gap) PLUS every daily
  `sold-discount-detail` CSV, so coverage and freshness improve automatically over time
  with no new export needed. Pooled across stores on purpose: "what does Valley Pawn get
  for this item" is not store-specific.
- Three matching tiers, best-first: **model** (digit-bearing token, e.g. `MS170`) →
  **brand-cat** (`STIHL` + `Leaf Blower`) → **category percentile**. The tier is carried
  through to the output so a thin comp reads as thin instead of as authority.
- Optional eBay corroboration via `Pawn Walks/tier3_valuation.py` (`use_external=True`).
  Currently OFF by default in the daily run — internal comps alone give 95% coverage, and
  eBay's number is active-listing × 0.88, not a true sold comp (see the eBay note below).
- **Blend leans conservative.** When internal and external agree within 25% they blend
  65/35 toward internal; when they disagree materially it takes the LOWER. Rationale: on
  the sold side an inflated benchmark manufactures false "you sold too cheap" alarms, and
  a report that cries wolf gets ignored and then protects nothing. Under-flagging costs
  one missed item; over-flagging costs the report's credibility.

**Calibrated against real data, not assumed.** Backtest (`python3 market_benchmark.py`)
runs the rule over past sold days and reports the flag rate, because flag rate is the only
thing that determines whether this is publishable. Tuning history:
- v1 (model-match only): **13% coverage** — too silent to be useful.
- v2 (added brand-cat + category): 95% coverage, 4.9% flag rate — but produced a false
  positive: an INDIO budget guitar at $76 flagged against a $170 **median** of 186 guitars
  spanning budget to premium. The median is a bad benchmark for a category with wide price
  dispersion.
- v3 (current): category tier uses the **25th percentile** as "floor of normal" rather than
  the median, plus a `MIN_GAP_DOLLARS = 25` absolute floor (v1 had flagged a SPRINGFIELD
  XD9 at $11.40 vs $16.62 — technically 69% of benchmark, $5 of real exposure, pure noise).
  Result: **95% coverage, 3.3% flag rate (2 of 61)**, both flags defensible.

Live 2026-08-13 output: `TRAXXAS TRX4M $100 vs $170 typical (n=4)` and `STIHL BG 50 blower
$40 vs $104 typical (n=45)`. The STIHL one is the strongest kind of signal this produces —
45 of our own sales behind it.

**Tunables** (top of `market_benchmark.py`): `FLOOR_RATIO` 0.70, `MIN_GAP_DOLLARS` 25,
`CATEGORY_PCTL` 25, `CATEGORY_FLOOR_RATIO` 0.75, `MIN_CATEGORY_N` 12. Re-run the backtest
after changing any of them — target an actionable flag rate (~2-5%), not a principled-
sounding number.

**Fails soft by design.** If the benchmark engine can't load, `attach_market()` logs a
warning and the margin report still goes out. This is an added signal, never a new single
point of failure for a report that already works.

**Known small gap:** STEP 7's flag DM in the scheduled task still counts only margin flags,
not market flags. The channel post (the main deliverable) carries both. Worth tidying.

## ✅ TRUE eBay SOLD DATA IS ACCESSIBLE — via Terapeak (proven live 2026-08-14)

Joshua's challenge was correct and is the reason this section exists: **an internal-only
benchmark is self-serving.** "We normally get $104 for this" answers "is this sale unusual
for us," NOT "is this the right price." If our counter systematically underprices, an
internal benchmark just certifies our own bad pricing as normal. Real market data is required.

**The route that works: Terapeak Product Research.** Free to every eBay seller with Seller
Hub — no store subscription, no API approval, no partner status. Up to 3 years of real
completed sales. This is the same sold data Marketplace Insights gates behind partner-only
approval, available to us through the seller UI because we ARE a seller.

Proven end-to-end 2026-08-14 in Chrome (logged in as `valley_pawn_lexington`, saved creds):
- **URL-driven queries work** — no clicking needed:
  `https://www.ebay.com/sh/research?marketplace=EBAY-US&keywords=<KW>&dayRange=90&categoryId=0&offset=0&limit=50&sorting=-itemsold&tabName=SOLD`
- **`get_page_text` extracts everything** after ~3s render: headline stats (avg sold price,
  sold price range, avg shipping, total sellers) AND every individual sold listing with
  title, sold price, shipping, units sold, and date last sold. Fully automatable.

### ⚠️ THE TRAP — do NOT use Terapeak's headline "Avg sold price"
Live proof, STIHL BG 50 leaf blower, last 30 days: headline **avg sold $61.84**, range
$6.95–$299.99. That average is contaminated by parts and accessories:

| Sold | Item |
|---|---|
| $14.95 | BG 50 gas cap |
| $13.79 | primer bulb |
| $43.00 | carburetor |
| $42.95 | flywheel |
| $6.95 | throttle trigger linkage |

The **complete blowers** in the same result set sold for **$125.99, $190.00, $199.99,
$209.95**. So the true market for the actual item is ~$126–210, not $62. Using the headline
number would have understated market by ~2-3x — the identical failure mode as the
`Husqvarna YTH22V46 → $22` bad match already logged in `Pawn Walks/STATUS.md`.

**Correct implementation:** parse the per-listing rows, apply a parts/accessory exclusion
(`PARTS_RE` already exists in `Pawn Walks/tier3_valuation.py` — reuse it, don't rewrite),
then take a median of the surviving complete-item sales. Never consume the summary stat.

**What this did to the live example:** internal comp said $104 typical; filtered real eBay
sold says $126+; the item sold for $40. Both benchmarks agree the sale was genuinely too
cheap — and the raw $61.84 average was the ONLY misleading figure in the whole picture.

### Build state
**DONE (2026-08-14):**
1. ✅ `terapeak.py` — `research_url(kw)` builds the URL-driven query; `parse_page(text)`
   parses per-listing rows, drops parts via a broad `PARTS_RE`, normalises multi-packs to
   per-unit, trims extremes, returns `{value, n, n_raw, low, high, headline_avg, excluded}`.
   30-day cache (`terapeak_cache.json`), atomic write, caches misses too so we don't retry
   a dud keyword daily.
   **Validated against the real page** (fixture: `test_fixtures/terapeak_stihl_bg50.txt`):
   14 rows → 8 excluded as parts → **median $195.00** (range $125.99–$249.85) vs Terapeak's
   headline **$61.84**. A +215% correction. This fixture is the regression test — if eBay
   changes their DOM, `parse_page` on this fixture must still return ~$195.
2. ✅ Wired into `market_benchmark.py` as the EXTERNAL source, preferred over the legacy
   Browse-API path. Blend logic unchanged. **Terapeak lookups always run** (free local cache
   read); `use_external` now gates only the legacy live-network Browse calls.
3. ✅ `terapeak_keywords()` maps a Bravo description to eBay search phrases, most specific
   first — `STIHL LEAF BLOWER BG 50` → `STIHL BG 50` (Bravo filler hurts match rate).
4. ✅ Report shows the eBay figure alongside ours when they differ >20%. Live output:
   `HAR · $40 sale · $104 typical · eBay sold ~$195 · −$64 · STIHL LEAF BLOWER BG 50`

5. ✅ **STEP 5b shipped in the live `sold-review` task (2026-08-14)** — the daily run now
   fills the cache itself: `market_benchmark.py --candidates <date>` prints up to 8
   `<keyword>\t<url>` lines (prioritised by SALE VALUE so a $400 item gets researched before
   a $9 one; already excludes precious metals, firearms, and anything cached fresh), Claude
   navigates each, waits ~4s, `get_page_text`, saves to `.terapeak_tmp.txt`, then
   `terapeak.py --ingest "<KW>" .terapeak_tmp.txt`. Compile then re-runs so the new comps
   blend in. Capped at 8 lookups/run to keep browser cost low; misses are cached too so a
   dud keyword isn't retried daily. Skipped entirely when `missing_stores` is non-empty
   (the report won't post anyway — don't waste the round-trips).
6. ✅ **FIREARMS EXCLUDED from Terapeak** (`FIREARM_RE`). Caught when the first candidate
   list surfaced GLOCK 19 / PHOENIX HP22A / HOLOSUN scope. eBay PROHIBITS firearm sales, so
   searching 'GLOCK 19' returns holsters, magazines and sights — a $500 pistol would be
   benchmarked against $30 of accessories and every legitimate gun sale would flag as "sold
   too cheap". This is the parts-contamination bug in its worst form. Internal comps still
   cover firearms fine (we sell plenty); `tier3_valuation.py` routes them to gun-value sites
   on the intake side. Exclusion is Terapeak-only, applied in both `candidates()` and
   `external()`.
7. ✅ STEP 7's flag DM now counts BOTH margin flags and market flags (was margin-only).

**Verified state 2026-08-14:** 42 items / 5 stores compile clean, 39/42 benchmarked,
2 flagged below market. Backtest across both available sold dates: 95% coverage, 3.3% flag
rate. Fixture regression passes (`parse_page` → $195.00).

### ⚠️ STRATEGIC FINDING — read this, it is bigger than the tooling
On the one item with both benchmarks, **our own realized price ($104, n=45) is ~46% BELOW
the real eBay sold market ($195)**. One item is not a trend, but it is the exact pattern
Joshua predicted when he rejected an internal-only benchmark: *if we systematically
underprice, our own history certifies that underpricing as "normal."* The conservative
blend (take the lower) means the FLAG still uses $104 — deliberately, to avoid false
alarms — but the report now surfaces the eBay number so the gap is visible.
**Worth investigating across categories once the cache has real volume:** if in-store
prices sit well under eBay sold on a whole category, that is a pricing-policy finding, not
a per-item one, and it is worth more than any individual flag this report will ever raise.

**Fragility note (be honest about this):** this is browser automation against a UI, not an
API. It will break when eBay changes the page. Cache hard, fail soft (fall back to
internal-only — the report must still go out), and treat a Terapeak miss as "no external
opinion," never as a zero.

## eBay / external market — API routes (2026-08-14, all verified CLOSED)
- `tier3_valuation.py` has a live, working eBay Browse OAuth integration (app
  `FullCirc-ValleyPa-PRD`) — real, running daily on the buy side.
- It queries **ACTIVE listings**, not sold comps, then applies `SOLD_HAIRCUT = 0.88` to
  approximate a sold price. That constant is a guess, not a measurement.
- **True sold comps (Marketplace Insights) are likely a dead end.** eBay now documents it
  as "restricted and not open to new users," and mid-2026 reports are of non-major-partners
  being denied. Do not build a roadmap around approval.
- Better unexploited path: `~/Documents/valley-pawn/ebay_weekly_rankings.py` already pulls
  **our own eBay orders** (real sold prices) via the Trading API. Calibrating the 0.88
  haircut against that would replace a guess with a measurement, no approval required.

## History (data-source evolution — read before re-deriving any of this)

1. **2026-07-23 — original build.** `sold-yesterday` cell / `SoldYesterday.ahk` handler / "Claude
   Sold Yesterday" saved report. Never proven live before this session.
2. **2026-08-13 morning — first live smoke test failed 0/5.** CUL failed 3/3 attempts to even
   select "Claude Sold Yesterday" via UIA (the saved report may not actually exist under that exact
   name/module). Rebuilt same day onto `jewelry-margin-sold` / `JewelrySoldMargin.ahk` / "Claude
   Sold Inv Details" — an existing, already-proven cell that carries every column this task needs
   (Cost, Last Sold Price, Ticket, Date, Days On Shelf).
3. **2026-08-13 — `jewelry-margin-sold` found to have two real data-integrity bugs** (caught by a
   parallel session's deeper validation, not by log-line "SUCCESS" text, which was misleading):
   (a) a zero-sale day wrote NO csv at all, so a genuinely quiet store was indistinguishable on disk
   from "never ran"; (b) the grid-capture could latch onto the wrong on-screen grid entirely —
   proven on WAY, which wrote its own Global Access store-picker table (`DisplayCode,Store`) to disk
   as if it were sold-item rows. This is the reason "SUCCESS" in a log is not sufficient evidence of
   correctness — see Rule #12 (no diagnosis from metadata, verify the actual output).
4. **2026-08-13 evening — rebuilt again onto `sold-discount-detail` / `SoldDiscountDetail.ahk`.**
   Strictly additive clone of `jewelry-margin-sold` with both bugs fixed: writes a header-only CSV
   on a zero-sale day (so "ran, no sales" is distinguishable from "never ran"), and validates grid
   identity before trusting captured rows. Verified live on all 5 stores 2026-08-13. This is the
   current, correct data source. **Do not switch this task back to `jewelry-margin-sold` or
   `sold-yesterday`** — both are left untouched on disk (additive-only) but are known-inferior.
5. **2026-08-13 evening — REUSE-FIRST added** so `sold-review` and `discount-review` (which need
   the identical daily pull) don't each independently drop a full 5-store trigger ~30-40 min apart.
   Whichever runs first pulls; the other reads the same CSVs.
6. **2026-08-14 07:49 AM ET — first live run under full hardening.** Result: HAR/LEX/ROA/WAY
   succeeded; **CUL failed** — all 3 UIA select-strategies (type-ahead, keyboard-walk, page-by-page)
   failed to select "Claude Sold Inv Details" from the Inventory Custom Reports saved-report
   dropdown, 3 attempts each, before the handler gave up and moved on (see Known Issues below). This
   is a NEW failure mode, distinct from the two 2026-08-13 bugs — the report-select routine itself,
   not the data captured after selection.

## Known Issues (open, as of 2026-08-14)

- **FIXED same day: STEP 6 Slack-post logic silently swallowed a real report.** The compile
  script's own direct-HTTP Slack post (`slack_post()` in `run_daily_sold_review.py`) has never had
  a working `SLACK_BOT_TOKEN` on this host (checked env var, `slack_config.json` in three candidate
  locations, and shell profiles — none exist), so every run sets `slack_skipped=true` +
  `slack_error="token_not_found"`, even when `slack_message` is fully composed with real data. The
  live scheduled task's old STEP 6 wording read `slack_skipped=true` as sufficient reason alone to
  skip posting — so the 2026-08-14 07:49 AM run (29 items, 1 flag, CUL missing) compiled correctly
  but never reached #sold-review. Caught ~20 min later during this hardening session; posted
  manually, and STEP 6 in both `sold-review`'s and `discount-review`'s live SKILL.md registrations
  was corrected: the only real "nothing to post" conditions are now an `info` field or a null
  `slack_message` — `slack_skipped`/`slack_error` are no longer treated as a skip signal on their
  own. `discount-review` uses the same compile-script pattern and almost certainly has the identical
  gap; unconfirmed until its own next live run, flagged in its SKILL.md accordingly. This script's
  own `_get_slack_token()` function could alternatively be fixed at the source (create one of its
  candidate config files with a real bot token) rather than relying on the scheduled task to always
  post manually — worth doing if this keeps needing a workaround.

- **CUL intermittently fails to select "Claude Sold Inv Details" from the saved-report dropdown.**
  Seen 2026-08-14 07:50-07:57 AM: 3 attempts × 3 strategies (type-ahead, Alt+Down keyboard walk,
  page-by-page from End) all failed against CUL specifically, while the identical handler succeeded
  cleanly on HAR/LEX/ROA/WAY the same run. The same cell was "verified live on all 5 stores"
  2026-08-13 evening, including CUL, so this reads as intermittent (timing/render-order dependent)
  rather than a permanent CUL-specific misconfiguration — but it has now failed live once. Full
  detail in `Bravo Data Extraction/logs/sold-review-2026-08-14T07-49-34.log`. This is inside
  `SoldDiscountDetail.ahk`, a shared handler this task's own CRITICAL RULES forbid modifying
  directly — flag it for whichever session next touches that handler (same owner as the
  2026-08-13 bug fixes) rather than patching it from this project. Effect on this task: CUL shows as
  `missing_stores` for that day rather than a hard failure — the rest of the report still compiles
  and posts normally, which is the correct degraded behavior, but CUL's realized-margin numbers are
  silently absent that day. Worth 1-2 more observations before deciding whether this needs a retry
  budget bumped from 3 to 5 attempts, or a different root cause (e.g., CUL's saved-report list being
  longer/differently ordered than other stores', pushing "Claude Sold Inv Details" out of reach of
  the keyboard-walk strategy's step budget).

## Redundancy check performed (2026-07-23, still valid)
- No other scheduled task, live trigger, or project folder produces a "sold yesterday" /
  "sold-review" data feed independent of this one. `pawn-walk` (buy-side, external market estimate)
  and `monthly-sold-inventory-refresh` (monthly CFO fringe-sale analysis) are the only adjacent
  pieces of infrastructure and don't overlap in cadence, data direction, or Slack destination.
  `discount-review` (point-of-sale discounting behavior, `#discount-review`) shares this task's data
  pull as of 2026-08-13 but is a distinct signal (Price vs Last Sold Price, not Cost vs Last Sold
  Price) posted to a different channel — not redundant, by design (see both SKILL.md files).
2026-08-25 07:5x — sold-review: STEP 6b (Terapeak enrichment) skipped — Claude in Chrome extension not connected this run. Report already posted successfully in STEP 6 (missing_stores empty, 70 items, 1 flag, 8 below-market). 8 candidate keywords from market_benchmark.py --candidates were not ingested to Terapeak cache this cycle; no data loss, just fewer cached comps for tomorrow. Not a failure per SKILL.md (6b is optional/last, interruption is harmless).
