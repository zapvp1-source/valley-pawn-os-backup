# Getting all the Bravo data: the plan

Written 2026-11-27 for Joshua. Working copy for future sessions: `Projects/Bravo Warehouse/STATUS.md` on the Mac Studio.

## The short version

Bravo has no back door. The vendor confirmed in writing there is no API, the database is hosted by Bravo (nothing local to query), and you already decided in September not to buy Reporting Pro or use emailed reports. So every byte comes out through the Bravo screen automation already running on the Mac Studio. That pipeline is mature: it has 100+ report pulls built, and it can already pull any date range, not just yesterday.

So the job is not "find a way in." It is three things:

1. **Put everything already pulled into one place you can query.** Done today (first version).
2. **Backfill history** using the pulls that already work, one month per store at a time, on Sundays when Bravo is idle.
3. **Build one new wide item report** that carries the missing link: which buy or loan ticket each inventory item came from, and the date it entered inventory. This is the piece that ties buys and loans to what sold and what is sitting.

Daily refresh stays as it is (it is already running for inventory, sales, intake, layaways and unpriced items). The emphasis shifts to history depth, per your note.

## What exists today (checked against the files, not the run logs)

| Data | Detail level | History on hand | Refresh |
|---|---|---|---|
| In-stock inventory | Every item: number, category, description, cost, price, date into inventory | Nightly since 11/24/2026 | Nightly, 1:45 AM |
| Sold items | Every item sold: cost, tag price, actual sold price, date | 5/17/2025 to 5/17/2026, then 8/12/2026 to now. **Gap: 5/18 to 8/11/2026. Nothing before May 2025.** | Daily |
| Buys from public | Every item: ticket, category, description, amount paid | 5/14/2024 to 4/30/2026 (Culpeper to 5/13). **Gap: May 2026 on, at ticket level.** | Not scheduled |
| Daily intake (loans and buys written) | Item, amount, associate. No ticket number. | Mid June 2026 to now | Daily |
| Loans | Ticket, customer, amount, outcome (redeemed, expired, on loan), due and pull dates | Patchy: a few months per store in 2025 and 2026. Jewelry and metals loans monthly back to Oct 2023. | Not scheduled |
| Open loans due soon | Full detail incl. last payment | Daily since 11/20/2026 | Daily |
| Layaways | Every active layaway, payments, age | Daily since 11/21/2026 | Daily |
| Unpriced items (waiting to be priced) | Item, source (expired buy, out of pawn, return), cost | Daily since June 2026 | Daily |
| End of Month report | Store totals: loan base, inventory base, sales, cost of sales, service charges | May to Aug 2026 on disk | Monthly |
| General ledger | By account, by store | Jan to Oct 2026 | Monthly |
| Scrap and refining | By lot | 2025 and 2026 | Monthly |

## The gaps, in order of importance

1. **No link between an inventory item and the ticket it came from.** Bravo gives an item a new number when it is priced, so today a sold item cannot be traced to the buy or the forfeited loan that produced it. Bravo's inventory report builder does offer the fields needed: Source, Last Ticket Number, Date to Inventory, Vendor, Customer, metal weight and purity, location. Nobody has built a report layout that shows them.
2. **Sold items have no "date into inventory."** Time to sell can only be measured for items that were in a nightly snapshot (since 11/24). The same new layout fixes this for all history.
3. **Loan history is thin.** No complete record of every loan written and how it ended.
4. **No transaction-level money trail**: interest and fees collected per loan, extensions, redemptions, layaway payments, refunds, voids. Bravo has Loan Journal, Loan Disposition, Loan History, Layaway Journal and Sold Inventory reports. Handlers were written for all of them in May but never proven.
5. **Transfers, cost adjustments, lost or stolen, vendor purchases**: handlers exist, one test pull each, not scheduled.
6. **History before May 2025 for sales and before May 2024 for buys** has never been pulled. Bravo keeps it (the oldest item on a shelf dates to 2016).

## The plan

### Step 1. One queryable store (done today)

`Projects/Bravo Warehouse/bravo_warehouse.sqlite` on the Mac Studio, rebuilt from the pipeline's files in about five seconds by `bin/build_warehouse.py`. It only reads the pipeline's output and changes nothing in it. First build holds:

- 36,734 in-stock item rows (three nightly snapshots; 12,257 items on the shelf as of 11/26, $653K at cost)
- 26,222 sold item lines, May 2025 to yesterday
- 23,746 buy lines, 7,808 intake lines, 73,000 loan rows, 2,282 layaway rows, 32,309 unpriced item rows
- `COVERAGE.md` beside it lists, per data type and store, exactly which days are covered. It regenerates on every build, so the gap list is always current.

### Step 2. Backfill with pulls that already work (starts Sunday 11/29)

No new Bravo objects, no changes to existing ones. One month, all five stores, per pull, queued through the normal trigger queue so nothing collides.

| Backfill | Window | Pulls |
|---|---|---|
| Sold items, the 2026 gap | 5/18 to 8/11/2026 | 3 |
| Buys at ticket level | May 2026 to now | 7 |
| Loans written, with outcome | Jan 2023 to now, monthly | ~47 |
| Sold items, older history | Back from April 2025 until Bravo returns nothing | open ended |
| Buys, older history | Back from April 2024 | open ended |

These run on Sundays and overnight slots that are free. Expect two to three weekends for the full depth. Each pull is checked against Bravo's own row count before it is accepted.

### Step 3. The item master report (the important new build)

Build one new shared column layout and saved report in Bravo, "Claude Item Master", through the same scripted builder that created two inventory reports on 11/21. Columns: item number, status, status date, store, category, source, type, last ticket number, date to inventory, cost, price, last sold price, vendor, customer, location, metal type, purity and weight, serial number.

Then two pulls from it:
- **Everything, once**: all items in every status (sold, scrapped, transferred, lost, layaway, in stock), month by month, as far back as Bravo goes. This single pull gives acquisition date, source ticket, cost, sale date and sale price on one row, which is the tie between buys, loans and sales.
- **Daily**: every item whose status changed yesterday. That is the running record of everything that sold, was scrapped, moved or written off.

Risk: creating a new column layout by script has not been done before (the 11/21 build reused existing layouts). I will probe it read-only first. If Bravo will not let a script build a layout, the fallback is a two-minute manual step: someone drags those columns into view once and saves the layout. I would ask you for that only if the script route fails.

### Step 4. The money trail

Prove the already-written handlers for Loan Journal, Loan Disposition, Loan History, Layaway Journal, Sold Inventory, Transfers, Cost Adjustment and Lost or Stolen, one store and one month each, then backfill monthly. These give interest and fees earned per loan and the cash timing needed to put a carrying cost on inventory.

### Step 5. Validation

Every month, per store, the warehouse totals must equal Bravo's End of Month report: cost of sales, sales revenue, ending inventory at cost, ending loan balance. The daily sold feed was found to tie to End of Month cost of sales on 11/23; the history pulls do not fully tie yet (see the update at the end). A month that does not tie is marked unverified in the coverage file and is not used in analysis until it does.

### Step 6. Keep it current

A small nightly job rebuilds the warehouse after the nightly inventory pull, so "inventory as of yesterday" and everything else is one query away at any time.

## What this unlocks

Once Steps 2 and 3 land, each item has: what it came in as (buy, forfeited loan, vendor), what was paid or loaned, when, when it hit the shelf, when it sold or was scrapped, for how much, and at which store. From that:

- Days to sell by category, store, price band and source, with a cost of capital charged for every day on the shelf
- True profit per item after carrying cost, so slow movers can be judged on real numbers
- Categories where money goes out on buys or loans and does not come back
- Loan outcomes: redemption rate and yield by category and loan size, and what forfeited items actually fetch
- Buy price against eventual sale price by associate and store

## What I need from you

Both answered 11/27: the backfill job is approved and installed, and Rocket Pawn is not on Bravo yet. Nothing else is needed. No spend, no vendor contact.

## Fixed along the way

The nightly inventory list had stopped publishing to Google Drive after 11/24 because Drive held a lock on a small note file. Fixed today; the 11/26 list (12,257 items) is now in Drive under `08 Reports & Analysis/Inventory - Item Level`.

## Update, 11/27 evening: first backfill results

- **New sold history pull works.** The existing sold pull came back short on a two-week window (135 of 152 rows), so I built a new one that copies the whole list at once and checks it against Bravo's own row count. The 5/18 to 8/11/2026 gap is now filled for all five stores (5,488 item lines, every pull matched Bravo's count).
- **Rocket Pawn** is not on Bravo yet, so it is out of scope until it is.
- **Unattended backfill is installed.** A job on the Mac works down a queue of history windows every Sunday (eight slots, four store-months each, placed around the existing Sunday jobs) and rebuilds the warehouse nightly at 3:05 AM. The queue currently holds sold items month by month back to January 2021.
- **Sales ledger proven to the penny.** Bravo's built-in Sold Inventory report for Lexington, 8/1 to 8/27/2026, came out at $11,028.32 cost, which equals End of Month sales cost of $11,081.98 less $53.66 of returns exactly. It lists every sale line with quantity, discount, price sold, cost, associate, shelf location and channel. It is now the sales ledger for the warehouse, and each file is checked against its own total before it is used.
- **Item report history is 92 to 98 percent of that** (an earlier note said 87 to 92; that compared against the wrong End of Month line). The shortfall is stock-number items sold repeatedly, where the item report keeps only the latest sale. It stays in the warehouse for category and tag price, not for totals.
- **Loans and buys history pulls built and proven.** Lexington, August 2026: 152 loan item rows on 108 tickets, and 212 buy item rows, both matching Bravo's row count. Loans written through 8/27 came to 97 tickets, the same as End of Month. Each row carries the ticket number, item, amount, customer, and how it ended (on loan, redeemed, expired).
- **Sunday queue now holds** sales ledger, loans and buys for every month from November 2026 back to January 2021 (six windows per slot), then the older item report months.

## Update, 11/27 late evening: the item to ticket link is built

- **Step 3 is done.** A new column layout and saved report, both named "Claude Item Master", now exist in Bravo. They were created by script and are additions only. The existing layout they were based on was checked afterwards and is unchanged.
- **First pull proven.** Lexington, August 2026: 556 item rows, matching Bravo's own count. Every row shows where the item came from (buy, pawn, vendor purchase), the ticket it came in on, the date it hit inventory, the customer, and how it ended (sold, still in stock, scrapped, shrinkage, redeemed). Shrinkage in the pull was 52 items and $868.11, exactly what End of Month reports.
- **First real number from it:** items Lexington sold in August had been in inventory 156 days on average.
- **End of Month check is built in.** The warehouse now reads every End of Month file on disk and compares Bravo's cost of sales to the sales ledger by store and month. October 2026 ties to the penny at all five stores.
- **Backfill is faster.** The history job now also runs every night at 11:20 PM, in addition to Sundays. The item master pull goes first for each month and runs back to 2016.
