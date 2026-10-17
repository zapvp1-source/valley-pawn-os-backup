#!/bin/bash
# Read-only probe 5 (2026-10-16): does the desktop-bundled Claude Code run headless and signed in on this Mac?
B=$(find "$HOME/Library/Application Support/Claude/claude-code" -maxdepth 5 -type f -perm -u+x -path '*MacOS/claude' 2>/dev/null | sort -V | tail -1)
cd /tmp
perl -e 'alarm 150; exec @ARGV' "$B" -p "Reply with exactly: PONG" --output-format text 2>&1 | head -8
echo "rc=${PIPESTATUS[0]}"
