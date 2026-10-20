#!/bin/bash
# vp_signin_close.sh — gracefully quit ONLY the automation Chrome on the single profile
# ~/Library/Application Support/valleypawn/pw-vp so its saved sign-ins are flushed to disk (2026-10-19).
# ONE SIGTERM to the main process = Chrome's graceful "end session" exit: cookies flushed to disk, Preferences
# records exit_type "SessionEnded" + exited_cleanly true (Cmd-Q records "Normal"; both proven equivalent for
# session-cookie persistence on 2026-10-19, job 20261019T1040-vp-profile-proof2). Never SIGKILL. Never
# touches Joshua's everyday Chrome.
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
MAIN=$(pgrep -f -- "Google Chrome --user-data-dir=$PROFILE" | head -1)
[ -n "$MAIN" ] && kill -TERM "$MAIN"
for i in $(seq 1 30); do pgrep -f -- "--user-data-dir=$PROFILE" >/dev/null || break; sleep 1; done
if pgrep -f -- "--user-data-dir=$PROFILE" >/dev/null; then echo "still running after 30s"; exit 1; fi
sleep 1
echo "automation browser closed; profile saved"
ls -la "$PROFILE/Default/Cookies" 2>/dev/null | awk '{print "cookies file:", $5, "bytes", $6, $7, $8}'
ET=$(/usr/bin/python3 "$OS_BIN/vp_browser.py" exit-type)
echo "$ET"
case "$ET" in *"'Normal', 1)"*|*"'SessionEnded', 1)"*) exit 0 ;; *) echo "WARNING: not a clean exit with the startup pref at 1 (expected ('Normal'|'SessionEnded', 1))"; exit 3 ;; esac
