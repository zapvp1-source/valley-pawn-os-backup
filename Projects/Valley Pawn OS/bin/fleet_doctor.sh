#!/bin/bash
# fleet_doctor.sh — the nightly self-check that keeps this work going without a session.
#
# WHY (2026-09-18): every diagnostic built today (log triage, agent doctor, delivery audit, the
# go/no-go gate) only ran because a session ran it. That is the same trap the fleet was already in —
# a control that depends on someone remembering to look is not a control. This runs them all at
# 02:10 every night, writes one dated report, and speaks up ONLY when something needs Joshua.
#
# It is pure stdlib Python + bash through vp-runner: no Claude session, no model cost, no Bravo, no
# Parallels, no osascript. It therefore cannot be taken out by the failure mode that took out
# everything else on 9/12-9/17.
#
# Rule 16: nothing goes to a team channel, ever. One DM to Joshua, in plain language, only when
# there is something actionable. Silence means clean.
AGENT="fleet-doctor"
. "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
BIN="$OS_DIR/bin"
OUT="$OS_DIR/fleet/doctor"
mkdir -p "$OUT"
DATE=$(date +%Y-%m-%d)
R="$OUT/$DATE.md"
vp_lock "$AGENT" 30

TOOLFAIL=""
run_tool() {   # run_tool <label> <cmd...> — a diagnostic that CRASHES must never read as "clean"
  local label="$1"; shift
  "$@" 2>&1
  local rc=$?
  if [ $rc -ne 0 ]; then
    TOOLFAIL="$TOOLFAIL $label(rc=$rc)"
    echo
    echo "**$label EXITED $rc — its findings above are incomplete or absent.**"
  fi
  return 0
}

{
  echo "# Fleet doctor — $DATE $(date +%H:%M)"
  echo
  echo "Nightly self-check. Runs outside Claude; cannot be taken out by a connector outage."
  echo
  echo "## 0. Sandbox regression suite — does the monitoring itself still work?"
  echo
  echo "Every scenario encodes a fault already found and fixed once. A red line here means a"
  echo "regression has been shipped, and nothing below this section can be trusted."
  echo
  run_tool fleet_sim $PY "$BIN/fleet_sim.py"
  echo
  echo "## 1. Launchd agents pointing at programs that do not exist"
  echo
  run_tool agent_doctor $PY "$BIN/agent_doctor.py"
  echo
  echo "## 2. Native agents crashing or silently stopped"
  echo
  run_tool log_triage $PY "$BIN/log_triage.py" --days 7
  echo
  echo "## 3. Delivery audit + go/no-go gate"
  echo
  run_tool vp_audit $PY "$BIN/vp_audit.py" --days 60 --json "$OS_DIR/fleet/audit.json" >/dev/null
  run_tool fleet_gate $PY "$BIN/fleet_gate.py" --json "$OS_DIR/fleet/audit.json"
} > "$R" 2>&1

vlog "report written: $R ($(wc -c < "$R" | tr -d ' ') bytes)"

# ---- decide whether this needs a human, WITHOUT posting jargon (Rule 16) ----
# Parse the tools' SUMMARY contract lines, never their prose. Grepping prose is what made this
# script print "clean — no DM" on 2026-09-19 while log_triage reported 8 agents failing: the
# wording had changed and the pattern silently matched nothing. A report that reads a wording
# change as good news is worse than no report.
sum_of() { grep -o "$2=[0-9]*" "$R" 2>/dev/null | head -1 | cut -d= -f2; }
BROKEN=$(sum_of x broken_vp); [ -z "$BROKEN" ] && BROKEN=0
DEAD=$(sum_of x still_failing); [ -z "$DEAD" ] && DEAD=0
STALE=$(sum_of x stale); [ -z "$STALE" ] && STALE=0
# If a contract line is missing entirely, the tool did not finish — treat that as a tool failure
# rather than as zeros, which would read as "all clean".
grep -q "SUMMARY still_failing=" "$R" || TOOLFAIL="$TOOLFAIL log_triage(no-summary)"
grep -q "SUMMARY broken_vp=" "$R" || TOOLFAIL="$TOOLFAIL agent_doctor(no-summary)"

# A dry run in effect would make everything look missing — say so instead of crying wolf.
if $PY "$BIN/vp_dryrun.py" status >/dev/null 2>&1; then
  vlog "publish guard is ARMED — skipping the nightly DM so a test is never reported as an outage"
  exit 0
fi

MSG=""
# A CRASHED DIAGNOSTIC IS THE MOST DANGEROUS RESULT THERE IS, and it is not hypothetical: on
# 2026-09-19 log_triage.py died with UnboundLocalError, produced no output, and this script's greps
# found nothing to report — so it printed "clean — no DM". A broken check read as a healthy fleet.
# That is precisely the failure that let the watchdog sit dead through two multi-day outages, and it
# must be louder than anything it might have found.
[ -n "$TOOLFAIL" ] && MSG="$MSG""The overnight check could not complete — part of it errored, so tonight's all-clear cannot be trusted and should not be read as one. "
# A red sandbox means a monitoring regression shipped: the checks themselves are wrong, so every
# other number in tonight's report is suspect. Say that first and in those terms.
grep -q "RESULT: .* 0 failed" "$R" || MSG="The self-test of the monitoring itself did not come back clean, so tonight's results are not trustworthy until that is looked at. $MSG"
[ "${DEAD:-0}" -gt 0 ]   && MSG="$MSG$DEAD background job(s) logged errors this week. "
[ "${STALE:-0}" -gt 0 ]  && MSG="$MSG$STALE background job(s) have gone quiet for longer than their own schedule allows, which usually means they have stopped running. "
[ -n "$TOOLFAIL" ] && vlog "TOOL FAILURES:$TOOLFAIL"
[ -n "$TOOLFAIL" ] && ledger "$AGENT" "A diagnostic errored during the nightly check:$TOOLFAIL — the all-clear is not trustworthy." "no"

if [ -n "$MSG" ]; then
  slack dm "Overnight system check — ${MSG}Details are in the fleet doctor report for $DATE. Nothing was changed automatically." >/dev/null \
    && vlog "DM sent" || vlog "DM failed"
  ledger "$AGENT" "Nightly check found: $MSG" "no"
else
  vlog "clean — no DM"
fi
vlog "=== fleet-doctor done ==="
