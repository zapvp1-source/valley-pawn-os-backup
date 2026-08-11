
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
