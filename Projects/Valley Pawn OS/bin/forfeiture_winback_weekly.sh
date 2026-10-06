#!/bin/bash
# forfeiture_winback_weekly.sh — Forfeited-Loan Win-Back v2 (exact match), native agent
# com.valleypawn.forfeiture-winback, Sunday 12:30 (stores closed, Bravo idle). Built 2026-09-29.
# Per store, one trigger per view (watcher caps a trigger at 45 min):
#   loans     "Claude Forfeiture Winback" + layout "High Dollar Loan Demographic" (name, ADDRESS, pull date, SMS), rows=5000
#   contacts  "...Comparison" + layout "Customer Address Check" (name, phone, address, e-mail, SMS)  Last Time In > RUN-60
#   visits    "...Comparison" + layout "Customers First Time In" (name, zip, LAST TIME IN)          Last Time In > RUN-7
#   + FULL contacts and visits (Last Time In > RUN-760, rows=20000) when the store has none < 84 days old
# Then fwb_build.py (v2, exact: name+address identity, Bravo Last Time In vs forfeit date),
# Brevo list 11 import, gated send (SEND_APPROVED). Args: [--no-pull] [--no-full] [--dry] [--date D] [--deadline HH:MM]
AGENT="forfeiture-winback"
. "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
FWB="$HOME/Documents/Claude/Projects/Email Refinement/forfeiture_winback"
PULL=1; DRY=""; NOFULL=0; DEADLINE=""; RUN=$(date +%Y-%m-%d)
while [ $# -gt 0 ]; do
  case "$1" in --no-pull) PULL=0 ;; --no-full) NOFULL=1 ;; --dry) DRY="--dry" ;; --date) shift; RUN="$1" ;; --deadline) shift; DEADLINE="$1" ;; esac; shift
done
vp_lock "$AGENT" 420
d_minus() { date -j -v-"$1"d -f %Y-%m-%d "$RUN" +%Y-%m-%d; }
D7=$(d_minus 7); D60=$(d_minus 60); DFULL=$(d_minus 760)
L_LOANS="SHARED GLOBALLY | High Dollar Loan Demographic"
L_CONTACTS="SHARED GLOBALLY | Customer Address Check"
L_VISITS="SHARED GLOBALLY | Customers First Time In"
G="$BRAVO/_bravo_foreground_guard.sh"
vlog "start v2 RUN=$RUN D7=$D7 D60=$D60 DFULL=$DFULL pull=$PULL nofull=$NOFULL deadline=$DEADLINE $DRY"

# --deadline HH:MM = the next occurrence of that clock time after the script started (crosses midnight)
DL_EPOCH=""
if [ -n "$DEADLINE" ]; then
  DL_EPOCH=$(date -j -f "%Y-%m-%d %H:%M" "$(date +%Y-%m-%d) $DEADLINE" +%s)
  [ "$DL_EPOCH" -le "$(date +%s)" ] && DL_EPOCH=$(( DL_EPOCH + 86400 ))
fi
past_deadline() { [ -n "$DL_EPOCH" ] && [ "$(date +%s)" -ge "$DL_EPOCH" ]; }

pull() {  # $1 report  $2 date-string  $3 store  $4 id-suffix  $5 expected output file
  local f="$BRAVO/output/$5"
  if [ -s "$f" ] && [ -s "$f.meta" ] && grep -q "^captured=" "$f.meta"; then
    if [ "$4" = "vfull" ] || [ "$4" = "cfull" ]; then
      [ "$(wc -l < "$f")" -gt 1 ] && { vlog "reuse $5"; return 0; }
      vlog "full file $5 is empty — pulling again"
    else vlog "reuse $5"; return 0; fi
  fi
  for i in 1 2 3; do
    [ -z "$(find "$BRAVO/triggers/claimed" -type f -mmin -3 ! -name 'fwb-*' 2>/dev/null | head -1)" ] && break
    vlog "pipeline busy with another task — wait 60s ($i/3)"; sleep 60
  done
  bash "$G" acquire "$AGENT" >/dev/null 2>&1   # keeps guarded relaunchers off Bravo mid-pull
  local j
  for j in 1 2; do
    bravo_run "fwb-$RUN-$3-$4-$(date +%H%M%S)" "{\"name\":\"$1\",\"stores\":[\"$3\"],\"date\":\"$2\"}" 2700
    [ -s "$f" ] && break
    vlog "attempt $j: $5 not produced"; sleep 30
  done
  [ -s "$f" ] || vlog "WARN: $5 missing after 2 attempts"
  return 0
}

if [ $PULL -eq 1 ]; then
  vlog "health gate: $(health_gate 600)"
  for ST in CUL HAR LEX ROA WAY; do
    pull forfeiture-winback "rows=5000|stamp=$RUN|layout=$L_LOANS|tag=addr" "$ST" loans "${RUN}_${ST}_forfeiture-winback-addr.csv"
    pull forfeiture-winback-comparison "$D60|rows=5000|layout=$L_CONTACTS|tag=contacts" "$ST" c60 "${D60}_${ST}_forfeiture-winback-comparison-contacts.csv"
    pull forfeiture-winback-comparison "$D7|rows=5000|layout=$L_VISITS|tag=visits" "$ST" v7 "${D7}_${ST}_forfeiture-winback-comparison-visits.csv"
    if [ $NOFULL -eq 0 ]; then
      MK="$FWB/full_$ST"; LAST=$(cat "$MK" 2>/dev/null); NEED=1
      if [ -n "$LAST" ]; then
        AGE=$(( ( $(date -j -f %Y-%m-%d "$RUN" +%s) - $(date -j -f %Y-%m-%d "$LAST" +%s) ) / 86400 ))
        [ "$AGE" -lt 84 ] && NEED=0
      fi
      if [ $NEED -eq 1 ]; then
        if past_deadline; then vlog "deadline reached — full directory for $ST left for next run"; else
          pull forfeiture-winback-comparison "$DFULL|rows=20000|layout=$L_VISITS|tag=visits" "$ST" vfull "${DFULL}_${ST}_forfeiture-winback-comparison-visits.csv"
          pull forfeiture-winback-comparison "$DFULL|rows=20000|layout=$L_CONTACTS|tag=contacts" "$ST" cfull "${DFULL}_${ST}_forfeiture-winback-comparison-contacts.csv"
          NV=$(wc -l < "$BRAVO/output/${DFULL}_${ST}_forfeiture-winback-comparison-visits.csv" 2>/dev/null || echo 0)
          NC=$(wc -l < "$BRAVO/output/${DFULL}_${ST}_forfeiture-winback-comparison-contacts.csv" 2>/dev/null || echo 0)
          if [ "${NV:-0}" -gt 1 ] && [ "${NC:-0}" -gt 1 ]; then echo "$RUN" > "$MK"; else vlog "full directory for $ST came back empty (visits=$NV contacts=$NC) — will retry next run"; fi
        fi
      fi
    fi
  done
  bash "$G" release "$AGENT" >/dev/null 2>&1
fi

"$PY" "$FWB/fwb_build.py" "$RUN" 2>&1 | tee -a "$VLOG/$AGENT.log"
RC=${PIPESTATUS[0]}
if [ $RC -ne 0 ]; then
  ledger "$AGENT" "Forfeited-loan win-back audience was not updated this week — store data was missing or incomplete (see runs/$RUN/report.md)." "no"
  exit 1
fi
"$PY" "$BIN/forfeiture_winback_brevo.py" import "$RUN" $DRY 2>&1 | tee -a "$VLOG/$AGENT.log"
[ ${PIPESTATUS[0]} -ne 0 ] && { ledger "$AGENT" "Forfeited-loan win-back list did not fully update in Brevo this week." "no"; exit 1; }
"$PY" "$BIN/forfeiture_winback_brevo.py" send "$RUN" $DRY 2>&1 | tee -a "$VLOG/$AGENT.log"
[ ${PIPESTATUS[0]} -ne 0 ] && { ledger "$AGENT" "Forfeited-loan win-back email did not go out this week." "no"; exit 1; }
vlog "done RUN=$RUN"
exit 0
