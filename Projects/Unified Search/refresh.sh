#!/bin/bash
P="$HOME/Documents/Claude/Projects/Unified Search"
cd "$P" || exit 1

# --- Single-run lock (added 2026-08-21: stacked refresh chains drove load avg >170).
# mkdir is atomic; a lock older than 6h is considered stale (crashed run) and reclaimed.
LOCK="$P/.refresh.lockdir"
if ! mkdir "$LOCK" 2>/dev/null; then
  if [ -n "$(find "$LOCK" -maxdepth 0 -mmin +360 2>/dev/null)" ]; then
    echo "reclaiming stale lock ($(date))"
    rm -rf "$LOCK" && mkdir "$LOCK" || exit 0
  else
    echo "refresh already running — exiting ($(date))"
    exit 0
  fi
fi
trap 'rm -rf "$LOCK"' EXIT

# --- Keep the whole chain polite: low CPU priority, capped worker pools.
export USEARCH_WORKERS="${USEARCH_WORKERS:-4}"
NICE="/usr/bin/nice -n 10"

echo "=== refresh $(date) ==="

# Fixed 2026-09-08: this used to run every step unconditionally and print
# "=== done ===" no matter what, so a step that crashed (e.g. photosindex.py's
# osxphotos timeout on 9/2 and 9/4) still got reported as success by
# refresh_hardened.sh, which only checks for the literal "=== done" marker.
# Now each step's exit code is checked; the final marker only says "=== done ==="
# (the string the wrapper greps for) when every step actually succeeded. On a
# partial failure it prints a marker WITHOUT that substring, so the hardened
# wrapper correctly treats the run as failed and retries / reports it.
FAILED_STEPS=""
run_step() {
  local label="$1"; shift
  $NICE "$@"
  local rc=$?
  if [ $rc -ne 0 ]; then
    echo "=== STEP FAILED: $label (exit $rc) $(date) ==="
    FAILED_STEPS="$FAILED_STEPS $label"
  fi
}

run_step "usearch.py mail" /usr/bin/python3 usearch.py mail
run_step "usearch.py files" /usr/bin/python3 usearch.py files
run_step "msgindex.py" /usr/bin/python3 msgindex.py
run_step "notesindex.py" /usr/bin/python3 notesindex.py
run_step "remindersindex.py" /usr/bin/python3 remindersindex.py
run_step "usearch.py gdrive" /usr/bin/python3 usearch.py gdrive
run_step "photosindex.py" /usr/bin/python3 photosindex.py
run_step "usearch.py stats" /usr/bin/python3 usearch.py stats > stats.txt

if [ -n "$FAILED_STEPS" ]; then
  echo "=== refresh FINISHED WITH FAILURES ($FAILED_STEPS) $(date) ==="
else
  echo "=== done $(date) ==="
fi
