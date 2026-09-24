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

# Step 1/2 — read the summary; if missing/stale/not ok, run the importer once
if ! fresh_ok; then
  vlog "summary missing or stale — running run_daily_v5.sh"
  /bin/bash "$H/bin/run_daily_v5.sh" >> "$VLOG/$AGENT.log" 2>&1
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
