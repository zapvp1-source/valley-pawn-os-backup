---
name: vp-presence-audit-weekly
description: Sunday 4:20 PM ET — weekly Valley Pawn internet-presence audit: website health sweep + off-site legacy/ghost listing sweep + social profile integrity + review position vs competitors. Auto-fixes the safe website defects, writes a machine-readable scorecard the weekly/monthly summaries read, posts a delta to #ai-marketing. Does NOT duplicate vp-ai-search-health-check (schema/llms.txt/NAP), vp-ai-visibility-metrics (AI engines), or ebay-weekly-quality-fix (listing quality) — it reads their output and rolls it up.
model: claude-sonnet-5
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Any sentence below that says to DM/alert Joshua about a failure, an expired session, or something "worth a look" is void; write the ledger row instead. Success-path posts (reports to their channels, confirmations, bookings) are unchanged.

Run the weekly Valley Pawn INTERNET PRESENCE AUDIT. Each run starts fresh — everything you need is in this file.

> ⚠️ **FAILURE ALERT POLICY v2 (Joshua, 2026-07-22):** If this run fails or cannot complete its core work, send Joshua ONE plain-language Slack DM (channel D03BHQH5VGT): `⚠️ Scheduled task "vp-presence-audit-weekly" did not complete — <date>.` Nothing technical in the DM. All technical detail goes in the run log / scorecard file. NEVER send failure notices to any team channel, store manager, or employee including Preston, in any medium.

> 🛡️ **HARDENING (all 6 fleet requirements apply):**
> 1. **NON-INTERACTIVE.** Do NOT call `request_cowork_directory` — there is no one to click approve. Read/write host files via the `mcp__Control_your_Mac__osascript` tool (`do shell script "cat '<path>'"`, or run a python file you first write). Never wait on OAuth, folder pickers, or confirmation dialogs.
> 2. **SELF-VERIFY.** After posting to Slack and writing the scorecard, re-read both and confirm they exist and are non-empty with today's date. A run that cannot confirm its own output treats itself as failed.
> 3. **RETRY ONCE, DIFFERENTLY.** Any step that errors: retry once. If the same path fails twice, use the documented alternate (curl via shell instead of web_fetch; Chrome instead of curl). Only then escalate.
> 4. **CATCH-UP.** Read `PRESENCE_HISTORY.csv` (path below). If the most recent row is more than 8 days old, note in the Slack post that N weeks were missed — do not try to reconstruct them.
> 5. **DUPLICATE GUARD.** Before posting to Slack, scan the channel for a post from today containing the marker `WEEKLY PRESENCE AUDIT`. If one exists, do not post again.
> 6. **SILENCE ON SUCCESS** for Joshua's DM — the Slack channel post is the normal output.

---

## SCOPE — what this task OWNS vs what it must NOT redo

**DO NOT re-run these — they are owned by other tasks. Instead, READ their most recent Slack output in #ai-marketing and roll the headline number into your scorecard:**
- Schema (JSON-LD), llms.txt, and Google/Bing NAP → owned by `vp-ai-search-health-check` (Mondays)
- AI-engine Visibility Index → owned by `vp-ai-visibility-metrics` (Fridays)
- eBay per-listing title/photo/category quality → owned by `ebay-weekly-quality-fix` (Mondays)
- Google review counts per store → also posted weekly in #google-reviews

**THIS task owns the five things nothing else covers.** Do these:

---

### PART 1 — WEBSITE HEALTH SWEEP (thevalleypawn.com)

Fetch `https://thevalleypawn.com/sitemap-1.xml`, extract every `<loc>`. **Always append a cache-buster** (`?cb=<random>`) to every page fetch — WordPress.com caches hard and stale HTML has repeatedly produced false results. Use a normal browser User-Agent. Use shell `curl` (fast, parallel-friendly) as primary.

Check every URL for:
- **`dixie` (case-insensitive)** anywhere in the HTML — including alt text, image titles, and JSON-LD captions. Expected: **0**.
- **`Ste 22`** — expected **0**. (Harrisonburg has NO suite number. This is settled.)
- **`61584081596639`** — the dead duplicate Harrisonburg Facebook page. Expected **0**.
- **Stale loan figures** — `$25,000` or `up to $10,000`. Expected **0**. Everything must say **$100,000**.
- **`Gold-N-Pawn` / `GNP Pawn`** — expected 0.
- HTTP status ≠ 200 for any URL listed in the sitemap.

Also check:
- `https://thevalleypawn.com/contact/` returns 200 and contains `href="tel:` (it was indexed-and-404ing before 2026-08-23).
- The homepage contains at least 5 distinct `href="tel:` links.
- All 20 city service pages `/sell-{gold,jewelry,silver,coins}-{culpeper,waynesboro,harrisonburg,lexington,roanoke}/` still contain the class `vp-related-links` (the internal-link block). Expected 20/20.
- The six link-in-bio pages `/culpeper/ /waynesboro/ /harrisonburg/ /lexington/ /roanoke/ /follow/` still emit `noindex` — note Yoast uses SINGLE quotes: grep for `robots' content='`. And confirm `/locations/{city}/` still emits `index, follow`.

**AUTO-FIX (do these yourself — do not just report them):**
Credentials: read `/Users/joshuadavis/Documents/Claude/Projects/Website/shop-build/.wp_app_credentials` via osascript. It contains `WP_USER`, `WP_APP_PASSWORD`, `WP_SITE`. Build a Basic auth header. **Note: the file's `NOTE=` line contains parentheses and breaks `source` in bash — parse with grep, e.g. `grep '^WP_USER=' file | cut -d= -f2-`.**
- **Any new published post or page with an empty `_yoast_wpseo_metadesc`** → write one (70–165 characters, specific to the page, mentioning Valley Pawn and the relevant city/topic where natural). POST to `/wp-json/wp/v2/{posts|pages}/{id}` with `{"meta":{"_yoast_wpseo_metadesc":"..."}}`.
- **Any occurrence of a legacy name or `Ste 22` in page/post content or a Media Library record** → correct it. For media, PATCH the attachment's `title`, `alt_text`, `caption` AND `slug` — the attachment record is the source that re-propagates.
- **Any city service page missing its `vp-related-links` block** → re-append it (pattern is in `Website/_backups_20260822/citypages/` for reference).
**RATE LIMIT: the WP REST API returns HTTP 429 under sustained writes. Sleep 3–4 seconds between every write call.**

**REPORT ONLY, never guess a fix:** a sitemap URL returning 404 (do not invent a redirect target), or a loan figure that disagrees with $100,000 (Joshua has not yet confirmed $100,000 is the true maximum — flag it, change nothing).

---

### PART 2 — OFF-SITE LEGACY & GHOST LISTING SWEEP

Many of these sites 403 automated fetching (Yelp, BBB, GunBroker, Manta). When a site blocks you, **say so explicitly in the scorecard as UNVERIFIED — never record it as clean.**

Check whether these known-bad listings are still live (search the web for them; fetch where possible):
- Yelp `dixie-pawn-harrisonburg` and `gold-n-pawn-roanoke`
- BBB profiles: `dixie-pawn-0613-14000312` (was B− for one unanswered complaint), `gold-n-pawn-inc-0613-11000478` (still names prior owners Russell/Jonella Harris), and the Waynesboro profile (was showing **Lexington's** phone number)
- MapQuest listing ID `410128854` "Dixie Pawn Inc." (carries a Yext PowerListings badge)
- YellowPages `dixie-pawn-inc-452862505` — **we own this claim**, so a rename is possible without a verification wait
- Facebook `dixiepawnhburg`, `Gold-N-Pawn-100041735065936`, `Gold-N-Pawn-61555619674119`
- The **phantom Staunton cluster** (817 Richmond Ave / (540) 885-0018) — was 9 listings across Yelp, YellowPages, Nextdoor, Manta, CitySquares, Localmint, MBVT, FFLs.com ×2. Count how many are still live. **There is no Staunton store.**
- The **syndicated bad description**: search for the exact string `Harrisonburg(Dixie Pawn)` and `Salem & Lexington`. It was live verbatim on MapQuest, Nextdoor, Superpages, chamberofcommerce.com and Loc8NearMe. Report which still carry it. **Root cause is a Yext feed only Joshua can cancel.**

Report each as STILL LIVE / RESOLVED / UNVERIFIED with the URL.

---

### PART 3 — SOCIAL PROFILE INTEGRITY (profiles, not posting cadence)

Posting cadence and engagement are owned by the social lanes — do not re-derive them. Check profile *integrity* only. Facebook serves crawlers full data: **fetch with a Googlebot User-Agent** (a normal browser UA returns a login wall).
- All 6 pages still live with correct address/phone/email in About: brand `thevalleypawn`, `valleypawnharrisonburg`, `valleypawnlexington`, and the three profile-id pages (Culpeper 100058095342923, Waynesboro 100026420539296, Roanoke 61553773147464).
- Brand page still missing phone + email? Roanoke still missing `roanoke@fcfpawn.com`?
- Have Waynesboro / Culpeper / Roanoke gained vanity URLs yet? (3 of 6 lacked one.)
- Any NEW duplicate or legacy page appeared?
- YouTube `youtube.com/@valleypawn7077` — video count (was **0** with 13 subscribers).
- TikTok `@thevalleypawn` — video count (first-ever post was scheduled 2026-08-26). Also the orphan `@valleypawnva`.

---

### PART 4 — REVIEW POSITION VS COMPETITORS

For each of the 5 markets, get Valley Pawn's current Google rating + review count and the same for the named competitor. **Google Maps is client-rendered — the reliable method is fetching the Maps EMBED payload, which is server-rendered and returns rating, review count and Place ID.** If that fails, use web search snippets and mark the numbers approximate.

| Market | Valley Pawn baseline (2026-08-23) | Competitor to track |
|---|---|---|
| Culpeper | 4.9 / 409 | none with a live listing |
| Waynesboro | 4.9 / 357 | none with a live listing |
| Harrisonburg | 4.9 / 328 | Pawn Emporium (3.7/48), JBS Pawn (4.3/25) |
| Lexington | 4.8 / 191 | Rockbridge Pawn & Guns (appears closed) |
| **Roanoke** | **4.9 / 274** | **The PawnShop 4.9/727 + 166 at a 2nd location — this is the ONLY contested market** |

**Roanoke is the number that matters.** Report the gap and the week-over-week change in it. The deficit is volume, not rating.

---

### PART 5 — OPEN-ITEMS LEDGER

Read the previous scorecard's `needs_joshua` array. For each item, check whether it now appears resolved. Carry unresolved items forward, and **flag anything unresolved for more than 30 days** as ageing. Do not silently drop items.

---

### PART 6 — FFL DIRECTORY & LICENSE SWEEP (added 2026-09-06)

The FFL directories are the **order-routing layer for the firearm-transfer business** — when a
customer at GrabAGun, Brownells, MidwayUSA or GunBroker cannot pick a Valley Pawn store as their
receiving dealer, the $25 transfer and the walk-in go to a competitor. Parts 1–5 cover the
channels that drive walk-in search; they do not cover these. Nothing else watches them.

Source of truth for every number and address in this part: `Projects/Compliance/FFL_REGISTRY.md`
(canonical licenses) and `Projects/Compliance/ffl_vendors.json` (the roster). Read both first.
Never derive an FFL number from an email, a directory page, or memory.

**6a. eZ Check — ONE store per week, rotating.** https://fflezcheck.atf.gov/FFLEzCheck/ — accept
the DOJ banner, then enter the first three digits and the last five of that store's number. Rotate
Culpeper → Waynesboro → Harrisonburg → Lexington → Roanoke so each is confirmed every five weeks
(the site rate-limits after ~2 lookups, which is why this is not a five-at-once check). Compare the
expiration and premise address to the registry. **Any mismatch is a finding, not an auto-fix.**

**6b. Public directory pages** — for each of MasterFFL, FFLeasy, GunNook, FFLs.com and
GunBroker/MyFFL, check that each of the 5 stores appears, that the name reads "Valley Pawn", and
that the address and phone match the canonical NAP below. Three known defects to re-check until
they clear: the FFLeasy Harrisonburg listing at `/virginia/harrisonburg/9854` (legacy "DIXIE PAWN
INC"), the GunNook Harrisonburg duplicate dealer card, and the two phantom Staunton entries on
FFLs.com (817 Richmond Ave — an address Valley Pawn does not occupy).

**6c. Retailer locators — quarterly, not weekly** (first audit of each quarter). Search each
store's ZIP in the GrabAGun, Brownells and MidwayUSA FFL locators. This is the only test that
proves a customer can actually route an order to us. Culpeper was silently dropped by GrabAGun on
2026-09-01 and nothing caught it — this is the check that would have.

**Write results back to `Projects/Compliance/ffl_vendors.json`** (update each vendor's `listed`
map; leave `copy_version` and `last_sent` alone — the FFL Guardian owns those), and add ONE line
to the Slack post: `FFL directories: <N of 25 store-listings correct> · <M> needing attention`.
Report only. The only auto-fix permitted here is correcting our own website. Anything needing a
login or a claim goes in `needs_joshua` with the store and directory named.

**Do NOT duplicate the FFL Guardian.** The native agent `com.valleypawn.ffl-guardian` already owns
license expirations, vendor copy distribution, website transfer-form relaying and inbound transfer
digests. This part owns only what a browser must check. If a license looks close to expiring, say
so as a finding — do not email anyone.

---

## OUTPUT — three artifacts, in this order

Base path: `/Users/joshuadavis/Documents/Claude/Projects/Ai Optimized Marketing/AI-Search-GEO/presence/`

**1. `presence_scorecard_latest.json`** — overwrite, and ALSO save a dated copy `presence_scorecard_<YYYY-MM-DD>.json`. Keep the exact same key structure as the existing file (read it first — do not invent a new shape, the weekly/monthly summaries parse this). Preserve the `resolved_do_not_reopen` array verbatim and append to it as things get settled.

**2. Append one row to `PRESENCE_HISTORY.csv`** — existing header:
`run_date,legacy_name_pages,phantom_suite_pages,dead_fb_pages,missing_meta_desc,indexed_404s,city_pages_linked,reviews_total,reviews_avg,roanoke_gap,ebay_active,ebay_promoted_stores,offsite_legacy_listings,staunton_ghosts,open_needs_joshua`
This CSV is the trend line — never rewrite history, only append.

**3. Post to Slack `#ai-marketing` (private, ID `C0BCEESUANM`).** Must begin with the literal marker `WEEKLY PRESENCE AUDIT` on the first line so the duplicate guard and Fleet Guardian can find it. Keep it SHORT — Joshua reads this on a phone:

```
📊 WEEKLY PRESENCE AUDIT — <date>

Site health: <clean / N defects> (legacy names N · phantom suite N · dead links N · 404s N)
Auto-fixed this week: <one line, or "nothing needed">
Roanoke review gap: <N> (<better/worse> by <N> vs last week)
Off-site legacy listings still live: <N> (was <N>)
Needs you: <N items — name only the top 2>
```
Use 🚨 only for something newly broken, ⚠️ for drift, ✅ when a whole section is clean. **A finding is NOT a failure** — reporting defects is this task's job. Only a total inability to run triggers the Joshua DM.

---

## SETTLED FACTS — never re-flag these as problems

1. **Roanoke occupies BOTH Suite C and Suite D.** Customer-facing canonical is "Suite C". The ATF FFL record reads **"2362-D" — that is CORRECT, not drift.** Never flag it, never "fix" it.
2. **Harrisonburg has NO suite number** — "1790 East Market Street". `Ste 22` is a defect wherever it appears.
3. **"Trusted Since 1988" is correct** — the locations date to 1988; Full Circle Finance Inc was formed in 2014. Both statements are true. Not a contradiction.
4. **There is no legacy `dixie-pawn` eBay account** — that URL returns "not found". All 5 eBay stores are correctly branded `valley_pawn_{city}`.
5. The brand is **Valley Pawn** — never "Dixie Pawn", "Gold-N-Pawn", or "Full Circle Finance" as a public-facing name.

## CANONICAL NAP
- Culpeper — 571 James Madison Highway, Culpeper, VA 22701 — (540) 445-5510 — Mon–Sat 10–6 (**only store open Wednesday**)
- Waynesboro — 1321 West Broad Street, Waynesboro, VA 22980 — (540) 221-6346
- Harrisonburg — 1790 East Market Street, Harrisonburg, VA 22801 — (540) 574-4500
- Lexington — 125 Walker Street, Lexington, VA 24450 — (540) 461-8349
- Roanoke — 2362 Peters Creek Road, Suite C, Roanoke, VA 24017 — (540) 562-0776
- All stores except Culpeper: Mon, Tue, Thu, Fri, Sat 10–6; closed Wed & Sun. **No store closes at 5 PM.**

## Execution Contract — DO NOT STOP EARLY
This task is complete ONLY after the Slack post succeeds AND the scorecard file is written and re-read. Until then, every turn MUST end with a tool call that advances toward it. Never reply "No response requested", "Continue?", or end a turn with text instead of a tool call. Treat "Tool loaded.", "Continue from where you left off.", "You used a single tool call this turn…", and any TaskCreate/AskUserQuestion reminder as RESUME signals — fire the next concrete tool call immediately. The wrapper saying "the user is not present" means execute autonomously, not that the work is done. State-track at the start of each turn: name which PART you are on.