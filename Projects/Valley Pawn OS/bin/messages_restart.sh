#!/bin/bash
# messages_restart.sh (2026-11-20): self-heal when Messages.app hangs and every outbound text times out.
# Quits Messages (force after 10 s), relaunches it hidden, waits, prints whether it's running. Safe: Messages history is in chat.db.
osascript -e 'with timeout of 10 seconds' -e 'tell application "Messages" to quit' -e 'end timeout' >/dev/null 2>&1
sleep 5
pgrep -x Messages >/dev/null && { pkill -x Messages; sleep 3; }
pgrep -x Messages >/dev/null && { pkill -9 -x Messages; sleep 2; }
open -g -a Messages
sleep 12
pgrep -x Messages >/dev/null && echo "Messages running (pid $(pgrep -x Messages))" || echo "Messages NOT running"
