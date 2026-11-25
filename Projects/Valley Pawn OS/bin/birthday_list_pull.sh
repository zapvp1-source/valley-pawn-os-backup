#!/bin/bash
# birthday_list_pull.sh [STORES,CSV] -- read-only Bravo pull for the birthday texts (built 2026-11-22).
# Per store: saved Customers report "Claude Forfeiture Winback Comparison" (Last Time In within 760 days) with the
# existing layout "SHARED GLOBALLY | Demographics Report" (Name + Birthday) -> output/<D>_<STORE>_forfeiture-winback-comparison-birthdays.csv
# Skips a store that already has a birthday file less than 6 days old (weekly refresh, Sunday 2:40 PM agent com.valleypawn.birthday-list). One trigger per store (45-min cap). Silent.
AGENT="birthday-list-pull"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 240
STORES="${1:-CUL,HAR,LEX,ROA,WAY}"
D=$(date -v-760d +%Y-%m-%d)
for ST in ${STORES//,/ }; do
  NEW=$(find "$BRAVO/output" -maxdepth 1 -name "*_${ST}_forfeiture-winback-comparison-birthdays.csv" -size +1k -mtime -6 2>/dev/null | head -1)
  [ -n "$NEW" ] && { vlog "$ST: reuse $(basename "$NEW")"; continue; }
  for try in 1 2; do
    bash "$BIN/bravo_pull.sh" forfeiture-winback-comparison "$D|rows=20000|layout=SHARED GLOBALLY | Demographics Report|tag=birthdays" "$ST" "birthdays-$ST-$(date +%Y%m%d)-$try" >> "$VLOG/$AGENT.log" 2>&1
    [ -s "$BRAVO/output/${D}_${ST}_forfeiture-winback-comparison-birthdays.csv" ] && break
    vlog "$ST: no birthday file after pull $try"; sleep 90
  done
done
ls -la "$BRAVO/output" | grep "comparison-birthdays.csv$" | tail -6
vlog "end"
exit 0
