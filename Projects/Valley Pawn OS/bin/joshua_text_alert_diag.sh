#!/bin/bash
# read-only diagnostics for com.valleypawn.joshua-text-alert (2026-11-20)
L="$HOME/Library/Logs/valleypawn"
launchctl list | grep -F joshua-text-alert
echo "--- alert log"; tail -15 "$L/joshua-text-alert.log"
echo "--- err"; tail -15 "$L/joshua-text-alert.err.log"
echo "--- runner"; tail -10 "$L/joshua-reply-runner.log" 2>/dev/null
echo "--- state"; /usr/bin/python3 -c "import json,os;d=json.load(open(os.path.expanduser('~/.joshua_text_alert_state.json')));print('reply_rowid',d.get('reply_rowid'),'alerts',len(d.get('alerts',[])))"
