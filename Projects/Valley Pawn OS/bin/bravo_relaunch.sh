#!/bin/bash
# Native replacement for bravo-preflight-relaunch (04:00) and bravo-prestaging-7am (06:30) — 2026-09-17.
# Relaunch Bravo + watcher in the VM, verify Bravo.exe and dfsvc.exe, retry once. Foreground-guarded.
AGENT=bravo-relaunch; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; vp_lock $AGENT 30
G="$BRAVO/_bravo_foreground_guard.sh"
if ! bash "$G" check >/dev/null 2>&1; then vlog "foreground guard BUSY — skip"; exit 0; fi
bash "$G" acquire "$AGENT" >/dev/null 2>&1
trap 'bash "'"$G"'" release "'"$AGENT"'" >/dev/null 2>&1; rmdir "'"$VLOG/.lock.$AGENT"'" 2>/dev/null' EXIT
# HEALTHY = Bravo.exe running. dfsvc.exe is the ClickOnce DEPLOYMENT service: it runs only while an
# update is in flight, and the health gate treats its presence as the "update-prompt wedge". Requiring
# it (as this script did on 2026-09-17) ledgers a false failure on every healthy run — 04:06 and 06:36
# on 9/18 both fired while Bravo was fine and the 06:50 morning pull then ran clean. Corrected 9/18.
for attempt in 1 2; do
  bravo_relaunch; vlog "relaunch attempt $attempt rc=$?"; sleep 90
  P=$(bravo_procs | tr '\n' ' '); vlog "procs: ${P:-none}"
  if echo "$P" | grep -q "Bravo.exe"; then
    echo "$P" | grep -q "dfsvc.exe" && vlog "NOTE: dfsvc.exe present — a ClickOnce update is in flight; _clickonce_guard.ahk owns that"
    vlog "OK — Bravo.exe running"; exit 0
  fi
  sleep 60
done
ledger "bravo-relaunch" "Bravo POS did not come back up in the Windows VM after two relaunch attempts." "no"
exit 1
