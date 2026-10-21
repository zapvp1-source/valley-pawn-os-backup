# Valley Pawn — Full Listing Audit, 2026-10-20 (summary; full report in Cowork project "Listing Managment Agent" → claude/LISTINGS-AUDIT-2026-10-20.md)

Big-5 live read 10/20: Google ✅ all 5 (hours, Suite C, Ste 22). Bing ✅ hours all 5; Roanoke missing Suite C; Lexington description mentions Salem.
Apple Maps ❌ OLD hours at Roanoke (Sat 10–6), Culpeper (Sat 10–6), Waynesboro (Wed closed, Sat 10–6); Roanoke no Suite C; Harrisonburg no Ste 22 + category Jewelry; descriptions mention Salem.
Yelp ❌ OLD hours at Roanoke/Culpeper (Sat 10–6) and Waynesboro (Wed closed, Sat 10–6, "West BRoad St"); Roanoke no Suite C + About typos; Harrisonburg no Ste 22 + primary category Jewelry. Yelp gold-n-pawn-roanoke now redirects to valley-pawn-roanoke-2 (name fixed).
Facebook ✅ addresses; hours set on edit forms 10/1 (CUL, ROA) and 10/15 (WAY).
ROOT CAUSE: BrightLocal Save-and-Sync pushes to Apple + Yelp (10/1, 10/15) never landed — sync silently failing. Fix directly in Yelp for Business (owner access in Chrome) + Apple Business Connect (Apple ID sign-in), then reconnect in BrightLocal.
Website: /sell-gold-culpeper/ stale copy (Mon–Sat 10–6; Roanoke closed Wed); /sell-gold-harrisonburg/ no Suite 22. Schema on /locations* correct. Google cache of /roanoke stale → re-index.
Long tail: Roanoke still Gold-N-Pawn on YP/Chamber/Nextdoor/BlueBook; Loc8NearMe says Roanoke CLOSED; MasterFFL Roanoke phone = Lexington's + publishes 844 Cypress Crossing mailing address; GunMade/MasterFFL "2362-D"/"UNIT C" + old hours; Harrisonburg Dixie Pawn on YP/Chamber/Nextdoor/Loc8; Lexington 439 E Nelson / 640 N Lee Hwy on MapQuest ×2, YP, Manta; ghost Salem (YP, GunMade) + Staunton (YP, Superpages, Manta, Yelp, Nextdoor, MerchantCircle); BBB Waynesboro phone = Lexington's, "Full Circle Finance" alt name, 282 Bald Rock Rd listed as a location; Nextdoor dup "Wayneboro"; Chamber "Wayneboro" tax-prep category.
BrightLocal not signed in (login page). Aggregators: Lexington expired 8/8.
