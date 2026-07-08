#!/bin/bash
# ============================================================================
# eom_runner_v3.sh - per-store EOM runner, NO store-switch (2026-06-22)
#
# Strategy (evidence-based):
#  - Export freeze = the CS toggle (now removed; gold-standard handler exports
#    clean, proven by CUL+ROA on 2026-06-22 16:03/16:06).
#  - Remaining residual = the store-SWITCH (EOM preview-exit/BackToDashboard
#    strands after the 2nd store). ELIMINATE switching entirely:
#    For each store: kill Bravo -> it relaunches to "Select a store" -> the
#    watcher gate (patched to read the trigger's single target store) selects
#    THAT store directly -> login -> run the single-store EOM. No switch ever,
#    and a fresh Bravo each time so no stranded preview can cascade.
#  - This VM is a dedicated automation box (not an in-store register), so
#    killing Bravo between stores is fine.
# ============================================================================
BASE="/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction"
VM="{7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}"
TRIG="$BASE/triggers"; RES="$BASE/results"; OUT="$BASE/output"
LOG="$BASE/logs/_eom_runner_v3.log"
PRL=/usr/local/bin/prlctl
ENDDATE="2026-06-21"
RANGE="2026-06-01..2026-06-21"
STORES="CUL HAR LEX ROA WAY"
MAX_ATTEMPTS=2
WAIT_SECS=420

log(){ echo "$(date '+%Y-%m-%d %H:%M:%S') $*" >> "$LOG"; }
killbravo(){ $PRL exec "$VM" --current-user wmic process where "name='Bravo.exe'" call terminate >/dev/null 2>&1; }

: > "$LOG"
log "=== EOM runner v3 (per-store, no switch) start ==="
SUMMARY=""
for S in $STORES; do
  ok=0
  for a in $(seq 1 $MAX_ATTEMPTS); do
    log "[$S] attempt $a/$MAX_ATTEMPTS: kill Bravo -> fresh 'Select a store', gate will pick $S directly"
    killbravo; sleep 6
    RF="$RES/eomdirect-$S.result.json"; rm -f "$RF" 2>/dev/null
    CSV="$OUT/${ENDDATE}_${S}_end-of-month.csv"; rm -f "$CSV" 2>/dev/null
    printf '{"id":"eomdirect-%s","requested_at":"%s","reports":[{"name":"end-of-month","stores":["%s"],"date":"%s"}]}' \
        "$S" "$(date '+%Y-%m-%dT%H:%M:%S-04:00')" "$S" "$RANGE" > "$TRIG/eomdirect-$S.json"
    log "[$S] attempt $a: trigger dropped; waiting up to ${WAIT_SECS}s"
    dl=$(( $(date +%s) + WAIT_SECS )); status=""
    while [ "$(date +%s)" -lt "$dl" ]; do
      if [ -f "$RF" ]; then status=$(grep -oE '"status":[[:space:]]*"[a-z]+"' "$RF" | head -1); break; fi
      sleep 5
    done
    if echo "$status" | grep -qi success && [ -s "$CSV" ]; then
      log "[$S] attempt $a: SUCCESS ($status, csv=$(wc -c <"$CSV") bytes)"; ok=1; break
    fi
    log "[$S] attempt $a: FAILED (status='${status:-none}', csv=$([ -s "$CSV" ] && echo present || echo missing))"
  done
  [ $ok -eq 1 ] && SUMMARY="$SUMMARY $S=OK" || SUMMARY="$SUMMARY $S=FAIL"
done
log "=== EOM runner v3 complete ===$SUMMARY"
