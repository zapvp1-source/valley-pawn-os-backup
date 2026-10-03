# Shop Us Online: Monthly eBay Customer Campaign (Playbook)

**Owner:** Joshua. Built 2026-09-29. **Domain:** 1 (Valley Pawn). **Status:** FULLY AUTOMATED 2026-09-29 (Joshua: "automate this, forget the counter signs"). Native agent `com.valleypawn.ebay-customer-campaign`.

## Goal
Show existing customers that all 5 stores can be shopped online, and use the physical stores and the online channel to send traffic to each other every month.
- The online-to-store loop: "See it online? Call or text the store that has it."
- The store-to-online loop: a counter QR sign and a staff line that send walk-ins to the online shelf.

**One destination:** `thevalleypawn.com/shop/`. It shows live eBay inventory from all 5 stores (`vp-website-shop-nightly` rebuilds it every night; 411 to 429 items as of 9/29), and every item on it links out to eBay checkout.
- We send customers there instead of to five separate eBay storefronts. It gives them one link, lets us measure clicks by channel, and it's our own page.
- The per-store eBay storefronts go in the email as secondary links:
  - Culpeper: ebay.com/str/vpculpeper
  - Waynesboro: ebay.com/str/valleypawnwaynesboro
  - Harrisonburg: ebay.com/str/valleypawnharrisonburg
  - Lexington: ebay.com/str/valleypawnlexington
  - Roanoke: ebay.com/str/valleypawnroanoke

## Monthly rhythm
One touch per channel per month, spaced out so nobody gets hit twice in a week:

| Week | Day | Channel | Audience | Sent from |
|---|---|---|---|---|
| 1 | Tuesday 10:00 AM | Email | Same lists as the latest weekly email, plus internal seeds (the domain is still warming) | Brevo, auto-scheduled ("Shop Online — YYYY-MM") |
| 2 | Friday ~11:00 AM | Push | All MobilePawn app users (~550 active, all 5 stores) | Bravo Mobile Messenger (in Bravo POS, ~$0.02/push) |
| 3 | Thursday ~11:00 AM | Text | Recent customers; opt-in/opt-out handled by Chekkit (~5,900/month) | Chekkit Campaigns, one per store |
| 4 | none | Rest week | | |

- **Why Tuesday for email:** the weekly email goes out Thursdays. Its drafts are named "Theme — Month D, YYYY", and the Deal-of-the-Week picker finds them by that date string. Our drafts are named `Shop Online — YYYY-MM` so the picker can never grab one by mistake.
- **Why push and text land Thursday or Friday:** stores are closed Wednesday except Culpeper. Sending then puts the message in front of people right before the busiest days, Thursday through Saturday.

## The 12-month calendar
The themes live in `calendar.json`, one per month, each tied to the retail season:

| Month | Theme | Month | Theme |
|---|---|---|---|
| Oct 26 | All five stores, one link (launch) | Apr 27 | Tax-refund tech |
| Nov 26 | Holiday gifts, shipped | May 27 | Music month |
| Dec 26 | Last-minute gifts | Jun 27 | Father's Day and grads |
| Jan 27 | New year, new tools and tech | Jul 27 | Summer games and gear |
| Feb 27 | Valentine's jewelry and watches | Aug 27 | Back-to-school tech |
| Mar 27 | Spring projects | Sep 27 | Fall projects |

Each month's email features 6 items that are live online at that moment. They're picked automatically from the shop feed:
- Items must match the month's theme.
- Picks rotate across stores so the email shows the whole company.
- Prices stay between $25 and $1,500.
- Weapons, knives and replicas are never featured.

To add a year, append months to `calendar.json` in the same shape.

## How a month gets built
Run `python3 build_month.py --month YYYY-MM` from this folder. It writes `packs/YYYY-MM/`:
- **`email.html`:** cloned from the production master email (campaign 28). All the locked parts stay untouched: logo, per-store "Your store" header, trust strip, 5-store directory with Call and Text buttons showing the number, correct hours, DBA-only footer. Only the hero, body and button change.
- **`push.txt`:** title (40 characters or fewer), body (120 characters or fewer), link and send date.
- **`sms.txt`:** one text of 160 characters or fewer. It includes "Valley Pawn:", the link and "Reply STOP to opt out".
- **`PACK.md`:** send dates, audiences, the tagged links and the featured items.

Adding `--apply` also creates the Brevo email as a draft and checks it after creating it. **The script never schedules or sends.**

The script checks every build automatically and refuses to create a draft if any check fails:
- logo present
- call and text links present for all 5 stores
- phone numbers visible
- no legal entity name and no legacy name
- no weapon words in the body
- button tag present
- shop link present
- push and text within length limits

## In store
Counter signs dropped (Joshua 2026-09-29). The physical/online link lives in the copy: every email tells customers to call or text the store that has the item. The QR/sign files remain in `in_store/` unused.
- **eBay-to-counter rule (from ebay-context):** if a customer wants an item that's listed online, the store sells it in Bravo and ends the eBay listing the same day.

## Compliance (non-negotiable)
- **Texts:** opt-in and opt-out are managed in Chekkit (Joshua 2026-09-29); the lists are not filtered in Bravo.
  - Messages must identify "Valley Pawn", include STOP wording, and go out between 8am and 9pm (handbook §07.06; federal TCPA and the Virginia Telephone Privacy Protection Act both apply to texts).
  - Opt-outs are honored immediately.
  - Marketing texts need consent. A past purchase alone isn't enough.
  - **Joshua 2026-09-29:** stores collect text opt-in; opt-in/opt-out is administered in Chekkit, which suppresses STOP replies.
- **Email:** the CAN-SPAM footer and unsubscribe come from the master email and are never edited.
- **Content:** no firearms, guns, ammo or weapons in any channel. This especially covers Roanoke. The same rule keeps knives and swords out of featured items.
  - No "fast cash" language. No "Dixie Pawn".
  - Precious metal can be featured, but it is never discounted (eBay Rule 4).
- **Frequency:** at most one campaign push and one campaign text per customer per month.
  - If the forfeited-loan win-back goes live, a customer who gets a win-back text that month is skipped for this one.

## Scorecard (read at month end)
| Metric | Where | Healthy |
|---|---|---|
| Shop-page visits by source (brevo / bravo_push / sms / instore) | Google Analytics | Every channel above zero; the trend is what matters |
| Email: button and item clicks, unsubscribes | Brevo campaign report | Button click rate ≥1.5%; unsubscribes under 0.5% |
| Text: STOP replies | Bravo marketing report | Under 1% |
| **Monthly eBay sales, all stores** | Bravo Monthly KPI emails, eBay column | Up against the baseline |

**Baseline:** August 2026 eBay sales were **$29,365**.

| Store | Aug 2026 eBay sales |
|---|---|
| Culpeper | $11,176 |
| Roanoke | $7,775 |
| Lexington | $5,254 |
| Harrisonburg | $3,224 |
| Waynesboro | $1,936 |

How the baseline was measured: taken from the 9/1/2026 Bravo Monthly KPI emails for each store; each store's eBay figure plus its in-store sales equals its total. September's figure arrives 10/1.

## Channels: exactly how each one goes out (updated 2026-09-29)
**Email (Brevo):** fully automatic (see Automation below).

**Text (Chekkit):** `build_text_lists.py` builds one upload list per store every month into `packs/<m>/chekkit_<Store>.csv`.
- Source: Bravo's "Chekkit Invites" exports (phone numbers by store).
- Customers first seen in the last 18 months.
- **Opt-in and opt-out are handled in Chekkit, not Bravo** (Joshua 2026-09-29: "do not filter in bravo"). Bravo's DNT flag is deliberately ignored; Chekkit suppresses anyone who has replied STOP.
- Staff numbers are excluded.
- Each phone goes to one store only.

October: Culpeper 1,467 · Waynesboro 1,264 · Harrisonburg 1,204 · Lexington 585 · Roanoke 1,399 (5,919).

Chekkit steps, per store:
1. Switch location (top-left).
2. Messenger → Campaigns & Scheduled Messages → Create New Campaign → Upload CSV (the store's file).
3. Name it `Shop Online YYYY-MM`.
4. Message = `sms.txt`.
5. Schedule for the 3rd Thursday at 11:00 AM.

- **Cost:** each location includes 2,000 texts a month, then $0.03 each. Expect roughly $0–$45 per store per month in overage.
- **Filtering risk:** Chekkit warns that more than 3,000 a month per location may be filtered.
- **Overlap:** Harrisonburg and Lexington also have a recurring monthly gold text.

**Automated (Joshua approved 2026-09-29):** Cowork scheduled task `ebay-campaign-chekkit-monthly` runs Thursdays at 11:00 AM (Sonnet, pinned) and acts only on the 3rd Thursday (day 15–21).
- It stages the store lists in its own session, then follows the proven `chekkit-weekly-review-requests` upload runbook: Upload CSV → Continue with all → name `Shop Online YYYY-MM` → type sms.txt exactly → Send immediately → check the three compliance boxes → Confirm & Send.
- It writes `packs/<m>/chekkit_sent.json` and posts per-store counts to #chekkit-updates.
- Joshua is the last row of every list, so he receives each store's text as a confirmation copy.
- Failures go to the fleet failure ledger, never to Slack.
- First live run: Thu 2026-10-15.

**Push (Bravo Mobile Messenger):** Bravo's managed service is NOT used; it costs about $1,500/month (Joshua 2026-10-02). Plan: map Bravo's Mobile Messenger screens in a session Joshua schedules, then build a native agent (new pipeline handler + trigger, additive) that sends `push.txt` to all app users on the 2nd Friday. Until then, the push copy is in the monthly DM.

## Automation (how it runs, no one touches it)
Native launchd agent `com.valleypawn.ebay-customer-campaign`, **24th of each month at 09:15**, runner `Valley Pawn OS/bin/ebay_customer_campaign.sh`:
1. Builds next month's pack from the live shop feed (`build_month.py --schedule`).
2. Creates the Brevo email (or reuses it if already there), runs the house preflight `Email Refinement/brevo_preflight.py`, and **schedules it for the 1st Tuesday 10:00 AM ET**. Any failed check leaves it unscheduled and logged; the next run retries.
3. Push + text: Bravo's marketing team sends these for us (they ran the July 2026 MobilePawn SMS campaign). If `config.json` `bravo_request_enabled` is true, `bravo_request.py` emails them the copy, dates and audience rules (cc Joshua). **Currently off, pending Joshua's OK on Bravo's monthly cost.** While off, the monthly DM carries the push + text copy.
4. One plain FYI DM to Joshua. Failures: log only (`~/Library/Logs/valleypawn/ebay-customer-campaign.log`), never Slack (Rule 16).

Installed 2026-09-29 via host queue job `20260929-ebay-customer-campaign-install.sh`, which also ran October as a catch-up. Rollback: `launchctl bootout` the label and rename the plist `.plist.disabled`.

## MobilePawn app block (added 2026-09-29)
Every monthly email carries a "Get the free app" block → thevalleypawn.com/app (utm_content=app_download), switched by `config.json app_block_enabled` (true). The build check refuses a draft if the block is missing while enabled. Full app-outreach program: `MobilePawn Participation/app_outreach/README.md`.
