---
name: saturday-facebook-posts
description: Saturday at 9 AM — Create premium branded content for all 5 Valley Pawn Facebook pages, Instagram, TikTok, and Google Business Profiles. Content focus: Community & Local Events. MIX OF SIMPLE + BOLD VISUAL POSTS. Posts summary to #social-media-posts channel.
---

> ⚠️ **FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE.** If this task fails, errors out, or cannot complete its intended work for any reason, DO NOT post anything to Slack — no error messages, no partial results, no "I couldn't finish" notices. Joshua reviews every run inside Claude to confirm success or failure, so a failed run must stay completely silent on Slack. Only post to Slack once the task has genuinely completed the work it was designed to do. Posting failure or error noise clutters Slack and reflects poorly on the team.

You are creating Saturday social media content for Valley Pawn — a family-owned pawn shop with 5 locations across Virginia (Culpeper, Waynesboro, Harrisonburg/Dixie Pawn, Lexington, Roanoke). Saturday's content focus is COMMUNITY & LOCAL EVENTS.

IMPORTANT — READ THE valley-pawn-context SKILL FIRST for brand voice, colors, GBP rules, and social media guidelines.

## CONTENT VISUAL STRATEGY (CRITICAL — NEW DIRECTIVE FROM JOSHUA)

Joshua wants a MIX of content styles. Keep the clean, simple text-based posts that have been working, but NOW also sprinkle in more graphical, photo-heavy, and visually bold/"loud and weird" posts. The split should be roughly:

- **60% CLEAN & SIMPLE** — Your standard text-on-gradient graphics, clean category lists, informational posts with brand colors. These build trust and convert. Keep doing these.
- **40% BOLD & VISUAL** — These are the scroll-stoppers. Pick from these formats:

### Bold/Visual Post Types to Rotate Through:
1. **Cinematic Store/Location Shots** — Dramatic, moody or warm photography of storefronts, local streets, Shenandoah Valley landscapes. Makes the community connection feel epic, not generic.
2. **Team Spotlight Posts with Heavy Graphic Treatment** — Feature a team member with bold colors, doodles, cutout effects, comic-book styling, or retro frames. Make the staff look like local heroes.
3. **Bold Typography + Texture Mashups** — Oversized blocky text on gritty/industrial textures, neon color pops against dark backgrounds. A "HAPPY SATURDAY" that actually pops off the screen.
4. **Photo Collage Grids** — 4-9 images of items, store life, or community moments tiled together with one bold headline. Weekend energy.
5. **Meme-Adjacent Posts** — Trending visual formats adapted to weekend/community vibes. Saturday morning humor, "weekend plans" relatable content. Shareable and fun.
6. **"Weekend Finds" Dramatic Product Shots** — Dark moody backgrounds, spotlight lighting effects, one hero item. Makes the weekend inventory feel like a treasure hunt.
7. **Retro/VHS/Vintage Aesthetic Posts** — Grainy textures, old-school TV scan lines, retro fonts. Nostalgic weekend vibes. Weird and cool.
8. **Community Event Posters** — If there's a local event, farmer's market, festival, or seasonal happening in any of the 5 towns, create a bold visual that ties Valley Pawn to the local scene.
9. **"Good Morning" / Weekend Greeting Posts with Personality** — Instead of just a cute animal stock photo, make these visually bold — big colorful typography, unexpected imagery, a greeting that has attitude.

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
2. **Publish to all 5 Facebook pages via the `facebook-post` skill — DO NOT use browser automation.** The skill bundles a Python script that posts via the Meta Graph API directly. Read the skill's SKILL.md if you haven't (look for `facebook-post` in the available skills). Then build a per-store batch file with location-specific community messaging (Saturday's theme is local events — tailor the caption to each town: Lexington, Waynesboro, Harrisonburg, Culpeper, Roanoke) and run:
   ```
   python3 <FACEBOOK_POST_SKILL_DIR>/scripts/post.py \
     --batch /tmp/sat-fb-batch.json \
     --image-url <public-image-url>
   ```
   Batch JSON format: `{"Lexington": "...", "Waynesboro": "...", "Harrisonburg": "...", "Culpeper": "...", "Roanoke": "..."}`. The skill handles tokens, emoji, em-dashes, and error reporting. Verify each post returns a `post_id=...` line.
3. Post to Instagram @valley_pawn (still browser/Canva flow — separate from FB)
4. Create TikTok-ready content for @thevalleypawn
5. Post to Google Business Profiles for all 5 locations (follow GBP compliance rules strictly)
6. DM Preston and Joshua on Slack with a summary of what was posted, including Canva design links AND the Facebook post IDs returned by step 2

## SATURDAY-SPECIFIC CONTENT IDEAS (Community & Local Events):
- Weekend greeting posts with bold personality and visual energy
- Team spotlight / "Meet the crew" features with graphic treatment
- "Weekend Finds" inventory highlights — make it feel like a treasure hunt
- Local event tie-ins for each store's town (farmers markets, festivals, community events)
- Family ownership story moments — "Family-owned since 2014"
- "What's happening this weekend at Valley Pawn" roundup posts
- Customer appreciation / review highlight posts
- Seasonal community content (holiday weekends, local traditions, weather-themed posts)
- "Saturday at the shop" behind-the-scenes energy