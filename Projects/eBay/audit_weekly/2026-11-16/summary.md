# eBay Channel Pulse — 2026-11-16

**Window:** trailing 90 days · **Method:** live eBay Trading API, all 5 store accounts, read-only (GetMyeBaySelling, GetSellerTransactions, GetAccount, GetStore, GetItem, GetMyMessages, GetFeedback, GetBestOffers), native Mac run (`Valley Pawn OS/bin/ebay_channel_audit.py`). Nothing on eBay was changed. Listing-quality fields come from a GetItem sample (222 listings), not the bulk pull. Week-over-week base: 2026-11-09.

## Slack post (as sent)

```
eBay Channel Pulse — 2026-11-16 (weekly, trailing 90d, all 5 stores, read-only)

Headline: 369 active listings / $63,677 listed value · 533 sold units / $94,877 revenue (90d) · fees $14,988 (15.8% of revenue) · 195 listings aged >90d ($31,025) · 210 unread messages (14 return/refund)

Holding steady: no-returns 0% (GetItem-sample verified, 222 listings).

Still open (ops-policy calls, not automated): TRS Plus eligibility still 0% channel-wide (dispatch time + free returns). Promoted Listings ~$0 at 4 of 5 stores (Waynesboro, Harrisonburg, Lexington, Roanoke).

New this week:
• vs 2026-11-09: active -23, listed value -$2,170, 90d revenue -$3,752, fee % -0.3pt, aged >90d +10 / +$7,460, unread +9
• 2 open Best Offers expiring within 48 h (Roanoke x2) — none answered yet, needs a pricing call.
• 95 listings sit at their 3rd markdown cut with no further scheduled action (Culpeper 73, Harrisonburg 5, Lexington 1, Roanoke 16).
• 7 video-game / console / game-accessory listings in the sample take offers (Culpeper 3, Waynesboro 2, Harrisonburg 1, Roanoke 1) — the standing rule is no offers on video games; store's call to switch off, not changed here.
• 1 new negative/neutral feedback since 2026-11-09 (Culpeper).
• 3 unread case/dispute-subject messages.

Full writeup: Projects/eBay/audit_weekly/2026-11-16/summary.md
```

## Per-store table

| Store | Active | Listed value | Sold 90d (units/$) | Fees 90d | Fee % | Aged >90d ($) | Days-to-sell (median) |
|---|---:|---:|---:|---:|---:|---:|---:|
| Culpeper | 174 | $27,162 | 226 / $28,854 | $4,386 | 15.2% | $21,573 (133 listings) | 60.0 |
| Waynesboro | 63 | $12,395 | 50 / $25,296 | $3,396 | 13.4% | $2,365 (20 listings) | 4.5 |
| Harrisonburg | 22 | $7,556 | 29 / $8,512 | $1,832 | 21.5% | $3,137 (11 listings) | 6 |
| Lexington | 20 | $3,343 | 64 / $12,573 | $2,203 | 17.5% | $964 (8 listings) | 1.5 |
| Roanoke | 90 | $13,221 | 164 / $19,642 | $3,171 | 16.1% | $2,986 (23 listings) | 7.5 |
| **Channel** | **369** | **$63,677** | **533 / $94,877** | **$14,988** | **15.8%** | **$31,025 (195)** | — |

## Listing quality (GetItem sample)

| Store | Sample | Best Offer on | No-returns | TRS-eligible | Avg photos | Dispatch | Return shipping paid by |
|---|---:|---:|---:|---:|---:|---|---|
| Culpeper | 60 | 48.3% | 0.0% | 0.0% | 6.1 | {'2': 57, '1': 1, 'unknown': 2} | {'Buyer': 60} |
| Waynesboro | 60 | 46.7% | 0.0% | 0.0% | 4.8 | {'2': 60} | {'Buyer': 60} |
| Harrisonburg | 22 | 90.9% | 0.0% | 0.0% | 6.3 | {'2': 22} | {'Buyer': 22} |
| Lexington | 20 | 95.0% | 0.0% | 0.0% | 6.5 | {'2': 20} | {'Buyer': 20} |
| Roanoke | 60 | 83.3% | 0.0% | 0.0% | 4.4 | {'3': 58, 'unknown': 2} | {'Buyer': 60} |

## Reputation, offers, messages

- Culpeper: score 1384, positive 1/6/12 mo 96.2/98.5/98.5%, neg/neutral without a reply field 3, open Best Offers 0 (0 expiring 48 h), unread 57 (4 return/refund, 0 case)
- Waynesboro: score 655, positive 1/6/12 mo 100.0/100.0/99.5%, neg/neutral without a reply field 1, open Best Offers 0 (0 expiring 48 h), unread 47 (0 return/refund, 1 case)
- Harrisonburg: score 639, positive 1/6/12 mo 100.0/98.6/98.6%, neg/neutral without a reply field 2, open Best Offers 0 (0 expiring 48 h), unread 9 (0 return/refund, 0 case)
- Lexington: score 1325, positive 1/6/12 mo 100.0/100.0/99.0%, neg/neutral without a reply field 2, open Best Offers 0 (0 expiring 48 h), unread 19 (2 return/refund, 0 case)
- Roanoke: score 5816, positive 1/6/12 mo 100.0/99.5/99.5%, neg/neutral without a reply field 1, open Best Offers 2 (2 expiring 48 h), unread 78 (8 return/refund, 2 case)

## Fees by category (90d, channel)

```
{
 "final_value_fee": 14411.72,
 "promoted_listings": 413.46,
 "insertion": 65.6,
 "other": 83.25,
 "return_shipping": 13.81
}
```

## Method notes

- Feedback 'no seller response' is a known GetFeedback gap (replies sent via RespondToFeedback don't always show); the reliable record is ~/ebay_feedback_answered.json. Read the count as a ceiling, not a trend.
- Not measured (API scope gap): impressions, click-through, conversion, seller level / Top Rated (see the monthly ratings sweep).
- The claude.ai 'eBay Channel Pulse' artifact is NOT refreshed by this native run (a Mac script cannot publish it).
- Store errors: none
