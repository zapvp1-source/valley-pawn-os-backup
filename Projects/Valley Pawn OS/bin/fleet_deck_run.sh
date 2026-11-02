#!/bin/bash
# launchd wrapper — com.valleypawn.fleet-deck (always on, KeepAlive). Invoked via ~/bin/vp-runner (TCC).
# Serves the VP Fleet Deck on http://127.0.0.1:8790 — read-only status of every agent on this Mac.
# Pure stdlib Python; never starts, stops or edits anything. Log: ~/Library/Logs/valleypawn/fleet-deck.out.log
AGENT="fleet-deck"
. "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
# no vp_lock here: the server execs and the 127.0.0.1:8790 bind is the single-instance guard
exec /usr/bin/python3 "$BIN/fleet_deck.py" --serve "$@"
