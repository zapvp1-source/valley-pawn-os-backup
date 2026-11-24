#!/bin/zsh
# Apply a Reminders plan JSON (preview -> y/N -> apply -> read-back -> log).
# Usage: reminders_apply.sh <plan.json> [--dry-run]
# Run from Terminal.app (it holds the Reminders permission). Rebuilds the binary if the source is newer.
BIN="$HOME/Documents/Claude/Projects/Life OS/bin"
if [[ ! -x "$BIN/reminders_apply" || "$BIN/reminders_apply.swift" -nt "$BIN/reminders_apply" ]]; then
  swiftc -O -o "$BIN/reminders_apply" "$BIN/reminders_apply.swift" || { echo "Build failed."; exit 1; }
fi
exec "$BIN/reminders_apply" "$@"
