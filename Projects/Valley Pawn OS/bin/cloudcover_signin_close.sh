#!/bin/bash
# cloudcover_signin_close.sh — gracefully quit ONLY the CloudCover automation Chrome (dedicated profile
# ~/Library/Application Support/valleypawn/pw-cloudcover) so its saved sign-in is flushed to disk.
# Never touches Joshua's everyday Chrome. (2026-10-15)
PROFILE="$HOME/Library/Application Support/valleypawn/pw-cloudcover"
PIDS=$(pgrep -f -- "--user-data-dir=$PROFILE" | tr '\n' ' ')
[ -z "$PIDS" ] && { echo "automation browser not running"; exit 0; }
MAIN=$(pgrep -f -- "Google Chrome --user-data-dir=$PROFILE" | head -1)
[ -n "$MAIN" ] && kill -TERM "$MAIN"
for i in $(seq 1 20); do pgrep -f -- "--user-data-dir=$PROFILE" >/dev/null || break; sleep 1; done
if pgrep -f -- "--user-data-dir=$PROFILE" >/dev/null; then echo "still running after 20s"; exit 1; fi
echo "automation browser closed; profile saved"
ls -la "$PROFILE/Default/Cookies" 2>/dev/null | awk '{print "cookies file:", $5, "bytes", $6, $7, $8}'
