---
name: ebay-weekly-quality-fix
description: Weekly: review new eBay listings across all 5 Valley Pawn stores, auto-fix title/category/photo issues, and DM each manager what was fixed and why.
model: claude-sonnet-5
---

Weekly eBay NEW-LISTING quality review and AUTO-FIX for all 5 Valley Pawn stores (Roanoke, Culpeper, Harrisonburg, Lexington, Waynesboro). Goal: review every listing created in the last 7 days, FIX the quality issues yourself, then DM each store's manager what was wrong, what you fixed, and why. Do NOT ask the team to fix things — you fix them.

ACCESS / TOOLS:
- Run scripts on the Mac with the Control-your-Mac osascript tool: `do shell script "..."`. eBay's API is reachable from the Mac.
- eBay Trading API. Per-store user tokens and app creds live in ~/ebay_weekly_rankings.py (the STORES list of {name, token}; plus APP_ID, DEV_ID, CERT_ID -- see that file; never hardcode credential values in this SKILL.md).
- Helper scripts already built (idempotent, reversible):
  • ~/ebay_title_stripper.py <Store> --apply  → strips internal intake codes like (VA123456) from titles. Only changes titles that still have a code, so re-running fixes new listings. Reversible via ~/ebay_title_state.json.
  • ~/ebay_caps_fixer.py <Store> --apply  → converts ALL-CAPS titles to proper case. Reversible via ~/ebay_caps_state.json.
- eBay Taxonomy API for categories (no per-store auth needed): get an app token via client_credentials — POST https://api.ebay.com/identity/v1/oauth2/token, header Authorization: Basic base64(APP_ID:CERT_ID), body grant_type=client_credentials&scope=https://api.ebay.com/oauth/api_scope. Then GET https://api.ebay.com/commerce/taxonomy/v1/category_tree/0/get_category_suggestions?q=<title> with Bearer <app_token>.

STEPS each run:
1. For each store, pull listings created in the last 7 days (Trading API GetMyeBaySelling ActiveList; keep items whose ListingDetails/StartTime is within 7 days).
2. Run the mechanical fixes on each store: `/usr/bin/python3 ~/ebay_title_stripper.py <Store> --apply` and `/usr/bin/python3 ~/ebay_caps_fixer.py <Store> --apply` (idempotent — they only touch what still needs it, i.e. this week's new listings).
3. For each NEW listing with a weak or short title, WRITE a strong ~80-character keyword title (brand + model + key specs + condition + searchable keywords) and apply it via Trading API ReviseFixedPriceItem (<Item><ItemID>..</ItemID><Title>..</Title></Item>). For cryptic model-only titles, do a quick web search to identify the product rather than guessing. Never fabricate specs you can't confirm.
4. Check each new listing's category against the Taxonomy suggestion; if clearly wrong, correct it via ReviseFixedPriceItem PrimaryCategory. If eBay rejects the category change on an active listing, note it instead.
5. Review each new listing's PRIMARY photo: fetch photos via GetItem (PictureDetails/PictureURL) and actually look at the primary image. Flag intake/webcam stills, blurry photos, and detail close-ups used as the primary. If a better whole-item photo already exists in the listing, reorder it to be primary via ReviseFixedPriceItem. If new photos are needed (can't fix yourself), note it for the manager.
6. Tally per store: how many new listings, what was wrong, what you fixed.

THEN DM each store's manager on Slack (post to their user_id as the channel_id) a concise, friendly note: # of new listings reviewed, what issues you found, what you fixed (titles / category / photo order), anything only they can do (e.g. re-shoot a photo), and a one-line why (good titles/categories/photos drive sales). Manager Slack IDs:
  Roanoke → Benjie U0631AECK4K | Culpeper → Sandi U04C5DL5EKH | Waynesboro → Chadd U04U136MF6V | Harrisonburg → Walker U09UTFT4P7X | Lexington → Uriah U09H9ES2LKA
Also DM Preston (Operations, U03BWMEM9GR) a short roll-up across all stores. If a store had no new listings or nothing to fix, send a quick "all clean this week" note or skip it.

All title changes are reversible via the state files. Consult the ebay-context and valley-pawn-context skills for brand voice. Keep DMs brief and warm.