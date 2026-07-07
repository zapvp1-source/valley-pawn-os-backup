# Intake Margin Reporting — Project STATUS

> READ FIRST. Resume from here; do not restart. Additive-only (Rule #4) — no existing Bravo report,
> handler, pipeline cell, or scheduled task may be modified.

**Last updated:** 2026-06-10
**Owner:** Joshua Davis
**Goal:** Daily report that grades what we take in (new pawn LOANS + BUYS from public) against an
INDEPENDENT, item-level value estimate, to catch employees over-paying at intake — target ~50% gross margin.

---

## Decisions made (do not re-ask)
- Scope: BOTH loans + buys.
- Metric: margin vs 50% target = (Est Value − Cost) / Est Value.
- Cadence: daily, on the PREVIOUS day's intake.
- Valuation must be ITEM-LEVEL (specific make/model), never category-average-only.
- Value sourced INDEPENDENTLY of our cost: metals→melt; general merch→eBay/web sold comps; guns→GunBroker/gun-value sites; internal sold-history as a cross-check.
- Employee accountability: STORE-LEVEL ONLY for now; add per-counter naming later.
- Daily metric on fresh intake = intended margin (Asking/Est Value vs Cost), plus rolling realized scorecard.

## Data reality (verified 2026-06-09, Bravo Data Extraction/output/)
- `inventory-details` (HAR/LEX/ROA, 12 mo, SOLD): Number, Status, Category, Description, **Cost, Price, Last Sold Price**, Date. 10,055 rows. This is the realized-margin + internal-comp source.
- `buys-from-public` Ad Hoc: Ticket Number, Category, Full Description, Loan Amount(=paid). 2024 files have data; 2026 pulls were empty.
- `loan-portfolio-2026`: Ticket, Disposition, dates, Customer, Loan Amount, Age — **no category, no value field**.
- CUL & WAY have a known inventory-details pipeline gap (per Optimize Loan Portfolio STATUS).
- Spot (2026-06-09): Gold $4,350/ozt, Silver $68/ozt. Production wires to `vp-weekly-spot-price-update`.

## What's built (in /Pawn Walks/)
- `intake_margin_analysis.py` → `Intake_Margin_Scorecard_2026-06-09.xlsx` — realized-margin baseline (Cost vs Last Sold Price) by store + category. Company blended realized margin 51.4%; firearms & bullion margin worst where most capital sits.
- `intake_valuation_engine.py` → `Intake_Valuation_ItemLevel_2026-06-09.xlsx` — item-level engine:
  - Tier 1 MELT (gold/silver): parse DWT/oz + karat × spot. Exact.
  - Tier 2 COMP: match to our SOLD items by **model-number token** (brand-only matches NOT trusted).
  - Routing: precious metals never token-comp (→ melt or PM-NEEDS-WEIGHT).
  - Proven on 6,695 real buy records: ~51% valued high-confidence from internal data alone.

## KEY FINDING (2026-06-09) — Tier 3 is required for credible flags
Spot-checked internal "overpay" flags vs WebSearch market value: ALL were false positives (internal
UNDER-stated value on thin-history / high-end items). Springfield Prodigy, Milwaukee 2922-20 press tool,
Browning BPS, Meze Elite all priced well by the store. Internal-only flags are NOT safe to act on for
non-metal, thin-history items. **WebSearch per-model (cached) is viable and necessary.** No eBay sold-comp
MCP connector exists; use WebSearch (gun-value sites for firearms).

## eBay API asset (noted 2026-06-09, per Joshua)
- Existing program: `~/Documents/valley-pawn/ebay_weekly_rankings.py` + LaunchAgent `com.valleypawn.ebay-weekly-rankings.plist`.
- Uses a PRODUCTION eBay developer app (App ID / Cert ID / Dev ID) + 5 per-store user tokens; currently pulls OUR OWN orders via the legacy Trading API (GetOrders).
- Tier-3 implication: we already hold production eBay app creds → use the modern Browse API (app-OAuth) for live market prices, and check if the app is approved for Marketplace Insights API (true SOLD comps, last 90 days = best source). Do NOT reuse the store user-tokens for comps; mint an app-level OAuth token from the App/Cert ID. (Secrets stay in the script; never echo them.)

## eBay API VERIFIED (2026-06-09, ebay_value_probe.py)
- App-level OAuth (client_credentials, App/Cert ID from ebay_weekly_rankings.py) WORKS — 7200s tokens.
- Browse API (active listings) WORKS but NOISY: needs title model-match + outlier trim (saw a $992k junk listing; accessory contamination). Usable for general merch/electronics/tools.
- FIREARMS: eBay useless (gun sales banned → only holsters/mags return). Route guns to gun-value sites via WebSearch (TrueGunValue/Blue Book/GunBroker) — confirmed good.
- Marketplace Insights (true SOLD, 90d): app NOT subscribed — requesting the buy.marketplace.insights scope returns invalid_scope (definitive). To get true eBay sold comps, APPLY for Marketplace Insights API access in the eBay developer portal for app FullCirc-ValleyPa-PRD. Once approved, engine swaps active→sold with one scope change.
- Joshua's priority: SOLD comps >> active listings. Interim sold-first sources: gun-value sites (reflect real sold), our own realized sales (internal item-level comps), and eBay Browse active prices with a ~10-15% sold-haircut + outlier trim for general merch until Insights is approved.
- Tier-3 routing CONFIRMED: metals→melt; general merch→eBay Browse(filtered); firearms→gun-value sites.

## Daily output destination (Joshua 2026-06-09)
- Slack channel **#pawn-walks** = `C0B8WR95N31` (PRIVATE). Confirmed postable by the integration.

## Tier 3 BUILT + TESTED (2026-06-09)

### Files added (additive only — no existing files modified):
- `tier3_valuation.py` — Tier 3 module; `get_tier3_value(desc, cat, cost)` → `{value, source, confidence, range_low, range_high}`
- `tier3_cache.json` — value cache: 7-day TTL (general merch), 30-day (firearms)
- `run_tier3_test.py` — test harness; runs 50 low-confidence items from existing buy records

### Routing implemented:
- PRECIOUS METALS → passthrough (Tier 1 handles; Tier 3 not called)
- FIREARMS (cat or desc match) → DuckDuckGo lite (Webkit UA — Chrome UA causes empty results) broad query: `{make model} used value price` + fallback `{make model} gun value blue book used`
- GENERAL MERCH → eBay Browse API (app-level OAuth from existing creds), model-key matching + PARTS filter + 10%/90% outlier trim + 0.88 sold haircut

### Known issues fixed during build:
- Chrome UA on DDG lite returns 14k-char blank form page (no prices); Webkit UA returns 24k-char results. Fixed in `_ddg_fetch`.
- `_build_gun_query` preserves hyphens (Security-9, DDM4-V7) by splitting on `[,./\s]+` not `[^A-Z0-9 ]`.
- Cache must NOT persist failed lookups across long periods; `_clear_gun_cache.py` strips entries where `value=None` if needed.

### Test results — `Intake_Valuation_Tier3_Test_2026-06-09.xlsx` (50 items):
- **Hit rate: 20/50 (40%)** — 12 high, 8 medium confidence; 30 none
- **Guns: 5/15 hit** — common modern models (Python, DDM4, MKAP5, PS90) return prices; rare/older models (Trooper, Vaquero, Dan Wesson 15) return no DDG prices (expected)
- **General merch: 15/35 hit** — items without model-number tokens (guitars by name, cameras, some laptops) return no-model-token
- **Flagged overpay:** Husqvarna YTH22V46 lawn tractor ($450 paid vs $22 T3 est) — suspect eBay match (review: may be parts listings); only 1 genuine overpay from T3
- **9 below 50% target** at medium/high confidence
- **Blended margin on hits:** 59.8% (paid $9,762 vs est $24,274)
- **Wide range flag:** Fender 50th Anniversary Strat and Colt HBAR II show very wide ranges ($132–$5,269; $5k flat) — single-comp thin hits; treat as directional only

### Suspected bad eBay match to investigate:
- Husqvarna YTH22V46 → $22 est (range $11–$44) — likely matching lawn tractor PARTS, not the tractor itself. Consider adding "TRACTOR" to PARTS_RE exclusion list, or requiring 2+ model-key tokens for categories like "Lawn Tractor".

### intake_valuation_engine.py change (additive):
- `USE_TIER3 = False` toggle at top of file — set True when running with network access
- Tier 3 called only for `conf in ('low','none') and not is_pm` items
- T3 source and range columns added to CSV output

## Daily scheduled task — BUILT (2026-06-10)

### Files added (additive only):
- `run_daily_intake.py` — main pipeline script:
  - Reads yesterday's `{DATE}_{STORE}_buys-from-public.csv` (falls back gracefully when `intake-detail.csv` doesn't exist yet)
  - Runs T1/T2/T3 valuation with `USE_TIER3=True` (cache-backed, no API hammering on re-runs)
  - Flags trusted items with margin < 30% (overpay risk threshold)
  - Posts per-store Slack summary to #pawn-walks (`C0B8WR95N31`) via Slack Web API
  - Saves `daily/{DATE}_intake_margin.xlsx` (3 tabs: Items, Summary, Flags) + `daily/{DATE}_intake_margin_summary.json`
  - Token resolution: env var `SLACK_BOT_TOKEN` → nearby config JSON → shell profile
  - Skip post if total items < 3; skip inactive stores
- `daily-intake-margin/SKILL.md` — scheduled task definition, fires 7:30 AM daily:
  - Pipeline-driven: no computer-use, no Parallels grant
  - Runs script via `mcp__Control_your_Mac__osascript`
  - Reads JSON summary for status/error checking
  - Falls back to `slack_send_message` MCP if Python token resolution fails
  - DMs Joshua (U03BB52MDSA) on EXIT:1, JSON not found, or any flags > 0

### To activate the scheduled task:
Create via the `schedule` skill or `create_scheduled_task` tool with:
- `taskName`: `daily-intake-margin`
- `cronExpression`: `30 7 * * *` (7:30 AM daily)
- Prompt: the self-contained SKILL.md content above

### Known limitation — buys-only until live feed:
Currently reads `buys-from-public.csv` only (what Bravo produces today). Loans are not included until the "Claude Intake Detail" Ad Hoc report is built (see step 2 below). Script will auto-prefer `intake-detail.csv` files when they exist — no code change needed.

## Next build (recommended order)
1. **eBay Marketplace Insights** — apply for API access in eBay developer portal for app `FullCirc-ValleyPa-PRD`. Once approved, flip `use_insights=True` in `_ebay_value`; one scope change eliminates the sold-haircut approximation.
2. **Live feed** — NEW additive Bravo "Claude Intake Detail" Ad Hoc report (date, store, ticket, category, full description, amount) for loans + buys → new handler (clone) → new pipeline cell `intake-detail`. Needs computer-use Bravo session.
3. **Tractor/large-equipment fix** — add "MOWER|TRACTOR|RIDING" category check to require title to contain a non-parts word, or add to PARTS_RE.
4. **Later** — add employee field; repair CUL/WAY inventory-details gap for full 5-store coverage.

## Hard rules carried
Additive only; never modify existing saved Bravo reports/handlers/cells or production scheduled tasks.

---

## UPDATE 2026-06-11 — Producer gap closed + eBay status

PRODUCER: The full daily pipeline already existed (run_daily_intake.py + tier3_valuation.py + tier3_cache.json + `daily-intake-margin` task, enabled, 7:34 AM). Gap: nothing produced yesterday's buys CSVs -> reported no-activity daily. FIX (additive): new scheduled task `daily-intake-prestage` (6:36 AM daily) drops a buys-from-public trigger for yesterday (single-day range Y..Y, all 5 stores). Output `<Y>_to_<Y>_<STORE>_buys-from-public.csv` matches the consumer glob (verified). Modifies nothing; DMs Joshua on pipeline failure. STILL TO VALIDATE: first live run needs Bravo watcher up + store login (bravo-store-cycle).

EBAY all-eBay SOLD: path = Application Growth Check, but developer support contact is INACTIVE. Joshua must activate it (Profile & Contacts -> Edit Primary Contact -> Save -> Activate Support), then the Marketplace Insights request can be filed (justification drafted; app FullCirc-ValleyPa-PRD; eBay reviews, not instant). Until then T3 general-merch uses eBay Browse active + haircut.

---

## UPDATE 2026-06-11 (PM) — Slack posting fixed + GLOBAL RULE

**GLOBAL RULE (Joshua):** NEVER post a failure/error message to ANY Slack channel — applies to every Valley Pawn task/script. Channels get success summaries only; ALL failures DM Joshua (U03BB52MDSA). Saved to persistent memory.

**Slack fix:** No bot token exists anywhere on the Mac → `token_not_found` is EXPECTED, not a bug. Fix (additive): `run_daily_intake.py` now saves the formatted message into the JSON as `slack_message`; the scheduled task posts it verbatim via the Slack MCP (`slack_send_message`) — this MCP fallback is now the PRIMARY posting path. Live `daily-intake-margin` task prompt + project SKILL.md both updated: failure-post-to-channel removed (was "⚠️ script failed → #pawn-walks"), all failures DM-only. `daily-intake-prestage` was already compliant.

**Verified end-to-end:** re-ran 2026-06-04 → EXIT:0, slack_message in JSON, posted to #pawn-walks via MCP (WAY 86 items, 57% avg margin, 4 flags). NOTE: that "6/4" data is actually the 7-day WAY test pull (6/4–6/10) — the `2026-06-04_to_2026-06-10` filename matches the 6/4 glob. Future daily runs use single-day prestage files (Y..Y), no collision.

**Confirmed working:** IntakeDetail.ahk handler + "Claude Pawn Walks" saved report (loans+buys) registered in pipeline; consumer auto-prefers intake-detail CSVs over buys-from-public; foreground keeper installed + running (startup shortcut). First fully-automatic live run: tomorrow 6:36 AM prestage → 7:34 AM consumer.

**Still open:** eBay Marketplace Insights (blocked on Joshua activating dev support contact); tractor/parts filter fix; CUL/WAY inventory-details gap.

