#!/bin/bash
# launchd wrapper — native monthly-loan-layaway-outcomes (Mac-first wave 3, 2026-10-19). 2nd of month 10:30 ET.
# Dormant unless fleet/state/native_live/monthly-loan-layaway-outcomes exists (bin/vp_live.sh).
# The SKILL's whole job is one command: loan_layaway_outcomes.py --send (writes the outbox envelope to Joshua +
# the <ym>.sent marker; ALREADY_SENT = nothing). SENT=none(nothing-usable) -> the SKILL's one plain on-hold line.
#   --render  = the script's own --test mode (writes <ym>-TEST.* files, sends nothing)
AGENT="monthly-loan-layaway-outcomes"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
if [ "$1" = "--render" ]; then shift; "$PY" "$BIN/loan_layaway_outcomes.py" --test "$@"; exit $?; fi
vp_live_gate "$AGENT"
vp_lock "$AGENT" 60
LINE=$("$PY" "$BIN/loan_layaway_outcomes.py" --send "$@" 2>>"$VLOG/$AGENT.log") || { vlog "script failed: $LINE"; ledger "$AGENT" "The monthly loan and layaway outcomes report did not build." "no"; exit 1; }
vlog "$LINE"
case "$LINE" in
  *"SENT=none(nothing-usable)"*)
    M=$(echo "$LINE" | sed -n 's/^MONTH=\([0-9-]*\).*/\1/p'); MON=$(date -j -f %Y-%m-%d "$M-01" "+%B %Y")
    HM="$OS_DIR/fleet/state/loan_layaway_hold_$M"; mkdir -p "$OS_DIR/fleet/state"
    if [ ! -f "$HM" ]; then touch "$HM"   # one hold line per month, ever
      T="$OS_DIR/fleet/outbox/monthly-loan-layaway-outcomes-hold-$(date +%Y%m%d-%H%M%S).txt"
      printf 'The monthly loan and layaway outcomes report for %s is on hold — the month-end store numbers aren'"'"'t in yet. It will go out once they are.\n' "$MON" > "$T"
      printf '{"channel": "U03BB52MDSA", "file": "%s"}\n' "$T" > "${T%.txt}.json"
      vlog "hold line queued for $MON"
    fi ;;
esac
exit 0
