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
$NICE /usr/bin/python3 usearch.py mail
$NICE /usr/bin/python3 usearch.py files
$NICE /usr/bin/python3 msgindex.py
$NICE /usr/bin/python3 notesindex.py
$NICE /usr/bin/python3 remindersindex.py
$NICE /usr/bin/python3 usearch.py gdrive
$NICE /usr/bin/python3 photosindex.py
$NICE /usr/bin/python3 usearch.py stats > stats.txt
echo "=== done $(date) ==="
