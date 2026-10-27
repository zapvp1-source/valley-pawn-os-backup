# eBay Channel Pulse — 2026-10-26

**Window:** trailing 90 days · **Method:** live eBay Trading API, all 5 store accounts, read-only (GetMyeBaySelling, GetSellerTransactions, GetAccount, GetStore, GetItem, GetMyMessages, GetFeedback, GetBestOffers), native Mac run (`Valley Pawn OS/bin/ebay_channel_audit.py`). Nothing on eBay was changed. Listing-quality fields come from a GetItem sample (202 listings), not the bulk pull. Week-over-week base: 2026-10-21.

## Slack post (as sent)

```
eBay Channel Pulse — 2026-10-26 (weekly, trailing 90d, all 5 stores, read-only)

Headline: 365 active listings / $62,924 listed value · 559 sold units / $93,333 revenue (90d) · fees $15,390 (16.5% of revenue) · 182 listings aged >90d ($22,920) · 206 unread messages (13 return/refund)

Holding steady: no-returns 0% (GetItem-sample verified, 202 listings).

Still open (ops-policy calls, not automated): TRS Plus eligibility still 0% channel-wide (dispatch time + free returns). Promoted Listings ~$0 at 4 of 5 stores (Waynesboro, Harrisonburg, Lexington, Roanoke).

New this week:
• vs 2026-10-21: active -5, listed value +$2,424, 90d revenue -$139, fee % -0.1pt, aged >90d +5 / +$3,075, unread -26
• 2 open Best Offers expiring within 48 h (Roanoke x2) — none answered yet, needs a pricing call.
• 98 listings sit at their 3rd markdown cut with no further scheduled action (Culpeper 78, Harrisonburg 4, Lexington 2, Roanoke 14).
• 8 video-game / console / game-accessory listings in the sample take offers (Culpeper 1, Waynesboro 3, Harrisonburg 3, Roanoke 1) — the standing rule is no offers on video games; store's call to switch off, not changed here.
• 5 unread case/dispute-subject messages.

Full writeup: Projects/eBay/audit_weekly/2026-10-26/summary.md
```

## Per-store table

| Store | Active | Listed value | Sold 90d (units/$) | Fees 90d | Fee % | Aged >90d ($) | Days-to-sell (median) |
|---|---:|---:|---:|---:|---:|---:|---:|
| Culpeper | 181 | $25,191 | 252 / $30,875 | $4,732 | 15.3% | $15,686 (121 listings) | 58.5 |
| Waynesboro | 39 | $13,395 | 32 / $15,761 | $2,203 | 14.0% | $1,526 (9 listings) | 6.5 |
| Harrisonburg | 24 | $5,990 | 29 / $9,625 | $2,073 | 21.5% | $1,090 (15 listings) | 3 |
| Lexington | 19 | $4,000 | 66 / $15,221 | $2,860 | 18.8% | $1,116 (9 listings) | 2.5 |
| Roanoke | 102 | $14,348 | 180 / $21,852 | $3,521 | 16.1% | $3,502 (28 listings) | 6.0 |
| **Channel** | **365** | **$62,924** | **559 / $93,333** | **$15,390** | **16.5%** | **$22,920 (182)** | — |

## Listing quality (GetItem sample)

| Store | Sample | Best Offer on | No-returns | TRS-eligible | Avg photos | Dispatch | Return shipping paid by |
|---|---:|---:|---:|---:|---:|---|---|
| Culpeper | 60 | 41.7% | 0.0% | 0.0% | 6.3 | {'2': 59, '1': 1} | {'Buyer': 60} |
| Waynesboro | 39 | 94.9% | 0.0% | 0.0% | 7.2 | {'2': 39} | {'Buyer': 39} |
| Harrisonburg | 24 | 87.5% | 0.0% | 0.0% | 6.0 | {'2': 24} | {'Buyer': 24} |
| Lexington | 19 | 94.7% | 0.0% | 0.0% | 6.6 | {'2': 19} | {'Buyer': 19} |
| Roanoke | 60 | 98.3% | 0.0% | 0.0% | 4.2 | {'3': 59, 'unknown': 1} | {'Buyer': 60} |

## Reputation, offers, messages

- Culpeper: score 1359, positive 1/6/12 mo 100.0/99.0/99.0%, neg/neutral without a reply field 2, open Best Offers 0 (0 expiring 48 h), unread 59 (6 return/refund, 2 case)
- Waynesboro: score 639, positive 1/6/12 mo 100.0/100.0/99.5%, neg/neutral without a reply field 1, open Best Offers 0 (0 expiring 48 h), unread 39 (0 return/refund, 1 case)
- Harrisonburg: score 633, positive 1/6/12 mo 100.0/98.5/98.6%, neg/neutral without a reply field 2, open Best Offers 0 (0 expiring 48 h), unread 25 (0 return/refund, 0 case)
- Lexington: score 1310, positive 1/6/12 mo 100.0/100.0/99.0%, neg/neutral without a reply field 2, open Best Offers 0 (0 expiring 48 h), unread 5 (0 return/refund, 0 case)
- Roanoke: score 5790, positive 1/6/12 mo 98.5/99.5/99.5%, neg/neutral without a reply field 1, open Best Offers 2 (2 expiring 48 h), unread 78 (7 return/refund, 2 case)

## Fees by category (90d, channel)

```
{
 "insertion": 74.9,
 "final_value_fee": 14761.63,
 "promoted_listings": 456.47,
 "other": 83.25,
 "return_shipping": 13.81
}
```

## Method notes

- Feedback 'no seller response' is a known GetFeedback gap (replies sent via RespondToFeedback don't always show); the reliable record is ~/ebay_feedback_answered.json. Read the count as a ceiling, not a trend.
- Not measured (API scope gap): impressions, click-through, conversion, seller level / Top Rated (see the monthly ratings sweep).
- The claude.ai 'eBay Channel Pulse' artifact is NOT refreshed by this native run (a Mac script cannot publish it).
- Store errors: none
