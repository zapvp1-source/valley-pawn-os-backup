#!/bin/bash
# RETIRED 2026-09-24 before first use. Written for the missed-call-text agent, then found not
# needed: the fleet already has Zoom Server-to-Server credentials at ~/.vp_secrets/zoom_s2s.json
# (app "Valley Pawn Ops Agent", used by the Zoom Call Pipeline), and missed_call_text.py reads
# that file. Removed from host_queue_allowlist.txt so it cannot run. Safe to delete.
echo "retired — see header"; exit 0
