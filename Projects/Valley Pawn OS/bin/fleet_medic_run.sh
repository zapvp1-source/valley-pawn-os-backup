#!/bin/bash
# launchd wrapper — com.valleypawn.fleet-medic (every 5 min). Invoked via ~/bin/vp-runner (TCC).
# Layer-1 self-healing for the native agent fleet; see the header of bin/fleet_medic.py for the playbook.
# Observe-only switch: touch "fleet/state/fleet_medic_off". Log: ~/Library/Logs/valleypawn/fleet-medic.log
AGENT="fleet-medic"
. "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 10
/usr/bin/python3 "$BIN/fleet_medic.py" "$@"
