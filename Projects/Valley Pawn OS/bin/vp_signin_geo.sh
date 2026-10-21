#!/bin/bash
# vp_signin_geo.sh — the AI-search listing sign-in block (2026-10-20, expert-panel deep dive step 1).
# Opens ONE Google Chrome window IN FRONT of Joshua on the shared automation profile (pw-vp, same as
# vp_signin_front.sh) with the eight sign-ins the GEO plan needs. He signs in to each tab ONCE and
# quits the window (Cmd-Q). Nothing here types or stores a password. The directory-listing-push and
# vp-ai-search-autofix lanes reuse the saved sessions off-screen through bin/vp_browser.py.
#   1. Yext            https://www.yext.com/users/login          find + cancel the Dixie Pawn / Salem PowerListings feed
#   2. YellowPages     https://accounts.yellowpages.com/login    claim dixie-pawn-inc-452862505 + Gold-N-Pawn Roanoke
#   3. Apple Biz Conn  https://businessconnect.apple.com/        claim Harrisonburg, suite numbers
#   4. Bing Places     https://www.bingplaces.com/               stay signed in; watcher applies queued fixes
#   5. BBB             https://www.bbb.org/account/login                 answer Harrisonburg complaint, Waynesboro phone
#   6. Yelp for Biz    https://biz.yelp.com/login                claim 5 stores, merge legacy pages
#   7. Wikidata        https://www.wikidata.org/wiki/Special:CreateAccount   free account for Q140316156 enrichment
#   8. Copilot         https://copilot.microsoft.com/            finish the one-time account setup wall
# Same launch recipe as vp_signin_front.sh (quit any open copy, apply persistence prefs, open -na, bring to front).
PROFILE="$HOME/Library/Application Support/valleypawn/pw-geo"   # dedicated (2026-10-20): pw-vp is closed by the daily checks
OS_BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
PORT=9334   # not 9333 (pw-vp)
mkdir -p "$PROFILE"; chmod 700 "$PROFILE"
MAIN=$(pgrep -f -- "Google Chrome --user-data-dir=$PROFILE" | head -1)
if [ -n "$MAIN" ]; then
  kill -TERM "$MAIN"
  for i in $(seq 1 20); do pgrep -f -- "--user-data-dir=$PROFILE" >/dev/null || break; sleep 1; done
fi
/usr/bin/python3 "$OS_BIN/vp_geo_prep.py"
TABS=("https://www.yext.com/users/login" "https://accounts.yellowpages.com/login" "https://businessconnect.apple.com/" "https://www.bingplaces.com/" "https://www.bbb.org/account/login" "https://biz.yelp.com/login" "https://www.wikidata.org/wiki/Special:CreateAccount" "https://copilot.microsoft.com/")
open -na "Google Chrome" --args --user-data-dir="$PROFILE" --no-first-run --no-default-browser-check --remote-debugging-port=$PORT --window-position=80,60 --window-size=1400,950 --new-window "${TABS[@]}"
sleep 3
NEW=$(pgrep -f -- "Google Chrome --user-data-dir=$PROFILE" | head -1)
[ -n "$NEW" ] && osascript -e "tell application \"System Events\"" -e "set p to first process whose unix id is $NEW" -e "set visible of p to true" -e "set frontmost of p to true" -e "repeat with w in windows of p" -e "set position of w to {80, 60}" -e "end repeat" -e "end tell" 2>&1
echo "GEO sign-in window opened in front (pid ${NEW:-unknown}) — 8 tabs; sign in to each once, then Cmd-Q"
