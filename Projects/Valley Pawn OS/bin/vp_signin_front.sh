#!/bin/bash
# vp_signin_front.sh — THE one sign-in window for every native browser check (2026-10-19).
# Opens ONE Google Chrome window IN FRONT of the user on the single automation profile
#   ~/Library/Application Support/valleypawn/pw-vp     (separate from Joshua's everyday Chrome)
# with four tabs:
#   1. https://tune.cloudcovermusic.com/#/admin/zones      CloudCover
#   2. https://home.google.com/                            Google Home — sign in as fullcirclepawn@gmail.com (passkey OK)
#   3. https://app.gusto.com/                              Gusto — jdavis@fcfpawn.com, tick "Remember this device for 30 days"
#   4. https://app.northwestregisteredagent.com/           Northwest Registered Agent (tick "Remember me")
# Joshua signs in to each tab ONCE, then QUITS that window (Cmd-Q) — or runs bin/vp_signin_close.sh.
# Nothing here types or stores a password. The native checks (cloudcover_check.py, dress_code_check.py,
# clockin_check.py, northwest_check.py) reuse the saved sessions off-screen through bin/vp_browser.py.
#
# Before opening: quits any copy already open on the profile (the sign-in window and the scripts never share
# the profile at the same time) and applies the persistence prefs (vp_browser.py prefs) while it is closed.
#
#   vp_signin_front.sh          the real thing (4 tabs, window in front)
#   vp_signin_front.sh --test   persistence proof only: the SAME `open -na` launch, but the tabs are two
#                               cookie-setting test pages and the window is parked off-screen (no human needed)
PROFILE="$HOME/Library/Application Support/valleypawn/pw-vp"
OS_BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
mkdir -p "$PROFILE"; chmod 700 "$PROFILE"
MAIN=$(pgrep -f -- "Google Chrome --user-data-dir=$PROFILE" | head -1)
if [ -n "$MAIN" ]; then
  kill -TERM "$MAIN"
  for i in $(seq 1 20); do pgrep -f -- "--user-data-dir=$PROFILE" >/dev/null || break; sleep 1; done
fi
/usr/bin/python3 "$OS_BIN/vp_browser.py" prefs
/usr/bin/python3 "$OS_BIN/vp_browser.py" set-startup
if [ "$1" = "--test" ]; then
  open -na "Google Chrome" --args --user-data-dir="$PROFILE" --no-first-run --no-default-browser-check --new-window \
    --window-position=-2400,-2400 --window-size=1280,900 \
    "https://httpbin.org/cookies/set?vp_quit_test=1" \
    "https://postman-echo.com/cookies/set?vp_quit_test=1" \
    "https://example.com/"
  sleep 3
  NEW=$(pgrep -f -- "Google Chrome --user-data-dir=$PROFILE" | head -1)
  echo "TEST: automation Chrome opened off-screen via open -na (pid ${NEW:-unknown})"
  exit 0
fi
open -na "Google Chrome" --args --user-data-dir="$PROFILE" --no-first-run --no-default-browser-check --new-window \
  "https://tune.cloudcovermusic.com/#/admin/zones" \
  "https://home.google.com/" \
  "https://app.gusto.com/" \
  "https://app.northwestregisteredagent.com/"
sleep 3
NEW=$(pgrep -f -- "Google Chrome --user-data-dir=$PROFILE" | head -1)
[ -n "$NEW" ] && osascript -e "tell application \"System Events\" to set frontmost of (first process whose unix id is $NEW) to true" 2>/dev/null
echo "automation Chrome opened in front (pid ${NEW:-unknown}) — sign in to the 4 tabs once, then quit that window (Cmd-Q)"
