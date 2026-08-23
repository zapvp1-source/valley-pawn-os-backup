# Valley Pawn — Creative Drift Engine
**Built 2026-08-22.** The meta-layer that makes the content system evolve on its own — week to
week, season to season, year to year — without anyone curating it.

> Joshua, 2026-08-22: *"this also needs to shift and move with creative genius over time, season
> and year. We need a comprehensive plan here for a self-iterating, with new drift for content,
> all run by you."*

---

## The problem this solves

A content system left alone does one of two things, and both are failure:

**It freezes.** The 90-day audit found the same caption posted 21 times across 5 accounts, and
"A Martin D-28 doesn't just sit on a wall" run **four times on the same page**. 76% of captioned
posts were verbatim reuse. Nothing was choosing new material because nothing was responsible for
novelty.

**Or it converges on noise.** The existing Friday→Monday loop reads Publer engagement and nudges the
mix ±5%. Its 2026-08-21 output was: *"top content: warranty (36 reach), bottom: warranty (0 reach),
adjustment: +5% warranty."* Warranty was simultaneously the best and worst performer, at n=8, on
single-digit engagement. That loop is not learning — it is chasing static, and it will happily lock
the whole calendar onto a format that got lucky once.

Drift fixes both: a **forced novelty budget** stops the freeze, and a **statistical gate** stops the
convergence-on-noise.

---

## The four clocks

Content evolves on four different timescales, and the engine runs a separate mechanism for each.
Conflating them is why most "AI content calendars" go stale in six weeks.

| Clock | Period | Mechanism | What changes |
|---|---|---|---|
| **Weekly** | 7 days | Bandit selection + cooldowns | *Which* formats fill this week's slots |
| **Seasonal** | ~6–13 weeks | Season skin + local calendar | Palette, hooks, subject matter, which formats are even eligible |
| **Quarterly** | 13 weeks | Creative refresh | Formats are retired, and **new ones are invented** |
| **Annual** | 52 weeks | Anniversary re-skin | Last year's seasonal formats return *transformed*, never repeated |

---

## 1. WEEKLY — selection under a forced novelty budget

Every format lives in a registry (`creative_state.json`) as a record with a status:

```
candidate → active → resting → retired
```

Each week, Lane C/D/B slots are filled by scoring every eligible format:

```
score = performance_index × confidence  +  novelty_bonus  −  fatigue_penalty
```

- **performance_index** — rolling engagement per post for that format, normalized per account
  (Brand IG's median reach of 4 and a store FB's median reach of 23 are not comparable raw).
- **confidence** — 0 until the format has `MIN_POSTS_FOR_SIGNAL` posts behind it (default **30**).
  **Below that threshold a format's measured performance is ignored entirely.** This is the direct
  fix for the n=8 warranty problem. An unproven format is *unknown*, not *bad*.
- **novelty_bonus** — decays with each use. A format used once this quarter outranks one used ten
  times, all else equal.
- **fatigue_penalty** — see cooldowns below.

### The exploration budget (the anti-freeze mechanism)

**A fixed share of every week's slots is reserved for formats that have never run.** Not "if there's
room" — reserved, first, before performance is consulted at all.

| Condition | Exploration share |
|---|---|
| Cold start — under 200 measured posts | **40%** |
| Warming — 200–800 measured posts | **25%** |
| Warm — over 800 measured posts | **15%** |
| Floor, permanently | **never below 15%** |

Valley Pawn is at cold start today: 485 measured posts across 90 days, but a median engagement of
**0.0 on 8 of 9 accounts** means we have volume without signal. The engine treats near-zero-variance
history as *no information* and stays at 40% exploration until real differences appear.

The 15% permanent floor is the important number. A pure exploit loop eventually posts one thing
forever. Fifteen percent is the tax we pay to never go stale.

### Cooldowns (hard, non-negotiable)

Carried from `PILLAR_OVERLAY` and extended:

| Rule | Value |
|---|---|
| Same **hook/angle** on the same page | 45 days |
| Same **humor bit** anywhere | 60 days |
| Same **format** on the same page | 21 days |
| Byte-identical **caption** anywhere | **never** — hard block, not a cooldown |
| Same format across **all 5 stores in one week** | allowed only for Deal Reels and seasonal tentpoles |

Cooldowns override score. A format that is winning still rests. This is deliberate: the audit's
worst finding was not a bad post, it was the *same* post.

---

## 2. SEASONAL — the skin layer

A season does not change *what* the formats are; it changes what they are made of. Every active
format is rendered through the current season skin.

| Season | Window | Palette shift | Hook register | Subject drift |
|---|---|---|---|---|
| **Late summer** | Aug 22 – Sep 15 | Warm gold, high sun | Back-to-school, last-warm-evenings | Laptops, tablets, dorm, mowers |
| **Early fall** | Sep 15 – Oct 15 | Amber, oxblood accents | First cool morning, harvest | Tools, generators, hunting prep, layaway opens |
| **Peak fall** | Oct 15 – Nov 10 | Deep amber, navy | Foliage, Friday night lights | Storm prep, gold selling, Halloween |
| **Early winter** | Nov 10 – Dec 5 | Navy, gold, ivory | Gratitude, Veterans, gathering | Black Friday, layaway payoff |
| **Holiday** | Dec 5 – Dec 26 | Gold on navy, warm light | Gifts, tradition, "made it home" | Jewelry, watches, layaway pickup |
| **New year** | Dec 26 – Jan 31 | Cool navy, clean ivory | Reset, cash flow, fresh start | Gold buying, pawn loans — peak pawn season |

Seasonal rules the engine enforces:
- **Foliage timing differs per town and the copy must reflect it.** Harrisonburg's first frost is
  Oct 1–15; Roanoke's is ~Oct 22; the Piedmont (Culpeper) peaks *later* than the mountain towns.
  A single "fall is here" post fanned to all five is exactly the byte-identical failure we banned.
- **Local calendar beats generic season.** If `CITY_COMMUNITY_KB.md` has a `[C26]` dated event that
  week for that town, it takes the community slot. Generic seasonal content is the fallback, never
  the default.
- **Season transitions are staged over 7 days,** not flipped overnight — the palette and hook
  register cross-fade so the feed doesn't visibly lurch.

---

## 3. QUARTERLY — the creative refresh (where genuinely new ideas come from)

Every 13 weeks, `vp-creative-refresh` runs and does four things in order:

**(a) Retire.** Any format that is (i) past the signal threshold AND (ii) in the bottom quintile for
two consecutive quarters is retired. Retired formats are archived with their numbers, never deleted
— a retired idea that gets forgotten will be reinvented and re-fail.

**(b) Rest.** Any format above the signal threshold but showing a >40% decline from its own peak is
moved to `resting` for a quarter. Formats fatigue; that is not the same as being bad.

**(c) Invent.** The engine generates **8–12 new candidate formats** for the coming quarter, seeded by:
- what actually performed (top quintile, above threshold)
- the incoming season skin
- the next quarter's `[C26]` local events from `CITY_COMMUNITY_KB.md`
- real Bravo inventory categories moving that quarter
- what the brand has *never* tried — the engine keeps an explicit `untried_territory` list

**(d) Gate for novelty.** A candidate is rejected if it is too close to something already active.
Cheap, deterministic checks, run before anything reaches the queue:
- opening-5-words overlap with any active format
- structural template match (same slot pattern)
- same pillar + same subject + same hook verb

This step is what stops "invent new formats" from quietly regenerating the same five ideas each
quarter with different adjectives — the standard failure mode of a self-prompting loop.

**Seed territory for Q4 2026** (already on the untried list): behind-the-counter appraisal
explainers · "what walked in this week" round-ups · then-and-now local photos · employee picks with
the employee's actual reasoning · price-guess games · restoration before/afters · the story of one
object · storm-prep checklists · "who made this?" maker-mark close-ups · counter POV time-lapses.

---

## 4. ANNUAL — anniversary re-skin

At the one-year mark, the engine detects that a format ran at this point last year and **forces a
transformation rather than a repeat**. Same slot, same season, deliberately different execution:
new medium (static → Reel), new angle, new opening structure, new subject.

Also annual: a **year-in-review pass** that writes what the brand learned into
`CREATIVE_LEDGER.md` — which pillars grew, which towns responded to what, which humor registers
landed, what died. That ledger seeds the next year's exploration list, so year two starts smarter
than year one instead of starting over.

---

## The hard floors drift may never cross

Drift is bounded. These are not preferences and the engine treats a violation as a run failure:

1. **Authenticity** (`PILLAR_OVERLAY` §6) — real photos, real facts, real prices. No invented
   inventory, no invented events, no claim we can't source.
2. **No empty captions. Ever.** 45% of the audited 90 days shipped with no caption at all.
3. **No byte-identical text across platforms or pages.** Every account gets its own variant.
4. **Humor guardrails** — never mock a customer, never joke about needing money or hard times,
   never firearms, punch at objects not people.
5. **Community posts carry no CTA and no product.**
6. **Category-scale realism** (`PILLAR_OVERLAY` §9) — AI enhances a post, it never fabricates the
   product. The toy-riding-mower incident is the standing example.
7. **Local accuracy** — a `[PATTERN]` date is never published as a date.
8. **Brand palette and type are locked** (`vp-brand-studio`). Drift changes *ideas*, never identity.

---

## State and files

| File | Role |
|---|---|
| `creative_state.json` | The live registry: formats, status, performance, cooldowns, exploration counters |
| `creative_drift.py` | Selection, scoring, cooldown enforcement, exploration budget, novelty gate |
| `CREATIVE_LEDGER.md` | Append-only human-readable record of every promotion, retirement and invention |
| `CITY_COMMUNITY_KB.md` | Per-town local truth Lane C draws from |
| `weekly-adjustments.json` | Existing Friday loop output — **now consumed as one input to drift, no longer the sole authority** |

## Relationship to the existing Friday loop

`vp-publer-analytics-friday` is not replaced and not disabled. It keeps writing
`weekly-adjustments.json`. What changes is authority: drift reads that file as *evidence*, applies
the confidence gate to it, and decides. The Friday loop can no longer move the mix on its own — which
is what it was doing at n=8.

## How to extend
Add a format by appending a record to `creative_state.json` with `status: "candidate"`. The engine
picks it up on the next weekly selection through the exploration budget. Never hand-promote a format
straight to `active` — that bypasses the gate this whole file exists to enforce.
