# Login Elimination Plan — Valley Pawn / Real Estate
Owner: Joshua Davis · Built 2026-10-14 · Status file for the LOGINS project (supersedes the 1Password part of LOGIN_PLAN.md)

## The evidence
- 87 scheduled tasks are switched on. 34 of them depend on a signed-in web browser on some site; 53 do not.
- In the 3 weeks since the failure ledger was restarted (9/24–10/14): 45 sign-in failures. Gusto alone caused 26.
  The rest: Google Home 6, Guesty 5, Chekkit 5, Northwest 4, Zoom 4, eBay 3, and one each for Amazon, Publer, QBO, Meta, Google (jdavis) and Cloud Cover.
- Asks in Joshua's DM since 9/10 to sign in or reconnect: Zoom (3x), Northwest RA (6x), Chekkit Facebook (5x), Gusto (3x), Google Home (2x), Bing Places, Google re-verify, DocuSign, T-Mobile.
- Root cause: Claude is not allowed to type passwords, 2FA codes or passkeys, and in unattended runs the safety classifier also blocks it from even opening a login page. So any task that needs a live website session will keep failing the moment that session expires, no matter how good the playbook is. Keep-alive tricks only delay the failure. The only durable fix is for tasks **not to need a browser session**.

## The rule from now on
1. Every recurring job gets its data from an API, a connector, or a file a native Mac agent writes. Browsers are for one-off work while Joshua is present.
2. Native agents on the Mac Studio hold the API keys (Keychain, never in files or chat). They write data to **Google Drive › Valley Pawn Data / Bald Rock Data**, and the cloud tasks read it with the Drive connector. No session can expire because there is no session.
3. Anything that still truly needs Joshua is a sign-in item. Sign-in items are batched and shown **once a month on Login Day (first Monday)**, never day by day. The only exception is a sign-in blocking money or a legal deadline within 3 days.
4. No new task may be created that depends on a signed-in website without a written API plan.

## Per-site plan (34 browser-dependent tasks)
| Site | Tasks | Fix | Joshua, once | Status |
|---|---|---|---|---|
| Gusto web | Gusto signature check (daily), Vp gusto signature chase, + fallbacks in Daily clockin / Weekly timekeeping | Retire the web use. HR e-signatures moved to DocuSign on 10/13 (no login). Timesheets and clock-ins already come from the Gusto connector. | none | Done — Joshua switched both off 10/14 |
| Zoom web | (old voicemail tasks, now off) · Preston call-load one-shot | Already on the Zoom API (Server-to-Server app "Valley Pawn Ops Agent"); native missed-call alerts run every 60 s. Zoom web sign-in is never needed. | none | Done |
| Guesty / Airbnb / VRBO | Bald Rock Monday briefing, Bald Rock 15-day contract, Bald Rock guest reviews | **Checked 10/20: the Guesty account is Guesty Lite ($324/listing/yr), which has no Developer tools / Open API — the key step is impossible on this plan.** Two paths: (a) upgrade to Guesty Pro (quote-based, Joshua's money decision) and the built `guesty_pull.py` goes live; or (b) no upgrade: booking data comes from the Airbnb/Vrbo emails that already land in jdavis Gmail (name, dates, phone, payout, cancellations, reviews — read with the Gmail connector, no login), and only guest messaging stays in the Guesty browser session, which has held 16+ days without a sign-in. Default = (b). | Decide on Pro upgrade; otherwise none | Re-plumb the 3 tasks to the Gmail rail (next) |
| GA4 / Search Console web UI | Weekly analytics summary, Vp website trend daily refresh, Vp ai visibility metrics (GA4 part) | `ga4_pull.py` / `gsc_pull.py` already exist. New `analytics_api_pull.sh` runs them daily at 5:20 AM and copies the results to Drive › Valley Pawn Data/analytics. | none. The 9/9 Google grant was still valid; a Sheets helper kept rewriting the token file's scope list, so the scripts wrongly thought access was missing and the tasks fell back to the browser. Fixed 10/14 (scopes read live from Google). Verified: GA4 443 sessions / 71 phone clicks, Search Console 218 clicks last 7 days. | Done — daily agent installed |
| Bing Places console | Vp ai search health check | Bing hours come from BrightLocal Active Sync (it pushes Google, Apple, Facebook, Bing, Yelp). Compare against the public Bing listing; no console sign-in. | none | Prompt change pending |
| TalentLMS | course uploads, reports | TalentLMS API key → native uploads/reports | Paste the API key into the Mac dialog (2 min) | Setup dialog built |
| Slack web (photos) | Sunday checklist, Monthly gun audit, Weekly returns, Staff video chase, Thursday email watchdog, Jewelry counts (fallback) | Download photos with the ops bot token (files:read) instead of the Slack web page. | Add the file permissions to the ops bot (3 min, already on the list) | Next |
| Chekkit web | Shop Us Online text, Bonus qualifiers | The Chekkit API tokens already exist for all 5 stores (leaderboard, reviews). Campaign upload stays web until Chekkit's API supports it. | Reconnect Harrisonburg Facebook once (2 min) | Partly done |
| Publer web | Follower growth, Bonus qualifiers | Publer API (vp_publer.py already in use) for follower counts | none | Next |
| Northwest RA | Daily document check | Stop logging in daily. Northwest's 2FA code makes an unattended check impossible. Replace with watching Northwest's document-arrival emails, plus a monthly Login Day look. | none for now (Joshua: working 10/14) | Left as is |
| Google Home / Cloud Cover | Daily dress-code check, Daily Cloud Cover check | Consumer Google account (fullcirclepawn@gmail.com) with passkey re-verification; no usable camera API for this camera grid. Keep on the browser, but failures go to the monthly list, not daily. Remove the 1Password Chrome extension (subscription cancelled); it's what blocks the Cloud Cover sign-in. | Remove the 1Password extension; Google Home sign-in on Login Day | Batched |
| Retail Brilliance | Training brief, session check | Magic-link only, no API yet (vendor asked 10/13). Monthly Login Day until the vendor answers. | Login Day | Waiting on vendor |
| Indeed | Preston assistant (listings) | No employer API. Long sessions; Login Day only. Move the account to jdavis@fcfpawn.com Google sign-in. | Login Day | Batched |
| Amazon Business | Monthly store allocation, supply order | Amazon keeps sessions about a year; product lookups need no sign-in. Login Day if ever signed out. | none | OK |
| VSP e-billing | Monthly gun-check fees | Joshua clicks Pay every month anyway, so any sign-in happens in that same sitting. | none | OK |
| QBO web | Eom bravo gl export (journal entry) | Conflicts with books Gate 4 (no journal entries in an open year). Flagged separately; not a login problem. | decision | Flagged |

## Login Day 0 — the one sitting that clears the backlog (~12 min, Claude drives everything up to each paste/sign-in; those parts are blocked for Claude by design)
1. TalentLMS API key: Claude opens the TalentLMS page and the Mac dialog; Joshua signs in (session was expired 10/20) and pastes the key.
2. Slack ops bot: add the file scopes, reinstall (3 min).
3. Chekkit: reconnect Harrisonburg Facebook.
4. Chrome: remove the 1Password extension.
5. Google Home (fullcirclepawn@gmail.com) and Retail Brilliance: sign in once, ticking "remember this device".
After this: Login Day is the first Monday each month, and the list should normally be empty or 1–2 items.

## Decisions made 2026-10-14
- Gusto signature check (daily) and Vp gusto signature chase: switched off by Joshua.
- Fleet guardian updated (Joshua approved): sign-in items are tagged [SIGN-IN] and shown only on Login Day (first Monday, 21:45 note), except a sign-in blocking a payment or legal deadline within 3 days. Retired sites (Gusto web, Zoom web, Bing Places, GA4/Search Console web) are never queued again.
- Northwest Registered Agent: Joshua reports it is working; left as is.

## Files
- Valley Pawn OS/bin: guesty_pull.py, guesty_pull.sh, api_keys_setup.sh, analytics_api_pull.sh, login_wall_audit.py
- Valley Pawn OS/fleet: com.valleypawn.guesty-pull.plist, com.valleypawn.analytics-api-pull.plist, LOGIN_WALL_AUDIT.json
