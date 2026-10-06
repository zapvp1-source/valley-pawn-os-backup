#!/bin/bash
# bravo_screen.sh — READ-ONLY: capture the VM's interactive desktop to Bravo Data Extraction/logs/_vmshot.png
# (Session-1 scheduled-task trick, the pipeline's own _session1_shot.ps1). Allow-listed diagnostic.
. "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
rm -f "$BRAVO/logs/_vmshot.png"
"$PRLCTL" exec "$VM" --current-user powershell.exe -NoProfile -ExecutionPolicy Bypass -File '\\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction\_session1_shot.ps1' 2>&1 | tail -2
for i in 1 2 3 4 5 6; do [ -s "$BRAVO/logs/_vmshot.png" ] && break; sleep 3; done
ls -la "$BRAVO/logs/_vmshot.png" 2>&1
echo "--- Bravo/dfsvc processes ---"; bravo_procs | tr '\n' ' '; echo
echo "--- health gate ---"; cat "$BRAVO/logs/_health_gate_status.txt" 2>/dev/null; tail -6 "$BRAVO/logs/_health_gate.log" 2>/dev/null | cut -c1-160
