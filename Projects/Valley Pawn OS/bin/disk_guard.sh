#!/bin/bash
# disk_guard.sh — native disk-space guard (added 2026-11-15, stopgap until the 2TB Mac
# Studio arrives mid-Dec 2026). Complements disk-health (which MONITORS + thins Time
# Machine snapshots). This one MEASURES where the space goes and clears only
# regenerable developer caches + logs older than 30 days. Never deletes documents,
# Downloads, Trash, mail, photos, Parallels/Bravo, Chrome, Claude, Drive, or anything
# under ~/Documents or ~/Library/Logs/valleypawn. Log only — no Slack/DMs.
#
# MODES (env DISK_GUARD_MODE): clean (daily 4:10 AM) | report (Sun 4:20 AM + at install)
MODE="${DISK_GUARD_MODE:-${1:-report}}"
LOGDIR="$HOME/Library/Logs/valleypawn"; mkdir -p "$LOGDIR"
LOG="$LOGDIR/disk_guard.log"
CSV="$LOGDIR/disk_guard.csv"
REPORT="$HOME/Documents/Claude/Projects/Valley Pawn OS/DISK_GUARD.md"
LOCK="/tmp/vp_disk_guard.lock"
now() { date '+%Y-%m-%d %H:%M:%S'; }
log() { echo "$(now) [$MODE] $*" >> "$LOG"; }
if ! mkdir "$LOCK" 2>/dev/null; then
  if [ -n "$(find "$LOCK" -maxdepth 0 -mmin +60 2>/dev/null)" ]; then
    for p in $(pgrep -f "disk_guard.sh" 2>/dev/null); do
      [ "$p" = "$$" ] || [ "$p" = "$PPID" ] && continue
      pkill -P "$p" 2>/dev/null; kill "$p" 2>/dev/null && log "killed stale run pid $p"
    done
    rm -rf "$LOCK"; mkdir "$LOCK" 2>/dev/null || exit 0
  else
    exit 0
  fi
fi
trap 'rm -rf "$LOCK"' EXIT

free_gb() { df -g /System/Volumes/Data 2>/dev/null | awk 'NR==2{print $4}'; }
capped() { local secs="$1"; shift; perl -e 'alarm shift; exec @ARGV' "$secs" "$@"; }
sz() { local o; o=$(capped 240 du -sk "$1" 2>/dev/null | awk '{printf "%.1f", $1/1048576}'); echo "${o:-timeout}"; }   # GB
F0=$(free_gb)

clean() {
  local before after
  before=$(free_gb)
  # regenerable package-manager caches
  for d in "$HOME/.npm/_cacache" "$HOME/Library/Caches/pip" "$HOME/.cache/pip" "$HOME/Library/Caches/Homebrew"; do
    [ -d "$d" ] || continue
    s=$(sz "$d"); rm -rf "$d" 2>/dev/null && log "cleared cache $d (${s} GB)"
  done
  command -v brew >/dev/null 2>&1 && brew cleanup -s >/dev/null 2>&1 && log "brew cleanup"
  # logs older than 30 days (not the fleet's own logs)
  n=$(find "$HOME/Library/Logs" -type f \( -name '*.log' -o -name '*.log.*' -o -name '*.gz' -o -name '*.ips' -o -name '*.crash' \) \
       -mtime +30 -not -path "*/valleypawn/*" 2>/dev/null | wc -l | tr -d ' ')
  find "$HOME/Library/Logs" -type f \( -name '*.log' -o -name '*.log.*' -o -name '*.gz' -o -name '*.ips' -o -name '*.crash' \) \
       -mtime +30 -not -path "*/valleypawn/*" -delete 2>/dev/null
  [ "$n" -gt 0 ] && log "deleted $n log/crash files older than 30 days"
  after=$(free_gb)
  log "free ${before} GB -> ${after} GB"
}

report() {
  local tmp="$REPORT.tmp"
  {
    echo "# Disk Guard — $(now)"
    echo
    echo "Native agents com.valleypawn.disk-guard (clean, daily 4:10 AM) + disk-guard-report (Sun 4:20 AM)."
    echo "Script: Valley Pawn OS/bin/disk_guard.sh. Stopgap until the 2TB Mac Studio arrives (mid-Dec 2026)."
    echo
    echo "## Volume"
    echo '```'; df -H /System/Volumes/Data 2>/dev/null; echo '```'
    echo "Swap files: $(sz /private/var/vm) GB · Time Machine local snapshots: $(tmutil listlocalsnapshots / 2>/dev/null | grep -c TimeMachine)"
    echo
    echo "## Biggest places (GB)"
    echo '| GB | Path |'; echo '|---|---|'
    for p in "$HOME/Parallels" "$HOME/Applications (Parallels)" "$HOME/.ollama" "$HOME/.vp-studio" "$HOME/Downloads" "$HOME/Desktop" \
             "$HOME/Movies" "$HOME/Music" "$HOME/Pictures" "$HOME/.Trash" "$HOME/.npm" "$HOME/.cache" "$HOME/Library/Caches" \
             "$HOME/Library/Mail" "$HOME/Library/Messages" "$HOME/Library/CloudStorage" "$HOME/Library/Mobile Documents" \
             "$HOME/Library/Containers" "$HOME/Library/Group Containers" "$HOME/Library/Application Support" \
             "$HOME/Library/Developer" "$HOME/Library/Logs" "$HOME/Documents" "/Applications" "/Library"; do
      [ -e "$p" ] && echo "| $(sz "$p") | $(echo "$p" | sed "s|^$HOME|~|") |"
    done | sort -t'|' -k2 -rn
    for parent in "$HOME/Library/Application Support" "$HOME/Library/Containers" "$HOME/Library/Group Containers" \
                  "$HOME/Documents/Claude/Projects" "$HOME/Library/CloudStorage"; do
      [ -d "$parent" ] || continue
      echo; echo "### Top 10 inside $(echo "$parent" | sed "s|^$HOME|~|") (GB)"
      echo '```'
      capped 300 du -sk "$parent"/* "$parent"/.[!.]* 2>/dev/null | sort -rn | head -10 | awk '{s=$1/1048576; $1=""; printf "%6.1f %s\n", s, $0}' | sed "s#$HOME#~#"
      echo '```'
    done
    echo; echo "## Files over 2 GB anywhere in home"
    echo '```'
    capped 600 find "$HOME" -xdev \( -path "$HOME/Library/CloudStorage" -o -path "$HOME/Library/Mobile Documents" -o -name "*.photoslibrary" -o -path "$HOME/Library/Containers/com.apple.*" \) -prune -o -type f -size +2G -print 2>/dev/null | head -40 | while read -r f; do printf "%6.1f %s\n" "$(stat -f %z "$f" | awk '{print $1/1073741824}')" "$(echo "$f" | sed "s|^$HOME|~|")"; done | sort -rn
    echo '```'
    echo; echo "## Recent guard actions"; echo '```'; tail -15 "$LOG" 2>/dev/null; echo '```'
  } > "$tmp" 2>/dev/null && mv "$tmp" "$REPORT"
  rm -f "$tmp" 2>/dev/null
  log "report written"
}

renice 15 $$ >/dev/null 2>&1
if [ "$MODE" = "clean" ]; then
  clean
  if [ ! -f "$REPORT" ] || [ -n "$(find "$REPORT" -mtime +7 2>/dev/null)" ]; then report; fi
else clean; report; fi
[ -f "$CSV" ] || echo "time,mode,free_gb_before,free_gb_after" > "$CSV"
echo "$(now),$MODE,$F0,$(free_gb)" >> "$CSV"
exit 0
