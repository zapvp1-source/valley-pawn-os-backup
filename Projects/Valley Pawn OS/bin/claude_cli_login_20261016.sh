#!/bin/bash
# 2026-10-16 (Joshua approved): start the one-time Claude Code CLI sign-in on the Mac host in the background.
# It opens claude.ai in the default browser; Joshua clicks Authorize once. Log: ~/Library/Logs/valleypawn/claude-cli-login.log
export PATH="$HOME/.local/bin:$PATH"
L="$HOME/Library/Logs/valleypawn/claude-cli-login.log"
claude auth --help 2>&1 | head -20 > "$L"
nohup perl -e 'alarm 900; exec @ARGV' claude auth login </dev/null >>"$L" 2>&1 &
sleep 20
cat "$L"
