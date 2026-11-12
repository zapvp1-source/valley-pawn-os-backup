# Outbound Community Engagement — Runbook
Built 2026-10-31. Joshua: "We should be commenting and reposting stuff around the community" → plan approved ("go and build").
Run daily by the scheduled task **Social outbound engagement** (Claude in Chrome on Joshua's Chrome + device_bash on the Mac).
This file is the source of truth for the procedure — the task prompt only points here, so improve THIS file (with a dated note at the bottom), not the prompt.

## TWO MODES (2026-11-01 — read first)
Unattended scheduled runs are refused by Claude's permission check when they try to post publicly (comment/share/follow/reply) — confirmed 3 times on 11/1, even with Joshua's written OK in the prompt. So:
- **PREP mode = the daily scheduled run.** Do everything EXCEPT clicks that publish: resolve/upkeep the watchlist (searches are read-only), read each store's watchlist pages, pick today's posts within the RAMP caps, draft the comment/share text, list follow candidates and any comments on our own posts that need replies. Do NOT switch into pages and do NOT click Post/Share/Follow. Write the picks to `QUEUE.json` (replace entries older than 48 h — a stale pick is dropped, never posted late) and summarize in DAILY_LOG.md. QUEUE entry: {"id","created","store","action": comment|share|follow|reply,"target","target_url","post_url","post_snippet","post_time","text","checks": "facts in source post: yes; NO-list: clear"}.
- **POST mode = a chat Joshua starts** ("post the community queue", "do today's Facebook engagement", or similar). That session reads QUEUE.json, re-opens each post (skip it if deleted, older than 48 h, or the thread has turned negative), re-checks the RAMP caps against ledger.jsonl for today, posts as the store page per the click path below, appends ledger rows, removes posted items from QUEUE.json, switches back to Joshua Davis. Joshua's request in that chat is the approval; no per-post questions.
- **SHARES go out in POST mode (2026-11-03).** The Publer route was tried 11/2: Facebook published the community post's link as a bare URL with no preview card and the original page was not notified — it looked like spam and lost the point of sharing. So PREP queues shares like everything else (`action: "share"`, `post_url` permalink, caption in `text`, no `auto` flag) and the POST-mode chat uses Facebook's own Share button as the store page. The native agent `com.valleypawn.community-share-autopost` stays installed but only acts on items marked `auto: true` (none) — do not set it.
- Comments on other pages, follows and replies on our own posts stay in POST mode (browser-only).
- Nothing in PREP mode needs Joshua; no HUMAN_QUEUE rows for this.

## Why
90-day audit (SOCIAL_AUDIT_2026-10-20.md): followers flat (~6,400), 24 comments in 90 days, Roanoke 38 followers. We only ever posted on our own pages.
Commenting on and sharing posts from the pages our neighbors already follow puts each store's name in front of people who don't follow us yet, and the shared page usually notices and returns the favor.

## Proven mechanics (2026-10-31, live)
- Joshua's Chrome is signed in to Facebook as Joshua, who manages all 6 pages.
- To act as a store: open the store's `page_url` → click **"Switch Now"** (or "Switch") → the comment box then reads **"Comment as Valley Pawn-<Store>"**. CHECK THAT LABEL before typing — if it names Joshua, stop and switch again. Never comment as Joshua.
- Comment: click the post's comment textbox → type → Return → confirm the comment appears "by Valley Pawn-<Store>".
- Share: post's **Share** button → dialog shows the page name + **Feed** + **Public** → "Say something about this..." → type caption → **Share now** → confirm on the store page's Posts list ("Shared post from <org>").
- Switching from one page to another: the page's own "Switch" button can silently leave you on the previous page. Reliable path: top-right avatar → **See all profiles** → pick the page; then re-check the "Comment as" label (2026-11-02).
- Switch back: top-right avatar → **"Switch to Joshua Davis"**. ALWAYS do this at the end of the run AND before stopping on any failure — Joshua's Chrome must never be left acting as a page.
- Facebook search for pages: `https://www.facebook.com/search/pages/?q=<query>`; results are `div[role="feed"] > div` cards (name · category · address · followers).
- Use short browser batches (≤6 actions) with explicit `computer wait` steps; long batches time out. Don't put long sleeps inside javascript.

## RAMP — overrides every cap in this file (Joshua 2026-10-31: "modest approach and build over time", don't draw Facebook's attention)
All 6 pages act through Joshua's one Facebook account, so volume grows slowly. Level is per page; start date 2026-10-31. Store the current level per store in WATCHLIST.json `ramp_level` (default 1) and `ramp_since`.
| Level | Comments/day | Shares/week | New follows/day | Own-page replies |
|---|---|---|---|---|
| 1 (weeks 1–2: 10/31–11/13) | 1 | 1 | 5 | all |
| 2 (weeks 3–4) | 2 | 2 | 8 | all |
| 3 (weeks 5–6) | 2 | 3 | 12 | all |
| 4 (week 7+, ceiling) | 3 (Roanoke 4) | 3 (Roanoke 4) | 15 (Roanoke 20) | all |
- Move up ONE level only after 14 days at the current level with zero Facebook warnings for that page. Never skip levels.
- Any warning, "action blocked", "try again later", a comment that silently fails to appear, or a "this looks like spam" prompt on ANY page → stop everything for all pages that day; that page drops back one level (min 1) and holds 14 days; all other pages hold their level 14 days. Log it in DAILY_LOG.
- Act like a person: skip one random day per page per week (no actions that day except replies); spread a page's actions over the run with 30–90 s gaps between comments/shares/follows; vary which store goes first; never the same comment length/pattern back to back.
- Replies to people who comment on OUR posts are not capped — answering our own customers is normal behavior.
- The caps tables below are the level-4 ceiling, not the starting point.

## Daily volume (caps — never exceed)
| Page | Comments/day | Shares |
|---|---|---|
| Roanoke (priority: 38 followers) | up to 5 | 1/day Mon–Sat |
| Culpeper, Waynesboro, Harrisonburg, Lexington | up to 3 each | 1 on Mon, Wed, Fri |
| Brand (Valley Pawn) | up to 2 | 1 on Sun |
- Max 1 comment per target page per store per day. Never two Valley Pawn pages on the same post (check ledger by target_url+post_snippet).
- Never comment on the same post twice. If there aren't enough good posts, do fewer — zero is fine. Quality over quota.

## What to engage with (posted within the last 48 h)
YES: high-school/college wins and senior nights, community events and festivals, parades, library/park programs, downtown happenings, charity and food drives, first-responder thank-yous/milestones, local business milestones on chamber/downtown pages, weather/seasonal beauty, history posts, pet adoption features.
NO (skip the post entirely): crime, arrests, accidents, fires with injuries, deaths/obituaries, anything political or about elections, taxes, government disputes, lawsuits, school closures for safety reasons, anything with an angry comment section, anything about guns/ammo/hunting gear, posts from or about competitors (pawn shops, jewelers, gold buyers, cash-for-gold), posts naming private individuals in a negative or personal way, fundraisers asking for money (a share is OK only for a food/toy drive asking for items or volunteers).

## How the words must read
- Comments: 6–25 words, one sentence or two, about a SPECIFIC detail in that post (the score, the event name, the photo). Warm, neighborly, plain. Max one emoji. No hashtags, no links, no prices, no "come see us", no mention of the store, pawn, loans, gold, sales. Never repeat an opening phrase used by the same store in the last 30 days (check ledger.jsonl).
- Share captions: 1–2 sentences, credit the organization by name, add one useful specific (date/time/place copied exactly from their post — never invent or "fix" a fact), optionally end with a short question to neighbors. Same no-selling rules. Use the town's own words from WATCHLIST `town_words` and CITY_COMMUNITY_KB.md (e.g. Culpeper is Piedmont, never "Shenandoah Valley").
- Never state a date, time or place that isn't in the source post itself.
- Never use "Dixie Pawn" or "Gold-N-Pawn". No giveaway references.

## Replies on our own pages (same run)
For each store page (while switched into it): open the page's notifications / recent posts; reply to every new comment on our posts from the last 3 days that has no page reply yet — short, warm, specific; thank them; answer a simple fact only if it is on the post. Do NOT reply publicly to complaints, pricing disputes, legal/firearm questions or anything heated — log those in DAILY_LOG.md under "Needs a person" (no messages to anyone). Customer DMs stay with Chekkit — don't touch Messenger.

## Local follow sweep (Joshua 2026-10-31: "follow all the community pages… and anyone in the geographic area")
Done while switched into each store page, after comments/shares. Every follow is a ledger row (action "follow").
1. **Every watchlist page** (status active) is followed as the store page — no cap; this is a one-time catch-up, then automatic as new pages resolve.
2. **Every local Page in the town:** search Facebook Pages with each of these, one or two queries per run, rotating: "<town> VA", "<town> church", "<town> restaurant", "<town> school", "<town> youth sports", "<town> fire", "<town> events", "<town> real estate", "<town> salon", "<town> auto". Follow results whose card shows an address in that town or county (or its name clearly is a local org there). Skip competitors (pawn, jewelry, gold/silver buyers, gun shops), political/campaign pages, adult/vape/cannabis, and anything that fails the NO list.
3. **Local people who engage with us:** anyone who commented on, reacted to, or reviewed that store page in the last 14 days → follow them back if Facebook offers a Follow button on their profile (many personal profiles don't; skip those). Never search out or bulk-follow private individuals who haven't interacted with us — Facebook treats that as spam and can block the page from following, commenting or posting, which would also stop our regular posts.
4. **Pacing (protects the page):** at most 20 new follows per store page per day (Roanoke 25), spaced out (a few seconds between). If Facebook shows "You're temporarily blocked", "action blocked", or "try again later": stop ALL follows/comments for that page for 72 h, note it in DAILY_LOG, and cut that page's follow cap in half for the next 2 weeks (record in WATCHLIST.json store-level `follow_cap`).
5. Record followed local pages in WATCHLIST.json under the store's `followed_local` list ({name, url, followed}) so they are never re-followed; good ones (active, community-minded, posting weekly) can be promoted into `pages` for commenting.

## Watchlist upkeep (self-healing, every run)
- `url: null` (status unresolved): search Facebook Pages with `query`; accept the result only if its card/page shows the same town (address or name) and the right organization; save url, followers, status active. Not found → resolve_attempts += 1; after 3 → status "retired" with a note.
- On first visit to an active page as the store: click **Follow** if offered (status followed_as_page = true). Following puts their posts in the store page's feed.
- A page whose newest post is older than 60 days → status "dormant" (re-check monthly).
- Discovery: up to 2 NEW pages per store per week — a local organization a watchlist page tagged or shared, located in that town, that fits the YES list. Add it with a note "discovered <date> via <page>".
- Update `last_checked`, `last_post_seen`, `followers`. Never delete entries.

## Order of work each run
1. device_bash: read WATCHLIST.json, last 30 days of ledger.jsonl, top of DAILY_LOG.md, CITY_COMMUNITY_KB.md section for each town.
2. Chrome: tabs_context_mcp, then a NEW tab. Go to facebook.com — if it asks to log in or shows a security checkpoint: switch nothing, add ONE line to `Life OS/HUMAN_QUEUE.md` ("Facebook needs Joshua to sign in on the Mac's Chrome — outbound engagement paused") if not already there, write DAILY_LOG, stop.
3. For each store in order Roanoke, Culpeper, Waynesboro, Harrisonburg, Lexington, Brand: switch into the page → watchlist upkeep for 3–4 of its pages (rotate; oldest last_checked first) → pick posts → comment / share per caps → reply sweep on own page → append each action to ledger.jsonl immediately after it is confirmed on screen.
4. Switch back to Joshua Davis. Close your tab.
5. Write WATCHLIST.json back (full JSON, valid), prepend today's section to DAILY_LOG.md (counts per store, anything in "Needs a person", watchlist changes).

## Ledger row (ledger.jsonl, one JSON object per line)
{"ts": ISO-8601 ET, "store", "action": comment|share|reply|follow, "target", "target_url", "post_snippet" (first ~100 chars), "text", "verified": true, "run": "daily-YYYY-MM-DD"}

## Failure rules (Rule 16 — no failure pings)
- Chrome/Mac unreachable → one row in `Valley Pawn OS/fleet/FAILURE_LEDGER.md` (| date time ET | social-outbound-engagement | plain sentence | NEEDS_HUMAN: no | OPEN |), stop; tomorrow retries.
- A click doesn't do what's expected twice → skip that action, log it, continue with the next store.
- Never message Joshua, any Slack channel, or any employee from this task. Measurement is reported by the Monday "Social campaign scorecard" task.

## Change notes
- 2026-11-11 (PREP run): (1) The page-feed `story_message` walk-up can return the PREVIOUS post's photo link when posts share a wrapper; stop walking up as soon as the ancestor holds more than one `story_message`, then take the first `a[href*="/photo"]` or `/posts/` link inside. (2) On a multi-photo post the photo permalink shows only "This photo is from a post. View post" — read that link's href and use the `/posts/pfbid…` URL as post_url after confirming key phrases on it. (3) If the Chrome extension drops mid-batch ("connection was lost"), pause ~45 s, call tabs_context_mcp, and re-run only read-only calls. (4) In device_bash, write scratch files under $HOME (e.g. ~/sec.md), never /tmp — /tmp can hold a stale file from another session that you cannot overwrite, and a script would silently read it instead (happened today; DAILY_LOG was restored byte-for-byte).
- 2026-11-10 (PREP run): (1) The run can start with NO folders connected (device_bash errors "No folders are connected"). Call device_request_folder_access for ~/Documents/Claude/Projects once — it was granted unattended — then continue; do not log it as a failure. (2) A multi-photo post's photo permalink can show scrambled caption text in `[role=complementary]`; if the key phrases don't read back, don't use that photo as a share post_url — pick a single-photo post whose text confirms.
- 2026-11-09 (PREP run): (1) Joshua's Chrome can be switched to another page he manages (seen: Mountain Valley Luxury Shenandoah Valley) by something outside this task mid-run. Before closing the tab, open facebook.com and read the composer ("What's on your mind, <name>?"); if it isn't Joshua, avatar → Joshua Davis — a PREP run may make this one switch. (2) Photo posts have no /posts/ link even after hovering; walk up from the story_message to `a[href*="/photo"]` and use `https://www.facebook.com/photo/?fbid=<fbid>` as post_url — open it and check key phrases in `[role=complementary]` text to confirm. (3) When hover returns 2+ /posts/ links, open each; the first is not always the hovered post.
- 2026-11-08 (PREP run): (1) Sunday is the last day of the share week; on Sundays queue shares for the next week only from posts made Saturday or later, so they are still inside 48 h on Monday. (2) If a drafted comment is tied to a date ("this weekend", "tonight"), re-check it each run and reword or replace it once that date passes, even if the post is still under 48 h. (3) On page-search pages, `document.title` itself can trip the query-string block; print only the card text with `?&=` stripped.
- 2026-11-07 (PREP run): permalink without hovering — find the post's `[data-ad-rendering-role=story_message]`, walk up `parentElement` until a node contains `a[href*="/posts/"]`, and return that pathname split with spaces; `elementFromPoint` on the timestamp returned nothing. Picks can name a private person only if the post is about an organization; leave performers/presenters/students unnamed in our text (CITY_COMMUNITY_KB rule 2).
- 2026-11-06 (PREP run): (1) inside a browser_batch, put navigate → a fixed `computer wait` 5–6 s → JS; a JS polling loop that waits for `location.pathname` can throw 'Inspected target navigated' if the navigation commits mid-loop — just re-run the JS standalone. (2) Searching a name that redirects (Salem Red Sox → Salem RidgeYaks) only shows the new name in the card; accept it when the address matches the town. (3) The page search blocks output that echoes `location.search` — print `document.title` instead.
- 2026-11-04 (PREP run): faster page read without screenshots of every post — after load, run JS: click every `div[role=button]` whose text is 'See more', then read `[data-ad-rendering-role=story_message]` (one per post, in order). Post times are scrambled in the DOM; read them from a 0.55-scale screenshot or a zoom of the header (hover the time for the full date). Facebook events: `a[href*="/events/"]` gives the event permalink — open it and read `[role=main]` for date/time/place before writing a share caption.
- 2026-11-03 (PREP run): mechanics — (1) Facebook page-to-page navigation is a single-page app: a 3 s wait can still show the PREVIOUS page (twice today). Wait 5 s and confirm `location.pathname` matches the target before reading or screenshotting. Same for page search: if results look identical to the last query, re-run it before counting a miss. (2) On Election Day and holidays most watchlist pages post closings — those are NO-list; expect thin picks. (3) PREP drops `posted`/`scheduled` items from QUEUE.json each run (they are already in ledger.jsonl) and re-syncs WATCHLIST `last_share` from Publer ledger rows.
- 2026-11-02 (PREP run): mechanics — (1) the tool output blocks URLs that carry a query string, so in page-search extraction return `u.pathname + ' id=' + u.searchParams.get('id')` (profile.php pages) and, if a slug is still blocked, `.split('').join(' ')` it. (2) A post's permalink appears in the DOM only after hovering its timestamp: hover the "Xm/Xh" label, then read `a[href*="/posts/"]` (strip the query) and open it once to confirm before putting it in a share pick. (3) Fast page read: navigate → scroll the "Posts" heading into view via JS → one 0.55-scale screenshot shows the newest post and its readable time; click "See more" via JS and read `div[dir=auto]` for full text.
- 2026-11-01 (third firing): a manual fire_trigger re-run started from Joshua's linked session was also refused. Scheduled or fired runs can't post publicly no matter who starts them. Posting only works in an interactive chat where Joshua can approve each post.
- 2026-11-01 (second firing): adding Joshua's written pre-authorization to the task prompt did NOT get past the permission check — the comment send was refused again. Don't spend more firings re-testing: until Joshua answers the HUMAN_QUEUE [DECISION] row, unattended firings should go straight to read-only watchlist upkeep (page searches, no switching into pages) and log. When a send is refused after text is typed, clear the draft (cmd+a, Delete) before switching back.
- 2026-11-01: the unattended scheduled run was refused by the permission check when it tried to post a comment ("Real-World Transactions") — nothing posted. Rule added: if any comment/share/follow/reply click is refused by a permission check, do NOT retry or work around it; switch back to Joshua Davis, finish read-only watchlist upkeep (page searches only), log it in DAILY_LOG + one FAILURE_LEDGER row, and make sure HUMAN_QUEUE has the one [DECISION] row (don't duplicate). Mechanics learned: a 'Review changes to your Page' dialog can cover the store page on load — close it (X, top-right of the dialog) before clicking Switch; the Switch button opens a 'Switch profiles' confirm with a blue Switch button.
- 2026-10-31 (first daily run): mechanics learned — (1) on any page with a cover photo the header **Follow** button sits at about x=1068, y=438 (y≈75–115 when the page loads scrolled); always zoom after clicking to confirm it reads "Following". (2) Many store pages already follow local orgs (Lexington follows ~62) — a page that already shows "Following" is marked followed_as_page=true and does NOT count toward the day's follow cap. (3) Page search extraction that works: `[...document.querySelectorAll('div[role=feed] > div')].slice(0,3).map(d=>{const a=d.querySelector('a[href*="facebook.com"]'); ...})` returns url + name + category + address + followers in one call — batch 3 searches per browser_batch. (4) Take ledger timestamps from the Mac clock (`TZ=America/New_York date`), not from estimates. (5) WATCHLIST stores now carry `last_share` (date) so the weekly share cap can be checked without re-reading the ledger.
- 2026-11-03: shares moved back to POST mode (Publer link-posts showed a bare URL, no preview, no notification to the shared page).
- 2026-11-02: shares now auto-publish via native agent + Publer (split version); POST-mode session on 11/2 posted 5 comments, 1 share, 6 follows.
- 2026-11-01: switched the scheduled run to PREP mode (picks + drafts to QUEUE.json); posting happens in a chat Joshua starts (POST mode).
- 2026-10-31: Joshua: "start it today" — first full run fired 10/31 afternoon; Roanoke's proof comment+share count toward its 10/31 cap and its first week's share.
- 2026-10-31 (latest): added RAMP — start at 1 comment/day, 1 share/week, 5 follows/day per page; step up every 14 clean days to a lower ceiling (3/day, 3/week, 15 follows; Roanoke 4/4/20); any Facebook warning = all pages stop that day, that page drops a level.
- 2026-10-31 (later): added Local follow sweep — follow every watchlist page, every local Page found by town searches, and local people who engage with us; 20/day/page cap (Roanoke 25) with an automatic back-off on any Facebook block.
- 2026-10-31: created; proof run on Roanoke (1 comment + 1 share on Downtown Roanoke, Inc., verified on page).
