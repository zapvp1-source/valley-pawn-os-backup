# Valley Pawn Studios — STATUS

## PERMANENT-FIX-NEEDED (from preflight 2026-08-24)

1. Store-photo website mirror (Check 8, path 1) does not exist. No deal_store.json feed is reachable on thevalleypawn.com — checked WP-JSON route list (no deal routes) and three guessed static paths (all 404). No file anywhere on this Mac references deal_store.json either. This is the same class of blind assumption that zeroed out store-local content for three straight weeks (8/3, 8/10, 8/17) per the check's own history. Next interactive session should either (a) find/build the real feed endpoint on the WordPress site and document its actual URL, or (b) drop path 1 from the check entirely and rely on paths 2 (Slack) + 3 (local deal_of_week_uploads/), which both verified healthy today.
2. No PublerClient.upload_media helper script exists on this machine. Check 8's last-mile test (upload a test image, confirm a usable media URL) couldn't be run as specified — there's no local Python client for it. Verified Publer reachability via the live Chrome session instead (logged in, dashboard loads). Next interactive session should either build the helper script the check assumes, or rewrite the check to test via the Chrome/Publer UI path that's actually in use.
3. ~/.vp-studio/publer-session.json (saved cookie backup) does not exist. Today's Publer check passed on a live Chrome session, so this wasn't a blocker, but if that session ever drops, the documented auto-restore-from-file remediation has nothing to restore from. Next interactive session should export current Publer cookies to that path.
4. ~/.vp-studio/patches/MANIFEST.sha256 did not exist before this run. Generated it fresh from the three canonical patch files (publisher, reel-publisher, ai-text) since no manifest was present to verify against. Worth confirming in the next interactive session that these are in fact the intended/trusted versions of those patches.
5. Check 1's literal filename pattern (inventory_export) doesn't match anything Bravo Data Extraction actually produces (real outputs are named aged-inventory-summary, buys-from-public, end-of-month, etc.). Freshness was confirmed via aged-inventory-summary (today's date) instead. Preflight's grep pattern should be corrected so this isn't a lucky pass.
6. Check 4's literal grep pattern (graph.facebook.com/facebook-post) matches on purpose in vp-content-batch/SKILL.md — the 11 hits are all "DO NOT use this, it's retired" warnings, not live calls. File is healthy; the check's pass/fail logic is too naive to tell the difference. No patch was applied.

## Preflight run log
See output/preflight_2026-08-24.json for the full structured report.

