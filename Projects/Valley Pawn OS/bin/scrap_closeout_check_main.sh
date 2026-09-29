#!/bin/bash
# scrap_closeout_check_main.sh — one-off check: is the main Bravo pipeline
# watcher back up after a scrap-closeout stop/resume? (added 2026-09-28b)
. "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
echo "bravo procs:"; bravo_procs
echo "ahk cmdlines:"
vm_ps_file '\\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction\_check_ahk_cmdline.ps1' 2>&1 | tail -20
