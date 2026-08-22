#!/bin/bash
# refresh_hardened.sh — self-healing wrapper around refresh.sh (ADDITIVE — never edits refresh.sh).
#
# Why (2026-08-21): a refresh run died silently mid-files-step (parent killed, workers
# threw BrokenPipe, no error of its own, no done marker). An immediate identical retry
# succeeded end-to-end. Lesson: transient death is survivable IF something retries and
# IF the stale lock left by a SIGKILL'd run (whose EXIT trap never fired) gets reclaimed.
# This wrapper bakes both in so the nightly task self-heals instead of reporting failure.
#
# Behavior:
#   - Up to 3 attempts of refresh.sh, 60s apart.
#   - Before each attempt: if the lockdir exists but NO refresh/index process is running,
#     the lock is stale (crashed run) — reclaim it instead of waiting 6h.
#   - Success = the literal "=== done" marker in that attempt's output (Rule 12: verify
#     against output, never exit codes).
#   - Exit 0 on success, exit 1 only after all attempts fail.
# Logs: appends everything to refresh_hardened.log next to this script.

P="$HOME/Documents/Claude/Projects/Unified Search"
LOG="$P/refresh_hardened.log"
LOCK="$P/.refresh.lockdir"
ATTEMPTS=3

cd "$P" || exit 1

for i in $(seq 1 $ATTEMPTS); do
  # Reclaim a stale lock: lockdir present but no live refresh/index process anywhere.
  if [ -d "$LOCK" ] && ! pgrep -f 'refresh\.sh|usearch\.py|msgindex\.py|notesindex\.py|remindersindex\.py|photosindex\.py' >/dev/null 2>&1; then
    echo "=== hardened: reclaiming stale lock before attempt $i $(date) ===" >> "$LOG"
    rm -rf "$LOCK"
  fi

  # If a live refresh IS running (another chain), don't stack — wait up to 30 min then re-check.
  if [ -d "$LOCK" ]; then
    echo "=== hardened: live refresh already running, waiting $(date) ===" >> "$LOG"
    for w in $(seq 1 60); do
      sleep 30
      [ ! -d "$LOCK" ] && break
    done
  fi

  ATT="$P/.refresh_attempt.log"
  : > "$ATT"
  echo "=== hardened attempt $i/$ATTEMPTS $(date) ===" >> "$LOG"
  bash "$P/refresh.sh" >> "$ATT" 2>&1
  cat "$ATT" >> "$LOG"

  if grep -q '=== done' "$ATT"; then
    echo "=== hardened success on attempt $i $(date) ===" >> "$LOG"
    rm -f "$ATT"
    exit 0
  fi
  echo "=== hardened: attempt $i missing done marker — retrying in 60s $(date) ===" >> "$LOG"
  sleep 60
done

echo "=== hardened FAILED after $ATTEMPTS attempts $(date) ===" >> "$LOG"
exit 1
