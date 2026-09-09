# Phone Call Review → Training Program — the plan

**Owner:** Joshua · **Delivered by:** Preston + store managers · **Produced by:** automation
**Scope today:** Harrisonburg, Waynesboro, Lexington (the three stores on Zoom Phone). Culpeper
and Roanoke join when they're ported.

---

## The one-sentence version

Every week, the phones get read; the machine turns them into four things — **a coaching pack per
store, a teachable-call library, a policy queue, and an inventory want-list** — and people do the
part only people can do: play the calls, have the conversations, sign the policies, buy the stock.

---

## What we learned building the first week, and why the design looks like this

One week of calls, read properly, produced: three genuine compliance exposures, one open
legal/firearms matter, a ~$5,000 pricing error, a category of guns we're sold out of during deer
season, and ten calls good enough to train from. **None of that is visible in Bravo, in Slack, or
in any report we have.** The phone is the only place customers tell us what they wanted and
didn't get, and the only place we can hear how our people actually sound.

Three things drove the design:

1. **Reading beats counting.** The keyword classifier got the week wrong; reading the calls got it
   right. So the analysis layer is a reading layer, not a keyword layer. Keywords stay for cheap
   weekly counts only.
2. **Individual feedback and team feedback are different products.** Aggregate patterns go to
   everyone. Anything about a person goes only to that person and their manager. This is already a
   standing rule and it doesn't change.
3. **The good calls are worth more than the bad ones.** A team hears "don't do X" and shrugs. A
   team hears their own coworker close a crossbow loan in three minutes and copies it. The library
   is built around the exemplars.

---

## The weekly cycle

Every Monday, automatically, from the previous Monday–Sunday:

| Step | What happens | Output |
|---|---|---|
| **1. Ingest** | Pull recordings, transcribe locally (with the loop fix), classify employee vs customer | Transcripts on disk — already running |
| **2. Read** | Six parallel reading passes over the week, one shared rubric (below) | Structured findings, every one traced to a call ID |
| **3. Sort** | Findings split by audience and severity | Four packs |
| **4. Deliver** | Each pack goes where it belongs (below) | Monday morning, before the stores open |
| **5. Score** | Week-over-week metrics computed | The scoreboard |

### The reading rubric (every call, every week)

Each call gets tagged on:

- **Type** — loan inquiry · selling to us · buying from us · existing-loan admin · hours · spam · other
- **Outcome** — quoted · not quoted · appointment set · name captured · we had it · we didn't have it · turned away
- **Verification** — did we confirm identity before disclosing anything? (yes / no / n/a)
- **Conduct flag** — none · LOW · MEDIUM · HIGH, with the category
- **Exemplar flag** — none · STRONG · EXCEPTIONAL, with the skill it demonstrates
- **Want-list** — item asked for and not in stock
- **Policy gap** — a rule stated wrong, inconsistently, or invented

That's the whole schema. Everything downstream is a filter on it.

---

## The four packs

### Pack 1 — Store coaching pack (per store, per week) → **that store's manager, privately**

- The store's numbers vs. last week (quote rate, capture rate, verification rate)
- **Every MEDIUM/HIGH conduct item at that store**, with audio, verbatim quote, and the exact call to play — no interpretation, the manager hears it themselves
- The store's best call of the week, with what specifically made it good
- Two or three "do this instead" notes drawn from the store's own misses

The manager handles it in their huddle or one-on-one. Nothing in the pack reaches the team channel.

**HIGH conduct items also go to Preston the same morning**, and anything with legal/firearms/
compliance exposure goes to you directly. Those don't wait for a huddle.

### Pack 2 — The teachable-call library → **shared, growing every week**

A folder of audio clips, each named by the skill it teaches, with a one-paragraph "what to
listen for." Organized by skill, not by date, because that's how you'll use it:

| Skill | What the exemplar shows | First entries (already pulled) |
|---|---|---|
| **Quoting without seeing it** | Conditional range, comps out loud, close with a time | Crossbow (LEX), Xbox Series X (HAR, Logan) |
| **Needs-based discovery** | "What do you need?" before any number | Console + 70 games (HAR) |
| **The anxious past-due call** | Pull the account, count the days, "your stuff is safe" | HAR Sep 1 |
| **Collections without shame** | Exact numbers, split payments, offer the app | Lego + tools (LEX), Jeff's courtesy call |
| **Saving a redemption** | Turn "I can't afford to pick up" into a $12 extension | Stevens (HAR) |
| **Service recovery** | Let them vent, apologize, then protect them | Louis Armstrong award (WAY) |
| **Saying no well** | Real reason, real referral, door left open | Drumsticks (LEX), muzzleloader (HAR) |
| **Teaching the product** | Interest vs principal, grace vs expiration | Charizard (HAR), title-loan caller (LEX) |
| **Going out of your way** | Laptop on the counter, the stuffed elephant | LEX, WAY |
| **Owning a mistake** | "I was wrong, come in and we'll fix it" | Uriah's fee-waiver callback |

Each week the reading pass nominates candidates; you or Preston approve additions. The library
becomes the new-hire onboarding pack automatically — a new hire listens to ten calls before they
touch a phone.

**Recognition:** one "Call of the Week" goes to the team channel, by name, with the clip. Positive
only, ever. This is the one place individual performance is public, and only when it's good.

### Pack 3 — Policy queue → **you**

Every week the reading pass flags rules that were stated wrong, stated three ways, or invented.
They accumulate into a queue. You approve, edit, or kill each one; approved ones run through the
existing policy flow — drafted, published, e-signed in Gusto, added to the manual.

**Already in the queue from week one** (`POLICY_GAPS_top5.md`, updated for the complete data):

1. Verify before you disclose — name plus one non-public identifier, always
2. Never confirm a firearm is on the premises, to anyone, by phone
3. No precious-metal quote without the spot sheet open
4. Sell-side standard: a number, a time, or a name — every call
5. What staff may not say — no owner/GM/colleague names, no staffing, no cash position, no speculation about customers
6. *(added)* Stolen-property inquiries: take the report, refer to police, never search a named person for a caller
7. *(added)* One grace / late-fee / expiration script, identical at every store
8. *(added)* Delayed firearm transfers: the written procedure, not the employee's own habit

### Pack 4 — Inventory want-list → **Preston and the buyers**

Every "asked for, didn't have" gets logged with store, date, and item. Weekly rollup with counts.
Cross-referenced against Bravo so "we don't have it" gets checked against "we have it at another
store." From week one: straight-wall deer rifles (350/400 Legend, 450 Bushmaster), rifled-barrel
12ga, non-gaming laptops under $800, outdoor power equipment, PS3 controllers, keyboards.

Over time this is the cheapest demand signal in the business — the customer told us, we just
weren't writing it down.

---

## The scoreboard — how you'll know it's working

Five numbers, weekly, by store, trended. Aggregate only in any shared view.

| Metric | Week 1 baseline | Target |
|---|---|---|
| **Quote rate** — sell-side calls where a number or range was given | ~30% | 80% |
| **Capture rate** — unfilled requests where a name + number was taken | **0%** | 90% |
| **Verification rate** — account details disclosed only after ID check | low | 100% |
| **Conduct incidents** (MEDIUM+) | ~20 / week | trending to 0 |
| **Want-list fills** — items we stocked because the phone told us to | 0 | tracked |

Quote rate and capture rate are the money. Verification rate is the exposure. The first two will
move within a month if the packs are actually used in huddles.

---

## People — who does what

- **Automation** produces every pack, every Monday, and maintains the library and the scoreboard.
- **Store managers** run their coaching pack in the weekly huddle and one-on-ones. They play the
  calls. Fifteen minutes a week.
- **Preston** handles HIGH conduct items directly, approves library additions, owns the want-list.
- **You** approve policies and get the compliance/legal items same-day. Ten minutes a week unless
  something's on fire.
- **Nobody** ranks people or stores on these numbers, and nothing here touches bonus qualifiers.
  The moment a number affects pay, people optimize the number instead of the customer.

---

## Phasing

### This week — foundations (mostly done)
- ✅ Transcription pipeline with the loop fix, all 789 recordings on disk
- ✅ First week fully read, all four packs produced by hand
- ✅ Audio library started (22 clips pulled and labeled)
- ☐ Fix the store-label and call-direction bug in the metadata (per-store numbers are wrong until this is done)
- ☐ Written disposition on the Lexington firearm
- ☐ Register the Monday task so the cycle runs without anyone remembering to run it

### Weeks 2–4 — launch
- First automated Monday packs delivered to managers
- Top 5 policies drafted → your review → Gusto e-signature
- Teachable-call library folder shared with managers; first "Call of the Week"
- Scoreboard baseline established from weeks 1–4
- New-hire onboarding pack assembled from the library

### Month 2 — steady state
- Monthly training module: one skill, two good calls, one anonymized miss, a one-page script. Delivered in the monthly meeting, twelve a year, built from your own calls.
- Want-list reviewed at the monthly buy planning
- Add the Zoom call-log scope so hold time and abandons are measured, not inferred
- Culpeper and Roanoke onboarded as soon as they're on Zoom Phone — the whole program extends to five stores with no changes

### Ongoing
- The library grows every week. After six months it's the best sales training asset the company has, and it cost nothing but listening.

---

## What I'd build next, in order

1. **The Monday task** — one scheduled run that produces all four packs. The pieces exist; this wires them together and delivers them. Highest leverage, do first.
2. **The metadata fix** — store labels and direction. Blocks trustworthy per-store numbers.
3. **The library folder + index** — a shared location managers can open on a phone in a huddle.
4. **The policy drafts** — top 5 into real policy language for your sign-off.
5. **The scoreboard** — weekly numbers, trended, per store, in one place.

Say the word and I'll start on #1.
