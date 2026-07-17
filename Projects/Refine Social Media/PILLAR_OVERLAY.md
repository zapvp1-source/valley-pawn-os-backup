# Valley Pawn Pillar Overlay — Community + Humor + Adjust Loop (2026-07-06)

**Authoritative addendum to `vp-brand-studio` pillars and the `vp-content-batch` mix rules.**
The `vp-content-batch-weekly` runner reads this file at Step 1. If this file conflicts
with the skill cache, THIS FILE WINS (same precedence pattern as vp_fb_content_strategy.md).

Commissioned by Joshua 2026-07-06: "AI content is good but we need variety. Community
posts that engage people NOT about our business. Funny videos. And a measure/adjust/iterate loop."

---

## 1. Community pillar — promoted to first-class (15–20% of weekly mix)

The old ~15% "Community / Local" sub-pillar under Story is now its own pillar.

- **Quota:** 3–4 items of the 20-item weekly batch.
- **Content:** local landmarks, events, festivals, trails, parks, JMU/VMI/W&L, farmers
  markets, Shenandoah NP. NEVER competitors. NEVER a Valley Pawn CTA or product mention.
  Address footer at the very bottom is allowed; the content leads 100% with the community subject.
- **Source:** `hook-library/community.json` (this folder). Rotate regions; skip any hook
  used in the last 45 days (`last_used_at` — write it back when picked).
- **Routing:** region-specific hooks → that store's GBP + FB (store-local tier).
  Valley-wide hooks → Brand tier (1–2 per week max, counts toward the 3 Brand posts).
- **Style:** STYLE-B warmth for MJ scenes; real local photos preferred when available.
  MJ TEXT RULE applies as always.
- **Voice test:** if a stranger would read the post as "a local business that loves its
  town," it's right. If it reads as marketing, rewrite or kill.

## 2. Humor pillar — new, hard-capped (10% of mix, max 1/week)

- **Quota:** 1 item per week MAX. 10% of rolling 4-week mix hard cap. Humor doesn't
  scale — ration it.
- **Register:** dry Shenandoah humor. STYLE-D Polaroid Playful only.
- **Source:** `hook-library/humor.json` (this folder). 60-day reuse cooldown.
- **Boundaries (hard):** never mock identifiable customers; never joke about needing
  money or hard times; never firearms humor; punch at objects/situations, not people;
  no junk-shop tropes. Text on images goes through the compose_text_on_hero.py pass —
  never MJ-rendered.
- **Routing:** Brand tier by default (humor represents the whole brand). Skip GBP
  (GBP stays informational — Option A policy).

## 3. Revised default weekly footprint (still 20 items)

| Slot | Count | Notes |
|---|---|---|
| Brand posts | 3 | 1 may be Community (valley-wide) or Humor — not both in the same week's Brand set unless a floor forces it |
| Store-local statics | 8 (varies/store) | reduced from 10 — 2 static slots per week were converted to video per Section 8; 1 of each store's remaining statics may be a Community post for that region |
| Deals-of-the-Week | 5 | unchanged |
| Reels | 4 | **raised from 2 (2026-07-11) — see Section 8.** casual-video-inbox pipeline items are still ADDITIVE on top of this |
| **Community across all slots** | **3–4** | the 15–20% target |
| **Humor across all slots** | **≤1** | the 10% cap |

All other caps/floors from vp_fb_content_strategy.md still apply.

## 4. Measure → adjust → iterate loop

- Friday 4 PM: the `vp-publer-analytics-friday` task runs `publer_weekly_digest.py`
  (this folder) → Publer API post-level insights, last 7 days, all accounts.
- Output: `friday_digests/friday_digest_{date}.md` + one-line DM to Joshua +
  **`weekly-adjustments.json`** (this folder).
- Monday 2:02 AM: the batch runner READS `weekly-adjustments.json` before Step 2 and
  applies the suggested pillar nudge (±5% max per week, never violating caps/floors,
  never below the Community 15% floor or above the Humor 10% cap).
- `adjustments_log.jsonl` (this folder) accumulates one line per week so drift is auditable.

## 5. Casual-video pipeline (additive track)

- Inbox: `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn Studios/casual-video-inbox/`
- Joshua/Lainie/managers drop phone-shot 15–30s clips (mp4/mov). Optional sidecar
  `{samebasename}.txt`: line 1 = lower-third title, remaining lines = post caption.
- Daily 7 PM: `vp-casual-video-daily` task runs `casual_video_processor.py` →
  Whisper captions burned in (brand caption spec), lower-third, end-card, 9:16.
- **Auto-schedules** (Joshua's 2026-07-06 decision — no approval gate) to
  Brand FB + IG + TikTok + X via Publer at the next evening slot (5–8 PM ET).
  X gets a ≤270-char compressed caption (separate Publer job).
- Processed originals move to `casual-video-inbox/processed/`. Failures stay in place,
  logged to `casual-video-inbox/failed.log`, silent to Joshua (Claude self-heals).

## 6. Authenticity & Caption-Integrity Gate (added 2026-07-11 content review)

**Why this section exists:** Joshua flagged that AI content "does not have real
messaging, especially the brand pieces" and asked for a full review. A live pull
of Publer's own post history (not the manifest files — the actual published
record) found the real cause was worse than generic tone:

- **69% of every post ever published (55 of 80, back to 2026-05-26) had a
  completely EMPTY caption** — just an image, zero words. Store-local pages
  (Roanoke/Waynesboro/Culpeper) were hit worst at 90% blank. This is almost
  certainly what reads as "why are they posting this" — there's often nothing
  to read.
- The blank posts did NOT come from `vp_social_publisher.py` (it already
  refuses empty captions) — they were published through some other ad-hoc
  path that bypassed the one hardened script. **There is no single enforced
  publishing path today**, which is how this went undetected for 6+ weeks.
- The Friday measurement loop (`publer_weekly_digest.py` /
  `friday_close_engagement_publer.py`) has been silently broken since it was
  built — it called Publer's analytics endpoint with `since`/`until` params
  that Publer's API doesn't recognize (real params are `from`/`to`), so every
  single call 500'd and got swallowed as "no data." **Fixed 2026-07-11** in
  `publer_client.py`. This means the "measure → adjust → iterate" loop
  described in section 4 has never actually run on real signal until now.
- No Valley Pawn scheduled task for this pipeline (`vp-content-batch-weekly`,
  `vp-publer-analytics-friday`, `vp-casual-video-daily`, pre/post-flight, etc.)
  was ever actually registered as a live recurring task in this account's
  scheduler — confirmed by querying the live trigger list directly (0 of ~6
  documented tasks exist). Whatever posted, posted from manual/ad-hoc runs,
  not a running autonomous pipeline. **Two of these were rebuilt as real
  scheduled tasks on 2026-07-11** (weekly batch + Friday analytics); the rest
  are deferred until the core loop proves reliable for a few weeks.
- When captions DID exist, some contained fabricated claims not grounded in
  real store data — e.g. a live gold-buy post claimed stores are open "seven
  days a week," which is false for every location. And identical caption text
  (hashtags included) was copy-pasted across Facebook, Instagram, and Google
  Business Profile despite `vp-content-batch`'s own spec calling for
  platform-specific versions (FB/GBP should never carry hashtags).

**New hard rules, effective immediately, enforced in code in
`vp_social_publisher.py`'s `qa_check_caption()`:**

1. **No post may ship with an empty caption.** Ever. No exceptions, no
   "the image speaks for itself."
2. **All Valley Pawn social publishing goes through `vp_social_publisher.py`.**
   Never call `PublerClient.schedule_post()` directly from a one-off script,
   inline snippet, or interactive session. That bypass is exactly how the
   blank posts and the copy-pasted duplicate captions happened.
3. **Fact-check every caption against real store data before scheduling** —
   hours, addresses, and warranty terms must match `valley-pawn-context`
   exactly. `STORE_FACTS` in `vp_social_publisher.py` now hard-blocks known
   bad claims ("seven days a week," "closes at 5pm," "Dixie Pawn") and should
   grow every time a new fact-check miss is found.
4. **Every caption needs at least one concrete, specific, real detail** — an
   actual price + item description, a real employee name + tenure, a real
   local landmark name, or a dated fact. Adjective-only brand voice ("modern,
   trustworthy, family-owned") with no concrete anchor is the generic pattern
   Joshua is reacting to — kill it and rewrite with a specific.
5. **No verbatim copy-paste across platforms.** FB, IG, and GBP each get their
   own version per the existing `vp-content-batch` Step 6 spec (GBP: zero
   hashtags, zero phone numbers, zero ALL-CAPS; FB: no hashtags; IG: hashtags
   OK). Identical text reused across all three is the templated, corporate
   feel Joshua is calling out — GBP posts additionally get hard-blocked by
   `qa_check_caption()` if they contain a hashtag or phone number.
6. **Heritage/Community/brand-tier ("soft") posts get the same specificity bar
   as Value/Find posts.** These are the posts most likely to lean on generic
   template language ("Serving the valley since 2014") because there's no
   SKU/price to anchor them. Ground every Heritage post in one real, checkable
   detail: an actual employee's real tenure from the `valley-pawn-context`
   employee directory, a specific dated event, or a named real landmark —
   never a bare tagline restated with no supporting fact.

## 7. Imagery Authenticity Gate (added 2026-07-11 imagery audit)

**Why this section exists:** Joshua asked, on top of the caption review, to "make sure
the actual pictures relevant to our business" — not just captions. A visual review
of every actual image published through Publer (downloaded directly from Publer's
CDN, not from the manifest files) found:

- Item-specific photos — a real Taylor 710 guitar, a real VOX amp, each tied to a
  caption naming that exact item at that exact store — were genuinely relevant and
  well composed. **No problem there.**
- But several generic AI-rendered "mood" images (an antique desk with a compass and
  ledger, a Shenandoah Valley pasture-and-fence landscape, a pile of gold chains on
  a jeweler's scale) were reused, pixel-for-pixel identical, across DIFFERENT
  physical store locations and different days — e.g. the same valley-landscape
  render on Harrisonburg's GBP one day and Roanoke's GBP the next; the same
  antique-desk render on Waynesboro's GBP and two separate Brand FB/Twitter posts.
  Every one of these was also a blank-caption post, so there was nothing else
  tying the image to that specific store, town, or inventory. This is a second,
  independent authenticity problem from the caption issue: a customer scrolling
  past two different towns' Google Business Profiles would see the literal same
  stock photo both times.

**New hard rule, enforced in code:** `vp_social_publisher.py` now runs
`qa_check_image_diversity()` across the whole batch at publish time (in `main()`,
before any item is sent to Publer). Any `image_url` assigned to posts for two or
more different physical stores (Culpeper/Waynesboro/Harrisonburg/Lexington/Roanoke,
via either the FB Page or the matching `GBP_*` key) is blocked outright — the whole
group of conflicting items gets an `error` result instead of publishing. Reusing one
image across a single store's own FB/IG/GBP (same store, same item) is unaffected —
that's normal, expected cross-posting.

**Process rule for content generation (not just publishing):** every store-local and
GBP post needs imagery that is genuinely specific to that store — an actual item
currently in inventory (per Bravo data), an actual storefront/interior photo, or at
minimum an MJ render prompted with that store's real location details — never a
generic interchangeable "pawn shop mood" render pulled from a shared pool and
stamped onto whichever store's post needs an image that week. If Bravo has no fresh
item photo available for a store-local slot, prefer skipping that slot's image
specificity requirement by using a real storefront photo over a generic MJ render.

## 8. Video-first weighting (added 2026-07-11 — Joshua: "videos get more engagement")

Confirmed direction from Joshua: video content gets more engagement than static
images, and the content mix should reflect that going forward, not just as an
additive afterthought.

- **Weekly Reels quota raised from 2 → 4** (Section 3 table), pulled from what were
  2 store-local static slots. These 4 should rotate store coverage across the
  5-store roster week over week so no store goes more than ~2 weeks without a video.
- **`vp-casual-video-daily` re-enabled 2026-07-11**, but phased in at 3x/week
  (Mon/Wed/Fri, 7 PM ET) rather than full daily cadence, since this exact pipeline
  has zero verified live run history — it was documented as "shipped" in a prior
  session but was never actually a live scheduled task (see Section 6 and
  `vp-2026-07-11-content-review.md` in project memory). Same auto-schedule behavior
  as originally designed: Whisper captions, lower-third, end-card, 9:16, auto-posts
  to Brand FB/IG/TikTok/X with no approval gate. Review the first 2 weeks of Friday
  digests once the analytics loop has real signal (it was broken until today) before
  deciding whether to move to full daily.
- **When a content slot could reasonably be either a static image or a short video
  (e.g. a Deal-of-the-Week item with a real product in hand), default to video.**
  Only fall back to a static image when no video source exists and shooting one
  isn't practical (e.g. a GBP post that must go out same-day with only a catalog
  photo available).
- The Friday `publer_weekly_digest.py` report (now that its analytics call is fixed
  per Section 6) should break out video vs. static engagement explicitly so the
  Monday adjust loop can keep nudging the mix toward whichever actually performs —
  this is exactly the "measure → adjust → iterate" loop in Section 4, now with a
  video/static split as one of the things it measures.

## 9. Category-Scale Realism Gate (added 2026-07-13 — the toy riding-mower incident)

**Why this section exists:** Joshua flagged a live Waynesboro post — a Troy-Bilt Super
Bronco XP 50 riding lawn mower (a real ~5-6 foot outdoor vehicle) rendered as a toy-scale
model sitting on a leather desk next to a brass compass and an antique map. It looks like
a die-cast toy, not a real machine. His words: "this does not represent the product at
all, lends to us being inaccurate and not authentic. AI should be enhancing our posts not
making them look like AI."

**Root cause, confirmed by direct filesystem check:** `vp-brand-studio/SKILL.md`
repeatedly instructs `vp-hero-image` to read `vp-brand-studio/references/
prompt-templates.md` for per-category prompt guidance (the thing that's supposed to make
a watch shoot differently than a guitar than a riding mower). **That file does not
exist** — `vp-brand-studio`'s skill directory contains only `SKILL.md`, no `references/`
folder at all. Every hero-image generation has therefore been running with zero
category guidance and falling back to one generic small-object "collector's desk"
composition (leather desk, compass, antique map — the STYLE-B "Heritage Story" look)
regardless of what the actual item is or how big it is. This is a distinct problem from
Section 7's image-reuse gate — that one is about the same image reused across stores;
this one is about a render that never matched the item's real-world scale or setting in
the first place, even on first use.

**Fix:** a new file, `IMAGE_CATEGORY_TEMPLATES.md` (this folder), is now the authoritative
category-template substitute until `vp-brand-studio`'s real `references/
prompt-templates.md` is actually built. It defines four buckets — small valuables (desk/
tabletop staging is correct here), mid-size items (counter/showroom staging), large
equipment (riding mowers, generators, tillers, ATVs, appliances — must render at true
scale in a realistic setting, NEVER on a desk with tabletop props; prefer a real photo
over a scale-broken render), and firearms (existing never-render-for-social rule,
unchanged). **`vp-hero-image` and `vp-content-batch` must read `IMAGE_CATEGORY_TEMPLATES.md`
before generating any hero image, in addition to (not instead of) `vp-brand-studio`.**

**Pre-publish sanity check (add wherever hero images get reviewed before scheduling):**
ask "does this look like a photo/render of the real item at its real size, in a plausible
real setting?" If it reads as a toy, miniature, or diorama, it fails — regenerate in the
correct bucket's staging or use a real photo instead.

---
*Changelog: 2026-07-06 — created (Community + Humor pillars, adjust loop, casual video).*
*Changelog: 2026-07-11 — added Authenticity & Caption-Integrity Gate after full content/performance review found a 69% blank-caption rate, a broken analytics loop (wrong API params), zero real scheduled tasks, and a factual hours error live on Facebook.*
*Changelog: 2026-07-11 (same-day follow-up) — added Imagery Authenticity Gate (generic stock images reused pixel-identical across different store locations, now hard-blocked in code) and Video-First Weighting (Reels quota 2→4, `vp-casual-video-daily` re-enabled at 3x/week) per Joshua's follow-up instructions.*
*Changelog: 2026-07-13 — added Category-Scale Realism Gate after a toy-scale riding-mower render shipped live; root cause is a missing `vp-brand-studio/references/prompt-templates.md` file, worked around via new `IMAGE_CATEGORY_TEMPLATES.md`.*
