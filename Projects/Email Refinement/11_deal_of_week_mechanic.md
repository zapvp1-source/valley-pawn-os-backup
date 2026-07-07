# Deal of the Week — Operating Mechanic

This is the recurring beat that makes the 12-week engine work. Every Thursday's send leads with one specific item from one specific store, picked from manager submissions.

## The weekly rhythm

### Monday morning

**8:00 AM** — Automated Slack post lands in `#deal-of-the-week`:
> Good morning. Submit your Deal of the Week candidate by 12:00 PM today.
>
> Reply in this thread with:
> 1. Photo (clear, well-lit, white-ish background if possible)
> 2. Item name + brand
> 3. Your price (under retail — that's the whole point)
> 4. The store and your name
> 5. Why it's a good deal (one sentence)
>
> Best submission goes in Thursday's email to ~11,000 subscribers. Tag @Joshua if unclear.

**8:00 AM – 12:00 PM** — Managers submit. Each store gets to submit one. If a manager doesn't submit, that store sits this week out.

### Monday afternoon

**12:30 PM** — Automation picks the strongest submission based on:
- **Item visibility:** does the photo show the item clearly?
- **Price gap:** how far below new-retail / used-market is the asking price? Bigger gap wins.
- **Universality:** would a Roanoke subscriber be interested even though the item is in Lexington? (Higher = better.)
- **Story:** is there an angle ("guy who pawned this can't redeem, our loss is your win" / "this DeWalt cost $400 new, $169 here")?

**1:00 PM** — Automation posts the choice back to `#deal-of-the-week`:
> This week's pick: **[item] from [store]** — submitted by [manager]. Drafting the Thursday email now. Other submissions go in next week's rotation.

### Monday evening / Tuesday morning

The `weekly-valley-pawn-email-campaign` skill:
1. Pulls the submission photo from Slack
2. Uploads to Brevo's media library (or runs through the vp-hero-image skill if photo quality is too low — generates a cinematic-premium product render)
3. Builds the Deal block: hero image + price + store + "See it at [store]" CTA pointing at `https://thevalleypawn.com/locations#<store>` (or the store's map link with `utm_content=deal_of_week_<store>`)
4. Drops the block into the week's calendar-driven template (W1/W2/W3 etc. from the 12-week calendar)
5. Creates the Brevo draft

### Wednesday morning

**9:00 AM** — Slack DM to Joshua:
> Thursday's email is staged. Subject: "[subject]". Hero deal: [item, $price, store]. Body theme: [calendar theme this week]. Review and approve: [Brevo link] [preview link]

Joshua approves in Slack (one click) or replies with edits.

### Thursday

**10:00 AM ET** — Send fires from Brevo's scheduler.

## What "automation" does NOT do

- It does NOT pick deals without a manager submission. If a store doesn't submit, they're not in this week. No fake deals.
- It does NOT change the calendar theme. The 12-week calendar drives the editorial half of every send.
- It does NOT send without Joshua's Wednesday approval.

## Submission scoring (the picker logic)

Each submission gets scored 1–5 on four dimensions:

| Dimension | 1 | 5 |
|---|---|---|
| **Photo quality** | Phone snap, dim, cluttered background | Clean, well-lit, item is the focus |
| **Price gap vs retail/market** | Same or higher than market | At least 40% under |
| **Universal appeal** | Niche / one-off / story-only | Broad daily-use item |
| **Story / angle** | None | Concrete, specific, memorable |

Total /20. Highest score wins the week. Ties go to the store that hasn't been featured most recently.

If no submission scores above 12, the email still sends but leads with the editorial theme instead of a deal block. We never force a weak deal.

## Tracking conventions

The Deal of the Week CTA URL pattern:
```
https://thevalleypawn.com/locations?utm_source=brevo&utm_medium=email&utm_campaign=<week-slug>&utm_content=deal_of_week_<store>
```

This rolls up two ways in Brevo analytics:
- **Per-store performance:** which store's deals draw the most click-throughs (informs which managers' submissions to weight higher)
- **Per-week performance:** which weeks' deals over- or under-performed (informs the picker's scoring weights over time)

By week 8 we'll have enough data to know which kinds of items consistently win.

## In-store attribution

When a customer comes in for "the email deal," the manager:
1. Sells the item normally in Bravo POS
2. Adds a note on the sale: `EOTW <YYYY-MM-DD>` (Email of the Week + date)

This lets us tie sends to actual sales weekly. Even if only 1 in 20 deals gets the note added, we'll know the order of magnitude of in-store conversion.

## What the manager gets

Beyond their store getting featured to 11K subscribers (good for the store):
- Their name in the email (good for the manager)
- Bragging rights in `#deal-of-the-week`
- A "Manager Spotlight of the Quarter" — whichever manager's submissions drove the most measurable in-store traffic gets called out at the quarterly meeting

## Implementation status

**This document is the spec.** The Monday automation that posts the Slack prompt + the Tuesday draft-builder is a build that will live inside the updated `weekly-valley-pawn-email-campaign` skill. That's the next task.

**For weeks 1–4 (June 4 / 11 / 18 / 25):** Joshua will manage submissions manually in Slack while the automation gets built. The drafts already in Brevo (IDs 19/20/21/22) have a clearly-marked placeholder block where the deal will land each week — Joshua or I can replace the placeholder with the actual deal content the day before send.

**Week 5 onward:** the automation runs the whole Monday → Wednesday flow.
