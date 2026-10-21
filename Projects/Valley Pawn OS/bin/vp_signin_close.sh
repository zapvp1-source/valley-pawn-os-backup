#!/bin/bash
# vp_signin_close.sh — gracefully quit ONLY the automation Chrome on the single profile
# ~/Library/Application Support/valleypawn/pw-vp so its saved sign-ins are flushed to disk (2026-10-19).
#
# 2026-10-20: FIRST try CDP Browser.close through the sign-in window's DevTools port (vp_browser.py cdp-close;
# the port is opened by vp_signin_front.sh --remote-debugging-port=9333). That is Chrome's own quit, the same
# path as Cmd-Q, so Preferences records exit_type "Normal". FALLBACK = ONE SIGTERM to the main process, which
# Chrome records as "SessionEnded" + exited_cleanly true (not a crash, not a sign-out: with the startup pref at
# "Continue where you left off" session cookies are restored either way — proven 2026-10-19, job
# 20261019T1040-vp-profile-proof2, re-proven 2026-10-20). Never SIGKILL. Never touches Joshua's everyday Chrome.
# Exit 0 = closed cleanly (Normal or SessionEnded) with the startup pref at 1; 1 = still running after 30 s;
# 3 = closed but not recorded as a clean exit (the next launch's prefs() repairs the flag, but say so).
PROFILE="$HOME/Library/Application Support/valleypawn/pw-vp"
OS_BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
PIDS=$(pgrep -f -- "--user-data-dir=$PROFILE" | tr '\n' ' ')
if [ -z "$PIDS" ]; then
  echo "automation browser not running"
  /usr/bin/python3 "$OS_BIN/vp_browser.py" exit-type
  exit 0
fi
R=$(/usr/bin/python3 "$OS_BIN/vp_browser.py" cdp-close 2>&1 | tail -1)
echo "cdp-close: $R"
if [ "$R" != "CLOSED" ] && pgrep -f -- "--user-data-dir=$PROFILE" >/dev/null; then
  MAIN=$(pgrep -f -- "Google Chrome --user-data-dir=$PROFILE" | head -1)
  [ -n "$MAIN" ] && kill -TERM "$MAIN" && echo "fallback: SIGTERM to pid $MAIN"
fi
for i in $(seq 1 30); do pgrep -f -- "--user-data-dir=$PROFILE" >/dev/null || break; sleep 1; done
if pgrep -f -- "--user-data-dir=$PROFILE" >/dev/null; then echo "still running after 30s"; exit 1; fi
sleep 1
echo "automation browser closed; profile saved"
ls -la "$PROFILE/Default/Cookies" 2>/dev/null | awk '{print "cookies file:", $5, "bytes", $6, $7, $8}'
ET=$(/usr/bin/python3 "$OS_BIN/vp_browser.py" exit-type)
echo "$ET"
case "$ET" in *"'Normal', 1)"*|*"'SessionEnded', 1)"*) exit 0 ;; *) echo "WARNING: not a clean exit with the startup pref at 1 (expected ('Normal'|'SessionEnded', 1))"; exit 3 ;; esac
