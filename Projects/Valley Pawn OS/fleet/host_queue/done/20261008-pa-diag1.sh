#!/bin/bash
# Read-only diagnostics for the Preston assistant (no changes).
echo "== date"; date
echo "== preston-watch launchctl"; launchctl list | grep -i preston
echo "== preston-watch log tail"; tail -n 25 "$HOME/Library/Logs/valleypawn/preston-watch.log" 2>&1
echo "== cutoff file"; cat "$HOME/preston_claude_last_ts.txt" 2>&1
echo "== pending file"; cat "$HOME/preston_claude_pending.json" 2>&1 | head -40
echo "== state"; cat "$HOME/.preston_watch_state.json" 2>&1 | head -c 1500; echo
echo "== plist"; cat "$HOME/Library/LaunchAgents/com.valleypawn.preston-watch.plist" 2>&1
echo "== claude cli"; for p in "$HOME/.local/bin/claude" "$HOME/.claude/local/claude" /opt/homebrew/bin/claude /usr/local/bin/claude; do [ -e "$p" ] && { echo "FOUND $p"; "$p" --version 2>&1 | head -2; }; done
which claude 2>&1; ls "$HOME/.claude" 2>&1 | head -30
echo "== anthropic key present"; security find-generic-password -s vp-agent-anthropic-key -w >/dev/null 2>&1 && echo yes || echo no
echo "== slack bot token present"; security find-generic-password -s vp-ops-slack-bot-token -a "$(whoami)" -w 2>/dev/null | cut -c1-5
echo "== node/npm"; which node npm 2>&1; node --version 2>&1
echo "== vp-runner"; ls -la "$HOME/bin" 2>&1 | head -20
echo "== old task skill"; ls -la "$HOME/Documents/Claude/Scheduled/preston-interactive-assistant" 2>&1; wc -c "$HOME/Documents/Claude/Scheduled/preston-interactive-assistant/SKILL.md" 2>&1
cp "$HOME/Documents/Claude/Scheduled/preston-interactive-assistant/SKILL.md" "$HOME/Documents/Claude/Projects/Valley Pawn OS/fleet/host_queue/done/pia_SKILL_copy.md" 2>&1
cp "$HOME/Documents/Claude/Scheduled/preston-claude-evening-check/SKILL.md" "$HOME/Documents/Claude/Projects/Valley Pawn OS/fleet/host_queue/done/pce_SKILL_copy.md" 2>&1
echo "== done"
