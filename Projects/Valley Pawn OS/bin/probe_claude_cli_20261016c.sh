#!/bin/bash
# Read-only probe 3 (2026-10-16): list the desktop app's bundled Claude Code folder and try it headless.
ls -la "$HOME/Library/Application Support/Claude/claude-code" | head
find "$HOME/Library/Application Support/Claude/claude-code" -maxdepth 4 -type f -size +10M 2>/dev/null | head -5
B=$(find "$HOME/Library/Application Support/Claude/claude-code" -maxdepth 4 -type f -size +10M -perm -u+x 2>/dev/null | sort -V | tail -1)
echo "bin: $B"
[ -n "$B" ] && file "$B"
[ -n "$B" ] && "$B" --version 2>&1 | head -2
[ -n "$B" ] && cd /tmp && timeout 120 "$B" -p "Reply with exactly: PONG" --output-format text 2>&1 | head -5
echo "rc=$?"
