# AI avatar test — Joshua's digital twin (4 weeks)

Decided 2026-10-31 by Joshua: "4-week test, your digital twin". Status: WAITING ON 3 HUMAN STEPS (HUMAN_QUEUE row 2026-10-31).

## What runs
- One 45–60 s talking-head video a week, hosted by an AI avatar of Joshua (owner), on the BRAND pages only:
  Brand FB, BrandIG, BrandTikTok. Store pages are untouched (their authentic local posts are the core plan).
- Script source = that week's five verified Deal-of-the-Week items (already fact-checked by the daily 7:38 task)
  + one store-hours/warranty line. Facts allowed: family-owned since 2014, five Virginia stores, 30-day warranty,
  items + prices exactly as submitted in #deal-of-the-week. Nothing else.
- Slot: Tuesday afternoon inside the 1–3 PM window, minute chosen collision-free at build time.

## Rules (non-negotiable)
- Disclosed every time: Meta "AI info" label ON (Meta requires it for photorealistic AI video) + first caption line
  "Made with AI — a digital version of owner Joshua Davis."
- Never a customer, testimonial, review, or "real person" claim (FTC 16 CFR 465 bans AI/fake testimonials).
- No firearms, no loan-rate or legal claims, no prices not in the week's intake.
- Same caption QA as every post (vp_social publish.py _FORBIDDEN list).

## Measurement + kill rule
- Control = the existing weekly Brand five-deal compilation video (same pages, same topic, no avatar).
- Social campaign scorecard (Mondays) adds an "avatar" row. After 4 videos: avatar median reach below the
  compilation's median → stop, cancel the subscription, note in CHANGELOG. Above → keep and decide on stores.

## Human steps
- DONE 2026-10-31: Creator plan (yearly), Digital Twin recorded (HeyGen setup 1/4).
- LEFT: add the HeyGen remote MCP connector in claude.ai (https://mcp.heygen.com/mcp/v1/, OAuth). Generation draws on the Creator plan's 600 credits/month; the HeyGen API (key + separate wallet) is NOT used, so no extra spend.
- Then Claude: list_avatar_looks → twin id; create_video (script) → get_video → download → Publer, AI label on; video 1 to Joshua for approval first.

## Avatar assets (2026-10-31)
- Approved-style look: "Professional in navy blazer" 9cac63cd9a7042538eb3679d506cb9bd (Modern Corporate pack). Other looks in the group: blue blazer eea8ff46…, boardroom grey c83dd359…, white shirt a83c2643…, grey suit 76af13e5….
- Render recipe: create_video_from_avatar, engine avatar_v with reference_look_id = twin 067b2be949c446ab9da508d4c6820c89, default (cloned) voice, 1080p, captions burned.
- Pronunciation: HeyGen brand glossary "Valley Pawn" 67fa05b68f384b189674b6386feefcbb (Joshua Davis → JOSH-oo-uh DAY-vis, Culpeper, Waynesboro, Harrisonburg). Pass brandGlossaryId on every render; voice speed 0.95.
- Polish pass (v2, 2026-10-31): MediaPipe FaceLandmarker per frame → teeth whiten (inner-lip mask, bright low-red pixels: L+22, yellow pulled 75% to neutral, strength 1.4) + skin redness cut (face oval, only LAB a* above 140, ×0.6), re-mux original audio, x264 crf 18. Rebuild this as a script in the weekly generator.
- Better source = better avatar: re-record the Digital Twin rested, soft even front light (window or ring light at eye level), no overhead-only light, plain wall, collared shirt.

- 2026-10-31: Joshua rejected v1/v2 ("terrible"); deleted both HeyGen videos, the 5 Modern Corporate looks, and the draft MP4s. Original twin 067b2be9… kept until Joshua re-records (HUMAN_QUEUE). Brand glossary kept. Next: new twin → re-apply Modern Corporate pack → re-render welcome.
