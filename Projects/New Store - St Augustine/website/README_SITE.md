# Rocket Pawn & Jewelry website — how it is built and updated

Live site: **rocketpawnjewelry.com** (rocketpawnandjewelry.com forwards to it). WordPress.com Business plan,
site id 258887816, in **Coming Soon** mode until opening.

## Source -> site
1. `website_black_red/` — design source (cloned from thevalleypawn.com in Rocket colours, logo K). Never edited by the build.
2. `prelaunch.py` — builds the publishable copy: drops the copied Valley Pawn blog and the app page, turns the
   five-store copy into one store, hides the street address / phone / hours until they are public, rewrites
   FFL, careers, contact, deals and shop pages for a store that is not open yet, cleans the search data, and pulls
   today's gold/silver price as the calculator fallback. Output: `_preview/rocket_site_prelaunch.zip`.
3. Upload the zip with the WordPress.com static import **into site 258887816** (same address, replaces all pages).
4. **WordPress strips page scripts on import.** Re-insert one Custom HTML block after the main block on each page
   listed in `post_import/` (sell-gold, sell-silver, sell-jewelry, sell-coins, hub-jewelry, hub-coins, hub-silver).
   Page ids change on every import: list pages first. Then check each calculator returns an offer.
5. Re-check: visibility still Coming Soon (a plan or domain change can flip it to public), titles, contact email.

## Going public, in order
- Lease executed -> set `address_public=True` in `prelaunch.py`, rebuild, re-import (address, map, directions return).
- Store number exists -> set `phone='(904) ...'` (call/text buttons return everywhere).
- Hours decided -> set `hours='...'`.
- Social accounts made -> fill `social={...}` (icons and the follow block return).
- Bravo confirms the app -> `app=True`.
- Opening (T-60 per blitz) -> launch the site from Coming Soon.

Calculator prices: the same 7 AM feed the Virginia stores use
(thevalleypawn.com/wp-json/wp/v2/pages?slug=spot-prices-feed), read live by the page.
