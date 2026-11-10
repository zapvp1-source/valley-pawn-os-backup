# eBay Channel Pulse — 2026-11-09

**Window:** trailing 90 days · **Method:** live eBay Trading API, all 5 store accounts, read-only (GetMyeBaySelling, GetSellerTransactions, GetAccount, GetStore, GetItem, GetMyMessages, GetFeedback, GetBestOffers), native Mac run (`Valley Pawn OS/bin/ebay_channel_audit.py`). Nothing on eBay was changed. Listing-quality fields come from a GetItem sample (225 listings), not the bulk pull. Week-over-week base: 2026-11-02.

## Slack post (as sent)

```
eBay Channel Pulse — 2026-11-09 (weekly, trailing 90d, all 5 stores, read-only)

Headline: 392 active listings / $65,847 listed value · 556 sold units / $98,630 revenue (90d) · fees $15,859 (16.1% of revenue) · 185 listings aged >90d ($23,565) · 201 unread messages (12 return/refund)

Holding steady: no-returns 0% (GetItem-sample verified, 225 listings).

Still open (ops-policy calls, not automated): TRS Plus eligibility still 0% channel-wide (dispatch time + free returns). Promoted Listings ~$0 at 4 of 5 stores (Waynesboro, Harrisonburg, Lexington, Roanoke).

New this week:
• vs 2026-11-02: active -15, listed value -$1,189, 90d revenue -$1,841, fee % -0.2pt, aged >90d +2 / +$1,272, unread +19
• 97 listings sit at their 3rd markdown cut with no further scheduled action (Culpeper 75, Harrisonburg 5, Lexington 1, Roanoke 16).
• 6 video-game / console / game-accessory listings in the sample take offers (Waynesboro 2, Harrisonburg 3, Roanoke 1) — the standing rule is no offers on video games; store's call to switch off, not changed here.
• 14-day-return listings in the sample: Roanoke 1 (template default, not fixed at the source).
• 1 new negative/neutral feedback since 2026-11-02 (Culpeper).
• 3 unread case/dispute-subject messages.

Full writeup: Projects/eBay/audit_weekly/2026-11-09/summary.md
```

## Per-store table

| Store | Active | Listed value | Sold 90d (units/$) | Fees 90d | Fee % | Aged >90d ($) | Days-to-sell (median) |
|---|---:|---:|---:|---:|---:|---:|---:|
| Culpeper | 181 | $24,233 | 242 / $31,539 | $4,809 | 15.2% | $17,809 (133 listings) | 58.0 |
| Waynesboro | 66 | $16,457 | 49 / $22,311 | $3,047 | 13.7% | $1,103 (6 listings) | 4 |
| Harrisonburg | 27 | $8,092 | 29 / $9,380 | $2,037 | 21.7% | $823 (13 listings) | 2 |
| Lexington | 18 | $3,107 | 65 / $14,208 | $2,556 | 18.0% | $847 (8 listings) | 2 |
| Roanoke | 100 | $13,957 | 171 / $21,192 | $3,410 | 16.1% | $2,982 (25 listings) | 7 |
| **Channel** | **392** | **$65,847** | **556 / $98,630** | **$15,859** | **16.1%** | **$23,565 (185)** | — |

## Listing quality (GetItem sample)

| Store | Sample | Best Offer on | No-returns | TRS-eligible | Avg photos | Dispatch | Return shipping paid by |
|---|---:|---:|---:|---:|---:|---|---|
| Culpeper | 60 | 45.0% | 0.0% | 0.0% | 6.8 | {'2': 59, 'unknown': 1} | {'Buyer': 60} |
| Waynesboro | 60 | 50.0% | 0.0% | 0.0% | 5.0 | {'2': 60} | {'Buyer': 60} |
| Harrisonburg | 27 | 88.9% | 0.0% | 0.0% | 6.3 | {'2': 27} | {'Buyer': 27} |
| Lexington | 18 | 94.4% | 0.0% | 0.0% | 6.2 | {'2': 18} | {'Buyer': 18} |
| Roanoke | 60 | 90.0% | 0.0% | 0.0% | 4.4 | {'3': 59, 'unknown': 1} | {'Buyer': 60} |

## Reputation, offers, messages

- Culpeper: score 1377, positive 1/6/12 mo 98.5/98.5/98.5%, neg/neutral without a reply field 3, open Best Offers 0 (0 expiring 48 h), unread 54 (4 return/refund, 0 case)
- Waynesboro: score 646, positive 1/6/12 mo 100.0/100.0/99.5%, neg/neutral without a reply field 1, open Best Offers 0 (0 expiring 48 h), unread 39 (0 return/refund, 1 case)
- Harrisonburg: score 637, positive 1/6/12 mo 100.0/98.5/98.6%, neg/neutral without a reply field 2, open Best Offers 0 (0 expiring 48 h), unread 10 (0 return/refund, 0 case)
- Lexington: score 1323, positive 1/6/12 mo 100.0/100.0/99.0%, neg/neutral without a reply field 2, open Best Offers 0 (0 expiring 48 h), unread 15 (0 return/refund, 0 case)
- Roanoke: score 5806, positive 1/6/12 mo 100.0/99.5/99.5%, neg/neutral without a reply field 1, open Best Offers 0 (0 expiring 48 h), unread 83 (8 return/refund, 2 case)

## Fees by category (90d, channel)

```
{
 "insertion": 65.6,
 "final_value_fee": 15268.57,
 "promoted_listings": 427.62,
 "other": 83.25,
 "return_shipping": 13.81
}
```

## Method notes

- Feedback 'no seller response' is a known GetFeedback gap (replies sent via RespondToFeedback don't always show); the reliable record is ~/ebay_feedback_answered.json. Read the count as a ceiling, not a trend.
- Not measured (API scope gap): impressions, click-through, conversion, seller level / Top Rated (see the monthly ratings sweep).
- The claude.ai 'eBay Channel Pulse' artifact is NOT refreshed by this native run (a Mac script cannot publish it).
- Store errors: none
