# eBay Ratings Sweep — August 2026

Monthly public feedback + seller-standards sweep for all 5 Valley Pawn eBay store accounts.
Run date: 2026-08-21. First run of this task (migrated from cloud to local 2026-08-21) — no
prior month's sweep doc exists yet, so there is nothing to compare against. This doc is the
baseline for future monthly comparisons.

Note on save location: the task asked for this to live in an "Online Store" Claude project
under a `claude/` subfolder. No project by that name exists in `~/Documents/Claude/Projects/`
(searched Google Drive and the local Projects folder — nothing named "Online Store" or matching
`online-sales-status-*.md`). Saved instead in the existing `eBay` project folder, which is where
all other eBay-related tracking docs already live. Flagging this as a naming mismatch to resolve
next run — if Joshua wants a dedicated "Online Store" project going forward, this file can be
moved there.

## Ranked by 12-month positive % (best to worst)

| Rank | Store | Username | Feedback Score | 12-mo Positive % | Top Rated Seller |
|---|---|---|---|---|---|
| 1 | Roanoke | valley_pawn_roanoke | 5,663 | 100% | Not showing on profile |
| 2 | Harrisonburg | valley_pawn_harrisonburg | 617 | 100% | Not showing on profile |
| 3 | Culpeper | valley_pawn_culpeper | 1,196 | 99.8% | Yes |
| 4 | Waynesboro | valley_pawn_waynesboro | 618 | 99.6% | Yes |
| 5 | Lexington | valley_pawn_lexington | 1,269 | 98.9% | Not showing on profile |

## Feedback detail by store

### Roanoke — valley_pawn_roanoke
- Feedback score: 5,663 | Member since Aug-20-10
- Positive/Neutral/Negative — 1-mo: 39/0/0 · 6-mo: 145/1/0 · 12-mo: 267/1/0
- Detailed seller ratings (12-mo avg): accurate description, shipping cost, shipping speed, communication all rated on recent transactions
- No Top Rated Seller badge shown on public profile

### Culpeper — valley_pawn_culpeper
- Feedback score: 1,196 | Member since Oct-14-20
- Positive/Neutral/Negative — 1-mo: 70/0/0 · 6-mo: 293/1/1 · 12-mo: 548/3/1
- **Top Rated Seller** badge shown

### Waynesboro — valley_pawn_waynesboro
- Feedback score: 618 | Member since Jul-04-19
- Positive/Neutral/Negative — 1-mo: 19/0/0 · 6-mo: 98/0/0 · 12-mo: 233/1/1
- **Top Rated Seller** badge shown

### Harrisonburg — valley_pawn_harrisonburg
- Feedback score: 617 | Member since Sep-18-21
- Positive/Neutral/Negative — 1-mo: 15/0/0 · 6-mo: 78/1/0 · 12-mo: 148/2/0
- No Top Rated Seller badge shown on public profile

### Lexington — valley_pawn_lexington
- Feedback score: 1,269 | Member since Jul-27-15
- Positive/Neutral/Negative — 1-mo: 18/0/0 · 6-mo: 96/0/1 · 12-mo: 186/1/2
- No Top Rated Seller badge shown on public profile
- **Seller Standards dashboard (only account reachable this run — Chrome was signed into Lexington):**
  - Current seller level: **Below Standard** (as of Aug 20, 2026)
  - Past seller level: Below Standard (as of Jul 20, 2026)
  - If evaluated today: would be **Above Standard** — next real evaluation Sep 20, 2026
  - Transaction defect rate: 2 of 215 transactions
  - Late shipment rate: **4.23%** (9 of 213) — above the 3% target in `ebay-context`
  - Cases closed without seller resolution: 2 of 215
  - Tracking uploaded on time: 100% (56 of 56)
  - Return rate: 5.12% (11 of 215) — worst categories: Cameras & Photo (33.3%), Collectibles (18.2%), Business & Industrial (18.2%)
  - Transactions/sales (trailing period): 215 transactions, $40,593.09
  - Sales snapshot: last 7 days $600.86, last 31 days $5,197.00, last 90 days $10,821.73, YTD $30,037.42
  - Selling costs: $1,336 (26% of total sales) across eBay fees + taxes/gov't fees

No account showed new negative or neutral feedback strictly within the past month (1-month
columns all clean); the negatives/neutrals reflected above fall in the trailing 6–12 month window.

## Bottom line / priorities

1. **Lexington needs attention.** It's the only account currently Below Standard, driven mainly
   by a late shipment rate (4.23%) above the 3% target — tightening handling time should flip it
   to Above Standard by the Sep 20 re-evaluation. Return rate (5.12%) and 2 unresolved cases are
   secondary but worth watching, especially in Cameras & Photo and Collectibles.
2. Culpeper and Waynesboro are healthy, Top Rated, and need no action beyond normal monitoring of
   their single open negatives.
3. Roanoke and Harrisonburg have perfect 12-month feedback but don't display the Top Rated Seller
   badge — worth checking each one's own Seller Hub → Seller Level page directly (not reachable
   this run since Chrome was only signed into the Lexington account) to see whether they're
   missing a volume/transaction threshold or just not surfacing the badge.
4. Going forward: log into each of the 5 store eBay accounts at least once a month so the Seller
   Standards dashboard can be pulled for all 5, not just whichever account Chrome happens to be
   signed into that day.

## Data gaps this run
- Seller Standards dashboard only available for Lexington (the signed-in account). Roanoke,
  Culpeper, Waynesboro, and Harrisonburg dashboards were not reachable via the shared Chrome
  session — only their public feedback profiles were pulled.
- No "Online Store" Drive/Projects location exists — saved to the `eBay` project folder instead
  (see note at top).
