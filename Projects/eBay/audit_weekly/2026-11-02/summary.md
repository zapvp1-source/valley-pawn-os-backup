# eBay Channel Pulse — 2026-11-02

**Window:** trailing 90 days · **Method:** live eBay Trading API, all 5 store accounts, read-only (GetMyeBaySelling, GetSellerTransactions, GetAccount, GetStore, GetItem, GetMyMessages, GetFeedback, GetBestOffers), native Mac run (`Valley Pawn OS/bin/ebay_channel_audit.py`). Nothing on eBay was changed. Listing-quality fields come from a GetItem sample (228 listings), not the bulk pull. Week-over-week base: 2026-10-26.

## Slack post (as sent)

```
eBay Channel Pulse — 2026-11-02 (weekly, trailing 90d, all 5 stores, read-only)

Headline: 407 active listings / $67,035 listed value · 562 sold units / $100,471 revenue (90d) · fees $16,348 (16.3% of revenue) · 183 listings aged >90d ($22,293) · 182 unread messages (9 return/refund)

Holding steady: no-returns 0% (GetItem-sample verified, 228 listings).

Still open (ops-policy calls, not automated): TRS Plus eligibility still 0% channel-wide (dispatch time + free returns). Promoted Listings ~$0 at 4 of 5 stores (Waynesboro, Harrisonburg, Lexington, Roanoke).

New this week:
• vs 2026-10-26: active +42, listed value +$4,111, 90d revenue +$7,139, fee % -0.2pt, aged >90d +1 / -$627, unread -24
• 5 open Best Offers expiring within 48 h (Harrisonburg x1, Lexington x1, Roanoke x3) — none answered yet, needs a pricing call.
• 101 listings sit at their 3rd markdown cut with no further scheduled action (Culpeper 76, Harrisonburg 6, Lexington 2, Roanoke 17).
• 9 video-game / console / game-accessory listings in the sample take offers (Culpeper 2, Waynesboro 3, Harrisonburg 3, Roanoke 1) — the standing rule is no offers on video games; store's call to switch off, not changed here.
• 5 unread case/dispute-subject messages.

Full writeup: Projects/eBay/audit_weekly/2026-11-02/summary.md
```

## Per-store table

| Store | Active | Listed value | Sold 90d (units/$) | Fees 90d | Fee % | Aged >90d ($) | Days-to-sell (median) |
|---|---:|---:|---:|---:|---:|---:|---:|
| Culpeper | 192 | $24,904 | 249 / $32,659 | $4,994 | 15.3% | $15,721 (124 listings) | 54 |
| Waynesboro | 70 | $17,246 | 45 / $21,319 | $2,911 | 13.7% | $1,282 (8 listings) | 4 |
| Harrisonburg | 27 | $7,731 | 29 / $9,979 | $2,178 | 21.8% | $992 (15 listings) | 2 |
| Lexington | 21 | $3,584 | 65 / $15,279 | $2,841 | 18.6% | $1,029 (9 listings) | 2 |
| Roanoke | 97 | $13,570 | 174 / $21,235 | $3,424 | 16.1% | $3,269 (27 listings) | 6.5 |
| **Channel** | **407** | **$67,035** | **562 / $100,471** | **$16,348** | **16.3%** | **$22,293 (183)** | — |

## Listing quality (GetItem sample)

| Store | Sample | Best Offer on | No-returns | TRS-eligible | Avg photos | Dispatch | Return shipping paid by |
|---|---:|---:|---:|---:|---:|---|---|
| Culpeper | 60 | 40.0% | 0.0% | 0.0% | 6.0 | {'1': 1, '2': 58, 'unknown': 1} | {'Buyer': 60} |
| Waynesboro | 60 | 50.0% | 0.0% | 0.0% | 4.9 | {'2': 60} | {'Buyer': 60} |
| Harrisonburg | 27 | 85.2% | 0.0% | 0.0% | 6.3 | {'2': 27} | {'Buyer': 27} |
| Lexington | 21 | 95.2% | 0.0% | 0.0% | 6.4 | {'2': 21} | {'Buyer': 21} |
| Roanoke | 60 | 96.7% | 0.0% | 0.0% | 4.3 | {'3': 60} | {'Buyer': 60} |

## Reputation, offers, messages

- Culpeper: score 1364, positive 1/6/12 mo 100.0/99.0/99.0%, neg/neutral without a reply field 2, open Best Offers 0 (0 expiring 48 h), unread 53 (4 return/refund, 2 case)
- Waynesboro: score 643, positive 1/6/12 mo 100.0/100.0/99.5%, neg/neutral without a reply field 1, open Best Offers 0 (0 expiring 48 h), unread 40 (0 return/refund, 1 case)
- Harrisonburg: score 635, positive 1/6/12 mo 100.0/98.5/98.6%, neg/neutral without a reply field 2, open Best Offers 1 (1 expiring 48 h), unread 9 (0 return/refund, 0 case)
- Lexington: score 1315, positive 1/6/12 mo 100.0/100.0/99.0%, neg/neutral without a reply field 2, open Best Offers 1 (1 expiring 48 h), unread 8 (0 return/refund, 0 case)
- Roanoke: score 5801, positive 1/6/12 mo 98.4/99.5/99.5%, neg/neutral without a reply field 1, open Best Offers 3 (3 expiring 48 h), unread 72 (5 return/refund, 2 case)

## Fees by category (90d, channel)

```
{
 "insertion": 65.6,
 "final_value_fee": 15734.69,
 "promoted_listings": 450.42,
 "other": 83.25,
 "return_shipping": 13.81
}
```

## Method notes

- Feedback 'no seller response' is a known GetFeedback gap (replies sent via RespondToFeedback don't always show); the reliable record is ~/ebay_feedback_answered.json. Read the count as a ceiling, not a trend.
- Not measured (API scope gap): impressions, click-through, conversion, seller level / Top Rated (see the monthly ratings sweep).
- The claude.ai 'eBay Channel Pulse' artifact is NOT refreshed by this native run (a Mac script cannot publish it).
- Store errors: none
