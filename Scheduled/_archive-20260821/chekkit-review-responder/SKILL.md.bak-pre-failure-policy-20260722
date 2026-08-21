---
name: chekkit-review-responder
description: Respond to 4-5 star reviews across all 5 pawn shop locations in Chekkit, then notify Preston and Joshua on Slack.
---

Navigate to https://dashboard.chekkit.io/reviews and respond to all 4-star and 5-star reviews across all 5 Valley Pawn store locations using Chekkit's AI "Generate Response" button. Process BOTH Google and Facebook reviews for each store.

**Stores to process:**
1. Valley Pawn - Culpeper
2. Valley Pawn - Harrisonburg
3. Valley Pawn - Roanoke
4. Valley Pawn - Waynesboro
5. Valley Pawn-Lexington

**For each store, process Google reviews first, then Facebook reviews:**
- Switch to the store using the location dropdown in the top-left corner
- In the top-right corner of the reviews dashboard, there is a platform dropdown that defaults to "Google". Process all reviews under Google first, then click that dropdown and switch it to "Facebook" and process those reviews too.
- For each platform, scroll through all reviews and find any with a "Respond to [Name]" button (these are unresponded reviews)
- For each unresponded review, zoom in to confirm the star rating before acting:
  - **4 or 5 stars:** Click "Respond to [Name]", click "Generate Response", wait for the AI to finish generating, then click "Post". Confirm the "Success - You responded to your review!" toast appears.
  - **1, 2, or 3 stars:** Skip — do NOT respond. Record the reviewer's name, star rating, store location, platform (Google or Facebook), and a brief snippet of the review text for the summary report.

**After all 5 stores and both platforms are complete, send a Slack DM to both Preston Peters (U03BWMEM9GR) and Joshua Davis (U03BB52MDSA) with a summary that includes:**

1. Confirmation that all 4 and 5-star reviews were responded to successfully, with a count of how many were responded to across all locations (combined Google + Facebook).
2. A breakdown of any 1-3 star reviews that need their personal attention, including: reviewer name, platform (Google/Facebook), store location, star rating, and a brief excerpt of the review. If there are no 1-3 star reviews needing attention, explicitly say "No 1-3 star reviews require attention tonight."

Example message format:
---
✅ Nightly review responses complete! Successfully responded to X reviews across all 5 Valley Pawn locations (Google + Facebook).

⚠️ The following 1-3 star reviews need your attention:
• [Reviewer Name] — [Google/Facebook] — [Store] — [X stars]: "[Review snippet]"
• ...

(or "No 1-3 star reviews require attention tonight." if none found)
---