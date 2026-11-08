#!/bin/bash
# cpu_guard.sh — native agent com.valleypawn.cpu-guard (every 5 min). Built 2026-11-07 after the Mac Studio
# ran at 100% CPU / 0% idle: Google Drive pinned at ~200% re-uploading files that change all day inside
# ~/Documents, on top of 10 live camera agents competing with Bravo/Windows/Claude at normal priority.
#  1. PRIORITY  — every run: any camera agent (door counter / conduct watch) not yet at nice >= 10 is reniced
#                 to 10, so the Mac always serves Bravo, Parallels and the desktop first. Survives restarts.
#  2. RUNAWAY   — any process above 150% CPU on 6 straight samples (30 min) that is not an expected heavy
#                 process -> one FAILURE_LEDGER row per process per day (Failure policy v3: no DM, no Slack).
#  3. SYNC HAZARD (hourly) — a file over 500 MB modified in the last 24 h anywhere under ~/Documents is being
#                 re-uploaded by Google Drive/iCloud on every change: retries bin/sync_relocate.sh (deferred
#                 moves), then one ledger row per path per week for anything still there.
# Status: fleet/CPU_GUARD.md. bash 3.2 compatible.
AGENT="cpu-guard"
. "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"; vp_lock "$AGENT" 20
ST="$OS_DIR/fleet/state/cpu_guard"; mkdir -p "$ST"; OUT="$OS_DIR/fleet/CPU_GUARD.md"; TODAY=$(date +%F)

# 1. priority for camera agents
reniced=""
for pid in $(pgrep -f "Store Traffic Counter|Store Conduct Watch|counter.py|watch.py" 2>/dev/null); do
  c=$(ps -o command= -p "$pid" 2>/dev/null)
  case "$c" in *python*counter.py*|*python*watch.py*) ;; *) continue ;; esac
  n=$(ps -o nice= -p "$pid" 2>/dev/null | tr -d ' ')
  if [ -n "$n" ] && [ "$n" -lt 10 ]; then renice -n 10 -p "$pid" >/dev/null 2>&1 && reniced="$reniced $pid"; fi
done
[ -n "$reniced" ] && vlog "reniced camera agents to 10:$reniced"

# 1b. one-time plist reload (Nice 10 + LowPriorityIO in fleet/*.plist) — only while NO camera agent is running
#     (after close / Sunday), so no store loses counting time. Flag: fleet/state/cpu_guard/pending_reload
if [ -f "$ST/pending_reload" ] && [ -z "$(pgrep -f 'counter.py|watch.py')" ]; then
  for l in $(cat "$ST/pending_reload"); do bash "$BIN/install_agent.sh" "$l" >> "$ST/reload.log" 2>&1; done
  vlog "reloaded camera agent plists with Nice 10"; mv "$ST/pending_reload" "$ST/reload_done-$TODAY"
fi

# 2. runaway CPU (expected heavy processes are ignored: camera agents, Parallels VM, WindowServer, kernel)
HOT="$HOME/.vp-studio/cpu-guard"; mkdir -p "$HOT"   # outside iCloud/Drive: renames there spawn "hot 2.txt" conflict copies
SNAP="$HOT/hot.txt"; NEW="$HOT/hot.new"; : > "$NEW"
ps -Ao pid=,pcpu=,comm= | awk '$2>150' | while read -r pid pcpu comm; do
  case "$comm" in *prl_vm_app*|*WindowServer*|*kernel_task*|*"Virtual Machine Service"*) continue ;; esac
  c=$(ps -o command= -p "$pid" 2>/dev/null); case "$c" in *counter.py*|*watch.py*) continue ;; esac
  prev=$(awk -v p="$pid" '$1==p{print $2}' "$SNAP" 2>/dev/null); k=$(( ${prev:-0} + 1 ))
  echo "$pid $k $pcpu $(basename "$comm" | tr ' ' '_')" >> "$NEW"
done
mv "$NEW" "$SNAP"
while read -r pid k pcpu name; do
  [ "$k" -ge 6 ] || continue
  flag="$ST/runaway-$TODAY-$name"; [ -f "$flag" ] && continue; touch "$flag"
  ledger "cpu-guard" "$name has been using about ${pcpu}% CPU for over 30 minutes and is slowing the Mac Studio." "no"
done < "$SNAP"

# 3. hourly: big files churning inside the Drive/iCloud-synced Documents folder
if [ "$(date +%M)" -lt 5 ] || [ "$1" = "--scan" ]; then
  bash "$BIN/sync_relocate.sh" > "$ST/relocate_last.txt" 2>&1
  find "$HOME/Documents" -xdev -type f -size +500M -mtime -1 -not -path "*/.tmp.driveupload/*" 2>/dev/null > "$ST/hazards.txt"
  while read -r f; do
    [ -n "$f" ] || continue
    key=$(echo "$f" | cksum | cut -d' ' -f1); flag="$ST/hazard-$key-$(date +%G%V)"; [ -f "$flag" ] && continue; touch "$flag"
    ledger "cpu-guard" "A large file ($(du -h "$f" | cut -f1 | tr -d ' ')) keeps changing inside Documents, so Google Drive re-uploads it all day: ${f#$HOME/}" "no"
  done < "$ST/hazards.txt"
fi

# status page
{
  echo "# CPU Guard — $(date '+%F %H:%M %Z')"
  echo; echo "Native agent com.valleypawn.cpu-guard (bin/cpu_guard.sh), every 5 min. See header of the script."
  echo; echo "## Load"; uptime | sed 's/^ *//'
  echo; echo "## Process states (R=running, U=waiting on disk)"; echo '```'; ps -Ao state= | cut -c1 | sort | uniq -c | tr '\n' ' '; echo
  ps -Ao state=,pid=,comm= | awk '$1 ~ /^[RU]/' | awk '{c[$3]++} END {for (k in c) print c[k], k}' | sort -rn | head -8; echo '```'
  echo; echo "## Top CPU right now"; echo '```'; ps -Ao pcpu,nice,pid,comm -r | head -12; echo '```'
  echo; echo "## Memory"; echo '```'; sysctl -n vm.swapusage; memory_pressure -Q 2>/dev/null | tail -1; echo '```'
  echo; echo "## Camera agents (nice should be 10)"; echo '```'
  for pid in $(pgrep -f "counter.py|watch.py"); do ps -o pid=,nice=,pcpu=,command= -p "$pid" | cut -c1-150; done; echo '```'
  echo; echo "## Hot processes (pid, consecutive 5-min samples >150%, %cpu, name)"; echo '```'; cat "$SNAP"; echo '```'
  echo; echo "## Large files changing inside Documents (last scan)"; echo '```'; cat "$ST/hazards.txt" 2>/dev/null; echo '```'
  echo; echo "## Last relocation pass"; echo '```'; cat "$ST/relocate_last.txt" 2>/dev/null | head -20; echo '```'
} > "$HOT/status.md" && cat "$HOT/status.md" > "$OUT"   # in-place write: no rename inside the synced folder
exit 0
