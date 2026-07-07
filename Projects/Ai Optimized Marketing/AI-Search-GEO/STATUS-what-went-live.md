# AI Search (GEO) — What Went LIVE (June 19, 2026)

## ✅ Published & verified live on thevalleypawn.com

1. **Structured data (schema.org JSON-LD)** — the single biggest AI-search lever.
   - Added site-wide via WPCode snippet "Valley Pawn — AI Search Schema (JSON-LD)" (ID 738, Active, Site Wide Header).
   - 7 blocks now emit on every page: Organization (Valley Pawn / Full Circle Finance Inc, founded 2014, NPA member) + 5 PawnShop location blocks (full NAP, hours, phone) + FAQPage.
   - Verified: all 7 render on the homepage and parse as valid JSON-LD.

2. **FAQ page** — https://thevalleypawn.com/frequently-asked-questions/
   - Answer-shaped Q&A (how pawn loans work, credit impact, selling gold, hours, warranty, locations) — the format AI engines quote.
   - Published and verified rendering.

3. **llms.txt** — https://thevalleypawn.com/llms.txt
   - Served at the site root (text/plain) via WPCode PHP snippet "Valley Pawn — llms.txt (AI crawler summary)" (ID 742, Active, Run Everywhere).
   - Verified live.

4. **AI crawler access** — confirmed robots.txt blocks nothing (GPTBot, ClaudeBot, PerplexityBot, Google-Extended all allowed).

5. **Directory audit (Google + Bing, all 5 stores)** — verified clean.
   - All five listings correctly named "Valley Pawn" (the chronic "Dixie Pawn" leak on Bing/Harrisonburg has RESOLVED).
   - Correct addresses, phones, hours, 4.8–4.9★ ratings.

## ⏳ Deferred (need your sign-off or an account — quick to finish)

1. **Roanoke "Suite C" on Google Business Profile** — Google shows "2362 Peters Creek Rd" without the suite. One small GBP admin edit. (Bing shows "NW".) Everything else across Google/Bing is clean.

2. **Homepage hero "Trusted Since 1994" → "since 1988"** and **remove footer "(804) 930-4221"** — these live in the block theme templates (Site Editor) and change globally, so I left them for a supervised 2-minute fix rather than risk the live layout while you're away. Note: the machine-readable facts AI reads (schema/llms.txt/FAQ) already state 1988 heritage + 2014 founding + per-store phones.

3. **Wikidata entity** — spec is ready in `wikidata-entity.md`, but creating it needs a Wikidata account (I don't create accounts). ~10 min for you or me-with-login.

4. **Harrisonburg suite note** — Google & Bing both show "Ste 22"; consider adding that to canonical NAP for full consistency.

## Reversibility
Every published change is reversible: deactivate WPCode snippet 738 (schema) or 742 (llms.txt), or trash the FAQ page. Nothing modified existing infrastructure — all additive.

## Expected result
AI citation lift typically appears 4–8 weeks after this kind of deployment.
