# Valley Pawn eBay — Listing-Age Standard (Reprice & Pull Cadence)

> # ⚠️ SUPERSEDED 2026-09-17 — DO NOT WORK FROM THE LADDER BELOW
>
> **Joshua amended this standard on 2026-09-17 after feedback from the stores: markdowns now start
> at 90 days aged, not 30.** Cutting at day 30 was giving away margin on items that were still
> selling at full price.
>
> **The cadence in force is:**
>
> | Age | Action |
> |---|---|
> | Day 0–89 | **Hands off.** No reprice, no price cut, no offers to watchers. Make the title, photos and item specifics right at listing time instead. |
> | **Day 90** | **First price cut (~10%)** via Markdown Manager, after a sold-comp check. |
> | **Day 120** | Second reduction (~10%), or end & relist fresh (Sell Similar) if it has no watchers. |
> | **Day 150** | **Pull or final relist.** One last relist with a materially new price + title + photos, or pull it from eBay — move to in-store retail, bundle, liquidate, or write off. |
>
> Cuts stop at the **30%-off floor** (3 cuts max), minimum 25 days between cuts. At the floor +
> 14 days with no sale, the listing is ended.
>
> **Also changed the same day, and binding on every listing regardless of age:**
> - **Best Offer is never switched on by anyone's automation.** A listing marked "no offers
>   allowed" stays that way — that is the store's decision. **Video games never take offers at all.**
> - **Model numbers are never removed from a title.** Only our own stock number — one of
>   `VAP VP VA CUL ROA WAY HAR LEX` followed by 5 or more digits, e.g. `(VAP031234)` — comes out,
>   and it gets moved into the listing's custom label rather than deleted. A code like `(A2482)`
>   or `(DCD771)` is the manufacturer's model number and is one of the most searched things in the
>   title. When in doubt, leave it in.
>
> **Status of this document:** every script and scheduled task was changed to the 90/120/150
> ladder on 2026-09-17. **This document itself has not yet been re-issued for signature** — it was
> e-signed by all 14 employees through Gusto on 2026-08-05 in its original 30/60/90 form. It must
> be redrafted and re-signed through `policy-lifecycle`; see `Life OS/OPEN_ITEMS_REGISTER.md`
> (2026-09-17). Until then, **this banner governs and everything below it is historical context
> only** — the evidence and reasoning are still worth reading, the day numbers are not.

---

**Prepared 2026-07-04 · Based on our own sales data + eBay platform research**
**Original ladder below SUPERSEDED 2026-09-17 — see the banner above.**

## The question
eBay is a "buy it now" marketplace — how long should a listing sit before we cut the price, and before we pull/relist it? We wanted the sweet spot backed by evidence, not a guess.

---

## What our own data says (382 sales across all 5 stores, last 90 days)

We matched every recent sale back to the day it was listed and measured how long it took to sell:

| Time on eBay | % of all sales | Cumulative |
|---|---|---|
| 0–3 days | 43.7% | **44%** |
| 4–7 days | 8.9% | **53%** |
| 8–14 days | 11.5% | **64%** |
| 15–30 days | 14.9% | **79%** |
| 31–60 days | 10.7% | **90%** |
| 61–90 days | 4.2% | **94%** |
| 90+ days | 6.0% | 100% |

**Median time to sell: 6 days.**

The takeaways are stark:
- **Over half of everything we sell (53%) sells within a week.** ~80% within 30 days.
- **After 90 days, an item has almost no chance of selling as-is — only 6% of our sales come from listings older than 90 days.**
- Meanwhile, **41% of our active listings are already older than 90 days**, and 146 of them are 180+ days old (some over a year). That inventory is proven dead weight — it sits in the catalog dragging down sell-through and search rank, but it essentially doesn't sell.

Important context: our items sell **much faster than the eBay average** (industry norm is 60–90 days to sell; ours is a 6-day median). That's because pawn inventory is priced to move. It means generic "wait 6 months before relisting" advice is wrong for us — our own data says intervene far sooner.

## What eBay's platform behavior says (external research)

- **Freshness boost:** a new listing gets a ~48–72 hour visibility bump while eBay tests it with buyers. Don't touch a listing in its first couple of weeks.
- **Cassini buries stale listings:** eBay's search algorithm deprioritizes listings that haven't converted, and specifically targets non-converting inventory around the **90-day** mark. An 8-month-old unsold listing is effectively invisible.
- **Send Offers to Watchers:** once a listing is 10+ days old, you can send watchers an offer ≥5% below list — the cheapest way to close an item that has interest but no buyer.
- **Reprice, don't just wait:** the market telling you "watchers but no sale after ~a week" means the price is wrong. Use Markdown Manager (shows the discount visually) rather than silent price edits.
- **Relisting (Sell Similar) resets the clock:** ending and relisting creates a new item ID and a fresh freshness boost, but wipes watchers and history. Best used on genuinely stale items with no watchers — not on items that already have interest.

---

## The Valley Pawn standard (recommended) — ⚠️ SUPERSEDED 2026-09-17, see the banner at the top of this file

> **The day numbers in this section are the OLD ladder and are no longer in force.** The cadence
> in force is 90 → first cut · 120 → second · 150 → pull or final relist. Nothing is repriced or
> offered to watchers before day 90.

A simple three-gate cadence, tuned to our data (90% of sales happen by day 60, 94% by day 90):

**Days 0–14 — Hands off.** This is the freshness window and when 64% of our sales happen. Don't reprice, don't relist. Just make sure title, photos, and item specifics are good from the start.

~~**Day 21–30 — First intervention.** If it hasn't sold:~~ **← SUPERSEDED 2026-09-17. There is no day-21 or day-30 intervention. Nothing happens to a listing before day 90.**
- ~~Has watchers? → **Send Offer to Watchers**, 5–10% below list, 48-hour expiry.~~ **No offers to watchers before day 90.**
- ~~No watchers? → **First price cut (~10%)** via Markdown Manager, after a quick sold-comp check.~~ **The first cut happens at day 90.**
- (By day 30, 79% of the sales that will ever happen already have — a still-unsold item is now in the slow tail. *Still true as data; it is no longer the basis for acting at day 30 — cutting that early was giving away margin on items that were still selling at full price.*)

**Day 60 — Act decisively.** Still no sale:
- **Second reduction (~10–15%)**, or
- **End & relist fresh (Sell Similar)** with a new lead photo / sharper title if it has no watchers — get a new freshness boost.

**Day 90 — Pull or final relist.** This is the hard gate. Only 6% of sales happen past 90 days and Cassini has buried it:
- One last relist with a **materially new price + title + photos**, OR
- **Pull it from eBay** — move to in-store retail, bundle, liquidate, or write off.
- **Nothing sits past 90 days untouched.**

### One-line version for the team
> ~~**Reprice at 30 days. Reduce or relist at 60. Pull or final-relist at 90.**~~ **← SUPERSEDED 2026-09-17.**
> **The line in force is: first cut at 90 days. Second at 120. Pull or final-relist at 150. Nothing is repriced before day 90.**

---

## How this plugs into our automation
- **"Aged / needs action" = 90+ days** — this is the line for the weekly cleanup email (already matches our aged-inventory report).
- ~~Natural next step: the weekly job can flag three buckets per store — *reprice now (30–59d)*, *relist/reduce (60–89d)*, *pull now (90+d)*.~~ **SUPERSEDED 2026-09-17** — the buckets are now *first cut (90–119d)*, *second cut / relist (120–149d)*, *pull or final relist (150d+)*. Nothing under 90 days appears on a worklist at all.

*Data source: eBay Trading API (GetOrders + GetSellerList + GetMyeBaySelling), all 5 Valley Pawn stores, pulled 2026-07-04. Analysis script: `ebay_dts_analysis.py`.*
