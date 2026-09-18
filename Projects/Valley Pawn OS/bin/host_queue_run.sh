#!/bin/bash
# Host Job Queue runner — Valley Pawn (additive, 2026-09-16).
#
# WHY: interactive Cowork sessions cannot touch protected host paths
# (~/Library/Application Support/Claude, ~/Library/Logs/Claude, ~/Library/LaunchAgents)
# and cannot type into Terminal. But native launchd agents already execute scripts
# that live in this Projects folder (via ~/bin/vp-runner). So a session can DROP a
# job here and a native agent runs it on the host within minutes.
#
# HOW: any file matching  fleet/host_queue/*.sh  is executed ONCE (sorted by name),
# with its stdout/stderr captured to  fleet/host_queue/done/<name>.log , then the
# script itself is moved to done/. A job that must not run again is simply not
# re-dropped. mkdir-lock prevents overlap between callers.
#
# CALLERS: hooked (background, non-blocking) from bin/preston_watch_run.sh
# (every 2 min). Safe to hook from any other vp-runner wrapper the same way.
#
# RULES for jobs: idempotent, self-verifying, no output to Slack unless recovery
# failed (Rule 16), backups before edits, never write null into any registry.

OS_DIR="$HOME/Documents/Claude/Projects/Valley Pawn OS"
Q="$OS_DIR/fleet/host_queue"
DONE="$Q/done"
LOCK="$Q/.lock"
LOG="$HOME/Library/Logs/valleypawn/host-queue.log"
mkdir -p "$Q" "$DONE" "$(dirname "$LOG")"

# stale-lock guard: a lock older than 30 min is abandoned
if [ -d "$LOCK" ]; then
  if [ -n "$(find "$Q" -maxdepth 1 -name .lock -mmin +30 2>/dev/null)" ]; then rmdir "$LOCK" 2>/dev/null; fi
fi
mkdir "$LOCK" 2>/dev/null || exit 0
trap 'rmdir "$LOCK" 2>/dev/null' EXIT

# ---- ALLOW-LIST (FLEET_FREEZE_2026-09-16.md Rule 4 / Phase 0.6, Joshua 2026-09-16) ----
# A job may only (a) set variables, echo, sleep, mkdir -p, exit, and (b) invoke scripts that live
# in bin/ AND are named in fleet/host_queue_allowlist.txt. Anything else (curl, launchctl, cp,
# plutil, python one-liners, arbitrary binaries) is REFUSED before execution: the job is moved to
# done/ with a REFUSED log and rc=99. Need a new host capability? Add a versioned script to bin/,
# list it, and call that — never widen this check.
ALLOW="$OS_DIR/fleet/host_queue_allowlist.txt"
BIN_DIR="$OS_DIR/bin"
validate_job() {  # $1 = job path ; prints reasons; returns 0 = ok, 1 = refused
  local n=0 ok=0 line first script base
  [ -f "$ALLOW" ] || { echo "REFUSED: allowlist file missing ($ALLOW)"; return 1; }
  [ -s "$1" ] || { echo "REFUSED: job file empty or missing"; return 1; }
  while IFS= read -r line || [ -n "$line" ]; do
    n=$((n+1))
    # strip leading whitespace; skip blanks, comments, shebang
    line="${line#"${line%%[![:space:]]*}"}"
    [ -z "$line" ] && continue
    case "$line" in \#*) continue ;; esac
    # one command per line — no chaining, pipes, or substitution that could smuggle a second command
    case "$line" in *";"*|*"&&"*|*"||"*|*"|"*|*'`'*|*'$('*)
      echo "REFUSED: line $n chains/pipes/substitutes (one plain command per line): $line"; ok=1; continue ;; esac
    first="${line%% *}"
    case "$first" in
      set|echo|printf|sleep|exit|mkdir|true|:) continue ;;
      [A-Za-z_]*=*) continue ;;                       # VAR=value
      bash|/bin/bash|python3|/usr/bin/python3) ;;      # checked below
      *) echo "REFUSED: line $n starts with '$first' (not allowed): $line"; ok=1; continue ;;
    esac
    # the first .sh/.py token must resolve to bin/<allow-listed name>
    script="$(printf '%s\n' "$line" | grep -oE '"[^"]+\.(sh|py)"|[^[:space:]"]+\.(sh|py)' | head -1 | tr -d '"')"
    [ -z "$script" ] && { echo "REFUSED: line $n runs an interpreter with no script path: $line"; ok=1; continue; }
    base="$(basename "$script")"
    case "$script" in *"/Valley Pawn OS/bin/$base"|"\$BIN/$base"|"\$OS/bin/$base"|"\$OS_BIN/$base") ;;
      *) echo "REFUSED: line $n script is not under Valley Pawn OS/bin: $script"; ok=1; continue ;; esac
    grep -qxF "$base" "$ALLOW" || { echo "REFUSED: line $n '$base' is not in host_queue_allowlist.txt"; ok=1; }
  done < "$1"
  return $ok
}

shopt -s nullglob
for job in "$Q"/*.sh; do
  name="$(basename "$job" .sh)"
  stamp="$(date '+%F %T')"
  echo "$stamp START $name" >> "$LOG"
  # move first so a crash mid-run can never re-execute the same job
  mv "$job" "$DONE/$name.sh"
  if ! reasons="$(validate_job "$DONE/$name.sh")"; then
    { echo "=== $name REFUSED by host_queue allow-list $(date '+%F %T') ==="; echo "$reasons"; } > "$DONE/$name.log"
    echo "$(date '+%F %T') REFUSED $name" >> "$LOG"
    echo "exit=99" >> "$DONE/$name.log"
    continue
  fi
  /bin/bash "$DONE/$name.sh" > "$DONE/$name.log" 2>&1
  rc=$?
  echo "$(date '+%F %T') END   $name rc=$rc" >> "$LOG"
  echo "exit=$rc" >> "$DONE/$name.log"
done
exit 0
