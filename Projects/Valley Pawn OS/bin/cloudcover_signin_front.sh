#!/bin/bash
# cloudcover_signin_front.sh — (re)open the CloudCover automation Chrome IN FRONT of the user (2026-10-16).
# Quits any hidden copy of the automation profile first, then launches it via `open -na` so macOS activates it.
PROFILE="$HOME/Library/Application Support/valleypawn/pw-cloudcover"
mkdir -p "$PROFILE"; chmod 700 "$PROFILE"
MAIN=$(pgrep -f -- "Google Chrome --user-data-dir=$PROFILE" | head -1)
if [ -n "$MAIN" ]; then
  kill -TERM "$MAIN"
  for i in $(seq 1 15); do pgrep -f -- "--user-data-dir=$PROFILE" >/dev/null || break; sleep 1; done
fi
open -na "Google Chrome" --args --user-data-dir="$PROFILE" --no-first-run --no-default-browser-check --new-window \
  "https://tune.cloudcovermusic.com/#/admin/zones" \
  "https://home.google.com/u/0/home/1-8567d747ce9987f177a24524772591264b3b242f5f709024934038bc65ce80e6/devices"
sleep 3
NEW=$(pgrep -f -- "Google Chrome --user-data-dir=$PROFILE" | head -1)
[ -n "$NEW" ] && osascript -e "tell application \"System Events\" to set frontmost of (first process whose unix id is $NEW) to true" 2>/dev/null
echo "automation Chrome opened in front (pid ${NEW:-unknown})"
