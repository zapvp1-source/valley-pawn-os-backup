---
name: vp-website-shop-nightly
description: Publish & refresh thevalleypawn.com/shop/ — pulls all 5 stores' live eBay listings, filters weapons-adjacent, renders a searchable buy-now grid, updates the /shop/ page marker block, posts to #website. Additive; never touches /retail/ or vp-website-deals-weekly.
---

You are refreshing Valley Pawn's online storefront at https://thevalleypawn.com/shop/. This is an ADDITIVE task: NEVER modify the /retail/ page, the vp-website-deals-weekly task, or any other existing task/report. Only create/update the /shop/ page.

GOAL: Build one cohesive, searchable "Shop Valley Pawn" page that shows live inventory from all 5 stores' public eBay listings, where each item's "Buy Now" links to that item's eBay listing (real checkout, no double-sell). Then publish it to the /shop/ page and post a summary to Slack.

STEP 1 — Pull live inventory from all 5 stores (public eBay seller search; NO login needed).
Use the Claude in Chrome browser tools. For each store username below, navigate to:
  https://www.ebay.com/sch/i.html?_ssn=<USERNAME>&_ipg=240&_sop=10
Stores (name -> username):
  Culpeper -> valley_pawn_culpeper
  Waynesboro -> valley_pawn_waynesboro
  Harrisonburg -> valley_pawn_harrisonburg
  Lexington -> valley_pawn_lexington
  Roanoke -> valley_pawn_roanoke
After each page loads, run this layout-agnostic extractor via javascript_tool and collect the returned array (each element is [title, price, itemUrl, imageUrl]):
  (function(){var seen=new Set(),items=[];document.querySelectorAll('a[href*="/itm/"]').forEach(function(a){var m=a.href.match(/itm\/(\d+)/);var itm=m&&m[1];if(!itm||seen.has(itm))return;var box=a;for(var i=0;i<7&&box;i++){if(box.querySelector&&box.querySelector('img')&&/\$[\d,]/.test(box.textContent))break;box=box.parentElement;}if(!box)return;var img=box.querySelector('img');var isrc=img?(img.getAttribute('src')||img.getAttribute('data-src')||img.currentSrc||''):'';var pe=[].slice.call(box.querySelectorAll('span,div')).find(function(e){return /^\$[\d,]+\.?\d*$/.test(e.textContent.trim())});var p=pe?pe.textContent.trim():'';var t=(a.getAttribute('aria-label')||a.textContent||'').trim();if(!t){var h=box.querySelector('[role=heading],h3');t=h?h.textContent.trim():'';}t=t.replace(/\s*Opens in a new window or tab\s*/i,'').replace(/\s+/g,' ').trim();if(t&&p&&isrc&&!/Shop on eBay/i.test(t)){seen.add(itm);items.push([t,p,'https://www.ebay.com/itm/'+itm,isrc]);}});return JSON.stringify(items);})()
Use _ipg=240 to get the full inventory per store (there may be ~200+ at Culpeper). If a store shows more than 240, that's fine — cap at 240 per store.

STEP 2 — Assemble items.json.
Build a JSON object of the form {"colors":{...},"items":[{"t":title,"p":price,"u":itemUrl,"img":imageUrl,"s":storeName}, ...]} merging all 5 stores (add the store name to each item). Use exactly these colors:
  {"Culpeper":"#0099DD","Waynesboro":"#2D1A5E","Harrisonburg":"#E07A5F","Lexington":"#3DB8E8","Roanoke":"#2A9D8F"}
Write this to /Users/joshuadavis/Documents/Claude/Projects/Website/shop-build/items.json (overwrite the seed).

STEP 3 — Generate the WordPress-safe block.
Run: python3 /Users/joshuadavis/Documents/Claude/Projects/Website/shop-build/generate_shop_block.py
This reads items.json and writes /Users/joshuadavis/Documents/Claude/Projects/Website/shop-build/shop-block.html — an embeddable block delimited by <!-- VP-SHOP-START --> and <!-- VP-SHOP-END -->. The generator already: excludes weapons-adjacent items (gun/rifle/pistol/firearm/ammo/scope/optic/tactical/holster/knife/blade/etc.), renders STATIC cards (so inventory shows even if scripts are stripped) with store badges + Buy Now links, and layers on search/store-filter/price-sort. Read the resulting shop-block.html.

STEP 4 — Publish to the /shop/ page.
Use the WordPress.com connector (the same one that maintains the /retail/ page) for thevalleypawn.com:
  - If a Page with slug "shop" does NOT exist: create a published Page titled "Shop" (slug "shop") whose entire content is the shop-block.html content.
  - If it exists: replace everything between <!-- VP-SHOP-START --> and <!-- VP-SHOP-END --> (inclusive) with the new block; if those markers are absent, replace the whole page content with the new block. Keep the page published.
If the WordPress.com connector cannot create/update the page, fall back to Chrome (wordpress.com admin for thevalleypawn.com, logged in via saved passwords — never ask Joshua to log in): create/edit the "Shop" page, add a single Custom HTML block containing shop-block.html, and Publish/Update.
Do not alter the site nav automatically; note in the Slack post that /shop/ is live and can be added to the menu.

STEP 5 — Post a summary to Slack channel #website (channel ID C0ASE9C0GQ0):
  ":shopping_trolley: *Shop page refreshed* — thevalleypawn.com/shop/" then per-store item counts (Culpeper, Waynesboro, Harrisonburg, Lexington, Roanoke), the total count, and how many weapons-adjacent items were excluded. Include the link https://thevalleypawn.com/shop/.
On ANY failure (extraction, publish, etc.): do NOT post a success message; instead DM Joshua on Slack (user U03BB52MDSA) with a short description of what failed and at which step.

Notes: The public eBay seller-search pages require no login. Keep everything additive. Prefer the MCP connectors (WordPress.com, Slack) over browser automation where available.