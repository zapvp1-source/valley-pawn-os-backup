#!/bin/bash
# bravo_whatsnew_dismiss.sh — close Bravo's "What's New in Bravo" panel (2026.10.0.85 update, 10/28) that
# blocks store switching and report menus. Contention-guarded (foreground guard). Allow-listed. Additive 2026-10-30.
AGENT=bravo-whatsnew; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
G="$BRAVO/_bravo_foreground_guard.sh"
if ! bash "$G" check; then vlog "Bravo busy — not touching it"; exit 0; fi
bash "$G" acquire "$AGENT"
rm -f "$BRAVO/logs/_whatsnew.log"
"$PRLCTL" exec "$VM" --current-user powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File '\\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction\_run_whatsnew.ps1' 2>&1 | tail -1
for i in $(seq 1 20); do grep -q "=== end" "$BRAVO/logs/_whatsnew.log" 2>/dev/null && break; sleep 3; done
cat "$BRAVO/logs/_whatsnew.log"
bash "$G" release "$AGENT"
