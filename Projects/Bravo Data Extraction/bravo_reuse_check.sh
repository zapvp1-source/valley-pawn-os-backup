#!/bin/bash
# bravo_reuse_check.sh -- shared "check-before-trigger" helper for the Bravo Data
# Extraction pipeline. NEW, additive file (2026-08-02). Does not modify any
# existing AHK handler, dispatch table, or hardened scheduled task.
#
# PURPOSE: before any task drops a trigger JSON for cell X / store Y / date Z,
# it should check whether output/ already has a fresh (same-day) result for
# that exact cell+store+date and reuse it instead of re-triggering Bravo.
# This script does that check.
#
# Usage:
#   bravo_reuse_check.sh <cell-name> <date-or-window-token> <ext> <store1> [store2] ...
#
# <date-or-window-token> must match how the pipeline names the output file
# for that cell (e.g. a single date YYYY-MM-DD for most cells, or the END
# date for end-of-month since its filename only encodes the end date).
#
# Prints one line per store:
#   <STORE> FRESH <path>     file exists, modified today, >500 bytes
#   <STORE> STALE <path>     file exists but is old and/or undersized
#   <STORE> MISSING          no matching file at all
#
# Exit code 0  = ALL requested stores are FRESH -> safe to SKIP triggering Bravo,
#                just read the existing files.
# Exit code 1  = at least one store needs a fresh pull -> fall through to the
#                normal drop-trigger-and-poll flow (only the STALE/MISSING
#                stores need it, if the cell supports partial per-store
#                triggers; otherwise trigger for all requested stores).

OUTPUT_DIR="/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output"
CELL="$1"; DATE_TOKEN="$2"; EXT="$3"; shift 3
TODAY=$(date +%Y-%m-%d)
ALL_FRESH=1

if [ -z "$CELL" ] || [ -z "$DATE_TOKEN" ] || [ -z "$EXT" ] || [ "$#" -eq 0 ]; then
  echo "Usage: bravo_reuse_check.sh <cell-name> <date-token> <ext> <store1> [store2] ..." >&2
  exit 2
fi

for STORE in "$@"; do
  FILE=$(ls -t "$OUTPUT_DIR"/*"${DATE_TOKEN}"*"${STORE}"*"${CELL}"*."${EXT}" 2>/dev/null | head -1)
  if [ -z "$FILE" ]; then
    echo "$STORE MISSING"
    ALL_FRESH=0
    continue
  fi
  MTIME_DATE=$(date -r "$FILE" +%Y-%m-%d 2>/dev/null)
  SIZE=$(stat -f%z "$FILE" 2>/dev/null || stat -c%s "$FILE" 2>/dev/null || echo 0)
  if [ "$MTIME_DATE" = "$TODAY" ] && [ "$SIZE" -gt 500 ]; then
    echo "$STORE FRESH $FILE"
  else
    echo "$STORE STALE $FILE (mtime=$MTIME_DATE size=$SIZE)"
    ALL_FRESH=0
  fi
done

exit $((1 - ALL_FRESH))
