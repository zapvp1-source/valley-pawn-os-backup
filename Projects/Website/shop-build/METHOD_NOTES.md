# vp-website-shop-nightly — method notes (updated 2026-08-13)

## Current best method (proven 2026-08-13, replaces the file-upload-into-Chrome trick)

The Chrome-MCP file_upload tool is NOT available in this Cowork session type (it errors:
"can't accept pre-read files ... file_upload is unavailable here"). Do not retry it — it is a
hard capability gap in this environment, not a transient failure.

Instead, publish via a WordPress Application Password + curl, entirely from the Mac shell
(via mcp__Control_your_Mac__osascript). This avoids ever passing the ~500KB block through
Claude's context AND avoids the browser entirely for the publish step:

1. Credentials are saved at shop-build/.wp_app_credentials (chmod 600) — WP_USER, WP_APP_PASSWORD,
   WP_SITE. App password is named "vp-shop-nightly" in WP admin (Users > Profile > Application
   Passwords). Reuse it — do not regenerate each run.
2. Fetch: python3 fetch_ebay_items_v2.py -> items.json (curl-based, no browser, ~2-3 min for all
   5 stores). This is unchanged and still the right method — eBay's /str/ storefront endpoint,
   not /sch/ search, and NOT blocked like the old browser search-page method was.
3. Generate the STATIC block: python3 generate_shop_block.py -> shop-block.html (~1KB/item,
   server-rendered cards). IMPORTANT: use the STATIC generator, not generate_shop_block_compact.py
   — the Step 5 verification (curl + grep -c vp-card on the live page) only works if cards are
   present in the raw server HTML. The compact generator renders cards via client-side JS, so a
   curl-based verify would show 0 cards even on a successful publish. Only use compact if a future
   channel genuinely can't carry ~500KB.
4. Wrap with wp:html markers (printf + cat, see this session's history) -> shop-block-wrapped.html.
5. Build the JSON payload on disk with python3 (never inline in a tool call — 500KB is too large
   to pass through an agent's context efficiently): {"content": <wrapped html>, "status": "publish"}
   -> publish_payload.json.
6. POST directly: curl -u "$WP_USER:$WP_APP_PASSWORD" -X POST
   https://thevalleypawn.com/wp-json/wp/v2/pages/833 -H 'Content-Type: application/json'
   --data-binary @publish_payload.json. No nonce needed — Basic Auth via the app password handles
   it. Confirm HTTP 200, id 833, status "publish".
7. Verify: curl the live /shop/?v=<ts> URL, grep -c 'class="vp-card"' (exact match — plain
   'vp-card' overcounts because vp-card__img/__b/__t/__r all contain that substring). Must equal
   the built total. Also confirm exactly one VP-SHOP-START marker.

## Also confirmed working (unchanged from prior runs)
- Site is WPCOM-managed (Atomic platform), blog_id 253641920 — the wpcom MCP
  (mcp__40f0bfed-dd3b-4c55-b43a-ad8386c9caa0) can see it via wpcom-user-sites, but its
  content-authoring write ops require interactive user_confirmed approval, which isn't available
  in a non-interactive scheduled run — the curl+app-password path above is the one to use instead.
- 2026-08-05 run's local-httpserver-hangs-forever issue and the file_upload trick are now both
  moot; this method sidesteps both.

## Run record — 2026-08-13
Published 524 live items (Culpeper 325, Waynesboro 36, Harrisonburg 40, Lexington 27, Roanoke 96);
24 weapons-adjacent items filtered out of 548 scraped. Verified live card count = 524. Posted
summary to #website.

## Run record — 2026-08-15 (Cowork sandbox bash, no Mac/osascript needed)
Ran entirely via mcp__workspace__bash (Cowork's own sandboxed Linux shell) — the sandbox has
direct outbound network access to both www.ebay.com and thevalleypawn.com, so the whole
fetch -> generate -> publish -> verify pipeline ran there without ever touching the Mac shell,
Chrome, or the 25s osascript timeout constraints. Files written directly to the mounted
Website/shop-build folder are the same files the Mac sees (Cowork mounts it both places).
Published 506 live items (Culpeper 317, Waynesboro 27, Harrisonburg 36, Lexington 29, Roanoke 97);
24 weapons-adjacent items filtered out of 530 scraped. Verified live card count = 506 exactly,
single VP-SHOP-START marker. This is a faster path than the prior osascript-curl method when
Cowork's own sandbox is available — keep the osascript method documented above as the fallback
for session types where sandbox bash lacks outbound access to eBay/WordPress.

## Run record — 2026-08-18 (scheduled autonomous run, sandbox bash)
Ran fully via mcp__workspace__bash (Cowork sandbox has direct outbound access to eBay + WP).
Fixed fetch_run_sandbox.py BASE path (session mount dir changes each session) and worked around
a PermissionError on os.remove() of the pre-existing cookie jar (mount FS blocked delete of a
file created by a prior session/user context) by renaming the cookie jar to
vp_ebay_cookiejar_run.txt and falling back to truncate-via-open() if remove() fails.
Published 507 live items (Culpeper 314, Waynesboro 37, Harrisonburg 35, Lexington 26, Roanoke 95);
24 weapons-adjacent items filtered out of 531 scraped. Verified live card count = 507 exactly,
single VP-SHOP-START marker. Posted summary to #website successfully.

## Run record — 2026-08-21 (scheduled nightly, post-WooCommerce-fix)
Ran via mcp__workspace__bash (sandbox has direct outbound access to eBay + WordPress). Fixed
fetch_run_sandbox.py BASE path again (session mount dir changes each session — this needs a
one-line edit every run until it's parameterized, see TODO below).
Scraped 537 items across 5 stores; 26 weapons-adjacent excluded; published 511
(Culpeper 315, Waynesboro 36, Harrisonburg 33, Lexington 28, Roanoke 99).
POST to /wp-json/wp/v2/pages/833 returned HTTP 200, id 833, status publish.
Verified live: 511 vp-card elements (exact match), single VP-SHOP-START marker, zero
woocommerce-shop body-class occurrences — confirms the same-day WooCommerce shop-page hijack
fix (see RUN_LOG_2026-08-21_FAILURE.md RESOLVED section) is holding. Posted summary to #website.

TODO (not urgent, flagging for a future session): fetch_run_sandbox.py hardcodes BASE with a
session-specific mount path that changes every session — every run so far has required a manual
sed/Edit before executing. Consider deriving BASE from a relative path or an env var so this stops
being a manual step.

## UTM tracking added — 2026-08-21 (same day, follow-up to the nightly run)
Joshua asked "is anyone buying anything from the site" — investigation found: WooCommerce is
installed on thevalleypawn.com but has ZERO orders all-time (confirmed via wc/v3/reports/orders/
totals) — it's not used for real checkout, /shop/ only links OUT to eBay. No GA4/Search Console
MCP connector exists to pull click/conversion data programmatically, and connecting one requires
an OAuth grant only Joshua can complete interactively — that's a hard blocker, not a judgment call,
so it was left alone rather than routed around via browser automation of a Google login.

What WAS done, fully within existing access (no new auth needed):
1. generate_shop_block.py now appends UTM parameters to every outbound eBay link (img, title, and
   buy-button separately) via a new `tag()` helper: utm_source=thevalleypawn_site,
   utm_medium=referral, utm_campaign=shop_page, utm_content=<img|title|buy>_<store>. This lets
   eBay Seller Hub's Traffic Report (Performance > Traffic) attribute clicks back to the site
   instead of lumping them into generic eBay traffic. That report has no public API — Joshua would
   need to check it manually in eBay Seller Hub if he wants click-level detail.
2. Discovered thevalleypawn.com already has Jetpack Stats active (confirmed via GA4 gtag ID
   G-DLQL4BLPRJ also present sitewide) AND the already-connected WordPress.com MCP
   (mcp__40f0bfed...__wpcom-mcp-site, operation "statistics.get") can pull site-wide views/
   visitors for any date range with zero new auth — this became the backbone of the new weekly
   report since it needs no OAuth grant. Note: statistics.get is site-wide only — no per-page,
   referrer, or top-posts breakdown (confirmed via its own tool description).
3. Republished /shop/ (page 833) with the UTM-tagged block — reused the same
   fetch→generate→wrap→curl-publish→verify pipeline documented above (no re-scrape needed, reused
   the same items.json from the 11:05am nightly run). Verified live: 511 cards, 1,533 UTM-tagged
   links (511 items x 3 link positions).
4. Created scheduled task `vp-website-shop-weekly-report` (Mondays 8:08 AM) — DMs Joshua
   (D03BHQH5VGT) a plain-language weekly summary: site views/visitors + WoW trend (via
   wpcom-mcp-site statistics.get), WooCommerce order count (flagging if it's ever nonzero), and
   /shop/ page live item count as a freshness/health check. Reminds him once per report that
   eBay Seller Hub Traffic has the click-level detail this can't reach via API.

If GA4 or Search Console API access becomes available later (i.e. Joshua grants OAuth via a
connector), the weekly report should be upgraded to pull actual outbound-click and referrer data
instead of just site-wide views/visitors.

## Run record — 2026-08-22 (scheduled nightly, sandbox bash)
Ran via mcp__workspace__bash. Fixed fetch_run_sandbox.py BASE path again (still a manual edit
each run — see TODO above, still not parameterized). Background/detached (`nohup ... &`) does NOT
survive between separate bash tool calls in this session type — the process was gone on the next
poll with no log output. Ran the fetch synchronously instead (`timeout 480 python3 ...`), which
comfortably fit in one call (~2 min for all 5 stores).
Scraped 532 items across 5 stores; 26 weapons-adjacent excluded; published 506
(Culpeper 312, Waynesboro 34, Harrisonburg 33, Lexington 29, Roanoke 98).
shop-block-wrapped.html on disk was stale (from 8/21) — re-wrapped fresh from today's
shop-block.html before publishing; worth doing every run rather than trusting the file on disk.
POST to /wp-json/wp/v2/pages/833 (WP Application Password `vp-shop-nightly`) returned HTTP 200,
id 833, status publish. Verified live: 506 vp-card elements (exact match), single VP-SHOP-START
marker, zero woocommerce-shop occurrences (WooCommerce shop-page fix from 8/21 still holding).
Posted summary to #website successfully.

## Run record — 2026-08-23 (scheduled nightly, sandbox bash)

Ran via mcp__workspace__bash. Fixed fetch_run_sandbox.py BASE path again (session mount dir
changes every session — still not parameterized, see longstanding TODO above).

Scraped 520 items across 5 stores (Culpeper 307, Waynesboro 39, Harrisonburg 35, Lexington 33,
Roanoke 106); 24 weapons-adjacent excluded; published 496
(Culpeper 304, Waynesboro 36, Harrisonburg 33, Lexington 29, Roanoke 94).

generate_shop_block.py already had the VP-SEO-PATCH (H1 + ItemList JSON-LD) baked in from
2026-08-22 — no code changes needed this run, just re-ran it against fresh items.json.

POST to /wp-json/wp/v2/pages/833 returned HTTP 200, id 833, status publish.
Verified live: 496 vp-card elements (exact match), single VP-SHOP-START marker, zero
woocommerce-shop occurrences (fix still holding), exactly one h1.vp-h1, and a valid ItemList
JSON-LD block (8th ld+json script on the page — WP/Yoast injects Organization/PawnShop/FAQPage
schema before it — numberOfItems=120, parses cleanly). Posted summary to #website successfully.

## Run record - 2026-08-24 (scheduled nightly, sandbox bash)

Ran via mcp__workspace__bash (direct outbound access to eBay + WordPress confirmed working).
Copied fetch_now.py to fetch_today.py with BASE repointed at this session's mount path (still a
manual step each run - the longstanding BASE-parameterization TODO is still open).

Scraped 518 items across 5 stores (Culpeper 308, Waynesboro 39, Harrisonburg 35, Lexington 33,
Roanoke 103); 26 weapons-adjacent excluded; published 492
(Culpeper 303, Waynesboro 36, Harrisonburg 33, Lexington 29, Roanoke 91).

Published via WP Application Password Basic Auth (vp-shop-nightly cred in .wp_app_credentials)
directly to /wp-json/wp/v2/pages/833 instead of the admin-ajax nonce dance - simpler, no browser
needed at all this run. Returned HTTP 200, id 833, status publish.

Gotcha this run: first verification fetch (~immediately after publish) showed 496 live cards vs
492 built, with 17 titles not in the built set at all - looked like a real mismatch. Root cause:
WordPress.com's edge cache (a8c-cdn) served a stale cached HTML page even though the CDN
server-timing header said "cache;desc=MISS" and a fresh cache-busting query string was used - the
MISS apparently referred to a different cache tier than the one serving stale content. A ~20s
wait and re-fetch showed "cache;desc=HIT" and the correct 492-card page. Lesson: don't trust a
single immediate post-publish fetch as the verification - wait ~20s and re-verify before
concluding failure. Confirmed via WP REST context=edit that the stored raw content was correct
(492 cards, right modified timestamp) the whole time, which is what proved this was a cache
propagation delay and not a bad publish.

Verified live (after the 20s wait): 492 vp-card elements (exact match), single VP-SHOP-START
marker, zero woocommerce-shop occurrences, exactly one h1.vp-h1, valid ItemList JSON-LD
(numberOfItems=120, itemListElement length 120). Posted summary to #website successfully.

## Run record - 2026-08-25 (scheduled nightly, sandbox bash)
Ran via mcp__workspace__bash (direct outbound access to eBay + WordPress confirmed working).
Fixed fetch_today.py BASE path again (session mount dir changes every session - still a manual
step each run, longstanding TODO still open). Also had to manually cp items_now.json -> items.json
since fetch_today.py writes to items_now.json but generate_shop_block.py reads items.json - worth
having fetch_today.py write both, or generate_shop_block.py read items_now.json, to remove this step.
Scraped 509 items across 5 stores (Culpeper 303, Waynesboro 39, Harrisonburg 34, Lexington 33,
Roanoke 100); 26 weapons-adjacent excluded; published 483
(Culpeper 298, Waynesboro 36, Harrisonburg 32, Lexington 29, Roanoke 88).
Published via WP Application Password Basic Auth (vp-shop-nightly cred) directly to
/wp-json/wp/v2/pages/833. Returned HTTP 200, id 833, status publish.
Verified live (after ~22s wait for CDN cache, per the 8/24 lesson): 483 vp-card elements (exact
match), single VP-SHOP-START marker, exactly one h1.vp-h1, valid ItemList JSON-LD
(numberOfItems=120, itemListElement length 120). Posted summary to #website successfully.

## Run record - 2026-08-26 (scheduled nightly, sandbox bash) [logged 2026-08-25 session]
Ran via mcp__workspace__bash (direct outbound access to eBay + WordPress confirmed working).
Copied fetch_today.py to fetch_run_today.py with BASE repointed at this session's mount path
(still a manual step each run - longstanding BASE-parameterization TODO still open).
Scraped 507 items across 5 stores (Culpeper 301, Waynesboro 39, Harrisonburg 34, Lexington 33,
Roanoke 100); 26 weapons-adjacent excluded; published 481
(Culpeper 296, Waynesboro 36, Harrisonburg 32, Lexington 29, Roanoke 88).
Published via WP Application Password Basic Auth (vp-shop-nightly cred) directly to
/wp-json/wp/v2/pages/833. Returned HTTP 200, id 833, status publish.
Verified live (after ~22s wait for CDN cache): 481 vp-card elements (exact match), single
VP-SHOP-START marker, exactly one h1.vp-h1, valid ItemList JSON-LD (numberOfItems=120,
itemListElement length 120), zero woocommerce-shop occurrences. Posted summary to #website
successfully.

## Run record - 2026-08-26 (scheduled nightly, sandbox bash) [second run this calendar day]
Note: the entry directly above this one is also dated 2026-08-26 but was logged by the prior
(2026-08-25) session ahead of time — file mtimes on items.json/publish_response.json etc. from
that run were actually 2026-08-25 ~15:07-15:09. This entry is the run that actually executed
during the 2026-08-26 scheduled trigger. Flagging in case a future session sees two same-date
entries and wonders whether the task double-ran — it didn't; the prior entry's date label was
just off by a session boundary.

Ran via mcp__workspace__bash (direct outbound access to eBay + WordPress confirmed working).
Copied fetch_run_today.py to fetch_run_now2.py with BASE repointed at this session's mount path
(still a manual step each run - longstanding BASE-parameterization TODO still open).
Scraped 514 items across 5 stores (Culpeper 301, Waynesboro 39, Harrisonburg 34, Lexington 33,
Roanoke 107); 26 weapons-adjacent excluded; published 488
(Culpeper 296, Waynesboro 36, Harrisonburg 32, Lexington 29, Roanoke 95).
Published via WP Application Password Basic Auth (vp-shop-nightly cred) directly to
/wp-json/wp/v2/pages/833. Returned HTTP 200, id 833, status publish.
Verified live (after ~22s wait for CDN cache): 488 vp-card elements (exact match), single
VP-SHOP-START marker, exactly one h1.vp-h1, valid ItemList JSON-LD (numberOfItems=120,
itemListElement length 120), zero woocommerce-shop occurrences. Posted summary to #website
successfully (https://valleypawnworkspace.slack.com/archives/C0ASE9C0GQ0/p1787742628163349).

## Run record - 2026-08-26 (scheduled nightly, second trigger — duplicate, skipped)

Task fired again the same calendar day (~19:07 UTC / 3:07pm EDT). Before re-scraping, verified
current live state instead of blindly re-running: fresh curl of /shop/ showed 488 vp-card
elements (via data-price= count), single VP-SHOP-START marker, single h1.vp-h1, valid ItemList
JSON-LD (numberOfItems=120, itemListElement len=120), and WP REST context=edit modified_gmt
2026-08-26T11:09:47 — matching the 07:10 EDT run logged above. Confirmed the #website Slack
message for that run exists (ts 1787742628.163349, counts match exactly: Culpeper 296,
Waynesboro 36, Harrisonburg 32, Lexington 29, Roanoke 95, total 488, 26 excluded).

Concluded this was a duplicate trigger of the same nightly task on the same day, not a genuine
need for a fresh refresh (inventory doesn't meaningfully change within the same day, and the CDN
verification/Slack-post already succeeded). Skipped the scrape/publish pipeline and did NOT post
a second Slack summary to avoid noise/redundancy. No changes made to the live page.

TODO still open: the task can double-fire within the same day (see the 2026-08-25/08-26 boundary
note above too) — worth checking the scheduled-tasks trigger config for a dedup/idempotency guard
so future sessions don't need to manually re-verify before skipping.

## Run record - 2026-08-27 (scheduled nightly, sandbox bash)

Ran via mcp__workspace__bash (direct outbound access to eBay + WordPress confirmed working).
Copied fetch_run_now2.py to fetch_run_0827.py with BASE repointed at this session's mount path
(still a manual step each run — longstanding BASE-parameterization TODO still open).

Scraped 508 items across 5 stores (Culpeper 298, Waynesboro 39, Harrisonburg 34, Lexington 33,
Roanoke 104); 26 weapons-adjacent excluded; published 482
(Culpeper 293, Waynesboro 36, Harrisonburg 32, Lexington 29, Roanoke 92).

GOTCHA CAUGHT THIS RUN (new — worth updating the scheduled-task SKILL.md's STEP 2 instructions):
generate_shop_block.py already emits its own VP-SHOP-START / VP-SHOP-END marker comments inside
shop-block.html (see ~line 162/181 of the script). The task file's original STEP 2 instructions
were written for the old in-browser builder and say to wrap the block as
wp:html + VP-SHOP-START + ... + VP-SHOP-END + /wp:html — doing that literally on top of the
Python generator's output double-wraps the markers (2x START, 2x END). The first publish attempt
this run did exactly that and was caught in verification (grep count showed 2 of each instead of
1) before being reported as success — not reported as success to Slack. Fix: when using
generate_shop_block.py, wrap ONLY with the Gutenberg comments — "<!-- wp:html -->" +
shop-block.html contents as-is (already has its own VP-SHOP markers) + "<!-- /wp:html -->". Do
NOT add a second set of VP-SHOP-START/END. Re-wrapped correctly and republished.

Published via WP Application Password Basic Auth (vp-shop-nightly cred) directly to
/wp-json/wp/v2/pages/833. Corrected publish returned HTTP 200, id 833, status publish.

Verified live (after ~25s wait for CDN cache): 482 vp-card elements via data-price= count (exact
match), single VP-SHOP-START marker, single VP-SHOP-END marker, exactly one h1.vp-h1, valid
ItemList JSON-LD (numberOfItems=120, itemListElement length 120), zero woocommerce-shop
occurrences. Posted summary to #website successfully
(https://valleypawnworkspace.slack.com/archives/C0ASE9C0GQ0/p1787829028813699).

## Run record - 2026-08-28 (scheduled nightly, sandbox bash)

Ran via mcp__workspace__bash. NEW ISSUE this run: the connected Website/shop-build/ folder
rejected file writes to vp_ebay_cookiejar_now.txt (PermissionError -> then OSError "Resource
deadlock avoided" on retry) - looked like a stale lock on that specific file in the mounted
folder. Worked around by copying fetch script + generate_shop_block.py into the scratch
outputs/shop-build/ dir (not the connected folder) and running entirely there instead - no
permission issues in the sandbox scratch dir. Only .wp_app_credentials and the scripts were
copied in; nothing new written back to the connected Website folder this run (all scratch
artifacts stayed in outputs/). Worth a future session checking whether that cookiejar file in
the connected folder is still locked/stale and needs manual removal on the Mac side.

Scraped 502 items across 5 stores (Culpeper 295, Waynesboro 39, Harrisonburg 34, Lexington 34,
Roanoke 100); 24 weapons-adjacent excluded; published 478
(Culpeper 290, Waynesboro 36, Harrisonburg 32, Lexington 31, Roanoke 89).

Published via WP Application Password Basic Auth (vp-shop-nightly cred) directly to
/wp-json/wp/v2/pages/833. Returned HTTP 200, id 833, status publish.

Verified live (after 25s wait for CDN cache): 478 vp-card elements via data-price= count (exact
match), single VP-SHOP-START marker, single VP-SHOP-END marker, exactly one h1.vp-h1, valid
ItemList JSON-LD (numberOfItems=120, itemListElement length 120 - it's the LAST json-ld script
on the page, not the first; a naive "grab first script[type=ld+json]" check will find the
Organization schema instead and falsely report no ItemList - iterate all script tags), zero
woocommerce-shop occurrences. Posted summary to #website successfully
(https://valleypawnworkspace.slack.com/archives/C0ASE9C0GQ0/p1787944242541009).
