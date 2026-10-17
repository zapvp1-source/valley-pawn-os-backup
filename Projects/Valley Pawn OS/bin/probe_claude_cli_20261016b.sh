#!/bin/bash
# Read-only probe 2 (2026-10-16): find a Claude Code binary bundled with the desktop app, and whether it is signed in.
for d in "$HOME/Library/Application Support/Claude/claude-code" "$HOME/Library/Application Support/Claude/claude-code-vm" /Applications/Claude.app/Contents/Resources; do
  [ -d "$d" ] && { echo "dir: $d"; find "$d" -maxdepth 3 -name 'claude*' -type f -perm -u+x 2>/dev/null | head -5; }
done
security find-generic-password -s "Claude Code-credentials" >/dev/null 2>&1 && echo "cc credentials: present"
B=$(find "$HOME/Library/Application Support/Claude/claude-code" -maxdepth 3 -name claude -type f -perm -u+x 2>/dev/null | sort | tail -1)
echo "bin: $B"
[ -n "$B" ] && "$B" --version 2>&1 | head -2
[ -n "$B" ] && cd /tmp && timeout 90 "$B" -p "Reply with exactly: PONG" --output-format text 2>&1 | head -5
