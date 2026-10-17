#!/bin/bash
# Read-only probe 7 (2026-10-16): why the bundled Claude Code exits silently.
B=$(find "$HOME/Library/Application Support/Claude/claude-code" -maxdepth 5 -type f -perm -u+x -path '*MacOS/claude' 2>/dev/null | sort -V | tail -1)
cd /tmp
echo "== help"; perl -e 'alarm 30; exec @ARGV' "$B" --help </dev/null 2>&1 | head -15; echo "rc=${PIPESTATUS[0]}"
echo "== auth"; perl -e 'alarm 30; exec @ARGV' "$B" auth status </dev/null 2>&1 | head -10
echo "== verbose run"; perl -e 'alarm 120; exec @ARGV' "$B" -p "Reply with exactly: PONG" --verbose --output-format stream-json </dev/null 2>&1 | head -c 2500; echo; echo "rc=${PIPESTATUS[0]}"
echo "== env"; echo "USER=$USER HOME=$HOME TERM=$TERM"
