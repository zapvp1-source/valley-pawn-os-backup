#!/bin/bash
# =============================================================================
# bravo_health_gate.sh  —  Unified Bravo health gate + auto-recover ladder
# -----------------------------------------------------------------------------
# Purpose: ONE entrypoint that EVERY Bravo data pull runs FIRST. It drives Bravo
# from ANY broken state back to a verified store Dashboard, autonomously, using
# the recovery primitives already proven in production. Never hammers logins
# (lockout guard). Writes a structured status file the caller polls.
#
# ADDITIVE (Rule #4): this file is NET-NEW. It only *invokes* existing, hardened
# scripts (_relaunch_bravo_and_watcher.ps1, _nudge_login.ahk via _run_nudge_session1.ps1,
# _recover_to_dashboard.ahk). It edits none of them.
#
# Failure modes covered (all observed in KNOWN_ISSUES.md / status logs):
#   1. VM not running                 -> prlctl start
#   2. Parallels guest agent dead     -> bounded prlctl restart (the 06-10 hang)
#   3. Bravo not running              -> _relaunch_bravo_and_watcher.ps1
#   4. Bravo "(Not Responding)"/hung  -> relaunch (only acceptable kill) + nudge
#   5. Black-window render            -> nudge (WinRestore+Activate+Maximize)
#   6. At Select-Store / login screen -> _recover_to_dashboard.ahk
#   7. Login bounce / auto-lock       -> recover handles it; capped retries
#   8. Watcher down                   -> relaunch script also relaunches watcher
#
# USAGE (run detached; poll the STATUS file):
#   nohup bash bravo_health_gate.sh CUL [--smoke] >/dev/null 2>&1 &
#   then read logs/_health_gate_status.txt  ->  "PASS <code>" | "FAIL <reason>"
#
# Exit codes: 0 = PASS (Bravo on verified Dashboard). 1 = FAIL (needs Joshua).
# =============================================================================

set -u

# ---- Config -----------------------------------------------------------------
GUID="{7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}"
PRLCTL="/usr/local/bin/prlctl"
ROOT_MAC="/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction"
ROOT_VM='\\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction'
AHK='C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe'
LOGDIR="$ROOT_MAC/logs"
LOG="$LOGDIR/_health_gate.log"
STATUS="$LOGDIR/_health_gate_status.txt"
RECOVER_RES="$LOGDIR/_recover_result.txt"

TARGET="${1:-CUL}"
SMOKE="no"
for a in "$@"; do [ "$a" = "--smoke" ] && SMOKE="yes"; done

mkdir -p "$LOGDIR"

ts()  { date '+%Y-%m-%d %H:%M:%S'; }
log() { echo "$(ts) | $*" | tee -a "$LOG" >&2; }
set_status() { echo "$1" > "$STATUS"; }

# Run a prlctl-exec command with a hard Mac-side timeout so a DEAD guest agent
# (failure mode #2) cannot hang us forever. $1=secs, rest=command.
exec_vm() {
  local secs="$1"; shift
  ( "$@" ) & local p=$!
  local i=0
  while kill -0 "$p" 2>/dev/null; do
    sleep 1; i=$((i+1))
    if [ "$i" -ge "$secs" ]; then kill -9 "$p" 2>/dev/null; wait "$p" 2>/dev/null; return 124; fi
  done
  wait "$p"; return $?
}

log "==================== HEALTH GATE start target=$TARGET smoke=$SMOKE ===================="
set_status "RUNNING"

# ---- Rung 1: VM running -----------------------------------------------------
VMSTATE=$("$PRLCTL" list "$GUID" -o status --no-header 2>/dev/null | tr -d ' ')
log "Rung1 VM state=$VMSTATE"
if [ "$VMSTATE" != "running" ]; then
  log "Rung1 VM not running -> starting"
  "$PRLCTL" start "$GUID" >/dev/null 2>&1
  sleep 40
  VMSTATE=$("$PRLCTL" list "$GUID" -o status --no-header 2>/dev/null | tr -d ' ')
  log "Rung1 VM state after start=$VMSTATE"
  if [ "$VMSTATE" != "running" ]; then set_status "FAIL vm-not-running"; log "FAIL vm-not-running"; exit 1; fi
fi

# ---- Rung 2: guest agent alive (prlctl exec responsive) ---------------------
agent_alive() { exec_vm 20 "$PRLCTL" exec "$GUID" --current-user cmd /c "echo READY" >/dev/null 2>&1; }
if agent_alive; then
  log "Rung2 guest agent OK"
else
  log "Rung2 guest agent DEAD (prlctl exec hung/failed) -> bounded VM restart"
  "$PRLCTL" restart "$GUID" >/dev/null 2>&1
  sleep 60
  if agent_alive; then
    log "Rung2 guest agent recovered after restart"
  else
    set_status "FAIL guest-agent-dead"; log "FAIL guest-agent-dead (manual: restart Parallels Tools)"; exit 1
  fi
fi

# ---- Rung 3: Bravo running + responsive --------------------------------------
bravo_tasklist() { exec_vm 25 "$PRLCTL" exec "$GUID" --current-user tasklist /v /fi "IMAGENAME eq Bravo.exe" /fo list 2>/dev/null; }
relaunch_bravo() {
  log "Rung3 relaunching Bravo + watcher (Session-1 trick)"
  exec_vm 90 "$PRLCTL" exec "$GUID" --current-user powershell -ExecutionPolicy Bypass -File "$ROOT_VM\\_relaunch_bravo_and_watcher.ps1" >/dev/null 2>&1
  sleep 35
  log "Rung3 nudge window (wake black render / un-minimize)"
  exec_vm 40 "$PRLCTL" exec "$GUID" --current-user powershell -ExecutionPolicy Bypass -File "$ROOT_VM\\_run_nudge_session1.ps1" >/dev/null 2>&1
  sleep 5
  # (added 2026-06-19) The relaunch ps1 starts the watcher from the UNC path
  # (\\Mac\Home). AHK #SingleInstance Force keys on script PATH, so that UNC
  # watcher does NOT replace the existing Y: watcher -> two watchers coexist
  # (double-claim risk + slow UNC CSV writes). _restart_watcher.ps1 kills ALL
  # bravo_watcher.ahk (any path) and starts exactly ONE on Y:. Idempotent.
  log "Rung3 consolidate watcher -> single Y: instance (_restart_watcher.ps1)"
  exec_vm 60 "$PRLCTL" exec "$GUID" --current-user powershell -ExecutionPolicy Bypass -File "$ROOT_VM\\_restart_watcher.ps1" >/dev/null 2>&1
  sleep 8
}

# ---- ClickOnce-aware kill guard (added 2026-06-22) ---------------------------
# ROOT CAUSE of the 2026-06-22 wedge: a "no-window" can mean Bravo is mid-
# ClickOnce-update (dfsvc.exe) or sitting on the Bravo trust/install prompt, NOT
# that Bravo is hung. Force-killing Bravo.exe in that state TEARS the ClickOnce
# trust/cache and turns a silent auto-update into a stuck, human-gated prompt.
# So before ANY force-kill we (a) auto-click the trust prompt and (b) WAIT OUT an
# in-flight update instead of killing. dfsvc.exe = the ClickOnce deployment svc.
clickonce_active() {
  local tl
  tl="$(exec_vm 25 "$PRLCTL" exec "$GUID" --current-user tasklist /fi "IMAGENAME eq dfsvc.exe" /fo csv 2>/dev/null)"
  echo "$tl" | grep -qi "dfsvc.exe"
}
handle_clickonce() {  # returns 0 if Bravo is up afterward, 1 otherwise
  log "ClickOnce: active update/trust-prompt detected -> auto-click Install + wait out update (NO kill)"
  exec_vm 30 "$PRLCTL" exec "$GUID" --current-user "$AHK" "$ROOT_VM\\_clickonce_guard.ahk" >/dev/null 2>&1
  local i tl
  for i in $(seq 1 36); do          # up to ~6 min
    sleep 10
    tl="$(bravo_tasklist)"
    if echo "$tl" | grep -qi "Bravo.exe" && ! echo "$tl" | grep -qi "Not Responding"; then
      log "ClickOnce: Bravo.exe up post-update (waited ~$((i*10))s) -> recovered without kill"
      return 0
    fi
    exec_vm 20 "$PRLCTL" exec "$GUID" --current-user "$AHK" "$ROOT_VM\\_clickonce_guard.ahk" >/dev/null 2>&1
  done
  log "ClickOnce: update window elapsed, Bravo still not visible"
  return 1
}
# guarded_kill_bravo: 0 = Bravo recovered via ClickOnce (skip relaunch),
#                     1 = killed (or no ClickOnce) -> caller should relaunch.
guarded_kill_bravo() {
  if clickonce_active; then
    handle_clickonce && return 0
    return 1
  fi
  log "guarded_kill: no ClickOnce activity -> force-kill Bravo.exe (genuine hang)"
  exec_vm 20 "$PRLCTL" exec "$GUID" --current-user taskkill /F /IM Bravo.exe >/dev/null 2>&1
  return 1
}

TL="$(bravo_tasklist)"
if ! echo "$TL" | grep -qi "Bravo.exe"; then
  log "Rung3 Bravo NOT running"
  relaunch_bravo
elif echo "$TL" | grep -qi "Not Responding"; then
  log "Rung3 Bravo HUNG (Not Responding) -> ClickOnce-guarded kill, then relaunch if needed"
  if guarded_kill_bravo; then
    log "Rung3 Bravo recovered via ClickOnce wait -> skipping relaunch"
  else
    sleep 3
    relaunch_bravo
  fi
else
  log "Rung3 Bravo running + responsive"
fi

# ---- Rung 4: ensure verified Dashboard (capped retries; no login hammer) -----
# NOTE: prlctl-exec of AutoHotkey64.exe is FIRE-AND-FORGET — the GUI process
# detaches and the exec call returns in seconds while the .ahk keeps running.
# So we LAUNCH the recover script, then POLL its result file (it writes
# logs/_recover_result.txt = "OK <code>" | "FAIL <reason>" when done, ~30-90s).
DASH_OK="no"
for attempt in 1 2; do
  log "Rung4 recover-to-dashboard attempt $attempt target=$TARGET"
  rm -f "$RECOVER_RES" 2>/dev/null
  exec_vm 30 "$PRLCTL" exec "$GUID" --current-user "$AHK" "$ROOT_VM\\_recover_to_dashboard.ahk" "$TARGET" >/dev/null 2>&1
  RES=""
  for j in $(seq 1 24); do          # poll up to ~120s for the script to finish
    sleep 5
    # strip CR and the UTF-8 BOM (EF BB BF = \357\273\277) the AHK script writes
    RES="$(cat "$RECOVER_RES" 2>/dev/null | tr -d '\r\357\273\277')"
    [ -n "$RES" ] && break
  done
  log "Rung4 recover result='$RES'"
  if echo "$RES" | grep -qi "^OK"; then DASH_OK="yes"; break; fi
  sleep 8   # brief backoff; never rapid-loop logins (lockout guard)
done
# ---- Rung 4b: ESCALATE to force-relaunch if gentle recover failed -----------
# (added 2026-06-19) Covers the failure that defeated the gate on 6/18 & 6/19:
# Bravo is running+responsive but STUCK on a sticky Report Preview / parked store
# that _recover_to_dashboard.ahk cannot navigate out of (Rung 3 saw "responsive"
# so it never relaunched). Force-kill + relaunch is the PROVEN recovery for that
# state. Fires ONLY after the gentle recover already failed.
if [ "$DASH_OK" != "yes" ]; then
  log "Rung4b ESCALATE: gentle recover failed -> ClickOnce-guarded kill + relaunch, then retry recover"
  if guarded_kill_bravo; then
    log "Rung4b Bravo recovered via ClickOnce wait -> skipping relaunch, going straight to recover"
  else
    sleep 4
    relaunch_bravo
  fi
  for attempt in 1 2; do
    log "Rung4b recover-to-dashboard (post-relaunch) attempt $attempt target=$TARGET"
    rm -f "$RECOVER_RES" 2>/dev/null
    exec_vm 30 "$PRLCTL" exec "$GUID" --current-user "$AHK" "$ROOT_VM\\_recover_to_dashboard.ahk" "$TARGET" >/dev/null 2>&1
    RES=""
    for j in $(seq 1 30); do
      sleep 5
      RES="$(cat "$RECOVER_RES" 2>/dev/null | tr -d '\r\357\273\277')"
      [ -n "$RES" ] && break
    done
    log "Rung4b recover result='$RES'"
    if echo "$RES" | grep -qi "^OK"; then DASH_OK="yes"; break; fi
    sleep 8
  done
fi
if [ "$DASH_OK" != "yes" ]; then
  # (added 2026-06-22) Capture WHY on fail: which relevant processes/dialogs were
  # live (dfsvc = ClickOnce update, Bravo, AutoHotkey modal). No more blind "no-window".
  DIAG="$(exec_vm 25 "$PRLCTL" exec "$GUID" --current-user tasklist /fo csv 2>/dev/null | grep -iE 'dfsvc|Bravo|AutoHotkey|dfshim' | tr '\n' ';')"
  log "FAIL diagnostics (live procs): ${DIAG:-none}"
  if echo "$DIAG" | grep -qi 'dfsvc'; then
    log "FAIL note: dfsvc.exe present -> a Bravo ClickOnce UPDATE was in flight; this is the update-prompt wedge, not a hang. _clickonce_guard.ahk should have handled it; check logs/_clickonce_guard.log"
  fi
  set_status "FAIL no-dashboard"; log "FAIL no-dashboard after gentle recover + force-relaunch"; exit 1
fi

# ---- Rung 5 (optional): 1-cell smoke ----------------------------------------
if [ "$SMOKE" = "yes" ]; then
  SID="healthgate-smoke-$(date '+%Y-%m-%dT%H-%M-%S')"
  TODAY="$(date '+%Y-%m-%d')"
  echo "{\"id\":\"$SID\",\"requested_at\":\"$(date '+%Y-%m-%dT%H:%M:%S-0400')\",\"reports\":[{\"name\":\"aged-inventory-summary\",\"stores\":[\"$TARGET\"],\"date\":\"$TODAY\"}]}" > "$ROOT_MAC/triggers/$SID.json"
  log "Rung5 smoke trigger dropped $SID"
  SR="$ROOT_MAC/results/$SID.result.json"
  for i in $(seq 1 16); do
    if [ -f "$SR" ]; then
      if grep -qi '"status": *"success"' "$SR" || grep -qi '"status":"success"' "$SR"; then
        log "Rung5 smoke SUCCESS"; break
      else
        log "Rung5 smoke result present but not success"; cat "$SR" >> "$LOG"; break
      fi
    fi
    sleep 15
  done
fi

set_status "PASS $TARGET"
log "==================== HEALTH GATE PASS target=$TARGET ===================="
exit 0
