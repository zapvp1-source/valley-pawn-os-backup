#!/bin/bash
# =============================================================================
# bravo_ensure_healthy.sh  —  single-flight guard around the Bravo health gate
# -----------------------------------------------------------------------------
# Purpose: the ONE line every daily Bravo task runs FIRST. Guarantees Bravo is
# healthy before a pull, WITHOUT ever running two gates at once (the 2026-06-19
# "Bravo is already running" collision). Two guards:
#
#   1. FRESHNESS short-circuit — if the gate already reported PASS within the
#      last $FRESH_SECS seconds, return instantly. Clustered morning tasks reuse
#      one healthy state instead of each kicking a gate.
#   2. LOCK (single-flight) — only one gate ever runs at a time. A second caller
#      WAITS for the in-flight gate to finish (then re-checks freshness) instead
#      of launching a rival gate.
#
# ADDITIVE (Rule #1): NET-NEW file. Only *invokes* bravo_health_gate.sh; edits
# nothing. Tasks gain exactly one line: `bash bravo_ensure_healthy.sh <STORE>`.
#
# USAGE (blocks until healthy or fails):
#   bash bravo_ensure_healthy.sh CUL
#   echo $?   # 0 = Bravo healthy (PASS)   1 = FAIL (needs Joshua)
#
# Exit codes: 0 = PASS (Bravo verified healthy).  1 = FAIL.
# =============================================================================

set -u

ROOT="/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction"
GATE="$ROOT/bravo_health_gate.sh"
LOGDIR="$ROOT/logs"
STATUS="$LOGDIR/_health_gate_status.txt"
LOCKDIR="$LOGDIR/_health_gate.lock"
WLOG="$LOGDIR/_ensure_healthy.log"

TARGET="${1:-CUL}"

FRESH_SECS=300      # a PASS newer than this is reused (no re-run)
LOCK_WAIT_SECS=420  # how long a waiting caller will wait for an in-flight gate
STALE_LOCK_SECS=600 # a lock older than this is presumed dead and stolen

mkdir -p "$LOGDIR"
ts()  { date '+%Y-%m-%d %H:%M:%S'; }
log() { echo "$(ts) | ensure[$TARGET] | $*" | tee -a "$WLOG" >&2; }

# --- mtime helper (macOS stat) ---
mtime() { stat -f %m "$1" 2>/dev/null || echo 0; }
age()   { echo $(( $(date +%s) - $(mtime "$1") )); }

# --- freshness check: PASS status file, recently written ---------------------
is_fresh_pass() {
  [ -f "$STATUS" ] || return 1
  grep -qi '^PASS' "$STATUS" || return 1
  [ "$(age "$STATUS")" -lt "$FRESH_SECS" ] || return 1
  return 0
}

if is_fresh_pass; then
  log "fresh PASS ($(age "$STATUS")s old) -> reuse, skip gate"
  exit 0
fi

# --- acquire single-flight lock (atomic mkdir) -------------------------------
acquire() { mkdir "$LOCKDIR" 2>/dev/null; }   # succeeds only if it did not exist

waited=0
while ! acquire; do
  # someone else holds the lock. steal it if it is stale (dead gate).
  if [ -d "$LOCKDIR" ] && [ "$(age "$LOCKDIR")" -ge "$STALE_LOCK_SECS" ]; then
    log "lock is stale ($(age "$LOCKDIR")s) -> stealing"
    rmdir "$LOCKDIR" 2>/dev/null
    continue
  fi
  # in-flight gate: wait for it, then reuse its result if it passed
  if is_fresh_pass; then
    log "in-flight gate finished PASS while waiting -> reuse"
    exit 0
  fi
  if [ "$waited" -ge "$LOCK_WAIT_SECS" ]; then
    log "waited ${waited}s for in-flight gate, no PASS -> giving up, will FAIL"
    exit 1
  fi
  sleep 5; waited=$((waited+5))
done

# we hold the lock. ensure it is always released.
trap 'rmdir "$LOCKDIR" 2>/dev/null' EXIT INT TERM
log "lock acquired"

# double-checked locking: a gate may have finished PASS between our first
# freshness check and acquiring the lock. if so, skip the redundant gate.
if is_fresh_pass; then
  log "fresh PASS after acquiring lock ($(age "$STATUS")s) -> skip gate"
  exit 0
fi

log "running health gate"
bash "$GATE" "$TARGET"
RC=$?

if [ "$RC" = "0" ] && grep -qi '^PASS' "$STATUS" 2>/dev/null; then
  log "gate PASS"
  exit 0
fi
log "gate FAIL (rc=$RC, status=$(cat "$STATUS" 2>/dev/null))"
exit 1
