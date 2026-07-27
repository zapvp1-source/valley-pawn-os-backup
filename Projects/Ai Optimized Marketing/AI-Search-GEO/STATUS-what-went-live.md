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

---

## ⚠️ Re-verification — July 22, 2026 — item #5 above ("Dixie Pawn RESOLVED") was wrong, correcting the record

A weekly AI-visibility scorecard run flagged "Dixie Pawn" surfacing again in a Google organic result. Live-checked it directly rather than trusting the prior claim:

- **MapQuest — confirmed still live.** `https://www.mapquest.com/us/virginia/dixie-pawn-inc-410128854` — a listing named **"Dixie Pawn Inc."** at 1790 E Market St, Harrisonburg (the correct address, wrong name) sits **separately** from the correct "Valley Pawn" MapQuest listing at the same address. This listing is marked **"Owner-Verified"**, meaning someone (presumably under the old ownership/name, pre-2026 rebrand) already claimed it — that verification lock is why it hasn't self-corrected and won't via a public "report a problem" form.
- **Bing Places & Apple Business Connect** — not re-verified live today (no logged-in session available in this browser — see blocker below), but the June 22 `Refine Social Media/audit_2026-06-22/FINDINGS.md` audit (more recent and more thorough than this file's June 19 claim) already documented Dixie Pawn still showing on **both**, including Apple Maps showing **Dixie Pawn only, with no Valley Pawn listing at all**. Treat the June 19 "RESOLVED" line above as **inaccurate** — it likely reflected Google/Bing search-result spot checks, not a systematic per-directory listing audit.
- **thevalleypawn.com/sell-gold-harrisonburg** — re-checked live, page is 100% correct (Harrisonburg address/phone throughout). The Google organic snippet that showed Culpeper's info was a stale SERP cache, not a live site bug. No action needed; will self-correct as Google recrawls, can be sped up via Search Console re-index request if it hasn't cleared in a few weeks.
- **Gemini "wrong Harrisonburg address" claim (from this week's AI-visibility scorecard)** — also **retracted**. Gemini said 1790 East Market Street, which is the correct canonical address. That was a false positive in the scorecard, not a real AI hallucination.

### Blocker — needs Joshua, can't be pushed autonomously
Claimed/verified business directory listings require account login + identity/2FA verification that I won't do on Joshua's behalf (no saved session exists for any of these three consoles in this browser):

1. **MapQuest** — `https://business.mapquest.com/?sourceUrl=https%3A%2F%2Fwww.mapquest.com%2Fus%2Fvirginia%2Fdixie-pawn-inc-410128854&mqid=410128854` → "Sign in to get started," then claim/dispute the existing owner-verified "Dixie Pawn Inc." listing and rename it (or merge into the correct Valley Pawn listing at the same address).
2. **Bing Places for Business** — `https://www.bingplaces.com/` → sign in, find Harrisonburg, verify/fix the name field. Per the `directory-listing-push` skill, Bing's syndication layer has a history of reverting this specific field even after a prior fix.
3. **Apple Business Connect** — `https://businessconnect.apple.com/` → sign in, claim/fix the Harrisonburg listing (currently showing Dixie Pawn with no Valley Pawn alternative at all on Apple Maps — the most severe of the three).

Once Joshua logs into any of these (or shares/creates dedicated business accounts), I can drive the actual field edits via `directory-listing-push`. Re-run `directory-listing-monitor` after each fix to confirm it stuck — all three directories have a documented history of silently reverting this specific correction.
