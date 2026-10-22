# eBay Channel Pulse — 2026-10-21

**Window:** trailing 90 days · **Method:** live eBay Trading API, all 5 store accounts, read-only (GetMyeBaySelling, GetSellerTransactions, GetAccount, GetStore, GetItem, GetMyMessages, GetFeedback, GetBestOffers), native Mac run (`Valley Pawn OS/bin/ebay_channel_audit.py`). Nothing on eBay was changed. Listing-quality fields come from a GetItem sample (204 listings), not the bulk pull. Week-over-week base: 2026-09-07.

## Slack post (as sent)

```
eBay Channel Pulse — 2026-10-21 (weekly, trailing 90d, all 5 stores, read-only)

Headline: 370 active listings / $60,500 listed value · 569 sold units / $93,472 revenue (90d) · fees $15,520 (16.6% of revenue) · 177 listings aged >90d ($19,845) · 232 unread messages (18 return/refund)

Still open (ops-policy calls, not automated): TRS Plus eligibility still 0% channel-wide (dispatch time + free returns). Promoted Listings ~$0 at 4 of 5 stores (Waynesboro, Harrisonburg, Lexington, Roanoke).

New this week:
• vs 2026-09-07: active -76, listed value -$10,965, 90d revenue +$6,709, fee % -0.1pt, aged >90d -22 / -$300, unread -150
• 3 open Best Offers expiring within 48 h (Culpeper x1, Harrisonburg x1, Roanoke x1) — none answered yet, needs a pricing call.
• 102 listings sit at their 3rd markdown cut with no further scheduled action (Culpeper 82, Harrisonburg 4, Lexington 2, Roanoke 14).
• 28 video-game / console / game-accessory listings in the sample take offers (Culpeper 11, Waynesboro 8, Harrisonburg 5, Lexington 2, Roanoke 2) — the standing rule is no offers on video games; store's call to switch off, not changed here.
• No-returns listings back in the sample: Culpeper 1.
• 14-day-return listings in the sample: Roanoke 5 (template default, not fixed at the source).
• 2 new negative/neutral feedback since 2026-09-07 (Culpeper, Roanoke).
• 6 unread case/dispute-subject messages.

Full writeup: Projects/eBay/audit_weekly/2026-10-21/summary.md
```

## Per-store table

| Store | Active | Listed value | Sold 90d (units/$) | Fees 90d | Fee % | Aged >90d ($) | Days-to-sell (median) |
|---|---:|---:|---:|---:|---:|---:|---:|
| Culpeper | 186 | $26,708 | 254 / $29,542 | $4,676 | 15.8% | $12,678 (115 listings) | 52.0 |
| Waynesboro | 42 | $13,050 | 31 / $16,072 | $2,243 | 14.0% | $1,736 (11 listings) | 7 |
| Harrisonburg | 21 | $4,190 | 31 / $9,312 | $1,972 | 21.2% | $1,050 (14 listings) | 6 |
| Lexington | 21 | $4,140 | 66 / $15,134 | $2,868 | 18.9% | $811 (6 listings) | 2.5 |
| Roanoke | 100 | $12,412 | 187 / $23,412 | $3,761 | 16.1% | $3,570 (31 listings) | 6 |
| **Channel** | **370** | **$60,500** | **569 / $93,472** | **$15,520** | **16.6%** | **$19,845 (177)** | — |

## Listing quality (GetItem sample)

| Store | Sample | Best Offer on | No-returns | TRS-eligible | Avg photos | Dispatch | Return shipping paid by |
|---|---:|---:|---:|---:|---:|---|---|
| Culpeper | 60 | 96.7% | 1.7% | 0.0% | 6.6 | {'2': 59, 'unknown': 1} | {'Buyer': 59, 'unknown': 1} |
| Waynesboro | 42 | 100.0% | 0.0% | 0.0% | 7.0 | {'2': 42} | {'Buyer': 42} |
| Harrisonburg | 21 | 100.0% | 0.0% | 0.0% | 5.9 | {'2': 21} | {'Buyer': 21} |
| Lexington | 21 | 100.0% | 0.0% | 0.0% | 6.4 | {'2': 21} | {'Buyer': 21} |
| Roanoke | 60 | 100.0% | 0.0% | 0.0% | 4.2 | {'3': 60} | {'Buyer': 60} |

## Reputation, offers, messages

- Culpeper: score 1351, positive 1/6/12 mo 100.0/99.0/99.0%, neg/neutral without a reply field 2, open Best Offers 1 (1 expiring 48 h), unread 62 (6 return/refund, 3 case)
- Waynesboro: score 637, positive 1/6/12 mo 100.0/100.0/99.5%, neg/neutral without a reply field 1, open Best Offers 0 (0 expiring 48 h), unread 43 (2 return/refund, 1 case)
- Harrisonburg: score 633, positive 1/6/12 mo 100.0/98.5/98.6%, neg/neutral without a reply field 2, open Best Offers 1 (1 expiring 48 h), unread 22 (0 return/refund, 0 case)
- Lexington: score 1307, positive 1/6/12 mo 100.0/100.0/99.0%, neg/neutral without a reply field 2, open Best Offers 0 (0 expiring 48 h), unread 2 (0 return/refund, 0 case)
- Roanoke: score 5782, positive 1/6/12 mo 98.5/99.5/99.5%, neg/neutral without a reply field 1, open Best Offers 1 (1 expiring 48 h), unread 103 (10 return/refund, 2 case)

## Fees by category (90d, channel)

```
{
 "insertion": 95.3,
 "final_value_fee": 14858.19,
 "promoted_listings": 454.26,
 "other": 83.25,
 "return_shipping": 28.73
}
```

## Method notes

- Feedback 'no seller response' is a known GetFeedback gap (replies sent via RespondToFeedback don't always show); the reliable record is ~/ebay_feedback_answered.json. Read the count as a ceiling, not a trend.
- Not measured (API scope gap): impressions, click-through, conversion, seller level / Top Rated (see the monthly ratings sweep).
- The claude.ai 'eBay Channel Pulse' artifact is NOT refreshed by this native run (a Mac script cannot publish it).
- Store errors: none
