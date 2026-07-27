#!/bin/bash
# =============================================================================
# bravo_pull_complete.sh  —  ALL-OR-RETRY puller (no partial "success")
# -----------------------------------------------------------------------------
# Joshua's rule (2026-06-19): a partial result is NOT a success. If a store
# wedges, recover Bravo and GO BACK for that store. Only ALL requested stores
# reporting counts as done.
#
# What it does, per round:
#   1. ensure Bravo healthy (single-flight guard; force-rechecks on retries so a
#      mid-run wedge is actually recovered, not masked by a stale PASS)
#   2. drop ONE trigger for the still-missing stores
#   3. wait for the watcher's result.json, parse PER-STORE status
#   4. mark the stores that succeeded; whatever is still missing goes to the
#      next round
# Repeats up to MAX_ROUNDS. Exit 0 ONLY if every requested store succeeded.
#
# ADDITIVE: NET-NEW file. Invokes bravo_ensure_healthy.sh + the watcher via
# trigger files. Edits nothing.
#
# USAGE (run detached; poll the STATUS file):
#   nohup bash bravo_pull_complete.sh <cell> <date> <STORE...> >/dev/null 2>&1 &
#   STATUS file -> "RUNNING" | "COMPLETE" | "INCOMPLETE <csv-of-missing>"
#   On COMPLETE, read output/<date>_<STORE>_<cell>.csv as usual.
#
# Exit: 0 = all stores succeeded.  1 = incomplete after retries.
# =============================================================================
set -u

ROOT="/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction"
ENSURE="$ROOT/bravo_ensure_healthy.sh"
LOGDIR="$ROOT/logs"; TRIGDIR="$ROOT/triggers"; RESDIR="$ROOT/results"
GATE_STATUS="$LOGDIR/_health_gate_status.txt"

CELL="${1:?cell required}"; DATE="${2:?date required}"; shift 2
ALL_STORES=("$@")
[ ${#ALL_STORES[@]} -gt 0 ] || { echo "no stores given" >&2; exit 2; }

MAX_ROUNDS=4
POLL_CAP=44          # ~15s each -> ~11 min per round (breaks as soon as result lands)
STAMP="$(date '+%Y-%m-%dT%H-%M-%S')"
SAFE="$(echo "${CELL}_${DATE}" | tr -c 'A-Za-z0-9' '_')"
STATUS="$LOGDIR/_pull_status_${SAFE}.txt"
PLOG="$LOGDIR/_pull_complete.log"

ts(){ date '+%Y-%m-%d %H:%M:%S'; }
log(){ echo "$(ts) | pull[$CELL $DATE] | $*" | tee -a "$PLOG" >&2; }
echo "RUNNING" > "$STATUS"
log "START stores=${ALL_STORES[*]}"

declare -A DONE
remaining=("${ALL_STORES[@]}")

for round in $(seq 1 "$MAX_ROUNDS"); do
  [ ${#remaining[@]} -eq 0 ] && break

  # On any retry round, a store almost certainly wedged Bravo. Force the guard
  # to actually re-run (don't let a pre-wedge PASS short-circuit the recovery).
  [ "$round" -gt 1 ] && rm -f "$GATE_STATUS" 2>/dev/null

  log "round $round: ensure-healthy, then pull: ${remaining[*]}"
  if ! bash "$ENSURE" "${remaining[0]}"; then
    log "round $round: ensure-healthy returned non-PASS; retrying loop"
    sleep 5
  fi

  # build JSON store array
  sj=""; for s in "${remaining[@]}"; do sj="$sj\"$s\","; done; sj="${sj%,}"
  TID="${CELL}-complete-${STAMP}-r${round}"
  NOW="$(date '+%Y-%m-%dT%H:%M:%S%z')"
  printf '%s' "{\"id\":\"$TID\",\"requested_at\":\"$NOW\",\"reports\":[{\"name\":\"$CELL\",\"stores\":[$sj],\"date\":\"$DATE\"}]}" > "$TRIGDIR/$TID.json"
  log "round $round: dropped $TID"

  RJ="$RESDIR/$TID.result.json"
  for i in $(seq 1 "$POLL_CAP"); do sleep 15; [ -f "$RJ" ] && break; done
  if [ ! -f "$RJ" ]; then
    log "round $round: TIMEOUT waiting for result.json"
    continue
  fi

  # parse per-store success (BOM-safe)
  succ="$(python3 -c "import json,sys
d=json.load(open(sys.argv[1],encoding='utf-8-sig'))
print(' '.join(c['store'] for c in d.get('cells',[]) if c.get('status')=='success'))" "$RJ" 2>/dev/null)"
  log "round $round: succeeded=[$succ]"
  for s in $succ; do DONE[$s]=1; done

  newrem=(); for s in "${ALL_STORES[@]}"; do [ -z "${DONE[$s]:-}" ] && newrem+=("$s"); done
  remaining=("${newrem[@]}")
  log "round $round: still missing=[${remaining[*]:-none}]"
done

if [ ${#remaining[@]} -eq 0 ]; then
  echo "COMPLETE" > "$STATUS"
  log "COMPLETE — all stores reported: ${ALL_STORES[*]}"
  exit 0
else
  miss="$(IFS=,; echo "${remaining[*]}")"
  echo "INCOMPLETE $miss" > "$STATUS"
  log "INCOMPLETE — missing after $MAX_ROUNDS rounds: $miss"
  exit 1
fi
