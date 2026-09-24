#!/bin/bash
# backup_health.sh — native replacement for the Cowork task `backup-health-watchdog`.
#
# WHY (2026-09-23): the Cowork version failed on 9/22 AND 9/23 for the same stated reason — it needs
# the Control_your_Mac connector to run tmutil/ping/git on the host, and that connector is gone from
# scheduled sessions for good. A native agent IS on the host. Same checks, same thresholds, same
# escalation, straight from the task's own Step 2 — nothing invented.
#
# Publishes ONE plain DM to Joshua only on WARN/CRIT; silent when OK. Through vp_slack (receipt +
# publish guard for free). Escalates the wording after 3 consecutive bad days so the DM does not
# become wallpaper (the task's own Step 3.5).
AGENT="backup-health-watchdog"
. "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
RENDER=0; for a in "$@"; do [ "$a" = "--render" ] && RENDER=1; done
[ $RENDER -eq 0 ] && vp_lock "$AGENT" 20
STATE="$OS_DIR/fleet/backup_health_state.json"
NOW=$(date +%s)

CRIT=""; WARN=""
# --- NAS ---
ping -c 1 -t 3 valleypawn-nas.local >/dev/null 2>&1 || CRIT="$CRIT NAS unreachable;"
# --- newest backup ---
LATEST=$(tmutil latestbackup 2>/dev/null | tail -1)
if [ -z "$LATEST" ]; then
  CRIT="$CRIT no latest backup reported;"
else
  # backup folders end in YYYY-MM-DD-HHMMSS
  STAMP=$(basename "$LATEST" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{6}' | head -1)
  if [ -n "$STAMP" ]; then
    T=$(date -j -f "%Y-%m-%d-%H%M%S" "$STAMP" +%s 2>/dev/null || echo 0)
    AGE_H=$(( (NOW - T) / 3600 ))
    if [ "$AGE_H" -gt 48 ]; then CRIT="$CRIT newest backup ${AGE_H}h old;"
    elif [ "$AGE_H" -gt 26 ]; then WARN="$WARN newest backup ${AGE_H}h old;"; fi
  fi
fi
# --- AutoBackup ---
tmutil destinationinfo 2>/dev/null | grep -q "AutoBackup" 2>/dev/null   # informational only on newer macOS
AB=$(defaults read /Library/Preferences/com.apple.TimeMachine AutoBackup 2>/dev/null)
[ "$AB" = "1" ] || [ -z "$AB" ] || CRIT="$CRIT AutoBackup is off;"
# --- exclusions ---
for p in "$HOME/Documents" "$HOME/Documents/Claude" "$HOME/Parallels" "$HOME/Library/Parallels" "$HOME/Desktop"; do
  tmutil isexcluded "$p" 2>/dev/null | grep -q '\[Excluded\]' && CRIT="$CRIT $(basename "$p") excluded from backup;"
done
# --- zero-backup days in the last 14 ---
DEST=$(tmutil destinationinfo 2>/dev/null | awk -F': ' '/Mount Point/{print $2; exit}')
if [ -n "$DEST" ]; then
  DAYS=$(tmutil listbackups -d "$DEST" 2>/dev/null | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' | sort -u | tail -14 | wc -l | tr -d ' ')
  [ "$DAYS" -lt 10 ] && [ "$DAYS" -gt 0 ] && WARN="$WARN only $DAYS of the last 14 days have a backup;"
  USE=$(df -P "$DEST" 2>/dev/null | awk 'NR==2{gsub("%","",$5); print $5}')
  [ -n "$USE" ] && [ "$USE" -ge 85 ] && WARN="$WARN backup drive ${USE}% full;"
fi
# --- offsite git (judge by the COMMIT, never the log's mtime — the task's own warning) ---
GT=$(git -C "$HOME/Documents/Claude" log -1 --format='%ct' origin/main 2>/dev/null)
if [ -n "$GT" ]; then
  GH=$(( (NOW - GT) / 3600 )); [ "$GH" -gt 72 ] && WARN="$WARN offsite GitHub copy ${GH}h old;"
else
  WARN="$WARN could not read the offsite GitHub copy;"
fi

if   [ -n "$CRIT" ]; then STATUS=CRIT; ISSUES="$CRIT"
elif [ -n "$WARN" ]; then STATUS=WARN; ISSUES="$WARN"
else STATUS=OK; ISSUES=""; fi

# consecutive-bad-day counter
PREV=$($PY -c "import json;d=json.load(open('$STATE'));print(d.get('streak',0),d.get('date',''))" 2>/dev/null || echo "0 ")
STREAK=${PREV%% *}; PDATE=${PREV#* }; TODAY=$(date +%Y-%m-%d)
if [ "$STATUS" = "OK" ]; then STREAK=0
elif [ "$PDATE" != "$TODAY" ]; then STREAK=$((STREAK+1)); fi
[ $RENDER -eq 0 ] && printf '{"streak":%d,"date":"%s","status":"%s"}\n' "$STREAK" "$TODAY" "$STATUS" > "$STATE"

MSG=$(printf ':floppy_disk: *Backup health — %s* (%s)\n' "$STATUS" "$TODAY")
[ "$STREAK" -ge 3 ] && MSG=$(printf ':rotating_light: *Backups have been %s for %d days running — this needs a hand today.*\n%s' "$STATUS" "$STREAK" "$MSG")
MSG="$MSG"$'\n'"$(echo "$ISSUES" | tr ';' '\n' | sed 's/^ */• /' | grep -v '^• *$')"
[ -n "$LATEST" ] && MSG="$MSG"$'\n'"Latest backup: $(basename "$LATEST")"

vlog "status=$STATUS streak=$STREAK issues=[$ISSUES]"
if [ $RENDER -eq 1 ]; then echo "=== RENDER ONLY ==="; echo "$MSG"; exit 0; fi
[ "$STATUS" = "OK" ] && { vlog "OK — no DM"; $PY "$BIN/vp_receipt.py" write "$AGENT" --surface file --target "$STATE" >/dev/null 2>&1; exit 0; }
slack dm "$MSG" >/dev/null && vlog "DM sent" || ledger "$AGENT" "Backup check found $STATUS but the DM could not be sent." "no"
