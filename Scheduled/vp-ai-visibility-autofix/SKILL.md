---
name: vp-ai-visibility-autofix
description: Self-healing companion to vp-ai-visibility-metrics — repairs the GA4 AI-referral channel definition, removes Valley Pawn-owned legacy "Dixie Pawn" content, defaults the Copilot scorecard cell to a working proxy, logs every action, and posts a Fixed/Needs-you digest to #ai-marketing
model: claude-sonnet-5
---

Runs Fridays 9:30am ET, ~30 minutes after `vp-ai-visibility-metrics` posts its scorecard to Slack #ai-marketing (private, ID C0BCEESUANM). Each run starts fresh. Device for any local/browser work: "mac-studio-2-local".

CONTEXT: vp-ai-visibility-metrics tests Valley Pawn against a named local rival on 5 AI engines, pulls GA4 AI-referral traffic, and lists "Fix" items. THIS task acts on the parts that are safely, reversibly fixable by Claude alone. Everything else is named for Joshua, with why.

STEP 1 — READ THIS WEEK'S SCORECARD.
Read the most recent "Valley Pawn — AI Visibility Scorecard" message in Slack #ai-marketing (C0BCEESUANM). Note the Fix list and whether Copilot shows "n/t (blocked)".

STEP 2 — WHITELIST FIXES:
A. GA4 "AI Assistants Tracking" channel group not catching an AI source (e.g. chatgpt.com landing in Unassigned/Direct instead of "AI Assistants") → open GA4 Admin (https://analytics.google.com/analytics/web/?authuser=1, account a256872788 / property p353209303, fullcirclepawn@gmail.com) via Claude in Chrome → Admin > Channel Groups > "AI Assistants Tracking" → confirm/repair the Source regex so it matches chatgpt\.com|chat\.openai\.com|openai|perplexity|gemini|copilot|claude\.ai|bard|you\.com|edgeservices (add any missing token — never remove existing ones) → save. Log as "pending verification" this run; confirm it held on next Friday's traffic pull.
B. Legacy "Dixie Pawn" brand name found in content Valley Pawn owns and controls directly (an old company Facebook post, a WordPress page/post) → locate it (Facebook: search the relevant store Page's own posts via the Graph API token from the `facebook-post` skill; WordPress: WordPress.com MCP connector) and edit/delete it so it reads "Valley Pawn." Do NOT touch a customer-authored review's text — you cannot and should not edit someone else's review; if "Dixie Pawn" appears inside a customer review, log it under STEP 3 as "reply, don't edit" and note it in the Needs-you queue only if it needs a brand-voice reply Joshua should see first.
C. Copilot cell shows "n/t (blocked)" because copilot.microsoft.com requires a new personal Microsoft account signup → do NOT create the account — personal identity signup is Joshua's call, not a system fix. Instead substitute Bing's local pack (https://www.bing.com/search?q=<query>) as the Copilot-engine proxy for this and future runs, score presence/rank there the same way the other engines are scored, and label the column "Copilot (via Bing proxy)" in both the Slack post and the Tracker sheet row so nobody mistakes it for true Copilot testing.

Do NOT touch: duplicate/legacy third-party listings (e.g. a "Gold-N-Pawn" ghost listing at the wrong Roanoke address, MapQuest's separate "Dixie Pawn Inc." entry) — claiming/merging those requires a business-verification step Valley Pawn hasn't completed; review-volume gaps — these need real customer reviews, not an edit, so surface as a suggestion to route through the existing Chekkit review-request flow rather than building a new mechanism.

STEP 3 — LOG EVERY ACTION.
Append rows to the "Valley Pawn — AI Search Autofix Log" sheet (ID 1A_gJuj5siq2bEKE7-ZvVyjAs6DNK7rzEaKkBbkBY9yY) — same columns as vp-ai-search-autofix. If you changed how a metric is measured (e.g. the Copilot-via-Bing substitution), also note that in this week's row of the AI Visibility Tracker sheet (ID 17gkCl9BpB8yAQZcCs6cg8SDXQfaSGdyKceNJKfwMRMs) so the trend line stays interpretable.

STEP 4 — NEEDS-JOSHUA QUEUE.
Name each non-automatable item specifically with the one concrete reason (ownership/claim, needs a real review, needs his decision).

STEP 5 — POST TO SLACK #ai-marketing (ID C0BCEESUANM; do NOT DM anyone).
Always post, regardless of outcome:
"🔧 _Valley Pawn — AI-visibility autofix (week of <date>)_ — Fixed: <n> · Needs you: <n>"
One skimmable line per item under each heading (skip empty sections).
*Sent using Claude*
