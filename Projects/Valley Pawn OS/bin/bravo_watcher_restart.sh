#!/bin/bash
# bravo_watcher_restart.sh — restart ONLY the AHK watcher in the Bravo VM so it picks up a newly
# registered report handler (#Include + REPORT_HANDLERS line in bravo_watcher.ahk). Allow-listed
# host primitive, added 2026-09-30 for the loans75-detail cell. Bravo itself is never touched.
#   - waits until the pipeline is idle (no claimed trigger / result in the last 6 min), up to 3 tries
#   - runs the exact watcher_restart the SKILLs and bravo_run's self-heal already use
#   - verifies a fresh bravo_watcher.ahk process exists in the VM afterwards
# Exit 0 = watcher restarted and seen running. Exit 1 = could not verify (nothing else changed).
AGENT=bravo-watcher-restart; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; vp_lock $AGENT 30
for i in 1 2 3; do bravo_busy 6 || break; vlog "pipeline busy — wait 3 min ($i/3)"; sleep 180; done
bravo_busy 6 && { vlog "still busy after 9 min — not restarting mid-run, exit"; exit 1; }
vlog "restarting watcher"
watcher_restart; vlog "watcher_restart rc=$?"
sleep 45
W=$(vm_ps_cmd "Get-CimInstance Win32_Process | Where-Object { \$_.CommandLine -like '*bravo_watcher.ahk*' } | Select-Object -ExpandProperty CommandLine" 2>/dev/null | tr -d '\r')
vlog "watcher cmdline: ${W:-none}"
echo "$W" | grep -q "bravo_watcher.ahk" && { vlog "OK — watcher running"; exit 0; }
vlog "watcher not seen after restart"; exit 1
