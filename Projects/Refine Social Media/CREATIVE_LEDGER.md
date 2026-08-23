# Valley Pawn — Creative Ledger

Append-only. One dated section per quarterly refresh. Records what was retired and **why**, what
was rested, every candidate invented **with its seed reasoning**, and what the quarter actually
taught. This file is the input to the next quarter's exploration list — it exists so year two
starts smarter than year one instead of starting over.

Written by `vp-creative-refresh-quarterly`. Never edit a past section; append a new one.

---

## 2026-08-22 — Q4 2026 refresh (first run)

**Incoming season:** late summer → early fall → peak fall → early winter (Aug 22 – Nov 21)
**Registry before:** 22 formats, all `candidate`, 1 measured post
**Registry after:** 35 formats, all `candidate`, every lane fills a 4-slot week in all four seasons
**Evidence base:** 554 published posts / 485 with insights, 2026-05-24 → 2026-08-22, live Publer
pull (`audit_2026-08-22/publer_90day_raw.json`, 100% insight completeness on all 9 measurable
accounts, zero API errors). Plus `weekly-adjustments.json`, `adjustments_log.jsonl`, `#social-media`,
and Bravo sold-detail across 37 store-days of August.

### Standing caveat on this first run

The drift registry was created **2026-08-22** — the day of this run. No format has a quarter of
history, let alone the two consecutive weak quarters retirement requires. **The engine therefore
retired nothing and rested nothing, and that is the correct result, not a failure.** What follows
under "Retired" is not a registry action; it is an honest reckoning with the *publishing behaviours*
the 90-day evidence measured, recorded here so they are not silently reinvented.

Likewise the **annual pass (Step 6) is N/A** — there is no same-season predecessor a year back.
First real annual transformation pass: **Q3 2027**.

---

### What the quarter actually taught

**1. The Friday loop has spent eight consecutive weeks optimising toward a category that does not
exist.** This is the single most important finding of the quarter and it corrects the standing
read of the adjust loop.

`publer_weekly_digest.py` line 47 classifies a post as `warranty` on the regex
`warranty|what'?s right is right`. **"What's Right Is Right" is the brand tagline** and it sits in
the footer of nearly every post we publish. Of the 98 posts the classifier called "warranty," only
**8 are actually about the warranty**; the other 90 are a blowout-sale post (21×), a June
birthstone post (15×), a Memorial Day cash-discount post (10×) and others that merely carry the
tagline.

So the eight `adjustments_log.jsonl` entries reading `+5% warranty next batch` (7/12, 7/27, 7/31,
8/7, 8/14, 8/21) were not a content decision. They were the loop discovering that most of our posts
contain our own slogan, and then asking for more posts containing our own slogan.

For completeness, the category is also flatly inert: 0.541 engagements per post against a
whole-quarter average of 0.513 across all 485 posts — a difference of four one-hundredths of an
interaction. Even taken at face value it is noise. **The drift engine's `MIN_POSTS_FOR_SIGNAL = 30`
gate would not have caught this**, because the fake category cleared 30 posts easily. The lesson is
that a confidence threshold protects against small samples but not against a mislabelled one, and
the quarterly run must therefore always check *what the classifier actually matched*, never just
its output.

**2. Reach in this market is bought with local news value, not with craft.** The only genuine reach
outliers in 90 days were the 2026-07-23 hiring posts: **942 (Lexington), 469 (Culpeper), 435
(Waynesboro), 295 (Brand), 162 (Harrisonburg)** against a whole-corpus median reach of **13**. A 30×
to 70× multiple, on the plainest copy we published all quarter. They won because a job opening is
something a person forwards to another person. Second-best was the $100 giveaway at 44 median reach
(3.4×). Nothing else cleared baseline. Roanoke is the exception that proves it — the same hiring
post drew **14** reach there, which is a page-distribution problem, not a content problem, and is
tracked separately.

**3. The brand has never once asked anybody anything, and it shows.** 485 measured posts produced
**18 comments** and **zero replies from us, ever**. Fifteen of those 18 comments are a single
comment apiece on consecutive empty-caption Waynesboro photos synced from Facebook between 5/24 and
7/04 — a per-post constant on one page, almost certainly one loyal commenter, and **not evidence
that any format works.** Read honestly, the true comment count attributable to content is **3**.

**4. Video is not the problem; the route to the page is.** Video was the worst-performing type in
the quarter — 47 posts, median reach 1.0, one total interaction. But **45 of those 47 were posted
by staff straight to Facebook** (`source: sync`) and drew 0 or 1 reach each. The **two** that went
out through Publer drew **29 and 136 reach and 194 of the quarter's 216 total video views.** Two
posts is not proof, but it is the only directional evidence we have and it points at distribution,
not at the medium. Video stays. It routes through Publer.

**5. Scarcity is outperforming volume, and we have been reading it backwards.** Harrisonburg
published **13 posts in 90 days — the fewest of any store — and has the highest median reach of any
store page at 46**, against Culpeper's 23 on 111 posts and Roanoke's 6 on 81. More posting is
currently correlated with *less* reach per post. This does not yet justify posting less; it does
justify never treating raw post count as the health metric again.

**6. Reach is converting to attention but not to audience.** Joshua, 2026-08-06: reach +937% (7K),
engagements +997% (658), 74 QR/giveaway link clicks — and **+6 net new followers in 28 days.**
Nothing in the old registry gave anyone a reason to be there *next* week. Two of this quarter's
candidates exist specifically to fix that.

**7. Which towns responded to what.** Too little signal for a real ranking, and it would be
dishonest to publish one. What can be said: the two best-performing non-hiring photos of the
quarter were both community, both product-free, and both *specific* — Walker Street before the
shops open with the VMI cadets out marching (Lexington, 448 reach) and Skyline Drive's 75 overlooks
(Brand, 101). Meanwhile the community *category* has a median reach of 1.0 across 29 posts, so a
handful of hits carried a mean of 39.4. **Community is not "the top performer" — specific,
verifiable, place-named community content is, and generic seasonal community content is dead
weight.** That distinction is now enforced by the season skin's per-town foliage rule.

---

### Retired — with numbers, and why

Not registry retirements (see caveat above). These are publishing behaviours this run is recording
as dead so they are not reinvented.

| Behaviour | The numbers | Why it died |
|---|---|---|
| **`warranty` as an adjust-loop category** | 98 posts matched, **8 genuine**; 0.541 eng/post vs 0.513 corpus | It was never a category. The regex matched the brand tagline. Eight weeks of `+5% warranty` were an artefact. |
| **Blog syndication as a social slot** (`BrandBlog`, article type) | **24 posts. Max reach 3. Total engagement 0.0. Every single post.** | Zero is not a small number here, it is every observation. The blog may have SEO value; it has no social value and should stop consuming a content slot. |
| **X/Twitter as an equal-weight destination** (`BrandTwitter`) | 25 posts, median reach **1.0**, max 10, total engagement 9, 0 comments | Not worth a byte-identical fan-out that also violates the cross-platform rule. Demote, don't delete. |
| **Staff-posted video straight to Facebook** | 45 posts, reach 0 or 1 on all 45, 22 total views | The medium is fine (see lesson 4). The route is not. |
| **Empty-caption photo posts** | **239 of 485 (49%)**, median reach 13 | Already banned by `PILLAR_OVERLAY` §6 rule 1 and the drift hard floors. Recorded here with its number so the ban stays justified. |

**Rested:** none. Nothing has a peak to have declined 40% from.

---

### Invented — 13 candidates, with seed reasoning

Twelve were the Step 4 slate; the thirteenth (`pro_longest_tag`) was added during Step 9
verification to close a lane gap — see "Lane repair" below. All 13 cleared both the base novelty
gate and the stricter v2 gate described further down. **Zero rejections at the base gate, which is
itself a finding** — see "Defect found and fixed."

**Product lane — built from zero.** The lane did not exist. Every product post was previously
generated inside `vp-content-batch-weekly`'s monolith, which is exactly why product content
survived and community/humor/video did not.

- **`pro_appraisal_explainer` — "How we actually priced this."** One real item, its real tag, and
  the three things that set the number: condition, real comps, and what a 30-day warranty costs us.
  Ends by asking what they'd have guessed.
  *Seed:* untried_territory #1. Also the only constructive answer to the two unanswered 1-star
  Culpeper reviews alleging gold lowballing — publish the arithmetic instead of arguing. Ends on a
  question because 485 posts produced 3 real comments.
- **`pro_retro_shelf` — "The retro shelf this week."** Recurring. Whatever console, cartridge,
  controller or handheld came in, at its real price, with one line on why it still gets picked up.
  *Seed:* Bravo moved ~49 console/game items in three August weeks (Switch 12, NES 9, PS4 games 8,
  PSP 8, PS3 6, controllers 6) and retro gaming has **never been content once.** Recurring by
  design, against lesson 6.
- **`pro_storm_kit` — "What's actually in a storm kit."** Generator, chainsaw, work light,
  batteries, fuel cans — what we have, what it costs, and honestly what you don't need.
  *Seed:* untried_territory #5. Chainsaws sold 5 units / $1,290 and batteries are the #8 category by
  unit in August. Utility content is what gets forwarded, and forwarding is what produced every
  reach outlier this quarter (lesson 2). Season-gated to early fall onward.
- **`pro_price_ladder` — "Three of the same thing, three prices."** Good/better/best in one
  category, real tags, what the extra money buys and where it stops being worth it.
  *Seed:* distinct from `eng_this_or_that`, which is pure preference between two items; this one
  teaches a decision. Impact drivers, drills and laptops each show 3+ simultaneous units in the
  live pricing queue, so the ladder is real stock.
- **`pro_longest_tag` — "The tag that has been here longest."** *(Step 9 lane repair.)* The oldest
  price tag on the floor, how long it's sat, an honest guess at why, a real reduction applied on the
  spot, and a question to the room.
  *Seed:* aged inventory is already extracted from Bravo weekly and the items-to-price queue
  regenerates daily at all five stores — zero new work for the stores. Self-deprecating rather than
  promotional, which is precisely why it invites a reply. Punches at the object's stubbornness,
  never at a person.

**Video lane — 3 → 6, and no longer dependent on a human remembering.**

- **`vid_sixty_second_repair` — "Sixty seconds of cleaning it up."** Silent before/after time-lapse.
  Photo pair plus ffmpeg.
  *Seed:* untried_territory #2 and #3 at once. Requires no filming.
- **`vid_case_walk` — "Walk the case."** One slow phone pan down a single case, prices legible, no
  voiceover, one store per post.
  *Seed:* **the case photos already exist** — jewelry case counts are captured at all five stores
  every week for compliance (2026-08-21 files present for CUL/HAR/LEX/ROA/WAY). This converts a
  compliance artefact into publishable video, which is the only way a video lane survives an empty
  casual-video-inbox. That inbox has been empty **47 days**.
- **`vid_closing_time` — "Closing time."** Fixed camera, last ten minutes of a Saturday, twenty
  seconds, no product, no CTA.
  *Seed:* untried_territory #3. The quarter's best store photo was Walker Street before the shops
  open — quiet, human, product-free. This is that, in motion, and requires nobody to have an idea.

**Humor lane — 2 → 4, because 2 could not survive its own cooldown.**
With a 1-per-week quota and a 60-day same-bit cooldown, two formats mathematically run dry by week
nine. This was a structural certainty, not a creative shortfall.

- **`hum_wrong_guess` — "What people are sure this is worth."** The gap between an object's
  reputation and its actual market — always followed by the one time the myth was true.
  *Seed:* pairs with `pro_retro_shelf`; the console-worth-a-fortune belief is the most common
  counter conversation there is. It is a joke about a *market*, which keeps it inside the
  `PILLAR_OVERLAY` §2 boundary against joking at a customer's expense.
- **`hum_seasonal_arrival` — "It is that season again."** Mowers in September, generators the
  morning after a storm warning, treadmills the first week of January.
  *Seed:* seasonal by construction, and structurally incapable of drifting into joking about hard
  times because the subject is the calendar.

**Engagement lane — 7 → 9, targeting the follow gap specifically.**

- **`eng_two_week_answer` — "We asked, and here is what we did."** Week one asks a question we
  intend to act on. Week two publishes what we actually changed, naming the change — and ships even
  when the answer was inconvenient.
  *Seed:* lesson 6, directly. This is the only format in the registry that creates a reason to come
  back. Distinct from `eng_stock_poll`, where follow-up is an afterthought; here the follow-up *is*
  the format.
- **`eng_hometown_bracket` — "Town versus town."** A running bracket on something harmless and
  local — best fall drive, best breakfast, best field to watch a game from. One round a week.
  *Seed:* civic rivalry is the most reliable comment engine in small-market local Facebook. It is
  also the one legitimate five-store same-week fan-out the drift rules permit (seasonal tentpole),
  because each town carries different entrants and therefore different text — it fans out *without*
  the byte-identical repetition that produced 229 verbatim reposts last quarter.

**Community lane — 10 → 11, adding the one thing that actually travels.**

- **`com_local_news_desk` — "Something that happened here this week."** One verifiable local thing
  that is not about us: a road reopening, a new business on the block, a school record, the Parkway
  closing for the season. Sourced, dated, no CTA, no product.
  *Seed:* lesson 2. The hiring posts did not win on craft, they won because they were local news
  people forwarded. Nothing in the registry was built to be forwarded. This is.

**Q4 local calendar these draw against** (all `[C26]`, from `CITY_COMMUNITY_KB.md`): JMU classes
Aug 26 · Block Party in the Burg Aug 29 · Rockbridge Fair Sept 10–13 · Boro Fiddlen' Folk Fest
Sept 12 · Culpeper Fall Restaurant Week Sept 29–Oct 5 · Culpeper Air Fest Oct 10 · Virginia Fall
Foliage Art Show Oct 10–11 · Vinton Fall Festival Oct 10 · GO Fest Oct 16–18 · Hop N Hog Oct 17 ·
JMU Homecoming Oct 16–18 · VMI Family Weekend Oct 23–25 · Skeleton Festival Oct 24 · farmers-market
final days Oct 31 · JMU Veterans Celebration parade Nov 8 · VMI vs The Citadel Nov 14 · AQHA
Virginia Harvest Festival Nov 20–22.

---

### Lane repair (Step 9)

Verification caught the product lane holding only **3** late-summer-eligible formats against a
4-slot weekly ask — it would have under-filled every week from Aug 22 to Sep 15.
`pro_longest_tag` was invented and added in-run rather than deferred. Post-repair depth, every lane
against a 4-slot week:

| Season | community | engagement | humor | product | video | total |
|---|---|---|---|---|---|---|
| late summer | 8 | 9 | 4 | 4 | 6 | 31 |
| early fall | 10 | 9 | 4 | 5 | 6 | 34 |
| peak fall | 11 | 9 | 4 | 5 | 6 | 35 |
| early winter | 8 | 9 | 4 | 5 | 6 | 32 |

35 active-or-candidate formats against a floor of 20. No lane under-fills in any season of the
quarter. Live `select` smoke-tested on all five lanes — no warnings.

---

### Defect found and fixed — the novelty gate had a hole

**All 12 Step 4 candidates passed the base gate on the first attempt. That is a suspicious result,
not a good one**, so the gate was stress-tested rather than trusted.

`DriftEngine.is_novel()` compares the **first five words** of two titles and rejects at an overlap
of ≥3. Formats with **short titles can therefore never be matched.** Confirmed live: the title
*"Caption this photo please"* scores an overlap of 2 against the active format *"Caption this"* and
**passes cleanly.** So do *"Who made this thing"* against *"Who made this?"* and *"Guess the price
of this"* against *"Guess the price."* Roughly a third of the seed registry has titles under four
words, so a third of the registry was unprotected against exactly the re-skinning this gate exists
to stop.

Fixed **additively** per Rule #4 — `creative_drift.py` was not touched. New module
`novelty_gate_v2.py` is a strictly-tightening supplementary check (word-subset, 55% Jaccard on
content words, and same-pillar-same-opening-verb). It can only ever reject *more* than the base
gate, never less. All three example holes above are now blocked; **all 13 Q4 candidates clear the
stricter bar**, which is the reassurance that the slate is genuinely novel and not merely
un-caught.

Recommendation for the expert review board, logged in `OPEN_ITEMS_REGISTER.md`: fold v2 into the
base gate at the next hardening pass so future quarters get it automatically.

---

### Race condition caught during verification

While verifying the registry after the invention step, a **concurrent community-lane task wrote 21
post-records at 16:13, two minutes after this run saved 13 new candidates at ~16:11.** All 13
survived and the history entry is intact — but only because the lane task happened to load state
*after* this run saved. `DriftEngine.save()` is atomic per write (tmp + `replace`, so a killed run
never truncates), **but nothing locks across the read-modify-write**. A lane task that loads before
the quarterly run saves would silently erase an entire quarter of invented formats, with no error
and no way to notice except by counting.

Also observed in the same write: the community lane fanned `com_landmark_morning`,
`com_local_calendar` and `com_local_word` to **all five stores on the same day**, which
`CREATIVE_DRIFT.md` §1 permits only for Deal Reels and seasonal tentpoles. `select()` enforces
per-account cooldown but appears not to enforce the cross-store rule.

Both logged in `OPEN_ITEMS_REGISTER.md`. Neither was fixed in this run — a lock belongs in the same
hardening pass as the `novelty_gate_v2` fold-in, so `creative_drift.py` is opened once rather than
twice, and the fan-out rule is a live-behaviour question for the expert review board rather than a
quarterly-refresh change.

---

### Seed territory carried into Q1 2027

Q4's `untried_territory` list was consumed by this run (appraisal explainers, restoration
before/afters, counter POV time-lapses, storm-prep checklists, maker-mark close-ups, then-and-now,
one-object stories, employee picks). Replaced with territory the brand still has not been anywhere
near:

- customer-submitted "what is this" photos
- a standing Saturday live Q&A at one store
- long-form single-item write-ups with real provenance research
- audio only — a 60-second counter story with no video
- a printed zine/handout that gets photographed for social
- collaboration posts with a non-competing local business
- seasonal town-bracket results as a recurring civic institution
- "we were wrong about this item" — public correction as content

### What the next run must check first

1. **Re-read `publer_weekly_digest.py`'s classifier regexes before trusting any category.** Lesson
   1 will otherwise happen again in a different category. `heritage`, `team` and `how-it-works` have
   not been audited for the same tagline-collision failure.
2. **Has anything cleared 30 posts honestly?** If yes, the first real retirement quintile becomes
   available in Q1 2027 — but only the second consecutive weak quarter retires, so the earliest
   genuine retirement is **Q2 2027**.
3. **Did we ever actually reply to a comment?** The number to beat is zero.
4. **Did `pro_retro_shelf` and `eng_two_week_answer` move followers?** They are the two bets
   against lesson 6 and the follower number is the cleanest scoreboard we have.
