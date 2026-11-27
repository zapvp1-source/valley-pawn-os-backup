# AI Answer Check (GEO/AEO) — weekly, Thursdays

AI assistants repeat listing data, so a wrong AI answer is a listing defect. Each week: 5 cities x 4 engines, 3 questions each ("best pawn shop in <city> VA", "is Valley Pawn <city> open on Wednesday", "what are Valley Pawn <city>'s hours and address"). Wrong facts become FIX_QUEUE rows (source "ai-answer") pointing at the page the AI took them from. Newest week on top; last 8 weeks kept in full, older weeks rolled into the summary at the bottom.

Canonical facts: see RUNBOOK.md. Culpeper, Roanoke, Waynesboro open Wed (Mon–Fri 10–6, Sat 10–5). Harrisonburg, Lexington closed Wed & Sun (Mon, Tue, Thu, Fri, Sat 10–6).

---

## Week of 2026-11-26 (Thu, Thanksgiving)

**Named in 20 of 20 city/engine checks. 2 wrong facts (both Copilot, both from directory sources). Every Google, Perplexity and ChatGPT answer had the right name, address (Suite C / Ste 22), phone, hours and Wednesday status. Last week's "since 1988 / 30+ years" did not reappear.**

Cell = named in "best pawn shop" answer (position) · wrong facts across the 3 answers.

| City | Google (AI Overview / local) | Perplexity | ChatGPT | Copilot (Bing AI Mode) |
|---|---|---|---|---|
| Culpeper | Yes (#1, AIO) · 0 | Yes (#1) · 0 | Yes (#1) · 0 | Yes (#1) · 0 |
| Waynesboro | Yes (#1, AIO) · 0 | Yes (#1) · 0 | Yes (#1) · 0 | Yes (#1) · 0 |
| Harrisonburg | Yes (#1 local pack; AIO names us first) · 0 | Yes (#1) · 0 | Yes (#1) · 0 | Yes (#1) · **1** |
| Lexington | Yes (#1, AIO) · 0 | Yes (#1) · 0 | Yes (#1) · 0 | Yes (#1) · **1** |
| Roanoke | Yes (#2 local pack behind The PawnShop - 9th) · 0 | Yes (#2 behind The PawnShop) · 0 | Yes (#2 behind The PawnShop - 9th St) · 0 | Yes (#1) · 0 |

Wednesday answers: 20/20 correct. No "Dixie Pawn", "Gold-N-Pawn", Salem or Staunton store in any answer. Google AIO added Thanksgiving/Christmas/New Year closures correctly from GBP.

### Wrong facts → FIX_QUEUE
1. **Copilot, Harrisonburg hours:** "generally open Monday–Saturday… Places data: open Wednesday, closed Thursday." Source: Bing Places Harrisonburg, which shows Wednesday 10–6 as regular hours and a description saying "In operation for more than 30 years". → **LQ-048** (Bing Places sign-in needed).
2. **Copilot, Lexington "best pawn shop":** "a second Valley Pawn location at 640 North Lee Highway, Lexington." Source: chamberofcommerce.com. → added to **LQ-025** (captcha form; Joshua decision on an owner account).

### Holiday artifacts (not defects)
- Copilot (Culpeper, Lexington, Roanoke) and Perplexity (Harrisonburg, Lexington) read today's Thanksgiving closure as "closed Thursday" and in places listed Thursday as a regular closed day. Bing/Google carry the holiday hours correctly; this clears after today. Re-check Bing Lexington's Thursday row on 11/30 (it showed Closed without a holiday marker).

### Wrong source pages seen in answers (not repeated as fact)
- Perplexity Culpeper: Henry USA ("Unit C", Mon–Sat 10–6) → LQ-041; MapQuest 641 James Madison Hwy → LQ-043.
- Perplexity Waynesboro: rangeadvisor lists Wednesday closed (new; low priority, not queued yet).
- Perplexity Lexington: "Yelp, Closo and MapQuest list 439 E Nelson / 640 N Lee Hwy". Yelp search found no such listing; MapQuest → LQ-028.
- Perplexity Roanoke: "some listings show Saturday closing 6 PM, one shows Wednesday closed" → YP Roanoke (LQ-009).
- ChatGPT map widget ratings (Mapbox/Foursquare data) show Valley Pawn ★3 for Waynesboro and Lexington vs 4.8–4.9 on Google. Rating, not a listing fact; noted only.

### Sources the engines cited
- Google AIO: thevalleypawn.com location pages + FAQ, Yelp, GBP.
- Perplexity: thevalleypawn.com on every answer; gunmade, bbb, henryusa, mapquest, rangeadvisor, local.yahoo, yellowpages.
- ChatGPT: thevalleypawn.com, pawnstores.net, loopnet, mapquest, worldatlas, YellowPages.
- Copilot (Bing AI Mode): thevalleypawn.com, Bing Places, Yelp, Facebook, Chamber of Commerce, Yellow Pages.

### Method notes
- copilot.microsoft.com still redirects Joshua's Chrome to the blocked work M365 Copilot; used bing.com/copilotsearch signed out (answer is inside an iframe; read via contentDocument).
- ChatGPT guest (chatgpt.com/?q=…&hints=search). Perplexity via /search?q= in Joshua's session. Google signed in; text read from #rcnt.

---

## Week of 2026-11-19 (Thu)

**Named in 20 of 20 city/engine checks. 2 wrong facts (both "since 1988 / 30+ years"). Every name, address, suite, phone, hours and Wednesday answer was correct.**

Cell = named in "best pawn shop" answer (position) · wrong facts across the 3 answers.

| City | Google (AI Overview / local) | Perplexity | ChatGPT | Copilot (Bing AI Mode) |
|---|---|---|---|---|
| Culpeper | Yes (#1, AIO) · 0 | Yes (#1) · 0 | Yes (#1) · 0 | Yes (#1) · 0 |
| Waynesboro | Yes (no AIO loaded; #2 in Yelp list, local result) · 0 | Yes (#1) · 0 | Yes (#1) · 0 | Yes (#1) · 0 |
| Harrisonburg | Yes (no AIO; #1 local pack) · 0 | Yes (#1) · 0 | Yes (#1) · 0 | Yes (#1) · 0 |
| Lexington | Yes (#1, AIO) · 0 | Yes (#1) · 0 | Yes (#1) · **1** | Yes (#1) · 0 |
| Roanoke | Yes (no AIO; #2 local pack behind The PawnShop) · 0 | Yes (#1) · 0 | Yes (#2 behind The PawnShop) · 0 | Yes (#1) · **1** |

Wednesday answers: 20/20 correct (CUL/WAY/ROA "open 10–6", HAR/LEX "closed"). Suite C and Ste 22 present wherever an address was given. No "Dixie Pawn", "Gold-N-Pawn", Salem or Staunton store in any AI answer.

### Wrong facts → FIX_QUEUE
1. **ChatGPT, Lexington "best pawn shop":** "More than 30 years of business experience." Cited Pawn Spots + thevalleypawn.com. → LQ-040.
2. **Copilot/Bing AI Mode, Roanoke "best pawn shop":** "has served Virginia communities since 1988." Cited "Valley Pawn". Source found: our own Facebook page Valley Pawn-Roanoke (61553773147464) bio "Family Owned Pawn Shop since 1988!" → **fixed today** (bio edited, verified live). Also carried by BaseLocal (Roanoke "Family owned since 1988") and pawnshopatlas.com (Waynesboro "Since 1988", also wrong hours Mon–Sat 10–6). → LQ-040. thevalleypawn.com and its live llms.txt are clean (foundingDate 2014). Note: the local working copy `Ai Optimized Marketing/AI-Search-GEO/llms.txt` still says "since 1988" — it is not what's live, but don't republish it as-is.

### Wrong source pages seen in the results (the AIs didn't repeat them this week)
- Google still shows the old cached snippet for thevalleypawn.com/culpeper/ ("Wed & Sun: Closed … Mon–Sat 10–6"). The live page is now `noindex` with no hours, so it drops on recrawl (LQ-030).
- Henry Repeating Arms dealer locator: CUL "Unit C, Mon–Sat 10–6"; WAY "closed Wed"; ROA "closed Wed" (2362-D is correct). → LQ-041.
- Buya (WAY) "closed Wednesdays and Sundays"; CLOSO (WAY) "Mon–Sat 10–6"; Wheree (WAY) "opens 9 AM". → LQ-042.
- MapQuest Culpeper "Valley Pawn" at 641 James Madison Hwy (Pawn-Mart's address). → LQ-043.
- Bing Places (per Copilot) shows Lexington open Wednesday 10–6. Probably the 11/25 holiday special hours, needs a check. → LQ-044.
- YellowPages "Dixie Pawn Inc" (HAR), "Gold-N-Pawn" (ROA) and Lexington at 439 E Nelson: already LQ-008/009/028.

### Sources the engines cited
- Google AIO: thevalleypawn.com (location, contact, sell-gold pages), Yelp, MapQuest, Facebook, Yahoo Local.
- Perplexity: thevalleypawn.com on every answer; pawnspots for Harrisonburg competitors.
- ChatGPT: thevalleypawn.com, YellowPages, Pawn Spots.
- Copilot (Bing AI Mode): thevalleypawn.com, Bing Places, Yellow Pages.

### Method notes
- copilot.microsoft.com redirects Joshua's Chrome to the work Microsoft 365 Copilot (search "something went wrong"). Used Bing's consumer **Copilot Search / AI Mode** (bing.com/copilotsearch) signed out instead. Same Microsoft engine and index; noted in case results differ from the chat app.
- ChatGPT ran as a guest (chatgpt.com/?q=, search on). Perplexity ran in Joshua's signed-in session (no guest toggle on the URL route). Google signed in, location set from the query city.
- Google AI Overview didn't render for 3 "best pawn shop" queries (WAY, HAR, ROA); local pack/organic used for the named/position column.

---

## Older weeks (one line each)
(none yet)
