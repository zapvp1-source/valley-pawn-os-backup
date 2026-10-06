#!/bin/bash
# scrap_closeout_run.sh <manifest-id> [cap-seconds]   (added 2026-09-28, allow-listed host primitive)
#
# Runs ONE scrap bucket close-out manifest through the native AHK handler
# (Bravo Data Extraction/reports/ScrapBucketCloseout.ahk) and waits for its result.
# The caller (a Cowork session or the precious-metals task) writes the manifest FIRST to
#   Bravo Data Extraction/triggers-scrap/<manifest-id>.json
# then drops a host_queue job that calls this script. Nothing here decides amounts —
# the manifest is the approved allocation workbook, already reviewed by Joshua.
#
# Steps: foreground guard -> Bravo alive check (health gate if not) -> launch the scrap
# watcher one-shot in the VM (Session 1) -> wait for results-scrap/<id>.result.json ->
# print the run log + result -> stop the scrap watcher, re-arm the main pipeline
# watchdog -> release guard. Exit 0 = result file written (read it for per-bucket status).
AGENT=scrap-closeout; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; vp_lock $AGENT 60
ID="$1"; CAP="${2:-2700}"
[ -z "$ID" ] && { echo "usage: scrap_closeout_run.sh <manifest-id> [cap-seconds]"; exit 2; }
MAN="$BRAVO/triggers-scrap/$ID.json"; RES="$BRAVO/results-scrap/$ID.result.json"; LOGF="$BRAVO/logs-scrap/$ID.log"
[ -f "$MAN" ] || { echo "manifest not found: $MAN"; exit 2; }
[ -f "$RES" ] && { echo "result already exists for $ID — refusing to re-run (delete/rename it first)"; exit 3; }

G="$BRAVO/_bravo_foreground_guard.sh"
for i in 1 2 3 4 5 6 7 8 9 10 11 12; do
  if bash "$G" check >/dev/null 2>&1 && ! bravo_busy 6; then break; fi
  vlog "Bravo busy — wait 60s ($i/12)"; sleep 60
done
bash "$G" check >/dev/null 2>&1 || { vlog "foreground guard still BUSY — giving up, nothing touched"; exit 4; }
bash "$G" acquire "$AGENT" >/dev/null 2>&1
cleanup() {
  vm_ps_file '\\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction\_scrap_closeout_stop.ps1' 2>&1 | tail -4
  bash "$G" release "$AGENT" >/dev/null 2>&1
  rmdir "$VLOG/.lock.$AGENT" 2>/dev/null
}
trap cleanup EXIT

if ! bravo_procs | grep -q "Bravo.exe"; then
  vlog "Bravo.exe not running — health gate"; vlog "health gate: $(health_gate 600)"
fi
bravo_procs | grep -q "Bravo.exe" || { vlog "Bravo still not running — aborting, nothing touched"; exit 5; }

vlog "launching scrap watcher for $ID"
vm_ps_file '\\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction\_scrap_closeout_launch.ps1' 2>&1 | tail -3
t0=$(date +%s)
while [ $(( $(date +%s) - t0 )) -lt "$CAP" ]; do
  [ -f "$RES" ] && break
  sleep 20
done
echo "=== LOG $LOGF ==="; cat "$LOGF" 2>/dev/null | tail -400
if [ -f "$RES" ]; then echo "=== RESULT $RES ==="; cat "$RES"; exit 0; fi
vlog "TIMEOUT after ${CAP}s waiting for $ID (manifest claimed: $([ -f "$BRAVO/triggers-scrap/claimed/$ID.json" ] && echo yes || echo no))"
exit 1
