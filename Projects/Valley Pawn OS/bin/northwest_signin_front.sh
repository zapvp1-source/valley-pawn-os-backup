#!/bin/bash
# northwest_signin_front.sh — (re)open the Northwest automation Chrome IN FRONT of the user (2026-10-18; copy of
# cloudcover_signin_front.sh). Dedicated profile ~/Library/Application Support/valleypawn/pw-northwest — separate
# from Joshua's everyday Chrome. Joshua signs in to Northwest ONCE (email + password + SMS code; tick "remember
# this device" if offered), then just quits that window (Cmd-Q). Nothing here types or stores a password.
# The 08:49 native check (bin/northwest_check.py) then reuses the saved session headlessly.
PROFILE="$HOME/Library/Application Support/valleypawn/pw-northwest"
mkdir -p "$PROFILE"; chmod 700 "$PROFILE"
/usr/bin/python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/northwest_profile_prefs.py" 2>/dev/null
MAIN=$(pgrep -f -- "Google Chrome --user-data-dir=$PROFILE" | head -1)
if [ -n "$MAIN" ]; then
  kill -TERM "$MAIN"
  for i in $(seq 1 15); do pgrep -f -- "--user-data-dir=$PROFILE" >/dev/null || break; sleep 1; done
fi
open -na "Google Chrome" --args --user-data-dir="$PROFILE" --no-first-run --no-default-browser-check --new-window \
  "https://www.northwestregisteredagent.com/login"
sleep 3
NEW=$(pgrep -f -- "Google Chrome --user-data-dir=$PROFILE" | head -1)
[ -n "$NEW" ] && osascript -e "tell application \"System Events\" to set frontmost of (first process whose unix id is $NEW) to true" 2>/dev/null
echo "Northwest automation Chrome opened in front (pid ${NEW:-unknown}) — sign in once, then quit that window"
