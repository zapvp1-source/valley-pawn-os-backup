#!/bin/bash
# append_line.sh <file under ~/Documents/Claude/Projects> "<line>"  — append-only, path-restricted host primitive.
F="$1"; L="$2"; ROOT="$HOME/Documents/Claude/Projects"
case "$F" in "$ROOT"/*) ;; *) echo "REFUSED: $F not under $ROOT"; exit 2;; esac
[ -n "$L" ] || { echo "REFUSED: empty line"; exit 2; }
printf '%s\n' "$L" >> "$F" && echo "appended to ${F#$ROOT/}"
