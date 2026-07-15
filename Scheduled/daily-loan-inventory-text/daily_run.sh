#!/bin/bash
# daily-loan-inventory-text :: background data pull (runs detached on the Mac).
# Health-gate -> (retry up to 3x) drop a company-kpis trigger for
# <first-of-month>..<yesterday> -> wait for the consolidated xlsx -> compute.py.
# Window ends YESTERDAY on purpose: the report's Loan/Inventory Balance are the
# close-of-that-date standing balances, and Bravo's picker/date logic rejects
# today/future. On the 1st of a month, yesterday == prior month-end, which is
# exactly the baseline (0 growth that day). Launch with nohup so it never hits
# the osascript ~25s kill.
set -u
BX="/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction"
TASK="/Users/joshuadavis/Documents/Claude/Scheduled/daily-loan-inventory-text"
STATUS="$TASK/latest_status.txt"
MSG="$TASK/latest_message.txt"
JSONOUT="$TASK/latest_reading.json"
LOG="$TASK/run.log"

echo "RUNNING $(date)" > "$STATUS"
echo "=== run $(date) ===" >> "$LOG"
cd "$BX" 2>/dev/null || { echo "FAIL no-bravo-dir" > "$STATUS"; exit 3; }

TODAY=$(TZ=America/New_York date +%F)
YEST=$(TZ=America/New_York date -v-1d +%F)
FIRST=$(TZ=America/New_York date +%Y-%m-01)
OUT="$BX/output/${YEST}_ALL_company-kpis.xlsx"

heal() {
  nohup ./bravo_ensure_healthy.sh >/dev/null 2>&1 &
  for i in $(seq 1 48); do
    grep -q PASS logs/_health_gate_status.txt 2>/dev/null && break
    sleep 10
  done
}

heal

ok=0
[ -f "$OUT" ] && ok=1
for attempt in 1 2 3; do
  [ "$ok" = "1" ] && break
  TID="loan-inv-text-$(TZ=America/New_York date +%Y-%m-%dT%H-%M-%S)-a${attempt}"
  TS=$(TZ=America/New_York date +%FT%T%z)
  printf '%s' "{\"id\":\"$TID\",\"requested_at\":\"$TS\",\"reports\":[{\"name\":\"company-kpis\",\"stores\":[\"ALL\"],\"date\":\"${FIRST}..${YEST}\"}]}" > "$BX/triggers/$TID.json"
  echo "attempt $attempt: dropped $TID (window ${FIRST}..${YEST})" >> "$LOG"
  # Wait for the xlsx, or for this attempt's result.json (then re-check xlsx). Cap ~8 min/attempt.
  for i in $(seq 1 48); do
    [ -f "$OUT" ] && { ok=1; break; }
    [ -f "$BX/results/${TID}.result.json" ] && { sleep 5; [ -f "$OUT" ] && ok=1; break; }
    sleep 10
  done
  [ "$ok" = "1" ] && break
  echo "attempt $attempt: no xlsx (likely flaky SSRS date-picker) — re-healing and retrying" >> "$LOG"
  heal
done

if [ -f "$OUT" ]; then
  if python3 "$TASK/compute.py" --xlsx "$OUT" --asof "$TODAY" --json-out "$JSONOUT" > "$MSG" 2>> "$LOG"; then
    echo "OK" > "$STATUS"; echo "OK $(date)" >> "$LOG"
  else
    echo "FAIL compute" > "$STATUS"
  fi
else
  echo "FAIL no-xlsx-after-3-attempts" > "$STATUS"
  echo "no xlsx at $OUT after 3 attempts" >> "$LOG"
fi
