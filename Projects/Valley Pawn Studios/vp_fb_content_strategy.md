# Valley Pawn — FB/IG/GMP Content Strategy (Authoritative Routing + Caption + Time + Pillar Rules)

> **This is the authoritative source `vp-content-batch` Step 1 reads.** If anything in the `vp-content-batch` SKILL conflicts with this file, **this file wins.**
>
> Canonical persistent location (read this exact path on every run):
> `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn Studios/vp_fb_content_strategy.md`
>
> Rebuilt 2026-07-06 after the original was found missing (it had lived only in an ephemeral session `outputs/` folder and was lost, which is why scheduled runs could not read it). Content reconstructed from the rules embedded in the `vp-content-batch`, `valley-pawn-context`, and `vp-brand-studio` skills. Keep this file here so every scheduled run can read it.

---

## 1. Publishing platform — PUBLER ONLY (as of 2026-07-04)

All Meta Graph API publish paths are **disabled**. The "Valley Pawn Social Poster" Meta app is blocked and the brand IG account carries a suspicious-activity flag from direct browser automation on 2026-07-04. **Route ALL Meta traffic through Publer.** Never open instagram.com/facebook.com against Valley Pawn accounts; never hit developers.facebook.com/apps. If a run needs Meta insight data only the Graph API can provide, log the gap and DM Joshua — do not attempt a browser fallback.

Approved items are queued/scheduled in Publer (Facebook, Instagram, Google Business Profile, plus Twitter/X for the ≤280-char Brand variant). One composer per channel per item.

---

## 2. Routing tiers (explicit — no implicit fan-out)

Every item is tagged exactly one of `Brand` / `Store-local` / `Fan-out`, and only that tier publishes it.

| Tier | Pages | Page ID(s) |
|---|---|---|
| Brand | Valley Pawn `@thevalleypawn` | `1603970336542485` |
| Store-local | Valley Pawn-Lexington | `379605279045904` |
| Store-local | Valley Pawn-Waynesboro | `303444680270846` |
| Store-local | Valley Pawn-Harrisonburg | `795439020329931` |
| Store-local | Valley Pawn- Culpeper | `100478091680300` |
| Store-local | Valley Pawn (Roanoke) | `188243497698836` |

- Harrisonburg's correct page ID is `795439020329931`. Do **not** post Harrisonburg content to `188243497698836` (that is Roanoke). Do **not** post to legacy page `474248069342834`.
- **Fan-out** (same content to all stores) is capped at **≤2 per quarter** and requires an explicit `--allow-fanout` flag plus a documented reason in the manifest.
- **Hard rule:** the same image+caption may NEVER appear on more than one Store-local page in the same week. If two stores received the same SKU, one store runs it this week, the other next week.
- Routing conflict (item tagged both Brand and Store-local) → **Brand wins**, drop the store-local copy.
- Instagram is the single shared `@valley_pawn` account for all stores; GBP is per store.

---

## 3. Weekly footprint (default)

**3 Brand posts + 10 store-local statics (2/store) + 5 Deals-of-the-Week (1/store) + 2 Reels = 20 items.**

- Brand post count defaults to 3 (bump to ~5 for holiday-heavy weeks e.g. July 4th).
- Store-local defaults to 2/store.
- Reels default to 2/week (0 for a stills-only test week, 4 for holiday/app-launch weeks).
- Minimum **3 Brand posts per week** — the Brand page must never go dark.

---

## 4. Captions are MANDATORY

No image-only posts. Every item gets a drafted caption or it is skipped. If a caption is empty or under the minimum after 2 regenerate retries → skip the item and DM Joshua.

**Brand-tier caption** = opening line + brand-voice line ("What's Right Is Right" / 30-day warranty / family-owned / rate) + the full 5-store address footer:
```
📍 125 Walker St, Lexington
📍 1321 W Broad St, Waynesboro
📍 1790 E Market St, Ste 22, Harrisonburg
📍 571 James Madison Hwy, Culpeper
📍 2362 Peters Creek Rd Ste C, Roanoke
```
Minimum 3 sentences.

**Store-local caption** = opening line + store-specific angle/CTA + that store's single-store address footer. Minimum 2 sentences.

**Per-platform rules within a tier:**
- **Instagram** — ≤1500 chars, 5–8 niche hashtags + `#ValleyPawn #WhatsRightIsRight #TheValleyPawn`.
- **Facebook** — same body as IG, **no hashtags** (FB doesn't reward them). Applies to Reels too.
- **GMP** — ≤1500 chars, **no hashtags, no phone numbers in body, no ALL-CAPS, ≤2 emojis, no firearms language**, informational tone (soft CTA). Roanoke GMP: never reference firearms — pivot to gold/silver, electronics, tools, loans, or warranty.

**Reels** additionally require a burned-in caption overlay (≤6 words) confirmed in the sidecar (`has_burned_captions=true`); if false, skip the Reel and DM Joshua. FB body for a Reel is 2–4 sentences leading with the hook, plus the tier's address footer, no hashtags.

**Hard stop:** the name "Dixie Pawn" must never appear in any output. If it does, skip the item and DM Joshua. Never reference firearms/guns/weapons on any social/GMP channel.

---

## 5. Time-window quotas (30/30/30/10)

Distribute the full lineup so published output meets:

| Window (ET) | Quota | Notes |
|---|---|---|
| 8 AM – noon | 30% | store-local statics fill this |
| noon – 4 PM | 30% | store-local + Deals (Value window) |
| 4 PM – 9 PM | 30% | **both Reels here by default**; Brand fills high-visibility evening |
| other (e.g. Sun 8 PM) | 10% | overflow |

Reels bias to **4–9 PM** (peak Reels engagement for our 25–65 Shenandoah Valley audience). The scheduler refuses to publish if the resulting weekly distribution violates the quota — re-shuffle slots instead.

---

## 6. Pillar mix — monthly weighting + hard sub-pillar caps/floors

Base monthly weighting (from the brand-studio seasonal calendar):

| Period | Weighting |
|---|---|
| Jan | Story 40 / Value 30 / Find 20 / Heritage 10 |
| Feb–Apr | Find 35 / Value 35 / Story 20 / Heritage 10 |
| May–Jun | Find 50 / Value 30 / Story 10 / Heritage 10 |
| **Jul–Aug** | **Heritage 20 / Find 30 / Story 30 / Value 20** |
| Sep–Oct | Value 40 / Find 30 / Story 20 / Heritage 10 |
| Nov–Dec | Find 50 / Value 40 / Story 5 / Heritage 5 |

Apply these audit-driven sub-pillar caps/floors over a **rolling 4-week window** (combine the proposed batch with the prior 3 weeks' manifests; re-balance BEFORE generating heroes if any cap breaks or floor misses):

| Sub-pillar | Cap / Floor | Tier preference |
|---|---|---|
| Birthstone / Calendar | ≤15% (≤1/month) | Brand only |
| New arrivals (The Find, specific item) | 25–30% | Store-local |
| Gold/silver buying | 15–20% | Brand (campaign) / Store-local (local) |
| Loans | ~15% | Brand (rates) + Store-local |
| Layaway | ~15% | mostly Store-local |
| Warranty / "What's Right Is Right" | ≥10% | Brand |
| Community / Local | ~15% | Store-local |
| The Team (employee shoutouts) | ≥10% | Store-local |
| How It Works (modern pawn / tech / app) | ≥10% | Brand |
| Mobile app | ≥5% | Brand |
| **Deals of the Week** | **≥15%** | Store-local (Value) |
| Holidays (per occasion) | hit every named holiday | Brand |

**Reel pillar floors (rolling 4 weeks):** Warranty ≥1, Team ≥1, How-It-Works ≥1, Mobile-app ≥1; Find ≤4, Heritage ≤2. A missing floor forces the next week's Reel to that pillar. Reels carry the four engagement-floor pillars by default and are Brand-tier unless a store-specific Team/local-event Reel.

Content pillars (naming): **The Find, How It Works, The Team, Deals & Value, Community** (+ Warranty / "What's Right Is Right", Heritage, Mobile app, Gold/Silver, Loans, Layaway as sub-pillars).

---

## 7. Deals-of-the-Week (Step 3c-bis, added 2026-07-04)

Each Tuesday 9 AM the `weekly-new-deal-request` task DMs managers for that week's deals, posted to Slack **`#deal-of-the-week`** (channel ID `C0AVCANK7E3`; note the singular channel name). The same deals email Thursday via `weekly-valley-pawn-email-campaign`.

Pipe the last 7 days of `#deal-of-the-week` submissions into per-store social posts — **5 store-local Deal posts/week (one per store), sub-pillared Deals (under Value).** Match each submission to its store, generate an MJ hero from the manager's photo via `vp-hero-image --cref` (so the hero resembles the actual item), compose assets, draft a caption with deal price + fair-market comparison + 30-day warranty line, schedule Thursday 10 AM–4 PM (Value window) via Publer.

Multi-channel target per Deal: `{Store} FB + shared @valley_pawn IG + {Store} GBP`. If a store's GBP isn't connected in Publer yet, target FB+IG only and DM Joshua to complete the GBP connection. **If a store's manager doesn't submit by Wednesday EOD, skip that store's Deal slot and DM Joshua.**

---

## 8. Reuse-vs-regenerate

Query the asset library `Valley Pawn Studios/asset-library/heroes/` first. Reuse a hero for the same SKU/description generated in the last 30 days if it wasn't used in the last 2 weekly batches. Cross-style reuse is forbidden. Target ≥40% reuse rate. Brand items (storefront/palette/tagline lockups) reuse heavily; store-local Find items usually need fresh per-SKU heroes.

---

## 9. Staging + approval

Stage the approval-card stack in Slack **`#vp-studio-queue`** (one message per item, threaded under a "Week of {date}" parent), with routing prefix `[BRAND]`/`[STORE-XXX]`, the chosen headline + per-platform captions + CTA + schedule slot + a pillar-window check line. Joshua approves from his phone (~5 min). Approved items publish across the week via Publer. Save `batch_manifest_{YYYY-MM-DD}.json` to `Valley Pawn Studios/output/{YYYY-MM-DD}/`.

> **Setup note (2026-07-06):** `#vp-studio-queue` did not exist in the workspace at rebuild time. It must be created before the staging step can run. Until it exists, stage to a confirmed existing channel or hold for Joshua.

---

## 10. Inventory source filenames (pipeline reality)

The `vp-content-batch` SKILL references `inventory_export_*.csv`, but the Bravo Data Extraction pipeline actually produces per-store files in `Bravo Data Extraction/output/`:
- `{YYYY-MM-DD}_{STORE}_items-to-price.csv` — freshly-received items needing pricing (use for "just in" Find picks)
- `{YYYY-MM-DD}_{STORE}_aged-inventory-summary.csv` — sellable aged inventory (use for higher-margin Find substitutes)

Store codes: `CUL, WAY, HAR, LEX, ROA` (note: Harrisonburg = `HAR` in Bravo filenames, `HBG` in some studio naming). Use the most recent dated file; if the latest export is >24h stale, log staleness and DM Joshua.

---

## 11. Guardrails (hard stops)

- MJ fast hours exhausted → pause + DM Joshua (never silently drop to relax mode).
- Bravo export missing/stale >24h → log + DM Joshua.
- Empty caption after 2 retries → skip + DM Joshua.
- "Dixie Pawn" in generated copy → HARD STOP, skip + DM Joshua.
- Firearms language on any social/GMP channel → substitute a non-firearm item (highest-margin non-firearm from that store's inventory).
- Pillar cap breach at Step 2 → re-balance before generating heroes.
- On any task failure, the scheduled run must post **nothing** to Slack (Joshua reviews runs inside Claude).
