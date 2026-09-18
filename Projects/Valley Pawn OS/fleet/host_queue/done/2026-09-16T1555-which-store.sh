#!/bin/bash
AS="$HOME/Library/Application Support/Claude"
for p in "$AS/local-agent-mode-sessions/823f6874-6252-4031-ae4e-a3c22d37598e/f6b75d02-cca9-4943-ad6e-88390a3f201d/scheduled-tasks.json" "$AS/claude-code-sessions/823f6874-6252-4031-ae4e-a3c22d37598e/f6b75d02-cca9-4943-ad6e-88390a3f201d/scheduled-tasks.json"; do
  echo "## $(stat -f '%Sm %z' -t '%F %T' "$p")  ${p#$AS/}"
  /usr/bin/python3 -c "import json;d=json.load(open('$p'));print('   tasks:',[t.get('id') for t in d['scheduledTasks']])"
done
grep -n "ScheduledTasks\]" "$HOME/Library/Logs/Claude/main.log" | tail -12 | cut -c1-220
