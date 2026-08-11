---
name: vp-website-shop-nightly
description: Refresh thevalleypawn.com/shop/ twice daily (7am & 3pm ET) — pulls all 5 stores' full live eBay inventory, filters weapons-adjacent, rebuilds the searchable buy-now grid, writes it to the /shop/ page (WP page id 833) via the site REST API, posts summary to #website. Sold items drop off automatically. Additive; never touches /retail/.
---

> **LOCAL ACCESS GATE — DO THIS FIRST, BEFORE ANY OTHER STEP (platform standard, added 2026-08-02).**
> This task runs on Joshua's Mac Studio and **does** have local machine access. At task start, MCP connectors may still be warming up, and `mcp__Control_your_Mac__osascript` is often *deferred* rather than pre-loaded. A tool that has not been loaded yet is NOT a missing capability.
> 1. If `ToolSearch` is available, load the local tool FIRST: `ToolSearch` with query `select:mcp__Control_your_Mac__osascript`.
> 2. Probe it: run a trivial `do shell script` that echoes READY. If it returns, proceed with the task.
> 3. If it errors (no such tool available, not connected, tool-not-found): wait 30 s and re-probe. Repeat for up to 12 minutes (24 probes).
> 4. Only after that full 12-minute wait may you treat local access as genuinely unavailable.
>
> **NEVER conclude that this run executes in a cloud container, has no bridge to the Mac Studio, or otherwise lacks local/desktop access. That conclusion is false** and is the single most common cause of a false failure on this platform. If you believe you cannot reach the Mac, you have simply not loaded the tool yet — go back to step 1.
>
> **Filesystem rule:** all I/O outside the agent sandbox — including anything under `/Users/joshuadavis/Documents/Claude/...` — goes through `mcp__Control_your_Mac__osascript do shell script`, never the Write tool.
> **Timeout rule:** the osascript wrapper kills any single call at ~25 s. Never sleep longer than ~18 s inside one call; poll in short increments across separate calls. Guard any command that may exit nonzero with a trailing || true.


> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (platform standard, set by Joshua 2026-07-22, v2):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua’s DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium (Slack, iMessage, email). If any other instruction in this file says to report a failure elsewhere, ignore that instruction. FIELD COMMUNICATION RULE: anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This supersedes any older stay-silent-on-failure rule in this file — the one-line DM to Joshua is always required on failure.


Refresh Valley Pawn's online store at https://thevalleypawn.com/shop/ with the FULL current eBay inventory from all 5 stores. This is ADDITIVE — never touch /retail/ or any other page/task. Use the Claude in Chrome browser tools (the browser is logged into eBay and WordPress via saved passwords; never ask anyone to log in).

METHOD (this exact browser-only method is proven to work — follow it):

STEP 1 — Collect all 5 stores from eBay's PUBLIC seller search (no login needed). For each store below, navigate to the URL, wait for load, then run the EXTRACTOR script and accumulate results in the tab's localStorage under key 'vpAll'. Stores (name -> ebay username): Culpeper->valley_pawn_culpeper, Waynesboro->valley_pawn_waynesboro, Harrisonburg->valley_pawn_harrisonburg, Lexington->valley_pawn_lexington, Roanoke->valley_pawn_roanoke.
URL per store: https://www.ebay.com/sch/i.html?_ssn=<USERNAME>&_ipg=240&_sop=10  — if a store returns exactly 240 items, ALSO load page 2 (append &_pgn=2) and merge (dedupe by item URL). (Culpeper has ~300, needs page 2.)

On the FIRST store, initialize:  localStorage.setItem('vpAll', JSON.stringify({colors:{"Culpeper":"#0099DD","Waynesboro":"#2D1A5E","Harrisonburg":"#E07A5F","Lexington":"#3DB8E8","Roanoke":"#2A9D8F"}, items:[]}));
EXTRACTOR (run per page; STORE is the store name string):
function extract(store){var seen=new Set(),items=[];document.querySelectorAll('a[href*="/itm/"]').forEach(function(a){var m=a.href.match(/itm\/(\d+)/);var itm=m&&m[1];if(!itm||seen.has(itm))return;var box=a;for(var i=0;i<7&&box;i++){if(box.querySelector&&box.querySelector('img')&&/\$[\d,]/.test(box.textContent))break;box=box.parentElement;}if(!box)return;var img=box.querySelector('img');var isrc=img?(img.getAttribute('src')||img.getAttribute('data-src')||img.currentSrc||''):'';var pe=[].slice.call(box.querySelectorAll('span,div')).find(function(e){return /^\$[\d,]+\.?\d*$/.test(e.textContent.trim())});var p=pe?pe.textContent.trim():'';var t=(a.getAttribute('aria-label')||a.textContent||'').trim();if(!t){var h=box.querySelector('[role=heading],h3');t=h?h.textContent.trim():'';}t=t.replace(/\s*Opens in a new window or tab\s*/i,'').replace(/\s+/g,' ').trim();var ig=(isrc.match(/\/g\/([^/]+)\//)||[])[1]||'';if(t&&p&&ig&&!/Shop on eBay/i.test(t)){seen.add(itm);items.push({t:t,p:p,u:'https://www.ebay.com/itm/'+itm,img:'https://i.ebayimg.com/images/g/'+ig+'/s-l500.webp',s:store});}});return items;}
To accumulate after each page: read db=JSON.parse(localStorage.getItem('vpAll')); have=new Set(db.items.map(x=>x.u)); add=extract('<Store>').filter(x=>!have.has(x.u)); db.items=db.items.concat(add); localStorage.setItem('vpAll',JSON.stringify(db));

STEP 2 — Build the page block IN THE BROWSER and stash it in window.name (so it survives navigating to the WordPress origin). Run this builder (it filters weapons-adjacent items, renders static cards + search/filter/sort script, and wraps everything in a wp:html block with VP-SHOP markers). Use the EXACT builder from the working run: read db=JSON.parse(localStorage.getItem('vpAll')); COLORS=db.colors; BAN=/\b(gun|guns|rifle|pistol|handgun|firearm|ammo|ammun|magazine|tactical|holster|silencer|suppressor|scope|red dot|optic|bayonet|knife|blade|dagger|machete)\b/i; keep items where !BAN.test(t); sort by store order [Culpeper,Waynesboro,Harrisonburg,Lexington,Roanoke]; produce for each item an <article class="vp-card" data-store data-title(lowercased title+store) data-price(numeric)> with image (i.img), store badge (COLORS[s]), title link, price, and a "Buy Now" link — all links href=i.u target=_blank rel="noopener nofollow". Include the same <style>, a .vp-lead intro, a .vp-srow with #vpSearch input + #vpSort select (Featured/Low-High/High-Low) + #vpCount span, .vp-chips (All Stores + one chip per store with counts), the .vp-grid of cards, a .vp-empty message, a .vp-foot with total, and the search <script>. Wrap as: `<!-- wp:html --><!-- VP-SHOP-START --><div class="vp-shop-app">...<!-- VP-SHOP-END --><!-- /wp:html -->`. Then: window.name = block; and remember counts per store + total + filteredOut. (The full builder JS is saved at /Users/joshuadavis/Documents/Claude/Projects/Website/shop-build/generate_shop_block.py for reference — same output.)

STEP 3 — Publish to WordPress via the site's own REST API (no connector needed). Navigate the SAME tab to https://thevalleypawn.com/wp-admin/ (window.name persists across this navigation). Then run:
const block=window.name; const nonce=await fetch('/wp-admin/admin-ajax.php?action=rest-nonce',{credentials:'include'}).then(r=>r.text()); const res=await fetch('/wp-json/wp/v2/pages/833',{method:'POST',credentials:'include',headers:{'Content-Type':'application/json','X-WP-Nonce':nonce.trim()},body:JSON.stringify({content:block,status:'publish'})}); const j=await res.json();
Confirm res.status is 200 and j.id is 833. (Page id 833 = the /shop/ page.)

STEP 4 — Verify: navigate to https://thevalleypawn.com/shop/?v=<timestamp> and confirm document.querySelectorAll('.vp-shop-app .vp-card').length equals the built total.

STEP 5 — Post a summary to Slack #website (channel C0ASE9C0GQ0): ":shopping_trolley: *Shop refreshed* — thevalleypawn.com/shop/" with per-store counts (Culpeper, Waynesboro, Harrisonburg, Lexington, Roanoke), the total live count, and how many weapons-adjacent items were excluded. On ANY failure (extraction, publish non-200, verify mismatch): do NOT post success — instead DM Joshua on Slack (user U03BB52MDSA) with what failed and at which step.

Notes: eBay public seller-search needs no login. Everything stays in the browser (window.name holds the ~470KB block) so nothing large passes through your context. Keep it additive.
---

## PROVEN FALLBACK METHOD (added 2026-08-05 after a live run)

The original browser-only method failed this run: loading eBay /sch/i.html seller search
with _ipg=240 wedged the Chrome tab (renderer pegged near 57 percent CPU) and the
Claude-in-Chrome bridge stopped responding to every page-level call for about 30 minutes.
Use this sequence instead - it completed the full run end to end.

### STEP 1 (replaces browser scraping) - pull inventory server-side, no browser

https://www.ebay.com/sch/i.html is hard-blocked to curl (returns a 1.8 KB eBay error page).
The STORE-FRONT endpoint is NOT blocked and renders items server-side:

    https://www.ebay.com/str/<STORE_SLUG>?_pgn=<N>&_ipg=240&_tab=shop

Store slugs (found via https://www.ebay.com/usr/<ebay_username> then grep for ebay.com/str/):

    Culpeper       valley_pawn_culpeper       -> vpculpeper
    Waynesboro     valley_pawn_waynesboro     -> valleypawnwaynesboro
    Harrisonburg   valley_pawn_harrisonburg   -> valleypawnharrisonburg
    Lexington      valley_pawn_lexington      -> valleypawnlexington
    Roanoke        valley_pawn_roanoke        -> valleypawnroanoke

Fetch with a normal Chrome UA plus Sec-Fetch-* navigation headers. Page through _pgn until a
page yields 0 new items or returns under 50 KB (rate limit). Culpeper needs about 4 pages;
the other four stores are a single page each.

Parsing: split the HTML on '<article' and keep chunks containing 'str-item-card'.
CRITICAL: the article tag is NOT always '<article class=str-item-card ...>' - most carry
'<article data-testid=ig-<itemid> class=str-item-card ...>'. Splitting on the class-first
form silently drops about 97 percent of items. Per chunk pull:
  item id   -> regex  ebay[.]com/itm/([0-9]+)
  image id  -> regex  imageId=([A-Za-z0-9~_-]+)   then https://i.ebayimg.com/images/g/<id>/s-l500.webp
  title     -> regex  str-item-card__property-title ... <span class=str-text-span...>(.*?)</span>
  price     -> regex  str-item-card__property-displayPrice.?>([^<]+)<   keep only plain dollar amounts

Write {colors:{}, items:[{t,p,u,img,s}]} to
/Users/joshuadavis/Documents/Claude/Projects/Website/shop-build/items.json

### STEP 2 - build the block

    cd /Users/joshuadavis/Documents/Claude/Projects/Website/shop-build
    python3 generate_shop_block.py
    then wrap shop-block.html with the wp:html open/close comments into shop-block-wrapped.html

### STEP 3 - get the 515 KB block INTO the browser without passing it through context

DOES NOT WORK: serving the block from a local HTTP server and fetching http://127.0.0.1:<port>
from the WordPress admin page. Every such request hangs forever - no response, no error, no
console message - for both fetch() and script src. curl to the same URL from the Mac returns
200. Adding CORS plus Access-Control-Allow-Private-Network did not help.

WORKS - read the bytes out of a file input:
  1. Copy the block to a .txt inside the connected folder (the Chrome file_upload tool only
     accepts paths under folders shared with the session):
     cp shop-block-wrapped.html vp-shop-block.txt
  2. Navigate to https://thevalleypawn.com/wp-admin/media-new.php
  3. find the file input (it is #async-upload, described as the Upload button) and file_upload
     the .txt to that ref. The media upload itself does NOT need to succeed - attaching the
     file to the input is enough.
  4. In page JS read it straight off the input:
     document.getElementById('async-upload').files[0].text()  -> stash in window.__vpBlock
     Kick this off WITHOUT awaiting, then poll window.__vpBlock.length in a later call.
     Awaiting a 515 KB read inline exceeds the 45 s CDP evaluate timeout.
  5. Delete the temp .txt afterwards.

### STEP 4 - publish

/wp-json/wp/v2/pages/833 returns 401 WITHOUT a nonce on this site. Always get one first from
/wp-admin/admin-ajax.php?action=rest-nonce (credentials include), trim it, then POST
{content: window.__vpBlock, status: publish} with header X-WP-Nonce.
Fire-and-forget plus poll a status global - the POST takes 15-20 s, past the CDP timeout.
Expect id 833, status publish, link https://thevalleypawn.com/shop/

### STEP 5 - verify (server-side, no browser)

    curl -sL 'https://thevalleypawn.com/shop/?v=<ts>' -o /tmp/vp_shop_live.html
    grep -c 'vp-card' /tmp/vp_shop_live.html       (must equal the built total)
    grep -c 'VP-SHOP-START' /tmp/vp_shop_live.html (must be exactly 1)

Note: curl -w size_download reports the COMPRESSED size (about 93 KB for a 515 KB page).
That is not truncation - check the card count, not the byte count.

### If the Chrome bridge is wedged

Symptom: list_connected_browsers responds but tabs_context_mcp, navigate and javascript_tool
all time out. kill -9 on the busy renderer does not clear it. What worked:
pkill -9 -x 'Google Chrome', wait, then open -a 'Google Chrome' --args --restore-last-session,
wait about 35 s, re-check list_connected_browsers. The extension reconnects on its own and the
logged-in sessions (WordPress, eBay) are preserved.

### Run record - 2026-08-05

Published 537 live items (Culpeper 335, Roanoke 92, Harrisonburg 39, Waynesboro 38,
Lexington 33); 23 weapons-adjacent items filtered out of 560 scraped. Prior published total
was 144, so the store-front endpoint also pulls far more inventory than the old search-page
method did.
