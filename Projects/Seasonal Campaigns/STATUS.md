# Seasonal Campaigns — STATUS (created 2026-11-21)

Joshua's direction (2026-11-21): one enterprise campaign plan, every channel, every seasonal event, automatic, like a big retailer. Default offer 15% off in store, "some exclusions apply", public, email to the full list.

## Source of truth
`campaigns.json` in this folder. 16 campaigns through Black Friday 2027. Each has dates, lead side, offer, landing page, channels, status.

## What already exists to build on (do not rebuild)
- `eBay Customer Campaign/` is already a 12-month, multi-channel engine (calendar.json -> build_month.py -> packs with email.html, push.txt, sms.txt; native agent com.valleypawn.ebay-customer-campaign). The conductor should follow that exact pattern.
- Social: `Refine Social Media/vp_social` planner + Publer publisher; lanes read CALENDAR_AUG_DEC_2026.md.
- Email: Brevo weekly chain, draft guard, test loop (Valley Pawn OS/bin/brevo_*.py, email_test_loop.py). Key at ~/.config/valley-pawn/brevo_api_key.
- Texts: build_text_lists.py + vp_textable.py rules; Chekkit campaigns.
- Push: Bravo Mobile Messenger handlers (Bravo Data Extraction/MobileEvents*.ahk).
- Website: WordPress connector / wp client. Google profiles: store GBP slots in vp_social; BrightLocal for hours.

## Black Friday 2026 (live)
See campaigns.json -> black-friday-2026 (done / open).

## Build order (next)
1. `build_campaign.py --id <campaign>`: one pack per campaign (email.html, social briefs per channel, gbp post, banner block, push.txt, sms.txt, PACK.md), modelled on eBay Customer Campaign/build_month.py. Never sends.
2. Native agent `com.valleypawn.campaign-conductor` (daily): reads campaigns.json, runs the countdown, hands each piece to the existing engine, records receipts. Dry-run first week.
3. First full T-21 cycle: new-year-reset-2027 (T-21 = 2026-12-06). December gift campaign runs through it in parallel with the existing Brevo drafts.
4. T+7 scorecard from Bravo intake/sales vs same week last year.

## Open with Joshua
- Black Friday email is still set to 901 recipients; the switch to the full list needs him (or a session allowed to change a scheduled send).
- The exclusion list itself (what staff exclude at the counter) is not written down anywhere found.


## 2026-11-21 afternoon — 12 months built and scheduled (Joshua: "build the next 12 months and set it and forget it")
No agent is needed for any of this; each system runs it on its own clock.
- **Email (Brevo's scheduler):** #93 Black Friday now 11,624 recipients (full list added). #94-#106 scheduled, all 10:00 AM ET, all 11,624 recipients: Christmas 12/15, Valentine's 2/9, Tax refund 2/23, St. Patrick's 3/16, Mother's Day 5/5, Memorial Day 5/25, Father's Day 6/15, July 4th 6/29, Back to School 8/10, Labor Day 8/31, Layaway 9/14, Fall 10/26, Black Friday 11/22/2027. Named "Seasonal — <name> — YYYY-MM-DD" so the Thursday picker never grabs them. Built by duplicating #93 and replacing only the title, preheader, hero and body slot; store blocks untouched.
- **Website (WordPress scheduler):** 11 sale pages future-dated (ids 2055-2065); they publish themselves ~10 days before each sale. Homepage page 7 block index 1 is a banner scheduler (inline script with a date table) that shows the right banner on the right dates through 11/27/2027 and nothing in between.
- **Social / Google profiles:** 12 months of briefs in Refine Social Media/CALENDAR_AUG_DEC_2026.md between CAMPAIGN-BRIEFS markers, for the weekly lanes to read.
- **If store hours, an address or a phone number changes:** the 13 scheduled emails and 12 pages carry today's facts. Update them (search Brevo for "Seasonal —", pages 2051, 2055-2065).
- **Blocked this session:** adding seasonal_campaigns.py to fleet/host_queue_allowlist.txt (so no native conductor); creating a scheduled task. bin/seasonal_campaigns.py was never created.
- **Still to build:** app push, texts, Google profile holiday hours, eBay promotions, signs, T+7 scorecard, a written exclusion list for staff.

## 2026-11-21 2:45 PM — daily check built, waiting on install
`Valley Pawn OS/bin/seasonal_campaigns.py` (+ .sh, + fleet plist, daily 06:20). Read-only; see its docstring. Install is one Terminal paste by Joshua (HUMAN_QUEUE row 2026-11-21). After install, first real output appears in RUN_LOG.md. Exclusion list: Joshua will define later (11/21). Next channel builds once the check is live: app push, texts, Google holiday hours, eBay promotions.

## 2026-11-21 3:00 PM — Easter added, Fall renamed Halloween (Joshua asked)
Easter Sale Mar 26-27, 2027: Brevo #107 (Tue 3/23 10:00, 11,624), page 2066 /easter-sale/ (publishes 3/16), banner 3/21-3/27. Brevo #105 and page 2064 renamed Halloween Sale (/halloween-sale/), same dates Oct 29-30. Homepage banner table, campaigns.json and social briefs updated. Not in the calendar: Christmas 2027 and New Year 2028 (past the 12 months), Presidents' Day, Juneteenth, Columbus Day, Cyber Monday. Veterans Day and Thanksgiving Day are thank-you only by design.

## 2026-11-21 3:25 PM — extended through New Year 2028; daily check is LIVE
- Christmas 2027: Brevo #108 (Tue 12/14/27 10:00), page 2070 /christmas-sale-2027/ (publishes 12/7/27), banner 12/7-12/18, sale Dec 17-18. New Year 2028: Brevo #109 (Tue 12/28/27 10:00, gold + loans, no discount), banner 12/27/27-1/15/28 to /loans/.
- Joshua ran the install paste ~3:11 PM. First native run wrote RUN_LOG.md: Black Friday email, page, banner, brief PASS; Christmas email, banner, brief PASS; no failures queued. com.valleypawn.seasonal-campaigns runs daily 06:20.
