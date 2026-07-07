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
| Store-local statics | 10 (2/store) | 1 of each store's 2 may be a Community post for that region |
| Deals-of-the-Week | 5 | unchanged |
| Reels | 2 | unchanged; casual-video pipeline items are ADDITIVE, not counted here |
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

---
*Changelog: 2026-07-06 — created (Community + Humor pillars, adjust loop, casual video). *
