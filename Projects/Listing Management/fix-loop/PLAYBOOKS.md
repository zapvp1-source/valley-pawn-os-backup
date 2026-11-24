# Listing platform playbooks (self-maintained — edit with a dated note when a path changes)

## Sign-in state (probe each run)
- **Signed in, in Joshua's Chrome (2026-11-17):** Yelp for Business (biz.yelp.com) and Facebook (Joshua manages all store pages). YellowPages owner claims worked 10/20.
- *2026-11-18:* Facebook page text reads fine, but screenshots/clicks on facebook.com return "permission denied" in Claude in Chrome; BrightLocal (tools.brightlocal.com) is not allowed for Claude in Chrome at all. BBB "Continue with Google" (jdavis@fcfpawn.com) asks for the Google password.
- **Signed out — one-time Joshua sign-in needed:** Apple Business (business.apple.com — Apple Account + 2FA); BrightLocal (tools.brightlocal.com — Google SSO did not complete 11/17; alternative: authorize the BrightLocal connector once); BBB (bbb.org/account/login — try "Continue with Google" first).

## Yelp (biz.yelp.com)
- Owner edits: biz.yelp.com → location switcher (top left) → Business Information → edit the field → Save. Hours, address and categories go to Yelp review; check the public page after about 7 days.
- Duplicate or closed listing: on the public page, Suggest an edit (right column) → tick "Business Closed or Moved" → Permanently Closed, or "This is a duplicate…" → context box (**300-character limit**, use form_input) → Submit Changes → green banner "moderators will take a look".
- *Changed 2026-11-18:* Yelp has **no web support/contact form** any more. biz.yelp.com "Need Help?" = sales chat + Support Center; yelp.com/contact = FAQ article; only human channel is phone (877) 767-9357. Rung 3 for Yelp is therefore not available unattended — go to rung 4 (BrightLocal Location Manager push) instead.

## Facebook
- Navigating to a page id that redirects to another id means it is the same page (profile id vs page id). Mark the item resolved and record both ids.
- A page we admin shows "Manage Page" in the left rail. Legacy page we admin: Settings → General → Merge Pages (or Unpublish). Page we don't admin: ⋯ → Report profile → "Duplicate"/"Pretending to be a business".

## YellowPages / Thryv
- "Suggest an Edit" on the public listing (name field) goes to Thryv's data team. Owner dashboard: the name field is locked.
- Rung 3: yellowpages.com/about/contact-us → "click here" feedback modal (name, email, comments). *2026-11-18:* the modal has a **reCAPTCHA** on submit — do not attempt. thryv.com/contact-us form needs phone + a privacy-statement checkbox (don't tick unattended). Next try: a Thryv/YP support email address from jdavis@fcfpawn.com.

## BBB
- Business Portal: bbb.org/account/login (Continue with Google). Rung 3: BBB Serving Western Virginia, (540) 342-3455. Email the bureau through the profile's "Contact BBB" with the correction.

## MapQuest
- Owned by the weekly "MapQuest Dixie Pawn removal" task. Free path = listing page → "Let us know" → duplicate. Direct confirm-listing URLs give "Session Expired".

## Loc8NearMe
- Listing URLs keep the old slug: Roanoke /virginia/roanoke/gold-n-pawn/5652844/, Harrisonburg /virginia/harrisonburg/dixie-pawn-inc/5726932/. Site search ignores location; use a web search with site:loc8nearme.com.
- Fix: listing → "Suggest an Edit" (opens a popup) → tick "I'm the owner", store email (city@fcfpawn.com), message → Send Suggestion. The popup closes itself on send. Roanoke's 10/20 edit was live by 11/18.

## FFLeasy
- Claim needs a new FFLeasy account (don't create). Use ffleasy.com/contact → Department "Other" → name/phone/email/message → "Email is sent. Thank You!".

## Small directories (FFLeasy, GunNook, GunMade, MasterFFL, BlueBook, mallsinamerica, Manta, Nextdoor, ChamberofCommerce.com, Loc8NearMe)
- Look for "Claim / Is this your business? / Suggest an edit / Report" on the listing first. Otherwise use the site's contact form. Fallback: email the address in the site footer from jdavis@fcfpawn.com.
- Many sit behind Cloudflare. If a challenge blocks the page, go to the support email (rung 3) instead of retrying.

## Bing Places (added 2026-11-20)
- Public check: bing.com/maps?q=Valley+Pawn+<address> → read the hours table (javascript `document.querySelectorAll('table')`). Listings are claimed (verified badge).
- Owner edit: bingplaces.com → Sign in. Both "Continue as Joshua" (Google) and "Microsoft account" open a popup outside the Claude in Chrome tab group and do not finish → needs Joshua's one-time sign-in, or a BrightLocal push.

## pawnshopatlas.com / BaseLocal (added 2026-11-20)
- pawnshopatlas: city pages /virginia/<city>/; "Spotted an error? Let us know" = mailto contact@pawnshopatlas.com. No form.
- BaseLocal: "best of" list pages only (no business page); correction = hello@baselocal.com.

## Nextdoor (added 2026-11-21)
- All 5 store pages are claimed under one business login (Google jdavis@fcfpawn.com); edit via /page-admin/home/?profile_id=<id> (ids in CHANGELOG 11/21).
- Unclaimed duplicate/ghost: public page → "Suggest an Edit" (right column) → Operating status = Permanently closed → Submit → toast "Thanks! Your suggestion has been submitted." The ⋯ menu has no report option.

## ChamberofCommerce.com (added 2026-11-21)
- Listing → "Listing Incorrect?" opens /request-contact?help=Dispute&id=<id> — the form **requires a captcha** on submit (don't attempt). No support email is published. Claim = new account. It is a Yext publisher, so the Yext correction (LQ-003) may also clear it.

## Henry Repeating Arms dealer locator (added 2026-11-21)
- Only path: henryusa.com/contact-henry-repeating/ → Reason "Become a Henry Dealer / Current Dealer Inquiries" → Store Name + Message. Submitting **auto-subscribes the sender to the Henry newsletter**, so it needs Joshua's OK.

## CLOSO / Wheree / Buya (added 2026-11-21)
- CLOSO registry pages have no edit link; email support@closo.co.
- Wheree (*.wheree.com) sits behind Cloudflare; use a support email.
- Buya store profile (buya.com/StoreProfile/About/VALLEY-PAWN-WAYNESBORO/1557) is correct as of 11/21.

## FFLs.com (added 2026-11-23)
- FFLs.com keeps a page for every ATF license ever issued, including expired ones (marked "This FFL is Expired"). Harrisonburg's old "DIXIE PAWN INC" pages (/ffl/154660029m39381, /ffl/154660022m39381, expired 2019) are historical — never treat them as a defect. Check the active record on /directory/va/<city> (HAR = VALLEY PAWN, 1-54-165-02-7M-26284). "Claim this FFL" needs a new account.
