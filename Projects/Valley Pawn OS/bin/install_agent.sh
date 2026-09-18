#!/bin/bash
# install_agent.sh <label> [--restart-only]
# The ONE sanctioned way to (re)install or restart a com.valleypawn.* launchd agent from the host
# job queue (allow-listed; see host_queue_run.sh). Copies fleet/<label>.plist into
# ~/Library/LaunchAgents (backing up any existing copy), bootouts, bootstraps, kickstarts, and
# prints the resulting launchctl row. Refuses anything that is not a com.valleypawn.* label or
# whose plist does not route through ~/bin/vp-runner (every healthy agent does — TCC).
set +e
LABEL="$1"; MODE="$2"
U=$(id -u)
OS="$HOME/Documents/Claude/Projects/Valley Pawn OS"
SRC="$OS/fleet/$LABEL.plist"
LA="$HOME/Library/LaunchAgents"; DST="$LA/$LABEL.plist"
BK="$OS/fleet/_backups"; mkdir -p "$BK" "$LA"
case "$LABEL" in com.valleypawn.*) ;; *) echo "REFUSED: label must be com.valleypawn.* (got '$LABEL')"; exit 2 ;; esac
if [ "$MODE" = "--restart-only" ]; then
  launchctl kickstart -k "gui/$U/$LABEL" 2>&1 && echo "$LABEL restarted"
  sleep 2; launchctl list | grep -F "$LABEL"; exit 0
fi
[ -f "$SRC" ] || { echo "REFUSED: $SRC not found"; exit 2; }
grep -q "/bin/vp-runner" "$SRC" || { echo "REFUSED: $SRC does not run through ~/bin/vp-runner"; exit 2; }
plutil -lint "$SRC" >/dev/null 2>&1 || { echo "REFUSED: $SRC is not a valid plist"; exit 2; }
[ -f "$DST" ] && cp "$DST" "$BK/$LABEL.plist.bak-$(date +%Y%m%d-%H%M%S)"
cp "$SRC" "$DST"
launchctl bootout "gui/$U/$LABEL" 2>/dev/null; sleep 1
launchctl bootstrap "gui/$U" "$DST" 2>&1 && echo "$LABEL bootstrapped"
sleep 3; launchctl list | grep -F "$LABEL"
exit 0
