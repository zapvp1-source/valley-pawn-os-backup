#!/bin/bash
# morning_pull.sh — native replacement for the Cowork task `bravo-morning-pull` (2026-09-17).
#
# WHY: the Cowork task fired every morning (lastRunAt current) and died before writing its
# trigger — no intake/sold CSVs 9/12–9/16, pawn walk / sold review / discount review dark for
# five days, nobody noticed. Everything that task did was plain shell via osascript; nothing in
# it needs a model. A launchd agent cannot die silently in the same way: it either writes the
# trigger file or leaves a non-zero exit in its log.
#
# CONTRACT (identical to the SKILL.md it replaces): one combined trigger (intake-detail +
# sold-discount-detail for YESTERDAY, items-to-price for TODAY, all 5 stores), watcher singleton
# hygiene first, health gate, poll for the result, ONE retry of failed cells, then an honest
# per-report CLEAN/FAILED certificate in logs/_morning_pull_status_<DATE>.txt and one history
# line. Silent: never Slack, never DM. Downstream tasks trust only a CLEAN line.
#
# Run manually:  bash morning_pull.sh            (full run, ~30-40 min)
#                bash morning_pull.sh --dry-run  (prints the trigger, touches nothing)
set +e
PROJECT="$HOME/Documents/Claude/Projects/Bravo Data Extraction"
VLOG="$HOME/Library/Logs/valleypawn"; mkdir -p "$VLOG"
LOG="$VLOG/morning-pull.log"
VM='{7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}'
PRLCTL=/usr/local/bin/prlctl
DRY=0; [ "$1" = "--dry-run" ] && DRY=1
STORES='["CUL","HAR","LEX","ROA","WAY"]'

log() { echo "$(date '+%Y-%m-%d %H:%M:%S') $*" | tee -a "$LOG"; }

DATE=$(date +%Y-%m-%d); YESTERDAY=$(date -v-1d +%Y-%m-%d)
NOW=$(date +%Y-%m-%dT%H:%M:%S%z); STAMP=$(date +%Y-%m-%dT%H-%M-%S)
TRIGGER_ID="morning-pull-$STAMP"
CERT="$PROJECT/logs/_morning_pull_status_$DATE.txt"
START=$(date +%s)
log "=== morning_pull start id=$TRIGGER_ID date=$DATE yesterday=$YESTERDAY dry=$DRY ==="

# ---- single-instance guard (never two morning pulls on the VM) ----
LOCK="$PROJECT/logs/.morning_pull.lock"
if [ -d "$LOCK" ] && [ -n "$(find "$PROJECT/logs" -maxdepth 1 -name .morning_pull.lock -mmin +90)" ]; then rmdir "$LOCK"; fi
if ! mkdir "$LOCK" 2>/dev/null; then log "ABORT: another morning pull is running (lock present)"; exit 1; fi
trap 'rmdir "$LOCK" 2>/dev/null' EXIT

# ---- STEP 2: watcher singleton hygiene ----
if [ $DRY -eq 0 ]; then
  rm -f "$CERT"
  "$PRLCTL" exec "$VM" --current-user powershell -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File '\\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction\_restart_watcher_v2.ps1' > /tmp/mp_watcher.log 2>&1
  log "watcher hygiene rc=$? :: $(tail -3 /tmp/mp_watcher.log | tr '\n' ' ' | cut -c1-200)"
  # ---- STEP 3: health gate (backgrounded, poll status file, 10 min cap) ----
  "$PRLCTL" exec "$VM" --current-user powershell.exe -NoProfile -WindowStyle Hidden -Command "Get-Process WindowsTerminal,OpenConsole -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue" >/dev/null 2>&1
  ( cd "$PROJECT" && LC_ALL=C LANG=C nohup ./bravo_ensure_healthy.sh > logs/_mp_health.log 2>&1 < /dev/null & )
  for i in $(seq 1 40); do
    sleep 15
    S=$(cat "$PROJECT/logs/_health_gate_status.txt" 2>/dev/null)
    case "$S" in *PASS*) break ;; *FAIL*) break ;; esac
  done
  log "health gate: ${S:-no status} (proceeding either way — the gate already ran its self-heal)"
fi

# ---- STEP 4: drop ONE combined trigger ----
mk_trigger() {  # $1 id  $2 reports-json
  printf '{"id":"%s","requested_at":"%s","reports":[%s]}' "$1" "$(date +%Y-%m-%dT%H:%M:%S%z)" "$2"
}
R_INTAKE="{\"name\":\"intake-detail\",\"stores\":$STORES,\"date\":\"$YESTERDAY..$YESTERDAY\"}"
R_SOLD="{\"name\":\"sold-discount-detail\",\"stores\":$STORES,\"date\":\"$YESTERDAY..$YESTERDAY\"}"
R_ITP="{\"name\":\"items-to-price\",\"stores\":$STORES,\"date\":\"$DATE\"}"
JSON=$(mk_trigger "$TRIGGER_ID" "$R_INTAKE,$R_SOLD,$R_ITP")
if [ $DRY -eq 1 ]; then echo "$JSON"; log "dry-run: trigger printed, nothing written"; exit 0; fi
printf %s "$JSON" > "$PROJECT/triggers/$TRIGGER_ID.json"
log "trigger written: triggers/$TRIGGER_ID.json"

# ---- STEP 5: poll for the result (cap 50 min); one self-heal if unclaimed >3 min / silent >12 min ----
wait_result() {  # $1 id  $2 cap-seconds  -> 0 when results/<id>.result.json exists
  local id="$1" cap="$2" t0=$(date +%s) healed=0 last_size=0 last_change=$(date +%s)
  while [ $(( $(date +%s) - t0 )) -lt "$cap" ]; do
    [ -f "$PROJECT/results/$id.result.json" ] && return 0
    sleep 20
    local now=$(date +%s) size=0
    size=$(stat -f %z "$PROJECT/logs/$id.log" 2>/dev/null || echo 0)
    if [ "$size" != "$last_size" ]; then last_size=$size; last_change=$now; fi
    local unclaimed=0; [ -f "$PROJECT/triggers/$id.json" ] && unclaimed=1
    if [ $healed -eq 0 ] && { { [ $unclaimed -eq 1 ] && [ $((now - t0)) -gt 180 ]; } || { [ $unclaimed -eq 0 ] && [ $((now - last_change)) -gt 720 ]; }; }; then
      log "self-heal: trigger unclaimed=$unclaimed silent=$((now - last_change))s — restarting watcher once"
      "$PRLCTL" exec "$VM" --current-user powershell -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File '\\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction\_restart_watcher_v2.ps1' > /tmp/mp_watcher2.log 2>&1
      healed=1; sleep 120
    fi
  done
  return 1
}
wait_result "$TRIGGER_ID" 3000; log "poll done (result present: $([ -f "$PROJECT/results/$TRIGGER_ID.result.json" ] && echo yes || echo no))"

# ---- STEP 6: integrity gate per report (disk + log), then ONE retry of failed cells ----
gate() {  # prints "CLEAN" or "FAILED <stores>" for report $1 using log $2
  /usr/bin/python3 - "$1" "$2" "$PROJECT" "$DATE" "$YESTERDAY" <<'PY'
import sys,os,re
rep,logid,proj,date,yday=sys.argv[1:6]
stores=["CUL","HAR","LEX","ROA","WAY"]
log=""
try: log=open(os.path.join(proj,"logs",logid+".log"),errors="replace").read()
except Exception: pass
bad=[]
for s in stores:
    f = f"{date}_{s}_items-to-price.csv" if rep=="items-to-price" else f"{yday}_to_{yday}_{s}_{rep}.csv"
    p=os.path.join(proj,"output",f)
    if not os.path.exists(p): bad.append(s); continue
    if rep=="items-to-price":
        # section for this store: no GAVE UP, and csv rows >= maxY-1 from seen=X/Y lines
        sec=re.split(r"\n(?=\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} +Running items-to-price for )",log)
        mine=[x for x in sec if f"Running items-to-price for {s}" in x]
        txt=mine[-1] if mine else ""
        if "GAVE UP" in txt: bad.append(s); continue
        ys=[int(y) for x,y in re.findall(r"seen=(\d+)/(\d+)",txt)]
        maxy=max(ys) if ys else 0
        rows=sum(1 for _ in open(p,errors="replace"))-1
        if maxy>0 and rows < maxy-1: bad.append(s)
print("CLEAN" if not bad else "FAILED "+" ".join(bad))
PY
}
G_INTAKE=$(gate intake-detail "$TRIGGER_ID"); G_SOLD=$(gate sold-discount-detail "$TRIGGER_ID"); G_ITP=$(gate items-to-price "$TRIGGER_ID")
log "gate: intake=[$G_INTAKE] sold=[$G_SOLD] itp=[$G_ITP]"

if [ "$G_INTAKE" != "CLEAN" ] || [ "$G_SOLD" != "CLEAN" ] || [ "$G_ITP" != "CLEAN" ]; then
  RSTAMP=$(date +%Y-%m-%dT%H-%M-%S); RID="morning-pull-retry-$RSTAMP"; parts=""
  addr() { local name="$1" g="$2" dt="$3"; [ "$g" = "CLEAN" ] && return
           local st=$(echo "$g" | sed 's/^FAILED //' | tr ' ' '\n' | sed 's/.*/"&"/' | paste -sd, -)
           parts="$parts${parts:+,}{\"name\":\"$name\",\"stores\":[$st],\"date\":\"$dt\"}"; }
  addr intake-detail "$G_INTAKE" "$YESTERDAY..$YESTERDAY"; addr sold-discount-detail "$G_SOLD" "$YESTERDAY..$YESTERDAY"; addr items-to-price "$G_ITP" "$DATE"
  ( cd "$PROJECT" && LC_ALL=C LANG=C nohup ./bravo_ensure_healthy.sh > logs/_mp_health2.log 2>&1 < /dev/null & ); sleep 90
  printf %s "$(mk_trigger "$RID" "$parts")" > "$PROJECT/triggers/$RID.json"
  log "retry trigger written: $RID [$parts]"
  wait_result "$RID" 1200
  G_INTAKE=$(gate intake-detail "$RID"); G_SOLD=$(gate sold-discount-detail "$RID"); G_ITP=$(gate items-to-price "$RID")
  # a store that was already clean in the first pass stays clean; re-gate against BOTH logs
  [ "$G_INTAKE" != "CLEAN" ] && G_INTAKE=$(gate intake-detail "$TRIGGER_ID")
  [ "$G_SOLD" != "CLEAN" ] && G_SOLD=$(gate sold-discount-detail "$TRIGGER_ID")
  log "gate after retry: intake=[$G_INTAKE] sold=[$G_SOLD] itp=[$G_ITP]"
fi

# ---- STEP 7: certificate + history (honest — never CLEAN for an unverified report) ----
{ echo "intake-detail $G_INTAKE"; echo "sold-discount-detail $G_SOLD"; echo "items-to-price $G_ITP"; } > "$CERT"
c() { [ "$1" = "CLEAN" ] && echo C || echo F; }
MIN=$(( ( $(date +%s) - START ) / 60 ))
echo "$NOW $TRIGGER_ID intake=$(c "$G_INTAKE") sold=$(c "$G_SOLD") itp=$(c "$G_ITP") duration=${MIN}m NOTE: native launchd (morning_pull.sh)" >> "$PROJECT/logs/_morning_pull_history.log"
log "certificate written: $(tr '\n' ' ' < "$CERT") duration=${MIN}m"
log "=== morning_pull done ==="
exit 0
