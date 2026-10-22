# Online Store Audit — October 21, 2026

Scope: all 5 eBay store accounts and the thevalleypawn.com /shop page. Checked against what was actually posted and pulled live, not against run records: the live Trading API pull this morning (all 5 stores), the 10/20 seller-standards pull, #ebay-performance, #ebay-listings and #website for the last 3 weeks, and the engine, state and ledger files on the Mac.

## Scorecard (trailing 90 days, live 10/21)

| Store | Active | Listed $ | Sold 90d | Revenue 90d | Fee % | Aged >90d | Seller level (9/21 eval) |
|---|---:|---:|---:|---:|---:|---:|---|
| Culpeper | 186 | $26,708 | 254 | $29,542 | 15.8% | 115 ($12,678) | Top Rated |
| Roanoke | 100 | $12,412 | 187 | $23,412 | 16.1% | 31 ($3,570) | Above Standard |
| Waynesboro | 42 | $13,050 | 31 | $16,072 | 14.0% | 11 ($1,736) | Top Rated |
| Lexington | 21 | $4,140 | 66 | $15,134 | 18.9% | 6 ($811) | Above Standard |
| Harrisonburg | 21 | $4,190 | 31 | $9,312 | 21.2% | 14 ($1,050) | **Below Standard** |
| **Channel** | **370** | **$60,500** | **569** | **$93,472** | **16.6%** | **177 ($19,845)** | |

October month to date (through 10/18): $25,725 across 111 orders. Run rate is about $375K a year.

## What's working

- **Revenue is growing while inventory shrinks.** 90-day revenue is up $6,709 versus the 9/7 pull, even though there are 76 fewer active listings.
- **Feedback is strong everywhere.** Every store's 12-month positive rate is between 98.6% and 99.6%. Culpeper and Waynesboro are both Top Rated, and Lexington climbed from Below Standard to Above Standard.
- **Reporting runs on its own.** Seven reports are posting on schedule from the Mac with no Claude session needed: daily listings, Monday sales rankings, Monday channel pulse, Friday efficiency, Sunday online-store audit, the monthly ratings and seller-standards sweep, and the /shop refresh twice a day.
- **The return policy fixes itself.** Each Sunday the audit switches stray 14-day and no-returns listings to 30-day returns (22 on 10/18, 48 on 10/11), then spot-checks them live.
- **The four hard rules are built into the code.** That covers the 90-day markdown start, no Best Offer switched on, model numbers kept, and no repricing of precious metal. The monthly markdown engine skips metal and fails closed if it can't run that check.
- **The website shop is current.** It shows 364 live eBay items, refreshed at 7 AM and 3 PM, with weapons-adjacent items filtered out. Yesterday's website audit removed the unused WooCommerce cart from every page and fixed page speed.

## What's not working

1. **Harrisonburg is Below Standard.** Its defect rate is 5.23% (9 of 172), 2.33% of its cases closed without a seller resolution (4), and 4.27% of its orders shipped late. That costs higher fees and lower search placement on every Harrisonburg listing. Its fee rate (21.2%) is already the highest of the five stores. The next evaluation result comes in the November sweep.
2. **A Best Offer cleanup you approved sat undone for 5 weeks.** On 9/17 you approved switching off the Best Offer setting our own August fix had turned on for 193 Culpeper listings. The job failed three times and was never retried. The cause was the script looking for the wrong record file. **Fixed today** (see below).
3. **Video games were still taking offers.** 59 to 64 were flagged every week since 9/17 and assigned to Marketing on 10/12, but nobody switched them off. **Fixed today.** I also fixed a bug in the video-game check: it matched "Wii" inside "WWII," so it was treating W. Britain WWII soldier figures and a WWII bayonet as video games.
4. **Aged stock at Culpeper is stuck.** 115 of its 186 listings are past 90 days old, holding $12.7K of its $26.7K listed. 66 Culpeper listings have taken all three markdown cuts, are past 150 days, and nothing is scheduled for them next. Under the standard, the step at 150 days is to pull them.
5. **Supply is running out where items sell fastest.** Lexington sells more than 100% of its active count every month (median 2.5 days to sell) but has only 21 listings. Harrisonburg also has 21. Culpeper has the most listings and sells slowest (median 52 days). The channel adds about 8 new listings a day.
6. **Listing quality is below standard.** Average photo counts run 4.2 (Roanoke) to 7.0 per listing, against the 8–12 standard; 93% of Roanoke listings have fewer than 8. None of the listings carry a Bravo SKU, which leaves no automatic cost floor and no way to cross-check eBay sales against Bravo.
7. **No listing qualifies for Top Rated Plus.** Every listing has 2-day handling (3 days at Roanoke) and buyer-paid returns. Top Rated Plus requires 1-day handling and free 30-day returns. Without it, Culpeper and Waynesboro miss a 10% final-value-fee discount and the badge and search boost that come with it.
8. **Roanoke uploads tracking late.** Only 85.8% of its orders had tracking uploaded on time; Top Rated requires 95%. That one number keeps the store with the most sales history (5,782 feedback) from being Top Rated.
9. **Best Offers expire unanswered.** Three were open this week with nobody responding: Harrisonburg's lapsed this morning, Roanoke's ends tonight, Culpeper's tomorrow. Listings that take offers have no auto-accept or auto-decline limits set.
10. **Promoted Listings is only running at Culpeper** ($454 over 90 days). The other four stores spend $0.
11. **The reports overlap.** Four weekly reports in #ebay-performance each give their own number for the same measure (active listings shown as 370, 374 and 378). The Channel Pulse dashboard page hasn't been refreshed since 10/5.
12. **Buyer messages are piling up.** 232 are unread. Most are eBay's own notices, but 6 are case or dispute messages and 18 are return or refund messages, and those turn into defects (see item 1).
13. **The website shop has never taken an order.** It works as a catalog that sends shoppers to eBay, and nothing measures which eBay sales came from the website.

## Fixed today (no action needed)

- **Video-game check corrected** in `eBay/engine/ebay_rules.py`. It now matches whole words, so "Wii" no longer matches "WWII," and it also catches "PS4" at the start of a title and PSP. I tested it against 12 real titles, including the false matches, and all 12 came out right. Backup: `ebay_rules.py.bak-pre-wiiboundary-20261021`.
- **Best Offer cleanup pointed at the right records** in `eBay/engine/ebay_bestoffer_off.py`. It now reads `~/vp_ebay_fix_state.json`, the file the August fix actually wrote, which lists all 193 records. Backup: `ebay_bestoffer_off.py.bak-pre-statepath-20261021`.
- **Best Offer switched OFF on the listings below.** A test run first confirmed 93 listings: 79 are the August Culpeper listings still live, and 14 are video games or consoles at other stores. The script re-reads every listing live before changing it, can only switch Best Offer off, and records each change. **Result: 93 switched off, 0 failed**, and 3 random listings re-checked live all show OFF (run `20261021-124259-bestoffer-off`, recorded in `eBay/engine/ledger.jsonl`).
- **The fix now repeats every week.** The Sunday online-store audit switches Best Offer off on any video game (Rule 2), including the 21 listings skipped today because a buyer's offer was still pending. Until 11/15 it also retries the August Culpeper listings. Backup: `fleet/_backups/online_store_audit.sh.bak-pre-bestofferoff-20261021`.
- **Pull list built:** `eBay/audit_weekly/2026-10-21/pull_list_150d_capped.csv` has 84 listings, $6,332 listed, that have taken all three cuts and are past 150 days (Culpeper 66, Roanoke 12, Harrisonburg 4, Lexington 2). 12 precious-metal listings are left off the list under Rule 4; those need a person's decision.

## How we optimize — ranked by dollars

| # | Move | Why | What it takes |
|---|---|---|---|
| 1 | **Get Harrisonburg back above standard** | Every Harrisonburg sale pays the Below-Standard fee surcharge, and its listings are pushed down in search | Preston: answer every return or case within 24 hours and never let a case close without a seller response; ship within 1 day |
| 2 | **Move inventory to Lexington and Waynesboro** | Lexington sells everything it lists in about 2 days; Culpeper takes 52. Shifting 20–30 listable items a week from the counters to the fast stores turns stock into cash | Operating call: a weekly listing quota per store (suggest 15/week at Lexington, Waynesboro and Harrisonburg) |
| 3 | **Pull the 84 capped listings** and send them back to the counter or to auction | $6.3K is sitting in listings that won't sell at 30% off; pulling them also lifts sell-through and search ranking | Stores work through the CSV; it needs the standard's "pull at 150 days" step |
| 4 | **Top Rated Plus at Culpeper + Waynesboro** (1-day handling + free 30-day returns) | 10% off final value fees is about $635 per 90 days, roughly $2.5K a year, before the search boost and badge. Return shipping costs run about $1K–1.5K a year at current return volume | Your decision: it changes the return-shipping policy |
| 5 | **Fix Roanoke's on-time tracking (85.8% → 95%)** | Makes Roanoke eligible for Top Rated: another ~$1.5K a year in fee discount, plus Top Rated Plus | Roanoke prints labels through eBay the same day it ships |
| 6 | **Turn on Promoted Listings (Standard, pay-per-sale) at the other 4 stores** at about 2–3% | You pay only when a promoted item sells; Culpeper's spend works out to 1.5% of its revenue | Your decision: it's ad spend |
| 7 | **8+ photos per listing, with the Bravo item number in the SKU** | Photos are the cheapest lever for conversion and for fewer item-not-as-described returns. A SKU gives every listing a cost floor and a Bravo match | Store training plus the engine's SKU-set step (already built, waiting to be enabled) |
| 8 | **Auto-accept / auto-decline limits** on listings that already take offers (accept ≥90%, decline ≤75%) | No offer expires unanswered again | Engine change. It only touches listings where offers are already on, per Rule 2 |
| 9 | **Merge the four weekly eBay reports into one** | One set of numbers, one place to read, less noise | Reporting rebuild |

## Needs you (3 decisions)

1. **Top Rated Plus** (1-day handling + free 30-day returns at Culpeper and Waynesboro): yes or no.
2. **Promoted Listings** at Waynesboro, Harrisonburg, Lexington and Roanoke at about 2–3% ad rate: yes or no.
3. **Weekly listing quota** per store: yes or no, and whether to start at 15 a week.

Sources: `eBay/audit_weekly/2026-10-21/summary.md` (live API pull), `eBay/ebay-ratings-sweep-2026-10.md` (seller standards 10/20), #ebay-performance, #ebay-listings, #website, the Best Offer cleanup's test-run and apply logs (10/21), and eBay's Top Rated Plus requirements (export.ebay.com).
