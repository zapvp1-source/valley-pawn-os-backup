#!/bin/bash
# launchd wrapper — com.valleypawn.fleet-deck-window (KeepAlive). Keeps the Fleet Deck open on screen as its
# own chromeless app window (a dedicated Chrome instance with its own profile, so Joshua's real Chrome,
# the nightly Chrome restart and tab hygiene never touch it). If the window is closed or Chrome is killed
# (3:30 AM restart), launchd brings it back after ThrottleInterval. Nothing here changes any data.
#
# Off switch (no uninstall needed):  touch "fleet/state/fleet_deck_window_off"   — window stays closed
#                                    rm    "fleet/state/fleet_deck_window_off"   — comes back within a minute
AGENT="fleet-deck-window"
. "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 5
URL="http://127.0.0.1:8790/"
PROFILE="$HOME/.vp-studio/fleet-deck-chrome"
OFF="$OS_DIR/fleet/state/fleet_deck_window_off"
mkdir -p "$PROFILE"

if [ -f "$OFF" ]; then vlog "off switch present — window not opened"; sleep 300; exit 0; fi

# wait for the collector (up to 2 min) so the window never opens on an error page
for i in $(seq 1 24); do
  curl -s -m 2 "${URL}health" | grep -q ok && break
  sleep 5
done

CHROME="/Applications/Google Chrome.app"
if [ -d "$CHROME" ]; then
  vlog "opening Fleet Deck window (chrome app mode)"
  # -W waits for THIS instance (separate user-data-dir => separate process) to exit; then launchd relaunches us.
  open -W -n -a "$CHROME" --args --user-data-dir="$PROFILE" --app="$URL" --window-size=1720,1060 --window-position=60,40 \
       --no-first-run --no-default-browser-check --disable-session-crashed-bubble --disable-features=TranslateUI --disable-sync --hide-crash-restore-bubble
  vlog "window closed (exit $?) — launchd will reopen it"
else
  vlog "Google Chrome not found — opening in Safari"
  open -W -a Safari "$URL"
fi
sleep 20   # throttle: never spin if the window closes immediately
exit 0
