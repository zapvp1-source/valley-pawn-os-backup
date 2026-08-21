---
name: wednesday-facebook-posts
description: Wednesday at 12 PM — Create premium branded content for all 5 Valley Pawn Facebook pages, Instagram, TikTok, and Google Business Profiles. Content focus: Tips & Education. MIX OF SIMPLE + BOLD VISUAL POSTS. Posts summary to #social-media-posts channel.
---

> ⚠️ **FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE.** If this task fails, errors out, or cannot complete its intended work for any reason, DO NOT post anything to Slack — no error messages, no partial results, no "I couldn't finish" notices. Joshua reviews every run inside Claude to confirm success or failure, so a failed run must stay completely silent on Slack. Only post to Slack once the task has genuinely completed the work it was designed to do. Posting failure or error noise clutters Slack and reflects poorly on the team.

You are creating Wednesday social media content for Valley Pawn — a family-owned pawn shop with 5 locations across Virginia (Culpeper, Waynesboro, Harrisonburg/Dixie Pawn, Lexington, Roanoke). Wednesday's content focus is TIPS & EDUCATION.

IMPORTANT — READ THE valley-pawn-context SKILL FIRST for brand voice, colors, GBP rules, and social media guidelines.

## CONTENT VISUAL STRATEGY (CRITICAL — NEW DIRECTIVE FROM JOSHUA)

Joshua wants a MIX of content styles. Keep the clean, simple text-based posts that have been working, but NOW also sprinkle in more graphical, photo-heavy, and visually bold/"loud and weird" posts. The split should be roughly:

- **60% CLEAN & SIMPLE** — Your standard text-on-gradient graphics, clean category lists, informational posts with brand colors. These build trust and convert. Keep doing these.
- **40% BOLD & VISUAL** — These are the scroll-stoppers. Pick from these formats:

### Bold/Visual Post Types to Rotate Through:
1. **Product Photography Close-ups** — Use striking stock photos or Canva imagery of items (gold chains, watches, guitars, power tools). Make it look almost editorial. Minimal or no text overlay — let the image do the talking with a punchy caption.
2. **Infographic-Style Education Posts** — Bold icons, numbered steps, visual flow diagrams showing "How Pawn Loans Work" or "5 Things to Know Before Selling Gold." Make education visually interesting, not just text walls.
3. **Bold Typography + Texture Mashups** — Oversized blocky text on gritty/industrial textures, neon color pops against dark backgrounds, collage-style layouts that feel more street art than corporate. Think unexpected, eye-catching.
4. **Myth vs. Reality Split-Screen Posts** — Visually dramatic left/right comparisons busting pawn shop myths. Dark/moody on the myth side, bright/clean on the reality side.
5. **Meme-Adjacent Posts** — Trending visual formats adapted to the pawn/education world. "Things people don't know about pawn shops" in a shareable format.
6. **"Did You Know?" Posts with Dramatic Imagery** — Big bold stat or fact layered over a cinematic photo. Example: a macro shot of gold with "Gold is up 30% this year. Your jewelry box might be a goldmine."
7. **Retro/VHS/Vintage Aesthetic Posts** — Grainy textures, old-school fonts, nostalgic vibes. Weird and eye-catching. Makes educational content feel cool instead of boring.
8. **Team/Store Candid Shots with Heavy Graphic Treatment** — Take a conceptual "staff tip" post and layer bold colors, doodles, cutout effects, or comic-book styling over it.

### Design Execution in Canva:
When creating Canva designs, vary the visual approach:
- Use the Canva `generate-design` or `generate-design-structured` tools to create designs
- For CLEAN posts: Use the existing brand color palette (deep purple #2D1A5E, bright blue #0099DD, coral #F58C8A, white text on dark gradients)
- For BOLD posts: Push the visual boundaries — use high-contrast colors, large-scale photography, unexpected layouts, textured backgrounds, cutout effects, neon accents. Still incorporate brand colors but let the visual energy be the star.
- ALWAYS include "Valley Pawn" branding and location info
- ALWAYS include "What's Right Is Right" tagline OR "30-day warranty" in at least one post per batch

### What NOT to Do:
- Don't mention firearms/guns/weapons in ANY post (especially Roanoke — Google and Meta policy violations)
- Don't use hashtags in Google Business Profile posts
- Don't put phone numbers in GBP post body text
- Don't use ALL CAPS headers in GBP posts
- Keep GBP posts informational and community-oriented, not salesy
- Don't make every post bold — the simple ones are important for trust. The mix matters.

## POSTING WORKFLOW

1. Create Canva designs for the content (mix of simple and bold styles as described above). Export each design and upload it somewhere with a public URL (Canva's "Share > Public link" works; or upload to Google Drive with link-share enabled).
2. **Publish to all 5 Facebook pages via the `facebook-post` skill — DO NOT use browser automation.** The skill bundles a Python script that posts via the Meta Graph API directly. Read the skill's SKILL.md first if you haven't (look for `facebook-post` in the available skills). Then build a batch file with per-store captions and run:
   ```
   python3 <FACEBOOK_POST_SKILL_DIR>/scripts/post.py \
     --batch /tmp/wed-fb-batch.json \
     --image-url <public-image-url>
   ```
   Where the batch JSON has one entry per store: `{"Lexington": "...", "Waynesboro": "...", "Harrisonburg": "...", "Culpeper": "...", "Roanoke": "..."}`. The skill handles tokens, emoji, em-dashes, and error reporting. Verify each post returns a `post_id=...` line.
3. Post to Instagram @valley_pawn (still browser/Canva flow — separate from FB)
4. Create TikTok-ready content for @thevalleypawn
5. Post to Google Business Profiles for all 5 locations (follow GBP compliance rules strictly)
6. DM Preston and Joshua on Slack with a summary of what was posted, including Canva design links AND the Facebook post IDs returned by step 2

## WEDNESDAY-SPECIFIC CONTENT IDEAS (Tips & Education):
- "How Pawn Loans Work" explainers (no credit check, doesn't affect credit score)
- Gold/silver appraisal tips — what determines value, what to bring in
- "What We Accept" category spotlights with visuals
- Myth-busting posts about pawn shops (we're modern, tech-driven, fair)
- Seasonal tips (spring cleaning = bring in what you don't need, back-to-school savings, etc.)
- "Pro tips" for getting the most value from your items
- How the mobile app works — shop and pay your bill online
- Warranty education — what the 30-day warranty covers and why it matters