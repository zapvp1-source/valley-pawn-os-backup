#!/bin/bash
# unload_oneshot.sh <label> — unload a *-oneshot agent whose job is DONE and verified.
# WHY (2026-09-24): com.valleypawn.chekkitperms-oneshot did its job on 9/22 02:10 (verified post-
# relaunch) but had no self-removal, so it kept quitting and relaunching Claude.app every night at
# 02:10. retire_agent.sh correctly refuses to touch an agent whose program still exists; this is the
# deliberate path for the one case that is not a broken agent: a finished one-shot.
# Only labels ending in -oneshot. Plist is moved to fleet/_retired-oneshots/, never deleted.
set +e
LABEL="$1"; U=$(id -u)
OS="$HOME/Documents/Claude/Projects/Valley Pawn OS"
case "$LABEL" in com.valleypawn.*-oneshot) ;; *) echo "REFUSED: $LABEL is not a com.valleypawn.*-oneshot label"; exit 2;; esac
P="$HOME/Library/LaunchAgents/$LABEL.plist"
launchctl bootout "gui/$U/$LABEL" 2>/dev/null && echo "booted out $LABEL" || echo "$LABEL was not loaded"
STAMP=$(date +%Y%m%d-%H%M%S); mkdir -p "$OS/fleet/_retired-oneshots"
[ -f "$P" ] && mv "$P" "$OS/fleet/_retired-oneshots/$LABEL.plist.retired-$STAMP" && echo "moved $P -> fleet/_retired-oneshots/"
[ -f "$OS/fleet/$LABEL.plist" ] && mv "$OS/fleet/$LABEL.plist" "$OS/fleet/_retired-oneshots/$LABEL.plist.fleetcopy-retired-$STAMP"
launchctl print "gui/$U/$LABEL" >/dev/null 2>&1 && echo "STILL LOADED" || echo "confirmed unloaded: $LABEL"
