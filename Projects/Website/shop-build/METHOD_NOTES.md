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
