#!/bin/bash
# bravo_lock_probe.sh — diagnostic for the Bravo 2026.10.0.85 store-switch break: logs where Lock Session is and
# what clicking it opens (UIA dump to Bravo Data Extraction/logs/_lock_probe.log). Foreground-guarded.
# Joshua 10/30 "fix this". Additive.
AGENT=bravo-lockprobe; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
G="$BRAVO/_bravo_foreground_guard.sh"
if ! bash "$G" check; then vlog "Bravo busy — not touching it"; exit 0; fi
bash "$G" acquire "$AGENT"
rm -f "$BRAVO/logs/_lock_probe.log"
"$PRLCTL" exec "$VM" --current-user powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File '\\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction\_run_lock_probe.ps1' 2>&1 | tail -1
for i in $(seq 1 30); do grep -q "=== end" "$BRAVO/logs/_lock_probe.log" 2>/dev/null && break; sleep 3; done
cat "$BRAVO/logs/_lock_probe_err.txt" 2>/dev/null
bash "$G" release "$AGENT"
