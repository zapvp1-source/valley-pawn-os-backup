#!/bin/bash
# Read-only probe 6 (2026-10-16): headless run with JSON output, stdin closed, stderr captured.
B=$(find "$HOME/Library/Application Support/Claude/claude-code" -maxdepth 5 -type f -perm -u+x -path '*MacOS/claude' 2>/dev/null | sort -V | tail -1)
cd /tmp
perl -e 'alarm 150; exec @ARGV' "$B" -p "Reply with exactly: PONG" --output-format json </dev/null >/tmp/vp_cc_probe.out 2>/tmp/vp_cc_probe.err
echo "rc=$?"
echo "--out"; head -c 1500 /tmp/vp_cc_probe.out; echo; echo "--err"; head -c 1500 /tmp/vp_cc_probe.err
