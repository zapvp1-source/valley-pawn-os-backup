---
name: vp-website-shop-weekly-report
description: Weekly DM to Joshua on thevalleypawn.com traffic + shop-page health (site views/visitors, WooCommerce order count, live item count)
model: claude-sonnet-5
---

Weekly website performance check for Full Circle Finance Inc DBA Valley Pawn's website, thevalleypawn.com. Run fully autonomously — no clarifying questions. This is a report-and-DM task; the only "write" action is the final Slack DM.

BACKGROUND: thevalleypawn.com/shop/ (WordPress page id 833) is a nightly-refreshed catalog of the company's live eBay inventory across all 5 stores (see the vp-website-shop-nightly scheduled task). Clicking any card sends the visitor OFF-SITE to eBay to complete checkout there — WooCommerce is installed on the site but is NOT used for real checkout on this page, so WooCommerce order counts are expected to stay at 0; only report on them to flag if that ever changes (a nonzero count would be a notable, surprising signal worth calling out). On 2026-08-21 all outbound eBay links on /shop/ were tagged with UTM parameters (utm_source=thevalleypawn_site, utm_medium=referral, utm_campaign=shop_page, utm_content=<img|title|buy>_<store>) so eBay Seller Hub's Traffic Report (Performance > Traffic, filtered by referring source) can show click-through activity from the site — that report is NOT available via API, so this task cannot pull it automatically; just remind Joshua once per report that it exists if he wants deeper attribution than what's below.

STEPS (do these in order; if any single step fails, skip it and continue — do not abort the whole report over one failed metric):

1. Site traffic: use the WordPress.com MCP tool `wpcom-mcp-site` (site: thevalleypawn.com) — action "execute", operation "statistics.get", params {"start_date": "<7 days ago, YYYY-MM-DD>", "end_date": "<today, YYYY-MM-DD>"}. This is a read-only call, no confirmation needed. Report views and visitors for the week, and also fetch the prior 7-day window the same way so you can show week-over-week change (e.g. "1,056 views (+12% vs prior week)").

2. WooCommerce order count: credentials are at the file that maps to `/Users/joshuadavis/Documents/Claude/Projects/Website/shop-build/.wp_app_credentials` (WP_USER, WP_APP_PASSWORD, WP_SITE — Basic Auth). In the Cowork sandbox shell, curl -u "$WP_USER:$WP_APP_PASSWORD" "$WP_SITE/wp-json/wc/v3/reports/orders/totals" — sum the "total" fields across all statuses. Expected: 0. If nonzero, flag it clearly as a real finding (someone completed a WooCommerce checkout — worth investigating what/who).

3. Shop page freshness: curl -sL "https://thevalleypawn.com/shop/?v=<timestamp>" and grep -c 'class="vp-card"' to confirm the page is live and has a reasonable item count (typically 480-560). If the page returns 0 cards or the WooCommerce "woocommerce-shop" body class appears (this happened once on 2026-08-21 — WooCommerce's shop-page setting had reverted to an invalid page and hijacked the /shop/ URL, see METHOD_NOTES.md / RUN_LOG_2026-08-21_FAILURE.md in that same folder for the fix), flag this prominently — it means the shop page is broken, not just stale.

4. Compose a short, plain-language Slack DM to Joshua (user U03BB52MDSA, channel D03BHQH5VGT) covering: this week's views/visitors + trend vs prior week, current live shop item count, WooCommerce order count (with the "expected to be 0" framing so a 0 doesn't read as bad news), and one line reminding him eBay Seller Hub's Traffic Report has the click-through detail this automated report can't reach. Keep it under 150 words, no jargon, no file paths, no error codes — this is a business update, not a technical log.

5. If Step 1 (the core traffic pull) fails entirely after one retry, do NOT post the normal summary — instead send Joshua one plain-language DM: "⚠️ Weekly website report couldn't run this week — <date>." per the standing Failure Alert Policy (technical detail stays out of the DM). Steps 2-3 failing individually should just be omitted from the report with a one-line "couldn't check X this week" rather than blocking the whole DM.

Do not post to any channel other than Joshua's DM. Do not post anything if this is clearly a duplicate run for the same week (check Slack DM history for a report already sent in the last 5 days before sending another).