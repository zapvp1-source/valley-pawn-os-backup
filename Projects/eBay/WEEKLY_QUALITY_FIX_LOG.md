
## 2026-08-03 run (ebay-weekly-quality-fix)
- Scope: listings started in last 7 days, all 5 stores.
- Counts: Culpeper 17, Waynesboro 0, Harrisonburg 0, Lexington 1, Roanoke 6 (24 total).
- Mechanical: title-stripper removed 7 intake codes (Culpeper 1, Roanoke 6); caps-fixer normalized 5 titles (Culpeper 1, Lexington 1, Roanoke 3).
- Weak-title rewrites (researched specs, applied via ebay_title_revise.py): Lexington 158128462819 (Kobalt SGY-AIR228), Roanoke 307090179556 (Vortex SPT1-M), 307090183337 (Warne 513M), 307100460137 (Maytronics Dolphin Explorer E25).
- Category fixes (via new additive script ebay_category_fix.py, state in ~/ebay_category_fix_state.json): Lexington 158128462819 Impact Wrenches -> Air Impact Wrenches; Roanoke 307100460137 Other Collectible Tools -> Pool Cleaners and Vacuums (required adding ItemSpecifics Type + Brand to pass eBay validation).
- Photos: all 24 primary photos downloaded and visually reviewed (new_listing_primaries/) - all clean, no reordering needed this week.
- Slack: individual DMs to Sandi (Culpeper), Uriah (Lexington), Benjie (Roanoke); all-clean notes to Chadd (Waynesboro) and Walker (Harrisonburg); roll-up to Preston.
- New additive files this run: ebay_new_listing_scan.py, ebay_new_listing_analyze.py, ebay_category_fix.py, new_listings_Store.json per store, analysis_report.json, new_listing_primaries folder. None of the existing scripts were modified.
- Noted overlap check: separate task ebay-title-photo-accuracy-audit covers ALL active listings for title-vs-photo content mismatches, posts to #preston-claude - different scope, no duplication with this new-listings-only run.

### Correction (same run, same day)
- The Lexington category fix (158128462819, Impact Wrenches -> Air Impact Wrenches) did NOT persist: eBay's product-catalog match for this exact item auto-reverts the category back to 168135 "Impact Wrenches" on every revision attempt (Warning message: "This product belongs to a different category, so the category has been changed"). Verified via GetItem after the revision call. Removed the false entry from ebay_category_fix_state.json. Net real category fixes this run: 1 (Roanoke Maytronics pool cleaner, confirmed still live at 181063). Sent correction DMs to Uriah and Preston.

## 2026-08-10 run (ebay-weekly-quality-fix)
- Scope: listings started in last 7 days, all 5 stores.
- Counts: Culpeper 40, Waynesboro 1, Harrisonburg 0, Lexington 1, Roanoke 13 (55 total).
- Mechanical: title-stripper removed 19 intake codes (Culpeper 4, Waynesboro 1, Harrisonburg 1, Roanoke 13); caps-fixer normalized 5 titles (Waynesboro 1, Harrisonburg 1, Roanoke 3).
- Weak-title rewrites (researched specs, applied via ebay_title_revise.py): Roanoke 307104894147 (Apple Watch Series 9 A2984 -> full spec title), 307107327128 (Snap-on MT2500 -> full spec title).
- Category fix (via ebay_category_fix.py, state ~/ebay_category_fix_state.json): Waynesboro 800471578856 Custom & Handmade -> Factory Manufactured (Case knife set, factory-made not handmade).
- Photos: all 55 primary photos downloaded and visually reviewed via contact sheets. All clean except Roanoke 307104894147 (Apple Watch) - all 7 listing photos show the watch screen stuck on a foreign-language pairing/setup prompt (no clean photo available to promote as primary); flagged to Benjie for reshoot, could not fix via reorder since every photo has the same issue.
- Slack: individual DMs to Sandi (Culpeper), Chadd (Waynesboro), Uriah (Lexington), Benjie (Roanoke); all-clean note to Walker (Harrisonburg); roll-up to Preston.
- New additive files this run: cat_fixes_20260810.json, title_fixes_20260810.json, primaries_20260810/, contact_sheets_20260810/, download_primaries_20260810.py, make_contact_sheets_20260810.py, watch_check/. None of the existing scripts were modified.

### Correction (2026-08-13, Joshua's direct request)
- Reverted 2 Waynesboro titles that had gone through the 8/10 run's mechanical title-stripper + caps-fixer pipeline, back to their true original (pre-strip) titles via `ReviseFixedPriceItem`, confirmed live via `GetMyeBaySelling`:
  - 800384735975: back to `SAMSUNG PORTABLE SSD T7 SHIELD (VAP031234)`. Joshua's reason: the title-cased version lost accuracy — this is a **new-in-box, fully tested** SSD and the caps-fixed title no longer reflected that.
  - 800471578856: back to `CASE KNIFE - W.R. CASE & SONS CUTLERY CO. CASE KNIVES (VAP031371)`. Joshua's reason: this is a specific/special Case knife set — the caps-fixer's title-casing (e.g. mangling "W.R." to "W.r.") lost the specificity that matters for this item.
  - **Known caps-fixer issue surfaced by this — FIXED same day (2026-08-14).** `ebay_caps_fixer.py`'s `KEEP` set didn't include `SSD`, and its `tc()` word-caser didn't special-case abbreviations with periods like `W.R.` — both got flattened to `Ssd` / `W.r.` on any ALL-CAPS title it touched. Patched additively (no other logic touched): added `SSD`/`HDD` to `KEEP`, and added an `ABBR` regex (`^[A-Za-z]\.([A-Za-z]\.)+$`) that keeps all-caps period-abbreviated tokens (`W.R.`, `U.S.A.`, etc.) as-is instead of title-casing them. Verified locally against both reverted titles plus 2 control cases (a fresh HDD title, an unrelated existing-behavior title) — `SAMSUNG PORTABLE SSD T7 SHIELD` -> `Samsung Portable SSD T7 Shield`, `CASE KNIFE - W.R. CASE & SONS CUTLERY CO. CASE KNIVES` -> `Case Knife - W.R. Case & Sons Cutlery Co. Case Knives`, unrelated titles unaffected. Not yet re-run against live listings — this only patches the script for the *next* `ebay-weekly-quality-fix` run; it does not retroactively fix any other already-live title the old logic may have mangled.
  - **Checked for other already-live titles hit by the same bug**: scanned all of `ebay_caps_state.json` (all stores) for "before" titles containing SSD/HDD or a period-abbreviation token — found 3 more, all Harrisonburg (800325668557, 800325674470, 800325680884, all "SANDISK EXTREME PORTABLE SSD ..."). Checked each against its live `GetMyeBaySelling` title before touching anything: 800325668557 and 800325674470 are **no longer active** (sold/ended — nothing to fix). 800325680884 is active but its item number has been **reused for a completely different product** ("WD Black P10 Game Drive 2TB Portable External HDD for Xbox") — applying the old SanDisk SSD title to it would have corrupted a live, unrelated listing. Left all 3 untouched. No other affected listings found beyond the 2 Waynesboro items already reverted.
  - Both items remain in `~/ebay_title_state.json` / `~/ebay_caps_state.json` under Waynesboro (39/24 total entries respectively, spanning many prior runs) — only these 2 specific items were touched, not a store-wide revert.

## 2026-08-21 — backlog cleanup + process fix (triggered by Joshua: "this doesn't seem to be working")
- Found: the `ebay-title-photo-accuracy-audit` task's (b)/(c) categories were "flag and wait" only, with no execution step ever closing the loop. Two identity errors had been confirmed on full-res in BOTH the 2026-08-02 and 2026-08-16 audits and were still live/wrong on 2026-08-21: Harrisonburg `800406852492` (titled "Amazon Kindle Fire Tablet", actually a Kindle e-reader) and Roanoke `298226614316` (titled "WHEEL MASTERS 6606 portable rear view mirror", box reads "Eagle Vision"). Four photo-content problems (wrong photos on the listing) were also still unresolved 3 weeks later with no store manager ever notified: Harrisonburg `385626892405` (milling bit listing, 2 unrelated photos), Harrisonburg `800112196687` (full item/photo mismatch — Playground pen kit photos on a PowerStation listing), Lexington `157840648182` and `157921257295` (NASCAR jackets, wrong-jacket photos).
- Fixed now (reversible via `ebay_title_revise.py --revert`, state in `~/ebay_toolfix_state.json`):
  - Harrisonburg `800406852492` -> "Amazon Kindle E-Reader - Tested & Powers On, Working Condition". Verified live via `getitem_detail.py`.
  - Roanoke `298226614316` -> "Eagle Vision Portable Rear-View Mirror". Verified live via `getitem_detail.py`.
- DM'd store managers directly for the photo problems (plain language, item number + what's wrong): Walker (Harrisonburg, both items), Uriah (Lexington, both jackets). Not yet confirmed fixed — no automated recheck; next weekly audit run will show if photos were swapped.
- Process fix (additive, via `mcp__scheduled-tasks__update_scheduled_task`, ran through expert-review-board first): `ebay-title-photo-accuracy-audit`'s SKILL.md now auto-applies category (b) title fixes when full-res is unambiguous (same reversible mechanism as category (a)), and auto-DMs the responsible store manager for category (c) photo problems instead of only logging it for Joshua to read. A new category (d) (genuinely ambiguous) stays flag-only. Nothing about price/quantity/photos/listing-ending changed — those remain fully manual.

## 2026-08-23 run (ebay-title-photo-accuracy-audit)
- Scope: ALL active listings, all 5 stores (Culpeper 304, Waynesboro 39, Harrisonburg 35, Lexington 27, Roanoke 106 = 511 total).
- Thumbnail screen: 87 contact sheets built, 36 candidate mismatches flagged by per-store subagents.
- Full-res verification: 18 of 36 were REJECTED as thumbnail misreads (lighting/angle/packaging artifacts, not real issues) after full-res + getitem_detail.py check.
- CONFIRMED and auto-fixed via ebay_title_revise.py --apply (reversible, state in ~/ebay_toolfix_state.json): 13 title changes attempted, 12 succeeded, 1 failed (Roanoke 307000372642 Apple Watch — eBay returned "item cannot be listed or modified", retried once, same result; needs manual look, not fixed).
  - Culpeper: 397528400544 (heater, +remote), 397531548727 (PS4 Pro, +2 controllers), 398106381642 (Assassin's Creed Unity, +Limited Edition), 398140133321 (Oddworld Soulstorm, +steelbook/collectible), 398204785291 (currency lot, Coin->Notes).
  - Waynesboro: 800321499390 (Sony ZV-E10 — re-corrected White->Black; all 10 full-res photos unambiguously show a black body, contradicting the White/L-kit MPN-based fix applied during last night's 8/22 incident. Flagging this one for Joshua's awareness given it's the second live change to the same item in 24 hours.)
  - Harrisonburg: 800232060996 (Switch OLED, +dock/grip/case), 800406845611 (identified as Boulder Creek AB4-TR acoustic preamp, was untitled), 800384051061 (Wii console, +remotes/sensor bar/cables/Wii Sports).
  - Roanoke: 298565157505 (Lenovo laptop, +charger), 307077675069 (Craftsman saw — completed a truncated live title, +battery/charger), 306926372024 (DeWalt drill — corrected model DCD793->DCD708 per the tool's own engraved label, confirmed on full-res photo).
  - Roanoke 307000372642 (Apple Watch, +charger): FAILED, eBay rejected the revision twice. Left as-is, needs manual check next run or by Joshua.
- CONFIRMED category (c) photo-content problems — DM'd store manager directly (plain language, item + what's wrong), no title/price/photo touched by this run:
  - Culpeper -> Sandi: 395523114047 (Trifari bracelet — unrelated gold rope bracelet photo mixed in).
  - Harrisonburg -> Walker (RE-NOTIFY, both first flagged 8/21, still wrong on this 8/23 recheck — going on 2 weeks unresolved): 800112196687 (PowerStation listing still has Playground pen-kit photos), 385626892405 (milling bit listing still has fan-blade/bearing photos).
  - Lexington -> Uriah (RE-NOTIFY): 157840648182 (Jeff Gordon jacket — still has Haas/GMAC/Bosch jacket photo mixed in). GOOD NEWS: 157921257295 (Earnhardt jacket), also flagged 8/21, checked out fine this run on full-res (orange photo was the jacket's own satin lining, not a wrong garment) — resolved, no further action.
  - Roanoke -> Benjie: 306926372024 (DeWalt drill — separate from the title fix above, one photo shows an unrelated "Atomic"-branded tool).
- CONFIRMED category (d) genuinely ambiguous, flag-only, no action: Harrisonburg 800055373631 (PS3 CECH-4001B/80GB — body style matches Super Slim family but no full-res photo shows a legible capacity sticker; Super Slim historically shipped 12GB/500GB not 80GB, so the capacity claim is plausible-but-unconfirmed either way).
- Two items previously flagged 8/02 and 8/16 and fixed 8/21 (Harrisonburg Kindle 800406852492, Roanoke mirror 298226614316) were rechecked this run and confirmed still holding correctly — no regression.
- Report DM'd to Joshua only (U03BB52MDSA), not posted to any team channel.

## 2026-09-04 run (ebay-title-photo-accuracy-audit)
- Scope: ALL active listings, all 5 stores (Culpeper 266, Waynesboro 37, Harrisonburg 31, Lexington 26, Roanoke 93 = 453 total).
- Thumbnail screen: 79 contact sheets built, 17 candidate mismatches flagged by per-store subagents.
- Full-res verification: 8 of 17 REJECTED as thumbnail misreads (PSP lot/case counts correct, Zelda cartridge label matched exactly, Blink 5-camera box confirmed, iPad triple-camera corner misread as iPhone, Sig Sauer KILO3000BDX confirmed genuine 2-barrel binocular with BDX box, laptop packaging didn't contradict Used status).
- CONFIRMED and auto-fixed via ebay_title_revise.py --apply (reversible, state in ~/ebay_toolfix_state.json):
  - Waynesboro 800548737480 (Sony a7 III body, +Battery & Charger)
  - Roanoke 306998407053 (MacBook Pro A1278, +Charger)
  - Waynesboro 800508952161 (McFarlane Batman: dropped incorrect "Red" from "Red Platinum Edition" - box only says Platinum Edition)
  - Harrisonburg 800396466895 (brand was wrong - box is Monster Jam not Mattel/Hot Wheels; also fixed "Tack"->"Take")
  - Harrisonburg 800396469929 (box reads "Mega Garage" not "Mega City Track Set")
- CONFIRMED category (c) photo-content problem - DM'd store manager: Harrisonburg 385626892405 (Putnam End Milling Bit) -> Walker, RE-NOTIFY 3rd time (first flagged 8/21, again 8/23, still has fan-blade + bearing/washer photos mixed in as of this run).
- CONFIRMED category (d) genuinely ambiguous, flag-only: Culpeper 398023637276 (Cabelas Nature Lot of 5 PSP Game - box art for 6 titles incl. non-nature Poker/fishing games shown but only 5 discs pictured, can't confirm actual lot contents); Lexington 157975837256 (Star Wars 2000pc puzzle New Sealed claim - no shrink wrap visible in photos but inconclusive).
- Report DM'd to Joshua only (U03BB52MDSA), not posted to any team channel.

## 2026-09-06 run (ebay-title-photo-accuracy-audit)
- Scope: ALL active listings, all 5 stores (Culpeper 266, Waynesboro 36, Harrisonburg 32, Lexington 27, Roanoke 97 = 458 total).
- Thumbnail screen: 79 contact sheets built, 17 candidate mismatches flagged by per-store subagents.
- Full-res verification: 6 of 17 REJECTED as thumbnail misreads: Waynesboro 800335233860 (Zelda cart shell color is a normal authentic GBC translucent shell, label genuine); Roanoke 298312214008 (PS4 console color cast from red velvet backdrop lighting, same console both angles, not two units); Lexington 157921257295 (Dale Earnhardt jacket "different jacket" photo was actually the Jeff Hamilton brand tag/collar embroidery, previously resolved 8/23, confirmed still fine); Roanoke 306861872975 (Judith Ripka necklace "different pendant" photo was the reverse/back of the same pendant, hallmark stamp confirms); plus 2 items where the accessory/spec claim couldn't be confirmed either way on full-res (left titles untouched).
- CONFIRMED and auto-fixed via ebay_title_revise.py --apply (reversible, state in ~/ebay_toolfix_state.json), all verified live via getitem_detail.py:
  - Harrisonburg: 800616885259 (Sony PS4 Pro, +Controller), 800123750148 (Novation Launchpad Pro, +Case), 800112196687 (case reads "Playground" not "PowerStation 2" -- brand corrected).
  - Lexington: 157975512781 (Bulova watch, +Box), 157488036886 (Philip Stein watch, +Box & Papers), 158260878900 (Samsung Tab S9+, +S Pen).
  - Roanoke: 307077672852 (Buck 498 knife, +Gut Hook tool), 306413806292 (Uncle Henry Schrade knife, +Bonus Care Kit -- left "3-Blade" claim untouched, couldn't confirm blade count on the 2 available photos).
- CONFIRMED category (c) photo-content problems -- DM'd store manager directly, no title/price/photo touched by this run:
  - Culpeper -> Sandi: 398162170503 (Starborn Creations pendant -- a completely different scrollwork/tree-design pendant photo mixed in, confirmed against the correct pelican/starfish/shell pendant in photo 0).
  - Harrisonburg -> Walker (RE-NOTIFY, 4th consecutive week unresolved -- first flagged 8/21, again 8/23, again 9/04, still wrong 9/06): 385626892405 (Putnam End Milling Bit -- photos 4-5 are a fan blade and a bearing/washer, confirmed on full-res again).
  - Lexington -> Uriah (RE-NOTIFY -- first flagged 8/21, again 8/23, still wrong 9/06): 157840648182 (Jeff Gordon DuPont jacket -- photos 2-3 show a navy sleeve with GMAC/HAAS/Bosch Spark Plugs patches, a different (Stewart-Haas) team jacket, confirmed on full-res).
  - Roanoke -> Benjie (RE-NOTIFY -- first flagged 8/10 as a reshoot request, ~4 weeks unresolved): 307104894147 (Apple Watch Series 9 -- every photo still shows the watch stuck on a foreign-language pairing/setup screen, no clean product photo exists to promote as primary).
  - Roanoke -> Benjie (new this week): 307164619925 (Milwaukee 2236-20 Clamp Meter -- photos 4-5 are unambiguously Klein Tools clamp meter packaging, a different brand/product, confirmed on full-res).
- No category (d) genuinely ambiguous items this run.
- Regression check: two items fixed in prior runs (Harrisonburg Kindle 800406852492, Roanoke mirror 298226614316) rechecked via getitem_detail.py -- both still holding correctly.
- Carryover check: Roanoke 307000372642 (Apple Watch, rejected revision from 8/23 run) is no longer in the active listing pull -- getitem_detail.py confirms ListingStatus: Completed, ended 2026-09-04. Self-resolved, no action needed.
- Report DM'd to Joshua only (U03BB52MDSA), not posted to any team channel.

## 2026-09-07 run (ebay-weekly-quality-fix)
- Scope: listings started in last 7 days, all 5 stores.
- Counts: Culpeper 7, Waynesboro 0, Harrisonburg 1, Lexington 1, Roanoke 15 (24 total).
- Mechanical (title-stripper + caps-fixer --apply): Roanoke -- 15 intake codes stripped, 1 ALL-CAPS title normalized (Milwaukee Tools 2236-20). No changes needed at Culpeper, Waynesboro, Harrisonburg, Lexington.
- Weak-title rewrite (researched specs via web search, applied via ebay_title_revise.py --apply, state ~/ebay_toolfix_state.json): Roanoke 307164619925 "Milwaukee Tools 2236-20" -> "Milwaukee 2236-20 True-RMS Clamp Meter HVAC/R 600A AC/DC Tool Only" (confirmed against package photo -- model, 600A rating, HVAC/R use all match).
- Category fix attempted (ebay_category_fix.py): Roanoke 298636228849 Milwaukee M12 REDLITHIUM CP2.5 battery, Battery Chargers -> Power Tool Batteries (per Taxonomy API suggestion). FAILED -- eBay requires the "Battery Technology" item specific before allowing this category, which the script doesn't set. Left as-is, flagged to Benjie for manual fix.
- Photos: all 24 primary photos downloaded and visually reviewed. 23 clean (whole-item shots, no intake/webcam stills or wrong close-ups). 1 problem: Lexington 158260878900 (Samsung Galaxy Tab S9+) has a phone-settings-menu screenshot as the primary photo instead of the tablet itself. A clean back-of-tablet photo (with S Pen) already exists in the listing at position 3 -- attempted to reorder it to primary via ebay_photo_reorder.py --apply, but eBay rejected the revision ("You can only add pictures at this time"). Flagged to Uriah to swap manually or reshoot.
- Slack: individual DMs to Sandi (Culpeper, all clean), Chadd (Waynesboro, no new listings), Walker (Harrisonburg, all clean), Uriah (Lexington, photo-order issue flagged), Benjie (Roanoke, fixes summarized + category flag); roll-up to Preston.
- New additive files this run: new_listings_20260907/ (per-store scan), analysis_report.json (refreshed), title_fixes_20260907.json, cat_fixes_20260907.json, photo_reorder_20260907.json, primaries_20260907/ (downloaded primary photos + Lexington alt-angle photos for review). None of the existing scripts were modified.
