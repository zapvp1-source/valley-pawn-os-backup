#!/bin/bash
# bravo_watcher_validate.sh [--restart] — added 2026-10-06 (jewelry v3 handler).
# AHK /validate of bravo_watcher.ahk inside the VM (never touches Bravo or the running watcher).
# With --restart, and ONLY if validation exits 0, hands off to bravo_watcher_restart.sh (which waits
# for an idle pipeline). Exit 0 = valid (and restarted if asked); 1 = invalid or could not verify.
AGENT=bravo-watcher-validate; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
OUT="$BRAVO/logs/_validate_watcher_v3.txt"; rm -f "$OUT"
vm_ps_file 'Y:\Documents\Claude\Projects\Bravo Data Extraction\_validate_watcher_v3.ps1' > /tmp/vp_validate_v3.log 2>&1
sleep 3; cat "$OUT" 2>/dev/null || { echo "no validation output"; cat /tmp/vp_validate_v3.log; exit 1; }
grep -q "^VAL exit=0" "$OUT" || { vlog "validation FAILED — not restarting"; echo "INVALID"; exit 1; }
vlog "validation OK"; echo "VALID"
[ "$1" = "--restart" ] || exit 0
exec bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_watcher_restart.sh"
