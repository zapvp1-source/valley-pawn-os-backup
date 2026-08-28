---
name: weekly-website-health-audit
description: Monday 5:15 AM ET — full crawl-based health audit of thevalleypawn.com (tel/sms coverage, broken JSON-LD, meta descriptions, indexation, duplicate-content clusters, page weight). Auto-fixes safe reversible issues via WP REST, tracks week-over-week metrics in a history file, posts digest to #website, logs to CHANGELOG + Open Items Register for weekly/monthly summaries.
model: sonnet
---

You are running the WEEKLY WEBSITE HEALTH AUDIT for Valley Pawn's website, thevalleypawn.com. This is a recurring Monday-morning task. You have no memory of prior runs — reconstruct context from the files below before doing anything.

## 0. Context load (mandatory, do this first, silently)
- Load the `enterprise-map` skill/context if available in this environment, then `valley-pawn-context` and `vp-operating-rules`. If those skills aren't available in this execution context, at minimum read `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/CHANGELOG.md` (newest entries) and `/Users/joshuadavis/Documents/Claude/Projects/Website/AUDIT_2026-08-22/` (the original full audit + fix log this recurring task was built from) so you understand what's already been fixed and don't re-diagnose or re-fix the same things.
- Read the run history file at `/Users/joshuadavis/Documents/Claude/Projects/Website/AUDIT_2026-08-22/weekly-history.json` if it exists (it won't on the first run — create it). It's an array of one JSON object per prior run, keyed by date, with the metrics listed in step 4. Use it to compute week-over-week deltas and to avoid re-flagging things already fixed or already escalated to Joshua and still unresolved.
- Check `/Users/joshuadavis/Documents/Claude/Projects/Life OS/OPEN_ITEMS_REGISTER.md` for any open website items (search "thevalleypawn.com" / "website") before starting, so you don't duplicate an existing open item.

## 1. Crawl the live site
- Fetch `https://thevalleypawn.com/sitemap-1.xml`, extract every `<loc>` URL.
- Fetch each URL (a normal HTTP GET is fine — no browser needed) and parse: `<title>`, meta description, meta robots, canonical link, all `<script type="application/ld+json">` blocks (attempt `json.loads`/JSON.parse on each — flag any that fail to parse and quote the parse error), all `href="tel:"` / `href="sms:"` / `href="mailto:"` links, H1 count, word count, and approximate page weight (HTML + linked CSS/JS/image bytes, using a mobile user-agent).
- This mirrors the original audit in `Projects/Website/AUDIT_2026-08-22/WEBSITE_AUDIT_2026-08-22.md` — read that file once (first run only, or if the history file is missing) to see the original methodology and baseline numbers.

## 2. Auto-fix what's safe (fix-forward, per vp-operating-rules Rule 15)
The site's WP Application Password credentials are at `/Users/joshuadavis/Documents/Claude/Projects/Website/shop-build/.wp_app_credentials` (Basic Auth against `https://thevalleypawn.com/wp-json/wp/v2/...`). WPCode snippet 1135 ("Valley Pawn — Yoast SEO fields in REST API") is active and exposes `_yoast_wpseo_metadesc`, `_yoast_wpseo_title`, and the noindex/nofollow meta keys via REST — use it.

Auto-fix ONLY these categories, and ONLY when the fix is additive/reversible (every WP page keeps its full revision history automatically, so this is safe):
- A **newly broken JSON-LD block** on any page (parse error) — if the cause is an obvious, mechanical bug matching a known pattern (e.g., an array serialized as a quoted string, like the `dayOfWeek` bug fixed 2026-08-22), fix it the same way. If the cause isn't obviously mechanical, do NOT guess — flag it instead.
- A **commercial page with no meta description** — write one in the same voice as the 40 already on the site (see the file above for examples): 116–163 characters, leads with the offer, includes a call-to-action, ends in a period. Never overwrite an existing description.
- A **new indexable page** that duplicates an already-`noindex`'d utility page pattern (link-in-bio / QR pages, `/hello-world/`-style default content) — flag it for Joshua rather than auto-noindexing anything new; the original noindex list was hand-reviewed and you should not expand it autonomously.
- Do NOT touch: page body copy, pricing/loan-amount claims, the duplicate-content clusters (pawn-loan explainer, emergency-fund, selling-gold, etc. — consolidating those needs editorial judgment, not automation), the contact bar or footer template part (only touch those if you can prove via a live fetch that they've regressed — e.g., a tel: link count of 0 site-wide — and even then, only restore from the most recent WP revision, never rewrite from scratch).
- Log every auto-fix you make: what page, what changed, before/after.

## 3. Verify every fix against the LIVE page
Per vp-operating-rules Rule 12: never trust the REST API's response as proof. After any write, re-fetch the actual public URL (with a cache-busting query param) and confirm the fix is visible there before counting it as done.

## 4. Track metrics + append to history
Compute these counts (same definitions as the 2026-08-22 baseline, so trends are comparable):
- Total pages in sitemap; indexable pages (robots does not contain "noindex")
- Pages with zero tel: links
- Indexable pages missing a meta description
- Pages with broken/unparseable JSON-LD
- Pages with zero H1
- Titles over 62 characters; titles where the brand name appears twice
- Duplicate-content cluster count (pages that are near-duplicates of another live page — reuse the cluster list from the original audit as a starting point, note any NEW likely duplicates you find by title/topic similarity, but don't auto-merge them)
- Average page weight in KB across a 5-page sample (home, one location, one sell-gold city, /shop/, one blog post)
- Any 404s or 5xxs hit during the crawl

Append a new entry to `/Users/joshuadavis/Documents/Claude/Projects/Website/AUDIT_2026-08-22/weekly-history.json` (create the file with `[]` first if it doesn't exist) with: `{"date": "YYYY-MM-DD", "metrics": {...}, "auto_fixes": [...], "new_issues_found": [...], "still_open_from_baseline": [...]}`. Keep the file as a single JSON array — read, append, write back the whole array (don't shell out to `jq` if unavailable; do it in Python).

## 5. Post the weekly digest to Slack
Post to **#website** (channel ID `C0ASE9C0GQ0`). Format: a short header with the date, then week-over-week deltas for the headline metrics (e.g., "tel-less pages: 0 → 0 (steady)" or "meta descriptions missing: 34 → 31 (-3, auto-fixed)"), then a bulleted list of what was auto-fixed this run, then a short "needs a decision" section only if something new needs Joshua's judgment (a genuine business call, not a technical one — per the expert-review-board skill, technical judgment calls are yours to make and log, not to ask about). If literally nothing changed and nothing needs attention, post a short "clean run, no changes" message rather than staying silent — Joshua wants this feeding weekly/monthly summaries, so a silent success is not useful here (this task should NOT follow the "silent on success" pattern some other tasks use).

## 6. Log for the record
- Append a dated entry to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/CHANGELOG.md` (prepend near the top, after the H1, following the existing entry format — see recent entries for style) summarizing what ran and what changed. Keep it to ~5-10 lines; link to the Slack post/history file rather than repeating all detail.
- If anything was auto-fixed, or if a new item needs Joshua's business-level decision, add a row to `/Users/joshuadavis/Documents/Claude/Projects/Life OS/OPEN_ITEMS_REGISTER.md` per Rule 14. If a prior open item (like the "three different loan amounts" question from the 2026-08-22 audit) is still unresolved, don't re-add it — just note in the CHANGELOG that it's still open.

## 7. Failure handling
If the site is unreachable, if WP auth fails, or if you hit something you can't safely resolve: do NOT abandon the run. Post what you WERE able to check to #website, note what couldn't be completed and why, and follow the Failure Alert Policy v2 (one plain-language Slack DM to Joshua at `D03BHQH5VGT`, nothing technical, only if something is actually broken and needs him — not for routine "no changes" runs).

## Success criteria for this run
- `weekly-history.json` has a new entry with real numbers (not placeholders)
- Every claimed auto-fix has been verified against the live page
- A digest posted to #website (channel C0ASE9C0GQ0) every single week, clean-run or not
- CHANGELOG.md updated
- Site returns 200 on the homepage and at least 3 other spot-checked pages before you finish, with no PHP fatal/critical error strings in the response body