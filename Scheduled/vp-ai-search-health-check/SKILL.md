---
name: vp-ai-search-health-check
description: Weekly Valley Pawn AI-search (GEO) health check — schema, llms.txt, and Google/Bing NAP; posts to Slack #ai-marketing
model: claude-sonnet-5
---

Run the weekly Valley Pawn AI-search (GEO) health check, then post a summary to the Slack channel #ai-marketing (private channel, ID C0BCEESUANM). Use the Claude in Chrome browser tools for the web checks and the Slack MCP connector to post. Each run starts fresh — everything you need is below.

CONTEXT: Valley Pawn (thevalleypawn.com, WordPress). Schema is injected site-wide via WPCode snippet #738; /llms.txt is served via WPCode snippet #742. These were deployed for AI-search visibility and this check confirms nothing has silently broken or drifted.

CHECK 1 — SCHEMA (biggest lever):
- Navigate to https://thevalleypawn.com/?cb=health (cache-buster) and run JavaScript to collect every <script type="application/ld+json"> block.
- Confirm these 7 are present AND each parses as valid JSON: Organization "Valley Pawn"; PawnShop for Culpeper, Waynesboro, Harrisonburg, Lexington, Roanoke; and one FAQPage. (An 8th block from Yoast is normal — ignore it.)
- Flag if any of the 7 are missing or fail to parse.

CHECK 2 — LLMS.TXT:
- Navigate to https://thevalleypawn.com/llms.txt and confirm it returns plain-text content containing "Valley Pawn" and all five city names. Flag if it 404s, is empty, or returns HTML instead of text.

CHECK 3 — DIRECTORY NAP (Google + Bing, all 5 stores):
For each store, open the public listing and compare Name / Address / Phone / Hours to canonical below.
- Google: https://www.google.com/maps/search/valley+pawn+<city>+va
- Bing:   https://www.bing.com/maps?q=valley+pawn+<city>+va
Canonical NAP:
  • Culpeper — 571 James Madison Highway, Culpeper, VA 22701 — (540) 445-5510 — Mon–Sat 10am–6pm (ONLY store open Wednesdays)
  • Waynesboro — 1321 West Broad Street, Waynesboro, VA 22980 — (540) 221-6346 — Mon,Tue,Thu,Fri,Sat 10am–6pm (closed Wed & Sun)
  • Harrisonburg — 1790 East Market Street, Ste 22, Harrisonburg, VA 22801 — (540) 574-4500 — closed Wed & Sun
  • Lexington — 125 Walker Street, Lexington, VA 24450 — (540) 461-8349 — closed Wed & Sun
  • Roanoke — 2362 Peters Creek Road, Suite C, Roanoke, VA 24017 — (540) 562-0776 — closed Wed & Sun
Flag as DRIFT: any legacy/wrong name (especially "Dixie Pawn"), wrong street number, missing suite (Roanoke must show "Suite C"), any wrong phone digit, wrong hours (watch the Culpeper-only-Wednesday rule), or a missing / duplicate / "permanently closed" listing. Ignore pure formatting differences (St vs Street, ZIP vs ZIP+4, phone format).

POST TO SLACK — channel #ai-marketing (ID C0BCEESUANM; do NOT DM anyone):
- If everything is clean, post one line: "✅ Valley Pawn AI-search health check — schema 7/7 ✅, llms.txt live ✅, listings 10/10 clean ✅"
- If anything is off, post a short skimmable bullet list of exactly what's wrong and the suggested fix (e.g. which snippet to re-enable in WPCode, or which store/directory drifted and to what). Keep it phone-readable. Lead with a 🚨 or ⚠️ header line.