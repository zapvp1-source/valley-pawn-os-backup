# eBay Desk — list direct to eBay, keep Bravo in sync (design, 2026-11-17)

Why: Bravo bills 5% of every eBay sale made from a Bravo-created listing (Oct 2026: $2,088.64 on $41,770.55, INV2597398). Joshua 11/17: Bravo will not reduce it.
What Bravo's eBay module actually does for us today: it creates the listing (title carries the Bravo item # like (VAP031234)). It does NOT ring the sale into Bravo — stores already ring every eBay sale by hand on the eBay tender (policy "eBay Sales — Ring Them as eBay", PU-2026-11). So dropping the module loses only listing creation.

## What the stores see (one page, one login per store)
1. List an item: type the Bravo item #, snap photos on the phone. The desk fills title, item specifics and description to the ebay-context standard, suggests a price from sold comps, and blocks any price under cost + fees. Store taps Publish. SKU on eBay = Bravo item #.
2. Ring these sales: every new eBay order shows the Bravo item # and the price to ring on the eBay tender. Tap Done after ringing.
3. Ship these: label and tracking per order, oldest first, late-ship warning.
4. Returns: what came back and the restock step in Bravo.

## What runs behind it (no store work)
- Every 15 min: pull new orders from all 5 store accounts (Trading API GetOrders, tokens already on the Mac) into "Ring these sales".
- Next morning: check each order against the Bravo sold export. Not rung after 24 h -> flag to the store manager.
- Double-sell guard: when an item sells in the store and is still live on eBay, end the eBay listing automatically (EndItem), and log it.
- Nightly reconcile: every live eBay listing must be in Bravo active inventory; every eBay sale must be rung; exceptions listed for the manager.

## Cutover
1. Desk goes live; every NEW listing goes direct. Stores stop using Bravo's eBay listing screen.
2. Existing Bravo-created listings (about 500) keep selling until they sell or age out; the aged ones get relisted through the desk as part of the markdown cycle. Run-off about 90 days.
3. When the last Bravo-created listing is gone, turn off Bravo's eBay module and remove Bravo's access to the 5 eBay accounts (eBay > Account > third-party app permissions), so nothing is left for Bravo to bill on.

## Savings
About $25,000/yr at the October eBay sales rate, ramping up as the old listings run off.

## Build order
1. Order feed + "Ring these sales" + 24 h check (uses only existing tokens; also fixes the double-sell gap on today's listings).
2. Double-sell guard (needs an intraday Bravo sold pull; daily pull works at first).
3. List-an-item page (Trading API AddFixedPriceItem; photo upload via UploadSiteHostedPictures).
4. Returns tab, then cutover.

## Open items
- Confirm with Bravo in writing that the 5% applies only to listings created through Bravo.
- Confirm the Bravo "eBay hold" location/status (ebay-context CONFIRM item) so listed items can't be sold at the counter.
