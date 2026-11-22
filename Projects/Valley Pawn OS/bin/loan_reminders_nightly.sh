#!/bin/bash
# loan_reminders_nightly.sh -- native agent com.valleypawn.loan-reminders, 10:40 PM daily (built 2026-11-21; after jewelry-nightly, before the 12:45 AM daily GL).
# NO-SEND TRIAL. Nothing in this agent can text a customer: it only reads.
#   1. Bravo: pipeline cell loan-reminders (saved report "Claude Loan Reminders"), all 5 stores, read only.
#   1b. Bravo: pipeline cell layaway-detail, all 5 stores, read only.
#   2. Chekkit: refresh the opt-out list (GET only).
#   3. Plan what WOULD be texted tomorrow -> Loan Reminder Texts/trial/<date>/ + trial/SUMMARY.csv
# Silent (Rule 16): results go to files and the agent log only. Args: [--no-pull]
AGENT="loan-reminders"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 90
D=$(date +%Y-%m-%d)
# CATCH-UP (4:40 AM run): any store whose list did not come back last night is pulled again, still after close and
# before the stores open, then the plan for today is rebuilt. If everything is already there it does nothing in Bravo.
CATCHUP=0
if [ "$(date +%H)" -lt 9 ]; then D=$(date -v-1d +%Y-%m-%d); CATCHUP=1; fi
LR="$HOME/Documents/Claude/Projects/Loan Reminder Texts"
if [ "$1" != "--no-pull" ]; then
  WANT=""; for ST in CUL HAR LEX ROA WAY; do [ "$CATCHUP" = 1 ] && [ -s "$BRAVO/output/${D}_${ST}_loan-reminders.csv" ] || WANT="$WANT,$ST"; done; WANT="${WANT#,}"
  for try in 1 2 3; do
    [ -z "$WANT" ] && break
    bash "$BIN/bravo_pull.sh" loan-reminders "$D" "$WANT" "loan-reminders-$D-$try$( [ "$CATCHUP" = 1 ] && echo c )" >> "$VLOG/$AGENT.log" 2>&1
    MISSING=""; for ST in CUL HAR LEX ROA WAY; do [ -s "$BRAVO/output/${D}_${ST}_loan-reminders.csv" ] || MISSING="$MISSING,$ST"; done
    [ -z "$MISSING" ] && break
    WANT="${MISSING#,}"; vlog "missing after pull $try: $WANT (retrying only those)"; sleep 120
  done
fi
# layaways (cell layaway-detail, read only). Two triggers so neither can reach the watcher's 45-minute cap.
if [ "$1" != "--no-pull" ]; then
  for GRP in CUL,HAR,LEX ROA,WAY; do
    WANT=""; for ST in ${GRP//,/ }; do [ -s "$BRAVO/output/${D}_${ST}_layaway-detail-all-active.tsv" ] || WANT="$WANT,$ST"; done
    for try in 1 2; do
      [ -z "$WANT" ] && break
      bash "$BIN/bravo_pull.sh" layaway-detail "$D" "${WANT#,}" "layaway-reminders-$D-${GRP%%,*}-$try$( [ "$CATCHUP" = 1 ] && echo c )" >> "$VLOG/$AGENT.log" 2>&1
      WANT=""; for ST in ${GRP//,/ }; do [ -s "$BRAVO/output/${D}_${ST}_layaway-detail-all-active.tsv" ] || WANT="$WANT,$ST"; done
      [ -n "$WANT" ] && { vlog "layaway list missing after pull $try: ${WANT#,}"; sleep 90; }
    done
  done
fi
[ "$CATCHUP" = 1 ] || "$PY" "$BIN/chekkit_optouts_sync.py" --days 3 >> "$VLOG/$AGENT.log" 2>&1
"$PY" "$LR/loan_reminders_plan.py" --pull-date "$D" >> "$VLOG/$AGENT.log" 2>&1
vlog "end: plan rc=$?"
# one-time: read 120 days of Chekkit conversations for older opt-outs (slow; after the plan so it never delays it)
BF="$OS_DIR/fleet/state/chekkit_optouts/.backfill_done"
if [ "$CATCHUP" = 0 ] && [ ! -f "$BF" ]; then "$PY" "$BIN/chekkit_optouts_sync.py" --days 120 >> "$VLOG/$AGENT.log" 2>&1 && date > "$BF"; fi
exit 0
