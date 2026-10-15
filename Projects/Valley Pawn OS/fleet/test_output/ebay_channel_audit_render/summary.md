# eBay Channel Pulse — 2026-10-14

**Window:** trailing 90 days · **Method:** live eBay Trading API, all 5 store accounts, read-only (GetMyeBaySelling, GetSellerTransactions, GetAccount, GetStore, GetItem, GetMyMessages, GetFeedback, GetBestOffers), native Mac run (`Valley Pawn OS/bin/ebay_channel_audit.py`). Nothing on eBay was changed. Listing-quality fields come from a GetItem sample (205 listings), not the bulk pull. Week-over-week base: 2026-09-07.

## Slack post (as sent)

```
eBay Channel Pulse — 2026-10-14 (weekly, trailing 90d, all 5 stores, read-only)

Headline: 373 active listings / $63,383 listed value · 585 sold units / $87,629 revenue (90d) · fees $15,026 (17.1% of revenue) · 172 listings aged >90d ($18,663) · 236 unread messages (21 return/refund)

Still open (ops-policy calls, not automated): TRS Plus eligibility still 0% channel-wide (dispatch time + free returns). Promoted Listings ~$0 at 4 of 5 stores (Waynesboro, Harrisonburg, Lexington, Roanoke).

New this week:
• vs 2026-09-07: active -73, listed value -$8,081, 90d revenue +$867, fee % +0.4pt, aged >90d -27 / -$1,482, unread -146
• 1 open Best Offer expiring within 48 h (Roanoke x1) — none answered yet, needs a pricing call.
• 104 listings sit at their 3rd markdown cut with no further scheduled action (Culpeper 84, Harrisonburg 4, Lexington 2, Roanoke 14).
• 35 video-game / console / game-accessory listings in the sample take offers (Culpeper 16, Waynesboro 7, Harrisonburg 7, Lexington 2, Roanoke 3) — the standing rule is no offers on video games; store's call to switch off, not changed here.
• No-returns listings back in the sample: Culpeper 1, Harrisonburg 1.
• 14-day-return listings in the sample: Roanoke 3 (template default, not fixed at the source).
• 2 new negative/neutral feedback since 2026-09-07 (Culpeper, Roanoke).
• 6 unread case/dispute-subject messages.

Full writeup: Projects/eBay/audit_weekly/2026-10-14/summary.md
```

## Per-store table

| Store | Active | Listed value | Sold 90d (units/$) | Fees 90d | Fee % | Aged >90d ($) | Days-to-sell (median) |
|---|---:|---:|---:|---:|---:|---:|---:|
| Culpeper | 192 | $27,593 | 264 / $32,809 | $5,311 | 16.2% | $12,164 (112 listings) | 52.0 |
| Waynesboro | 37 | $14,220 | 36 / $8,493 | $1,300 | 15.3% | $1,016 (9 listings) | 13.0 |
| Harrisonburg | 23 | $4,260 | 32 / $9,119 | $1,903 | 20.9% | $1,060 (14 listings) | 24.5 |
| Lexington | 25 | $5,150 | 65 / $14,476 | $2,849 | 19.7% | $1,011 (6 listings) | 3 |
| Roanoke | 96 | $12,159 | 188 / $22,732 | $3,663 | 16.1% | $3,412 (31 listings) | 6.0 |
| **Channel** | **373** | **$63,383** | **585 / $87,629** | **$15,026** | **17.1%** | **$18,663 (172)** | — |

## Listing quality (GetItem sample)

| Store | Sample | Best Offer on | No-returns | TRS-eligible | Avg photos | Dispatch | Return shipping paid by |
|---|---:|---:|---:|---:|---:|---|---|
| Culpeper | 60 | 95.0% | 1.7% | 0.0% | 6.3 | {'2': 60} | {'Buyer': 59, 'unknown': 1} |
| Waynesboro | 37 | 100.0% | 0.0% | 0.0% | 6.6 | {'2': 36, 'unknown': 1} | {'Buyer': 37} |
| Harrisonburg | 23 | 100.0% | 4.3% | 0.0% | 5.8 | {'2': 23} | {'Buyer': 22, 'unknown': 1} |
| Lexington | 25 | 100.0% | 0.0% | 0.0% | 6.8 | {'2': 25} | {'Buyer': 25} |
| Roanoke | 60 | 100.0% | 0.0% | 0.0% | 4.2 | {'3': 60} | {'Buyer': 60} |

## Reputation, offers, messages

- Culpeper: score 1338, positive 1/6/12 mo 98.9/99.0/99.0%, neg/neutral without a reply field 2, open Best Offers 0 (0 expiring 48 h), unread 51 (6 return/refund, 3 case)
- Waynesboro: score 636, positive 1/6/12 mo 100.0/100.0/99.5%, neg/neutral without a reply field 1, open Best Offers 0 (0 expiring 48 h), unread 63 (4 return/refund, 1 case)
- Harrisonburg: score 629, positive 1/6/12 mo 100.0/98.4/98.6%, neg/neutral without a reply field 3, open Best Offers 0 (0 expiring 48 h), unread 12 (0 return/refund, 0 case)
- Lexington: score 1300, positive 1/6/12 mo 100.0/100.0/99.0%, neg/neutral without a reply field 2, open Best Offers 0 (0 expiring 48 h), unread 3 (0 return/refund, 0 case)
- Roanoke: score 5764, positive 1/6/12 mo 98.2/99.0/99.0%, neg/neutral without a reply field 2, open Best Offers 1 (1 expiring 48 h), unread 107 (11 return/refund, 2 case)

## Fees by category (90d, channel)

```
{
 "insertion": 107.3,
 "final_value_fee": 14235.71,
 "promoted_listings": 571.22,
 "other": 83.25,
 "return_shipping": 28.73
}
```

## Method notes

- Feedback 'no seller response' is a known GetFeedback gap (replies sent via RespondToFeedback don't always show); the reliable record is ~/ebay_feedback_answered.json. Read the count as a ceiling, not a trend.
- Not measured (API scope gap): impressions, click-through, conversion, seller level / Top Rated (see the monthly ratings sweep).
- The claude.ai 'eBay Channel Pulse' artifact is NOT refreshed by this native run (a Mac script cannot publish it).
- Store errors: none
