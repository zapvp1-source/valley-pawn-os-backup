#!/bin/bash
# instock_nightly.sh -- native agent com.valleypawn.instock-nightly, 1:45 AM daily + 2:35 AM catch-up (built 2026-11-24).
# Type A (drops triggers; queued by the watcher). Slot: after the 12:45 AM daily GL, done before its 3:15 AM retry.
# Full on-shelf item list, all 5 stores (Bravo cell instock-all, read only), as of the business day that just ended
# (the shelves do not change overnight). Then instock_merge.py publishes one company list to Google Drive.
# All-or-nothing; the catch-up run pulls only stores still missing. Silent (Rule 16): one ledger row if the
# catch-up run still cannot publish. Args: [--no-pull] [YYYY-MM-DD]
AGENT="instock-nightly"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 100
NOPULL=0; [ "$1" = "--no-pull" ] && { NOPULL=1; shift; }
if [ -n "$1" ]; then D="$1"; elif [ "$(date +%H)" -lt 12 ]; then D=$(date -v-1d +%Y-%m-%d); else D=$(date +%Y-%m-%d); fi
ST_DIR="$OS_DIR/fleet/state/instock"; mkdir -p "$ST_DIR"
[ $NOPULL -eq 0 ] && [ -f "$ST_DIR/nightly_done_$D" ] && { vlog "already published for $D"; exit 0; }
# A store's list counts only if it was pulled after that day's close (7 PM), so a daytime test pull is never
# mistaken for the nightly one. (--no-pull publishes whatever is on disk for the date.)
have() { [ -s "$BRAVO/output/${D}_$1_instock-all.tsv.meta" ] && [ -n "$(find "$BRAVO/output/${D}_$1_instock-all.tsv" -newermt "$D 19:00:00" 2>/dev/null)" ]; }
if [ $NOPULL -eq 0 ]; then
  for GRP in CUL,HAR,LEX ROA,WAY; do
    for try in 1 2; do
      WANT=""; for ST in ${GRP//,/ }; do have $ST || WANT="$WANT,$ST"; done; WANT="${WANT#,}"
      [ -z "$WANT" ] && break
      bash "$BIN/bravo_pull.sh" instock-all "$D" "$WANT" "instock-all-$D-${GRP%%,*}-$(date +%H%M)" >> "$VLOG/$AGENT.log" 2>&1
      sleep 30
    done
  done
fi
"$PY" "$BIN/instock_merge.py" "$D" >> "$VLOG/$AGENT.log" 2>&1; RC=$?
vlog "end: merge rc=$RC for $D"
[ $RC -eq 0 ] && [ $NOPULL -eq 0 ] && date > "$ST_DIR/nightly_done_$D"
if [ $RC -ne 0 ] && [ "$(date +%H%M)" -ge 0230 ] && [ "$(date +%H)" -lt 12 ]; then
  ledger "$AGENT" "Item-level inventory list for $D was not published; the last good list is still in Drive." "no"
fi
exit 0
