#!/bin/bash
# cloudcover_signin.sh — ONE-TIME sign-in for the native daily-cloudcover-check (2026-10-14).
# Opens a normal, visible Google Chrome window on the DEDICATED automation profile
#   ~/Library/Application Support/valleypawn/pw-cloudcover
# (separate from Joshua's everyday Chrome) with two tabs:
#   1. CloudCover (tune.cloudcovermusic.com)  -> sign in once (tick "remember me" if offered)
#   2. Google Home (home.google.com)           -> sign in once as fullcirclepawn@gmail.com (passkey OK)
# Then just QUIT that Chrome window (Cmd-Q). The 10:25 check reuses the saved session headlessly.
# Nothing here types or stores a password — Joshua signs in himself. Re-run any time CloudCover or
# Google logs the profile out (the check writes one ledger row saying so).
PROFILE="$HOME/Library/Application Support/valleypawn/pw-cloudcover"
mkdir -p "$PROFILE"; chmod 700 "$PROFILE"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
[ -x "$CHROME" ] || { echo "Google Chrome not found at $CHROME"; exit 2; }
if pgrep -f -- "--user-data-dir=$PROFILE" >/dev/null 2>&1; then
  echo "the automation profile is already open — use that window"; exit 0
fi
nohup "$CHROME" --user-data-dir="$PROFILE" --no-first-run --no-default-browser-check --new-window \
  "https://tune.cloudcovermusic.com/#/admin/zones" \
  "https://home.google.com/u/0/home/1-8567d747ce9987f177a24524772591264b3b242f5f709024934038bc65ce80e6/devices" \
  >/dev/null 2>&1 &
echo "opened the CloudCover automation browser (pid $!) — sign in to both tabs, then quit that window"
