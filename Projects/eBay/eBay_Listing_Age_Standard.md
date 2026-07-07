# Valley Pawn eBay — Listing-Age Standard (Reprice & Pull Cadence)

**Prepared 2026-07-04 · Based on our own sales data + eBay platform research**

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

## The Valley Pawn standard (recommended)

A simple three-gate cadence, tuned to our data (90% of sales happen by day 60, 94% by day 90):

**Days 0–14 — Hands off.** This is the freshness window and when 64% of our sales happen. Don't reprice, don't relist. Just make sure title, photos, and item specifics are good from the start.

**Day 21–30 — First intervention.** If it hasn't sold:
- Has watchers? → **Send Offer to Watchers**, 5–10% below list, 48-hour expiry.
- No watchers? → **First price cut (~10%)** via Markdown Manager, after a quick sold-comp check.
- (By day 30, 79% of the sales that will ever happen already have — a still-unsold item is now in the slow tail.)

**Day 60 — Act decisively.** Still no sale:
- **Second reduction (~10–15%)**, or
- **End & relist fresh (Sell Similar)** with a new lead photo / sharper title if it has no watchers — get a new freshness boost.

**Day 90 — Pull or final relist.** This is the hard gate. Only 6% of sales happen past 90 days and Cassini has buried it:
- One last relist with a **materially new price + title + photos**, OR
- **Pull it from eBay** — move to in-store retail, bundle, liquidate, or write off.
- **Nothing sits past 90 days untouched.**

### One-line version for the team
> **Reprice at 30 days. Reduce or relist at 60. Pull or final-relist at 90. Never let a listing sit past 90 days as-is.**

---

## How this plugs into our automation
- **"Aged / needs action" = 90+ days** — this is the line for the weekly cleanup email (already matches our aged-inventory report).
- Natural next step: the weekly job can flag **three buckets per store** — *reprice now (30–59d, no sale)*, *relist/reduce (60–89d)*, and *pull now (90+d)* — so the team gets a specific worklist, not just a pile.

*Data source: eBay Trading API (GetOrders + GetSellerList + GetMyeBaySelling), all 5 Valley Pawn stores, pulled 2026-07-04. Analysis script: `ebay_dts_analysis.py`.*
