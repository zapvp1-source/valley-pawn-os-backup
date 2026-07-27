---
name: daily-social-media-content
description: Create daily social media content for Valley Pawn with MIX of simple + bold visual posts (60/40 split) and publish to Facebook, Instagram, and YouTube via Canva
---

> ⚠️ **FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE.** If this task fails, errors out, or cannot complete its intended work for any reason, DO NOT post anything to Slack — no error messages, no partial results, no "I couldn't finish" notices. Joshua reviews every run inside Claude to confirm success or failure, so a failed run must stay completely silent on Slack. Only post to Slack once the task has genuinely completed the work it was designed to do. Posting failure or error noise clutters Slack and reflects poorly on the team.

You are creating daily social media content for Valley Pawn — a family-owned pawn shop with 5 locations across Virginia.

IMPORTANT — READ THE valley-pawn-context SKILL FIRST for brand voice, colors, GBP rules, and social media guidelines.

## CONTENT VISUAL STRATEGY (CRITICAL — DIRECTIVE FROM JOSHUA)

Create a MIX of content styles — keep clean simple posts but also create bold, graphical, photo-heavy, "loud and weird" posts. The split:

- **60% CLEAN & SIMPLE** — Text-on-gradient graphics, clean category lists, informational posts with brand colors (deep purple #2D1A5E, bright blue #0099DD, coral #F58C8A).
- **40% BOLD & VISUAL** — Scroll-stoppers. Rotate through these formats:
  1. Product Photography Close-ups — editorial-style item shots, minimal text
  2. Bold Typography + Texture Mashups — oversized text, gritty textures, neon pops, street art energy
  3. Photo Collage Grids — "What $50 Gets You" or "Today's Haul"
  4. Meme-Adjacent Posts — trending formats adapted to pawn/resale world
  5. Cinematic/Dramatic Product Shots — moody backgrounds, spotlight lighting
  6. Retro/VHS/Vintage Aesthetic — grainy textures, nostalgic and weird
  7. Team/Store Candids with Graphic Treatment — bold colors, doodles, cutout effects
  8. "Did You Know?" with Dramatic Imagery — bold fact over cinematic photo

### Rules:
- NEVER mention firearms/guns/weapons
- ALWAYS include Valley Pawn branding
- Don't make every post bold — the mix matters
- Use Canva generate-design tools

## WORKFLOW
1. Create Canva designs (mix of simple + bold). Export and upload to a public URL (Canva share link or Drive link-share).
2. **Publish to Facebook via the `facebook-post` skill — DO NOT use browser automation.** Read the skill's SKILL.md first if you haven't. Build a per-store batch file and run:
   ```
   python3 <FACEBOOK_POST_SKILL_DIR>/scripts/post.py \
     --batch /tmp/daily-fb-batch.json \
     --image-url <public-image-url>
   ```
   Stores: `Lexington`, `Waynesboro`, `Harrisonburg`, `Culpeper`, `Roanoke`. Verify each post returns a `post_id=...` line.
3. Publish to Instagram (browser/Canva flow) and YouTube as usual — separate from FB.
4. DM Joshua and Preston on Slack with a summary including Canva links AND Facebook post IDs from step 2.