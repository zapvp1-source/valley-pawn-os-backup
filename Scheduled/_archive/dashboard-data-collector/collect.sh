#!/bin/bash
# dashboard-data-collector — native launchd version
# Runs entirely on this Mac (network + Keychain access required — this is
# why it can no longer be a Claude Code Remote scheduled trigger; see
# SKILL.md and the project doc "Enterprise Backup, Redundancy & Cybersecurity Plan.md"
# for the full story of why the old CCR-trigger version silently failed for days).
#
# What it does each run:
#   1. Scans every task folder under /Users/joshuadavis/Documents/Claude/Scheduled/
#   2. Finds the most recently modified file in each (a proxy for "did this
#      task produce output recently")
#   3. Writes one TaskRuns row per folder (informational — hours since last activity)
#   4. Writes an Alerts row (severity warning) for any folder with NO file
#      activity in 14+ days — a conservative threshold so weekly/monthly
#      tasks don't false-positive, while genuinely dead automations still surface.
#   5. POSTs everything to the Google Sheets ingest endpoint via the verified
#      two-step curl pattern (secret retrieved from macOS Keychain at runtime).
#
# NOTE: this is a mechanical file-mtime check, not the fuller Slack+BUSINESS_OS.md
# aware version the original SKILL.md envisioned (that requires an LLM in the loop,
# which — per the diagnosis above — cannot run reliably on an hourly cron via CCR
# in this environment). This trades sophistication for something that actually works.

set -uo pipefail

SCHEDULED_DIR="/Users/joshuadavis/Documents/Claude/Scheduled"
INGEST_URL="https://script.google.com/macros/s/AKfycby5QyYAqHFYEr8MsSeoSokqD0Kp6L0OvuYXLq9ld8l-1dkH5UbqbDz8841FFT5ranFY/exec"
LOG_FILE="$SCHEDULED_DIR/dashboard-data-collector/collector.log"
STALE_ALERT_HOURS=336   # 14 days

log() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $*" >> "$LOG_FILE"; }

SECRET=$(security find-generic-password -a 'dashboard-collector' -s 'valley-pawn-ingest-secret' -w 2>/dev/null)
if [ -z "$SECRET" ]; then
  log "FATAL: could not retrieve ingest secret from Keychain"
  exit 1
fi

post_rows() {
  # $1 = tab name, $2 = keyField or empty, $3 = json rows array
  local tab="$1" keyfield="$2" rows="$3"
  local body
  if [ -n "$keyfield" ]; then
    body=$(printf '{"secret":"%s","tab":"%s","keyField":"%s","rows":%s}' "$SECRET" "$tab" "$keyfield" "$rows")
  else
    body=$(printf '{"secret":"%s","tab":"%s","rows":%s}' "$SECRET" "$tab" "$rows")
  fi
  local LOC
  LOC=$(curl -sS -D - -o /dev/null --max-time 20 -X POST "$INGEST_URL" -H "Content-Type: application/json" -d "$body" | grep -i '^location:' | awk '{print $2}' | tr -d '\r')
  if [ -n "$LOC" ]; then
    curl -sS --max-time 20 "$LOC"
  else
    echo '{"ok":false,"error":"no redirect location returned"}'
  fi
}

NOW_EPOCH=$(date -u +%s)
TASKRUNS_ROWS=""
ALERTS_ROWS=""
TASK_COUNT=0
STALE_COUNT=0

for dir in "$SCHEDULED_DIR"/*/ ; do
  [ -d "$dir" ] || continue
  name=$(basename "$dir")
  case "$name" in
    _*|model-check-temp) continue ;;
  esac

  # Most recently modified file anywhere under this folder (depth-limited for speed)
  latest=$(find "$dir" -maxdepth 3 -type f -exec stat -f '%m %N' {} \; 2>/dev/null | sort -rn | head -1)
  if [ -z "$latest" ]; then
    mtime_epoch=0
    detail="no files found in task folder"
  else
    mtime_epoch=$(echo "$latest" | awk '{print $1}')
    mtime_iso=$(date -u -r "$mtime_epoch" +%Y-%m-%dT%H:%M:%SZ)
    hours_ago=$(( (NOW_EPOCH - mtime_epoch) / 3600 ))
    detail="last file activity ${hours_ago}h ago"
  fi

  status="active"
  if [ "$mtime_epoch" -eq 0 ]; then
    status="unknown"
  elif [ "$hours_ago" -ge 48 ]; then
    status="stale"
  fi

  last_run_iso="${mtime_iso:-}"
  task_name_esc=$(printf '%s' "$name" | sed 's/"/\\"/g')
  detail_esc=$(printf '%s' "$detail" | sed 's/"/\\"/g')

  row=$(printf '{"task_name":"%s","domain":"ops-scheduled","source":"local-file-scan","status":"%s","last_run_iso":"%s","detail":"%s","next_expected_iso":""}' \
    "$task_name_esc" "$status" "$last_run_iso" "$detail_esc")

  if [ -z "$TASKRUNS_ROWS" ]; then
    TASKRUNS_ROWS="$row"
  else
    TASKRUNS_ROWS="$TASKRUNS_ROWS,$row"
  fi
  TASK_COUNT=$((TASK_COUNT + 1))

  if [ "$mtime_epoch" -ne 0 ] && [ "$hours_ago" -ge "$STALE_ALERT_HOURS" ]; then
    STALE_COUNT=$((STALE_COUNT + 1))
    created_iso=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    alert_msg="Task folder '${task_name_esc}' has had no local file activity in ${hours_ago}h (>= 14 days) — possible silently-dead automation. Verify its scheduled task is still firing."
    alert_row=$(printf '{"severity":"warning","message":"%s","created_iso":"%s","resolved":""}' "$alert_msg" "$created_iso")
    if [ -z "$ALERTS_ROWS" ]; then
      ALERTS_ROWS="$alert_row"
    else
      ALERTS_ROWS="$ALERTS_ROWS,$alert_row"
    fi
  fi
done

log "Scanned ${TASK_COUNT} task folders, ${STALE_COUNT} flagged stale (>=14d)"

TR_RESULT=$(post_rows "TaskRuns" "task_name" "[$TASKRUNS_ROWS]")
log "TaskRuns POST result: $TR_RESULT"

if [ -n "$ALERTS_ROWS" ]; then
  AL_RESULT=$(post_rows "Alerts" "" "[$ALERTS_ROWS]")
  log "Alerts POST result: $AL_RESULT"
fi

# Self-check: if TaskRuns POST didn't report ok:true, raise a meta-alert so the
# failure is visible on the dashboard itself rather than silently dying again.
if ! echo "$TR_RESULT" | grep -q '"ok":true'; then
  created_iso=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  err_esc=$(printf '%s' "$TR_RESULT" | sed 's/"/\\"/g' | tr -d '\n')
  meta_row=$(printf '{"severity":"warning","message":"dashboard-data-collector TaskRuns POST failed: %s","created_iso":"%s","resolved":""}' "$err_esc" "$created_iso")
  post_rows "Alerts" "" "[$meta_row]" >> "$LOG_FILE" 2>&1
  log "Meta-alert posted for TaskRuns POST failure"
fi

log "Run complete."
