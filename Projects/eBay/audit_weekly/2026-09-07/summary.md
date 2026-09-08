# eBay Channel Pulse — 2026-09-07

**Window:** trailing 90 days (2026-06-09 → 2026-09-07) · **Method:** live eBay Trading API, all 5 store
accounts, read-only (`GetMyeBaySelling`, `GetSellerTransactions`, `GetAccount`, `GetStore`, `GetItem`,
`GetMyMessages`, `GetFeedback`, `GetBestOffers`). Nothing on eBay was changed. Same known gap as
2026-08-31: `GetMyeBaySelling`'s bulk response returned every listing-quality field (photos, item
specifics, Best Offer, return policy, dispatch time) blank again this run — verified via a `GetItem`
sample (214 of 446 active listings — all stores ≤40 listings sampled at 100%, Culpeper and Roanoke
sampled 60 each). All quality-field figures below come from that sample, not the bulk pull.

## Headline

| Metric | This week | vs 2026-08-31 |
|---|---:|---:|
| Active listings | **446** | -22 (-4.7%) |
| Listed value | **$71,464** | -$6,510 |
| Sold, 90d | **572 units / $86,762** | +$409 revenue |
| Fees, 90d | **$14,485 (16.7% of revenue)** | +$179, fee % +0.1pt |
| Aged >90d | **199 listings / $20,146** | -4 listings / -$4,931 |

## What's still open (unchanged since 8/31, both remain Joshua's ops-policy calls)

- **Top Rated Plus eligibility is still 0% channel-wide.** Dispatch time is 2 days at Culpeper/
  Waynesboro/Harrisonburg/Lexington and 3 days at Roanoke (worst in channel, unchanged). Return
  shipping is still 100% buyer-pays at every store — free returns is the other TRS Plus
  requirement. Fee-discount opportunity unchanged from prior estimate.
- **Promoted Listings still effectively dark at 4 of 5 stores.** Channel Promoted spend this run
  reclassifies to **$446** (vs $401 last week reported under a broken "other" bucket — see Method
  notes) — almost entirely Culpeper; Waynesboro/Harrisonburg/Lexington/Roanoke remain near $0.

## Holding steady (good news, no regression)

- **Best Offer enabled: 100% of the sample, all 5 stores** — same as 8/31.
- **No-returns listings: 0% of the sample** — same as 8/31.
- Roanoke's 14-day-return straggler is down to **1 listing** in this sample (was 3 on 8/31) — the
  underlying template issue (flagged separately in the 9/6 eBay-engine review — Roanoke's Seller
  Hub default still creates 14-day returns on new listings) has not been fixed at the source, so
  new stragglers will keep appearing until that template default changes. Not this task's call to
  fix (read-only).

## New flags this run

- **4 open Best Offers, all 4 expiring today/tonight (2026-09-07 ET):** Roanoke has 3 (3:12 PM,
  6:19 PM, 9:03 PM ET) and Lexington has 1 (8:43 PM ET). None answered as of the pull. Needs a
  pricing call now — logged to the Open Items Register.
- **133 listings sit at their 3rd/final markdown cut (30% off) with no further scheduled action**
  as of this pull (Culpeper 101, Roanoke 18, Harrisonburg 8, Lexington 6, Waynesboro 0) — this
  reads as a spike but isn't one: the pull ran at 11:48 AM ET, and `ebay-markdown-terminal-weekly`
  (the task built 8/31 specifically to close this gap) fires today at 12:24 PM ET, 36 minutes
  later. This is a snapshot taken just before the weekly cleanup runs, not a new backlog. Worth a
  spot-check next run that the 12:24 PM pass actually cleared these.
- **Fee categorization was silently broken and is now fixed.** `GetAccount`'s
  `AccountDetailsEntryType` values shifted from the generic `CustomCode` string (which the 8/31
  script's keyword match mapped to Final Value Fee) to short codes — `FeeInsertion`, `FeeAd`,
  `FeeReturnShipping`, and `CustomCode` — that this run's original keyword match did NOT catch,
  which would have reported **98.6% of channel fees ($14,327) as unclassified "other."** Caught
  before publishing (Rule 18 — withhold, don't caveat) and re-mapped explicitly: Final Value Fee
  $13,797, Promoted Listings $446, Insertion $98, Return shipping $60, true Other $83. Flagging in
  case the fee-type string keeps drifting — this mapping is inference from the 8/31 method note,
  not a documented eBay field.
- **Negative/neutral feedback "no seller response" figures need a caveat, not a trend read.**
  This run's `GetFeedback` pull shows 10 negative/neutral comments channel-wide with no `Response`
  field set (Culpeper 2, Waynesboro 1, Harrisonburg 3, Lexington 3, Roanoke 1) — identical to
  8/31's count. But a separate 9/5 session (logged in the Open Items Register) already proved
  `GetFeedback`'s `Response` field does **not** reliably reflect replies sent via
  `RespondToFeedback` — 8 replies were posted 9/5 and would not show here. Do not read this figure
  as "8 replies posted, count unchanged, so the reply didn't take" — it's a known API gap, not a
  regression. The reliable record lives at `~/ebay_feedback_answered.json` (11 FeedbackIDs), which
  this pull doesn't capture (no FeedbackID field in this script). Worth adding to a future run.
- **Unread message backlog: 382 across the channel over 60 days** (down 5 from 387), including 27
  unread return/refund-subject messages and 1 unread case/dispute-subject message. Roanoke remains
  heaviest at 159 unread (was 157).
- **eBay Store subscription tier still not confirmed via `GetStore`** — same gap as 8/31, the
  `SubscriptionLevel` field is absent from the response for this account across all 5 stores.

## Per-store table

| Store | Active | Listed value | Sold 90d (units/$) | Fees 90d | Fee % | Aged >90d ($) | Days-to-sell (median) |
|---|---:|---:|---:|---:|---:|---:|---:|
| Culpeper | 258 | $36,859 | 243 / $29,495 | $4,851 | 16.4% | $14,562 (142 listings) | 26 |
| Waynesboro | 36 | $12,380 | 59 / $13,906 | $1,829 | 13.2% | $0 (0) | 4 |
| Harrisonburg | 32 | $6,818 | 51 / $10,474 | $1,841 | 17.6% | $729 (13) | 3 |
| Lexington | 26 | $5,298 | 61 / $12,795 | $2,715 | 21.2% | $1,219 (13) | 5 |
| Roanoke | 94 | $10,109 | 157 / $20,092 | $3,249 | 16.2% | $3,637 (31) | 8 |
| **Channel** | **446** | **$71,464** | **572 / $86,762** | **$14,485** | **16.7%** | **$20,146 (199)** | — |

Culpeper still carries 72% of channel aged->90d value — down from ~79% on 8/31 ($19,813 of $25,077).

## Method notes

- No API/pull errors on any of the 5 stores this run — all data below is complete for every store,
  per Rule 18.
- See "New flags" above for the fee-categorization bug caught and fixed before this file was
  written, and the feedback-response caveat.
- Not measured (API scope gap, same as prior runs): impressions, click-through, conversion, search
  placement.
- Raw data + full computed summary: `raw_pull.json`, `sample_results.json`, `summary.json` in this
  folder.
