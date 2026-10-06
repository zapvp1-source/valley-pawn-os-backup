#!/bin/bash
# tail_any.sh <path under ~/Library/Logs/valleypawn> [lines] — READ-ONLY, path-restricted log reader.
F="$1"; N="${2:-40}"; ROOT="$HOME/Library/Logs/valleypawn"
case "$F" in "$ROOT"/*) ;; *) F="$ROOT/$F";; esac
case "$F" in "$ROOT"/*) ;; *) echo "REFUSED"; exit 2;; esac
echo "--- $F (last $N) ---"; tail -n "$N" "$F" 2>&1
