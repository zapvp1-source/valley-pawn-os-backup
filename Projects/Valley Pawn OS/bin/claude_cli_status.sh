#!/bin/bash
# read-only (2026-11-20): Claude Code CLI sign-in status + whether the sign-in window is still running
C="$HOME/.local/bin/claude"
echo "== auth status"; perl -e 'alarm 60; exec @ARGV' "$C" auth status </dev/null 2>&1 | head -15
echo "== login processes"; pgrep -fl "claude auth login" || echo none
echo "== ping"; perl -e 'alarm 90; exec @ARGV' "$C" -p "Reply with exactly: PONG" --output-format text </dev/null 2>&1 | tail -3
