#!/bin/bash
# HOST JOB (runs once via bin/host_queue_run.sh on the host, outside Claude).
# 2026-09-16 — Scheduled-task sidebar empty again (registry not loaded by the app since ~10:30 AM).
# 1) diagnostics that an interactive session cannot see  2) fix the broken claude-keepalive agent
# 3) install the native registry-guard agent  4) run the guard once now with a forced relaunch.
set +e
U=$(id -u)
OS="$HOME/Documents/Claude/Projects/Valley Pawn OS"
BIN="$OS/bin"; FLEET="$OS/fleet"; LA="$HOME/Library/LaunchAgents"
BK="$FLEET/_backups"; mkdir -p "$BK" "$HOME/Library/Logs/valleypawn"
echo "=== bootstrap start $(date) as $(whoami) uid=$U ==="

echo; echo "--- exec bits ---"
chmod +x "$BIN/host_queue_run.sh" "$BIN/host_queue_spawn.sh" "$BIN/registry_guard_run.sh" "$BIN/registry_guard.py" "$BIN/claude_keepalive.sh" "$BIN/preston_watch_run.sh" 2>&1
ls -la "$BIN/host_queue_run.sh" "$BIN/registry_guard_run.sh" "$BIN/registry_guard.py" "$BIN/claude_keepalive.sh"

echo; echo "--- Claude app ---"
defaults read /Applications/Claude.app/Contents/Info.plist CFBundleShortVersionString 2>&1
ps -axo pid=,lstart=,comm= | grep -F '/Applications/Claude.app/Contents/MacOS/Claude' | grep -v grep
echo; echo "--- vp-runner (head) ---"; head -c 1200 "$HOME/bin/vp-runner" 2>&1 | strings | head -20

echo; echo "--- registries ---"
for f in "$HOME/Library/Application Support/Claude/local-agent-mode-sessions"/*/*/scheduled-tasks.json*; do
  echo "$(stat -f '%Sm %z' -t '%F %T' "$f")  $f"
done
/usr/bin/python3 - <<'PY'
import json,glob,os
for p in sorted(glob.glob(os.path.expanduser('~/Library/Application Support/Claude/local-agent-mode-sessions/*/*/scheduled-tasks.json'))):
    try:
        d=json.load(open(p)); st=d.get('scheduledTasks',[])
        nulls=[(i,t.get('id'),k) for i,t in enumerate(st) for k,v in t.items() if v is None]
        print('OK  ',len(st),'tasks',sum(1 for t in st if t.get('enabled')),'enabled','nulls=',nulls[:10], os.path.basename(os.path.dirname(os.path.dirname(p))),'/',os.path.basename(os.path.dirname(p)))
        print('     top-level keys:',list(d.keys())[:10])
    except Exception as e:
        print('FAIL',p,e)
PY

echo; echo "--- app log: ZodError / scheduler lines (last 40 of each) ---"
for l in "$HOME/Library/Logs/Claude/main.log" "$HOME/Library/Logs/Claude/main1.log"; do
  [ -f "$l" ] || continue; echo "## $l ($(stat -f %z "$l") bytes)"
  grep -n "ZodError" "$l" | tail -20 | cut -c1-400
  grep -n -i "scheduled-tasks\|scheduler" "$l" | tail -40 | cut -c1-300
done
echo; echo "--- app log: last 25 lines ---"; tail -25 "$HOME/Library/Logs/Claude/main.log" | cut -c1-300

echo; echo "--- launchd agents (valleypawn) ---"
launchctl list | grep valleypawn
echo; echo "--- keepalive plist (current) ---"; plutil -p "$LA/com.valleypawn.claude-keepalive.plist" 2>&1
echo; echo "--- perf-guard plist (known-good reference) ---"; plutil -p "$LA/com.valleypawn.perf-guard.plist" 2>&1
echo; echo "--- keepalive log tail ---"; tail -5 "$BIN/claude_keepalive.log" 2>&1

echo; echo "--- FIX: claude-keepalive exit-126 (route through vp-runner like every healthy agent) ---"
KP="$LA/com.valleypawn.claude-keepalive.plist"
if [ -f "$KP" ]; then
  if ! grep -q "vp-runner" "$KP"; then
    cp "$KP" "$BK/com.valleypawn.claude-keepalive.plist.bak-$(date +%Y%m%d-%H%M%S)"
    plutil -replace ProgramArguments -json "[\"$HOME/bin/vp-runner\",\"$BIN/claude_keepalive.sh\"]" "$KP" && echo "ProgramArguments rewritten"
    plutil -replace RunAtLoad -bool true "$KP"
    launchctl bootout gui/$U/com.valleypawn.claude-keepalive 2>&1; sleep 1
    launchctl bootstrap gui/$U "$KP" 2>&1 && echo "keepalive re-bootstrapped"
    sleep 3; launchctl kickstart gui/$U/com.valleypawn.claude-keepalive 2>&1; sleep 3
    echo "keepalive last exit: $(launchctl list | grep claude-keepalive)"
    tail -2 "$BIN/claude_keepalive.log"
  else
    echo "keepalive already uses vp-runner; exit-126 cause is elsewhere:"; plutil -p "$KP"
  fi
else
  echo "no keepalive plist found at $KP"
fi
cp "$KP" "$FLEET/com.valleypawn.claude-keepalive.plist" 2>/dev/null

echo; echo "--- RUN registry guard once now (forced relaunch; 6-min wait if a session is active) ---"
touch "$FLEET/host_queue/.registry_guard_force_relaunch"
/usr/bin/python3 "$BIN/registry_guard.py" --diag 2>&1
echo "guard rc=$?"

echo; echo "--- INSTALL registry-guard agent (every 5 min) ---"
cp "$FLEET/com.valleypawn.registry-guard.plist" "$LA/com.valleypawn.registry-guard.plist"
launchctl bootout gui/$U/com.valleypawn.registry-guard 2>/dev/null
launchctl bootstrap gui/$U "$LA/com.valleypawn.registry-guard.plist" 2>&1 && echo "registry-guard bootstrapped"
sleep 20
launchctl list | grep -E "registry-guard|claude-keepalive|preston-watch"
echo; echo "--- post-state ---"
ps -axo pid=,lstart=,comm= | grep -F '/Applications/Claude.app/Contents/MacOS/Claude' | grep -v grep
tail -3 "$HOME/Library/Logs/valleypawn/registry-guard.log"
echo "=== bootstrap done $(date) ==="
