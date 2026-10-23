#!/bin/bash
# oura_import.sh — native replacement for the Cowork task `oura-daily-import`.
#
# WHY (2026-09-23): the Cowork version's every step is `do shell script` through the
# Control_your_Mac connector, which is gone from scheduled sessions. Its own SKILL says "launchd
# cannot touch ~/Documents at all (TCC denies it)" — that is the same disproven Full-Disk-Access
# belief; vp-runner writes into Projects every day. So this does the exact steps natively.
#
# Publishes nothing on success. Ledger row on failure (Failure Policy v3). Domain 3 — personal.
AGENT="oura-daily-import"
. "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
RENDER=0; for a in "$@"; do [ "$a" = "--render" ] && RENDER=1; done
[ $RENDER -eq 0 ] && vp_lock "$AGENT" 30
H="$HOME/Library/Application Support/HealthOS"
HP="$HOME/Documents/Claude/Projects/Health Optimization"
TODAY=$(date +%Y-%m-%d)

fresh_ok() {  # oura_latest.json exists, run_at is today, status ok
  [ -f "$H/oura_latest.json" ] || return 1
  $PY - "$H/oura_latest.json" "$TODAY" <<'PY'
import json,sys
d=json.load(open(sys.argv[1])); ok = str(d.get("run_at",""))[:10]==sys.argv[2] and str(d.get("status","")).lower()=="ok"
sys.exit(0 if ok else 1)
PY
}

if [ $RENDER -eq 1 ]; then
  echo "=== RENDER ONLY ==="; echo "summary fresh today: $(fresh_ok && echo yes || echo no)"; exit 0
fi

# 2026-10-06: HealthOS's own agent com.healthos.oura-import runs the SAME run_daily_v5.sh at the same
# 08:30. This check used to see "stale" while that run was still going and start a SECOND importer:
# the two raced on oura.db.gz.new / oura_latest.json.tmp ("mv: ... No such file", FileNotFoundError on
# 10/5 and 10/6) and fleet-doctor reported the job as failing. Let the other run start, wait for it to
# finish (cap 10 min), then decide. Only if the summary is still stale do we run the importer ourselves.
sleep 20
W=0; while pgrep -f run_daily_v5.sh >/dev/null && [ $W -lt 600 ]; do sleep 10; W=$((W+10)); done
[ $W -gt 0 ] && vlog "waited ${W}s for the HealthOS importer already running"

# Step 1/2 — read the summary; if missing/stale/not ok, run the importer once
if ! fresh_ok; then
  vlog "summary missing or stale — running run_daily_v5.sh"
  # 2026-10-22: importer output goes to a scratch file first so a "ring hasn't synced" day can be told apart
  # from a real fault (bad token, crash). 10/17-10/22: the API answered every call (personal_info /
  # ring_configuration rows came back, "=== Done." printed) but the ring itself had not synced, so the
  # sanity assert "readiness latest ... is N days old" failed and this job ledgered + was re-run twice a day.
  # A ring that hasn't synced is not a fleet fault: ONE quiet NEEDS_HUMAN ledger row per day, exit 0.
  OUT_TMP="$VLOG/.oura_import_run.txt"
  /bin/bash "$H/bin/run_daily_v5.sh" > "$OUT_TMP" 2>&1
  RING=$("$PY" "$BIN/oura_sync_check.py" "$OUT_TMP" "$H/oura_latest.json")
  if [ "${RING%% *}" = "RING_NOT_SYNCED" ]; then
    grep -v -E "Traceback|AssertionError|File \"<stdin>\"|WARN: sanity check failed|^\{\"status\"" "$OUT_TMP" >> "$VLOG/$AGENT.log"
    vlog "ring not synced: ${RING#* } (Oura API reachable, token OK) — not a fleet fault"
    MARK="$VLOG/.oura_ring_unsynced_$TODAY"
    if [ ! -f "$MARK" ]; then
      : > "$MARK"
      ledger "$AGENT" "Oura ring has not synced to the Oura cloud since ${RING#* } (the Oura API itself answers fine, so nothing in the fleet is broken). Health data waits until the ring syncs." "yes, open the Oura app to sync the ring"
    fi
    vlog "=== oura import done ==="
    exit 0
  fi
  cat "$OUT_TMP" >> "$VLOG/$AGENT.log"
  if ! fresh_ok; then
    ERR=$(tail -3 "$H/logs/oura-import.err.log" 2>/dev/null | tr '\n' ' ' | cut -c1-200)
    ledger "$AGENT" "Today's Oura import did not produce a good summary after one rerun. Last error: ${ERR:-none recorded}." "no"
    exit 1
  fi
fi
# Step 3 — mirror artifacts into the project folder
mkdir -p "$HP/oura"
for f in oura_latest.json STATUS_oura_pipeline.md; do [ -f "$H/$f" ] && cp "$H/$f" "$HP/oura/"; done
# Step 4 — refresh the nights ledger
( cd "$HP" && $PY scripts/night_signature.py >> "$VLOG/$AGENT.log" 2>&1 ) || ledger "$AGENT" "Oura import ran, but the nights ledger refresh failed." "no"
$PY "$BIN/vp_receipt.py" write "$AGENT" --surface file --target "$HP/oura/oura_latest.json" >/dev/null 2>&1
vlog "=== oura import done ==="
