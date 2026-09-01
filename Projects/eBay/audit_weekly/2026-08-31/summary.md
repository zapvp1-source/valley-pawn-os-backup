# eBay Channel Pulse — 2026-08-31

**Window:** trailing 90 days (2026-06-02 → 2026-08-31) · **Method:** live eBay Trading API, all 5 store
accounts, read-only (`GetMyeBaySelling`, `GetSellerTransactions`, `GetAccount`, `GetStore`, `GetItem`,
`GetMyMessages`, `GetFeedback`, `GetBestOffers`). Nothing on eBay was changed. Listing-quality/TRS/returns
fields verified via a `GetItem` sample (216 of 468 active listings — all stores <40 listings sampled at
100%, Culpeper and Roanoke sampled 60 each) after `GetMyeBaySelling`'s bulk response came back blank on
those fields — same under-reporting class the 2026-08-22 audit hit on item specifics, now confirmed wider.

## Headline

| Metric | This week | vs 2026-08-22 baseline |
|---|---:|---:|
| Active listings | **468** | -46 (-9.0%) |
| Listed value | **$77,974** | -$5,467 |
| Sold, 90d | **573 units / $86,354** | +$4,290 revenue |
| Fees, 90d | **$14,306 (16.6% of revenue)** | +$689, fee % flat |
| Aged >90d | **203 listings / $25,077** | -4 listings / -$2,178 |

## What changed since the 2026-08-22 audit

**Fixed:**
- **Best Offer is now enabled on 100% of the sampled listings at every store, including Culpeper** — the
  8/22 audit found 193 Culpeper listings with it off ($15,372 of inventory with no negotiation path). Gone.
- **No-returns listings are down to 0% in the sample** — 8/22 found 45 listings (mostly Culpeper) with no
  returns accepted at all ($10,932). Gone.
- **Roanoke's return window is now 30 days on 57 of 60 sampled listings** (was 14 days channel-worst on
  8/22); 3 stragglers remain at 14 days.
- **The markdown terminal-action gap is closed.** A new weekly task (`ebay-markdown-terminal-weekly`,
  Mondays 12:15 PM ET) now flags/ends listings that hit the 30%-off cap with no further action — live
  before tomorrow matters: **154 listings sit at their 2nd cut today (Culpeper 101, Roanoke 30,
  Harrisonburg 11, Lexington 7, Waynesboro 5) and take their 3rd/final cut tomorrow, 2026-09-01** — the
  first real test of the new task.

**Still open (unchanged since 8/22, both are Joshua's ops-policy calls, not Claude-executable):**
- **Top Rated Plus eligibility is still 0% channel-wide.** Dispatch time remains 2 days everywhere except
  Roanoke (3 days, worst in channel) — nowhere is at 1-day/same-day. Return shipping is still 100%
  buyer-pays everywhere — free returns is the other TRS Plus requirement. The ~$3,600–5,200/yr fee-discount
  opportunity from 8/22 is unchanged.
- **Promoted Listings still dark at 4 of 5 stores.** Culpeper's ad spend grew to $400.74/90d (was $314);
  Waynesboro, Harrisonburg, Lexington, Roanoke remain at **$0.00**. Matches this week's
  `marketing-ceo-briefing-weekly` cross-lane finding.

## New flags this run

- **4 open Best Offers, all 4 expiring within 48 hours, none answered yet:** Roanoke has 3 expiring
  *today* (8/31, between ~5:40 and 6:01 PM ET, plus one just after midnight into 9/1), and Culpeper has 1
  expiring tomorrow afternoon. Needs a human pricing call now — logged to the Open Items Register.
- **Active listings keep shrinking** — 514 (8/22) → ~490 per this week's marketing-CEO-briefing tracking →
  468 in this live pull. Sell-through and aged-inventory value are stable-to-improving, so this reads as
  net delisting rather than a sales problem, but it's worth a look at why listings are leaving the catalog.
- **9 negative/neutral feedback comments in the trailing 12 months have no seller response** (Culpeper 2,
  Waynesboro 1, Harrisonburg 3, Lexington 3, Roanoke 1) — full text and dates in `summary.json`. Not
  directly comparable to 8/22's "3 open" figure, which used a narrower window; this run measures a full
  12 months as the task spec calls for.
- **eBay Store subscription tier could not be confirmed via `GetStore` this run** — the API response for
  this account no longer includes a `SubscriptionLevel` field. Indirect signal (insertion fees stayed near
  zero — $95.70 across 468 listings/90d) is consistent with the 8/22 finding that all 5 stores carry a
  Store subscription, but this is inference, not a direct read. Flagged for the next session that touches
  `ebay-context`, not treated as confirmed fact.
- **Unread message backlog: 387 across the channel over 60 days**, including 23 unread return/refund
  messages (subject-line classification, so likely an undercount — no case/dispute-labeled subjects
  matched, which doesn't mean zero open cases). Roanoke remains the heaviest at 157 unread.

## Per-store table

| Store | Active | Listed value | Sold 90d (units/$) | Fees 90d | Fee % | Aged >90d ($) | Days-to-sell (median) |
|---|---:|---:|---:|---:|---:|---:|---:|
| Culpeper | 280 | $42,918 | 233 / $28,074 | $4,582 | 16.3% | $19,813 | 18 |
| Waynesboro | 37 | $13,180 | 67 / $13,986 | $1,831 | 13.1% | $0 | 7 |
| Harrisonburg | 31 | $6,765 | 61 / $12,010 | $2,073 | 17.3% | $596 | 2 |
| Lexington | 28 | $5,379 | 59 / $12,303 | $2,600 | 21.1% | $1,098 | 5 |
| Roanoke | 92 | $9,732 | 153 / $19,981 | $3,220 | 16.1% | $3,571 | 8 |
| **Channel** | **468** | **$77,974** | **573 / $86,354** | **$14,306** | **16.6%** | **$25,077** | — |

## Method notes

- No API/pull errors on any of the 5 stores this run — all data below is complete for every store, per
  Rule 18.
- 2026-08-24's run was a partial pull (active/sold-count/fee-count only, no write-up, no Slack post, no
  dashboard refresh) — used only for the active-listing count comparison in the flags above; the
  2026-08-22 full audit remains the baseline for everything else.
- Fee categories this run: Final Value Fee $13,708, Promoted Listings $401, Insertion $96, Return
  shipping $46, Unclassified $56 (channel totals). eBay's `GetAccount` reports FVF under the generic type
  `CustomCode` — confirmed by magnitude match against 8/22's reconstructed FVF figure, not a documented
  field name.
- Not measured (API scope gap, same as 8/22): impressions, click-through, conversion, search placement.
