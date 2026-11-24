# eBay Channel Pulse — 2026-11-23

**Window:** trailing 90 days · **Method:** live eBay Trading API, all 5 store accounts, read-only (GetMyeBaySelling, GetSellerTransactions, GetAccount, GetStore, GetItem, GetMyMessages, GetFeedback, GetBestOffers), native Mac run (`Valley Pawn OS/bin/ebay_channel_audit.py`). Nothing on eBay was changed. Listing-quality fields come from a GetItem sample (221 listings), not the bulk pull. Week-over-week base: 2026-11-16.

## Slack post (as sent)

```
eBay Channel Pulse — 2026-11-23 (weekly, trailing 90d, all 5 stores, read-only)

Headline: 375 active listings / $64,697 listed value · 521 sold units / $93,628 revenue (90d) · fees $14,725 (15.7% of revenue) · 197 listings aged >90d ($32,205) · 210 unread messages (13 return/refund)

Holding steady: no-returns 0% (GetItem-sample verified, 221 listings).

Still open (ops-policy calls, not automated): TRS Plus eligibility still 0% channel-wide (dispatch time + free returns). Promoted Listings ~$0 at 4 of 5 stores (Waynesboro, Harrisonburg, Lexington, Roanoke).

New this week:
• vs 2026-11-16: active +6, listed value +$1,020, 90d revenue -$1,250, fee % -0.1pt, aged >90d +2 / +$1,180, unread +0
• 93 listings sit at their 3rd markdown cut with no further scheduled action (Culpeper 72, Harrisonburg 5, Lexington 1, Roanoke 15).
• 3 video-game / console / game-accessory listings in the sample take offers (Culpeper 1, Waynesboro 1, Harrisonburg 1) — the standing rule is no offers on video games; store's call to switch off, not changed here.
• 5 unread case/dispute-subject messages.

Full writeup: Projects/eBay/audit_weekly/2026-11-23/summary.md
```

## Per-store table

| Store | Active | Listed value | Sold 90d (units/$) | Fees 90d | Fee % | Aged >90d ($) | Days-to-sell (median) |
|---|---:|---:|---:|---:|---:|---:|---:|
| Culpeper | 179 | $27,637 | 216 / $29,063 | $4,369 | 15.0% | $21,798 (135 listings) | 60.0 |
| Waynesboro | 64 | $12,335 | 48 / $24,179 | $3,213 | 13.3% | $3,415 (22 listings) | 5.0 |
| Harrisonburg | 23 | $8,095 | 31 / $8,678 | $1,869 | 21.5% | $3,101 (10 listings) | 6 |
| Lexington | 18 | $3,198 | 63 / $12,479 | $2,176 | 17.4% | $889 (7 listings) | 2 |
| Roanoke | 91 | $13,433 | 163 / $19,228 | $3,098 | 16.1% | $3,002 (23 listings) | 7 |
| **Channel** | **375** | **$64,697** | **521 / $93,628** | **$14,725** | **15.7%** | **$32,205 (197)** | — |

## Listing quality (GetItem sample)

| Store | Sample | Best Offer on | No-returns | TRS-eligible | Avg photos | Dispatch | Return shipping paid by |
|---|---:|---:|---:|---:|---:|---|---|
| Culpeper | 60 | 41.7% | 0.0% | 0.0% | 6.8 | {'2': 56, 'unknown': 3, '1': 1} | {'Buyer': 60} |
| Waynesboro | 60 | 46.7% | 0.0% | 0.0% | 4.8 | {'2': 60} | {'Buyer': 60} |
| Harrisonburg | 23 | 91.3% | 0.0% | 0.0% | 6.4 | {'2': 23} | {'Buyer': 23} |
| Lexington | 18 | 94.4% | 0.0% | 0.0% | 6.5 | {'2': 18} | {'Buyer': 18} |
| Roanoke | 60 | 76.7% | 0.0% | 0.0% | 4.5 | {'3': 59, 'unknown': 1} | {'Buyer': 60} |

## Reputation, offers, messages

- Culpeper: score 1393, positive 1/6/12 mo 95.6/98.5/98.5%, neg/neutral without a reply field 3, open Best Offers 0 (0 expiring 48 h), unread 60 (4 return/refund, 0 case)
- Waynesboro: score 658, positive 1/6/12 mo 100.0/100.0/99.5%, neg/neutral without a reply field 1, open Best Offers 0 (0 expiring 48 h), unread 46 (0 return/refund, 1 case)
- Harrisonburg: score 642, positive 1/6/12 mo 100.0/98.6/98.6%, neg/neutral without a reply field 2, open Best Offers 0 (0 expiring 48 h), unread 6 (0 return/refund, 0 case)
- Lexington: score 1329, positive 1/6/12 mo 100.0/100.0/99.0%, neg/neutral without a reply field 2, open Best Offers 0 (0 expiring 48 h), unread 17 (0 return/refund, 2 case)
- Roanoke: score 5820, positive 1/6/12 mo 100.0/99.5/99.5%, neg/neutral without a reply field 1, open Best Offers 0 (0 expiring 48 h), unread 81 (9 return/refund, 2 case)

## Fees by category (90d, channel)

```
{
 "insertion": 47.0,
 "final_value_fee": 14182.77,
 "promoted_listings": 398.37,
 "other": 83.25,
 "return_shipping": 13.81
}
```

## Method notes

- Feedback 'no seller response' is a known GetFeedback gap (replies sent via RespondToFeedback don't always show); the reliable record is ~/ebay_feedback_answered.json. Read the count as a ceiling, not a trend.
- Not measured (API scope gap): impressions, click-through, conversion, seller level / Top Rated (see the monthly ratings sweep).
- The claude.ai 'eBay Channel Pulse' artifact is NOT refreshed by this native run (a Mac script cannot publish it).
- Store errors: none
