#!/bin/bash
# daily-loan-inventory-text :: background data pull (runs detached on the Mac).
# Source = Bravo "End of Month" report (reliable Reports->Export, NO SSRS date-
# picker). One trigger for all 5 stores; each xlsx carries Ending Loan Base +
# Ending Inventory Base (same basis as the 6/30 baseline). Window ends YESTERDAY
# (EOM refuses today/future). compute.py sums the 5 stores and builds the text.
# Launch with nohup so it never hits the osascript ~25s kill.
set -u
BX="/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction"
TASK="/Users/joshuadavis/Documents/Claude/Scheduled/daily-loan-inventory-text"
STATUS="$TASK/latest_status.txt"; MSG="$TASK/latest_message.txt"
JSONOUT="$TASK/latest_reading.json"; LOG="$TASK/run.log"
OUT="$BX/output"
STORES="CUL HAR LEX ROA WAY"

echo "RUNNING $(date)" > "$STATUS"
echo "=== run $(date) ===" >> "$LOG"
cd "$BX" 2>/dev/null || { echo "FAIL no-bravo-dir" > "$STATUS"; exit 3; }

TODAY=$(TZ=America/New_York date +%F)
YEST=$(TZ=America/New_York date -v-1d +%F)
FIRST=$(TZ=America/New_York date +%Y-%m-01)
RANGE="${FIRST}..${YEST}"

heal() {
  nohup ./bravo_ensure_healthy.sh >/dev/null 2>&1 &
  for i in $(seq 1 48); do
    grep -q PASS logs/_health_gate_status.txt 2>/dev/null && break
    sleep 10
  done
}

missing_stores() {
  local m=""
  for s in $STORES; do
    [ -s "$OUT/${YEST}_${s}_end-of-month.xlsx" ] || m="$m $s"
  done
  echo $m
}

heal

for round in 1 2 3; do
  NEED=$(missing_stores)
  [ -z "$NEED" ] && break
  # Build JSON store array for the still-missing stores.
  arr=""; for s in $NEED; do arr="$arr\"$s\","; done; arr="[${arr%,}]"
  TID="loan-inv-text-$(TZ=America/New_York date +%Y-%m-%dT%H-%M-%S)-r${round}"
  TS=$(TZ=America/New_York date +%FT%T%z)
  printf '%s' "{\"id\":\"$TID\",\"requested_at\":\"$TS\",\"reports\":[{\"name\":\"end-of-month\",\"stores\":$arr,\"date\":\"$RANGE\"}]}" > "$BX/triggers/$TID.json"
  echo "round $round: dropped $TID for stores$NEED (window $RANGE)" >> "$LOG"
  # Poll up to ~24 min for all needed stores to appear.
  for i in $(seq 1 144); do
    [ -z "$(missing_stores)" ] && break
    sleep 10
  done
  [ -z "$(missing_stores)" ] && break
  echo "round $round: still missing$(missing_stores) — re-healing" >> "$LOG"
  heal
done

STILL=$(missing_stores)
if [ -z "$STILL" ]; then
  if python3 "$TASK/compute.py" --outdir "$OUT" --end "$YEST" --asof "$TODAY" --json-out "$JSONOUT" > "$MSG" 2>> "$LOG"; then
    echo "OK" > "$STATUS"; echo "OK $(date)" >> "$LOG"
  else
    echo "FAIL compute" > "$STATUS"
  fi
else
  echo "FAIL missing-stores:$STILL" > "$STATUS"
  echo "gave up with missing:$STILL" >> "$LOG"
fi
