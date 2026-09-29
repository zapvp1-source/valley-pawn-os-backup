#!/bin/bash
# scrap_closeout_diag_kill.sh — one-off diagnostic: screenshot the VM, then
# stop a stuck scrap watcher and re-arm the main pipeline. Added 2026-09-28b
# after scrap-closeout-2026-08-live-har-fix hung >9min past "already on HAR"
# with no further log lines (never reached the first bucket).
. "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
echo "--- screenshot ---"
vm_ps_file '\\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction\_shot.ps1' 2>&1
echo "--- stop scrap watcher / resume main watcher ---"
vm_ps_file '\\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction\_scrap_closeout_stop.ps1' 2>&1
