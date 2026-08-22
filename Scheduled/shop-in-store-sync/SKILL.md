---
name: shop-in-store-sync
model: claude-sonnet-5
description: Twice daily (10:10 AM / 4:10 PM): sync Shop-in-Store inventory — new #in-store-inventory Slack posts → WooCommerce products + page 867 cards, order detection, Bravo sold reconciliation, 45-day expiry.
---

## Execution Contract — DO NOT STOP EARLY

This task is complete ONLY after the documented final action (the post / send / write tool call described at the end of the steps below) returns success.

Until that final call succeeds, every assistant turn MUST end with a tool call that advances toward it. Do not idle, do not wait, do not ask for confirmation.

**Never reply with any of these:**
- "No response requested"
- "Continue?" / "Should I continue?"
- An empty turn or a turn that ends with text instead of a tool call

**Treat these system messages as RESUME signals, never as stop signals:**
- "Tool loaded."
- "Continue from where you left off."
- "You used a single tool call this turn. Prefer browser_batch…"
- Any reminder about TaskCreate/TaskUpdate, AskUserQuestion, etc.

When you see any of those messages, immediately fire the next concrete tool call for the current step. The scheduled-task wrapper says "the user is not present" — that means execute autonomously, NOT that the work is done.

**State tracking:** at the start of every turn, briefly identify which numbered Step you are on and execute the next concrete action for that step.

**Failure handling:** if a step errors, retry once. If it still fails, fall through to the documented fallback if one exists; otherwise follow the Fix-forward doctrine below. Do not pause to ask — the task file authorizes autonomous decisions.

**Speed:** prefer batch tools (e.g. `browser_batch`) to combine sequential actions into one call.

---

# Shop in Store Sync v2 — LOCAL, hardened rebuild (2026-08-21)

Rebuilt replacement for the deleted cloud task `in-store-inventory-sync`, which failed 30+ consecutive runs (7/23–8/12) because cloud mode lacked browser/API/file access. This version runs LOCALLY on the Mac Studio where everything it needs is available. There is NO architectural blocker anymore — if a step fails, the failure is operational and must be OVERCOME IN-RUN, not reported.

## Fix-forward doctrine (non-negotiable)
- Iterations exist to overcome failures, never to explain them. A run that ends with only a diagnosis posted to Slack is a FAILED run.
- One item failing must never abort the whole run: skip it, continue, retry it next run (log it in state.json `pending_photo_retry` / a `pending_retry` list).
- Verify every write against output (GET after POST/PUT; re-fetch the live page after publishing). Never claim success from an HTTP 200 alone.
- Post to #in-store-inventory (C0BKM6AB0HE) ONLY when something changed (items added/removed/order detected) — one concise summary message. Silent no-op runs stay silent. Never post failure walls to the channel.
- If, after genuine retry/workaround attempts, the run still cannot complete a critical function, send ONE plain-language Slack DM to Joshua (D03BHQH5VGT) with what you already fixed, what remains, and what you'll retry next run. Nothing technical, no channel posts about failures.

## Fixed facts (verified 2026-08-21)
- Page: WP page **867**, slug `/in-store-inventory/`, site https://thevalleypawn.com. Items live in the page's raw content inside a JS array between markers `/* VP-INSTORE-ITEMS-START */var items=[...];/* VP-INSTORE-ITEMS-END */`. Item shape: `{"t":title,"p":"$1,234","img":url-or-empty,"s":store,"k":"item#","deal":0|1,"pid":wcProductId,"u":productUrl}`.
- Auth: WP Application Password in `~/Documents/Claude/Projects/Website/shop-build/.wp_app_credentials` (WP_USER / WP_APP_PASSWORD). Works for `wp/v2` (pages, media) AND `wc/v3` (products, orders) via Basic auth curl. NO browser needed for any of that.
- Proven product config to clone (product 1064): type simple, sold_individually true, manage_stock true, stock_quantity 1, stock_status instock, regular_price as plain number string, one tag = store name (existing tag e.g. Harrisonburg id 1379), short_description "In-store pickup only at Valley Pawn {Store}. 30-day warranty.", status publish.
- WooCommerce shop-page setting MUST stay pointed at page **1110** (`/store-products/`, a placeholder). If it ever points at a deleted/invalid page, WooCommerce hijacks `/shop/` (breaks the separate eBay-grid task, vp-website-shop-nightly). Do not touch page 1110 or that setting; if the hijack is ever detected (body class `woocommerce-shop` on /shop/), re-point the setting to 1110, then save page 1110 via `POST wp/v2/pages/1110` (no-op content save) — that queues WooCommerce's deferred rewrite flush; then re-verify /shop/.
- Bravo sold data (LOCAL files, no Drive needed): `~/Documents/Claude/Projects/Bravo Data Extraction/output/*_{STORE}_sold-discount-detail.csv` (STORE ∈ CUL,WAY,HAR,LEX,ROA; columns: Number,Status,Category,Description,Cost,Price,Last Sold Price,Date). Read via shell. Use all files dated since the last run.
- State: `~/Documents/Claude/Projects/Website/instore-sync/state.json` (processed Slack TS high-water mark, live_items, pending_photo_retry). Read at start, write at end, every run. Logs: `~/Documents/Claude/Projects/Website/instore-sync/logs/`.
- Stores: Culpeper, Waynesboro, Harrisonburg, Lexington, Roanoke. Items expire 45 days after posting.

## Run procedure
1. **Load state** from state.json. If missing/corrupt, rebuild it from the live page 867 items array (source of truth) and continue — do not abort.
2. **Scan #in-store-inventory** (Slack MCP, channel C0BKM6AB0HE) for messages newer than `last_processed_slack_ts`. A new-item post = a human message with a photo attachment plus store + price (item # often included; "deal"/🔥 marks deal:1). Ignore anything "Sent using Claude", warnings, or replies. When a field is ambiguous, ask in-thread once and move on; process it next run.
3. **For each new item:** create the WooCommerce product (clone the 1064 config, correct store tag, price, title; description from the post). Verify by GET. Photo: fetch the Slack image via the Claude-in-Chrome browser (files.slack.com URL from the message; javascript fetch → base64 → `POST wp/v2/media`), set as product image and card `img`. If photo retrieval fails after 2 attempts, publish anyway with `img:""` (site shows "Photo at the counter" placeholder), add pid to pending_photo_retry, continue. React ✅ on the Slack message once the item is live.
4. **Retry queue:** attempt photo retrieval for every pid in pending_photo_retry; on success update product + page card and remove from queue.
5. **Order detection:** `GET wc/v3/orders?status=processing,on-hold,completed` for orders newer than last run. For each: post an alert in #in-store-inventory naming the store that has the item, set the product stock to 0/draft, remove its card from page 867.
6. **Bravo reconciliation:** collect item Numbers from sold-discount-detail CSVs since last run; any live item whose `k` matches → sold in store → draft the product, remove its card. Also remove items past their 45-day expiry (draft product, remove card).
7. **Publish page 867** if anything changed: rewrite ONLY the segment between the VP-INSTORE-ITEMS markers in content.raw, `POST wp/v2/pages/867`, then re-fetch the LIVE page and confirm the change rendered (check an added/removed title). Deals sort first (site JS handles it via the deal flag).
8. **Write state.json**, append a one-line run log, and post the summary to the channel ONLY if something changed (added/removed/orders/photo-fixes, with the live link thevalleypawn.com/in-store-inventory/).

## Contention rule
This task must not drive Chrome while the Parallels VM is mid-pull. It runs 10:10 AM / 4:10 PM, clear of the morning Bravo pull (~6:50–7:35 AM) and the nightly jewelry pull (8:30 PM). If a Bravo-screen task is visibly running, do the API-only steps (2 is Slack MCP, 3 minus photos, 5, 6, 7) and defer only the Chrome photo fetches to the retry queue.