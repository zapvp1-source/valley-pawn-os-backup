#!/bin/bash
# gusto_signin_front.sh — (re)open the Gusto automation Chrome IN FRONT of the user (2026-10-18; copy of
# cloudcover_signin_front.sh). Dedicated profile ~/Library/Application Support/valleypawn/pw-gusto — separate
# from Joshua's everyday Chrome. Joshua signs in to Gusto ONCE (jdavis@fcfpawn.com; tick "Remember this device
# for 30 days" on the verification step), then just quits that window (Cmd-Q). Nothing here types or stores a
# password. The 10:15 native check (bin/clockin_check.py) then reuses the saved session off-screen.
PROFILE="$HOME/Library/Application Support/valleypawn/pw-gusto"
mkdir -p "$PROFILE"; chmod 700 "$PROFILE"
/usr/bin/python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/gusto_profile_prefs.py" 2>/dev/null
MAIN=$(pgrep -f -- "Google Chrome --user-data-dir=$PROFILE" | head -1)
if [ -n "$MAIN" ]; then
  kill -TERM "$MAIN"
  for i in $(seq 1 15); do pgrep -f -- "--user-data-dir=$PROFILE" >/dev/null || break; sleep 1; done
fi
open -na "Google Chrome" --args --user-data-dir="$PROFILE" --no-first-run --no-default-browser-check --new-window \
  "https://app.gusto.com/payroll_admin/time_tracking"
sleep 3
NEW=$(pgrep -f -- "Google Chrome --user-data-dir=$PROFILE" | head -1)
[ -n "$NEW" ] && osascript -e "tell application \"System Events\" to set frontmost of (first process whose unix id is $NEW) to true" 2>/dev/null
echo "Gusto automation Chrome opened in front (pid ${NEW:-unknown}) — sign in once (tick Remember this device for 30 days), then quit that window"
