#!/bin/bash
# 2026-10-16 (Joshua approved): install the official Claude Code CLI on the Mac host (user-level, ~/.local/bin)
# so preston_watch can answer Preston's requests within ~2 min instead of waiting on the hourly cloud task.
# Idempotent: skips the download if already installed. Then runs one headless test.
export PATH="$HOME/.local/bin:$PATH"
if ! command -v claude >/dev/null 2>&1; then
  curl -fsSL https://claude.ai/install.sh -o /tmp/vp_claude_install.sh && bash /tmp/vp_claude_install.sh 2>&1 | tail -15
fi
echo "which: $(command -v claude)"
claude --version 2>&1 | head -2
cd /tmp
perl -e 'alarm 150; exec @ARGV' claude -p "Reply with exactly: PONG" --output-format text </dev/null >/tmp/vp_cc_t.out 2>/tmp/vp_cc_t.err
echo "rc=$?"; echo "--out"; head -c 800 /tmp/vp_cc_t.out; echo; echo "--err"; head -c 800 /tmp/vp_cc_t.err
