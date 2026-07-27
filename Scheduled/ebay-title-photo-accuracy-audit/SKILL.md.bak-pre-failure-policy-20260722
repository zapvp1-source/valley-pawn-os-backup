---
name: ebay-title-photo-accuracy-audit
description: Weekly: audit every eBay listing's title against its photos; auto-fix clear tool-only/battery-charger errors, flag the rest for Joshua
model: claude-sonnet-4-6
---

Weekly eBay TITLE-vs-PHOTO accuracy audit across all 5 Valley Pawn stores. Goal: find listings whose TITLE does not match what the PHOTOS actually show, correct ONLY the narrow high-confidence cases, and flag everything else for Joshua/Preston. Use the osascript tool (mcp__Control_your_Mac__osascript) for all local/Mac work.

AUTH: eBay Trading API. Store tokens from ~/ebay_weekly_rankings.py (STORES). App creds from ~/.vp_secrets/ebay_credentials.py (APP_ID, DEV_ID, CERT_ID) — never hardcode. Reuse patterns in ~/Documents/Claude/Projects/eBay/ebay_photos_pull.py, ebay_title_revise.py, ebay_toolfix_apply.py.

STEP 1 — PULL: For each store run /usr/bin/python3 ~/Documents/Claude/Projects/eBay/ebay_photos_pull.py <Store> ~/Documents/Claude/Projects/eBay/<Store>_photos.json. If eBay 503/usage-limit, stop gracefully and report it was throttled (retries next week).

STEP 2 — SCREEN (thumbnails): Build review sheets with /usr/bin/python3 ~/Documents/Claude/Projects/eBay/build_audit_sheets.py <Store> (writes audit/<Store>_sheet_NN.png, 6 listings each). You MAY spawn one general-purpose subagent per store (Sonnet) to read that store's sheets and return candidate mismatches: {id, current title, issue, suggested title}. Treat these as CANDIDATES ONLY — thumbnails are unreliable for small text, model numbers, and colors.

STEP 3 — VERIFY EACH CANDIDATE ON FULL-RES (critical, this is the dial-in): For every candidate, download that listing's individual photos at full size and look closely before believing the flag. About 20% of thumbnail flags are wrong (a purple dress read as purple hair, a box back read as a second item, etc.). Only keep a flag if the full-res photo clearly confirms it.

STEP 4 — CLASSIFY the confirmed flags:
  (a) ACCESSORY-INCLUSION ADDS — title omits an accessory that is unmistakably pictured (controller, battery+charger, case/bag, cables). These are safe.
  (b) IDENTITY / SPEC / COLOR / QUANTITY errors — wrong brand, model number, magnification, karat, color, or lot count. NEVER auto-change these.
  (c) PHOTO-CONTENT problems — a wrong or mismatched photo on the listing (e.g., an iPhone photo on an iPad listing, a different item in one photo). NEVER a title fix.

STEP 5 — ACT (narrow):
  - AUTO-FIX only category (a) and the specific "Tool Only/Bare but battery AND charger clearly shown" pattern. Write {id:{store,old,new}} and apply with /usr/bin/python3 ~/Documents/Claude/Projects/eBay/ebay_title_revise.py <fixes.json> --apply (reversible; keep titles <=80 chars). 
  - Do NOT change anything in category (b) or (c).

STEP 6 — REPORT: Post to Slack #preston-claude (channel_id C0BGXSTT4TY) AND DM Joshua (U03BB52MDSA): counts audited; the (a) items auto-corrected (list them); then category (b) identity/spec/color errors as "confirmed on full-res — needs OK to correct" with current title + issue + suggested title; and category (c) photo problems as "store needs to fix the image." Skimmable. If nothing found, one line.

HARD RULES: The only mutation allowed is the narrow Step-5 title add (reversible). Never end/relist/delist, never change photos/prices, never auto-change brand/model/color/quantity/identity. Everything uncertain is flag-only. End with <run-summary> of counts.