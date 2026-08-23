# FFL LISTINGS — STATUS

Where Valley Pawn's five FFLs appear (or don't) across dealer directories, transfer locators,
and wholesale vendor networks. Paired with `FFL_REGISTRY.md` (canonical license data).

**Last full pass: 2026-08-22.** Prior passes: 2026-04-24 (vendor campaign), 2026-08 (directory
audit, delivered as a Word doc that was never saved into the repo).

> **Why this file exists.** This work has been done at least three times by three different
> sessions with no durable artifact between them. The April campaign's tracker
> (`Valley_Pawn_FFL_Listing_Tracker.xlsx`) and plan doc, and the August audit's Word summary,
> all lived in session output folders that no longer exist. Each new session therefore started
> from zero and re-audited ground already covered. **This file is the memory. Update it, don't
> replace it.**

---

## The thing that actually costs money

On **2026-04-29** a customer, Jordan Culbertson, emailed Joshua:

> *"You are not listed with grabagun.com on their list of FFLs."*

He had orders sitting at GrabAGun and BattleHawk and could not select Valley Pawn as his
receiving dealer. That is the whole business case in one message: when Valley Pawn isn't in a
retailer's FFL locator, the customer picks a different dealer, and the $30 transfer plus the
walk-in traffic goes somewhere else. Directory presence is not a marketing nicety here — it is
the order-routing layer for the transfer business.

Counterweight: inbound transfers **are** flowing through GunBroker/MasterFFL at a steady clip
(a dozen-plus "FFL Transfer Complete" confirmations between Jan and Aug 2026). So the channel
works where Valley Pawn is listed. The gap is coverage, not viability.

---

## State by channel

### Tier A — retailer FFL locators (where customers pick a dealer)

| Vendor | Contact used | Status | Note |
|---|---|---|---|
| GrabAGun | FFL@grabagun.com | **Listed** (transfers received 2026-07-05) | Zendesk #1769057 from the 4/24 submission. Holds a **stale Culpeper FFL copy** — sent expiration warnings 7/31 and 8/16 |
| Impact Guns | sales@impactguns.com | Replied 4/24 and 4/28 (Zendesk) — outcome unconfirmed | Verify against their public locator |
| Brownells | ffl@brownells.com | **In flight** — Featured FFL Dealer Registration for Harrisonburg, 10 questions answered 2026-08-04 | Only Harrisonburg was submitted; the other four still need it |
| Primary Arms | ffl@primaryarms.com | Transfers observed (Culpeper, 4/28) — listing status unconfirmed | |
| KYGUNCO | FFL@kygunco.com | Submitted 4/24, no reply found | Follow up |
| BattleHawk Armory | FFL@BHArmory.com | Submitted 4/24, no reply found | Customer had an order here 4/29 |
| MidwayUSA | csffl2@midwayusa.com | **Inbound request unanswered** — MidwayUSA emailed 2026-08-01 *"Please Update Your FFL Information"* with a registration link | Easiest win on the board; they asked us |
| Buds Gun Shop / PSA / Classic / AIM / Rainier | forms + accounts | Not started | Tabled in April pending Tier A results |
| Guns.com Dealer Network | dealers.guns.com | Not started | Also opens consignment |
| Sportsman's Warehouse Local FFL | — | Not started | Free, but each store must be 40+ min from a SW retail store — run the radius check first |

### Tier B — dealer directories (SEO + discovery)

| Directory | Status as of the August audit | Note |
|---|---|---|
| FFLs.com | Correct, all five stores | Nothing to do |
| MasterFFL.com | All five show "Valley Pawn" — **all profiles unclaimed** | This is the GunBroker back end; every transfer email carries a *"Claim Your Master FFL Dealer Profile"* link. Claiming here is high-leverage |
| GunBroker / MyFFL | Harrisonburg still shows **"DIXIE PAWN"** | Legacy name |
| FFLeasy.com | Legacy **"DIXIE PAWN INC"** listing for Harrisonburg (`ffleasy.com/virginia/harrisonburg/9854`), other four missing entirely | Claim flow needs the FFL number |
| GunNook.com | Harrisonburg submitted 2026-07-31 — **two dealer card URLs appear in the confirmations** (`valley-pawn-harrisonburg-va` and `valley-pawn-harrisonburg-va-2`), suggesting a duplicate submission. All GunNook mail landed in **Spam** | Verify and merge/remove the duplicate; whitelist support@gunnook.com |
| FFL Registry, FFL Dealer Network, FFLGunDealers.net, GunStoresNearby | Not started | Each needs an account |

### Legacy "Dixie Pawn" remnants — treat as one problem, not many

Dixie Pawn shows up on FFLeasy, GunBroker/MyFFL, and (per the 2026-08-21 AI-search audit)
MapQuest and Apple Maps. The MapQuest listing carries a **Yext "PowerListings Synced" badge**,
meaning an old Yext syndication feed is still republishing the dead name. Killing the feed at
Yext is worth more than correcting listings one at a time — and the FFL directories should be
checked for the same upstream source before anyone hand-edits them.

Never use "Dixie Pawn" in any new submission (hard rule, `valley-pawn-context`).

---

## Open actions, highest value first

1. **Re-scan the renewed Culpeper license and push the new copy to every vendor of record**
   (GrabAGun first — they have flagged it twice). Vendors holding the old copy think Culpeper
   expires 2026-09-01. *(No account creation required — email attachment.)*
2. **Resend corrected dealer applications** to anyone who got the 2026-05-04 table with the two
   wrong FFL numbers and the wrong license type. See `FFL_REGISTRY.md` → "Known bad data".
3. **Answer MidwayUSA's 2026-08-01 FFL-information request.** They initiated it; lowest
   friction listing on the board.
4. **Claim the five MasterFFL profiles.** Claim links arrive in every GunBroker transfer email.
   This is the same back end that shows "Dixie Pawn" for Harrisonburg — one claim fixes the name
   and unlocks the profile.
5. **Extend Brownells' Featured Dealer registration to the other four stores** — Harrisonburg's
   registration answers from 2026-08-04 are the template.
6. **Fix the GunNook Harrisonburg duplicate**, submit the other four stores, and un-Spam
   support@gunnook.com.
7. **Claim FFLeasy Harrisonburg** (`/virginia/harrisonburg/9854`, needs the FFL number) and add
   the four missing stores. Paginated results use hash anchors, not query params — click "Page
   2" in-browser; `site:ffleasy.com "<store name>"` surfaces hidden listings.
8. **Check whether Yext is feeding the FFL directories too**, not just MapQuest.
9. **Decide the ATF mailing-address question** (see `FFL_REGISTRY.md`) before Roanoke's renewal
   form mails ≈2026-10-03.

Items 1–3 need no new accounts. Items 4–7 need logins on third-party sites; Chrome saved
credentials cover most, and per standing rules Claude drives those rather than handing them back.

---

## Monitoring — recommendation, not yet built

There is **no monitoring of any kind** on the FFL directories. `directory-listing-monitor`
covers Google Business Profile, Bing, Apple, Facebook and Yelp only — the channels that drive
walk-in search, not the ones that route firearm transfers. Nothing watches FFL expirations
either; the Culpeper near-miss was caught by a human noticing missing mail.

**Recommended shape — do not add a new scheduled task.** The fleet is already running ~128
scheduled tasks against a usage cap that was producing 150–250 skipped runs a day as recently
as 2026-08-21. Adding a 129th task to check a list that changes a few times a year is the wrong
trade. Instead:

- **Extend `directory-listing-monitor`** (already weekly, already does NAP drift) with an FFL
  block: eZ Check each of the five licenses, diff against `FFL_REGISTRY.md`, and check the
  MasterFFL / FFLeasy / GunBroker public pages for the strings "Dixie" and "Valley Pawn".
  Zero new tasks, zero new cap pressure.
- **Alert thresholds:** any license inside 120 days of expiration; any eZ Check result that
  doesn't match this file; any "Dixie" string found anywhere.
- **Roanoke is the live one** — 2027-01-01, renewal form mails ≈2026-10-03 to the Florida
  address.
