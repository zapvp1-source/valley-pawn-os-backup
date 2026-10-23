#!/bin/bash
# launchd wrapper — com.valleypawn.ebay-inbox-alert (Mon–Sat 10:15 = am, 15:15 = pm). Built 2026-10-22.
# Dormant unless fleet/state/native_live/ebay-inbox-alert exists (vp_live.sh). Usage: ebay_inbox_alert.sh am|pm [--render|--probe]
AGENT="ebay-inbox-alert"
. "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
SLOT="$1"; shift
if [ -z "$SLOT" ]; then H=$(date +%H); [ "$H" -lt 12 ] && SLOT=am || SLOT=pm; fi
MANUAL=0; for a in "$@"; do case "$a" in --render|--probe) MANUAL=1 ;; esac; done
if [ $MANUAL -eq 0 ]; then vp_live_gate "$AGENT"; vp_lock "$AGENT" 20; fi
if [ "$SLOT" = "probe" ]; then "$PY" "$BIN/ebay_inbox_alert.py" --probe 2>&1 | tee -a "$VLOG/$AGENT.log"; exit ${PIPESTATUS[0]}; fi
"$PY" "$BIN/ebay_inbox_alert.py" --slot "$SLOT" "$@" 2>&1 | tee -a "$VLOG/$AGENT.log"
exit ${PIPESTATUS[0]}
