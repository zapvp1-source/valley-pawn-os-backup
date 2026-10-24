#!/bin/bash
# launchd wrapper — com.valleypawn.chekkit-customer-tags, nightly 01:10 (stores closed, texting quiet).
# Bravo customer facts (files already on disk, written by the forfeiture-winback agent) -> Chekkit customer tags.
# Up to 90 minutes, all 5 stores in parallel, picks up where it left off. Added 2026-10-23 (comms review build #4).
AGENT="chekkit-customer-tags"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 120
"$PY" "$BIN/chekkit_tags.py" sync --max-minutes 90 "$@" >> "$VLOG/$AGENT.log" 2>&1
