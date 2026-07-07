# Valley Pawn — AI Search (GEO) Package & Publish Checklist

Goal: get Valley Pawn surfaced and cited by AI search engines (ChatGPT, Perplexity,
Gemini, Google AI Overviews, Claude). AI engines read the same trusted signals as search —
structured data, consistent directory listings, and clear question-and-answer content.

## What's in this folder
- `llms.txt` — AI-crawler summary file → publish at https://thevalleypawn.com/llms.txt
- `schema/valley-pawn-schema.html` — validated JSON-LD (Organization + 5 PawnShop + FAQ)
- `content/faq-page.md` — answer-shaped FAQ → publish as a page (e.g. /faq/)
- `content/city-answer-snippets.md` — per-city intro paragraphs for existing pages
- `wikidata-entity.md` — Wikidata item spec

## Publish checklist (in priority order)

### 1. Structured data (biggest lever)
- [ ] Add the JSON-LD from `schema/valley-pawn-schema.html` site-wide (header/footer
      injection plugin, e.g. WPCode / "Insert Headers and Footers", or Yoast custom schema).
- [ ] Validate: https://validator.schema.org/ and https://search.google.com/test/rich-results

### 2. AI crawlers + llms.txt
- [x] robots.txt already allows all bots (nothing disallowed) — AI crawlers can read the site.
- [ ] Publish `llms.txt` at the site root (llms.txt plugin, or hosting file manager).

### 3. Answer-shaped content
- [ ] Publish `content/faq-page.md` as a /faq/ page; apply the FAQPage schema to it.
- [ ] Add city snippets from `content/city-answer-snippets.md` to the matching city pages.

### 4. Directory consistency (NAP)
- [ ] Review the directory drift report (run separately) and push corrections via
      directory-listing-push for any Google/Bing/Apple/Yelp/Facebook drift.

### 5. Entity signal
- [ ] Create the Wikidata item per `wikidata-entity.md`.

## Homepage corrections needed (factual consistency — important for AI confidence)
- [ ] "Trusted Since 1994" → "Serving the Valley since 1988" (oldest acquired store opened 1988;
      "1994" matches none of the actual dates and creates a conflicting signal).
- [ ] "Trusted Since 1994 ⭐" badge → update to 1988 or remove the specific year.
- [ ] Footer contact "(804) 930-4221" → remove org-level number; rely on the five 540 store
      numbers (per decision). The Find Us map embed also uses a raw query that can pull stale
      listings — prefer the canonical "Valley Pawn <City> VA" map links.

## Expected timeline
Most businesses see measurable lift in AI citations 4–8 weeks after deploying this.
