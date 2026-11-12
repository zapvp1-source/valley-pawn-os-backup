#!/bin/bash
# mem_guard.sh — native Layer-0 MEMORY guard (added 2026-11-11, stopgap until the
# M5 Ultra 96GB Mac Studio arrives mid-December 2026).
#
# WHY: 2026-11-10 the M1 Max (32GB) sat at 28GB used + 15GB swap + 16GB compressed.
# Everything (Claude desktop app most of all) crawled. perf-guard/cpu-guard handle
# runaway CPU; nothing handled memory. This does.
#
# MODES (env MEM_GUARD_MODE, set by the launchd plist):
#   watch   — every 15 min (com.valleypawn.mem-guard). Escalates only as needed:
#             T1 swap>=8GB or pressure warn : quit idle non-essential apps (never the
#                                              front app, only when Joshua idle >=20 min)
#             T2 swap>=11GB or pressure crit: restart Google Drive (max once / 4h)
#             T3 swap>=14GB two checks in a row, Joshua idle >=20 min, Claude not
#                restarted in last 4h        : restart the Claude desktop app
#   nightly — 3:50 AM (com.valleypawn.mem-guard-nightly), after the 3:30 Chrome
#             restart: T1 + T2 + T3 unconditionally (still skips T3 if Joshua active).
#
# NEVER touches: Parallels / Windows 11 (Bravo), Chrome (chrome-tab-hygiene +
# nightly restart own it), Slack, Mail, Messages (iMessage sender), Calendar,
# Notes, Reminders, Excel, Timing, Python automations. No Slack/DM — log only
# (Joshua's standing rule). Status: Valley Pawn OS/MEM_GUARD.md.
# Uses pkill (SIGTERM) not AppleScript quit — no TCC Automation prompts.

MODE="${MEM_GUARD_MODE:-${1:-watch}}"
LOGDIR="$HOME/Library/Logs/valleypawn"
LOG="$LOGDIR/mem_guard.log"
CSV="$LOGDIR/mem_guard.csv"
STATE="$LOGDIR/mem_guard_state"
STATUS="$HOME/Documents/Claude/Projects/Valley Pawn OS/MEM_GUARD.md"
LOCK="/tmp/vp_mem_guard.lock"
mkdir -p "$LOGDIR"

# Apps safe to quit when idle (state restores on reopen). Exact process names.
NONESSENTIAL=("Maps" "iPhone Mirroring" "System Settings" "Activity Monitor" "Preview"
  "TextEdit" "Safari" "FaceTime" "Photos" "Music" "TV" "News" "Stocks" "Weather"
  "Freeform" "Image Playground" "Podcasts" "Books" "Home" "Shortcuts" "Font Book"
  "Disk Utility" "Console" "Calculator" "Clock")

now() { date '+%Y-%m-%d %H:%M:%S'; }
log() { echo "$(now) [$MODE] $*" >> "$LOG"; }

# single instance
if ! mkdir "$LOCK" 2>/dev/null; then
  # stale lock (>20 min) self-heals
  if [ -n "$(find "$LOCK" -maxdepth 0 -mmin +20 2>/dev/null)" ]; then
    rm -rf "$LOCK"; mkdir "$LOCK" 2>/dev/null || exit 0
  else
    exit 0
  fi
fi
trap 'rm -rf "$LOCK"' EXIT

# ---------- metrics ----------
swap_mb() { sysctl -n vm.swapusage 2>/dev/null | awk '{for(i=1;i<=NF;i++) if($i=="used"){v=$(i+2); sub(/M/,"",v); print int(v); exit}}'; }
pressure() { sysctl -n kern.memorystatus_vm_pressure_level 2>/dev/null || echo 0; }   # 1 normal, 2 warn, 4 critical
freepct() { memory_pressure -Q 2>/dev/null | awk -F': ' '/free percentage/{gsub(/%/,"",$2); print $2+0}'; }
idle_s() { ioreg -c IOHIDSystem 2>/dev/null | awk '/HIDIdleTime/ {print int($NF/1000000000); exit}'; }
front_app() { lsappinfo info -only name "$(lsappinfo front 2>/dev/null)" 2>/dev/null | sed -n 's/.*"LSDisplayName"="\(.*\)".*/\1/p'; }
running() { pgrep -x "$1" >/dev/null 2>&1; }

st_get() { [ -f "$STATE" ] && awk -F= -v k="$1" '$1==k{print $2}' "$STATE" | tail -1; }
st_set() { touch "$STATE"; grep -v "^$1=" "$STATE" > "$STATE.tmp" 2>/dev/null; echo "$1=$2" >> "$STATE.tmp"; mv "$STATE.tmp" "$STATE"; }

SWAP0=$(swap_mb); SWAP0=${SWAP0:-0}
PRES0=$(pressure); FREE0=$(freepct); IDLE=$(idle_s); IDLE=${IDLE:-0}
FRONT=$(front_app)
NOW_EPOCH=$(date +%s)
ACTIONS=""
add() { ACTIONS="${ACTIONS}${ACTIONS:+; }$*"; log "$*"; }

# ---------- tiers ----------
tier1_quit_idle_apps() {
  for app in "${NONESSENTIAL[@]}"; do
    running "$app" || continue
    [ "$app" = "$FRONT" ] && [ "$MODE" = "watch" ] && continue
    pkill -x "$app" 2>/dev/null && add "quit idle app: $app"
  done
}

restart_app() {   # $1 process name, $2 app name for open
  local proc="$1" appname="$2" i
  pkill -x "$proc" 2>/dev/null
  for i in $(seq 1 30); do running "$proc" || break; sleep 1; done
  if running "$proc"; then log "WARN $proc did not exit in 30s — leaving it running"; return 1; fi
  sleep 3
  open -ga "$appname" 2>/dev/null
  for i in $(seq 1 30); do running "$proc" && return 0; sleep 2; done
  # self-heal: one retry
  open -ga "$appname" 2>/dev/null; sleep 10
  running "$proc" && return 0
  log "ERROR $appname did not relaunch after retry"; return 1
}

tier2_restart_drive() {
  running "Google Drive" || { open -ga "Google Drive"; add "Google Drive was not running — launched"; return; }
  local last; last=$(st_get drive_restart); last=${last:-0}
  if [ "$MODE" = "watch" ] && [ $((NOW_EPOCH - last)) -lt 14400 ]; then return; fi
  if restart_app "Google Drive" "Google Drive"; then add "restarted Google Drive"; st_set drive_restart "$NOW_EPOCH"; fi
}

tier3_restart_claude() {
  if [ "$IDLE" -lt 1200 ]; then log "skip Claude restart: Joshua active (idle ${IDLE}s)"; return; fi
  local last; last=$(st_get claude_restart); last=${last:-0}
  if [ "$MODE" = "watch" ] && [ $((NOW_EPOCH - last)) -lt 14400 ]; then return; fi
  if restart_app "Claude" "Claude"; then add "restarted Claude desktop app"; st_set claude_restart "$NOW_EPOCH"; fi
}

# ---------- decide ----------
if [ "$MODE" = "nightly" ]; then
  tier1_quit_idle_apps
  tier2_restart_drive
  tier3_restart_claude
else
  HIGH=$(st_get high_count); HIGH=${HIGH:-0}
  if [ "$SWAP0" -ge 14336 ]; then HIGH=$((HIGH+1)); else HIGH=0; fi
  st_set high_count "$HIGH"
  if [ "$SWAP0" -ge 8192 ] || [ "$PRES0" -ge 2 ]; then
    [ "$IDLE" -ge 1200 ] && tier1_quit_idle_apps
  fi
  if [ "$SWAP0" -ge 11264 ] || [ "$PRES0" -ge 4 ]; then tier2_restart_drive; fi
  if [ "$HIGH" -ge 2 ]; then tier3_restart_claude; fi
fi

# ---------- record ----------
[ -n "$ACTIONS" ] && sleep 20
SWAP1=$(swap_mb); PRES1=$(pressure); FREE1=$(freepct)
[ -f "$CSV" ] || echo "time,mode,swap_mb_before,swap_mb_after,pressure_before,pressure_after,free_pct_before,free_pct_after,idle_s,actions" > "$CSV"
echo "$(now),$MODE,$SWAP0,$SWAP1,$PRES0,$PRES1,$FREE0,$FREE1,$IDLE,\"$ACTIONS\"" >> "$CSV"
[ -z "$ACTIONS" ] && log "ok swap=${SWAP0}MB pressure=$PRES0 free=${FREE0}%"

if [ -n "$ACTIONS" ] || [ "$MODE" = "nightly" ] || [ ! -f "$STATUS" ]; then
  {
    echo "# Memory Guard — $(now)"
    echo
    echo "Native agents com.valleypawn.mem-guard (every 15 min) + com.valleypawn.mem-guard-nightly (3:50 AM)."
    echo "Script: Valley Pawn OS/bin/mem_guard.sh. Stopgap until the 96GB Mac Studio arrives (mid-Dec 2026)."
    echo
    echo "## Last run ($MODE)"
    echo "- Swap: ${SWAP0} MB -> ${SWAP1} MB"
    echo "- Pressure level (1 ok / 2 warn / 4 critical): $PRES0 -> $PRES1"
    echo "- Free memory: ${FREE0}% -> ${FREE1}%"
    echo "- Actions: ${ACTIONS:-none needed}"
    echo
    echo "## Last 12 actions"
    echo '```'
    grep -v ' ok swap=' "$LOG" | tail -12
    echo '```'
  } > "$STATUS.tmp" 2>/dev/null && mv "$STATUS.tmp" "$STATUS"
fi
exit 0
