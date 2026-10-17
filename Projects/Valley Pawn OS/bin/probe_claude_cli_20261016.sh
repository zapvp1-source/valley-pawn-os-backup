#!/bin/bash
# Read-only probe (2026-10-16): is a Claude Code CLI installed on the Mac host? Used to decide whether
# preston_watch can answer Preston's requests locally instead of waiting for the hourly cloud task.
export PATH="$HOME/.local/bin:$HOME/.claude/local:/opt/homebrew/bin:/usr/local/bin:$PATH"
echo "which: $(command -v claude)"
for p in "$HOME/.local/bin/claude" "$HOME/.claude/local/claude" /opt/homebrew/bin/claude /usr/local/bin/claude "$HOME/.npm-global/bin/claude"; do [ -e "$p" ] && echo "exists: $p"; done
command -v claude >/dev/null && claude --version 2>&1 | head -2
ls "$HOME/.claude" 2>/dev/null | head -20
echo "node: $(command -v node) $(node --version 2>/dev/null)"
security find-generic-password -s vp-ops-slack-bot-token >/dev/null 2>&1 && echo "slack bot token: present"
security find-generic-password -s anthropic-api-key >/dev/null 2>&1 && echo "anthropic key item: present"
