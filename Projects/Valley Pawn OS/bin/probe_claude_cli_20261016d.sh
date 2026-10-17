#!/bin/bash
# Read-only probe 4 (2026-10-16): locate the desktop-bundled Claude Code executable and test a headless run.
find "$HOME/Library/Application Support/Claude/claude-code/2.1.299" -maxdepth 6 2>/dev/null | head -20
B=$(find "$HOME/Library/Application Support/Claude/claude-code/2.1.299" -maxdepth 6 -type f -perm -u+x -name 'claude*' 2>/dev/null | head -1)
echo "bin: $B"
[ -n "$B" ] && file "$B"
[ -n "$B" ] && "$B" --version 2>&1 | head -2
[ -n "$B" ] && cd /tmp && timeout 120 "$B" -p "Reply with exactly: PONG" --output-format text 2>&1 | head -5
echo "rc=$?"
