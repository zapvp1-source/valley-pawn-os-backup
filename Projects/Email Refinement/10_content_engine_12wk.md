# Valley Pawn — 12-Week Email Engagement Engine

**Author note (CMO framing):** This is a list-warming program, not a list-trimming one. Valley Pawn went 10 years without emailing, started sending 2 months ago, and is doing 1–2% clicks on weekly sends — which is exactly what you'd expect for a re-awakened list. The job is to climb that out to 6–10% by Q4 with content people actually want to open. Once we're there, then and only then do we revisit list hygiene.

---

## Strategic frame

**Audience:** 11,159 subscribers. Mostly customers who bought / pawned / borrowed at some point over the last decade. They know the brand. They forgot they're on the list. We need to reintroduce ourselves through value, not asks.

**The single thing that matters:** every send delivers a concrete reason to either (a) drive to a store, (b) call/text a store, (c) click through to the website. Anything that doesn't ladder to one of those is decoration.

**Brand voice (locked in `valley-pawn-context`):** warm, approachable, family-owned, "What's Right Is Right." Never stuffy. Never aggressive. Never spammy. Mention the 30-day warranty on retail content. Never mention firearms (deliverability + Roanoke policy).

**The north-star metric:** Calls + Texts per 1,000 recipients (now measurable thanks to the redirect infrastructure shipped 2026-05-28). Secondary: primary CTA click rate, engaged-subscriber count over rolling 90d.

---

## The recurring drumbeat — Deal of the Week

This is the heartbeat of the program. **Every Thursday send leads with one specific item priced below retail, from one specific store, available right now.** Same slot in every email so it becomes a habit.

Why it works:
- **Specificity drives clicks.** "This $89 Stihl chainsaw at the Lexington store" beats "great deals this week" every time.
- **It builds an expectation.** Once subscribers know Thursday = the deal, they open.
- **It feeds Bravo POS attribution.** When someone walks in for "the email deal," the manager can tag it.
- **It spreads the manager workload** (each store contributes ~once every 5 weeks).
- **It's measurable** — clicks on the deal CTA tell us which items hit.

### The mechanic

1. **Monday 8am:** each store manager has until 12pm to submit one item to the existing `#deal-of-the-week` Slack channel — photo, description, price, your name on it.
2. **Monday afternoon:** I (the automation) pick the strongest submission (best photo, best price-to-perceived-value ratio, best story).
3. **Tuesday:** I draft the Thursday send featuring that item as the hero deal.
4. **Wednesday:** Joshua reviews in Slack approval queue.
5. **Thursday 10am ET:** send goes out.

This process becomes the **`weekly-valley-pawn-email-campaign` skill** running on schedule.

---

## The 12-week thematic calendar

Every week has the Deal of the Week as the hero. Then a secondary "theme of the week" gives content variety so the program doesn't feel formulaic. Each theme is designed to pull a different audience segment to action.

| Week | Send date (Thu 10am) | Theme | Why this week | Audience pull |
|---|---|---|---|---|
| 1 | **June 4, 2026** | **Kickoff — "Every Thursday, something worth your time"** | Set the new cadence expectation. Reintroduce the brand. | All — set the table |
| 2 | June 11 | **Gold & silver price pulse** | Spot is volatile; people forget what their jewelry is worth | Gold-curious, loan-needers |
| 3 | June 18 | **Store spotlight: Culpeper** | Wednesday-open quirk; biggest store; flagship | Culpeper locals |
| 4 | June 25 | **Summer project tools** | Father's Day past, summer projects ramping | Retail buyers, tool buyers |
| 5 | **July 2** | **Independence Day — locally owned, locally everything** | Patriotic angle without cheese; family-owned story | All — brand-building |
| 6 | July 9 | **Store spotlight: Waynesboro** | Suburban, family customer mix | Waynesboro locals |
| 7 | July 16 | **How a pawn loan actually works** | Education = trust. The loans-curious segment is huge but quiet. | Loans-curious |
| 8 | July 23 | **Store spotlight: Harrisonburg** | College town, mid-summer dorm move-ins start | Harrisonburg locals + retail |
| 9 | July 30 | **Back-to-school tools & electronics** | Tactical, timely, high-intent | Retail buyers, parents |
| 10 | Aug 6 | **Store spotlight: Lexington** | VMI / W&L surrounding; military / academic mix | Lexington locals |
| 11 | Aug 13 | **The 30-day warranty story** | Differentiator vs every other pawn shop in the valley | Trust-building, retail |
| 12 | Aug 20 | **Store spotlight: Roanoke** | Largest market, distinct customer profile | Roanoke locals (no firearms) |

After week 12, we measure: did click rate climb? Did per-store segments fill? Is the dormant pool shrinking organically? Decide week 13+ from data.

---

## Anatomy of every send (the locked structure)

Every send uses VP Master Template (Brevo ID 11) and follows this body shape:

1. **Hero band** — the theme of the week. One headline. One subline. No noise.
2. **Deal of the Week block** — featured item, hero photo, price, store, single CTA: "See it at [store]." This goes ABOVE the rest of the content so it's seen first.
3. **Theme block** — the week's editorial content. 80–150 words. Specific to the theme.
4. **5-store directory** (locked in master) — Maps / Call / Text for every store. This stays put.
5. **Footer** (locked) — Instagram, website, hours, legal, unsubscribe.

The point: there's one always-on conversion mechanic (the deal), one editorial moment (the theme), and five always-on contact mechanics (the stores). Every email is a multi-front lever.

---

## Subject-line strategy

**Rules:**
- Specificity wins. "$89 chainsaw, Lexington only" > "deals are in!"
- Numbers in subject lines lift opens 15–20%.
- One emoji max. Often zero is better.
- Avoid spam triggers: FREE!!!, ACT NOW, LIMITED TIME, all-caps phrases.
- Length: 35–55 characters (mobile-truncation aware).
- Localization where it makes sense: name the city.

**Examples per theme:**

| Theme | Subject candidates |
|---|---|
| Kickoff | "Something new from Valley Pawn" / "Every Thursday, worth your time" |
| Gold pulse | "Gold is at $X. Here's what your ring's worth." / "Your jewelry box is hiding money" |
| Store spotlight | "What's new at Valley Pawn Culpeper" / "Culpeper just got 23 new items in" |
| Tools | "Summer tool drop, $39 and up" / "Pre-owned tools that work as hard as you do" |
| 4th of July | "Family-owned since [year]. Five Virginia stores." / "What 'locally owned' actually means" |
| Loans 101 | "What a pawn loan actually looks like" / "No credit check, no problem — here's how" |
| Back to school | "Dorm essentials, half price" / "Heading back to school? Start here." |
| Warranty | "The 30-day promise no other pawn shop makes" / "Why we warranty everything" |

**A/B testing:** Brevo supports subject-line A/B on every send. Default: split 50/50 to a small slice, send the winner to the rest. Set this up as standard practice from week 2 onward.

---

## Segmentation tilt (Phase 2 lives here)

By week 8 the per-store click data will start populating the segment infrastructure I built. From that point forward:

- **Store-spotlight weeks** (3, 6, 8, 10, 12) send a special variant to subscribers who've shown affinity for THAT store — a "you've engaged with our [city] store before, here's what's new there" send 24 hours after the broader send.
- **Gold/silver weeks** can be expanded with a follow-up to the Gold/Silver Interested segment.
- **The weekly newsletter itself** targets the Engaged segment by week 10–12 (currently 95, growing as we build engagement).

This isn't urgent — week 1–6 we send everything to the full list because the click history is still warming. By weeks 7+ we can start being smart about it.

---

## What "automation" means here

I am proposing two levels of automation:

**Level 1 — Skill-driven weekly generation (the heartbeat):**
The `weekly-valley-pawn-email-campaign` skill gets updated to read this calendar, identify the current week's theme, pull the manager submission from `#deal-of-the-week`, generate the email, and stage it in Brevo as a draft on Monday. Joshua approves Wednesday. Send fires Thursday 10am via Brevo's scheduler. **No manual content building per week.** This is the automation Joshua said yes to.

**Level 2 — Pre-staged drafts (the safety net):**
Weeks 1–4 are pre-built as Brevo drafts NOW so the program launches even if any week's Monday automation hits a snag. Joshua opens Brevo, schedules week 1 for June 4 Thursday 10am, done. The skill takes over from week 5.

---

## KPIs that matter

Reviewed every Friday in `#email-campaigns` per the existing `email-analytics-weekly` task:

| Metric | Where we are | 4-week target | 12-week target | Why |
|---|---|---|---|---|
| Real click rate (excluding bot opens) | 1.5–3% | 4% | 6–8% | The honest engagement signal |
| Calls + Texts per 1,000 recipients | 0 (no data yet) | 5 | 10+ | North star |
| Primary-CTA click rate | unknown | 2% | 4% | Money-action intent |
| Engaged subscribers (90d rolling) | 95 | 500 | 1,500+ | The real list size |
| Unsubscribe rate per send | 0.18% | < 0.3% | < 0.3% | Health check |
| Complaint rate per send | 0.08% | < 0.05% | < 0.05% | Deliverability red line |

A drop in unsub rate is just as valuable as a click-rate rise — it means we're picking content people actually want.

---

## What I'm NOT doing

- **NOT sending reactivation/sunset emails** to the 9,600 dormant subscribers (the prior drafts stay archived as a future option, not the current play).
- **NOT changing send cadence** from weekly. One Thursday per week. Predictable rhythm beats clever timing.
- **NOT promoting firearms** in any send (deliverability + Roanoke policy).
- **NOT chasing open rate** as a KPI — MPP makes it noise. Clicks and call/text actions are the truth.
- **NOT discounting holiday sends** out of the rotation — we keep Memorial Day–style holiday templates as separate moments layered on top of the weekly calendar.

---

## Decision rights

Joshua approves:
- Each Monday's manager submission pick (5-second yes/no in Slack)
- Each Wednesday's drafted send (subject line + body, 2-min skim)

I handle:
- Calendar execution
- Theme research and copy
- Template marker fill
- Brevo draft creation
- Subject A/B setup
- Friday analytics post

Lainie sees the Friday analytics post and weighs in if anything looks off.

---

## Next moves in this session (in execution order)

1. Build the Deal of the Week mechanic (Slack workflow, photo handling, submission rules)
2. Draft weeks 1–4 as fully written Brevo campaigns ready to schedule
3. Update the `weekly-valley-pawn-email-campaign` skill to drive this calendar from week 5 onward
4. Hand it back: Joshua schedules week 1 for next Thursday, the program runs from there
