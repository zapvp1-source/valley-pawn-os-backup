---
name: roanoke-culpeper-hours-listing-check-oneshot-20261005
description: One-time Mon 10/5 check that Bing, Apple, Yelp, Google show the new Culpeper/Roanoke hours; DM Joshua one line only if something is still wrong.
model: claude-sonnet-5
---

One-time verification for Valley Pawn (Full Circle Finance Inc). Load skills enterprise-map, valley-pawn-context, vp-operating-rules, directory-listing-push first.

Background: on 2026-10-01 Joshua set Roanoke (2362 Peters Creek Road, Suite C, Roanoke VA 24017) to open Wednesdays, and set the rule that 6-day stores close 5 PM Saturday. Canonical hours for BOTH Culpeper (571 James Madison Highway, Culpeper VA) and Roanoke: Mon-Fri 10:00 AM-6:00 PM, Sat 10:00 AM-5:00 PM, Sun closed. Changes were pushed through BrightLocal Active Sync and directly on Google/Facebook. As of 10/2: Google correct; Apple and Yelp showed Wed open but Sat still 6 PM (propagating); Bing showed Roanoke Wed CLOSED and Sat 6 PM (BrightLocal's 10/1 Bing hours push failed; Bing Places direct login is not available — jdavis@fcfpawn.com and fullcirclepawn@gmail.com both fail).

Do (read-only, public pages via Claude in Chrome, own new tab, close it after):
1. Google Maps: https://www.google.com/maps/search/?api=1&query=Valley+Pawn+Roanoke+VA and ...Culpeper+VA — expand hours.
2. Apple (via https://duckduckgo.com/?q=Valley+Pawn+<city>+VA&iaxm=maps) — expand hours.
3. Bing Maps: https://www.bing.com/maps?q=Valley+Pawn+<street>+<city>+VA — click "More hours".
4. Yelp: https://www.yelp.com/biz/valley-pawn-roanoke-2 and the Culpeper Valley Pawn Yelp page — Location & Hours.
Record each store x platform: Wed and Sat hours.

If everything matches canonical: write a one-line result to the CHANGELOG (/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/CHANGELOG.md, new dated section at top) and update the 2026-10-01 BrightLocal row in Life OS/OPEN_ITEMS_REGISTER.md to note it's verified. Send nothing to Slack.
If anything is still wrong: log it the same way, and if Bing is still wrong and Joshua is NOT at the Mac, do not touch BrightLocal. Send ONE plain Slack DM to Joshua (user U03BB52MDSA / channel D03BHQH5VGT), no jargon, e.g. "Bing still shows Roanoke closed Wednesdays. Need 2 minutes with you in BrightLocal to force it." Never post to any team channel. Never change listings in this run.