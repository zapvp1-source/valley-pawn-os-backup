#!/bin/bash
# _bravo_foreground_guard.sh -- additive, shared concurrency guard for Bravo POS access.
# Added 2026-07-07 to stop scheduled tasks from colliding on the single-instance
# Bravo Windows app. Does NOT modify bravo_watcher.ahk, the trigger/claim queue, or
# any existing pipeline cell -- this is a NEW, standalone utility other tasks opt into.
#
# Modes:
#   check              -> prints CLEAR or BUSY:<reason>; exit 0 (clear) / 1 (busy)
#   acquire <owner>    -> writes the foreground-owner flag for <owner>
#   release <owner>    -> clears the flag, but ONLY if currently held by <owner>
#
# State file (created on first use, safe to delete manually if ever stuck):
#   logs/_bravo_foreground_owner.txt   "<owner>\t<epoch_seconds>"
#
# NOTE (2026-07-07): triggers/claimed is a NEVER-CLEARED ARCHIVE in this pipeline
# (confirmed: oldest entries are weeks old), NOT a live in-flight queue. A naive
# "is claimed/ non-empty" test is therefore always true and useless as a busy
# signal. This script instead checks file RECENCY (mtime) in claimed/, the same
# way the pipeline already (correctly) checks results/*.result.json recency.
#
# Busy thresholds (tune here, not in callers):
PIPELINE_RECENT_MIN=6      # matches bravo-health-watchdog's existing results/ check
FOREGROUND_STALE_MIN=45    # generous ceiling for a full 5-store computer-use cycle

B="/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction"
OWNER_FILE="$B/logs/_bravo_foreground_owner.txt"
mkdir -p "$B/logs" 2>/dev/null

now_epoch() { date +%s; }

do_check() {
  if find "$B/triggers/claimed" -type f -mmin -"$PIPELINE_RECENT_MIN" 2>/dev/null | grep -q .; then
    echo "BUSY:pipeline-recent-claim"; exit 1
  fi
  if find "$B/results" -name '*.result.json' -mmin -"$PIPELINE_RECENT_MIN" 2>/dev/null | grep -q .; then
    echo "BUSY:pipeline-recent-result"; exit 1
  fi
  if [ -f "$OWNER_FILE" ]; then
    OWNER=$(cut -f1 "$OWNER_FILE" 2>/dev/null)
    TS=$(cut -f2 "$OWNER_FILE" 2>/dev/null)
    AGE_MIN=$(( ( $(now_epoch) - ${TS:-0} ) / 60 ))
    if [ "$AGE_MIN" -lt "$FOREGROUND_STALE_MIN" ]; then
      echo "BUSY:foreground-held-by-$OWNER"; exit 1
    else
      echo "STALE-CLEARING:foreground-flag-was-$OWNER-age-${AGE_MIN}m" >&2
      rm -f "$OWNER_FILE"
    fi
  fi
  echo "CLEAR"; exit 0
}

do_acquire() {
  OWNER="$1"
  [ -n "$OWNER" ] || { echo "acquire requires an owner name" >&2; exit 2; }
  printf "%s\t%s\n" "$OWNER" "$(now_epoch)" > "$OWNER_FILE"
  echo "ACQUIRED:$OWNER"
}

do_release() {
  OWNER="$1"
  [ -n "$OWNER" ] || { echo "release requires an owner name" >&2; exit 2; }
  if [ -f "$OWNER_FILE" ]; then
    CURRENT=$(cut -f1 "$OWNER_FILE" 2>/dev/null)
    if [ "$CURRENT" = "$OWNER" ]; then
      rm -f "$OWNER_FILE"
      echo "RELEASED:$OWNER"
    else
      echo "SKIPPED:flag-held-by-$CURRENT-not-$OWNER" >&2
    fi
  else
    echo "NOOP:no-flag-set"
  fi
}

case "$1" in
  check) do_check ;;
  acquire) do_acquire "$2" ;;
  release) do_release "$2" ;;
  *) echo "usage: $0 {check|acquire <owner>|release <owner>}" >&2; exit 2 ;;
esac
